"""
PredictaNoob — State Tracker
Tracks held positions to prevent duplicate buys.
Persists to pnb_state.json in the same directory.
"""
import json, os
from datetime import date

STATE_PATH = "/home/rob-alvarado/RJA/.pnb/pnb_state.json"

def _load():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH) as f:
            return json.load(f)
    return {"held": {}, "daily_log": {}, "wins": 0, "losses": 0, "pending": 0}

def _save(state):
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)

def already_holds(ticker):
    """True if we currently hold a position in this ticker."""
    return ticker in _load()["held"]

def record_buy(ticker, side, price_dollars, count, order_id):
    """Called after a confirmed fill."""
    state = _load()
    state["held"][ticker] = {
        "side": side,
        "price": price_dollars,
        "count": count,
        "order_id": order_id,
        "date": str(date.today())
    }
    state["pending"] = state.get("pending", 0) + 1
    today = str(date.today())
    state.setdefault("daily_log", {}).setdefault(today, []).append({
        "action": "BUY", "ticker": ticker, "side": side,
        "price": price_dollars, "count": count, "order_id": order_id
    })
    _save(state)

def record_settlement(ticker, won):
    """Called when a contract settles. Removes from held, updates W/L."""
    state = _load()
    state["held"].pop(ticker, None)
    if won:
        state["wins"] = state.get("wins", 0) + 1
    else:
        state["losses"] = state.get("losses", 0) + 1
    state["pending"] = max(0, state.get("pending", 1) - 1)
    _save(state)

def check_settlements(auth_get):
    """
    Poll Kalshi for all held live positions. Record win/loss for any that
    have finalized. Called at the top of each scan cycle in live mode.
    auth_get = pnb_auth.get
    """
    state = _load()
    if not state["held"]:
        return
    changed = False
    for ticker, pos in list(state["held"].items()):
        r = auth_get(f"/markets/{ticker}")
        if r.status_code != 200:
            continue
        market = r.json().get("market", {})
        status = market.get("status", "")
        result = market.get("result", "")
        if status not in ("finalized", "closed") or not result:
            continue
        won = (result.lower() == pos["side"].lower())
        pnl = round(((1.0 - pos["price"]) if won else -pos["price"]) * pos["count"], 4)
        state["held"].pop(ticker)
        if won:
            state["wins"] = state.get("wins", 0) + 1
        else:
            state["losses"] = state.get("losses", 0) + 1
        state["pending"] = max(0, state.get("pending", 1) - 1)
        today = str(date.today())
        state.setdefault("daily_log", {}).setdefault(today, []).append({
            "action": "SETTLE", "ticker": ticker, "result": result,
            "won": won, "pnl": pnl
        })
        changed = True
    if changed:
        _save(state)

def daily_pnl():
    """Return today's realized P&L from the daily log (live trades only)."""
    state = _load()
    today = str(date.today())
    total = 0.0
    for entry in state.get("daily_log", {}).get(today, []):
        if entry.get("action") == "SETTLE":
            total += entry.get("pnl", 0)
    return round(total, 4)

def prune_expired(active_tickers):
    """Remove held entries that are no longer in active_tickers set."""
    state = _load()
    expired = [t for t in state["held"] if t not in active_tickers]
    for t in expired:
        state["held"].pop(t)
    if expired:
        _save(state)
    return expired

def summary():
    state = _load()
    return {
        "held_count": len(state["held"]),
        "held": list(state["held"].keys()),
        "wins": state.get("wins", 0),
        "losses": state.get("losses", 0),
        "pending": state.get("pending", 0)
    }
