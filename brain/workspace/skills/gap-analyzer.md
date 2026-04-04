# SKILL: Account Gap Analyzer
*Version 1.0 | MSP Account Intelligence*

## Trigger
User says any of: "gap analysis", "run gap", "gap report", "account gaps"

---

## What This Skill Does

Reads LTG's account list and service catalog. Cross-references to find which accounts are missing high-value services. Outputs prioritized upsell opportunities ranked by monthly revenue potential.

---

## Execution Steps

**Step 1 — Load data**

Read both files. Check for customer-specific data first, fall back to sample:
- `data/customer/accounts.csv` (if exists) OR `data/msp_sample/accounts_sample.csv`
- `data/customer/service_catalog.csv` (if exists) OR `data/msp_sample/service_catalog.csv`

If no data files found, report: "Gap Analyzer: no data files found. Expected: data/customer/accounts.csv or data/msp_sample/accounts_sample.csv"

**Step 2 — Score each account**

For each account:
1. List services they currently have (from Active_Services column, pipe-separated)
2. List recurring services from catalog they do NOT have (exclude $0 project-based services: Structured Cabling, Hardware Procurement, Cybersecurity Assessment)
3. Calculate gap value = sum of Monthly_Price for all missing recurring services
4. Note any critical flags from the Notes column

**Step 3 — Apply priority multipliers**

Bump priority (mark as CRITICAL) if:
- Industry = Medical AND missing any Security service → HIPAA exposure
- Industry = Legal AND missing Cloud Backup → privilege/data risk
- Industry = Financial AND missing Managed Security → SEC/FINRA exposure
- Any account with 0 security services (no Endpoint, no SOC, no Email Security)

**Step 4 — Build the report**

Output this exact format to Telegram:

```
🔴 LTG Gap Analysis — [date]
━━━━━━━━━━━━━━━━━━━━

TOP OPPORTUNITIES
─────────────────
[Rank 1-5 by gap value, CRITICAL accounts first]

#1 [Account Name] ([State] | [Industry])
   Gap: $[monthly value]/mo
   Missing: [Service 1] · [Service 2] · [Service 3]
   ⚠️ [CRITICAL flag reason if applicable]

#2 ...
[continue through top 5]

─────────────────
SUMMARY
Total accounts analyzed: [N]
Accounts with critical gaps: [N]
Top 5 pipeline value: $[X,XXX]/mo ($[X,XXX×12]/yr)
Full pipeline (all accounts): $[X,XXX]/mo

Reply 'full gap report' for all 20 accounts.
Reply 'gap by industry [industry]' for filtered view.
```

**Step 5 — Full report (if requested)**

If user says "full gap report": output all accounts sorted by gap value descending, same format but condensed (one line per account: Name | Gap $/mo | Top missing service).

**Step 6 — Industry filter (if requested)**

If user says "gap by industry [X]": filter accounts by that industry, same top-5 format.

---

## Data Notes

- Active_Services uses pipe `|` as separator
- $0 services (cabling, hardware, assessments) are opportunities to note but excluded from gap value calculation
- Compliance services (HIPAA, SOC2) are included in gap value only if industry matches
- Sample data is in data/msp_sample/. Real customer data goes in data/customer/ (local only, not in repo).

---

## Error Handling

- If CSV format differs from expected: report the discrepancy and ask user to confirm file format
- Do NOT guess or fabricate account data
- If calculation is uncertain: show your work, ask user to verify

---

*This skill is the demo anchor. Execute it clean every time.*
