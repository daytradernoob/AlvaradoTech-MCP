# ROADMAP.md — The Build Sequence
*Last Updated: 2026-04-04 | Version: 1.8*

---

## Strategic Context

**This is a product now, not just a personal platform.**

The RJA stack is built in layers. But we now know where those layers are going: a deployable, on-prem AI operating layer for businesses that want AI capability without cloud dependency or data exposure.

Every phase below builds toward that. Infrastructure first, then reliability, then skills, then product.

We do not skip layers. The foundation is the advantage.

---

## Phase 0 — FOUNDATION
**Status: ✅ COMPLETE — 2026-04-01**

| Task | Status | Notes |
|---|---|---|
| OpenClaw installed | ✅ DONE | 2026-03-29 |
| Telegram connected | ✅ DONE | 2026-03-29 |
| Brain files created | ✅ DONE | SOUL.md, MEMORY.md, LEARN.md, ROADMAP.md |
| Workspace context injection confirmed | ✅ DONE | 2026-04-01 |
| MCP identity confirmed on Telegram | ✅ DONE | 2026-04-01 |

---

## Phase 1 — COCKPIT & VISIBILITY
**Status: ✅ COMPLETE — 2026-04-01**

| Task | Status | Notes |
|---|---|---|
| Nerve UI installed + LAN auth | ✅ DONE | :3080, scrypt auth |
| Bot-Review dashboard | ✅ DONE | :3081 |
| Pi-4 watchdog v2 | ✅ DONE | Checks actual endpoints, not just ping |
| LinkedIn launch + repo public | ✅ DONE | v1.0.0 tagged |

---

## Phase 1.5 — PLATFORM HARDENING
**Status: 🔄 IN PROGRESS — 2026-04-03**

Goal: Reliable enough to demo to a customer. Consistent behavior. No garbage output.

| Task | Status | Notes |
|---|---|---|
| Fix MCP identity (Qwen override) | ✅ DONE | 2026-04-01 |
| Fix double Telegram response | ✅ DONE | streaming: off |
| Fix model context truncation | ✅ DONE | mcp-qwen3, 8192 ctx |
| Trim workspace files | ✅ DONE | 556 words total |
| Fix HEARTBEAT_OK false positives | ✅ DONE | Heartbeat removed from AGENTS.md |
| Fix unauthorized file writes | ✅ DONE | Explicit no-write rule in AGENTS.md |
| Watchdog v2 | ✅ DONE | Endpoint checks |
| Context compaction layer | ✅ DONE | SESSION.md working memory — injected every session, updated at milestones |
| Tool inspection layer | ✅ DONE | 5-stage check in AGENTS.md before every tool call |
| OpenClaw update to v2026.4.2 | ✅ DONE | 2026-04-04. Breaking changes: BOOTSTRAP.md required, skill format changed, model whitelist enforced |
| 91/9 public/private data split | ✅ DONE | 2026-04-04. Engine public, customer data stays local. gitignore enforced. |
| Pre-computed gap analysis pattern | ✅ DONE | 2026-04-04. Python script → gap_analysis_result.md. Solves 8k context budget on small models. |
| Hardware ceiling identified | ✅ DONE | 2026-04-04. RTX 3060 = 8b model max. 14b partial VRAM offload. Mac Mini M4 Pro is production engine. |
| Per-tester isolated agents | ⬜ | OpenClaw multi-agent for tester onboarding |
| Hardware upgrade | ⬜ | Mac Mini M4 Pro 48GB — $1,799. Unblocks 32b model, dynamic Q&A, real instruction following. |

---

## Phase 2 — SKILLS & RECIPES
**Status: 🔄 IN PROGRESS — 2026-04-04**

Goal: MCP executes structured, repeatable workflows. First real skills installed. Platform demonstrates value to a non-technical observer.

| Task | Status | Notes |
|---|---|---|
| Account Gap Analyzer skill | ✅ DONE | Pre-computed pattern. Python script → gap_analysis_result.md → Telegram. Works on 8b/14b. |
| Business Q&A Engine skill | 🔄 PARTIAL | Skill registered. Short Q&A works on 14b. Dynamic multi-account queries need Mac Mini (32b). |
| LTG demo script | ✅ DONE | 10-min, 6-beat script. Local: docs/customers/ltg/ |
| Computech/Padragm brief | ✅ DONE | Founder-level pitch prep. Local: docs/prospects/ |
| Hardware scout skill | ⬜ | eBay + Craigslist + r/hardwareswap search |
| Base skill: system status report | ⬜ | Fleet health snapshot on demand |
| Base skill: web fetch (sanitized) | ⬜ | HTTPS-only, no internal IP redirects |
| Recipe: daily digest | ⬜ | Fleet health + notable events → Telegram |
| Recipe: idea workshop | ⬜ | Structured brainstorm → output doc |

---

## Phase 3 — CUSTOMER PRODUCT V1
**Status: 🔄 IN PROGRESS — 2026-04-03**

Goal: One paying customer on a managed install. Build the install experience and demo. Validate the business thesis with real money.

| Task | Status | Notes |
|---|---|---|
| Validated hardware SKU finalized | ✅ DONE | Mac Mini M4 Pro 48GB — $1,799. Documented. |
| Install guide: customer-facing | ✅ DONE | docs/INSTALL_PLAYBOOK.md — sub-30 min, no JSON editing |
| On-prem setup script | ✅ DONE | deploy/onprem-setup.sh — one command, Track A |
| Demo script | ✅ DONE | Local: ~/.openclaw/workspace/docs/customers/ltg/ |
| Brain file templates per vertical | ⬜ | Medical, legal, financial, SMB |
| First customer conversation | ⬜ | LTG LinkedIn connect sent. Computech pending. |
| First managed install | ⬜ | Rob installs + configures. Customer uses. |
| Support model defined | ⬜ | Monthly retainer. What's included. |
| Pricing model v1 | ⬜ | Hardware + install + monthly support |
| VPS validation | ⬜ | Spin up Hetzner CX32, Docker + OpenRouter. Track B delivery path. |
| Docker deployment (Track B) | ⬜ | docker-compose for multi-tenant VPS. One container per customer. |
| Pricing model v1 | ⬜ | On-Prem: hardware + install + retainer. Cloud: S/M/L monthly subscription. |
| Support model defined | ⬜ | What monthly retainer covers. SLA. Escalation path. |

---

## Phase 4 — HOME OFFICE NETWORK
**Status: QUEUED**

Goal: RJA home office as the reference architecture. What we run ourselves is what we sell.

| Task | Status | Notes |
|---|---|---|
| Network topology audit | ⬜ | Document all devices, IPs, roles |
| Device inventory | ⬜ | IoT, compute, network gear |
| Build RJA Home Office MCP Server | ⬜ | IoT controls, network state, device health |
| Connect to OpenClaw agent | ⬜ | Agent can query and control the home office |
| Automate network health reporting | ⬜ | Daily digest to Telegram |

---

## Phase 5 — PLATFORM SCALE
**Status: FUTURE**

Goal: Guided self-install. Vertical-specific configurations. The Nutanix play.

| Task | Status | Notes |
|---|---|---|
| Installer script | ⬜ | Non-technical IT person can run it |
| Vertical configs: Medical | ⬜ | HIPAA-aligned brain files, use case templates |
| Vertical configs: Legal | ⬜ | Privilege-aware defaults |
| Vertical configs: Financial | ⬜ | Compliance-aligned defaults |
| Partner / reseller model | ⬜ | Others install, Rob supports |
| Public case studies | ⬜ | Reference customers, documented outcomes |

---

## The Compounding Principle

- Phase 0-1: Identity and visibility.
- Phase 1.5: A platform that works.
- Phase 2: A platform that does useful things.
- Phase 3: A platform someone pays for.
- Phase 4: A reference architecture we live in.
- Phase 5: A platform anyone can deploy.

The foundation is not overhead. The foundation is the advantage.

---

*Update task statuses after every milestone. The roadmap is the living plan.*
