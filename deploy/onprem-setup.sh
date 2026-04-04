#!/bin/bash
# AlvaradoTech-MCP — On-Prem Setup Script (Track A)
# Tested on: macOS (Mac Mini M4 Pro), Ubuntu 22.04
# Run as regular user (not root)
# Prerequisites: Ollama installed, Node.js 20+, Telegram bot token ready

set -e

echo "═══════════════════════════════════════════"
echo "  AlvaradoTech-MCP — On-Prem Setup"
echo "  Track A: Local inference, no cloud"
echo "═══════════════════════════════════════════"
echo ""

# ── Check prerequisites ──────────────────────
echo "[1/6] Checking prerequisites..."

if ! command -v ollama &> /dev/null; then
  echo "✗ Ollama not found. Install from https://ollama.ai then re-run."
  exit 1
fi
echo "  ✓ Ollama found"

if ! command -v node &> /dev/null; then
  echo "✗ Node.js not found. Install Node.js 20+ then re-run."
  exit 1
fi
echo "  ✓ Node.js found"

if ! command -v npm &> /dev/null; then
  echo "✗ npm not found."
  exit 1
fi
echo "  ✓ npm found"

# ── Install OpenClaw ─────────────────────────
echo ""
echo "[2/6] Installing OpenClaw..."
if command -v openclaw &> /dev/null; then
  echo "  ✓ OpenClaw already installed ($(openclaw --version 2>/dev/null || echo 'version unknown'))"
else
  npm install -g openclaw@latest
  echo "  ✓ OpenClaw installed"
fi

# ── Pull model ───────────────────────────────
echo ""
echo "[3/6] Setting up inference model..."

if ollama list 2>/dev/null | grep -q "mcp-qwen3"; then
  echo "  ✓ mcp-qwen3 already exists"
else
  echo "  Pulling qwen3:8b base model (this may take a few minutes)..."
  ollama pull qwen3:8b

  echo "  Creating mcp-qwen3 (8k context, tuned parameters)..."
  MODELFILE=$(mktemp)
  cat > "$MODELFILE" << 'MODELEOF'
FROM qwen3:8b
PARAMETER num_ctx 8192
PARAMETER temperature 0.7
PARAMETER top_k 40
PARAMETER top_p 0.9
MODELEOF
  ollama create mcp-qwen3 --file "$MODELFILE"
  rm "$MODELFILE"
  echo "  ✓ mcp-qwen3 created"
fi

# ── Collect configuration ────────────────────
echo ""
echo "[4/6] Configuration"
echo ""
echo "You need two things from Telegram:"
echo "  1. A bot token from @BotFather"
echo "  2. Your Telegram user ID (message @userinfobot to get it)"
echo ""

read -p "  Telegram bot token: " BOT_TOKEN
read -p "  Your Telegram user ID: " CHAT_ID

echo ""
read -p "  Gateway auth token (press ENTER to auto-generate): " GW_TOKEN
if [ -z "$GW_TOKEN" ]; then
  GW_TOKEN=$(openssl rand -hex 32 2>/dev/null || cat /dev/urandom | head -c 32 | xxd -p | tr -d '\n')
  echo "  Generated: $GW_TOKEN"
  echo "  (Save this — you'll need it to connect external tools to the gateway)"
fi

# ── Generate config ──────────────────────────
echo ""
echo "[5/6] Generating OpenClaw config..."

mkdir -p ~/.openclaw/workspace/skills ~/.openclaw/workspace/data/msp_sample

cat > ~/.openclaw/openclaw.json << ENDCONFIG
{
    "models": {
        "mode": "merge",
        "providers": {
            "ollama": {
                "api": "ollama",
                "baseURL": "http://127.0.0.1:11434"
            }
        }
    },
    "agents": {
        "defaults": {
            "model": {
                "primary": "ollama/mcp-qwen3"
            },
            "workspace": "~/.openclaw/workspace",
            "elevatedDefault": "full",
            "timeoutSeconds": 900
        }
    },
    "tools": {
        "profile": "coding",
        "allow": ["group:runtime", "group:fs"],
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
    }
}
ENDCONFIG

echo "  ✓ Config written to ~/.openclaw/openclaw.json"

# ── Copy workspace files ─────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

if [ -d "$REPO_ROOT/brain/workspace" ]; then
  cp "$REPO_ROOT/brain/workspace/AGENTS.md" ~/.openclaw/workspace/
  cp "$REPO_ROOT/brain/workspace/SOUL.md" ~/.openclaw/workspace/
  cp "$REPO_ROOT/brain/workspace/IDENTITY.md" ~/.openclaw/workspace/
  cp "$REPO_ROOT/brain/workspace/SESSION.md" ~/.openclaw/workspace/
  cp -r "$REPO_ROOT/brain/workspace/skills" ~/.openclaw/workspace/
  cp -r "$REPO_ROOT/brain/workspace/data/msp_sample" ~/.openclaw/workspace/data/
  echo "  ✓ Workspace files copied"
else
  echo "  ⚠ brain/workspace not found — workspace files not copied"
  echo "    Run from inside the cloned AlvaradoTech-MCP repo directory"
fi

# Copy USER.md template if no USER.md exists
if [ ! -f ~/.openclaw/workspace/USER.md ]; then
  if [ -f "$REPO_ROOT/brain/workspace/USER.md.template" ]; then
    cp "$REPO_ROOT/brain/workspace/USER.md.template" ~/.openclaw/workspace/USER.md
    echo "  ✓ USER.md template installed (onboarding interview will run on first message)"
  fi
fi

# ── Launch ───────────────────────────────────
echo ""
echo "[6/6] Starting MCP gateway..."
openclaw gateway start &
sleep 3

echo ""
echo "═══════════════════════════════════════════"
echo "  MCP Platform is running"
echo ""
echo "  Gateway:  http://$(hostname -I | awk '{print $1}'):18789"
echo "  Model:    ollama/mcp-qwen3"
echo "  Telegram: connected"
echo ""
echo "  Message your Telegram bot to verify."
echo "  First message: 'who are you?'"
echo "═══════════════════════════════════════════"
