---
name: gap-analyzer
description: "MSP account gap analysis — finds which customer accounts are missing services from the catalog, ranks by revenue opportunity, flags HIPAA/legal/financial compliance risks. Use when user says: gap analysis, run gap, gap report, account gaps, upsell opportunities, missing services."
---

# Account Gap Analyzer
*MSP Account Intelligence*

## Execution Steps

**Step 1 — Load data**

Read both files. Check for customer-specific data first, fall back to sample:
- `data/customer/accounts.csv` (if exists) OR `data/msp_sample/accounts_sample.csv`
- `data/customer/service_catalog.csv` (if exists) OR `data/msp_sample/service_catalog.csv`

Use absolute paths: /home/rob-alvarado/.openclaw/workspace/data/customer/ or /home/rob-alvarado/.openclaw/workspace/data/msp_sample/

**Step 2 — Score each account**

For each account:
1. List services they have (Active_Services column, pipe-separated)
2. List recurring services from catalog they do NOT have (exclude $0 services: Structured Cabling, Hardware Procurement, Cybersecurity Assessment)
3. Gap value = sum of Monthly_Price for all missing recurring services
4. Note critical flags from Notes column

**Step 3 — Priority flags (mark CRITICAL)**

- Industry = Medical AND missing any Security service → HIPAA exposure
- Industry = Legal AND missing Cloud Backup → privilege risk
- Industry = Financial AND missing Managed Security → SEC/FINRA exposure
- Any account with zero security services

**Step 4 — Output to Telegram**

```
🔴 Gap Analysis — [date]
━━━━━━━━━━━━━━━━━━━━

TOP OPPORTUNITIES
─────────────────
#1 [Account Name] ([State] | [Industry])
   Gap: $[X,XXX]/mo
   Missing: [Service 1] · [Service 2]
   ⚠️ CRITICAL — [reason]

[#2 through #5]

─────────────────
Total accounts: [N] | Critical gaps: [N]
Top 5 value: $[X,XXX]/mo ($[XX,XXX]/yr)
Full pipeline: $[XX,XXX]/mo

Reply "full gap report" for all accounts.
Reply "gap by industry [X]" for filtered view.
```

**Step 5 — Full report** (if requested): all accounts, one line each, sorted by gap value desc.

**Step 6 — Industry filter** (if requested): filter by industry, same top-5 format.

## Data Notes
- Active_Services uses pipe | as separator
- Exclude $0 project services from gap value
- Sample data: data/msp_sample/ | Customer data: data/customer/
