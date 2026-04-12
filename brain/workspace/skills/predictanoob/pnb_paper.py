"""
PredictaNoob — Paper Trade Tracker
Records every DRY-RUN signal and checks settlement outcomes against Kalshi.
Without this, DRY-RUN is just watching. With this, it's a live backtest.
"""
import json, os, uuid
from datetime import datetime, timezone
import pnb_auth

PAPER_PATH = "/home/rob-alvarado/RJA/.pnb/pnb_paper.json"


def _load():
    if os.path.exists(PAPER_PATH):
        with open(PAPER_PATH) as f:
            return json.load(f)
    return {"trades": []}


def _save(data):
    with open(PAPER_PATH, "w") as f:
        json.dump(data, f, indent=2)


def already_holds(ticker):
    """True if we have an unsettled paper trade on this ticker."""
    data = _load()
    return any(t["ticker"] == ticker and not t["settled"] for t in data["trades"])


def record(ticker, side, price, contracts, signal, close_time):
    """Log a simulated trade entry. Skips if already holding this ticker."""
    if already_holds(ticker):
        return False
    data = _load()
    data["trades"].append({
        "id":         str(uuid.uuid4())[:8],
        "ts":         datetime.now().strftime("%Y-%m-%d %H:%M"),
        "ticker":     ticker,
        "side":       side,
        "price":      round(price, 4),
        "contracts":  contracts,
        "signal":     signal,
        "close_time": close_time,
        "settled":    False,
        "result":     None,
        "pnl":        None,
    })
    _save(data)


def check_settlements():
    """
    Poll Kalshi for any unsettled paper trades. Record win/loss and P&L.
    Call this at the start of each scan cycle.
    """
    data = _load()
    pending = [t for t in data["trades"] if not t["settled"]]
    if not pending:
        return

    for trade in pending:
        r = pnb_auth.get(f"/markets/{trade['ticker']}")
        if r.status_code != 200:
            continue

        market = r.json().get("market", {})
        status = market.get("status", "")
        result = market.get("result", "")   # "yes", "no", or ""

        if status not in ("finalized", "closed") or not result:
            continue

        won = (result.lower() == trade["side"].lower())
        if won:
            pnl = round((1.0 - trade["price"]) * trade["contracts"], 4)
        else:
            pnl = round(-trade["price"] * trade["contracts"], 4)

        trade["settled"] = True
        trade["result"]  = result.lower()
        trade["won"]     = won
        trade["pnl"]     = pnl

    _save(data)


def summary():
    """Return W/L/pending counts and total P&L for status reporting."""
    data = _load()
    settled = [t for t in data["trades"] if t["settled"]]
    pending = [t for t in data["trades"] if not t["settled"]]
    wins    = [t for t in settled if t.get("won")]
    losses  = [t for t in settled if not t.get("won")]
    total_pnl = sum(t["pnl"] for t in settled)
    win_rate  = len(wins) / len(settled) if settled else None

    return {
        "wins":      len(wins),
        "losses":    len(losses),
        "pending":   len(pending),
        "total_pnl": round(total_pnl, 4),
        "win_rate":  win_rate,
        "trades":    settled[-10:],   # last 10 settled for display
    }


def recent_trades(n=5):
    """Return last N trades (settled or not) for status display."""
    data = _load()
    return data["trades"][-n:]
