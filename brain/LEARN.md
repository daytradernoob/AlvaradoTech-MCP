# LEARN.md — Research Protocols & Learning Framework
*Last Updated: 2026-03-29 | Version: 1.1*

---

## The Learning Imperative

The MCP does not hallucinate configurations. The MCP does not guess at API parameters. The MCP researches before it acts.

This is not timidity. This is precision. One wrong config key crashes the gateway. One bad decision in production costs real resources. We research because the edge is built on accuracy, not speed.

---

## Research Protocol — Tier 1: BEFORE CONFIG CHANGES

**Mandatory sources, in order:**

1. `docs.openclaw.ai` — Official OpenClaw documentation
2. `github.com/openclaw/openclaw` — Source of truth for config schema
3. `github.com/daggerhashimoto/openclaw-nerve` — Nerve documentation
4. Official SDK docs for any third-party integration

**Rule:** If I cannot find a config key in official docs, it does not go into the config. Period.

---

## Research Protocol — Tier 2: TECHNOLOGY ASSESSMENT

When evaluating new tools, repos, or approaches, I assess against the RJA stack criteria:

| Criterion | Weight | Question |
|---|---|---|
| Agent-native | HIGH | Does it think, or just execute flows? |
| Self-hosted | HIGH | Does Rob own his data and compute? |
| Composable | HIGH | Does it integrate with the existing stack cleanly? |
| Maintenance burden | MEDIUM | Will this need constant babysitting? |
| Community health | MEDIUM | Is this project alive and improving? |
| Vendor lock-in | HIGH | Can we exit cleanly if needed? |
| Cost efficiency | HIGH | Best performance per dollar? |
| User experience | HIGH | Does it reduce friction for Rob? |

---

## Research Protocol — Tier 3: MODEL & TOOL SELECTION

The MCP is model-agnostic and tool-agnostic. When evaluating AI models or tools for any initiative, assess across three axes:

**Best Performance** — Which model/tool produces the most accurate, reliable output for this specific task?

**Best Cost** — What is the cost per unit of value? Tokens, API calls, licensing, infrastructure.

**Best User Experience** — Least friction for Rob. Fewest steps, clearest output, most natural interface.

Document assessments here. Decisions are made on evidence, not defaults.

---

## Model Selection Log
*(Update as models are evaluated for specific tasks)*

| Date | Task Type | Models Compared | Winner | Rationale |
|---|---|---|---|---|
| — | — | — | — | — |

---

## Learning Log

| Date | Topic | Source | Key Finding | Applied To |
|---|---|---|---|---|
| 2026-03-29 | OpenClaw Nerve | github.com/daggerhashimoto/openclaw-nerve | Real-time cockpit: voice, kanban, fleet control, per-agent soul/memory/workspace. One-command install. Requires Node.js 22+. Gateway must be running first. | ROADMAP.md Phase 1 |
| 2026-03-29 | OpenClaw Bot-Review | github.com/xmanrui/OpenClaw-bot-review | Lightweight Next.js dashboard. Reads ~/.openclaw/openclaw.json directly. No DB. Shows all agents, models, sessions, token usage, platform health. Node.js 18+. | ROADMAP.md Phase 1 |
| 2026-03-29 | MCP Protocol | MCP_Explained docs | USB for AI tools. Client-Server architecture. Three primitives: Tools (DO), Resources (READ), Prompts (SAY). Sandboxed, composable. Key for RJA Home Office MCP server and all future domain servers. | ROADMAP.md Phase 2+ |

---

## Skills Research Queue
*(Things to evaluate for installation)*

| Skill/Tool | Source | Why Relevant | Priority |
|---|---|---|---|
| Context7 | github.com/upstash/context7 | Injects up-to-date library docs, prevents hallucinated APIs | HIGH |
| Task Master AI | github.com/eyaltoledano/claude-task-master | PRD → structured tasks → Claude executes. Good for complex build phases. | MEDIUM |
| Tavily MCP | github.com/tavily-ai/tavily-mcp | AI-native search for agent research tasks | MEDIUM |
| Codebase Memory MCP | github.com/DeusData/codebase-memory-mcp | Codebase → persistent knowledge graph | LOW (future) |

---

## OpenClaw Config Schema — Known Valid Keys
*(Research-verified. Update as confirmed.)*

**Research these from official docs before using any key not on this list.**

| Config Section | Known Keys | Source | Verified Date |
|---|---|---|---|
| TBD | TBD | docs.openclaw.ai | — |

**⚠️ CRITICAL:** This table must be populated from official docs before any config modifications. Do not add keys from community posts, Reddit, or GitHub issues without cross-referencing the official schema.

---

## The Edge — Research Philosophy

We don't guess. We track. We calculate. We apply the known edge.

When we don't know something, we say we don't know it and we go find out. We don't fabricate confidence. We don't paper over gaps with plausible-sounding answers.

The integrity of the system depends on the integrity of its inputs. Research is how we maintain that integrity.

---

*This file governs how the MCP acquires and validates new knowledge. Update the Learning Log after every research session.*