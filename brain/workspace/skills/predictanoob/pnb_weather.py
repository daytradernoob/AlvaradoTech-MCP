"""
PredictaNoob — Weather Strategy
Becker Optimism Tax: buy NO on weather contracts where NOAA forecast
gives >= MIN_MARGIN_F temperature margin and historical hit rate confirms edge.

Runs: 9AM, 12PM, 3PM MST daily (cron handles scheduling)
"""
import sys, json, re, logging
from datetime import date, datetime
import requests
import pnb_auth, pnb_state, pnb_telegram, pnb_learn
from pnb_config import (
    MIN_MARGIN_F, MAX_YES_ASK, MIN_HIST_RATE, MIN_EV_WEATHER as MIN_YES_EDGE,
    MAX_CONTRACTS, HALT_BELOW_CENTS as HALT_BELOW, SKIP_SERIES
)

logging.basicConfig(
    filename="/home/rob-alvarado/RJA/.pnb/pnb_weather.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
log = logging.getLogger("pnb_weather")

BACKTEST_PATH  = "/home/rob-alvarado/RJA/.pnb/weather_backtest.json"

# Kalshi series ticker → NOAA station coordinates + CLI code
CITIES = {
    "KXHIGHDEN":   {"name": "Denver",      "lat": 39.8561, "lon": -104.6737, "cli": "DEN"},
    "KXHIGHLAX":   {"name": "LA",          "lat": 33.9425, "lon": -118.4081, "cli": "LAX"},
    "KXHIGHTPHX":  {"name": "Phoenix",     "lat": 33.4373, "lon": -112.0078, "cli": "PHX"},
    "KXHIGHMIA":   {"name": "Miami",       "lat": 25.7959, "lon": -80.2870,  "cli": "MIA"},
    "KXHIGHTDAL":  {"name": "Dallas",      "lat": 32.8998, "lon": -97.0403,  "cli": "DFW"},
    "KXHIGHTCHI":  {"name": "Chicago",     "lat": 41.9742, "lon": -87.9073,  "cli": "ORD"},
    "KXHIGHCHI":   {"name": "Chicago",     "lat": 41.9742, "lon": -87.9073,  "cli": "ORD"},
    "KXHIGHTBOS":  {"name": "Boston",      "lat": 42.3631, "lon": -71.0065,  "cli": "BOS"},
    "KXHIGHTLV":   {"name": "Las Vegas",   "lat": 36.0840, "lon": -115.1537, "cli": "LAS"},
    "KXHIGHTATL":  {"name": "Atlanta",     "lat": 33.6367, "lon": -84.4281,  "cli": "ATL"},
}

def load_backtest():
    try:
        with open(BACKTEST_PATH) as f:
            return json.load(f)
    except Exception as e:
        log.warning(f"Could not load backtest: {e}")
        return {}

_noaa_forecast_cache = {}  # (lat,lon) -> list of periods

def get_noaa_forecast_periods(lat, lon):
    """Fetch and cache NOAA forecast periods for a location."""
    key = (lat, lon)
    if key in _noaa_forecast_cache:
        return _noaa_forecast_cache[key]
    try:
        r = requests.get(f"https://api.weather.gov/points/{lat},{lon}", timeout=10)
        if r.status_code != 200:
            return []
        forecast_url = r.json()["properties"]["forecast"]
        r2 = requests.get(forecast_url, timeout=10)
        if r2.status_code != 200:
            return []
        periods = r2.json()["properties"]["periods"]
        _noaa_forecast_cache[key] = periods
        return periods
    except Exception as e:
        log.warning(f"NOAA fetch error ({lat},{lon}): {e}")
        return []

def get_noaa_high_for_date(lat, lon, target_date):
    """Return forecast high temp (F) for a specific date. Returns None on failure."""
    periods = get_noaa_forecast_periods(lat, lon)
    target_str = target_date.strftime("%Y-%m-%d")
    # Find the daytime period matching target date
    for p in periods:
        if target_str in p.get("startTime", "") and p.get("isDaytime", False):
            return p["temperature"]
    # If no daytime match (e.g., target is today and it's already evening),
    # use the highest temp in any period for that date
    temps = [p["temperature"] for p in periods if target_str in p.get("startTime", "")]
    return max(temps) if temps else None

def historical_no_rate(backtest, city_name, month, threshold, strike_type):
    """
    Look up historical NO win rate for this contract.
    Snaps to nearest available backtest threshold (5-degree increments).
    strike_type: 'greater' means YES wins if temp > threshold.
    """
    city_data = backtest.get(city_name, {})
    monthly = city_data.get("monthly", {})
    month_data = monthly.get(str(month), {})
    if not month_data:
        return None

    # Snap to nearest available threshold
    available = sorted(int(k) for k in month_data.keys())
    nearest = min(available, key=lambda x: abs(x - threshold))
    entry = month_data.get(str(nearest), {})

    hits = entry.get("hits")
    total = entry.get("total")
    if hits is None or total is None or total == 0:
        return None

    yes_rate = hits / total
    no_rate = 1.0 - yes_rate
    return no_rate if strike_type == "greater" else yes_rate

def expected_value(win_prob, ask_dollars):
    """EV per dollar staked. ask_dollars is what we pay for 1 contract."""
    profit_if_win = 1.0 - ask_dollars
    loss_if_lose  = ask_dollars
    return (win_prob * profit_if_win) - ((1 - win_prob) * loss_if_lose)

def place_order(ticker, side, price_dollars, count, dry_run):
    """
    Place a limit order. Returns (success, order_id, message).
    price_dollars: what we're willing to pay (ask price)
    """
    price_cents = round(price_dollars * 100)
    body = {
        "ticker": ticker,
        "side": side,
        "action": "buy",
        "count": count,
        "type": "limit",
        "yes_price": price_cents if side == "yes" else (100 - price_cents),
    }
    if dry_run:
        log.info(f"[DRY-RUN] Would BUY {count}x {ticker} {side} @ ${price_dollars:.2f} | EV pending")
        return True, "DRY-RUN", "dry run"

    r = pnb_auth.post("/portfolio/orders", body)
    if r.status_code in (200, 201):
        data = r.json().get("order", {})
        order_id = data.get("order_id", "")
        # Verify: must be a valid UUID
        if re.match(r"^[0-9a-f-]{36}$", order_id):
            log.info(f"ORDER PLACED: {ticker} {side} x{count} @ ${price_dollars:.2f} | id={order_id}")
            return True, order_id, "ok"
        else:
            log.error(f"ORDER RETURNED INVALID ID: {order_id} | response: {r.text[:200]}")
            return False, None, "invalid order id"
    else:
        log.error(f"ORDER FAILED: {r.status_code} | {r.text[:200]}")
        return False, None, r.text[:100]

def run():
    dry_run = not pnb_auth.is_live()
    backtest = load_backtest()
    today = date.today()
    month = today.month
    results = []

    log.info(f"=== Weather scan start | {datetime.now().strftime('%Y-%m-%d %H:%M')} | {'DRY-RUN' if dry_run else 'LIVE'} ===")

    # Safety: check balance
    bal_r = pnb_auth.get("/portfolio/balance")
    if bal_r.status_code != 200:
        log.error(f"Balance check failed: {bal_r.text[:100]}")
        return
    balance_cents = bal_r.json().get("balance", 0)
    log.info(f"Balance: ${balance_cents/100:.2f}")
    if balance_cents < HALT_BELOW:
        log.warning(f"Balance ${balance_cents/100:.2f} below halt threshold ${HALT_BELOW/100:.2f}. Halting.")
        return

    # Get active tickers from Kalshi, prune expired from state
    all_active = set()

    for series, city in CITIES.items():
        if series in SKIP_SERIES:
            continue

        # Pre-fetch NOAA periods for this city (cached per run)
        periods = get_noaa_forecast_periods(city["lat"], city["lon"])
        if not periods:
            log.warning(f"No NOAA data for {city['name']}, skipping")
            continue

        # Get open markets for this series
        r = pnb_auth.get("/markets", params={"series_ticker": series, "limit": 20, "status": "open"})
        if r.status_code != 200:
            log.warning(f"Market fetch failed for {series}: {r.status_code}")
            continue

        markets = r.json().get("markets", [])
        for m in markets:
            ticker = m["ticker"]
            all_active.add(ticker)

            # Parse contract date from close_time
            close_time = m.get("close_time", "")
            try:
                # close_time is next day (contracts close morning after), so contract date = day before close
                from datetime import timedelta
                close_dt = date.fromisoformat(close_time[:10])
                contract_date = close_dt - timedelta(days=1)
            except Exception:
                continue

            # Skip contracts more than 2 days out (forecast accuracy drops)
            days_out = (contract_date - today).days
            if days_out < 0 or days_out > 1:
                continue

            # Get NOAA high for the contract's date
            noaa_high = get_noaa_high_for_date(city["lat"], city["lon"], contract_date)
            if noaa_high is None:
                log.info(f"  No NOAA data for {city['name']} on {contract_date}, skip {ticker}")
                continue

            log.info(f"  {ticker} | contract_date={contract_date} | NOAA={noaa_high}°F")

            # Skip if already holding
            if pnb_state.already_holds(ticker):
                log.info(f"  SKIP {ticker} — already held")
                continue

            threshold  = m.get("floor_strike")
            strike_type = m.get("strike_type", "greater")
            yes_ask    = float(m.get("yes_ask_dollars") or 0)
            no_ask     = float(m.get("no_ask_dollars") or 0)

            if not threshold or yes_ask == 0 or no_ask == 0:
                continue

            # Only trade when YES is cheap (strong NO signal)
            if yes_ask > MAX_YES_ASK:
                log.info(f"  SKIP {ticker} — YES ask ${yes_ask:.2f} above ${MAX_YES_ASK:.2f} ceiling")
                continue

            # NOAA margin check
            margin = abs(noaa_high - threshold)
            if margin < MIN_MARGIN_F:
                log.info(f"  SKIP {ticker} — NOAA margin {margin}°F < {MIN_MARGIN_F}°F required")
                continue

            # Determine signal direction from NOAA
            # strike_type='greater': YES wins if temp > threshold
            if strike_type == "greater":
                # NOAA high < threshold = NO signal
                if noaa_high >= threshold:
                    log.info(f"  SKIP {ticker} — NOAA {noaa_high}°F >= threshold {threshold}°F (no NO edge)")
                    continue
                trade_side = "no"
                trade_ask  = no_ask
            else:
                # strike_type='less': YES wins if temp < threshold
                if noaa_high <= threshold:
                    log.info(f"  SKIP {ticker} — NOAA {noaa_high}°F <= threshold {threshold}°F (no NO edge)")
                    continue
                trade_side = "no"
                trade_ask  = no_ask

            # Historical rate check
            hist_no_rate = historical_no_rate(backtest, city["name"], month, threshold, strike_type)
            if hist_no_rate is not None:
                if hist_no_rate < MIN_HIST_RATE:
                    log.info(f"  SKIP {ticker} — hist NO rate {hist_no_rate:.0%} < {MIN_HIST_RATE:.0%}")
                    pnb_learn.record_weather_skip(ticker, city["name"], f"hist NO rate {hist_no_rate:.0%}", hist_no_rate, margin, yes_ask, threshold)
                    continue
                win_prob = hist_no_rate
            else:
                # No backtest data: use implied probability with conservative discount
                win_prob = 1.0 - yes_ask - 0.05  # knock 5% off implied
                if win_prob < MIN_HIST_RATE:
                    log.info(f"  SKIP {ticker} — estimated win prob {win_prob:.0%} insufficient")
                    continue

            # EV check
            ev = expected_value(win_prob, trade_ask)
            if ev < MIN_YES_EDGE:
                log.info(f"  SKIP {ticker} — EV {ev:.1%} below {MIN_YES_EDGE:.0%} minimum")
                continue

            log.info(f"  SIGNAL {ticker} | {trade_side} @ ${trade_ask:.2f} | NOAA margin={margin}°F | hist_NO={win_prob:.0%} | EV={ev:.1%}")

            ok, order_id, msg = place_order(ticker, trade_side, trade_ask, MAX_CONTRACTS, dry_run)
            if ok and order_id != "DRY-RUN":
                pnb_state.record_buy(ticker, trade_side, trade_ask, MAX_CONTRACTS, order_id)
            results.append({
                "ticker": ticker, "side": trade_side, "ask": trade_ask,
                "ev": ev, "order_id": order_id, "ok": ok
            })

    # Prune expired positions
    pruned = pnb_state.prune_expired(all_active)
    if pruned:
        log.info(f"Pruned expired: {pruned}")

    mode_tag = "[DRY-RUN] " if dry_run else ""
    if results:
        lines = [f"{mode_tag}PNB Weather -- {datetime.now().strftime('%H:%M MST')}"]
        for res in results:
            status = "PLACED" if res["ok"] else "FAILED"
            lines.append(f"  {status} {res['ticker']} {res['side'].upper()} @ ${res['ask']:.2f} | EV {res['ev']:.0%}")
        lines.append(f"Balance: ${balance_cents/100:.2f}")
        pnb_telegram.send("\n".join(lines))
    else:
        pnb_telegram.send(
            f"{mode_tag}PNB Weather scan -- {datetime.now().strftime('%H:%M MST')}\n"
            f"No edge found across all cities.\n"
            f"Balance: ${balance_cents/100:.2f}"
        )

    log.info(f"Scan complete | signals={len(results)} | balance=${balance_cents/100:.2f}")
    return results

if __name__ == "__main__":
    run()
