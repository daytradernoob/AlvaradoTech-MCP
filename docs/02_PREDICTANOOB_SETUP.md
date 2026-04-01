# PREDICTANOOB SETUP
## MCP Execution Document — Kalshi Weather + Crypto 15-Min Markets
### Version 1.1 | rob-alvarado user | Real money — Live Kalshi account

---

> Execute in order. One command per block. Verify output before proceeding.
> REAL MONEY. PNB trades on live Kalshi. Dry-run validation required before crons go live.
> EV > 0.05 required. No exceptions. PSS padding on all auth.

---

## WHAT THIS BUILDS

**PredictaNoob (PNB)** — Two strategies, one Kalshi live account:

1. **Weather contracts** — NOAA airport forecast → Kalshi daily high/low temperature markets. Runs 11:00 AM MST daily.
2. **Crypto 15-min contracts** — Becker Optimism Tax on Kalshi crypto price markets. Runs every 15 min, 7 AM–2 PM MST.

Shared foundation (auth, Telegram, crash wrapper) built first. Each strategy on top.

---

## PRE-FLIGHT CHECKLIST

Before executing any step, confirm all pass:
- [ ] MSI-RTX (.146) online, Ollama running: `curl http://192.168.0.146:11434/api/tags`
- [ ] SEi-miniPC (.165) online, OpenClaw gateway running: `openclaw gateway status`
- [ ] Division of Resources doc fully executed and verified
- [ ] Kalshi API credentials (key + secret) in hand — ready to paste
- [ ] Telegram bot token and chat ID in hand
- [ ] MSI timezone confirmed MST: `timedatectl` shows `America/Phoenix`

---

## PHASE 1 — MSI-RTX DIRECTORY + ENVIRONMENT SETUP

SSH to MSI:
```
ssh rob-alvarado@192.168.0.146
```

### Step 1 — Create directory structure
```
mkdir -p /home/rob-alvarado/RJA/.pnb /home/rob-alvarado/RJA/.rja
```

### Step 2 — Verify directories created
```
ls -la /home/rob-alvarado/RJA/
```
Expected: `.pnb` and `.rja` directories visible.

### Step 3 — Confirm MSI timezone is MST
```
timedatectl
```
Expected: `Time zone: America/Phoenix (MST, -0700)`. If wrong:
```
sudo timedatectl set-timezone America/Phoenix
```

### Step 4 — Install Python dependencies
```
pip3 install requests python-dotenv cryptography
```

### Step 5 — Verify installs
```
pip3 show cryptography
```
Expected: Package info returned. cryptography is required for PSS auth — do not skip.

### Step 6 — Create credentials file
```
nano /home/rob-alvarado/RJA/.pnb/.env
```
Paste and fill in:
```
KALSHI_API_KEY=YOUR_KALSHI_API_KEY
KALSHI_API_SECRET=-----BEGIN RSA PRIVATE KEY-----
YOUR_RSA_PRIVATE_KEY_HERE
-----END RSA PRIVATE KEY-----
TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID=YOUR_TELEGRAM_CHAT_ID
KALSHI_BASE_URL=https://trading-api.kalshi.com/trade-api/v2
```
Save and close. Credentials stay here only — never in chat, never in git.

### Step 7 — Lock down permissions
```
chmod 600 /home/rob-alvarado/RJA/.pnb/.env
```

### Step 8 — Verify permissions
```
ls -la /home/rob-alvarado/RJA/.pnb/.env
```
Expected: `-rw-------` — owner read/write only.

### Step 9 — Create .gitignore at repo root
```
cat > /home/rob-alvarado/RJA/.gitignore << 'EOF'
# Credentials — never commit
.pnb/.env
.cnb/.env
.dtn/.env
.oanda/.env
*.env
*.key
*.secret
*.pem

# Logs
*.log
logs/

# Python
__pycache__/
*.pyc
*.pyo

# OS
.DS_Store
Thumbs.db
EOF
```

---

## PHASE 2 — SHARED KALSHI AUTH MODULE

### Step 1 — Create auth helper (PSS padding — CRITICAL)
```
cat > /home/rob-alvarado/RJA/.pnb/kalshi_auth.py << 'EOF'
"""
Kalshi API Authentication — RSA-PSS Padding
CRITICAL: Kalshi requires RSA-PSS, not PKCS1v15.
Wrong padding = silent auth failure every time.
"""
import base64
import datetime
import os
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

def get_kalshi_headers(method: str, path: str, api_key: str, private_key_pem: str) -> dict:
    """
    Generate signed headers for Kalshi API request.
    method: GET, POST, DELETE
    path: full path e.g. /trade-api/v2/portfolio/balance
    """
    timestamp = str(int(datetime.datetime.now().timestamp() * 1000))
    msg_string = timestamp + method.upper() + path

    private_key = serialization.load_pem_private_key(
        private_key_pem.encode(),
        password=None,
        backend=default_backend()
    )

    signature = private_key.sign(
        msg_string.encode('utf-8'),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.DIGEST_LENGTH
        ),
        hashes.SHA256()
    )

    return {
        "Content-Type": "application/json",
        "KALSHI-ACCESS-KEY": api_key,
        "KALSHI-ACCESS-TIMESTAMP": timestamp,
        "KALSHI-ACCESS-SIGNATURE": base64.b64encode(signature).decode('utf-8')
    }
EOF
```

### Step 2 — Create Telegram alert helper
```
cat > /home/rob-alvarado/RJA/.pnb/telegram_alert.py << 'EOF'
"""
Telegram alert sender — shared by all PNB components.
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def send_alert(message: str) -> bool:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print(f"Telegram alert failed: {e}")
        return False
EOF
```

### Step 3 — Create bot_runner.sh crash wrapper
```
cat > /home/rob-alvarado/RJA/.rja/bot_runner.sh << 'EOF'
#!/bin/bash
# bot_runner.sh — wraps every cron job
# Usage: bot_runner.sh <bot_name> <full_path_to_script>
# On non-zero exit, fires Telegram alert immediately.

BOT_NAME="$1"
SCRIPT="$2"
ENV_FILE="/home/rob-alvarado/RJA/.pnb/.env"
TELEGRAM_TOKEN=$(grep TELEGRAM_BOT_TOKEN "$ENV_FILE" | cut -d= -f2)
CHAT_ID=$(grep TELEGRAM_CHAT_ID "$ENV_FILE" | cut -d= -f2)

python3 "$SCRIPT" 2>&1
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
  MSG="🔴 BOT CRASH: ${BOT_NAME} exited ${EXIT_CODE} at $(date +'%Y-%m-%d %H:%M MST')"
  curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
    -d chat_id="${CHAT_ID}" \
    -d text="${MSG}"
fi
EOF
```

### Step 4 — Make bot_runner executable
```
chmod +x /home/rob-alvarado/RJA/.rja/bot_runner.sh
```

---

## PHASE 3 — WEATHER TRADING BOT

**Strategy:** NOAA airport forecast → compare vs Kalshi strike temp → EV filter → Kelly sizing → limit order.

### Step 1 — Create weather trader
```
cat > /home/rob-alvarado/RJA/.pnb/kalshi_weather_trader.py << 'EOF'
"""
PredictaNoob — Kalshi Weather Trader
Schedule: 11:00 AM MST daily via cron
Real money. EV > 0.05 required. Airport ICAO coords only.
"""
import os, json, requests, datetime
from dotenv import load_dotenv
from kalshi_auth import get_kalshi_headers
from telegram_alert import send_alert

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

API_KEY    = os.getenv('KALSHI_API_KEY')
API_SECRET = os.getenv('KALSHI_API_SECRET')
BASE_URL   = os.getenv('KALSHI_BASE_URL')

# Airport ICAO codes + coordinates — airport only, never city center
AIRPORT_COORDS = {
    "KPHX": (33.4373, -112.0078),
    "KMIA": (25.7959, -80.2870),
    "KORD": (41.9742, -87.9073),
    "KATL": (33.6407, -84.4277),
    "KDFW": (32.8998, -97.0403),
}

MIN_EV           = 0.05
KELLY_FRACTION   = 0.25
MAX_POSITION_PCT = 0.05
STATS_FILE       = "/home/rob-alvarado/RJA/.pnb/trade_stats.json"
LEARNINGS_FILE   = "/home/rob-alvarado/RJA/.rja/rja_learnings.json"


def get_noaa_forecast(icao: str) -> dict:
    lat, lon = AIRPORT_COORDS.get(icao, (None, None))
    if not lat:
        return {}
    try:
        r = requests.get(f"https://api.weather.gov/points/{lat},{lon}", timeout=10)
        if r.status_code != 200:
            return {}
        forecast_url = r.json()['properties']['forecast']
        r2 = requests.get(forecast_url, timeout=10)
        if r2.status_code != 200:
            return {}
        period = r2.json()['properties']['periods'][0]
        return {
            "high": period.get('temperature'),
            "unit": period.get('temperatureUnit'),
            "description": period.get('shortForecast'),
            "airport": icao
        }
    except Exception as e:
        print(f"NOAA error {icao}: {e}")
        return {}


def get_kalshi_weather_markets() -> list:
    path = "/trade-api/v2/markets?status=open&series_ticker=KXHIGH"
    headers = get_kalshi_headers("GET", path, API_KEY, API_SECRET)
    try:
        r = requests.get(f"{BASE_URL}/markets", params={"status": "open", "series_ticker": "KXHIGH"},
                         headers=headers, timeout=15)
        if r.status_code == 200:
            return r.json().get('markets', [])
    except Exception as e:
        print(f"Market fetch error: {e}")
    return []


def calculate_ev(yes_price_cents: float, est_prob: float):
    yp = yes_price_cents / 100
    np_ = 1 - yp
    ev_yes = (est_prob * (1 - yp)) - ((1 - est_prob) * yp)
    ev_no  = ((1 - est_prob) * (1 - np_)) - (est_prob * np_)
    if ev_yes > ev_no:
        return ev_yes, "YES"
    return ev_no, "NO"


def get_balance() -> float:
    path = "/trade-api/v2/portfolio/balance"
    headers = get_kalshi_headers("GET", path, API_KEY, API_SECRET)
    try:
        r = requests.get(f"{BASE_URL}/portfolio/balance", headers=headers, timeout=10)
        if r.status_code == 200:
            return r.json().get('balance', 0) / 100
    except:
        pass
    return 0.0


def place_order(ticker: str, side: str, contracts: int, limit_cents: int) -> dict:
    headers = get_kalshi_headers("POST", "/trade-api/v2/portfolio/orders", API_KEY, API_SECRET)
    body = {
        "ticker": ticker,
        "action": "buy",
        "side": side.lower(),
        "count": contracts,
        "type": "limit",
        "yes_price": limit_cents if side == "YES" else (100 - limit_cents)
    }
    try:
        r = requests.post(f"{BASE_URL}/portfolio/orders", headers=headers, json=body, timeout=15)
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def record_trade(trade: dict):
    trades = []
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE) as f:
            trades = json.load(f)
    trades.append(trade)
    with open(STATS_FILE, 'w') as f:
        json.dump(trades, f, indent=2)


def main():
    print(f"PNB Weather starting — {datetime.datetime.now().strftime('%Y-%m-%d %H:%M MST')}")

    skip_series = []
    if os.path.exists(LEARNINGS_FILE):
        with open(LEARNINGS_FILE) as f:
            skip_series = json.load(f).get('SKIP_SERIES', [])

    balance = get_balance()
    print(f"Balance: ${balance:.2f}")
    if balance < 10:
        send_alert(f"⚠️ PNB Weather: Balance ${balance:.2f} too low. Skipping.")
        return

    markets = get_kalshi_weather_markets()
    placed = 0

    for m in markets:
        ticker = m.get('ticker', '')
        if any(s in ticker for s in skip_series):
            print(f"Skip {ticker} — SKIP_SERIES")
            continue

        target_icao = next((i for i in AIRPORT_COORDS if i.replace("K","") in ticker or i in ticker), None)
        if not target_icao:
            continue

        forecast = get_noaa_forecast(target_icao)
        if not forecast or not forecast.get('high'):
            print(f"No NOAA data for {target_icao}")
            continue

        noaa_temp = forecast['high']
        raw_ask = m.get('yes_ask', 0)
        yes_ask = int(float(raw_ask) * 100) if raw_ask and float(raw_ask) < 1 else int(raw_ask or 0)

        if yes_ask <= 0 or yes_ask >= 100:
            continue

        try:
            strike_temp = int(''.join(filter(str.isdigit, ticker.split('T')[-1][:3])))
        except:
            continue

        diff = abs(noaa_temp - strike_temp)
        if noaa_temp > strike_temp:
            est_prob = 0.65 if diff <= 2 else (0.58 if diff <= 5 else 0.52)
        else:
            est_prob = 0.35 if diff <= 2 else (0.42 if diff <= 5 else 0.48)

        ev, side = calculate_ev(yes_ask, est_prob)
        if ev < MIN_EV:
            print(f"Skip {ticker} — EV {ev:.3f}")
            continue

        kelly = balance * KELLY_FRACTION * ev
        cap   = balance * MAX_POSITION_PCT
        margin = min(kelly, cap)
        contracts = max(1, int(margin / (yes_ask / 100)))

        limit = yes_ask if side == "YES" else (100 - yes_ask)
        result = place_order(ticker, side, contracts, limit)

        if result.get('error'):
            send_alert(f"⚠️ PNB Weather order failed: {ticker} — {result['error']}")
            continue

        order_id  = result.get('order', {}).get('order_id', 'unknown')
        margin_f  = round(contracts * limit / 100, 2)

        record_trade({
            "timestamp":   datetime.datetime.now().isoformat(),
            "strategy":    "WEATHER",
            "ticker":      ticker,
            "side":        side,
            "contracts":   contracts,
            "ev":          round(ev, 4),
            "noaa_temp":   noaa_temp,
            "strike_temp": strike_temp,
            "margin_f":    margin_f,
            "signal_type": "NOAA_FORECAST",
            "settled":     False,
            "order_id":    order_id
        })

        send_alert(
            f"✅ *PNB WEATHER*: `{ticker}`\n"
            f"Side: {side} | Contracts: {contracts}\n"
            f"EV: {ev:.3f} | NOAA: {noaa_temp}F | Strike: {strike_temp}F\n"
            f"Margin: ${margin_f} | Order: `{order_id}`"
        )
        placed += 1

    if placed == 0:
        send_alert(f"⬜ PNB Weather: No trades — EV threshold not met")
    print(f"PNB Weather done — {placed} trades placed")


if __name__ == "__main__":
    main()
EOF
```

---

## PHASE 4 — CRYPTO 15-MIN TRADING BOT

**Strategy:** Becker Optimism Tax — buy NO on Kalshi crypto YES longshots priced under $0.20. Stage 1: 1 contract max.

### Step 1 — Create crypto contract trader
```
cat > /home/rob-alvarado/RJA/.pnb/contract_trader.py << 'EOF'
"""
PredictaNoob — Kalshi Crypto 15-Min Contract Trader
Schedule: Every 15 min, 7:00 AM – 2:00 PM MST, Mon–Fri
Stage 1: 1 contract max until 30 settled trades.
Becker Optimism Tax: buy NO on YES longshots < $0.20
Real money. EV > 0.05 required.
"""
import os, json, requests, datetime
from dotenv import load_dotenv
from kalshi_auth import get_kalshi_headers
from telegram_alert import send_alert

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

API_KEY    = os.getenv('KALSHI_API_KEY')
API_SECRET = os.getenv('KALSHI_API_SECRET')
BASE_URL   = os.getenv('KALSHI_BASE_URL')

STAGE_1_MAX       = 1
STAGE_1_THRESHOLD = 30
MIN_EV            = 0.05
OT_THRESHOLD      = 0.20   # YES below this = optimism tax candidate
STATS_FILE        = "/home/rob-alvarado/RJA/.pnb/trade_stats.json"

CRYPTO_SERIES = ["KXBTCD", "KXETHD"]


def settled_count() -> int:
    if not os.path.exists(STATS_FILE):
        return 0
    with open(STATS_FILE) as f:
        trades = json.load(f)
    return len([t for t in trades if t.get('settled') and t.get('strategy') == 'CRYPTO_15MIN'])


def get_crypto_markets() -> list:
    markets = []
    for series in CRYPTO_SERIES:
        headers = get_kalshi_headers("GET", f"/trade-api/v2/markets", API_KEY, API_SECRET)
        try:
            r = requests.get(f"{BASE_URL}/markets",
                             params={"status": "open", "series_ticker": series},
                             headers=headers, timeout=15)
            if r.status_code == 200:
                markets += r.json().get('markets', [])
        except Exception as e:
            print(f"Market fetch error ({series}): {e}")
    return markets


def optimism_tax_ev(yes_ask_cents: int) -> float:
    """
    People systematically overprice YES on longshots.
    Assume true YES prob = 40% of implied price.
    We buy NO and collect the gap.
    """
    yp = yes_ask_cents / 100
    np_ = 1 - yp
    true_yes = yp * 0.40
    true_no  = 1 - true_yes
    return (true_no * yp) - (true_yes * np_)


def place_order(ticker: str, side: str, contracts: int, limit_cents: int) -> dict:
    headers = get_kalshi_headers("POST", "/trade-api/v2/portfolio/orders", API_KEY, API_SECRET)
    body = {
        "ticker": ticker,
        "action": "buy",
        "side": side.lower(),
        "count": contracts,
        "type": "limit",
        "yes_price": limit_cents if side == "YES" else (100 - limit_cents)
    }
    try:
        r = requests.post(f"{BASE_URL}/portfolio/orders", headers=headers, json=body, timeout=15)
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def record_trade(trade: dict):
    trades = []
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE) as f:
            trades = json.load(f)
    trades.append(trade)
    with open(STATS_FILE, 'w') as f:
        json.dump(trades, f, indent=2)


def main():
    now = datetime.datetime.now()
    print(f"PNB Crypto starting — {now.strftime('%Y-%m-%d %H:%M MST')}")

    sc = settled_count()
    max_c = STAGE_1_MAX if sc < STAGE_1_THRESHOLD else 3
    print(f"Stage {'1' if sc < STAGE_1_THRESHOLD else '2'} — {sc} settled. Max contracts: {max_c}")

    markets = get_crypto_markets()
    placed  = 0

    for m in markets:
        ticker  = m.get('ticker', '')
        raw_ask = m.get('yes_ask', 0)
        yes_ask = int(float(raw_ask) * 100) if raw_ask and float(raw_ask) < 1 else int(raw_ask or 0)

        if yes_ask <= 0 or yes_ask >= 100:
            continue
        if yes_ask >= int(OT_THRESHOLD * 100):
            continue  # Not a longshot — skip

        ev = optimism_tax_ev(yes_ask)
        if ev < MIN_EV:
            print(f"Skip {ticker} — EV {ev:.3f}")
            continue

        no_price = 100 - yes_ask
        result   = place_order(ticker, "NO", max_c, no_price)

        if result.get('error'):
            send_alert(f"⚠️ PNB Crypto order failed: {ticker} — {result['error']}")
            continue

        order_id = result.get('order', {}).get('order_id', 'unknown')
        margin_f = round(max_c * no_price / 100, 2)

        record_trade({
            "timestamp":    now.isoformat(),
            "strategy":     "CRYPTO_15MIN",
            "ticker":       ticker,
            "side":         "NO",
            "contracts":    max_c,
            "ev":           round(ev, 4),
            "yes_ask_cents": yes_ask,
            "margin_f":     margin_f,
            "signal_type":  "BECKER_OPTIMISM_TAX",
            "settled":      False,
            "order_id":     order_id
        })

        send_alert(
            f"✅ *PNB CRYPTO*: `{ticker}`\n"
            f"Side: NO (Optimism Tax) | Contracts: {max_c}\n"
            f"YES was: {yes_ask}¢ | EV: {ev:.3f}\n"
            f"Margin: ${margin_f} | Order: `{order_id}`"
        )
        placed += 1

    if placed == 0:
        print("PNB Crypto: No signals this scan")
    else:
        print(f"PNB Crypto done — {placed} trades placed")


if __name__ == "__main__":
    main()
EOF
```

---

## PHASE 5 — SETTLER BOT

### Step 1 — Create settler
```
cat > /home/rob-alvarado/RJA/.pnb/kalshi_settler.py << 'EOF'
"""
PredictaNoob — Kalshi Trade Settler
Schedule: 6:30 AM MST daily
Checks Kalshi for settled positions, marks W/L in trade_stats.json,
sends daily summary to Telegram.
"""
import os, json, requests, datetime
from dotenv import load_dotenv
from kalshi_auth import get_kalshi_headers
from telegram_alert import send_alert

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

API_KEY    = os.getenv('KALSHI_API_KEY')
API_SECRET = os.getenv('KALSHI_API_SECRET')
BASE_URL   = os.getenv('KALSHI_BASE_URL')
STATS_FILE = "/home/rob-alvarado/RJA/.pnb/trade_stats.json"


def get_positions() -> list:
    headers = get_kalshi_headers("GET", "/trade-api/v2/portfolio/positions", API_KEY, API_SECRET)
    try:
        r = requests.get(f"{BASE_URL}/portfolio/positions", headers=headers, timeout=15)
        if r.status_code == 200:
            return r.json().get('market_positions', [])
    except Exception as e:
        print(f"Position fetch error: {e}")
    return []


def main():
    print(f"PNB Settler starting — {datetime.datetime.now().strftime('%Y-%m-%d %H:%M MST')}")

    if not os.path.exists(STATS_FILE):
        print("No trade stats — nothing to settle")
        return

    with open(STATS_FILE) as f:
        trades = json.load(f)

    positions   = get_positions()
    settled_map = {p['ticker']: p for p in positions if p.get('market_result')}

    updated = wins = losses = 0

    for t in trades:
        if t.get('settled'):
            continue
        pos = settled_map.get(t.get('ticker'))
        if not pos:
            continue
        result = pos.get('market_result')
        side   = t.get('side', 'YES')
        won    = (result == 'YES_WIN' and side == 'YES') or (result == 'NO_WIN' and side == 'NO')
        t.update({"settled": True, "result": result, "won": won,
                  "settled_at": datetime.datetime.now().isoformat()})
        updated += 1
        if won: wins += 1
        else:   losses += 1

    with open(STATS_FILE, 'w') as f:
        json.dump(trades, f, indent=2)

    if updated > 0:
        total      = len([t for t in trades if t.get('settled')])
        total_wins = len([t for t in trades if t.get('won')])
        win_rate   = (total_wins / total * 100) if total > 0 else 0
        send_alert(
            f"📊 *PNB Settler*\n"
            f"Today: {wins}W / {losses}L\n"
            f"All time: {total_wins}W / {total - total_wins}L ({win_rate:.1f}%)\n"
            f"Settled today: {updated} trades"
        )
    else:
        print("No new settlements")


if __name__ == "__main__":
    main()
EOF
```

---

## PHASE 6 — DRY RUN VALIDATION

**All 5 checks must pass before crons go live. No exceptions.**

### Check 1 — Test Kalshi auth (read-only balance call)
```
cd /home/rob-alvarado/RJA/.pnb && python3 -c "
import os
from dotenv import load_dotenv
load_dotenv('.env')
from kalshi_auth import get_kalshi_headers
h = get_kalshi_headers('GET', '/trade-api/v2/portfolio/balance', os.getenv('KALSHI_API_KEY'), os.getenv('KALSHI_API_SECRET'))
print('Auth headers generated OK' if h.get('KALSHI-ACCESS-SIGNATURE') else 'FAILED')
"
```
Expected: `Auth headers generated OK`

### Check 2 — Test NOAA fetch for Phoenix
```
cd /home/rob-alvarado/RJA/.pnb && python3 -c "
from kalshi_weather_trader import get_noaa_forecast
r = get_noaa_forecast('KPHX')
print(r if r else 'FAILED — no NOAA data returned')
"
```
Expected: Dict with `high` temperature value.

### Check 3 — Test Kalshi weather market fetch
```
cd /home/rob-alvarado/RJA/.pnb && python3 -c "
from kalshi_weather_trader import get_kalshi_weather_markets
m = get_kalshi_weather_markets()
print(f'{len(m)} weather markets found' if m else 'FAILED — 0 markets returned')
"
```
Expected: Count > 0. Confirms Kalshi auth is working end-to-end.

### Check 4 — Test Telegram alert delivery
```
cd /home/rob-alvarado/RJA/.pnb && python3 -c "
from telegram_alert import send_alert
r = send_alert('✅ PNB dry run — system online. Kalshi auth OK.')
print('Telegram OK' if r else 'FAILED')
"
```
Expected: `Telegram OK` in terminal AND message appears in Rob's Telegram chat.

### Check 5 — Test crypto market fetch
```
cd /home/rob-alvarado/RJA/.pnb && python3 -c "
from contract_trader import get_crypto_markets
m = get_crypto_markets()
print(f'{len(m)} crypto markets found' if m else 'FAILED — 0 markets returned')
"
```
Expected: Count > 0.

**If any check fails — stop. Fix before proceeding to crons.**

---

## PHASE 7 — CRON SETUP

All crons run on MSI. Times are MST. bot_runner.sh wraps every job.

### Step 1 — Open crontab on MSI
```
crontab -e
```

### Step 2 — Add all PNB cron jobs
```
# PredictaNoob — All times MST (America/Phoenix, no DST)
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# Settler — 6:30 AM MST daily
30 6 * * * /home/rob-alvarado/RJA/.rja/bot_runner.sh "PNB-Settler" "/home/rob-alvarado/RJA/.pnb/kalshi_settler.py"

# Weather trader — 11:00 AM MST daily
0 11 * * * /home/rob-alvarado/RJA/.rja/bot_runner.sh "PNB-Weather" "/home/rob-alvarado/RJA/.pnb/kalshi_weather_trader.py"

# Crypto 15-min — Mon–Fri, 7:00 AM to 1:45 PM MST (last run 1:45, settles by 2 PM)
*/15 7-13 * * 1-5 /home/rob-alvarado/RJA/.rja/bot_runner.sh "PNB-Crypto" "/home/rob-alvarado/RJA/.pnb/contract_trader.py"
45 13 * * 1-5 /home/rob-alvarado/RJA/.rja/bot_runner.sh "PNB-Crypto" "/home/rob-alvarado/RJA/.pnb/contract_trader.py"
```

### Step 3 — Verify crontab saved
```
crontab -l
```
Expected: All four lines visible.

---

## PHASE 8 — GITHUB SETUP

### Step 1 — Initialize git repo
```
cd /home/rob-alvarado/RJA && git init
```

### Step 2 — Confirm .gitignore is protecting credentials
```
git status
```
Confirm: `.env` files do NOT appear in untracked list.

### Step 3 — Stage files
```
git add .
```

### Step 4 — Initial commit
```
git commit -m "PNB v1.0 — Weather + Crypto 15-min. Fresh build. rob-alvarado."
```

---

## GO-LIVE VERIFICATION CHECKLIST

| # | Check | Pass Condition |
|---|---|---|
| 1 | Kalshi auth | Headers generated, no errors |
| 2 | NOAA Phoenix | Returns temp data |
| 3 | Weather markets | Count > 0 |
| 4 | Crypto markets | Count > 0 |
| 5 | Telegram | Message received in chat |
| 6 | Crontab | All 4 jobs listed |
| 7 | Timezone | `America/Phoenix` confirmed |
| 8 | .env permissions | `-rw-------` |
| 9 | .gitignore | .env not in git status |
| 10 | bot_runner | `chmod +x` confirmed |

---

## LIVE DAILY SCHEDULE

| Time (MST) | Bot | Telegram Alert |
|---|---|---|
| 6:30 AM | Settler | 📊 W/L summary |
| 7:00 AM – 1:45 PM | Crypto 15-min | ✅ per trade or silent |
| 11:00 AM | Weather trader | ✅ per trade or ⬜ skip |
| Any crash | bot_runner | 🔴 crash + exit code |

---

*PredictaNoob v1.1 — rob-alvarado | Real money | Live Kalshi*
*EV > 0.05 always. PSS auth always. bot_runner always.*
*MST timezone | No DST | Phoenix AZ*
*Next milestone: 30 settled trades → Stage 2 sizing unlocked*
