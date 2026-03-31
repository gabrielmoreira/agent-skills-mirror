---
name: investor-audits
description: "Handle investor audit confirmations and quarterly portfolio reporting requests. Use when: (1) Email from auditor (PwC, KPMG, EY, CBIZ, Deloitte) requesting confirmation, (2) Investor asks for quarterly reporting (revenue, runway, cap table), (3) User asks to 'help with audits' or 'process audit requests', (4) Email contains 'audit confirmation' or 'investment confirmation'. Maps requests to standard company data and drafts accurate responses."
---

# Investor Audit & Portfolio Reporting

Efficiently respond to investor auditors and quarterly reporting requests using standardized company data.

## Philosophy

**Accuracy over speed.** Auditors need precise numbers as of specific dates. Wrong data creates more work than delayed data.

**NEVER make up information.** If data is not in the reference files, DO NOT guess or fabricate. Flag as missing and ask user to provide source.

**Standard data, custom responses.** 95% of requests ask for the same underlying info in different formats. Maintain clean reference data, adapt presentation per request.

**Quarterly snapshots.** Auditors want point-in-time data (usually quarter-end), not live data. Local snapshots are actually better than API integrations for this use case.

## Mandatory Verification

**Before drafting ANY response, use a subagent to verify:**

1. **Investor name matches exactly** - Check cap table for exact legal entity name
2. **Share class is correct** - Verify which series (Seed, A-1, A-2, A-3) they actually hold
3. **Numbers pulled from source** - Every number must trace to cap-table or financials file
4. **Cross-check totals** - shares × price = cost basis, percentages add up

```
⚠️ VERIFICATION CHECKLIST (run via subagent)

□ Investor legal name matches cap table exactly
□ Share class stated in request matches their actual holdings
□ All numbers copied from reference files (not calculated/estimated)
□ If request mentions amounts, verify against our records
□ Flag ANY discrepancies to user before drafting response
```

If the investor states something that doesn't match our records (e.g., "our Series A-3 position" when they have A-2), **flag this discrepancy** - do not assume they're right or silently use their version.

## Reference Data Structure

Skill-specific reference data lives in the skill's `references/` directory:

```
references/
├── company-info.md                    # Legal names, addresses, EIN, formation, banking
├── cap-table-YYYY-MM-DD.xlsx          # Cap table export (SOURCE OF TRUTH)
├── cap-table-YYYY-MM-DD.csv           # CSV export for quick lookups
├── cap-table-YYYY-QX.md               # Pricing reference + column mapping only
├── entity-mappings.md                 # Common name → legal entity mappings
├── financials-YYYY-QX.md              # Summarized financials from bookkeeper
├── certificate-of-incorporation.pdf   # Certificate of Incorporation
├── insurance.md                       # D&O limits, coverage details
├── d-and-o-binder-YYYY.pdf            # Actual policy document
└── response-templates.md              # Standard response language
```

Shared financial data (used by multiple skills) lives in a shared data directory (`[YOUR_DATA_PATH]`):

```
data/
├── financials-YYYY-MM-DD.xlsx   # Raw bookkeeper financials (SOURCE OF TRUTH)
├── runway-model.xlsx            # Runway model
```

### External Data Sources

- **EIN**: From `references/company-info.md`
- **Cap Table**: Your cap table provider (Carta, Pulley, etc.) → export quarterly
- **Financials**: Your bookkeeper → monthly Excel files
- **Certificate of Incorporation**: Stored locally, update when amended

**CRITICAL: Use source files (Excel/CSV/PDF) directly. NEVER manually transcribe data into markdown.**

**Note:** Pending requests are tracked via the `audits` Gmail label - emails ARE the tracker.

## Company Context

Fill this in for your company. Used to sign responses and verify company identity in audit requests.

| Field          | Value                      |
| -------------- | -------------------------- |
| **Legal name** | [YOUR_LEGAL_COMPANY_NAME]  |
| **DBA**        | [YOUR_DBA_IF_APPLICABLE]   |
| **State**      | Delaware (or your state)   |
| **EIN**        | [from company-info.md]     |
| **Address**    | [from company-info.md]     |
| **Accounting** | [YOUR_BOOKKEEPER]          |
| **Cap table**  | [Carta / Pulley / etc.]    |

## Workflow

### 1. Parse the Request

When an audit/reporting request comes in, identify:

| Field               | Extract                                                      |
| ------------------- | ------------------------------------------------------------ |
| **Requester**       | Audit firm + contact (e.g., "KPMG - [Name]")                 |
| **On behalf of**    | Which investor fund                                          |
| **As-of date**      | What date they want data for (usually Dec 31 or quarter-end) |
| **Deadline**        | When response is due                                         |
| **Items requested** | List of specific data points                                 |

### 2. Map to Standard Data

Most requests ask for combinations of:

| Request Language                                           | Maps To                                               |
| ---------------------------------------------------------- | ----------------------------------------------------- |
| "Cap table", "ownership %", "shares held"                  | `cap-table-YYYY-QX.md`                                |
| "Investment confirmation", "cost basis", "amount invested" | `cap-table-YYYY-QX.md` (includes cost basis column)   |
| "Financials", "balance sheet", "P&L"                       | `financials-YYYY-QX.md` or bookkeeper export          |
| "Loans", "convertibles", "SAFEs"                           | `cap-table-YYYY-QX.md` (section for debt instruments) |
| "D&O insurance", "liability limits"                        | `insurance.md`                                        |
| "Runway", "cash position"                                  | `financials-YYYY-QX.md`                               |

### 3. Check Data Freshness

Before drafting response, verify:

```
⚠️ DATA FRESHNESS CHECK

Cap table:     Q4 2025 (as of Dec 31, 2025) ✓ Current
Financials:    Nov 2025 ⚠️ Dec not yet closed
Insurance:     2025 policy ✓ Current
Positions:     Last updated Jan 15, 2026 ✓ Current
```

Flag if:

- Requested as-of date is after our latest snapshot
- Data is >45 days old for quarterly requests
- Any referenced file is missing

### 4. Draft Response

Generate response email with:

1. **Greeting** - Professional, reference their request
2. **Data section** - Precise answers to each question
3. **Attachments note** - What docs are attached (cap table, financials)
4. **Contact info** - For follow-up questions

### 5. Track Request

Requests are tracked via the `audits` Gmail label. The emails themselves are the tracker - no separate tracking file needed.

## Common Request Types

### Type A: Share/Investment Confirmation

Auditors verifying their client's investment position.

**They need:**

- Number of shares held by investor
- Share class and price per share
- Total cost basis (amount invested)
- Ownership % (diluted and undiluted)
- Any loans/convertibles held

**Response template:**

```
Dear [Auditor],

We confirm the following investment position for [Investor Fund] in
[YOUR_LEGAL_COMPANY_NAME] as of [date]:

Shares: [X] Series [Y] Preferred Stock
Price per share: $[X.XX]
Total investment: $[X,XXX,XXX]
Ownership: [X.XX]% undiluted / [X.XX]% fully diluted

[Investor Fund] holds no loans, convertible notes, or other instruments.

Please find attached our cap table as of [date].

Best regards,
[YOUR_NAME]
[YOUR_TITLE], [YOUR_COMPANY]
```

### Type B: Full Audit Confirmation

Comprehensive request covering multiple data points.

**They need:**

- All of Type A, plus:
- Top 3 shareholders
- Total shares outstanding
- Loans/debt from all sources
- Latest financials
- D&O insurance limits
- Dividend history (usually none)
- Future funding commitments

**Response approach:**

1. Answer each question with specific data
2. Attach: cap table, latest financials, D&O certificate
3. Note what's not applicable (e.g., "No dividends declared")

### Type C: Quarterly Portfolio Reporting

Investor fund's internal reporting, not external audit.

**They need:**

- Quarterly revenue
- Operating cash flow
- Cash/runway position
- Headcount (FTEs)
- Cap table
- Key metrics

**Response approach:**

- More narrative acceptable
- Can provide preliminary numbers
- Usually less formal than audit confirmation

## Data Sources

### Cap Table → Cap Table Provider

- Export quarterly from Carta, Pulley, or your provider
- Save snapshot as `cap-table-YYYY-QX.md`
- Include: all shareholders, share counts, ownership %, share classes

### Financials → Bookkeeper

- Monthly financials from your bookkeeper
- Key accounts: Cash, Revenue, Expenses
- For runway: Cash balance ÷ monthly burn

### D&O Insurance → Policy docs

- Annual limits (per claim + aggregate)
- Policy period
- Carrier name

### Cost Basis → Cap table

- Include cost basis column when exporting cap table
- Each investor's total investment = shares × price per share

## Handling Missing Data

If data is missing or stale:

```
⚠️ MISSING DATA

Cannot complete response - need:
□ Q4 2025 cap table (export from cap table provider)
□ Dec 2025 financials (request from bookkeeper)

Suggested action:
1. Export cap table from your provider
2. Email bookkeeper requesting month-end close
```

## Bulk Processing

When multiple requests pending (in `audits` label):

1. **Count requests** - Record total emails with `audits` label
2. **Sort by deadline** - Overdue first
3. **Group by data needed** - Requests needing same data
4. **Process in batch** - Draft all, then send all
5. **Verify all processed** - Confirm count drafted = count fetched. If mismatch, investigate before completing.
6. **Archive when complete** - Remove from `audits` label when done

Output must include: `Fetched: X requests | Processed: X requests | Verified: ✓`

## Quality Checklist

Before sending any response:

- [ ] Numbers match source docs (cap table, financials)
- [ ] As-of date matches what they requested
- [ ] All their questions answered
- [ ] Correct investor/fund name used
- [ ] Attachments referenced are actually attached
- [ ] Contact info included for follow-up
