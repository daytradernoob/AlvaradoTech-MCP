"""
PredictaNoob -- Status + Learning Report
Sent to Telegram daily at 8AM and on demand.
"""
import json, os
from datetime import date
import pnb_auth, pnb_state, pnb_telegram, pnb_learn

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

    # Learning analysis
    analysis = pnb_learn.analyze()
    w = analysis["weather"]
    c = analysis["crypto"]

    lines = [
        f"PNB Daily Report -- {date.today()}",
        "=" * 32,
        f"Balance:  ${balance_cents/100:.2f}  /  Target: ${TARGET_CENTS/100:.2f}  ({pct:.1f}%)",
        f"Mode:     {mode}",
        f"Record:   {s['wins']}W / {s['losses']}L / {s['pending']} pending",
        "",
        f"Positions: {s['held_count']} held",
    ]
    lines.extend(held_lines or ["  (none)"])

    # --- Weather intelligence ---
    lines += ["", "-- WEATHER --"]
    if w["closest_rate_miss"]:
        m = w["closest_rate_miss"]
        lines.append(f"Closest near-miss: {m['city']} {m['ticker'].split('-')[1]}")
        lines.append(f"  Hist NO rate: {m['hist_no_rate']:.0%}  (need 70%)")
        lines.append(f"  NOAA margin: {m['margin_f']}F  |  YES ask: ${m['yes_ask']:.2f}")
    else:
        lines.append("  No near-misses logged yet")

    if w["recommendation"]:
        lines.append(f"RECOMMENDATION: {w['recommendation']}")

    # --- Crypto intelligence ---
    lines += ["", "-- CRYPTO --"]
    if c["prices_evaluated"]:
        lines.append(f"YES prices seen (7d): {c['prices_evaluated']} samples")
        lines.append(f"  Avg YES ask: ${c['avg_yes_ask']:.2f}")
        lines.append(f"  Above 0.55 ceiling: {c['pct_above_ceiling']:.0f}%")
        lines.append(f"  Signals fired: {c['signals_fired_7d']}")
    else:
        lines.append("  No crypto prices logged yet -- timing fix just applied")

    if c["recommendation"]:
        lines.append(f"RECOMMENDATION: {c['recommendation']}")

    text = "\n".join(lines)
    print(text)
    pnb_telegram.send(text)
    return text

if __name__ == "__main__":
    run()
