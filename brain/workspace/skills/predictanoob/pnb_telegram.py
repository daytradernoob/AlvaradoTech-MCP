"""
PredictaNoob -- Telegram Reporter
Sends messages via the OpenClaw bot already configured on SEi.
"""
import requests

BOT_TOKEN = "7674882880:AAHJytnPvztbM3YdyMxxTAj85AbDDf5mAcM"
CHAT_ID   = "1489345296"
API_URL   = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

def send(text):
    """Send a plain text message to Rob's Telegram chat."""
    try:
        r = requests.post(API_URL, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print(f"Telegram send failed: {e}")
        return False
