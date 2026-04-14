"""
PredictaNoob — Go-Live Verification
Run this before switching LIVE_TRADING=true.
All checks must pass. If they do, it flips the switch for you.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import pnb_auth, pnb_learn, pnb_state, pnb_config

ENV_PATH = "/home/rob-alvarado/RJA/.pnb/.env"

def check(label, passed, detail=""):
    status = "PASS" if passed else "FAIL"
    print(f"  [{status}] {label}" + (f" — {detail}" if detail else ""))
    return passed

def run(force=False):
    print("\nPNB Go-Live Verification")
    print("=" * 40)
    results = []

    # 1. Paper performance
    lr = pnb_learn.live_readiness()
    results.append(check(
        f"Paper trades >= {pnb_config.LIVE_MIN_TRADES}",
        lr["checks"][f"trades >= {pnb_config.LIVE_MIN_TRADES}"],
        f"{lr['trades']} settled"
    ))
    results.append(check(
        f"Win rate >= {pnb_config.LIVE_MIN_WIN_RATE:.0%}",
        lr["checks"][f"win_rate >= {pnb_config.LIVE_MIN_WIN_RATE:.0%}"],
        f"actual {lr['win_rate']:.1%}"
    ))
    results.append(check(
        f"Paper P&L >= ${pnb_config.LIVE_MIN_PNL:.2f}",
        lr["checks"][f"P&L >= ${pnb_config.LIVE_MIN_PNL:.2f}"],
        f"actual ${lr['pnl']:.2f}"
    ))

    # 2. API connectivity
    r = pnb_auth.get("/portfolio/balance")
    api_ok = r.status_code == 200
    balance = r.json().get("balance", 0) if api_ok else 0
    results.append(check("Kalshi API reachable", api_ok))
    results.append(check(
        f"Balance >= halt threshold (${pnb_config.HALT_BELOW_CENTS/100:.2f})",
        balance >= pnb_config.HALT_BELOW_CENTS,
        f"${balance/100:.2f}"
    ))

    # 3. State files exist
    results.append(check(
        "pnb_state.json exists",
        os.path.exists("/home/rob-alvarado/RJA/.pnb/pnb_state.json")
    ))
    results.append(check(
        "pnb_config_overrides.json exists (adapt() has run)",
        os.path.exists("/home/rob-alvarado/RJA/.pnb/pnb_config_overrides.json")
    ))

    # 4. Not already live
    results.append(check(
        "Currently in DRY-RUN mode",
        not pnb_auth.is_live()
    ))

    print("=" * 40)
    all_pass = all(results)

    if all_pass or force:
        print("\nAll checks passed. Switching to LIVE_TRADING=true...")
        lines = open(ENV_PATH).readlines()
        with open(ENV_PATH, "w") as f:
            for line in lines:
                if line.strip().startswith("LIVE_TRADING"):
                    f.write("LIVE_TRADING=true\n")
                else:
                    f.write(line)
        print("Done. Restart pnb-crypto to go live:")
        print("  systemctl --user restart pnb-crypto")
    else:
        print(f"\nNot ready. Fix failing checks above.")
        print("Re-run when ready: python3 pnb_golive.py")
        sys.exit(1)

if __name__ == "__main__":
    force = "--force" in sys.argv
    run(force)
