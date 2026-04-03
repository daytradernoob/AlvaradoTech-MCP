#!/bin/bash
# AlvaradoTech-MCP — VPS Quick Setup Script
# Tested on: Ubuntu 22.04 LTS (Hetzner CX32 or equivalent)
# Run as root or with sudo

set -e

echo "═══════════════════════════════════════════"
echo "  AlvaradoTech-MCP — VPS Setup"
echo "═══════════════════════════════════════════"

# ── System deps ──────────────────────────────
echo "[1/5] Installing system dependencies..."
apt-get update -qq
apt-get install -y -qq curl git docker.io docker-compose

# Enable Docker
systemctl enable docker
systemctl start docker

# ── Clone repo ───────────────────────────────
echo "[2/5] Cloning repository..."
cd /opt
if [ ! -d "AlvaradoTech-MCP" ]; then
  git clone https://github.com/daytradernoob/AlvaradoTech-MCP.git
fi
cd AlvaradoTech-MCP

# ── Environment setup ─────────────────────────
echo "[3/5] Setting up environment..."
if [ ! -f "deploy/.env" ]; then
  cp deploy/.env.example deploy/.env
  echo ""
  echo "┌─────────────────────────────────────────┐"
  echo "│  REQUIRED: Edit deploy/.env             │"
  echo "│  Add your Telegram token, chat ID,      │"
  echo "│  and Anthropic API key before continuing│"
  echo "└─────────────────────────────────────────┘"
  echo ""
  read -p "Press ENTER after editing deploy/.env..."
fi

# ── Build openclaw config ─────────────────────
echo "[4/5] Generating OpenClaw config..."
MODEL=$(grep MCP_PRIMARY_MODEL deploy/.env | cut -d= -f2)
BOT_TOKEN=$(grep TELEGRAM_BOT_TOKEN deploy/.env | cut -d= -f2)
CHAT_ID=$(grep TELEGRAM_CHAT_ID deploy/.env | cut -d= -f2)
ANTHROPIC_KEY=$(grep ANTHROPIC_API_KEY deploy/.env | cut -d= -f2)
BRAVE_KEY=$(grep BRAVE_SEARCH_API_KEY deploy/.env | cut -d= -f2)
GW_TOKEN=$(grep OPENCLAW_GATEWAY_TOKEN deploy/.env | cut -d= -f2)

mkdir -p /opt/openclaw-data
cat > /opt/openclaw-data/openclaw.json << ENDCONFIG
{
    "models": {
        "mode": "merge",
        "providers": {
            "anthropic": {
                "apiKey": "${ANTHROPIC_KEY}",
                "api": "anthropic"
            }
        }
    },
    "agents": {
        "defaults": {
            "model": {
                "primary": "${MODEL}"
            },
            "workspace": "/data/workspace",
            "elevatedDefault": "full",
            "timeoutSeconds": 900
        }
    },
    "tools": {
        "profile": "coding",
        "allow": ["group:runtime", "group:fs"],
        "web": {
            "search": {
                "enabled": true,
                "provider": "brave"
            }
        },
        "elevated": {
            "enabled": true,
            "allowFrom": {
                "telegram": ["${CHAT_ID}"]
            }
        }
    },
    "channels": {
        "telegram": {
            "enabled": true,
            "dmPolicy": "pairing",
            "botToken": "${BOT_TOKEN}",
            "streaming": "off"
        }
    },
    "gateway": {
        "port": 18789,
        "mode": "local",
        "bind": "lan",
        "auth": {
            "mode": "token",
            "token": "${GW_TOKEN}"
        }
    },
    "plugins": {
        "entries": {
            "brave": {
                "enabled": true,
                "config": {
                    "webSearch": {
                        "apiKey": "${BRAVE_KEY}"
                    }
                }
            }
        }
    }
}
ENDCONFIG

# Copy workspace files
cp -r brain/workspace/* /opt/openclaw-data/workspace/ 2>/dev/null || true

# ── Launch ────────────────────────────────────
echo "[5/5] Launching MCP platform..."
cd deploy
docker-compose up -d

echo ""
echo "═══════════════════════════════════════════"
echo "  MCP Platform is running"
echo "  Gateway: http://$(curl -s ifconfig.me):18789"
echo "  Message your Telegram bot to verify"
echo "═══════════════════════════════════════════"
