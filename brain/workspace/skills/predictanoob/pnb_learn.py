"""
PredictaNoob -- Learning Engine
Tracks near-misses, price distributions, and generates recommendations.
Appends to pnb_learn.json after every scan. Daily report reads it.
"""
import json, os
from datetime import date, datetime

LEARN_PATH = "/home/rob-alvarado/RJA/.pnb/pnb_learn.json"

def _load():
    if os.path.exists(LEARN_PATH):
        with open(LEARN_PATH) as f:
            return json.load(f)
    return {
        "weather_near_misses": [],   # last 30 days of closest skips
        "crypto_prices_seen": [],    # YES prices seen at evaluation time
        "crypto_signals_fired": [],  # actual signals and outcomes
        "weather_signals_fired": [],
    }

def _save(data):
    with open(LEARN_PATH, "w") as f:
        json.dump(data, f, indent=2)

def record_weather_skip(ticker, city, reason, hist_no_rate, margin_f, yes_ask, threshold):
    data = _load()
    entry = {
        "date": str(date.today()),
        "ticker": ticker,
        "city": city,
        "reason": reason,
        "hist_no_rate": round(hist_no_rate, 3) if hist_no_rate else None,
        "margin_f": round(margin_f, 1) if margin_f else None,
        "yes_ask": round(yes_ask, 2),
        "threshold": threshold,
    }
    data["weather_near_misses"].append(entry)
    # Keep last 200 entries
    data["weather_near_misses"] = data["weather_near_misses"][-200:]
    _save(data)

def record_crypto_price(ticker, yes_ask, no_ask, minutes_left, signal_fired):
    data = _load()
    data["crypto_prices_seen"].append({
        "ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "ticker": ticker,
        "yes_ask": round(yes_ask, 2),
        "no_ask": round(no_ask, 2),
        "minutes_left": round(minutes_left, 1),
        "signal": signal_fired,
    })
    data["crypto_prices_seen"] = data["crypto_prices_seen"][-500:]
    _save(data)

def analyze():
    """
    Return a dict with:
    - weather: top near-misses from last 7 days, threshold recommendation
    - crypto: YES price distribution, signal rate, threshold recommendation
    """
    data = _load()
    today = date.today()

    # --- Weather analysis ---
    recent_weather = [
        e for e in data["weather_near_misses"]
        if (today - date.fromisoformat(e["date"])).days <= 7
    ]

    # Find closest hist_no_rate misses
    rate_misses = [e for e in recent_weather if e.get("reason", "").startswith("hist NO")]
    rate_misses.sort(key=lambda e: e.get("hist_no_rate") or 0, reverse=True)

    # Find closest margin misses
    margin_misses = [e for e in recent_weather if "margin" in e.get("reason", "")]
    margin_misses.sort(key=lambda e: e.get("margin_f") or 0, reverse=True)

    weather_rec = None
    if rate_misses:
        best = rate_misses[0]
        gap = 0.70 - (best["hist_no_rate"] or 0)
        if gap < 0.08:
            weather_rec = (
                f"Closest near-miss: {best['city']} at {best['hist_no_rate']:.0%} hist NO "
                f"(need 70%). Gap = {gap:.0%}. "
                f"Consider loosening to {(0.70 - gap/2):.0%} if no signals in 3 more days."
            )

    # --- Crypto analysis ---
    recent_crypto = [
        e for e in data["crypto_prices_seen"]
        if (today - date.fromisoformat(e["ts"][:10])).days <= 7
    ]

    yes_prices = [e["yes_ask"] for e in recent_crypto if e["yes_ask"] > 0.05]
    above_ceiling = [p for p in yes_prices if p > 0.55]
    below_floor   = [p for p in yes_prices if 0 < p < 0.44]
    signals_fired  = [e for e in recent_crypto if e.get("signal")]

    crypto_rec = None
    if yes_prices:
        avg_yes = sum(yes_prices) / len(yes_prices)
        pct_above = len(above_ceiling) / len(yes_prices) * 100
        if pct_above < 5 and avg_yes < 0.55:
            crypto_rec = (
                f"YES prices avg ${avg_yes:.2f} — only {pct_above:.0f}% above 0.55 ceiling. "
                f"Market is not showing optimism bias recently. "
                f"Consider lowering ceiling to 0.52 to capture more signals."
            )
        elif pct_above > 20:
            crypto_rec = (
                f"YES prices avg ${avg_yes:.2f} — {pct_above:.0f}% above ceiling. "
                f"Becker signal appearing frequently. Check if trades are profitable."
            )

    return {
        "weather": {
            "scans_7d": len(set(e["date"] for e in recent_weather)),
            "near_misses_7d": len(recent_weather),
            "closest_rate_miss": rate_misses[0] if rate_misses else None,
            "closest_margin_miss": margin_misses[0] if margin_misses else None,
            "recommendation": weather_rec,
        },
        "crypto": {
            "prices_evaluated": len(yes_prices),
            "avg_yes_ask": round(sum(yes_prices)/len(yes_prices), 2) if yes_prices else None,
            "pct_above_ceiling": round(len(above_ceiling)/len(yes_prices)*100, 1) if yes_prices else None,
            "signals_fired_7d": len(signals_fired),
            "recommendation": crypto_rec,
        }
    }
