# ROADMAP.md — The Build Sequence
*Last Updated: 2026-04-03 | Version: 1.3*

---

## Strategic Context

The RJA stack is built in layers. Infrastructure first, then intelligence, then automation, then compounding.

We do not skip layers. A fleet of agents with no reliable foundation is a liability. We build from the ground up, we build it right, and we let the edge compound.

Each phase delivers a stable platform that the next phase builds on. Each initiative — current or future — plugs into this foundation.

---

## Phase 0 — FOUNDATION
**Status: ✅ COMPLETE — 2026-04-01**

Goal: OpenClaw running with identity, memory, and Telegram comms confirmed.

| Task | Status | Notes |
|---|---|---|
| OpenClaw installed | ✅ DONE | 2026-03-29 |
| Telegram connected | ✅ DONE | 2026-03-29 |
| SOUL.md created | ✅ DONE | 2026-03-29 |
| MEMORY.md created | ✅ DONE | 2026-03-29 |
| LEARN.md created | ✅ DONE | 2026-03-29 |
| ROADMAP.md created | ✅ DONE | 2026-03-29 |
| Workspace context injection confirmed | ✅ DONE | 2026-04-01 — AGENTS.md, SOUL.md, IDENTITY.md auto-injected each session |
| MCP agent identity confirmed on Telegram | ✅ DONE | 2026-04-01 — Bot responds as MCP |

---

## Phase 1 — COCKPIT & VISIBILITY
**Status: ✅ COMPLETE — 2026-04-01**

Goal: Nerve installed and running. Full fleet visibility. Bot-Review dashboard live.

| Task | Status | Notes |
|---|---|---|
| Verify Node.js 22+ is installed | ✅ DONE | 2026-04-01 — v22.22.2 |
| Install Nerve via one-command installer | ✅ DONE | 2026-04-01 — v1.5.2 |
| Configure Nerve — LAN mode with auth | ✅ DONE | 2026-04-01 — :3080, scrypt auth |
| Verify Nerve connects to OpenClaw gateway | ✅ DONE | 2026-04-01 — Connected |
| Install OpenClaw Bot-Review dashboard | ✅ DONE | 2026-04-01 — http://192.168.0.165:3081 |
| Verify Bot-Review reads openclaw.json correctly | ✅ DONE | 2026-04-01 — Operational |
| Pi-4 watchdog deployed | ✅ DONE | 2026-04-01 — Upgraded to check actual service endpoints |
| LinkedIn launch + repo public | ✅ DONE | 2026-04-01 — v1.0.0 tagged |

---

## Phase 1.5 — PLATFORM HARDENING
**Status: IN PROGRESS — 2026-04-03**

Goal: Bot that actually works. Reliable model. Clean workspace. Onboarding that runs correctly.

Research source: [block/goose](https://github.com/block/goose) — reviewed 2026-04-03. Key design patterns identified and being integrated.

| Task | Status | Notes |
|---|---|---|
| Fix MCP identity (Qwen override) | ✅ DONE | 2026-04-01 — IDENTITY.md + AGENTS.md identity lock |
| Fix double Telegram response | ✅ DONE | 2026-04-02 — streaming: off |
| Fix model context (4096 truncation) | ✅ DONE | 2026-04-03 — mcp-qwen3 custom model, 8192 ctx |
| Fix workspace file bloat | ✅ DONE | 2026-04-03 — AGENTS.md trimmed from 2135 to 556 words |
| Fix false HEARTBEAT_OK responses | ✅ DONE | 2026-04-03 — Heartbeat section removed from AGENTS.md |
| Fix unauthorized file writes | ✅ DONE | 2026-04-03 — Explicit no-write rule added to AGENTS.md |
| Watchdog v2 — check actual endpoints | ✅ DONE | 2026-04-03 — Checks Ollama API + OpenClaw gateway port |
| Tester onboarding interview flow | 🔄 IN PROGRESS | First contact interview working for new users |
| Context compaction layer | ⬜ NEXT | Goose-inspired: auto-compress at 80% token capacity |
| Tool inspection layer | ⬜ | Goose-inspired: 5-stage inspect before tool execution |
| Per-tester isolated agents | ⬜ | Each tester gets own agent + USER.md via OpenClaw agents command |
| OpenClaw update to v2026.4.2 | ⬜ | Current: v2026.3.28 — update when stable window available |

---

## Phase 2 — RECIPE SYSTEM & SKILLS
**Status: QUEUED**

Goal: MCP can execute structured, repeatable workflows from Telegram commands. First base skills installed.

Research source: Goose recipe/workflow architecture — declarative YAML/JSON task definitions with parameter validation, extension injection, and Unicode injection protection.

| Task | Status | Notes |
|---|---|---|
| Define recipe schema for RJA stack | ⬜ | Adapt Goose-style declarative workflow definitions |
| Base skill: web fetch (HTTPS-only, sanitized output) | ⬜ | Security-first: sanitize, no redirect following to internal IPs |
| Base skill: system status report | ⬜ | Fleet health snapshot on demand |
| Base skill: web search | ⬜ | Already live via Brave — formalize as skill |
| Base skill: X/Twitter RSS reader | ⬜ | Read-only, no auth required |
| Recipe: daily digest | ⬜ | Fleet health + calendar + notable events → Telegram |
| Recipe: idea workshop | ⬜ | Structured brainstorm → output document |

---

## Phase 3 — HOME OFFICE NETWORK
**Status: QUEUED**

Goal: The RJA Home Office operates as a managed, intelligent network. IoT, compute, and networking all known and controlled by MCP.

| Task | Status | Notes |
|---|---|---|
| Network topology audit | ⬜ | Document all devices, IPs, roles |
| Device inventory | ⬜ | All IoT, compute, network gear |
| Define network zones | ⬜ | IoT VLAN, trusted VLAN, DMZ if needed |
| Select network management approach | ⬜ | Research: Unifi, OPNsense |
| Build RJA Home Office MCP Server | ⬜ | Exposes: IoT controls, network state, device health |
| Connect MCP server to OpenClaw agent | ⬜ | Agent queries and controls the home office |
| Automate network health reporting | ⬜ | Daily digest to Telegram |

---

## Phase 4 — INITIATIVE EXPANSION
**Status: FUTURE**

Goal: The RJA stack extends to support additional business initiatives. Each initiative gets its own domain, its own agents, its own MCP servers.

| Task | Status | Notes |
|---|---|---|
| Define first expansion initiative | ⬜ | Rob's call. The stack is ready when he is. |
| Scope domain-specific MCP server(s) | ⬜ | What data and tools does this initiative need? |
| Deploy initiative-specific agents | ⬜ | Dedicated agents with their own soul, memory, skills |
| Connect to Nerve fleet | ⬜ | All agents managed from one cockpit |

---

## The Compounding Principle

Each phase builds leverage for the next:

- Phase 0 gives us identity and comms.
- Phase 1 gives us visibility and control.
- Phase 1.5 gives us a platform that actually works.
- Phase 2 gives us repeatable workflows and skills.
- Phase 3 gives us a stable, intelligent home base.
- Phase 4 multiplies across any initiative Rob chooses to run.

The foundation is not overhead. The foundation is the advantage.

---

*Update task statuses after every milestone. The roadmap is the living plan.*
