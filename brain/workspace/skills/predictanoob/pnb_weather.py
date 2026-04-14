"""
PredictaNoob — Weather Strategy v2

Improvements over v1:
  - Bidirectional: trade YES or NO — whichever side NOAA + backtest favor
  - Uncertainty EV buffer: margin 5–10°F raises the EV bar continuously
  - Kelly sizing: fractional binary Kelly, capped conservatively

Signal stack:
  1. NOAA forecast direction vs threshold (signed margin)
  2. 50-year historical win rate for that direction ≥ MIN_HIST_RATE
  3. Fee-aware EV ≥ MIN_EV_WEATHER + uncertainty_buffer

Runs: 9AM, 12PM, 3PM MST (cron)
"""
import json, re, logging
from datetime import date, datetime, timedelta
import requests
import pnb_auth, pnb_state, pnb_telegram, pnb_learn, pnb_paper
from pnb_config import (
    MIN_MARGIN_F, UNCERTAINTY_MARGIN_FULL, UNCERTAINTY_EV_BUFFER,
    MIN_HIST_RATE, MIN_EV_WEATHER, KALSHI_FEE_RATE,
    KELLY_FRACTION, KELLY_MAX_CONTRACTS, KELLY_MIN_CONTRACTS,
    HALT_BELOW_CENTS, SKIP_SERIES,
)

logging.basicConfig(
    filename="/home/rob-alvarado/RJA/.pnb/pnb_weather.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
log = logging.getLogger("pnb_weather")

BACKTEST_PATH = "/home/rob-alvarado/RJA/.pnb/weather_backtest.json"

CITIES = {
    "KXHIGHDEN":  {"name": "Denver",    "lat": 39.8561, "lon": -104.6737},
    "KXHIGHLAX":  {"name": "LA",        "lat": 33.9425, "lon": -118.4081},
    "KXHIGHTPHX": {"name": "Phoenix",   "lat": 33.4373, "lon": -112.0078},
    "KXHIGHMIA":  {"name": "Miami",     "lat": 25.7959, "lon": -80.2870},
    "KXHIGHTDAL": {"name": "Dallas",    "lat": 32.8998, "lon": -97.0403},
    "KXHIGHTCHI": {"name": "Chicago",   "lat": 41.9742, "lon": -87.9073},
    "KXHIGHCHI":  {"name": "Chicago",   "lat": 41.9742, "lon": -87.9073},
    "KXHIGHTBOS": {"name": "Boston",    "lat": 42.3631, "lon": -71.0065},
    "KXHIGHTLV":  {"name": "Las Vegas", "lat": 36.0840, "lon": -115.1537},
    "KXHIGHTATL": {"name": "Atlanta",   "lat": 33.6367, "lon": -84.4281},
}


def load_backtest():
    try:
        with open(BACKTEST_PATH) as f:
            return json.load(f)
    except Exception as e:
        log.warning(f"Could not load backtest: {e}")
        return {}


_noaa_cache = {}  # (lat, lon) → forecast periods

def get_noaa_periods(lat, lon):
    key = (lat, lon)
    if key in _noaa_cache:
        return _noaa_cache[key]
    try:
        r = requests.get(f"https://api.weather.gov/points/{lat},{lon}", timeout=10)
        if r.status_code != 200:
            return []
        r2 = requests.get(r.json()["properties"]["forecast"], timeout=10)
        if r2.status_code != 200:
            return []
        periods = r2.json()["properties"]["periods"]
        _noaa_cache[key] = periods
        return periods
    except Exception as e:
        log.warning(f"NOAA fetch error ({lat},{lon}): {e}")
        return []


def get_noaa_high(lat, lon, target_date):
    """Return forecast high (°F) for target_date. None if unavailable."""
    periods = get_noaa_periods(lat, lon)
    target_str = target_date.strftime("%Y-%m-%d")
    # Prefer daytime period
    for p in periods:
        if target_str in p.get("startTime", "") and p.get("isDaytime", False):
            return p["temperature"]
    # Fallback: any period for that date
    temps = [p["temperature"] for p in periods if target_str in p.get("startTime", "")]
    return max(temps) if temps else None


def historical_win_rate(backtest, city_name, month, threshold, strike_type, trade_side):
    """
    Return historical win rate for trade_side ('yes' or 'no').
    Snaps to nearest 5°F bucket in backtest.
    strike_type='greater': YES wins if temp > threshold.
    """
    city_data = backtest.get(city_name, {})
    month_data = city_data.get("monthly", {}).get(str(month), {})
    if not month_data:
        return None

    available = sorted(int(k) for k in month_data.keys())
    nearest = min(available, key=lambda x: abs(x - threshold))
    entry = month_data.get(str(nearest), {})

    hits  = entry.get("hits")
    total = entry.get("total")
    if hits is None or total is None or total == 0:
        return None

    yes_rate = hits / total
    no_rate  = 1.0 - yes_rate

    if strike_type == "greater":
        return yes_rate if trade_side == "yes" else no_rate
    else:
        # strike_type='less': YES wins if temp < threshold
        return no_rate if trade_side == "yes" else yes_rate


def uncertainty_ev_required(margin_f):
    """
    EV requirement scales with how close NOAA is to the threshold.
    5°F margin → full buffer added. 10°F+ → no buffer (base EV only).
    """
    if margin_f >= UNCERTAINTY_MARGIN_FULL:
        return MIN_EV_WEATHER
    # Linear interpolation: at MIN_MARGIN_F → full buffer, at UNCERTAINTY_MARGIN_FULL → 0
    u = 1.0 - (margin_f - MIN_MARGIN_F) / (UNCERTAINTY_MARGIN_FULL - MIN_MARGIN_F)
    return MIN_EV_WEATHER + u * UNCERTAINTY_EV_BUFFER


def fee_aware_ev(win_prob, ask_dollars, contracts=1):
    """Fee-aware EV. Kalshi fee = 7% × C × P × (1-P)."""
    fee    = KALSHI_FEE_RATE * contracts * ask_dollars * (1.0 - ask_dollars)
    profit = (1.0 - ask_dollars) - fee
    loss   = ask_dollars + fee
    return (win_prob * profit) - ((1 - win_prob) * loss)


def kelly_contracts(win_prob, ask_dollars, balance_cents):
    """
    Fractional binary Kelly, capped at KELLY_MAX_CONTRACTS.
    b = profit/loss ratio on this contract.
    """
    if ask_dollars <= 0 or ask_dollars >= 1:
        return KELLY_MIN_CONTRACTS
    fee    = KALSHI_FEE_RATE * 1 * ask_dollars * (1.0 - ask_dollars)
    profit = (1.0 - ask_dollars) - fee
    loss   = ask_dollars + fee
    b = profit / loss
    if b <= 0:
        return KELLY_MIN_CONTRACTS
    f = (win_prob * (b + 1) - 1) / b   # full Kelly fraction
    f = max(0.0, f * KELLY_FRACTION)    # fractional Kelly
    balance_dollars = balance_cents / 100
    dollar_amount = f * balance_dollars
    contracts = max(KELLY_MIN_CONTRACTS, round(dollar_amount / ask_dollars))
    return min(contracts, KELLY_MAX_CONTRACTS)


def place_order(ticker, side, price_dollars, count, dry_run):
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
        log.info(f"[DRY-RUN] Would BUY {count}x {ticker} {side} @ ${price_dollars:.2f}")
        return True, "DRY-RUN", "dry run"

    r = pnb_auth.post("/portfolio/orders", body)
    if r.status_code in (200, 201):
        data = r.json().get("order", {})
        order_id = data.get("order_id", "")
        if re.match(r"^[0-9a-f-]{36}$", order_id):
            log.info(f"ORDER PLACED: {ticker} {side} x{count} @ ${price_dollars:.2f} | id={order_id}")
            return True, order_id, "ok"
        else:
            log.error(f"INVALID ORDER ID: {order_id} | {r.text[:200]}")
            return False, None, "invalid order id"
    else:
        log.error(f"ORDER FAILED: {r.status_code} | {r.text[:200]}")
        return False, None, r.text[:100]


def run():
    dry_run = not pnb_auth.is_live()
    backtest = load_backtest()
    today    = date.today()
    month    = today.month
    results  = []

    log.info(f"=== Weather scan v2 | {datetime.now().strftime('%Y-%m-%d %H:%M')} | {'DRY-RUN' if dry_run else 'LIVE'} ===")

    # Check outcomes of any pending paper trades from previous scans
    if dry_run:
        pnb_paper.check_settlements()

    bal_r = pnb_auth.get("/portfolio/balance")
    if bal_r.status_code != 200:
        log.error(f"Balance check failed: {bal_r.text[:100]}")
        return
    balance_cents = bal_r.json().get("balance", 0)
    log.info(f"Balance: ${balance_cents/100:.2f}")
    if balance_cents < HALT_BELOW_CENTS:
        log.warning(f"Balance below halt (${HALT_BELOW_CENTS/100:.2f}). Halting.")
        return

    all_active = set()

    for series, city in CITIES.items():
        if series in SKIP_SERIES:
            continue

        if not get_noaa_periods(city["lat"], city["lon"]):
            log.warning(f"No NOAA data for {city['name']}, skipping")
            continue

        r = pnb_auth.get("/markets", params={"series_ticker": series, "limit": 20, "status": "open"})
        if r.status_code != 200:
            log.warning(f"Market fetch failed for {series}: {r.status_code}")
            continue

        for m in r.json().get("markets", []):
            ticker = m["ticker"]
            all_active.add(ticker)

            # Contract date = day before close_time
            try:
                close_dt      = date.fromisoformat(m.get("close_time", "")[:10])
                contract_date = close_dt - timedelta(days=1)
            except Exception:
                continue

            days_out = (contract_date - today).days
            if days_out < 0 or days_out > 1:
                continue

            noaa_high = get_noaa_high(city["lat"], city["lon"], contract_date)
            if noaa_high is None:
                log.info(f"  No NOAA data for {city['name']} on {contract_date}, skip {ticker}")
                continue

            if pnb_state.already_holds(ticker):
                log.info(f"  SKIP {ticker} — already held")
                continue

            threshold   = m.get("floor_strike")
            strike_type = m.get("strike_type", "greater")
            yes_ask     = float(m.get("yes_ask_dollars") or 0)
            no_ask      = float(m.get("no_ask_dollars")  or 0)

            if not threshold or yes_ask < 0.03 or no_ask < 0.03:
                continue

            # ── Signed margin: positive = NOAA above threshold ───────────────
            if strike_type == "greater":
                signed_margin = noaa_high - threshold   # + = NOAA above = YES likely
            else:
                signed_margin = threshold - noaa_high   # + = NOAA below = YES likely

            abs_margin = abs(signed_margin)
            log.info(f"  {ticker} | NOAA={noaa_high}°F threshold={threshold} margin={signed_margin:+.1f}°F | YES=${yes_ask:.2f} NO=${no_ask:.2f}")

            # ── Hard margin cutoff ────────────────────────────────────────────
            if abs_margin < MIN_MARGIN_F:
                log.info(f"  SKIP {ticker} — margin {abs_margin:.1f}°F < {MIN_MARGIN_F}°F boundary zone")
                pnb_learn.record_weather_skip(ticker, city["name"], f"boundary zone {abs_margin:.1f}°F", None, abs_margin, yes_ask, threshold)
                continue

            # ── Determine trade side from NOAA direction ──────────────────────
            if signed_margin > 0:
                # NOAA favors YES
                trade_side = "yes"
                trade_ask  = yes_ask
            else:
                # NOAA favors NO
                trade_side = "no"
                trade_ask  = no_ask

            # Sanity: don't buy near-expired side
            if trade_ask > 0.95:
                log.info(f"  SKIP {ticker} — {trade_side} ask ${trade_ask:.2f} already near settlement")
                continue

            # ── Historical win rate ───────────────────────────────────────────
            hist_rate = historical_win_rate(backtest, city["name"], month, threshold, strike_type, trade_side)
            if hist_rate is not None:
                if hist_rate < MIN_HIST_RATE:
                    log.info(f"  SKIP {ticker} — hist {trade_side} rate {hist_rate:.0%} < {MIN_HIST_RATE:.0%}")
                    pnb_learn.record_weather_skip(ticker, city["name"], f"hist {trade_side} rate {hist_rate:.0%}", hist_rate, abs_margin, yes_ask, threshold)
                    continue
                win_prob = hist_rate
            else:
                # No backtest data: implied probability minus conservative discount
                implied = (1.0 - trade_ask)
                win_prob = implied - 0.05
                if win_prob < MIN_HIST_RATE:
                    log.info(f"  SKIP {ticker} — implied win prob {win_prob:.0%} insufficient (no backtest)")
                    continue

            # ── Uncertainty-adjusted EV gate ─────────────────────────────────
            min_ev = uncertainty_ev_required(abs_margin)
            ev = fee_aware_ev(win_prob, trade_ask)
            if ev < min_ev:
                log.info(f"  SKIP {ticker} — EV {ev:.1%} < required {min_ev:.1%} (margin={abs_margin:.1f}°F adds {min_ev - MIN_EV_WEATHER:.1%} buffer)")
                continue

            # ── Kelly sizing ──────────────────────────────────────────────────
            contracts = kelly_contracts(win_prob, trade_ask, balance_cents)

            log.info(
                f"  SIGNAL {ticker} | {trade_side.upper()} @ ${trade_ask:.2f} | "
                f"margin={signed_margin:+.1f}°F | hist={win_prob:.0%} | "
                f"EV={ev:.1%} (min={min_ev:.1%}) | kelly={contracts}c"
            )

            ok, order_id, msg = place_order(ticker, trade_side, trade_ask, contracts, dry_run)
            if ok:
                if order_id == "DRY-RUN":
                    pnb_paper.record(
                        ticker, trade_side, trade_ask, contracts,
                        f"WEATHER-{trade_side.upper()}", m.get("close_time", ""),
                        conditions={
                            "noaa_high": noaa_high,
                            "threshold": threshold,
                            "margin_f":  round(signed_margin, 1),
                            "hist_rate": round(win_prob, 3),
                        }
                    )
                else:
                    pnb_state.record_buy(ticker, trade_side, trade_ask, contracts, order_id)
            results.append({
                "ticker": ticker, "side": trade_side, "ask": trade_ask,
                "ev": ev, "contracts": contracts, "order_id": order_id, "ok": ok
            })

    pnb_state.prune_expired(all_active)

    # Run adapt — may update thresholds based on settled paper outcomes
    adapt_changes = pnb_learn.adapt()
    for c in adapt_changes:
        log.info(f"[ADAPT] {c}")

    mode_tag = "[DRY-RUN] " if dry_run else ""
    if results:
        lines = [f"{mode_tag}PNB Weather — {datetime.now().strftime('%H:%M MST')}"]
        for res in results:
            status = "PLACED" if res["ok"] else "FAILED"
            lines.append(
                f"  {status} {res['ticker']} {res['side'].upper()} "
                f"x{res['contracts']} @ ${res['ask']:.2f} | EV {res['ev']:.0%}"
            )
        lines.append(f"Balance: ${balance_cents/100:.2f}")
        pnb_telegram.send("\n".join(lines))
    else:
        pnb_telegram.send(
            f"{mode_tag}PNB Weather — {datetime.now().strftime('%H:%M MST')}\n"
            f"No edge found.\nBalance: ${balance_cents/100:.2f}"
        )

    log.info(f"Scan complete | signals={len(results)} | balance=${balance_cents/100:.2f}")
    return results


if __name__ == "__main__":
    run()
