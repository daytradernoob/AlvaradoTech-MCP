# LEARN.md — Research Protocols & Learning Framework
*Last Updated: 2026-04-03 | Version: 1.2*

---

## The Learning Imperative

The MCP does not hallucinate configurations. The MCP does not guess at API parameters. The MCP researches before it acts.

This is not timidity. This is precision. One wrong config key crashes the gateway. One bad decision in production costs real resources. We research because the edge is built on accuracy, not speed.

---

## Research Protocol — Tier 1: BEFORE CONFIG CHANGES

**Mandatory sources, in order:**

1. `docs.openclaw.ai` — Official OpenClaw documentation
2. `github.com/openclaw/openclaw` — Source of truth for config schema
3. Official SDK docs for any third-party integration

**Rule:** If a config key cannot be found in official docs, it does not go into the config. Period.

---

## Research Protocol — Tier 2: TECHNOLOGY ASSESSMENT

When evaluating new tools, repos, or approaches, assess against the RJA stack criteria:

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

The MCP is model-agnostic and tool-agnostic. Evaluate AI models across three axes:

**Best Performance** — Most accurate, reliable output for the specific task.
**Best Cost** — Cost per unit of value: tokens, API calls, licensing, infrastructure.
**Best User Experience** — Least friction. Fewest steps. Clearest output.

Document assessments here. Decisions are made on evidence, not defaults.

---

## Model Selection Log

| Date | Task Type | Models Compared | Winner | Rationale |
|---|---|---|---|---|
| 2026-04-03 | General assistant / Telegram bot | qwen3-4k (num_ctx 4096) vs qwen3:8b (num_ctx default 2048) vs mcp-qwen3 (num_ctx 8192) | **mcp-qwen3** | qwen3-4k and qwen3:8b both had context windows smaller than the system prompt (~6k tokens), causing truncation and garbage output. Custom Ollama model with 8192 ctx resolves this. |

---

## Learning Log

| Date | Topic | Source | Key Finding | Applied To |
|---|---|---|---|---|
| 2026-03-29 | OpenClaw Nerve | github.com/daggerhashimoto/openclaw-nerve | Real-time cockpit: voice, kanban, fleet control, per-agent soul/memory/workspace. One-command install. Requires Node.js 22+. Gateway must be running first. | ROADMAP.md Phase 1 |
| 2026-03-29 | OpenClaw Bot-Review | github.com/xmanrui/OpenClaw-bot-review | Lightweight Next.js dashboard. Reads ~/.openclaw/openclaw.json directly. No DB. Shows agents, models, sessions, token usage. | ROADMAP.md Phase 1 |
| 2026-03-29 | MCP Protocol | MCP_Explained docs | USB for AI tools. Client-Server. Three primitives: Tools (DO), Resources (READ), Prompts (SAY). Sandboxed, composable. | ROADMAP.md Phase 3+ |
| 2026-04-03 | Goose agent framework | github.com/block/goose | Production-grade AI agent platform by Block (Square). Key patterns: progressive context compaction (80% threshold), 5-stage tool inspection pipeline, recipe/workflow system, SubTask multi-agent dispatch, dual message visibility (agent sees compressed, user sees full). 34.7K stars, Apache 2.0. | ROADMAP.md Phase 1.5, 2 |

---

## Goose Design Patterns — Integration Priority

Research date: 2026-04-03. Source: [github.com/block/goose](https://github.com/block/goose)

| Pattern | Goose Implementation | RJA Priority | Status |
|---|---|---|---|
| **Context compaction** | Auto-compress at 80% token capacity. Agent sees compressed history, user sees full. Progressive filtering: tool responses first. | HIGH — model currently chokes on accumulated context | ⬜ Phase 1.5 |
| **Tool inspection pipeline** | 5 inspectors before any tool runs: Security, Egress, Adversary, Permission, Repetition | HIGH — prevents unauthorized writes, egress | ⬜ Phase 1.5 |
| **Recipe / workflow system** | Declarative YAML/JSON workflows with parameter validation, extension injection | HIGH — needed for repeatable Telegram commands | ⬜ Phase 2 |
| **SubTask execution** | Parent agent delegates to child agent with isolated session | MEDIUM — per-tester isolation, background tasks | ⬜ Phase 2 |
| **Background execution mode** | Async task execution separate from interactive chat session | MEDIUM — scheduled jobs, daily digests | ⬜ Phase 2 |
| **Multi-LLM provider abstraction** | Uniform interface across Ollama, Anthropic, OpenAI, etc. | LOW — single provider for now, design for future | ⬜ Phase 3+ |

---

## Skills Research Queue

| Skill/Tool | Source | Why Relevant | Priority |
|---|---|---|---|
| Context7 | github.com/upstash/context7 | Injects up-to-date library docs, prevents hallucinated APIs | HIGH |
| Task Master AI | github.com/eyaltoledano/claude-task-master | PRD → structured tasks → agent executes. Good for complex build phases. | MEDIUM |
| Tavily MCP | github.com/tavily-ai/tavily-mcp | AI-native search for agent research tasks | MEDIUM |
| Codebase Memory MCP | github.com/DeusData/codebase-memory-mcp | Codebase → persistent knowledge graph | LOW (future) |

---

## OpenClaw Config Schema — Known Valid Keys

**Research-verified. Update as confirmed.**

| Config Section | Known Keys | Source | Verified Date |
|---|---|---|---|
| channels.telegram | streaming: "off"\|"partial"\|"block"\|"progress"\|true\|false | openclaw gateway --help | 2026-04-02 |
| agents.defaults.model | primary: "provider/model-id" | openclaw.json schema | 2026-04-01 |
| gateway | port, mode, bind, auth, controlUi | docs.openclaw.ai | 2026-04-01 |
| tools | profile, allow, web.search, elevated | docs.openclaw.ai | 2026-04-01 |

**⚠️ CRITICAL:** Do not add keys from community posts, Reddit, or GitHub issues without cross-referencing the official schema.

---

## The Edge — Research Philosophy

We don't guess. We track. We calculate. We apply the known edge.

When we don't know something, we say we don't know it and we go find out. We don't fabricate confidence. We don't paper over gaps with plausible-sounding answers.

The integrity of the system depends on the integrity of its inputs. Research is how we maintain that integrity.

---

*This file governs how the MCP acquires and validates new knowledge. Update the Learning Log after every research session.*
