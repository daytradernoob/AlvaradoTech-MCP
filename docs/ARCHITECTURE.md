# ARCHITECTURE.md — Platform Design Principles
*AlvaradoTech-MCP | Last Updated: 2026-04-03*

---

## The Mental Model: Air Traffic Control

MCP is the air traffic controller. It does not fly the planes — it directs them.

```
OPERATOR (Rob Alvarado)
    │
    ▼
MCP AGENT — Director. Holds the map. Knows what comes next.
    │
    ├── TELEGRAM — Radio. Commands in, reports out.
    ├── NERVE UI — Radar. Fleet visibility, agent control.
    ├── OPENCLAW — Execution engine. Plans, approvals, runs.
    │       ├── Agent sessions (one per context/user)
    │       ├── Skills (tools the agent can call)
    │       └── Workspace (.MD brain files, injected every session)
    ├── OLLAMA — Inference. Local GPU. No API cost.
    └── HARDWARE FLEET — The planes.
            ├── MSI-RTX (.146) — Inference
            ├── SEi-miniPC (.165) — Gateway
            └── Pi-4 (.204) — Watchdog
```

Technology is the extension of the operator. Every component exists to amplify Rob's capabilities — not replace his judgment.

---

## Design Principles

### 1. Local First
No cloud dependency for inference or execution. Data stays on hardware Rob owns. Running cost: electricity.

### 2. Brain in Files
The agent's identity, memory, and instructions live in version-controlled `.MD` files. Loadable into any session. Human-readable. Auditable. Not locked to any vendor's format.

```
brain/
├── SOUL.md       — Who the agent is
├── MEMORY.md     — What the agent knows
├── ROADMAP.md    — Where we're going
└── LEARN.md      — Research protocols
```

### 3. Approval Before Action
Nothing executes without human approval. The agent plans. The operator decides. This is not a limitation — it's the architecture. An agent that acts without approval is a liability.

### 4. Research Before Config
One wrong config key crashes the gateway. We read the docs first. We test on non-critical paths. We never add config keys from community posts without official source verification.

### 5. Lean Workspace
Local models have limited context windows. Every word in the workspace files competes for tokens with the actual conversation. Keep workspace files lean. Smaller is more reliable.

Current workspace budget target: < 800 words total across all injected files.

### 6. Compound the Edge
Small improvements, precision execution, compounded over time. Each phase builds leverage for the next. The foundation is not overhead — the foundation is the advantage.

---

## Goose-Inspired Design Patterns
*Source: [github.com/block/goose](https://github.com/block/goose) — reviewed 2026-04-03*

Goose is a production-grade agent framework by Block (Square). 34.7K stars. It has solved problems we are encountering. We adopt what helps without rebuilding what OpenClaw already does.

### Context Compaction
**Problem:** Long sessions accumulate context. Local models degrade or halt when context fills.
**Goose solution:** Monitor token usage. At 80% capacity, auto-compress: remove tool responses first, then progressively more history. Agent sees compressed context; user sees full history.
**RJA status:** Planned — Phase 1.5

### Tool Inspection Pipeline
**Problem:** Model tried to write ideas to HEARTBEAT.md instead of responding in chat.
**Goose solution:** 5-stage inspection before any tool executes: Security → Egress → Adversary → Permission → Repetition.
**RJA status:** Planned — Phase 1.5

### Recipe / Workflow System
**Problem:** Every task is ad hoc. Repeatable workflows require re-explaining.
**Goose solution:** Declarative YAML/JSON workflow definitions with parameters, extension injection, validation.
**RJA status:** Planned — Phase 2

### SubTask / Multi-Agent Dispatch
**Problem:** Single agent context for all users. No per-tester isolation.
**Goose solution:** Interactive, Background, and SubTask execution modes. Parent delegates to child agents with isolated sessions.
**RJA status:** Planned — Phase 2

---

## Stack Layers

| Layer | Component | What It Does |
|---|---|---|
| **L0 — Operator** | Rob Alvarado | Decision authority. Sets the pace. |
| **L1 — Strategy** | Claude (MCP) | Architecture, memory, planning. |
| **L2 — Execution** | OpenClaw | Runs the plan. Manages agents, sessions, tools. |
| **L3 — Interface** | Telegram | Commands in, reports out. |
| **L4 — Visibility** | Nerve UI + Bot-Review | Fleet control. Real-time cockpit. |
| **L5 — Inference** | Ollama + RTX 3060 | Local GPU inference. mcp-qwen3 model. |
| **L6 — Hardware** | MSI + SEi + Pi-4 | The machines that run it all. |

---

## What's Next

See `ROADMAP.md` for the live build sequence.

Current focus: Phase 1.5 — platform hardening. Context compaction, tool inspection, per-tester agent isolation.

Then: Phase 2 — recipe system, base skills, daily digest automation.

---

*This platform improves continuously through operation, research, and tester feedback. Every lesson learned gets committed.*
