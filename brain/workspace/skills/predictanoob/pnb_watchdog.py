"""
PredictaNoob — Watchdog
Runs every hour. Detects anomalies in trading data and alerts via Telegram.
This is the difference between a system that reports and one that thinks.

Checks:
  1. Stop-loss rate — exits > 30% of total positions = stop loss too tight
  2. Win rate decay — last 20 trades significantly below overall rate
  3. Signal drought — no signals fired in last 6 hours during active market
  4. Paper P&L regression — total P&L dropped since last check
  5. Adapt drift — ceiling/floor haven't moved despite persistent underperformance
  6. Weather miss rate — weather firing but losing consistently
"""
import json, os, time, logging
from datetime import datetime, timezone, timedelta

import pnb_telegram, pnb_learn, pnb_config

LOG_PATH    = "/home/rob-alvarado/RJA/.pnb/pnb_watchdog.log"
STATE_PATH  = "/home/rob-alvarado/RJA/.pnb/pnb_watchdog_state.json"
PAPER_PATH  = "/home/rob-alvarado/RJA/.pnb/pnb_paper.json"

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
log = logging.getLogger("pnb_watchdog")


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


def run():
    log.info("Watchdog run started")
    trades  = _load_paper()
    stats   = pnb_learn.signal_stats()
    state   = _load_state()
    alerts  = []
    now_ts  = datetime.now().strftime("%Y-%m-%d %H:%M")

    # ── 1. Stop-loss rate ─────────────────────────────────────────────────
    for sig, s in stats.items():
        total = s["total"]
        if total < 10:
            continue
        sl_rate = s["stop_losses"] / total
        if sl_rate > 0.30:
            alerts.append(
                f"STOP-LOSS RATE HIGH: {sig} — {s['stop_losses']} exits "
                f"out of {total} total ({sl_rate:.0%}). Stop loss may be too tight."
            )
            log.warning(f"High stop-loss rate on {sig}: {sl_rate:.0%}")

    # ── 2. Win rate decay (last 20 vs overall) ────────────────────────────
    settled_natural = [t for t in trades if t.get("settled") and t.get("result") in ("yes","no")]
    bno = [t for t in settled_natural if t.get("signal") == "BECKER-NO"]
    if len(bno) >= 25:
        last20_wr = sum(1 for t in bno[-20:] if t["won"]) / 20
        overall_wr = stats.get("BECKER-NO", {}).get("natural_win_rate") or 0
        if overall_wr > 0 and last20_wr < overall_wr - 0.15:
            alerts.append(
                f"WIN RATE DECAY: BECKER-NO last 20 trades at {last20_wr:.0%} "
                f"vs overall {overall_wr:.0%}. Signal may be deteriorating."
            )
            log.warning(f"BECKER-NO win rate decay: last20={last20_wr:.0%} overall={overall_wr:.0%}")

    # ── 3. Signal drought ─────────────────────────────────────────────────
    recent = sorted(
        [t for t in trades if t.get("signal","").startswith("BECKER")],
        key=lambda t: t["ts"]
    )
    if recent:
        last_signal_ts = datetime.strptime(recent[-1]["ts"], "%Y-%m-%d %H:%M")
        hours_since = (datetime.now() - last_signal_ts).total_seconds() / 3600
        if hours_since > 6:
            alerts.append(
                f"SIGNAL DROUGHT: No BECKER signal in {hours_since:.0f} hours. "
                f"Check if engine is running and markets are active."
            )
            log.warning(f"Signal drought: {hours_since:.0f}h since last BECKER trade")

    # ── 4. P&L regression ────────────────────────────────────────────────
    total_pnl = sum(t.get("pnl") or 0 for t in trades if t.get("settled"))
    last_pnl  = state.get("last_pnl", total_pnl)
    pnl_drop  = total_pnl - last_pnl
    if pnl_drop < -2.00:
        alerts.append(
            f"P&L REGRESSION: Down ${pnl_drop:.2f} since last watchdog check "
            f"(total now ${total_pnl:.2f})."
        )
        log.warning(f"P&L regression: {pnl_drop:.2f} since last check")

    # ── 5. Adapt drift — ceiling unchanged despite sustained underperformance ──
    overrides = {}
    op = "/home/rob-alvarado/RJA/.pnb/pnb_config_overrides.json"
    if os.path.exists(op):
        with open(op) as f:
            overrides = json.load(f)
    last_bno_total = overrides.get("_last_bno_total", 0)
    bno_nat_total  = len(bno)
    new_since_adapt = bno_nat_total - last_bno_total
    bno_stats = stats.get("BECKER-NO", {})
    bno_wr    = bno_stats.get("natural_win_rate") or 0
    if new_since_adapt >= 20 and bno_wr < 0.45:
        alerts.append(
            f"ADAPT STALLED: {new_since_adapt} new BECKER-NO trades since last "
            f"threshold change, win rate still {bno_wr:.0%}. adapt() may not be firing."
        )
        log.warning(f"Adapt stalled: {new_since_adapt} trades, wr={bno_wr:.0%}")

    # ── 6. Weather consistent losses ─────────────────────────────────────
    for sig in ("WEATHER-YES", "WEATHER-NO"):
        ws = stats.get(sig, {})
        if ws.get("total", 0) >= 8 and ws.get("natural_win_rate") is not None:
            if ws["natural_win_rate"] < 0.40:
                alerts.append(
                    f"WEATHER UNDERPERFORMING: {sig} natural win rate "
                    f"{ws['natural_win_rate']:.0%} over {ws['total']} trades. "
                    f"Review weather signal or SKIP_SERIES."
                )

    # ── Send report ───────────────────────────────────────────────────────
    lr = pnb_learn.live_readiness()
    header = (
        f"PNB Watchdog — {now_ts}\n"
        f"BECKER-NO: {bno_stats.get('wins',0)}W/{bno_stats.get('losses',0)}L  "
        f"nat_wr={bno_wr:.0%}  P&L=${total_pnl:+.2f}\n"
        f"Live ready: {'YES' if lr['ready'] else 'NO'} "
        f"(win_rate={lr['win_rate']:.1%})"
    )

    if alerts:
        msg = header + "\n\nALERTS:\n" + "\n".join(f"⚠ {a}" for a in alerts)
    else:
        msg = header + "\nNo anomalies detected."

    pnb_telegram.send(msg)
    log.info(f"Watchdog complete | alerts={len(alerts)} | pnl=${total_pnl:.2f}")

    # Save state for next run
    _save_state({
        "last_run":  now_ts,
        "last_pnl":  total_pnl,
        "alerts":    alerts,
    })

    return alerts


if __name__ == "__main__":
    run()
