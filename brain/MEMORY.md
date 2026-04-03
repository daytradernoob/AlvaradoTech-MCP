# MEMORY.md — Persistent Knowledge Base
*Last Updated: 2026-04-03 | Version: 1.3*

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
- **Status:** OPERATIONAL
- **Version:** v2026.3.28 (update to v2026.4.2 pending)
- **Telegram:** CONNECTED + VERIFIED — Bot responds as MCP
- **MCP Identity:** CONFIRMED — IDENTITY.md + SOUL.md + AGENTS.md injected each session
- **Model:** mcp-qwen3 (custom Ollama model — qwen3:8b base, num_ctx 8192)
- **Gateway Port:** 18789
- **Config Path:** `~/.openclaw/openclaw.json`
- **Gateway Host:** SEi-miniPC (192.168.0.165)
- **Inference Host:** MSI-RTX (192.168.0.146) — Ollama + RTX 3060

### Nerve UI
- **Status:** OPERATIONAL — http://192.168.0.165:3080
- **Auth:** scrypt password hash, NERVE_AUTH=true
- **Version:** v1.5.2

### Bot-Review Dashboard
- **Status:** OPERATIONAL — http://192.168.0.165:3081

### Pi-4 Watchdog
- **Status:** OPERATIONAL — cron every 5 min
- **v2 upgrade:** Checks Ollama API (:11434) and OpenClaw gateway (:18789) — not just ping

### Fleet
| Host | IP | SSH User | Role |
|---|---|---|---|
| MSI-RTX | 192.168.0.146 | rob-alvarado | Ollama inference, RTX 3060 |
| SEi-miniPC | 192.168.0.165 | rob-alvarado | OpenClaw gateway, Nerve, Bot-Review |
| Pi-4 | 192.168.0.204 | robalvarado | Watchdog (note: no hyphen in username) |
| HP-1030-G2 | 192.168.0.207 | rob-alvarado | Claude Code sessions |

---

## Key Decisions Made

| Date | Decision | Rationale |
|---|---|---|
| 2026-03-29 | OpenClaw selected as execution engine | Multi-agent, persistent, Telegram-native, Nerve cockpit |
| 2026-03-29 | Nerve selected as UI layer | Voice, kanban, fleet control, per-agent soul/memory/workspace |
| 2026-03-29 | MCP brain externalized to .MD files | Persistent, versionable, loadable into any session |
| 2026-04-01 | LinkedIn launched + repo public | v1.0.0 tagged. Two testers incoming. |
| 2026-04-02 | Telegram streaming set to off | Prevented double-response from partial message replays |
| 2026-04-03 | mcp-qwen3 as primary model | Custom Ollama model: qwen3:8b base + num_ctx 8192. Fixes context truncation that caused garbage output. |
| 2026-04-03 | Goose design patterns adopted as roadmap | Progressive context compaction, tool inspection, recipe system, SubTask dispatch — integrated into Phase 1.5 and Phase 2 planning |

---

## Architecture Decisions

### ATC Mental Model
MCP is an air traffic controller. It does not fly the planes — it directs them. Agents are planes. Nerve is the radar. Telegram is the radio. The operator is the decision authority.

Every tool, every skill, every agent is here to extend the operator's capabilities — not replace them. Technology is the extension of the person.

### Why .MD Files as Brain
- Loadable into any Claude session instantly
- Human-readable, versionable, auditable
- Not locked into any vendor's memory format
- Rob can read and edit directly. The brain is transparent.

### Why MCP Protocol Matters
- MCP = USB for AI tools. Write a server once, any compatible AI uses it.
- Standardized, discoverable, sandboxed, composable.
- Future: RJA Home Office MCP server exposes IoT controls, network state, device health.

### Goose-Inspired Architecture Principles (adopted 2026-04-03)
- **Context compaction**: Compress conversation history at 80% token capacity. Agent sees compressed context; user sees full history. Prevents model degradation on long sessions.
- **Tool inspection**: Multi-stage validation before any tool executes. Prevents unauthorized writes, egress, and adversarial inputs.
- **Recipe system**: Declarative workflow definitions. Repeatable tasks become commands.
- **SubTask dispatch**: Parent agent delegates to child agents with isolated sessions. Enables per-tester isolation and background execution.

---

## Public Mission

This repo is the homework. The goal: publish a base MCP model on GitHub that anyone can clone and use to run their own AI operating layer. Local inference. No cloud dependency. Self-hosted. The foundation is the advantage — share it.

We improve this platform continuously through hands-on operation, external research (Goose, context7, task-master-ai, etc.), and direct tester feedback. Every lesson learned gets committed.

---

## Lessons Learned

| Date | Lesson |
|---|---|
| 2026-03-29 | Unknown config keys crash the OpenClaw gateway. Research docs BEFORE any config change. |
| 2026-04-01 | OpenClaw workspace injection works — but old session history overrides it. Use `/reset` to start fresh. |
| 2026-04-01 | qwen3 has strong model identity training. IDENTITY.md + identity lock at top of AGENTS.md is required to override. |
| 2026-04-01 | Generic template files (SOUL.md, IDENTITY.md, AGENTS.md) ship with OpenClaw. All must be replaced with custom content before first use. |
| 2026-04-02 | Telegram streaming: "partial" causes double-response on provider restart. Set to "off". |
| 2026-04-02 | Poisoned session history propagates even after sessions.json is cleared — the .jsonl files persist. Delete both to truly reset. |
| 2026-04-03 | qwen3-4k had num_ctx 4096 and qwen3:8b defaulted to 2048. System prompt alone was 6k tokens. Context truncation caused garbage output ("I am MCP." only), random HEARTBEAT_OK responses, and unauthorized file writes. Always verify num_ctx against actual system prompt size. |
| 2026-04-03 | AGENTS.md bloat (2135 words) confused local models. Trimmed to 556 words. Keep workspace files lean — smaller is more reliable for local inference. |
| 2026-04-03 | OpenClaw injects a hardcoded session-start message: "greet the user… ask what they want to do." Workspace files must account for this specific prompt to override greeting behavior. |

---

*This file is the persistent memory layer. Update after every milestone. Never let it go stale.*
