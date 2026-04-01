# ROADMAP.md — The Build Sequence
*Last Updated: 2026-04-01 | Version: 1.2*

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
| SYSTEM.md created | ✅ DONE | 2026-03-29 |
| INSTRUCTIONS.md created | ✅ DONE | 2026-03-29 |
| Workspace context injection confirmed | ✅ DONE | 2026-04-01 — AGENTS.md, SOUL.md, IDENTITY.md auto-injected each session |
| MCP agent identity confirmed on Telegram | ✅ DONE | 2026-04-01 — Bot responds as MCP |

---

## Phase 1 — COCKPIT & VISIBILITY
**Status: IN PROGRESS — 2026-04-01**

Goal: Nerve installed and running. Full fleet visibility. Bot-Review dashboard live.

| Task | Status | Notes |
|---|---|---|
| Verify Node.js 22+ is installed | ✅ DONE | 2026-04-01 — v22.22.2 |
| Install Nerve via one-command installer | ✅ DONE | 2026-04-01 — v1.5.2 |
| Configure Nerve — Local mode (localhost) | ✅ DONE | 2026-04-01 — :3080, auth enabled |
| Verify Nerve connects to OpenClaw gateway | ✅ DONE | 2026-04-01 — Connected |
| Set MCP agent soul in Nerve UI | ⬜ NEXT | Load SOUL.md content into agent soul field |
| Set MCP agent memory in Nerve UI | ⬜ | Load MEMORY.md content into agent memory |
| Install OpenClaw Bot-Review dashboard | ✅ DONE | 2026-04-01 — http://192.168.0.165:3081 |
| Verify Bot-Review reads openclaw.json correctly | ✅ DONE | 2026-04-01 — Operational |
| Pi-4 watchdog deployed | ✅ DONE | 2026-04-01 — pings MSI + SEi every 5 min, Telegram alert on failure |
| Configure first Nerve kanban workflow | ⬜ | Phase 2 home office tasks |

---

## Phase 2 — RJA HOME OFFICE NETWORK
**Status: QUEUED**

Goal: The RJA Home Office operates as a managed, intelligent network. IoT, compute, and networking are all known and controlled by the MCP.

| Task | Status | Notes |
|---|---|---|
| Network topology audit | ⬜ | Document all devices, IPs, roles |
| Device inventory | ⬜ | All IoT, compute, network gear |
| Define network zones | ⬜ | IoT VLAN, trusted VLAN, DMZ if needed |
| Select network management approach | ⬜ | Research options: Unifi, OPNsense, etc. |
| Build RJA Home Office MCP Server | ⬜ | Exposes: IoT controls, network state, device health |
| Connect MCP server to OpenClaw agent | ⬜ | Agent can query and control the home office |
| Automate network health reporting | ⬜ | Daily digest to Telegram |
| Define initial IoT automation rules | ⬜ | First automations from inventory findings |

---

## Phase 3 — INITIATIVE EXPANSION
**Status: FUTURE**

Goal: The RJA stack extends to support additional business initiatives and domains. Each initiative gets its own domain, its own agents, its own MCP servers, and its own compounding edge.

The foundation built in Phases 0-2 makes every future initiative faster, cheaper, and more capable than building standalone.

| Task | Status | Notes |
|---|---|---|
| Define first expansion initiative | ⬜ | Rob's call. The stack is ready when he is. |
| Scope domain-specific MCP server(s) | ⬜ | What data and tools does this initiative need? |
| Deploy initiative-specific agents | ⬜ | Each initiative gets dedicated agents with their own soul, memory, skills |
| Connect to Nerve fleet | ⬜ | All agents managed from one cockpit |

---

## The Compounding Principle

Each phase builds leverage for the next:

- Phase 0 gives us identity and comms.
- Phase 1 gives us visibility and control.
- Phase 2 gives us a stable, intelligent home base.
- Phase 3 multiplies across any initiative Rob chooses to run.

The foundation is not overhead. The foundation is the advantage.

---

*Update task statuses after every milestone. The roadmap is the living plan.*