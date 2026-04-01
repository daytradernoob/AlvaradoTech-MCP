# MEMORY.md — Persistent Knowledge Base
*Last Updated: 2026-04-01 | Version: 1.2*

---

## Operator Profile

| Field | Value |
|---|---|
| Name | Rob Alvarado |
| Age | 54 |
| Location | Phoenix metro, AZ (MST — No DST) |
| Background | Former Army Flight Medic |
| IT Experience | 20+ years |
| Notable Achievement | Nutanix SE of the Year 2019 |
| Mindset | Has crossed the chasm |
| Operating Tempo | Self-directed. Does not need prompting to rest. |

---

## System State

### OpenClaw
- **Status:** OPERATIONAL — Phase 0 complete 2026-04-01
- **Telegram:** CONNECTED + VERIFIED — Bot responds as MCP
- **MCP Identity:** CONFIRMED — IDENTITY.md + SOUL.md injected each session
- **Workspace Injection:** CONFIRMED — AGENTS.md, SOUL.md, IDENTITY.md auto-load
- **Nerve:** OPERATIONAL — http://YOUR_SEI_IP:3080 — password: [stored locally]
- **Bot-Review Dashboard:** OPERATIONAL — http://YOUR_SEI_IP:3081
- **Gateway Port:** 18789
- **Config Path:** `~/.openclaw/openclaw.json`
- **Gateway Host:** SEi-miniPC (192.168.0.165)
- **Inference Host:** MSI-RTX (192.168.0.146) — Ollama + RTX 3060
- **Models:** qwen3-4k (primary), llama3.2:3b (available)

### Home Office Network (RJA-NET)
- **Status:** DESIGN PHASE — 2026-03-29
- **Scope:** IoT, networking, all tech inside RJA Home Office
- **Next Step:** Network topology audit and device inventory

---

## Key Decisions Made

| Date | Decision | Rationale |
|---|---|---|
| 2026-03-29 | OpenClaw selected as execution engine | Multi-agent, persistent, Telegram-native, Nerve cockpit available |
| 2026-03-29 | Nerve selected as UI layer | Voice, kanban, fleet control, per-agent soul/memory/workspace |
| 2026-03-29 | Bot-Review dashboard noted for monitoring | Lightweight, reads config directly, no DB, good for fleet health |
| 2026-03-29 | MCP brain externalized to .MD files | Persistent, versionable, loadable into any session |

---

## Architecture Decisions

### Why OpenClaw + Nerve (not n8n or AutoGPT)
- OpenClaw is agent-native, not workflow-native. The RJA stack needs agents that think, not flows that execute.
- Nerve gives real fleet control: per-agent soul, memory, workspace, kanban, voice — not just a chat window.
- Telegram integration is first-class, not bolted on.
- Skills system allows the agent to write its own skills. Self-improving.

### Why .MD Files as Brain
- Loadable into any Claude session instantly.
- Human-readable, versionable, auditable.
- Not locked into any vendor's memory format.
- Rob can read and edit directly. The brain is transparent.

### Why MCP Protocol Matters for This Stack
- MCP = USB for AI tools. Write a server once, any compatible AI uses it.
- Standardized, discoverable, sandboxed, composable.
- The RJA Home Office MCP server will expose: IoT controls, network state, device health, calendar, alerts.
- Any Claude session can connect and operate the home office.
- Future initiatives will add their own MCP servers as domains expand.

---

## Skills Installed
*(Update as skills are added)*

| Skill | Status | Purpose |
|---|---|---|
| None yet | — | — |

---

## MCP Servers Connected
*(Update as servers come online)*

| Server | Status | Exposes |
|---|---|---|
| None yet | — | — |

---

## Credentials & Secrets Location
**DO NOT store secrets in this file.**
Secrets live in: `~/.openclaw/.env` or system keychain.
Reference them here by name only.

| Secret Name | Purpose | Location |
|---|---|---|
| ANTHROPIC_API_KEY | Claude API | ~/.openclaw/.env |
| TELEGRAM_BOT_TOKEN | Telegram bot | ~/.openclaw/openclaw.json |

---

## Public Mission

This repo is the homework. The goal: publish a base MCP model on GitHub that anyone can clone and use to run their own AI operating layer. Local inference. No cloud dependency. Self-hosted. The foundation is the advantage — share it.

**Two testers are coming.** They bring their ideas. The stack develops and executes them. This platform proves the model — not just for Rob, but for anyone who clones it. The testers are the first proof that this is replicable.

LinkedIn launch target: Phase 1 complete (Nerve UI + dashboard = visual proof).

---

## Lessons Learned

| Date | Lesson |
|---|---|
| 2026-03-29 | Unknown config keys crash the OpenClaw gateway. Research docs BEFORE any config change. |
| 2026-04-01 | OpenClaw workspace injection works — but old session history overrides it. Use `/reset` to start fresh when identity/context seems wrong. |
| 2026-04-01 | qwen3 has strong model identity training. IDENTITY.md + identity lock at top of AGENTS.md is required to override. |
| 2026-04-01 | Generic template files (SOUL.md, IDENTITY.md, AGENTS.md) ship with OpenClaw. All must be replaced with custom content before first use. |

---

*This file is the persistent memory layer. Update after every milestone. Never let it go stale.*