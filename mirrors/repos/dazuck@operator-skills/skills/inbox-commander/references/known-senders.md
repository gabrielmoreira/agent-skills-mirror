# Known Senders

VIP contacts and sender patterns. Customize for your environment.

## Internal Team (Always Tier 3 HIGH)

### Team Domains

Add your organization's email domains:
```
# Example:
# *@yourcompany.com
# *@subsidiary.com
```

### Key Team Members

Add specific people to always surface:
```
# Example:
# Jane Doe (CEO) - jane@yourcompany.com
# John Smith (CTO) - john@yourcompany.com
```

### Misrouted Detection

Add addresses that sometimes receive your mail incorrectly:
```
# Example:
# similar-name@company.com - Often receives my emails incorrectly
```

## Investors & Board (Always Tier 3 HIGH)

Add investor contacts:
```
# Example:
# *@sequoiacap.com
# *@a16z.com
# specific-partner@firm.com
```

## Legal & Compliance (Always Tier 3 HIGH)

```
# Generic patterns:
*@*.law
*@*.legal

# Specific firms:
# *@cooley.com
# *@wsgr.com
```

## Key Vendors (Tier 3 if issues, Tier 1 if routine)

### Billing Vendor Properties

For invoice validation, vendors can have these properties:
- `autopay: true` - Skip invoice approval flow (auto-pay on file)
- `payment: crypto` - Expects USDC/crypto payment (not Brex)
- `payment: standard` - Expects ACH/wire/card via Brex (default)

### Payroll & HR
```
# *@justworks.com
#   - autopay: true (payroll is auto-debit)
#   - Payment confirmations → Tier 1
#   - Everything else → Tier 3 (often critical)
#
# *@gusto.com
# *@rippling.com
```

### Finance & SaaS (Auto-pay - card on file)
```
# *@brex.com | autopay: true
# *@mercury.com | autopay: true
# *@stripe.com | autopay: true
# *@aws.amazon.com | autopay: true
# *@cloud.google.com | autopay: true
# *@vercel.com | autopay: true
```

### Manual-Pay Vendors (Invoices need approval)
```
# Add vendors whose invoices need manual approval:
# *@lawfirm.com | payment: standard
# *@consulting-agency.com | payment: standard
# contractor@freelance.com | payment: standard
```

### Crypto-Native Vendors (Paid via USDC)
```
# Vendors that expect crypto payment:
# *@web3-infra.io | payment: crypto
# *@blockchain-service.com | payment: crypto
```

## Newsletter Senders (Tier 2 Digest)

### Priority Newsletters (summarize fully)

Add newsletters you want fully digested:
```
# TLDR (multiple editions):
*@tldrnewsletter.com

# Substack authors you follow:
# author@substack.com

# Other priority sources:
# *@thedeepview.co
# *@pitchbook.com
```

### Lower Priority (scan for relevance)
```
# General patterns:
*@substack.com
*@beehiiv.com
*@convertkit.com
```

## Known Spam/Cold Outreach Senders (Tier 4)

Add senders identified as persistent cold outreach:
```
# Example:
# sales@spammy-saas.com
# Breakcold CRM
```

## Blocked/Irrelevant (Auto-archive or ignore)

```
# Senders that are consistently wrong recipient or irrelevant:
# spam@example.com
```

---

## Updating This File

When patterns emerge:
1. Add VIP senders to appropriate section
2. Add spam senders to cold outreach section
3. Add new newsletter sources to digest section
4. Note any domain changes for team members

The skill will also suggest additions based on classification patterns.
