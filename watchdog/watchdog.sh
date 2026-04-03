#!/bin/bash
# Pi-4 Watchdog — checks MSI Ollama API and SEi OpenClaw gateway every 5 min
# Deploy to: /home/robalvarado/watchdog.sh on Pi-4 (.204)
# Cron: */5 * * * * /home/robalvarado/watchdog.sh

TELEGRAM_TOKEN="YOUR_BOT_TOKEN"   # Bot token from BotFather
CHAT_ID="YOUR_CHAT_ID"            # Your Telegram user ID
MSI="192.168.0.146"
SEI="192.168.0.165"

send_alert() {
  curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
    -d chat_id="${CHAT_ID}" \
    -d text="$1"
}

# Check MSI — Ollama API health (not just ping)
if ! curl -sf --connect-timeout 5 "http://${MSI}:11434/api/tags" > /dev/null 2>&1; then
  send_alert "⚠️ MSI-RTX (.146) UNREACHABLE — Ollama API down or machine offline"
fi

# Check SEi — OpenClaw gateway health (not just ping)
if ! curl -sf --connect-timeout 5 "http://${SEI}:18789/" > /dev/null 2>&1; then
  send_alert "⚠️ SEi-miniPC (.165) UNREACHABLE — OpenClaw gateway down or machine offline"
fi
