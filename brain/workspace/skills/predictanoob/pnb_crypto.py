"""
PredictaNoob — Crypto Engine v2
Strategy: KXBTC15M (15-min BTC direction contracts on Kalshi)

Signal stack (all three must agree to trade):
  1. Becker Optimism Bias   — YES ask outside threshold band
  2. BTC Momentum           — yfinance 1-min bars confirm price direction
  3. Orderbook Skew         — Kalshi depth confirms crowd leaning

EV model: fee-aware (Kalshi charges 7% of C × P × (1-P))
Mode: continuous loop via systemd — wakes every LOOP_INTERVAL_S seconds,
      evaluates markets, trades at most once per 15-min window.
"""
import re, time, logging, signal, sys
from datetime import datetime, timezone, timedelta

import yfinance as yf
import numpy as np

import pnb_auth, pnb_state, pnb_telegram, pnb_learn, pnb_paper
from pnb_config import (
    CRYPTO_SERIES, LOOP_INTERVAL_S, BECKER_YES_CEILING, BECKER_YES_FLOOR,
    MOMENTUM_LOOKBACK_BARS, MOMENTUM_BEARISH_THRESH, MOMENTUM_BULLISH_THRESH,
    SKEW_NO_CONFIRM, KALSHI_FEE_RATE, MIN_EV, MIN_MINUTES_TO_CLOSE,
    MIN_VOLUME, MIN_PRICE, HALT_BELOW_CENTS,
    KELLY_FRACTION, KELLY_MAX_CONTRACTS, KELLY_MIN_CONTRACTS,
    MAX_MINUTES_TO_CLOSE,
)

LOG_PATH = "/home/rob-alvarado/RJA/.pnb/pnb_crypto.log"
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
log = logging.getLogger("pnb_crypto")

_running = True

def handle_sigterm(sig, frame):
    global _running
    log.info("SIGTERM received — shutting down cleanly")
    _running = False

signal.signal(signal.SIGTERM, handle_sigterm)
signal.signal(signal.SIGINT, handle_sigterm)


# ─── Signal: BTC Momentum ─────────────────────────────────────────────────────

def btc_momentum():
    """
    Fetch last N+1 1-min BTC/USD bars from yfinance.
    Returns (direction, slope_pct_per_bar):
      direction: 'bearish', 'bullish', or 'neutral'
      slope: average % change per bar (signed)
    """
    try:
        df = yf.download("BTC-USD", period="1d", interval="1m", progress=False, auto_adjust=True)
        if df is None or len(df) < MOMENTUM_LOOKBACK_BARS + 1:
            log.warning("Momentum: insufficient BTC bars — treating as neutral")
            return "neutral", 0.0

        closes = df["Close"].dropna().values
        recent = closes[-(MOMENTUM_LOOKBACK_BARS + 1):]
        pct_changes = np.diff(recent) / recent[:-1]
        slope = float(np.mean(pct_changes))

        if slope <= MOMENTUM_BEARISH_THRESH:
            direction = "bearish"
        elif slope >= MOMENTUM_BULLISH_THRESH:
            direction = "bullish"
        else:
            direction = "neutral"

        log.info(f"Momentum: slope={slope:.5f} → {direction}")
        return direction, slope
    except Exception as e:
        log.warning(f"Momentum fetch error: {e}")
        return "neutral", 0.0


# ─── Signal: Orderbook Skew ───────────────────────────────────────────────────

def orderbook_skew(ticker):
    """
    Pull Kalshi orderbook for ticker.
    Returns ratio = sum(NO ask sizes) / sum(YES ask sizes).
    ratio > SKEW_NO_CONFIRM → crowd is on YES side (NO has depth advantage).
    Returns None on failure.
    """
    try:
        r = pnb_auth.get(f"/markets/{ticker}/orderbook")
        if r.status_code != 200:
            log.warning(f"Orderbook fetch failed: {r.status_code}")
            return None
        ob = r.json().get("orderbook", {})
        yes_asks = ob.get("yes", [])   # [[price, size], ...]
        no_asks  = ob.get("no",  [])

        # Sum top 10 levels by size
        yes_depth = sum(s for _, s in yes_asks[:10]) if yes_asks else 0
        no_depth  = sum(s for _, s in no_asks[:10])  if no_asks  else 0

        if yes_depth == 0:
            return None
        ratio = no_depth / yes_depth
        log.info(f"Orderbook skew {ticker}: NO/YES={ratio:.2f} (yes_depth={yes_depth} no_depth={no_depth})")
        return ratio
    except Exception as e:
        log.warning(f"Orderbook error: {e}")
        return None


# ─── Kelly Sizing ─────────────────────────────────────────────────────────────

def kelly_contracts(win_prob, ask_dollars, balance_cents):
    """Fractional binary Kelly capped at KELLY_MAX_CONTRACTS."""
    if ask_dollars <= 0 or ask_dollars >= 1:
        return KELLY_MIN_CONTRACTS
    fee    = KALSHI_FEE_RATE * ask_dollars * (1.0 - ask_dollars)
    profit = (1.0 - ask_dollars) - fee
    loss   = ask_dollars + fee
    b = profit / loss
    if b <= 0:
        return KELLY_MIN_CONTRACTS
    f = max(0.0, (win_prob * (b + 1) - 1) / b) * KELLY_FRACTION
    dollar_amount = f * (balance_cents / 100)
    contracts = max(KELLY_MIN_CONTRACTS, round(dollar_amount / ask_dollars))
    return min(contracts, KELLY_MAX_CONTRACTS)


# ─── EV: Fee-Aware ────────────────────────────────────────────────────────────

def fee_adjusted_ev(win_prob, ask_dollars, contracts=1):
    """
    Kalshi fee = 0.07 × C × P × (1-P)  where P = (1 - ask_dollars)
    Win payout = $1.00 per contract
    Net profit if win  = (1.0 - ask_dollars) - fee
    Net loss if lose   = ask_dollars + fee   (we lose our stake + paid the fee)

    Actually Kalshi fee is charged on fill regardless — we approximate:
    fee = KALSHI_FEE_RATE × contracts × ask_dollars × (1 - ask_dollars)
    """
    fee      = KALSHI_FEE_RATE * contracts * ask_dollars * (1.0 - ask_dollars)
    profit   = (1.0 - ask_dollars) - fee
    loss     = ask_dollars + fee
    ev       = (win_prob * profit) - ((1 - win_prob) * loss)
    return ev, fee


# ─── Win Probability ─────────────────────────────────────────────────────────

def no_win_prob(yes_ask):
    """Conservative: 52% base + scaled excess, capped at 60%."""
    excess = yes_ask - BECKER_YES_CEILING
    return min(0.60, 0.52 + excess * 0.5)

def yes_win_prob(yes_ask):
    """Conservative: 52% base + scaled deficit, capped at 60%."""
    deficit = BECKER_YES_FLOOR - yes_ask
    return min(0.60, 0.52 + deficit * 0.5)


# ─── Order Placement ─────────────────────────────────────────────────────────

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


# ─── Single Scan Cycle ────────────────────────────────────────────────────────

def scan_once(dry_run, balance_cents):
    """
    Evaluate one scan cycle. Returns a result dict for the hourly summary, or None
    if there was nothing to evaluate (between windows, already holding, etc.).

    Result dict keys:
      evaluated: bool — True if we got to signal analysis
      signal:    bool — True if all signals aligned
      ok:        bool — order placed successfully (only if signal=True)
      ticker, side, ask, contracts, ev, signal_name, momentum, skew_str
    """
    now = datetime.now(timezone.utc)

    # Check outcomes of any pending paper trades
    if dry_run:
        pnb_paper.check_settlements()

    # Fetch open KXBTC15M markets
    r = pnb_auth.get("/markets", params={"series_ticker": CRYPTO_SERIES, "limit": 5, "status": "open"})
    if r.status_code != 200:
        log.error(f"Market fetch failed: {r.status_code}")
        return None

    markets = r.json().get("markets", [])
    if not markets:
        log.info("No open KXBTC15M markets — between windows or outside hours")
        return None

    # Prune expired positions from state
    active_tickers = {m["ticker"] for m in markets}
    pnb_state.prune_expired(active_tickers)

    # Skip if already holding a KXBTC15M contract
    held = pnb_state.summary()["held"]
    btc_held = [t for t in held if t.startswith("KXBTC15M")]
    if btc_held:
        log.info(f"Already holding: {btc_held} — waiting for expiry")
        return None

    # Pick most liquid market
    market = sorted(markets, key=lambda m: float(m.get("volume_fp") or 0), reverse=True)[0]
    ticker  = market["ticker"]
    yes_ask = float(market.get("yes_ask_dollars") or 0)
    no_ask  = float(market.get("no_ask_dollars") or 0)
    volume  = float(market.get("volume_fp") or 0)
    if yes_ask < MIN_PRICE or no_ask < MIN_PRICE:
        log.info(f"Untraded {ticker} (yes=${yes_ask:.2f} no=${no_ask:.2f}) — skipping")
        return None
    if volume < MIN_VOLUME:
        log.info(f"Low volume {ticker} ({volume:.0f} < {MIN_VOLUME}) — skipping")
        return None

    # Time-to-close filter
    try:
        close_dt = datetime.fromisoformat(market.get("close_time", "").replace("Z", "+00:00"))
        minutes_left = (close_dt - now).total_seconds() / 60
    except Exception:
        minutes_left = 999
    if minutes_left < MIN_MINUTES_TO_CLOSE:
        log.info(f"Near expiry {ticker} ({minutes_left:.1f}min) — waiting for next window")
        return None
    if minutes_left > MAX_MINUTES_TO_CLOSE:
        log.info(f"Too early {ticker} ({minutes_left:.1f}min) — pricing inefficient, skipping")
        return None

    log.info(f"Evaluating {ticker} | YES=${yes_ask:.2f} NO=${no_ask:.2f} | {minutes_left:.0f}min | vol={volume:.0f}")

    # Record for learning engine (always, not just on signal)
    pnb_learn.record_crypto_price(ticker, yes_ask, no_ask, minutes_left, None)

    # ── Signal 1: Becker Bias ──────────────────────────────────────────────
    if yes_ask > BECKER_YES_CEILING:
        becker_side = "no"
        becker_ask  = no_ask
        win_prob    = no_win_prob(yes_ask)
        becker_signal = "BECKER-NO"
    elif BECKER_YES_FLOOR > 0 and yes_ask < BECKER_YES_FLOOR:
        becker_side = "yes"
        becker_ask  = yes_ask
        win_prob    = yes_win_prob(yes_ask)
        becker_signal = "BECKER-YES"
    else:
        log.info(f"Neutral zone YES=${yes_ask:.2f} — no Becker signal")
        return {"evaluated": True, "signal": False, "reason": f"neutral YES=${yes_ask:.2f}", "ticker": ticker}

    # ── Signal 2: BTC Momentum ────────────────────────────────────────────
    momentum_dir, slope = btc_momentum()
    if becker_side == "no" and momentum_dir == "bullish":
        log.info(f"Momentum conflict: Becker-NO but BTC trending bullish ({slope:.5f}) — skipping")
        return {"evaluated": True, "signal": False, "reason": f"momentum conflict (bullish)", "ticker": ticker}
    if becker_side == "yes" and momentum_dir == "bearish":
        log.info(f"Momentum conflict: Becker-YES but BTC trending bearish ({slope:.5f}) — skipping")
        return {"evaluated": True, "signal": False, "reason": f"momentum conflict (bearish)", "ticker": ticker}

    # ── Signal 3: Orderbook Skew ──────────────────────────────────────────
    skew = orderbook_skew(ticker)
    if skew is not None:
        if becker_side == "no" and skew < SKEW_NO_CONFIRM:
            log.info(f"Skew not confirming NO trade (NO/YES={skew:.2f} < {SKEW_NO_CONFIRM}) — skipping")
            return {"evaluated": True, "signal": False, "reason": f"skew={skew:.2f} < {SKEW_NO_CONFIRM}", "ticker": ticker}
    else:
        log.info("Orderbook unavailable — proceeding without skew confirmation")

    # ── EV Check ─────────────────────────────────────────────────────────
    contracts = kelly_contracts(win_prob, becker_ask, balance_cents)
    ev, fee = fee_adjusted_ev(win_prob, becker_ask, contracts)
    if ev < MIN_EV:
        log.info(f"EV {ev:.1%} (fee=${fee:.3f}) below {MIN_EV:.0%} minimum — skipping")
        return {"evaluated": True, "signal": False, "reason": f"EV={ev:.1%} < {MIN_EV:.0%}", "ticker": ticker}

    skew_str = f"{skew:.2f}" if skew is not None else "N/A"
    log.info(
        f"ALL SIGNALS ALIGN: {becker_signal} | momentum={momentum_dir} | skew={skew_str} | "
        f"win_prob={win_prob:.0%} | EV={ev:.1%} (fee=${fee:.3f}) | kelly={contracts}c"
    )

    # ── Execute ───────────────────────────────────────────────────────────
    ok, order_id, msg = place_order(ticker, becker_side, becker_ask, contracts, dry_run)
    if ok:
        if order_id == "DRY-RUN":
            pnb_paper.record(ticker, becker_side, becker_ask, contracts, becker_signal,
                             market.get("close_time", ""))
        else:
            pnb_state.record_buy(ticker, becker_side, becker_ask, contracts, order_id)
        pnb_learn.record_crypto_price(ticker, yes_ask, no_ask, minutes_left, becker_signal)

    return {
        "evaluated": True,
        "signal":    True,
        "ok":        ok,
        "ticker":    ticker,
        "side":      becker_side,
        "ask":       becker_ask,
        "contracts": contracts,
        "ev":        ev,
        "signal_name": becker_signal,
        "momentum":  momentum_dir,
        "skew_str":  skew_str,
        "win_prob":  win_prob,
        "fee":       fee,
    }


# ─── Main Loop ───────────────────────────────────────────────────────────────

HOURLY_INTERVAL_S = 3600

def run():
    global _running
    dry_run = not pnb_auth.is_live()
    mode = "DRY-RUN" if dry_run else "LIVE"
    log.info(f"=== PredictaNoob Crypto Engine v2 START | {mode} ===")
    pnb_telegram.send(f"PNB Crypto Engine v2 started ({mode})")

    last_hourly   = time.time()
    hour_windows  = 0   # distinct 15-min windows evaluated
    hour_signals  = []  # signal result dicts (fired trades)
    seen_tickers  = set()

    while _running:
        try:
            # Balance check every cycle
            bal_r = pnb_auth.get("/portfolio/balance")
            if bal_r.status_code != 200:
                log.error(f"Balance check failed: {bal_r.text[:100]}")
                time.sleep(LOOP_INTERVAL_S)
                continue

            balance_cents = bal_r.json().get("balance", 0)
            if balance_cents < HALT_BELOW_CENTS:
                log.warning(f"Balance ${balance_cents/100:.2f} below halt — sleeping 5min")
                time.sleep(300)
                continue

            result = scan_once(dry_run, balance_cents)

            # Track evaluated windows (count each ticker once per hour)
            if result and result.get("evaluated"):
                t = result.get("ticker", "")
                if t and t not in seen_tickers:
                    hour_windows += 1
                    seen_tickers.add(t)
                if result.get("signal"):
                    hour_signals.append(result)

            # ── Hourly summary ────────────────────────────────────────────
            if time.time() - last_hourly >= HOURLY_INTERVAL_S:
                mode_tag = "[DRY-RUN] " if dry_run else ""
                ts = datetime.now().strftime("%H:%M MST")
                paper = pnb_paper.summary()
                win_rate_str = f"{paper['win_rate']:.0%}" if paper['win_rate'] is not None else "n/a"

                lines = [
                    f"{mode_tag}PNB Crypto — {ts}",
                    f"Windows: {hour_windows} | Signals: {len(hour_signals)}",
                ]
                if hour_signals:
                    for s in hour_signals:
                        status = "PLACED" if s["ok"] else "FAILED"
                        lines.append(
                            f"  {status} {s['ticker']} {s['side'].upper()} "
                            f"x{s['contracts']} @ ${s['ask']:.2f} | EV {s['ev']:.0%}"
                        )
                else:
                    lines.append("  No edge found this hour")

                lines += [
                    f"Paper: {paper['wins']}W/{paper['losses']}L  win rate: {win_rate_str}  P&L: ${paper['total_pnl']:+.2f}",
                    f"Balance: ${balance_cents/100:.2f}",
                ]
                pnb_telegram.send("\n".join(lines))
                log.info(f"Hourly summary sent | windows={hour_windows} signals={len(hour_signals)}")

                # Reset counters
                last_hourly  = time.time()
                hour_windows = 0
                hour_signals = []
                seen_tickers = set()

        except Exception as e:
            log.exception(f"Unhandled error in scan loop: {e}")

        time.sleep(LOOP_INTERVAL_S)

    log.info("=== PredictaNoob Crypto Engine STOPPED ===")


if __name__ == "__main__":
    run()
