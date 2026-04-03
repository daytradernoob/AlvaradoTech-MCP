# BUSINESS.md — The Product Vision
*AlvaradoTech-MCP | Last Updated: 2026-04-03*

---

## The Product

**Idea Generating Platform to Execution Engine.**

Business owners have the ideas. They don't have the bandwidth, the analysis, or the systems to execute them at scale. This platform closes that gap — on their hardware, inside their building, with their data staying where it belongs.

Most AI tools are chat windows. This is an operating layer. It knows the business. It remembers every conversation. It executes tasks on approval. It identifies gaps the owner can't see because they're too close to the work. It connects tools and partners into a unified intelligence layer.

The business owner doesn't need to understand AI. They need outcomes.

---

## The Thesis

Businesses want AI. They fear the cloud.

That fear is not irrational:
- HIPAA. Patient data cannot leave the building.
- Attorney-client privilege. Case details cannot go to OpenAI.
- Compliance. Financial data cannot be in someone else's training set.
- Control. The $12K AWS bill that arrived without warning.
- Sovereignty. "We don't know what they do with our data."

The gap between "wants AI" and "can deploy and operate local AI" is enormous — and it is not closing on its own. The models get better. The fear gets bigger. Someone has to build the layer that bridges that gap.

That's this platform.

---

## The Parallel

**Nutanix did this for converged infrastructure.**

IT teams couldn't think in VMware + SAN terms. Nutanix built the layer that made both simple, unified, and manageable. Rob Alvarado was Nutanix SE of the Year 2019. He knows this playbook.

**AlvaradoTech-MCP does this for local AI.**

Business owners can't think in LLM + agent + inference terms. This platform makes it deployable, manageable, and productive for teams that aren't AI engineers.

---

## The Moat

Not everyone can build this. More importantly: **not everyone can think in these terms.**

The customer isn't buying hardware and software. They're buying:
1. The judgment of someone who already made the mistakes
2. A working system they don't have to understand
3. AI that stays inside their building
4. Ongoing support from someone who knows the stack

That knowledge is not easily replicated. It compounds with every deployment.

---

## Deployment Tracks

### Track A — On-Prem (Mac Mini M4 Pro)
**For:** Customers who want full data sovereignty. Medical, legal, financial, compliance-driven.

- Hardware: Mac Mini M4 Pro, 48GB unified memory — **$1,799**
- Inference: Local Ollama, 70B parameter models, no API cost
- Data: Never leaves the building
- Support: Rob installs, configures, maintains on monthly retainer
- Ongoing cost: Electricity + retainer

### Track B — VPS Cloud
**For:** Cloud-comfortable customers who want capability without hardware investment.

- Infrastructure: Hetzner CX32 VPS (~$20/month)
- Inference: Claude API (Anthropic Haiku/Sonnet) — ~$30-50/month usage
- Total: ~$50-70/month, well inside $100/month budget
- Setup: Same GitHub repo, one config switch: `anthropic/claude-haiku-4-5`
- Data: Processed by Claude API — appropriate for non-regulated businesses

Both tracks run the same codebase. Same SOUL.md, same AGENTS.md, same Telegram interface. The deployment config is the only difference.

---

## Target Markets — First Wave

### Medical Practices
- **Pain:** HIPAA. Patient notes, scheduling, follow-up. Can't use cloud AI.
- **Use case:** On-prem AI for front office, clinical notes, patient communication drafts.
- **Track:** A (on-prem required)

### Law Firms
- **Pain:** Attorney-client privilege. Case research, drafting, discovery.
- **Use case:** AI that reads case files and assists without data leaving the firm.
- **Track:** A (on-prem required)

### Financial Advisors / RIAs
- **Pain:** SEC/FINRA compliance. Client data, portfolio notes, meeting prep.
- **Use case:** Client relationship management, meeting summaries, compliance docs.
- **Track:** A or B depending on compliance requirements

### Technology Services Companies (MSPs, VARs)
- **Pain:** Too many customers, too few people. Cognitive overhead of managing diverse service portfolios.
- **Use case:** Business analysis, gap identification, proposal generation, partner solution mapping, account intelligence.
- **Track:** A or B
- **Reseller opportunity:** They embed MCP into their own customer offering → MRR

### SMBs with Data-Sensitive Operations
- **Pain:** Don't want operational data visible to competitors or vendors.
- **Use case:** Internal knowledge base, workflow automation, business analysis.
- **Track:** B (usually)

---

## First Customer: Leverage Technology Group (LTG)
*Scottsdale, AZ | ltgaz.com*

**Who they are:** Boutique technology services company. IT, security, AV, telecom, cabling. Founded 1999. 8-11 employees. 1,500+ customers. Arizona, California, Nevada, Texas.

**The tension:** Their differentiation — personalized, educated, customized service — doesn't scale at an 8-person / 1,500-customer ratio. Back office is the bottleneck: proposals, account review, gap analysis, documentation, partner solution mapping.

**What MCP does for them:**

| Problem | MCP Solution |
|---|---|
| "Are we using the right tools?" | Business analysis engine — ingests current toolset, identifies gaps, recommends changes |
| "Do we have gaps in our offerings?" | Scans 1,500 accounts against service catalog — surfaces upsell opportunities |
| Proposals take half a day | First draft in minutes. Human refines. |
| Client education is time-intensive | MCP generates client-specific education content |
| Partner solutions live in people's heads | MCP maps every partner offering and how they connect to maximize MRR |
| "Are we managing correctly?" | Department efficiency analysis — objective view the owner can't get from inside |

**The "3 to 30" math:** 3 back office people stop doing volume work (analysis, documentation, research, proposals). They do only judgment and relationship work. Effective output multiplies 3-5x. For 1,500 customers across 4 states, that's transformative.

**The reseller angle:** LTG serves 1,500 SMB customers. If LTG embeds MCP as part of their managed services offering — every client gets an AI operating layer. LTG manages it. LTG charges for it. Rob's first customer becomes Rob's first distribution channel.

This is the business model proof point. LTG is not just a customer. LTG is the case study that opens every door in the MSP/VAR market.

---

## What "Customer-Ready" Requires

| Gap | What It Takes |
|---|---|
| Reliable model output | Context compaction + tool inspection — Phase 1.5 |
| Install experience | Sub-30 min guided setup, VPS one-command deploy |
| Hardware recommendation | Mac Mini M4 Pro 48GB — validated, documented |
| VPS deployment | Docker-compose + .env.example + cloud config in GitHub |
| Customer brain templates | Vertical-specific SOUL.md, USER.md per industry |
| Demo script | 5 minutes. LTG use case. Clear before/after. |
| Support model | Monthly retainer. What's included. What escalates. |
| Pricing model | Hardware + install + monthly support (on-prem). Monthly VPS fee (cloud). |

---

## Immediate Next Steps

1. **LTG demo prep** — Build the specific use case: "Here's what MCP does for a technology services company with 1,500 customers and 8 staff." One conversation, one demo, first paying customer.

2. **VPS deployment** — Docker-compose + cloud config in GitHub. Enables Track B immediately. LTG might want cloud first to evaluate before committing to hardware.

3. **Platform reliability** — Context compaction + tool inspection. Can't demo a platform that writes ideas to HEARTBEAT.md.

4. **Hardware upgrade** — Mac Mini M4 Pro 48GB. Better demos, better output, becomes "the box" for Track A customers.

---

## The Business Model

**Version 1 — Managed Install (now)**
Rob installs + configures. Customer uses via Telegram. Monthly retainer for support and updates. Low scale, high margin, builds reference customers.

**Version 2 — Guided Self-Install (Phase 5)**
Documented, validated install process. Customer or their IT person runs it. Rob available for support. Hardware ships pre-configured or customer sources their own.

**Version 3 — Channel / Reseller (Phase 5+)**
Partners like LTG install for their customers. Rob trains the partner. Partner maintains the relationship. Revenue share. This is the Nutanix play at scale.

---

*This is not a side project. Update this file after every customer conversation and every architecture decision that has business implications.*
