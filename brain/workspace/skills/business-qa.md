# SKILL: Business Q&A Engine
*Version 1.0 | MSP Account Intelligence*

## Trigger
Any natural language question about accounts, services, revenue, coverage, or customers.

Examples:
- "how many accounts in California?"
- "which medical accounts have no security?"
- "what's our MRR by state?"
- "who's missing backup?"
- "what does Desert Sun Medical have?"
- "how many accounts have zero security?"
- "show me all Texas accounts"
- "what's our total pipeline?"
- "which accounts are HIPAA exposed?"
- "who are our top 5 by gap value?"

If unsure whether a question is meant for this skill vs the gap analyzer: use this skill for focused questions, gap-analyzer.md for full ranked reports.

---

## Data Sources

Always read fresh from file — do not rely on memory of previous reads.
Check for customer-specific data first, fall back to sample:
- `data/customer/accounts.csv` (if exists) OR `data/msp_sample/accounts_sample.csv`
- `data/customer/service_catalog.csv` (if exists) OR `data/msp_sample/service_catalog.csv`

---

## Question Categories + How to Answer

**COUNT queries** — "how many...?"
→ Filter the accounts list, count matches, state the number.
→ Format: "[N] accounts match. [1-sentence context if useful]"

**FILTER queries** — "which accounts...?" / "show me accounts that..."
→ Filter and list. Name, state, industry per line.
→ If more than 8 results, show first 8 and say "and [N] more — say 'all [filter]' for complete list."

**ACCOUNT LOOKUP** — "what does [account name] have?" / "show me [account]"
→ Find the account. List active services, gap value, notes.
→ Format:
```
[Account Name] ([State] | [Industry] | [N] employees)
Active: [service list]
Missing (recurring): [service list]
Gap value: $[X]/mo
Notes: [notes field]
```

**AGGREGATE queries** — "by state" / "by industry" / "total MRR"
→ Group, sum, sort descending.
→ Format as a compact table.

**REVENUE queries** — "what's our MRR?" / "total pipeline?"
→ Current MRR = sum of Monthly_Price × accounts that have each service.
→ Pipeline = sum of gap values across all accounts.
→ State both numbers and the ratio.

**GAP FILTER** — "who's missing [service]?" / "no backup" / "zero security"
→ Filter for accounts missing that specific service or category.
→ List with gap value. Flag CRITICAL accounts.

**COMPLIANCE/RISK queries** — "HIPAA exposed?" / "security risk?"
→ Medical accounts with no security layer = HIPAA critical.
→ Legal accounts with no backup = privilege risk.
→ Financial accounts with no security = SEC/FINRA risk.
→ List them. State the risk clearly.

---

## Response Rules

1. **Be direct.** Answer the question first, context second.
2. **Show the number.** Always include dollar amounts when relevant.
3. **Flag risk.** If a compliance risk is visible in the data, name it — even if not asked.
4. **Stay in the data.** Do not speculate beyond what the files contain.
5. **One follow-up.** After answering, offer one logical next question: "Want me to rank these by gap value?" or "Say 'full list' for all [N]."

---

## Format

Keep responses compact for Telegram. No headers unless listing more than 5 items.

For lists: use line breaks, not bullets. Telegram renders them cleanly.

For numbers: always format with commas. Monthly and annual both when relevant ($X,XXX/mo · $XX,XXX/yr).

---

## Error Handling

- Account name not found: "I don't have [name] in this dataset. Closest match: [suggest]. Say 'yes' to use that."
- Ambiguous question: ask one clarifying question, not multiple.
- Data file missing: report which file and stop.

---

*This skill makes MCP feel like it knows the business. That's the product.*
