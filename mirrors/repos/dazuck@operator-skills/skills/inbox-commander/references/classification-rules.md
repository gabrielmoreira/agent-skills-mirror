# Classification Rules

Detailed patterns for email classification.

**IMPORTANT**: Before applying these rules, load `learned-rules.md` and apply any overrides first. Learned patterns take precedence.

## Label Taxonomy

### Content Bundles (what kind of content)
- `Newsletters` - digested content
- `Receipts` - payment confirmations
- `Notifications` - tool/service notifications
- `Transactional` - shipping, confirmations, etc.

### Entity Types (who is this from)
- `Team` - internal team members
- `Investors` - investors, board members
- `Legal` - law firms, legal matters
- `Vendors` - payroll, finance, contractors

### Action State (workflow tracking)
- `ic/needs-response` - I owe a reply
- `ic/waiting-on` - ball in their court
- `ic/scheduled` - has follow-up date
- `ic/processed` - audit trail (applied before archiving)

### Snooze
- `snooze/YYYY-MM-DD` - defer until date

## Tier 1: Auto-Action Patterns

### Payment Confirmations → Label: Receipts, Archive

**FROM patterns:**
```
*@stripe.com
*@paypal.com
*@brex.com
*@mercury.com
*@remote.com
*@justworks.com (payment emails only)
```

**SUBJECT patterns:**
```
"payment processed"
"payment successful"
"payment confirmed"
"direct deposit"
"wire transfer complete"
"ACH payment"
"receipt for"
"payment receipt"
```

### Calendar Auto-Responses → Archive (no label needed)

**SUBJECT starts with:**
```
"Accepted:"
"Declined:"
"Tentative:"
"Updated invitation:"
"Canceled:"
"Cancelled:"
```

**FROM patterns:**
```
*@calendar.google.com
*@resource.calendar.google.com
calendar-notification@google.com
```

### Tool Notifications → Label: Notifications, Archive

**FROM patterns:**
```
*@linear.app
*@notion.so
*@github.com
*@vercel.com
*@slack.com (digest emails only)
*@figma.com
*@loom.com
*@airtable.com
```

**EXCEPTION - Escalate to Tier 3 if body contains:**
```
"failed"
"error"
"action required"
"urgent"
"security alert"
"unusual activity"
```

### Misrouted → Archive + note

```
TO field contains address that isn't user's AND user NOT in CC
```

## Tier 2: Newsletter Patterns → Label: Newsletters

### Explicit Newsletter Signals

**FROM domain patterns:**
```
*@substack.com
*@tldrnewsletter.com
*@mail.beehiiv.com
*@convertkit.com
*@mailchimp.com (if content is editorial, not marketing)
```

**SUBJECT patterns:**
```
contains "newsletter"
contains "digest"
contains "weekly"
contains "daily briefing"
contains "morning update"
```

### Content-Based Newsletter Detection

Look for:
- Multiple article links
- "Read more" or "Continue reading" patterns
- Curated content structure
- Unsubscribe link in footer
- "View in browser" header

## Invoice/Bill Handling → Label: Bills, Tier 3

Invoices and bills that require manual payment action. Always surface for decision.

### Scope: Manual-Pay Only

**SKIP this flow (auto-pay):**
- Vendors marked `autopay: true` in known-senders.md
- Subscriptions with card on file (AWS, GCP, SaaS tools)
- Recurring charges that auto-debit
- Payment confirmations (these are Receipts, not Bills)

**PROCESS through this flow:**
- Manual approval/payment invoices
- New vendors not on auto-pay
- One-time or irregular invoices

### Invoice Detection Patterns

**SUBJECT contains:**
```
"invoice"
"bill"
"payment due"
"amount due"
"statement"
"pay now"
"payment request"
"remittance"
```

**FROM patterns (known billing senders):**
```
*@bill.com
*@quickbooks.com
*@freshbooks.com
*@xero.com
invoices@*
billing@*
accounts@*
ar@*
```

**Body indicators:**
```
- "Invoice #" or "Invoice Number"
- "Amount Due" with currency
- "Due Date" with date
- "PO #" or "Purchase Order"
- "Net 30" / "Net 15" / "Due upon receipt"
- Bank routing/account info
- Payment portal link
```

### Payment Method Detection

**Validation applies to ALL payment types - crypto invoices can be fraudulent too.**

**💳 STANDARD (Brex):**
- ACH, wire, check, card payment
- If valid → forward to bills@brex.com

**🪙 CRYPTO/USDC:**
- Invoice requests USDC, USDT, ETH, or other crypto
- Check if vendor is marked `payment: crypto` in known-senders.md
- If known crypto vendor AND valid → present "Pay via USDC" (NOT sent to Brex)
- If NOT known crypto vendor requesting crypto → RED FLAG
- Apply same fraud validation as standard invoices

### Invoice Validation Checklist

Before approving for payment, verify:

**✅ VALIDITY SIGNALS (Good):**
- Sender domain matches known vendor in `known-senders.md`
- Invoice matches expected recurring amount (±10%)
- Service/product described matches actual vendor relationship
- Invoice number format is consistent with prior invoices
- Due date is reasonable (not already weeks overdue or dated in future)
- Reply-to matches From domain
- Links point to legitimate vendor domain
- Payment method matches vendor's expected method

**🚩 RED FLAGS (Suspicious):**
- First invoice from unknown sender
- Sender domain is misspelled/similar to known vendor (typosquatting)
- Amount significantly differs from prior invoices
- Urgency pressure ("Pay immediately to avoid service interruption")
- Bank details changed from prior invoices
- Generic greeting instead of company name
- Reply-to different domain than From
- Links to unexpected/shortened URLs
- Poor grammar or formatting
- No prior purchase order or agreement
- Crypto payment request from vendor that normally takes USD

**⛔ REJECT SIGNALS (Likely Fraud):**
- "Wire transfer only" from vendor that normally uses ACH
- Personal payment account (Venmo, personal PayPal)
- Attachments with unusual extensions (.exe, .zip, .scr)
- Claims "bank details updated" without prior context
- Typosquatted domain (amaz0n.com, go0gle.com)

### Invoice Classification Output

```
📄 INVOICE: [Vendor Name] - $[Amount] [💳/🪙]
   Invoice #: [number]
   Due: [date]
   Payment: [ACH/Wire/USDC/etc.]

   Validation: ✅ LOOKS VALID / 🚩 SUSPICIOUS / ⛔ LIKELY FRAUD

   Confidence: [HIGH/MEDIUM/LOW]
   Reason: [why this classification]

   Prior invoices from sender: [count] (avg: $[amount])

   If valid (standard):
   → [Approve & forward to bills@brex.com] [Review first] [Reject]

   If valid (crypto):
   → [Pay via USDC] [Review first] [Reject]

   If suspicious:
   → [Review carefully] [Compare to prior invoices] [Reject]
```

## Tier 3: Decision-Required Signals

### Entity Type: Team

**FROM patterns (customize in known-senders.md):**
```
*@[your-company-domain].com
```

Always surface unless purely informational (e.g., auto-generated status updates).

### Entity Type: Investors

Surface with 🟡 THIS WEEK or higher urgency. Check `known-senders.md` for specific domains.

### Entity Type: Legal

**FROM patterns:**
```
*@*.law
*@*.legal
# Plus specific firms in known-senders.md
```

Always 🟡 THIS WEEK or higher.

### Urgency Indicators → 🔴 TODAY

**SUBJECT contains:**
```
"URGENT"
"ACTION REQUIRED"
"IMMEDIATE"
"TIME SENSITIVE"
"ASAP"
```

**BODY contains:**
```
"by EOD"
"by end of day"
"deadline"
"due today"
"need this today"
```

### Starred Messages

User's hot list. Always Tier 3, never auto-modify.

## Tier 4: Elimination Candidates

### Cold Outreach Patterns

**Sender unknown AND body contains:**
```
"I came across your profile"
"I noticed you"
"qualified demos"
"lead generation"
"book a call"
"15 minutes"
"quick question"
"reaching out because"
"I help companies like yours"
"we specialize in"
```

**Structural signals:**
- First email from sender
- Generic greeting ("Hi there", "Hello")
- No prior relationship
- Sales CTA in first paragraph

### Marketing Drip Patterns

**SUBJECT patterns:**
```
"tips for using"
"getting started with"
"did you know"
"feature spotlight"
"product update"
"what's new in"
```

**FROM patterns:**
- `*@*.io` (SaaS tools) with onboarding content
- `no-reply@*` with marketing content

### Low-Value Forums/Communities

**Signals of low value:**
- User has never replied
- Consistent non-engagement
- Off-topic to user's work

## Classification Priority Order

When email matches multiple patterns, use this priority:

1. **Learned rules** → Check learned-rules.md first
2. **Starred** → Always Tier 3 (surface)
3. **Internal team domain** → Tier 3 + Team label
4. **Urgency indicators** → Tier 3 🔴 TODAY
5. **Error/failure signals** → Tier 3 (even if from notification sender)
6. **Known VIP sender** → Tier 3 + appropriate entity label
7. **Payment confirmation** → Tier 1 + Receipts label → Archive
8. **Calendar response** → Tier 1 → Archive
9. **Tool notification** → Tier 1 + Notifications label → Archive
10. **Newsletter** → Tier 2 + Newsletters label
11. **Cold outreach** → Tier 4 (elimination candidate)
12. **Unknown** → Tier 3 (ask for guidance)

## Bulk Unsubscribe Extraction

For Tier 4 emails, extract unsubscribe mechanism in this order:

### 1. List-Unsubscribe Header (Best)
```
Look for header: List-Unsubscribe: <mailto:unsub@example.com>, <https://example.com/unsub>
Prefer HTTPS link over mailto
```

### 2. Body Link Patterns
```
Search email body (case-insensitive) for:
- "unsubscribe" link
- "opt out" link
- "manage preferences" link
- "email preferences" link
- Link text containing "stop receiving"
```

### 3. Footer Extraction
```
Look in last 500 chars of email body for:
- Links to */unsubscribe/*
- Links to */optout/*
- Links to */preferences/*
```

### Unsubscribe Execution
- For HTTPS links: Open in browser or make GET request
- For mailto links: Send empty email to address
- Log result: success, failed, requires confirmation page

## Recording Corrections

When user overrides classification, log to `learned-rules.md`:

**User archives something surfaced as important:**
```
[DATE] Tier 3 HIGH → User archived | Pattern: [from/subject] | New: Tier 1 auto-archive
```

**User escalates something auto-archived:**
```
[DATE] Tier 1 auto-archive → User escalated | Pattern: [from/subject] | New: Tier 3
```

## Suggesting Gmail Filters

After classifying 3+ emails with the same pattern, suggest a Gmail filter:

**Pattern detection:**
- Same sender domain → same label (3+ times)
- Same subject pattern → same label (3+ times)

**Filter suggestion format:**
```
from:*@example.com → Label: [suggested label]
(classified N emails, X% match rate)
→ [Create filter] [Ignore]
```

Use Gmail MCP `create_filter` when user approves.
