#!/usr/bin/env bash
# Promotes an agent or workspace file from DEV (HP laptop) to PROD (SEi Mini PC).
# Usage:
#   ./promote-agent.sh                         # promote entire workspace
#   ./promote-agent.sh agents/MyBot.md         # promote a single file
#   ./promote-agent.sh agents/MyBot.md --dry-run

set -euo pipefail

PROD_HOST="rob-alvarado@192.168.0.165"
PROD_WORKSPACE="~/.openclaw/workspace"
LOCAL_WORKSPACE="/home/rob-alvarado/.openclaw/workspace"

# PROD notification tokens (set via environment variables)
# Export before running: export PROD_TELEGRAM_TOKEN="..." etc.

TARGET="${1:-}"
DRY_RUN="${2:-}"

timestamp() { date '+%Y-%m-%d %H:%M:%S'; }

notify_telegram() {
  local msg="$1"
  if [[ -z "${PROD_TELEGRAM_TOKEN:-}" ]]; then
    echo "[SKIP] Telegram: no token"
    return
  fi
  curl -s -X POST "https://api.telegram.org/bot${PROD_TELEGRAM_TOKEN}/sendMessage" \
    -d chat_id="${PROD_TELEGRAM_CHAT_ID:-1489345296}" \
    -d text="${msg}" \
    -d parse_mode="HTML" > /dev/null
}

notify_discord() {
  local msg="$1"
  if [[ -z "${PROD_DISCORD_TOKEN:-}" ]]; then
    echo "[SKIP] Discord: no token"
    return
  fi
  if [[ -n "${PROD_DISCORD_CHANNEL_ID:-}" ]]; then
    curl -s -X POST "https://discord.com/api/v10/channels/${PROD_DISCORD_CHANNEL_ID}/messages" \
      -H "Authorization: Bot ${PROD_DISCORD_TOKEN}" \
      -H "Content-Type: application/json" \
      -d "{\"content\": \"${msg}\"}" > /dev/null
  fi
}

# --- Determine what to sync ---
if [[ -z "$TARGET" ]]; then
  LABEL="full workspace"
  SRC="${LOCAL_WORKSPACE}/"
  DEST="${PROD_HOST}:${PROD_WORKSPACE}/"
  RSYNC_ARGS="--recursive --delete --exclude='*.log' --exclude='sessions/'"
else
  LABEL="$TARGET"
  SRC="${LOCAL_WORKSPACE}/${TARGET}"
  DEST="${PROD_HOST}:${PROD_WORKSPACE}/$(dirname "$TARGET")/"
  RSYNC_ARGS=""
fi

echo "[$(timestamp)] PROMOTE: $LABEL"
echo "  FROM: $SRC"
echo "  TO:   ${PROD_HOST}:${PROD_WORKSPACE}"

if [[ "$DRY_RUN" == "--dry-run" ]]; then
  echo "[DRY RUN] rsync $RSYNC_ARGS $SRC $DEST"
  exit 0
fi

# --- Sync ---
rsync -avz $RSYNC_ARGS "$SRC" "$DEST"

# --- Notify PROD channels ---
MSG="🚀 <b>DEPLOY — AlvaradoTech OpenClaw</b>
<b>Target:</b> ${LABEL}
<b>Time:</b> $(timestamp)
<b>From:</b> HP Laptop (DEV) → SEi Mini PC (PROD)

Agent/workspace changes are live. Restart OpenClaw if needed."

echo ""
echo "[$(timestamp)] Sending PROD notifications..."
notify_telegram "$MSG"
notify_discord "🚀 DEPLOY | ${LABEL} promoted to PROD at $(timestamp)"

echo "[$(timestamp)] Done."
