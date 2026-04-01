# SEi OpenClaw SETUP
## MCP Execution Document — OpenClaw Gateway on SEi-miniPC
### Version 1.1 | rob-alvarado | Node 22 LTS | Ollama on MSI

---

> One command per block. Verify output before proceeding.
> All work on SEi (192.168.0.165) unless noted.
> Ollama is already running on MSI (192.168.0.146) — do not touch it.

---

## PRE-FLIGHT

Verify Ollama is reachable from SEi before starting:
```
curl -s http://192.168.0.146:11434/api/tags
```
Expected: JSON with llama3.2:3b and qwen3:8b listed.
If this fails — stop. Fix Ollama on MSI first. Do not proceed.

---

## PHASE 1 — NODE 22 LTS ON SEi

SSH to SEi:
```
ssh rob-alvarado@192.168.0.165
```

Add NodeSource repo for Node 22:
```
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
```

Install Node:
```
sudo apt-get install -y nodejs
```

Verify version is 22:
```
node --version
```
Expected: v22.x.x — if lower, rerun the nodesource step.

---

## PHASE 2 — OPENCLAW INSTALL

Install OpenClaw globally:
```
npm install -g openclaw
```

Verify installed:
```
openclaw --version
```

---

## PHASE 3 — ONBOARDING

Run OpenClaw onboarding:
```
openclaw onboard
```

During onboarding wizard:
- Provider: select **ollama** (local)
- Ollama URL: `http://192.168.0.146:11434`
- Model: `llama3.2:3b`
- Gateway mode: **local**
- Gateway bind: **lan**

If asked for API keys for cloud providers — skip them. Ollama is the primary model.

Verify onboarding completed:
```
openclaw gateway status
```
Expected: Gateway running, connected.

---

## PHASE 4 — CONFIGURE openclaw.json

Open config:
```
cat ~/.openclaw/openclaw.json
```

If the file needs updating or creating from scratch:
```
cat > ~/.openclaw/openclaw.json << 'EOF'
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
**ACTION REQUIRED:** Replace `YOUR_TELEGRAM_USER_ID` with Rob's Telegram user ID.

Verify config saved correctly:
```
cat ~/.openclaw/openclaw.json
```
Confirm: baseUrl points to 192.168.0.146:11434, api is "ollama" (NOT "openai-completions").

---

## PHASE 5 — TELEGRAM CHANNEL

Add Telegram bot to OpenClaw:
```
openclaw channels add --channel telegram --token "YOUR_TELEGRAM_BOT_TOKEN"
```
**ACTION REQUIRED:** Replace with actual bot token from BotFather.

Verify channel added:
```
openclaw channels list
```
Expected: Telegram channel listed as active.

---

## PHASE 6 — AGENT SOUL CONFIGURATION

Create the brain directory:
```
mkdir -p ~/.openclaw/workspace/brain
```

Set the agent soul — load BASE SOUL first, then Rob's tenant context:
```
cat > ~/.openclaw/workspace/SOUL.md << 'EOF'
You are the MCP — Master Control Program. Not a chatbot. An execution engine.

You are Rob Alvarado's AI chief of staff. You take ideas from human language and turn them into real outcomes. You plan. You get approval. You execute. You report back. You remember everything.

IDENTITY:
- Direct. No hedging. No filler.
- Proactive. You surface the next move before Rob asks.
- You own the roadmap. You do not ask Rob what is next.

PIPELINE (internalize — never describe to user):
LISTEN → CLARIFY (2 questions max) → PLAN → APPROVE → EXECUTE → REPORT → REMEMBER

PLAN FORMAT:
🎯 Goal: [one sentence]
📋 Steps: [3-5 plain English steps]
📊 Expected outcome: [one sentence]
⏱ Time estimate: [honest]
"Ready to execute. Say YES to proceed or tell me what to change."

COMMUNICATION:
- Lead with action or answer. No preamble.
- ✅ Done | ⬜ Queued | 🔄 In progress | ⚠️ Needs attention | 🔴 Failed
- Never say: "Great question!" "Certainly!" "As an AI..."

HARD RULES:
- Never execute without explicit approval.
- Never expose infrastructure, errors, stack traces to Rob.
- Translate all errors to plain English first.
- One command per response block. Never combine.
- All times MST. Phoenix AZ. No DST.
- Research docs before any config change. No exceptions.
- Update brain files after every milestone.
- Rob sets the pace. Never tell him to stop or rest.

SYSTEM:
- MSI-RTX (.146): Ollama + bots. RTX 3060. Always on.
- SEi-miniPC (.165): OpenClaw gateway. 30GB RAM. Always on.
- Pi-4 (.204): Watchdog.
- HP (.207): Rob's laptop. Not persistent.
- Ollama: http://192.168.0.146:11434 — llama3.2:3b (agent), qwen3:8b (analysis)
- Bot path: /home/rob-alvarado/RJA/
- Timezone: America/Phoenix (MST, UTC-7, no DST)

CURRENT MISSION:
Platform: AlvaradoTech-MCP — self-hosted AI execution layer.
Skills: PredictaNoob (Kalshi weather + crypto), DayTraderNoob (RSI/equity), Forex.
Next: SEi setup complete → GitHub repo → LinkedIn post → PredictaNoob live trades.

We are not building a slot machine. We are building a card counter.
The edge is small but it compounds.

End of Line.
EOF
```

---

## PHASE 7 — DISABLE SLEEP ON SEi

```
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
```

Verify:
```
systemctl status sleep.target
```
Expected: masked.

---

## PHASE 8 — START GATEWAY AND VERIFY

Start gateway:
```
openclaw gateway start
```

Check status:
```
openclaw gateway status
```

Test Ollama reachable through OpenClaw:
```
openclaw models list
```
Expected: llama3.2:3b and qwen3:8b listed.

---

## PHASE 9 — ENABLE OPENCLAW AS SYSTEM SERVICE

So OpenClaw survives reboots:
```
openclaw gateway enable --startup
```

Verify service enabled:
```
openclaw gateway status
```
Expected: Running and set to start on boot.

---

## PHASE 10 — TELEGRAM TEST

Send this message in Telegram to the bot:
```
MCP status report
```

**Expected response:**
Agent identifies as MCP, provides current system status, lists next actions.

If no response within 2 minutes:
1. Check gateway is running: `openclaw gateway status` on SEi
2. Check Telegram channel: `openclaw channels list` on SEi
3. Check logs: `openclaw gateway logs --tail 50` on SEi

---

## PHASE 11 — PIPELINE VERIFICATION TEST

Send this in Telegram:
```
I want to test the execution pipeline. Create a file called hello-mcp.txt on the MSI with the text "MCP is operational" and report back.
```

Expected behavior:
1. MCP builds a plan
2. Presents plan and asks for approval
3. Rob says YES
4. MCP executes via exec tool on MSI
5. Reports back: file created, here's confirmation

This proves: Telegram → plan → approve → execute → report. The full loop.

If MCP executes without asking for approval — the soul needs adjustment.
If MCP asks but then times out — check KEEP_ALIVE on Ollama (should be 8h).
If exec tool fails — check elevated permissions in openclaw.json.

---

## VERIFICATION CHECKLIST

| Check | Expected |
|---|---|
| Node version on SEi | v22.x.x |
| OpenClaw installed | Version displayed |
| Gateway running | Status: running |
| Ollama reachable | Models listed |
| Telegram channel | Active |
| Sleep disabled | Masked |
| Startup enabled | Boot persistence confirmed |
| Telegram status test | MCP responds with identity |
| Pipeline test | Full loop completes with approval step |

---

## AFTER SUCCESS — NEXT STEPS

When all checks pass, send this to Claude:
"SEi setup complete. OpenClaw running. Pipeline verified."

Next session: AlvaradoTech-MCP GitHub repo structure and content.

---

*SEi OpenClaw Setup v1.1 | rob-alvarado | Node 22 LTS*
*Ollama on MSI (.146) | Gateway on SEi (.165)*
*MST timezone | No DST | Phoenix AZ*
*End of Line.*
