# RJA DIVISION OF RESOURCES
## MCP Execution Document — Hardware Fleet Configuration
### Version 1.1 | rob-alvarado user | Node 22 LTS | Ollama SEi-only binding

---

> Execute in order. One command per block. Verify output before proceeding.
> All times MST. Phoenix AZ does not observe DST.

---

## FLEET INVENTORY

| Host | IP | CPU | RAM | Storage | GPU | Assigned Role |
|---|---|---|---|---|---|---|
| HP-1030-G2 | 192.168.0.207 | i7-7600U (2c/4t) | 14GB | 256GB | HD 620 | Human Interface |
| MSI-RTX | 192.168.0.146 | i7-11800H (8c/16t) | 14GB | 953GB+1TB | RTX 3060 | Compute + Ollama |
| SEi-miniPC | 192.168.0.165 | i7-12650H (8c/16t) | 30GB | 465GB | UHD | OpenClaw Gateway + Brain |
| Pi-4 | 192.168.0.204 | Cortex-A72 (4c) | 4GB | 32GB | — | Watchdog / Heartbeat |

---

## ROLE DEFINITIONS

### HP-1030-G2 (.207) — HUMAN INTERFACE ONLY
- Rob's daily machine. SSH client, Claude Desktop, Telegram, browser.
- Nothing persistent runs here. No bots. No crons. No Ollama.
- OpenClaw installed here for Rob's direct interaction with the MCP agent.
- This machine goes to sleep. The system does not depend on it being online.

### MSI-RTX (.146) — COMPUTE NODE (Ollama + Bots)
- Headless Ubuntu. Sleep disabled. Always on.
- Runs Ollama with RTX 3060 GPU acceleration.
- Ollama binds to `192.168.0.146:11434` only — firewall restricts access to SEi (.165) only.
- Runs all trading bots via cron. bot_runner.sh wraps every job.
- Base path: `/home/rob-alvarado/RJA/`
- SSH only. No desktop environment.

### SEi-miniPC (.165) — OPENCLAW GATEWAY + BRAIN
- 30GB RAM handles OpenClaw gateway, Nerve UI, agent workspace, .MD brain files.
- Does NOT compete with Ollama for memory. MSI owns GPU inference.
- OpenClaw Ollama provider points to `http://192.168.0.146:11434`.
- Persistent brain files live here: SOUL.md, MEMORY.md, LEARN.md, ROADMAP.md, SYSTEM.md.
- Always on.

### Pi-4 (.204) — WATCHDOG
- Lightweight health checks only.
- Pings MSI and SEi every 5 minutes.
- Sends Telegram alert if either goes unreachable.
- Runs nothing else.

---

## PHASE 1 — MSI-RTX SETUP (Ollama + GPU)

SSH to MSI:
```
ssh rob-alvarado@192.168.0.146
```

### Step 1 — Verify GPU is recognized
```
nvidia-smi
```
Expected: RTX 3060 listed with driver version. If not found, install NVIDIA drivers before proceeding — do not continue without GPU confirmed.

### Step 2 — Install Ollama
```
curl -fsSL https://ollama.com/install.sh | sh
```

### Step 3 — Verify Ollama installed
```
ollama --version
```

### Step 4 — Configure Ollama: LAN IP binding + KEEP_ALIVE
```
sudo systemctl edit ollama
```
Add these lines between the comment markers:
```
[Service]
Environment="OLLAMA_HOST=192.168.0.146:11434"
Environment="OLLAMA_KEEP_ALIVE=8h"
```
Save and close.

### Step 5 — Reload systemd
```
sudo systemctl daemon-reload
```

### Step 6 — Restart Ollama
```
sudo systemctl restart ollama
```

### Step 7 — Verify Ollama binding (LAN IP only, not 0.0.0.0)
```
ss -tlnp | grep 11434
```
Expected: `192.168.0.146:11434` — if you see `0.0.0.0:11434` the override did not apply, recheck Step 4.

### Step 8 — Install ufw
```
sudo apt-get install -y ufw
```

### Step 9 — Allow SSH through firewall first (do not lock yourself out)
```
sudo ufw allow ssh
```

### Step 10 — Allow Ollama access from SEi only
```
sudo ufw allow from 192.168.0.165 to any port 11434
```

### Step 11 — Enable firewall
```
sudo ufw --force enable
```

### Step 12 — Verify firewall rules
```
sudo ufw status
```
Expected: SSH allowed, port 11434 allowed from 192.168.0.165 only.

### Step 13 — Pull agent model (llama3.2:3b — ~2GB VRAM)
```
ollama pull llama3.2:3b
```
Wait for full download before proceeding.

### Step 14 — Pull MCP analysis model (qwen3:8b — ~5GB VRAM)
```
ollama pull qwen3:8b
```
Wait for full download before proceeding.

### Step 15 — Verify both models present
```
ollama list
```
Expected: `llama3.2:3b` and `qwen3:8b` both listed.

### Step 16 — Disable sleep
```
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
```

### Step 17 — Confirm sleep disabled
```
systemctl status sleep.target
```
Expected: `masked`.

---

## PHASE 2 — SEi-miniPC SETUP (OpenClaw Gateway)

SSH to SEi:
```
ssh rob-alvarado@192.168.0.165
```

### Step 1 — Add NodeSource repo for Node 22 LTS
```
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
```

### Step 2 — Install Node 22 LTS
```
sudo apt-get install -y nodejs
```

### Step 3 — Verify Node version is 22
```
node --version
```
Expected: `v22.x.x`. If lower, the nodesource repo did not apply — rerun Step 1.

### Step 4 — Install OpenClaw
```
npm install -g openclaw
```

### Step 5 — Verify OpenClaw installed
```
openclaw --version
```

### Step 6 — Initialize OpenClaw workspace
```
openclaw init
```

### Step 7 — Create brain directory
```
mkdir -p /home/rob-alvarado/.openclaw/workspace/brain
```

### Step 8 — Write openclaw.json config
```
cat > /home/rob-alvarado/.openclaw/openclaw.json << 'EOF'
{
  "agents": {
    "defaults": {
      "model": { "primary": "ollama/llama3.2:3b" },
      "elevatedDefault": "full",
      "timeoutSeconds": 900
    }
  },
  "tools": {
    "profile": "coding",
    "allow": ["group:runtime", "group:fs"],
    "elevated": {
      "enabled": true,
      "allowFrom": { "telegram": ["YOUR_TELEGRAM_USER_ID"] }
    }
  },
  "models": {
    "providers": {
      "ollama": {
        "baseUrl": "http://192.168.0.146:11434",
        "apiKey": "ollama-local",
        "api": "ollama",
        "models": [
          {"id": "llama3.2:3b", "name": "llama3.2:3b", "api": "ollama"},
          {"id": "qwen3:8b", "name": "qwen3:8b", "api": "ollama"}
        ]
      }
    }
  }
}
EOF
```
**ACTION REQUIRED:** Replace `YOUR_TELEGRAM_USER_ID` with Rob's Telegram user ID before saving.

### Step 9 — Verify config
```
cat /home/rob-alvarado/.openclaw/openclaw.json
```
Confirm user ID is set and baseUrl points to 192.168.0.146:11434.

### Step 10 — Start OpenClaw gateway
```
openclaw gateway start
```

### Step 11 — Verify gateway running
```
openclaw gateway status
```
Expected: Running, model reachable.

### Step 12 — Test Ollama reachable from SEi
```
curl http://192.168.0.146:11434/api/tags
```
Expected: JSON with model list. If blocked, recheck ufw on MSI.

### Step 13 — Disable sleep on SEi
```
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
```

---

## PHASE 3 — Pi-4 WATCHDOG SETUP

SSH to Pi:
```
ssh rob-alvarado@192.168.0.204
```

### Step 1 — Install curl
```
sudo apt-get update && sudo apt-get install -y curl
```

### Step 2 — Create watchdog script
```
cat > /home/rob-alvarado/watchdog.sh << 'EOF'
#!/bin/bash
TELEGRAM_TOKEN="YOUR_BOT_TOKEN"
CHAT_ID="YOUR_CHAT_ID"
MSI="192.168.0.146"
SEI="192.168.0.165"

send_alert() {
  curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
    -d chat_id="${CHAT_ID}" \
    -d text="$1"
}

if ! ping -c 1 -W 3 $MSI > /dev/null 2>&1; then
  send_alert "🔴 MSI-RTX (.146) UNREACHABLE — bots may be down"
fi

if ! ping -c 1 -W 3 $SEI > /dev/null 2>&1; then
  send_alert "🔴 SEi-miniPC (.165) UNREACHABLE — OpenClaw gateway may be down"
fi
EOF
```
**ACTION REQUIRED:** Replace `YOUR_BOT_TOKEN` and `YOUR_CHAT_ID` with real Telegram credentials.

### Step 3 — Make executable
```
chmod +x /home/rob-alvarado/watchdog.sh
```

### Step 4 — Add to cron
```
crontab -e
```
Add:
```
*/5 * * * * /home/rob-alvarado/watchdog.sh
```

### Step 5 — Test manually
```
/home/rob-alvarado/watchdog.sh
```
Expected: Silence if both machines up. Telegram alert if either down.

---

## FINAL VERIFICATION CHECKLIST

| Check | Command | Machine | Expected |
|---|---|---|---|
| GPU recognized | `nvidia-smi` | MSI | RTX 3060 listed |
| Ollama running | `ollama list` | MSI | Both models listed |
| Ollama binding | `ss -tlnp \| grep 11434` | MSI | `192.168.0.146:11434` |
| Firewall | `sudo ufw status` | MSI | 11434 from .165 only |
| LAN reachable | `curl http://192.168.0.146:11434/api/tags` | SEi | JSON model list |
| Node version | `node --version` | SEi | v22.x.x |
| OpenClaw running | `openclaw gateway status` | SEi | Running |
| Telegram connected | Send `MCP status` | Telegram | Agent responds |
| Sleep disabled | `systemctl status sleep.target` | MSI + SEi | Masked |
| Watchdog cron | `crontab -l` | Pi | Entry visible |

---

## MODEL ASSIGNMENT SUMMARY

| Model | Host | VRAM | Purpose | Active Hours |
|---|---|---|---|---|
| llama3.2:3b | MSI (.146) | ~2GB | OpenClaw agent, tool calling | 7 AM – 3 PM MST |
| qwen3:8b | MSI (.146) | ~5GB | MCP nightly analysis | 11 PM – 1 AM MST |

KEEP_ALIVE=8h keeps llama3.2:3b loaded across trading hours. Models do not run simultaneously — no VRAM conflict.

---

*v1.1 — rob-alvarado | Node 22 LTS | Ollama SEi-only | ufw restricted*
*MST timezone | No DST | Phoenix AZ*
*Next: 02_PREDICTANOOB_SETUP.md*
