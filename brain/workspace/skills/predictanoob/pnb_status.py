"""
PredictaNoob -- Status + Learning Report
Sent to Telegram daily at 8AM and on demand.
"""
import json, os
from datetime import date
import pnb_auth, pnb_state, pnb_telegram, pnb_learn, pnb_paper, pnb_config

TARGET_CENTS = 5000

def run():
    # Balance
    bal_r = pnb_auth.get("/portfolio/balance")
    balance_cents = bal_r.json().get("balance", 0) if bal_r.status_code == 200 else 0
    pct = balance_cents / TARGET_CENTS * 100
    mode = "LIVE" if pnb_auth.is_live() else "DRY-RUN"

    # Positions
    s = pnb_state.summary()
    held_lines = []
    state_path = "/home/rob-alvarado/RJA/.pnb/pnb_state.json"
    if os.path.exists(state_path):
        with open(state_path) as f:
            raw = json.load(f)
        for ticker, info in raw.get("held", {}).items():
            held_lines.append(f"  {ticker} | {info['side']} @ ${info['price']:.2f}")

    # Paper trade settlement check + summary
    pnb_paper.check_settlements()
    paper = pnb_paper.summary()

    # Learning analysis
    analysis = pnb_learn.analyze()
    w        = analysis["weather"]
    c        = analysis["crypto"]
    sig_stats = analysis["signal_stats"]
    adapt_changes = analysis["adapt_changes"]

    win_rate_str = f"{paper['win_rate']:.0%}" if paper['win_rate'] is not None else "n/a"
    pnl_str = f"${paper['total_pnl']:+.2f}" if paper['wins'] + paper['losses'] > 0 else "$0.00"

    lines = [
        f"PNB Daily Report -- {date.today()}",
        "=" * 32,
        f"Balance:  ${balance_cents/100:.2f}  /  Target: ${TARGET_CENTS/100:.2f}  ({pct:.1f}%)",
        f"Mode:     {mode}",
        f"",
        f"-- DRY-RUN PAPER RECORD --",
        f"  {paper['wins']}W / {paper['losses']}L / {paper['pending']} pending",
        f"  Win rate: {win_rate_str}  |  P&L: {pnl_str}",
        "",
        f"-- SIGNAL BREAKDOWN --",
    ]

    if sig_stats:
        for sig, st in sorted(sig_stats.items()):
            nat_wr = f"{st['natural_win_rate']:.0%}" if st['natural_win_rate'] is not None else "n/a"
            sl_note = f"  SL={st['stop_losses']}" if st['stop_losses'] else ""
            unvalidated = " (unvalidated)" if sig == "BECKER-YES" and st["total"] < 15 else ""
            lines.append(
                f"  {sig:<20}  {st['wins']}W/{st['losses']}L{sl_note}  "
                f"nat_wr={nat_wr}  P&L=${st['total_pnl']:+.2f}{unvalidated}"
            )
    else:
        lines.append("  No settled trades yet")

    if adapt_changes:
        lines += ["", "-- AUTO-ADAPT --"]
        for c_line in adapt_changes:
            lines.append(f"  {c_line}")

    # Active config (shows overridden values if adapt() has changed them)
    overrides_path = "/home/rob-alvarado/RJA/.pnb/pnb_config_overrides.json"
    overrides = {}
    if os.path.exists(overrides_path):
        with open(overrides_path) as f:
            overrides = json.load(f)
    lines += ["", "-- ACTIVE CONFIG --"]
    lines.append(f"  BECKER_YES_CEILING: {pnb_config.BECKER_YES_CEILING:.2f}" + (" (adapted)" if "BECKER_YES_CEILING" in overrides else ""))
    lines.append(f"  BECKER_YES_FLOOR:   {pnb_config.BECKER_YES_FLOOR:.2f}")
    lines.append(f"  MIN_HIST_RATE:      {pnb_config.MIN_HIST_RATE:.2f}" + (" (adapted)" if "MIN_HIST_RATE" in overrides else ""))
    lines.append(f"  MIN_EV:             {pnb_config.MIN_EV:.2f}")
    lines.append(f"  STOP_LOSS_PCT:      {pnb_config.STOP_LOSS_PCT:.0%}  TAKE_PROFIT: {pnb_config.TAKE_PROFIT_PCT:.0%}")

    # Live readiness
    lr = analysis["live_readiness"]
    lines += ["", "-- LIVE READINESS --"]
    for check, passed in lr["checks"].items():
        lines.append(f"  {'OK' if passed else 'NO'}  {check}")
    lines.append(f"  {'>>> READY TO GO LIVE <<<' if lr['ready'] else 'Not ready yet'}")

    # Condition analysis (only if we have data)
    ca = analysis.get("condition_analysis", {})
    if ca.get("becker_no_by_momentum"):
        lines += ["", "-- CONDITION ANALYSIS --"]
        lines.append("  BECKER-NO by momentum:")
        for m, s in ca["becker_no_by_momentum"].items():
            wr = f"{s['win_rate']:.0%}" if s['win_rate'] else "n/a"
            lines.append(f"    {m:<10}  {s['wins']}W/{s['losses']}L  wr={wr}")

    lines += ["", f"Positions: {s['held_count']} held"]
    lines.extend(held_lines or ["  (none)"])

    # --- Weather intelligence ---
    lines += ["", "-- WEATHER --"]
    if w["closest_rate_miss"]:
        m = w["closest_rate_miss"]
        lines.append(f"Closest near-miss: {m['city']} {m['ticker'].split('-')[1]}")
        lines.append(f"  Hist rate: {m['hist_no_rate']:.0%}  (need 70%)")
        lines.append(f"  NOAA margin: {m['margin_f']}F  |  YES ask: ${m['yes_ask']:.2f}")
    else:
        lines.append("  No near-misses logged yet")

    if w["recommendation"]:
        lines.append(f"NOTE: {w['recommendation']}")

    # --- Crypto intelligence ---
    lines += ["", "-- CRYPTO --"]
    if c["prices_evaluated"]:
        lines.append(f"YES prices seen (7d): {c['prices_evaluated']} samples")
        lines.append(f"  Avg YES ask: ${c['avg_yes_ask']:.2f}")
        lines.append(f"  Above 0.55 ceiling: {c['pct_above_ceiling']:.0f}%")
        lines.append(f"  Signals fired: {c['signals_fired_7d']}")
    else:
        lines.append("  No crypto prices logged yet")

    if c["recommendation"]:
        lines.append(f"NOTE: {c['recommendation']}")

    text = "\n".join(lines)
    print(text)
    pnb_telegram.send(text)
    return text

if __name__ == "__main__":
    run()
