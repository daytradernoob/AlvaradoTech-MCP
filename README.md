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

The agent has persistent memory, a defined identity, and elevated tool access you approve once. It runs 24/7. It monitors itself.

---

## The Stack

| Layer | Component | What It Does |
|---|---|---|
| Inference | Ollama + RTX 3060 | Local GPU — no API costs |
| Agent Engine | OpenClaw | Multi-agent execution, Telegram integration |
| Human Interface | Telegram Bot | Commands, approvals, alerts |
| Cockpit | Nerve UI | Agent control, workspace, kanban |
| Dashboard | Bot-Review | Agents, models, sessions, stats at a glance |
| Watchdog | Pi-4 + cron | Pings fleet every 5 min, alerts on failure |
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

- Respond to commands in Telegram as a named agent (not "I am Qwen")
- Execute file operations, scripts, and system commands on approval
- Monitor fleet health and alert you when machines go down
- Maintain persistent memory across sessions via .MD files
- Display agent status, model usage, and session stats in a web dashboard

---

## Clone and Run It

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
3. Copy `brain/` files to `~/.openclaw/workspace/`
4. Run `openclaw gateway start`
5. Message your bot: `who are you?`

Full step-by-step: see [`docs/06_SEi_OPENCLAW_SETUP.md`](docs/06_SEi_OPENCLAW_SETUP.md)

---

## The Brain Files

Everything the agent knows about itself lives in `brain/`:

| File | Purpose |
|---|---|
| `SOUL.md` | Who the agent is — identity, character, directives |
| `MEMORY.md` | Persistent system state and lessons learned |
| `ROADMAP.md` | Build sequence — where we are and where we're going |
| `LEARN.md` | Research protocols |

These files are injected into the agent's context on every session. Edit them to make the agent yours.

---

## The Watchdog

Deploy `watchdog/watchdog.sh` to a Raspberry Pi (or any always-on machine):

```bash
# Add to crontab
*/5 * * * * /home/pi/watchdog.sh
```

Pings your fleet every 5 minutes. Sends a Telegram alert if anything goes down.

---

## Credentials

**Never commit to this repo:**
- API keys, tokens, bot tokens
- `.env` files or private keys

Store secrets in `~/.openclaw/openclaw.json` — it's in `.gitignore`.

---

## Why I Built This

AI is not a product. It's an operating layer.

The same insight that drove infrastructure shifts in enterprise IT applies here: the people who own the layer win. This repo is the foundation — a replicable base that anyone can clone, configure, and extend with their own ideas.

Two testers are already building on it. Their ideas, executed by the stack.

---

## Status

- Phase 0 — Foundation: ✅ Complete
- Phase 1 — Cockpit & Visibility: ✅ Complete
- Phase 2 — Home Office Network: In progress
- Phase 3 — Initiative Expansion: Queued

---

*Phoenix metro, AZ | Self-hosted. Local inference. End of Line.*
