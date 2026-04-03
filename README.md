# AlvaradoTech-MCP

**A self-hosted AI operating layer you can run on hardware you already own.**

This is my homework. Clone it. Run it. Build on it.

---

## What This Is

Most people interact with AI through a chat window. This is different.

This is an AI that **executes**. You send it a task via Telegram. It plans. It asks for your approval. It runs the command on your hardware. It reports back. No cloud dependency. No subscription. Your data stays on your machines.

```
YOU → Telegram → MCP Agent → OpenClaw → Your Hardware → Reports back to Telegram
```

The agent has persistent memory, a defined identity, and elevated tool access you approve once. It runs 24/7. It monitors itself. And it gets better every week — through operation, research, and direct tester feedback.

---

## The Stack

| Layer | Component | What It Does |
|---|---|---|
| Inference | Ollama + RTX 3060 | Local GPU — no API costs |
| Agent Engine | OpenClaw | Multi-agent execution, Telegram integration |
| Human Interface | Telegram Bot | Commands, approvals, alerts |
| Cockpit | Nerve UI | Agent control, workspace, kanban |
| Dashboard | Bot-Review | Agents, models, sessions, stats at a glance |
| Watchdog | Pi-4 + cron | Checks fleet endpoints every 5 min, alerts on failure |
| Brain | .MD files | Soul, memory, identity — version-controlled |

---

## Hardware I'm Running This On

| Machine | Role | Specs |
|---|---|---|
| MSI Laptop | Ollama inference | i7-11800H, 14GB RAM, RTX 3060 |
| Mini PC (SEi) | OpenClaw gateway | i7-12650H, 30GB RAM |
| Raspberry Pi 4 | Watchdog | 4GB RAM |
| Any machine | Human interface | Browser + Telegram |

Total cost: hardware you probably already have. Running cost: electricity.

---

## What It Can Do Right Now

- Respond to commands in Telegram as a named agent (MCP — not "I am Qwen")
- Answer questions, brainstorm ideas, and analyze requests
- Execute file operations, scripts, and system commands on approval
- Monitor fleet health and alert you when services go down
- Maintain persistent memory across sessions via .MD files
- Display agent status, model usage, and session stats in a web dashboard

---

## Two Ways to Run It

### Track A — On-Prem (Recommended for regulated industries)
Your data never leaves your building. Full 70B model quality. One-time hardware cost.

**Recommended hardware:** Mac Mini M4 Pro, 48GB unified memory (~$1,799)

### Track B — VPS Cloud (~$50-70/month)
No hardware purchase. Runs on a $20/month VPS with Claude API for inference. For cloud-comfortable customers.

```bash
# One-command VPS deploy (Ubuntu 22.04)
git clone https://github.com/daytradernoob/AlvaradoTech-MCP.git
cd AlvaradoTech-MCP
bash deploy/vps-setup.sh
```

Requirements: Anthropic API key, Telegram bot token. See `deploy/.env.example`.

---

## Clone and Run It (On-Prem)

```bash
git clone git@github.com:daytradernoob/AlvaradoTech-MCP.git
cd AlvaradoTech-MCP
```

**Requirements:**
- A machine with 8GB+ RAM (16GB+ recommended)
- [Ollama](https://ollama.ai) installed and running
- [OpenClaw](https://docs.openclaw.ai) installed
- A Telegram bot token ([BotFather](https://t.me/BotFather))

**Setup:**
1. Copy `config/openclaw.template.json` to `~/.openclaw/openclaw.json`
2. Fill in your bot token, Telegram user ID, and Ollama URL
3. Copy `brain/workspace/` files to `~/.openclaw/workspace/`
4. Create a custom Ollama model with adequate context: `ollama create mcp-qwen3 --from qwen3:8b`
5. Run `openclaw gateway start`
6. Message your bot: `who are you?`

Full step-by-step: see [`docs/06_SEi_OPENCLAW_SETUP.md`](docs/06_SEi_OPENCLAW_SETUP.md)

---

## The Brain Files

Everything the agent knows about itself lives in `brain/`:

| File | Purpose |
|---|---|
| `SOUL.md` | Who the agent is — identity, character, directives |
| `MEMORY.md` | Persistent system state, decisions, and lessons learned |
| `ROADMAP.md` | Build sequence — where we are and where we're going |
| `LEARN.md` | Research protocols, model selection log, design pattern research |
| `ARCHITECTURE.md` | Platform design principles and ATC mental model |

Runtime workspace files (what gets injected into every session) live in `brain/workspace/`. Edit them to make the agent yours.

---

## The Watchdog

Deploy `watchdog/watchdog.sh` to a Raspberry Pi (or any always-on machine):

```bash
# Add to crontab
*/5 * * * * /home/pi/watchdog.sh
```

Checks Ollama API and OpenClaw gateway every 5 minutes. Sends a Telegram alert if any service is unreachable — not just if the machine pings.

---

## How This Platform Evolves

This isn't a project that ships and stops. It gets better through use.

Every session generates data. Every tester brings a real idea. Every research pass (Goose, context7, task-master-ai) surfaces patterns that get integrated. Lessons learned go into `brain/MEMORY.md`. Architecture decisions go into `docs/ARCHITECTURE.md`. The roadmap reflects what we've learned, not what we planned to learn.

If you clone this, you're not getting a finished product. You're getting a foundation with a documented learning process. Fork it, build on it, and improve it the same way.

---

## Credentials

**Never commit to this repo:**
- API keys, tokens, bot tokens
- `.env` files or private keys

Store secrets in `~/.openclaw/openclaw.json` — it's in `.gitignore`.

---

## Why This Exists

Businesses want AI. They fear the cloud.

Not irrationally — HIPAA, attorney-client privilege, compliance, data sovereignty. The gap between "wants AI capability" and "can deploy and operate local AI" is enormous. Most businesses can't bridge it themselves. They don't have the infrastructure knowledge. They don't think in these terms.

This platform is the bridge. Local inference. No cloud dependency. Stays in the building. Managed by someone who understands the stack so the customer doesn't have to.

The open-source repo is the foundation. The product is the deployment, configuration, and support on top of it.

---

## Status

- Phase 0 — Foundation: ✅ Complete
- Phase 1 — Cockpit & Visibility: ✅ Complete
- Phase 1.5 — Platform Hardening: 🔄 In Progress
- Phase 2 — Recipe System & Skills: Queued
- Phase 3 — Home Office Network: Queued
- Phase 4 — Initiative Expansion: Future

---

*Phoenix metro, AZ | Self-hosted. Local inference. End of Line.*
