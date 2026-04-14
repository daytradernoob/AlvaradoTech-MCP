"""
PredictaNoob -- Learning Engine v2

Real learning loop:
  1. analyze()   -- reads settled paper trades, computes per-signal win rates
  2. adapt()     -- once a signal has MIN_ADAPT_TRADES settled, auto-adjusts
                    thresholds in pnb_config_overrides.json
  3. pnb_config  -- loads overrides at import time (defaults + overrides)

Status report shows actual signal performance, not just aggregate W/L.
"""
import json, os, logging
from datetime import date, datetime

LEARN_PATH     = "/home/rob-alvarado/RJA/.pnb/pnb_learn.json"
PAPER_PATH     = "/home/rob-alvarado/RJA/.pnb/pnb_paper.json"
OVERRIDES_PATH = "/home/rob-alvarado/RJA/.pnb/pnb_config_overrides.json"

MIN_ADAPT_TRADES = 20   # Don't auto-adjust until we have this many settled trades per signal
MIN_WIN_PROB_TRADES = 15  # Use observed win rate once we have this many settled trades

log = logging.getLogger("pnb_learn")


# ─── Raw data storage (prices seen, weather near-misses) ─────────────────────

def _load():
    if os.path.exists(LEARN_PATH):
        with open(LEARN_PATH) as f:
            return json.load(f)
    return {
        "weather_near_misses": [],
        "crypto_prices_seen": [],
        "crypto_signals_fired": [],
        "weather_signals_fired": [],
    }

def _save(data):
    with open(LEARN_PATH, "w") as f:
        json.dump(data, f, indent=2)

def record_weather_skip(ticker, city, reason, hist_no_rate, margin_f, yes_ask, threshold):
    data = _load()
    data["weather_near_misses"].append({
        "date":          str(date.today()),
        "ticker":        ticker,
        "city":          city,
        "reason":        reason,
        "hist_no_rate":  round(hist_no_rate, 3) if hist_no_rate else None,
        "margin_f":      round(margin_f, 1) if margin_f else None,
        "yes_ask":       round(yes_ask, 2),
        "threshold":     threshold,
    })
    data["weather_near_misses"] = data["weather_near_misses"][-200:]
    _save(data)

def record_crypto_price(ticker, yes_ask, no_ask, minutes_left, signal_fired):
    data = _load()
    data["crypto_prices_seen"].append({
        "ts":           datetime.now().strftime("%Y-%m-%d %H:%M"),
        "ticker":       ticker,
        "yes_ask":      round(yes_ask, 2),
        "no_ask":       round(no_ask, 2),
        "minutes_left": round(minutes_left, 1),
        "signal":       signal_fired,
    })
    data["crypto_prices_seen"] = data["crypto_prices_seen"][-500:]
    _save(data)


# ─── Signal performance from paper trades ────────────────────────────────────

def _load_paper():
    if not os.path.exists(PAPER_PATH):
        return []
    with open(PAPER_PATH) as f:
        return json.load(f).get("trades", [])

def signal_stats():
    """
    Group settled paper trades by signal type.
    Returns dict: { signal_name: {wins, losses, total, win_rate, avg_pnl} }
    """
    trades = _load_paper()
    settled = [t for t in trades if t.get("settled")]

    stats = {}
    for t in settled:
        sig = t.get("signal", "UNKNOWN")
        if sig not in stats:
            stats[sig] = {"wins": 0, "losses": 0, "pnl": 0.0}
        if t.get("won"):
            stats[sig]["wins"] += 1
        else:
            stats[sig]["losses"] += 1
        stats[sig]["pnl"] += t.get("pnl") or 0.0

    result = {}
    for sig, s in stats.items():
        total = s["wins"] + s["losses"]
        result[sig] = {
            "wins":     s["wins"],
            "losses":   s["losses"],
            "total":    total,
            "win_rate": s["wins"] / total if total else None,
            "avg_pnl":  round(s["pnl"] / total, 4) if total else None,
            "total_pnl": round(s["pnl"], 4),
        }
    return result


# ─── Config overrides (auto-adapt) ───────────────────────────────────────────

def _load_overrides():
    if os.path.exists(OVERRIDES_PATH):
        with open(OVERRIDES_PATH) as f:
            return json.load(f)
    return {}

def _save_overrides(overrides):
    with open(OVERRIDES_PATH, "w") as f:
        json.dump(overrides, f, indent=2)
    log.info(f"Config overrides updated: {overrides}")

def get_win_prob(signal_name, fallback):
    """
    Return observed win rate for signal_name if we have MIN_WIN_PROB_TRADES settled trades.
    Falls back to the static estimate otherwise.
    """
    stats = signal_stats()
    s = stats.get(signal_name)
    if s and s["total"] >= MIN_WIN_PROB_TRADES and s["win_rate"] is not None:
        return s["win_rate"]
    return fallback


def adapt():
    """
    Auto-adjust thresholds based on signal win rates once MIN_ADAPT_TRADES settled.

    BECKER-NO rules:
      - win rate < 45%  → raise BECKER_YES_CEILING by 0.03 (be more selective)
      - win rate > 70%  → lower BECKER_YES_CEILING by 0.02 (capture more trades)
      - BECKER_YES_CEILING clamped to [0.52, 0.72]

    WEATHER rules:
      - overall weather win rate < 55% → raise MIN_HIST_RATE by 0.03
      - overall weather win rate > 75% → lower MIN_HIST_RATE by 0.02
      - MIN_HIST_RATE clamped to [0.60, 0.80]

    Returns list of changes made (empty if none).
    """
    from pnb_config import BECKER_YES_CEILING, MIN_HIST_RATE

    stats    = signal_stats()
    overrides = _load_overrides()
    changes  = []

    # ── BECKER-NO adaptation ──────────────────────────────────────────────
    bno = stats.get("BECKER-NO")
    if bno and bno["total"] >= MIN_ADAPT_TRADES:
        current_ceiling = overrides.get("BECKER_YES_CEILING", BECKER_YES_CEILING)
        wr = bno["win_rate"]
        new_ceiling = None
        if wr < 0.45:
            new_ceiling = round(min(0.72, current_ceiling + 0.03), 2)
            changes.append(f"BECKER_YES_CEILING {current_ceiling:.2f} → {new_ceiling:.2f} (BECKER-NO win rate {wr:.0%} < 45%)")
        elif wr > 0.70:
            new_ceiling = round(max(0.52, current_ceiling - 0.02), 2)
            changes.append(f"BECKER_YES_CEILING {current_ceiling:.2f} → {new_ceiling:.2f} (BECKER-NO win rate {wr:.0%} > 70%)")
        if new_ceiling is not None:
            overrides["BECKER_YES_CEILING"] = new_ceiling

    # ── Weather adaptation ────────────────────────────────────────────────
    weather_sigs = {k: v for k, v in stats.items() if k.startswith("WEATHER")}
    w_wins   = sum(v["wins"]   for v in weather_sigs.values())
    w_losses = sum(v["losses"] for v in weather_sigs.values())
    w_total  = w_wins + w_losses
    if w_total >= MIN_ADAPT_TRADES:
        current_rate = overrides.get("MIN_HIST_RATE", MIN_HIST_RATE)
        wr = w_wins / w_total
        new_rate = None
        if wr < 0.55:
            new_rate = round(min(0.80, current_rate + 0.03), 2)
            changes.append(f"MIN_HIST_RATE {current_rate:.2f} → {new_rate:.2f} (weather win rate {wr:.0%} < 55%)")
        elif wr > 0.75:
            new_rate = round(max(0.60, current_rate - 0.02), 2)
            changes.append(f"MIN_HIST_RATE {current_rate:.2f} → {new_rate:.2f} (weather win rate {wr:.0%} > 75%)")
        if new_rate is not None:
            overrides["MIN_HIST_RATE"] = new_rate

    if changes:
        _save_overrides(overrides)
        # Restart pnb-crypto so it reloads pnb_config with new overrides
        import subprocess
        try:
            subprocess.Popen(["systemctl", "--user", "restart", "pnb-crypto"])
            log.info("Triggered pnb-crypto restart to apply config changes")
        except Exception as e:
            log.warning(f"Could not restart pnb-crypto: {e}")

    return changes


# ─── analyze() — called by pnb_status ────────────────────────────────────────

def condition_analysis():
    """
    Break down BECKER-NO win rates by entry conditions.
    Requires trades to have 'conditions' field (added 2026-04-14).
    Returns dict of condition splits with win rates.
    """
    trades = _load_paper()
    settled = [t for t in trades if t.get("settled") and t.get("conditions")]
    if not settled:
        return {}

    result = {}

    # Split by momentum direction
    momentum_groups = {}
    for t in settled:
        if t.get("signal") != "BECKER-NO":
            continue
        m = t["conditions"].get("momentum", "unknown")
        if m not in momentum_groups:
            momentum_groups[m] = {"wins": 0, "losses": 0}
        if t["won"]:
            momentum_groups[m]["wins"] += 1
        else:
            momentum_groups[m]["losses"] += 1

    if momentum_groups:
        result["becker_no_by_momentum"] = {}
        for m, s in momentum_groups.items():
            total = s["wins"] + s["losses"]
            result["becker_no_by_momentum"][m] = {
                "wins": s["wins"], "losses": s["losses"],
                "win_rate": round(s["wins"] / total, 3) if total else None,
            }

    # Split by minutes_left bucket (early 8-20min vs late 20-50min)
    time_groups = {"early (8-20min)": {"wins": 0, "losses": 0},
                   "late (20-50min)":  {"wins": 0, "losses": 0}}
    for t in settled:
        if t.get("signal") != "BECKER-NO":
            continue
        mins = t["conditions"].get("minutes_left", 0)
        bucket = "early (8-20min)" if mins <= 20 else "late (20-50min)"
        if t["won"]:
            time_groups[bucket]["wins"] += 1
        else:
            time_groups[bucket]["losses"] += 1

    result["becker_no_by_time"] = {}
    for bucket, s in time_groups.items():
        total = s["wins"] + s["losses"]
        if total:
            result["becker_no_by_time"][bucket] = {
                "wins": s["wins"], "losses": s["losses"],
                "win_rate": round(s["wins"] / total, 3),
            }

    return result


def live_readiness():
    """Check if paper performance meets criteria to go live."""
    from pnb_config import LIVE_MIN_TRADES, LIVE_MIN_WIN_RATE, LIVE_MIN_PNL
    trades = _load_paper()
    settled = [t for t in trades if t.get("settled")]
    if not settled:
        return {"ready": False, "reason": "no settled trades"}
    wins = [t for t in settled if t.get("won")]
    total_pnl = sum(t.get("pnl") or 0 for t in settled)
    win_rate = len(wins) / len(settled)
    checks = {
        f"trades >= {LIVE_MIN_TRADES}":    len(settled) >= LIVE_MIN_TRADES,
        f"win_rate >= {LIVE_MIN_WIN_RATE:.0%}": win_rate >= LIVE_MIN_WIN_RATE,
        f"P&L >= ${LIVE_MIN_PNL:.2f}":     total_pnl >= LIVE_MIN_PNL,
    }
    ready = all(checks.values())
    return {
        "ready":    ready,
        "checks":   checks,
        "trades":   len(settled),
        "win_rate": round(win_rate, 3),
        "pnl":      round(total_pnl, 2),
    }


def analyze():
    """
    Return performance summary for the status report.
    Pulls from actual paper trade outcomes, not just price observations.
    """
    data  = _load()
    today = date.today()
    stats = signal_stats()

    # Run adapt and log any threshold changes
    changes = adapt()
    if changes:
        for c in changes:
            log.info(f"[ADAPT] {c}")

    # ── Weather near-misses (last 7d) ────────────────────────────────────
    recent_weather = [
        e for e in data["weather_near_misses"]
        if (today - date.fromisoformat(e["date"])).days <= 7
    ]
    rate_misses = sorted(
        [e for e in recent_weather if e.get("reason", "").startswith("hist")],
        key=lambda e: e.get("hist_no_rate") or 0, reverse=True
    )
    weather_rec = None
    if rate_misses:
        best = rate_misses[0]
        gap = (best["hist_no_rate"] or 0)
        if best["hist_no_rate"] and (0.70 - best["hist_no_rate"]) < 0.08:
            weather_rec = f"Near-miss: {best['city']} at {best['hist_no_rate']:.0%} hist (need 70%). Gap={0.70 - best['hist_no_rate']:.0%}"

    # ── Crypto price distribution (last 7d) ──────────────────────────────
    recent_crypto = [
        e for e in data["crypto_prices_seen"]
        if (today - date.fromisoformat(e["ts"][:10])).days <= 7
    ]
    yes_prices    = [e["yes_ask"] for e in recent_crypto if e["yes_ask"] > 0.05]
    above_ceiling = [p for p in yes_prices if p > 0.55]
    crypto_rec    = None
    if yes_prices:
        avg_yes   = sum(yes_prices) / len(yes_prices)
        pct_above = len(above_ceiling) / len(yes_prices) * 100
        if pct_above < 5:
            crypto_rec = f"Only {pct_above:.0f}% of YES asks above 0.55 ceiling (avg ${avg_yes:.2f}) — Becker signal rare"

    return {
        "signal_stats":     stats,
        "adapt_changes":    changes,
        "condition_analysis": condition_analysis(),
        "live_readiness":   live_readiness(),
        "weather": {
            "near_misses_7d":    len(recent_weather),
            "closest_rate_miss": rate_misses[0] if rate_misses else None,
            "recommendation":    weather_rec,
        },
        "crypto": {
            "prices_evaluated":  len(yes_prices),
            "avg_yes_ask":       round(sum(yes_prices)/len(yes_prices), 2) if yes_prices else None,
            "pct_above_ceiling": round(len(above_ceiling)/len(yes_prices)*100, 1) if yes_prices else None,
            "signals_fired_7d":  len([e for e in recent_crypto if e.get("signal")]),
            "recommendation":    crypto_rec,
        },
    }
