"""
PredictaNoob — Self-Healing Watchdog
Detects problems, applies fixes, reports actions taken.
No human in the loop for known failure modes.

Problem → Root cause → Fix → Report. That's the loop.
"""
import json, os, subprocess, logging
from datetime import datetime

import pnb_telegram, pnb_learn, pnb_config

LOG_PATH   = "/home/rob-alvarado/RJA/.pnb/pnb_watchdog.log"
STATE_PATH = "/home/rob-alvarado/RJA/.pnb/pnb_watchdog_state.json"
PAPER_PATH = "/home/rob-alvarado/RJA/.pnb/pnb_paper.json"
OVERRIDES_PATH = "/home/rob-alvarado/RJA/.pnb/pnb_config_overrides.json"

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
log = logging.getLogger("pnb_watchdog")


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _load_paper():
    if not os.path.exists(PAPER_PATH):
        return []
    with open(PAPER_PATH) as f:
        return json.load(f).get("trades", [])

def _load_state():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH) as f:
            return json.load(f)
    return {}

def _save_state(state):
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)

def _load_overrides():
    if os.path.exists(OVERRIDES_PATH):
        with open(OVERRIDES_PATH) as f:
            return json.load(f)
    return {}

def _save_overrides(overrides):
    with open(OVERRIDES_PATH, "w") as f:
        json.dump(overrides, f, indent=2)

def _restart_crypto():
    subprocess.Popen(["systemctl", "--user", "restart", "pnb-crypto"])
    log.info("Triggered pnb-crypto restart")


# ─── Remediations ────────────────────────────────────────────────────────────

def fix_stop_loss_rate(sig, sl_rate, overrides):
    """Stop loss rate too high — disable stop loss."""
    overrides["STOP_LOSS_PCT"] = 0.0
    _save_overrides(overrides)
    _restart_crypto()
    return (
        f"FIXED: Stop loss disabled. {sig} had {sl_rate:.0%} exit rate — "
        f"mid-window volatility was shaking out winning trades. "
        f"Let contracts settle naturally."
    )

def fix_win_rate_decay(last20_wr, overall_wr, overrides):
    """Win rate decaying on recent trades — tighten ceiling further."""
    current = overrides.get("BECKER_YES_CEILING", pnb_config.BECKER_YES_CEILING)
    new_ceiling = round(min(0.72, current + 0.03), 2)
    overrides["BECKER_YES_CEILING"] = new_ceiling
    bno_nat = len([t for t in _load_paper()
                   if t.get("settled") and t.get("result") in ("yes","no")
                   and t.get("signal") == "BECKER-NO"])
    overrides["_last_bno_total"] = bno_nat
    _save_overrides(overrides)
    _restart_crypto()
    return (
        f"FIXED: BECKER_YES_CEILING raised {current:.2f} → {new_ceiling:.2f}. "
        f"Last 20 win rate {last20_wr:.0%} vs overall {overall_wr:.0%} — "
        f"being more selective about entry."
    )

def fix_signal_drought(hours_since):
    """No signals in 6+ hours — restart service in case it's stuck."""
    _restart_crypto()
    return (
        f"FIXED: Restarted pnb-crypto after {hours_since:.0f}h signal drought. "
        f"Service may have been stuck."
    )

def fix_pnl_regression(pnl_drop, total_pnl, overrides):
    """P&L dropped significantly — reduce Kelly sizing as protection."""
    current_kelly = overrides.get("KELLY_MAX_CONTRACTS", pnb_config.KELLY_MAX_CONTRACTS)
    if current_kelly > 1:
        new_kelly = max(1, current_kelly - 1)
        overrides["KELLY_MAX_CONTRACTS"] = new_kelly
        _save_overrides(overrides)
        _restart_crypto()
        return (
            f"FIXED: KELLY_MAX_CONTRACTS reduced {current_kelly} → {new_kelly}. "
            f"P&L dropped ${pnl_drop:.2f} (now ${total_pnl:.2f}). "
            f"Reducing position size until recovered."
        )
    return None

def fix_adapt_stall(new_since_adapt, bno_wr, overrides):
    """adapt() stalled — force it regardless of trade count threshold."""
    current = overrides.get("BECKER_YES_CEILING", pnb_config.BECKER_YES_CEILING)
    new_ceiling = round(min(0.72, current + 0.03), 2)
    overrides["BECKER_YES_CEILING"] = new_ceiling
    bno_nat = len([t for t in _load_paper()
                   if t.get("settled") and t.get("result") in ("yes","no")
                   and t.get("signal") == "BECKER-NO"])
    overrides["_last_bno_total"] = bno_nat
    _save_overrides(overrides)
    _restart_crypto()
    return (
        f"FIXED: Forced adapt — BECKER_YES_CEILING {current:.2f} → {new_ceiling:.2f}. "
        f"{new_since_adapt} trades accumulated with {bno_wr:.0%} win rate. "
        f"adapt() guard was blocking adjustment."
    )

def fix_weather_underperform(sig):
    """Weather signal consistently losing — add series to skip list via override."""
    # Map signal to series prefix for identification
    overrides = _load_overrides()
    skip = set(overrides.get("SKIP_SERIES_EXTRA", []))
    note = (
        f"ALERT: {sig} natural win rate below 40%. Manual review needed — "
        f"add underperforming series to SKIP_SERIES in pnb_config.py."
    )
    # Can't auto-skip without knowing which specific series is bad
    # Flag for manual review instead
    return note


# ─── Main ────────────────────────────────────────────────────────────────────

def run():
    log.info("Watchdog run started")
    trades  = _load_paper()
    stats   = pnb_learn.signal_stats()
    state   = _load_state()
    overrides = _load_overrides()
    actions = []   # things we fixed
    alerts  = []   # things needing human attention
    now_ts  = datetime.now().strftime("%Y-%m-%d %H:%M")

    # ── 1. Stop-loss rate ─────────────────────────────────────────────────
    for sig, s in stats.items():
        if s["total"] < 10:
            continue
        sl_rate = s["stop_losses"] / s["total"]
        stop_pct = overrides.get("STOP_LOSS_PCT", pnb_config.STOP_LOSS_PCT)
        if sl_rate > 0.30 and stop_pct > 0:
            result = fix_stop_loss_rate(sig, sl_rate, overrides)
            overrides = _load_overrides()  # reload after write
            actions.append(result)
            log.info(f"Remediated stop-loss rate on {sig}")

    # ── 2. Win rate decay ────────────────────────────────────────────────
    settled_natural = [t for t in trades if t.get("settled") and t.get("result") in ("yes","no")]
    bno = [t for t in settled_natural if t.get("signal") == "BECKER-NO"]
    if len(bno) >= 25:
        last20_wr  = sum(1 for t in bno[-20:] if t["won"]) / 20
        overall_wr = stats.get("BECKER-NO", {}).get("natural_win_rate") or 0
        if overall_wr > 0 and last20_wr < overall_wr - 0.15:
            result = fix_win_rate_decay(last20_wr, overall_wr, overrides)
            overrides = _load_overrides()
            actions.append(result)
            log.info(f"Remediated win rate decay: last20={last20_wr:.0%}")

    # ── 3. Signal drought ─────────────────────────────────────────────────
    recent_becker = sorted(
        [t for t in trades if t.get("signal","").startswith("BECKER")],
        key=lambda t: t["ts"]
    )
    if recent_becker:
        last_ts = datetime.strptime(recent_becker[-1]["ts"], "%Y-%m-%d %H:%M")
        hours_since = (datetime.now() - last_ts).total_seconds() / 3600
        if hours_since > 6:
            result = fix_signal_drought(hours_since)
            actions.append(result)
            log.info(f"Remediated signal drought: {hours_since:.0f}h")

    # ── 4. P&L regression ────────────────────────────────────────────────
    total_pnl = sum(t.get("pnl") or 0 for t in trades if t.get("settled"))
    last_pnl  = state.get("last_pnl", total_pnl)
    pnl_drop  = total_pnl - last_pnl
    if pnl_drop < -2.00:
        result = fix_pnl_regression(pnl_drop, total_pnl, overrides)
        if result:
            overrides = _load_overrides()
            actions.append(result)
            log.info(f"Remediated P&L regression: {pnl_drop:.2f}")

    # ── 5. Adapt stall ───────────────────────────────────────────────────
    last_bno_total  = overrides.get("_last_bno_total", 0)
    bno_nat_total   = len(bno)
    new_since_adapt = bno_nat_total - last_bno_total
    bno_wr          = stats.get("BECKER-NO", {}).get("natural_win_rate") or 0
    if new_since_adapt >= 20 and bno_wr < 0.45:
        result = fix_adapt_stall(new_since_adapt, bno_wr, overrides)
        overrides = _load_overrides()
        actions.append(result)
        log.info(f"Remediated adapt stall: {new_since_adapt} trades, wr={bno_wr:.0%}")

    # ── 6. Weather underperformance ──────────────────────────────────────
    for sig in ("WEATHER-YES", "WEATHER-NO"):
        ws = stats.get(sig, {})
        if ws.get("total", 0) >= 8 and ws.get("natural_win_rate") is not None:
            if ws["natural_win_rate"] < 0.40:
                alerts.append(fix_weather_underperform(sig))

    # ── Build and send report ─────────────────────────────────────────────
    lr = pnb_learn.live_readiness()
    bno_s = stats.get("BECKER-NO", {})
    header = (
        f"PNB Watchdog — {now_ts}\n"
        f"BECKER-NO: {bno_s.get('wins',0)}W/{bno_s.get('losses',0)}L  "
        f"nat_wr={bno_wr:.0%}  P&L=${total_pnl:+.2f}\n"
        f"Live ready: {'YES ✓' if lr['ready'] else 'NO'} "
        f"({lr['win_rate']:.1%} win rate)"
    )

    if actions or alerts:
        parts = []
        if actions:
            parts.append("ACTIONS TAKEN:\n" + "\n".join(f"• {a}" for a in actions))
        if alerts:
            parts.append("NEEDS ATTENTION:\n" + "\n".join(f"• {a}" for a in alerts))
        msg = header + "\n\n" + "\n\n".join(parts)
    else:
        msg = header + "\nAll systems nominal."

    pnb_telegram.send(msg)
    log.info(f"Watchdog complete | actions={len(actions)} alerts={len(alerts)} pnl=${total_pnl:.2f}")

    _save_state({
        "last_run":    now_ts,
        "last_pnl":    total_pnl,
        "actions":     actions,
        "alerts":      alerts,
    })

    return actions, alerts


if __name__ == "__main__":
    run()
