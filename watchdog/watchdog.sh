#!/bin/bash
# Pi-4 Watchdog — pings MSI and SEi every 5 min, alerts via Telegram on failure
# Deploy to: /home/rob-alvarado/watchdog.sh on Pi-4 (.204)
# Cron: */5 * * * * /home/rob-alvarado/watchdog.sh

TELEGRAM_TOKEN="YOUR_BOT_TOKEN"   # Use the bot token, NOT the chat ID
CHAT_ID="YOUR_CHAT_ID"            # Your Telegram user ID
MSI="192.168.0.146"
SEI="192.168.0.165"

send_alert() {
  curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
    -d chat_id="${CHAT_ID}" \
    -d text="$1"
}

if ! ping -c 1 -W 3 $MSI > /dev/null 2>&1; then
  send_alert "MSI-RTX (.146) UNREACHABLE — Ollama and bots may be down"
fi

if ! ping -c 1 -W 3 $SEI > /dev/null 2>&1; then
  send_alert "SEi-miniPC (.165) UNREACHABLE — OpenClaw gateway may be down"
fi
