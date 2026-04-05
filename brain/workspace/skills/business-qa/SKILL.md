---
name: business-qa
description: "Natural language Q&A against MSP account and service data. Use when user asks questions about their accounts, customers, services, revenue, coverage, or compliance — e.g. how many accounts in California, which medical accounts have no security, what is our MRR by state, who is missing backup, what does [account name] have, how many accounts have zero security."
---

# Business Q&A Engine
*MSP Account Intelligence*

## Data Sources

Always read fresh. Check customer data first, fall back to sample:
- `/home/rob-alvarado/.openclaw/workspace/data/customer/accounts.csv` OR `data/msp_sample/accounts_sample.csv`
- `/home/rob-alvarado/.openclaw/workspace/data/customer/service_catalog.csv` OR `data/msp_sample/service_catalog.csv`

## Question Types

**COUNT** — "how many...?"
→ Filter, count, state the number + 1-sentence context.

**FILTER** — "which accounts...?"
→ List matches: Name, State, Industry per line. Cap at 8, offer full list.

**ACCOUNT LOOKUP** — "what does [name] have?"
→ Active services, missing services, gap value, notes.

**AGGREGATE** — "by state / by industry / total MRR"
→ Group, sum, sort descending. Compact table.

**REVENUE** — "total MRR / total pipeline"
→ Current MRR = sum of (price × accounts with service). Pipeline = sum of all gap values.

**GAP FILTER** — "who's missing [service]?"
→ List accounts missing that service. Show gap value. Flag CRITICAL.

**COMPLIANCE** — "HIPAA exposed / security risk"
→ Medical + no security = HIPAA critical. Legal + no backup = privilege risk. Financial + no security = SEC/FINRA.

## Response Rules

1. Answer first, context second.
2. Always include dollar amounts when relevant.
3. Flag compliance risk even if not asked.
4. Stay in the data — do not speculate.
5. Offer one logical follow-up question.

## Format
Compact for Telegram. Line breaks not bullets. Numbers with commas. Monthly + annual when relevant.
