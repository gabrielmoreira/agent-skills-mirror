---
name: credits-inventory
description: "Find startup credits, perks, and offers you may have but aren't using. Use when: (1) User wants to inventory available credits/perks across accounts, (2) User asks 'do I have a deal for X?' when signing up for something new, (3) User mentions banking, cloud, or VC relationships. Searches known programs + email for forgotten offers."
---

# Credits & Perks Inventory

Surface forgotten credits, discounts, and perks across startup programs, banking relationships, corporate cards, VC portfolios, and email offers.

## State Files

This skill maintains two living documents:

| File              | Purpose                                                                      |
| ----------------- | ---------------------------------------------------------------------------- |
| `references/your-context-template.md`   | **Inputs** - User's accounts, relationships, subscriptions                   |
| `my-inventory.md` | **Outputs** - Available perks organized by service/tool, with usage tracking |

Both live in `~/.claude/skills/credits-inventory/`. Read them at skill start; update them as you discover new information.

## Usage Tracking

The inventory tracks the full lifecycle of each perk:

| Status            | Meaning                                          |
| ----------------- | ------------------------------------------------ |
| `Available`       | Not yet claimed, can be activated                |
| `Claimed [DATE]`  | Activated on date, now in use                    |
| `Active`          | Currently being used (for ongoing subscriptions) |
| `Expiring [DATE]` | Has a known expiration date                      |
| `Depleted`        | Credits fully used                               |
| `Expired`         | Past expiration, no longer available             |
| `Verify`          | Needs manual verification of status              |

**Track for metered credits (API credits, cloud credits):**

- Original value
- Remaining balance (when known)
- Burn rate (if trackable)

**Track for time-limited perks (free subscriptions):**

- Claim date
- Expiration date
- Auto-renewal status

## Two Modes

### Mode 1: Full Inventory ("What do I have?")

Comprehensive scan of all accounts to surface available credits and perks.

### Mode 2: Specific Lookup ("Do I have a deal for X?")

User is signing up for a specific service - check if they have a discount.

---

## Workflow

### 1. Load Context

```
Read: ~/.claude/skills/credits-inventory/my-context.md
Read: ~/.claude/skills/credits-inventory/my-inventory.md
```

If context file is empty or outdated, ask user to update their accounts.

### 2. For Full Inventory: Scan All Sources

For each account type in context:

**A. Check known programs** (see reference database below)

**B. Search email via gscli**

```bash
# Search for perks from known sources
gscli gmail search "from:[source] perks OR credits OR offer" -l 20

# Search for specific services
gscli gmail search "[service] free OR credits OR discount" -l 10

# Search for expiring offers
gscli gmail search "expires OR expiring credits OR offer" -l 15
```

**C. Read promising emails**

```bash
gscli gmail read [message-id]
```

Look for:

- Claim links/URLs
- Promo codes
- Expiration dates
- Specific values

### 3. For Specific Lookup: Check for Service

When user asks "do I have a deal for [SERVICE]?":

1. Check `my-inventory.md` for existing entries
2. Search email: `gscli gmail search "[SERVICE] free OR credits OR discount OR offer" -l 15`
3. Check if any of user's accounts (VCs, banking, subscriptions) offer it
4. Report findings with claim instructions

### 4. Update Inventory

After discovery, update `my-inventory.md` with findings organized by service.

**Inventory organization:**

- Group by SERVICE/TOOL name (alphabetical)
- Under each service, list all available offers
- Include: value, source, claimed date, expiration, remaining, status

### 5. Track Usage (When User Claims or Updates)

When user says "I claimed [perk]" or "update [perk] status":

1. Find the perk in `my-inventory.md`
2. Update the row:
   - Set `Claimed` to today's date
   - Set `Expires` if known (often 1 year from claim)
   - Set `Status` to `Active` or `Claimed YYYY-MM-DD`
3. Add to "Recently Claimed" section in Dashboard
4. Recalculate Dashboard totals

**For balance updates** ("I have $X left on [perk]"):

1. Update the `Remaining` column
2. If low or depleted, flag in Dashboard

### 6. Expiration Monitoring

When running inventory checks:

1. Scan all items with `Expires` dates
2. Flag anything expiring within 90 days
3. Update "Expiring Soon" section in Dashboard
4. Alert user to time-sensitive items

**Expiration actions:**

- 90 days out: Add to "Expiring Soon"
- 30 days out: Highlight as urgent
- Expired: Move status to `Expired`, keep in inventory for reference

---

## Email Search Patterns

### gscli Commands

```bash
# VC portfolio perks (replace with actual investor names from context)
gscli gmail search "from:usv perks OR credits OR offer" -l 20
gscli gmail search "from:getproven" -l 10

# Banking perks
gscli gmail search "from:brex perks OR credits" -l 15
gscli gmail search "from:mercury perks OR partner" -l 15

# Newsletter perks
gscli gmail search "from:lenny product pass OR perks" -l 10

# Service-specific (when doing lookups)
gscli gmail search "[servicename] free OR credits OR startup" -l 15

# Catch expiring offers
gscli gmail search "expires soon OR expiring credits" -l 20
gscli gmail search "activate your OR claim your" -l 15
```

### Reading Emails

When you find a promising email:

```bash
gscli gmail read [message-id]
```

Extract:

- **Claim URL** - The link to activate the offer
- **Promo code** - If applicable
- **Value** - Dollar amount or description
- **Expiration** - When it expires
- **Requirements** - Any eligibility criteria

If you find a claim URL but can't access it directly, provide clear instructions:

```
**How to claim:**
1. Go to: [URL]
2. Log in with your [account type] credentials
3. Look for [specific button/section]
4. Apply code: [CODE] (if applicable)
```

---

## Inventory File Format

`my-inventory.md` should be organized BY SERVICE with usage tracking:

```markdown
# Credits & Perks Inventory

Last updated: YYYY-MM-DD

## Dashboard

| Metric                      | Value   |
| --------------------------- | ------- |
| Total available (unclaimed) | $X,XXX  |
| Total claimed (active)      | $X,XXX  |
| Total remaining balance     | $X,XXX  |
| Expiring within 90 days     | [count] |

### Expiring Soon

| Service     | Source | Expires    | Value            | Action      |
| ----------- | ------ | ---------- | ---------------- | ----------- |
| AWS credits | Brex   | 2026-03-15 | $2,340 remaining | Use or lose |

### Recently Claimed

| Service | Source  | Claimed    | Value   |
| ------- | ------- | ---------- | ------- |
| PostHog | Lenny's | 2026-01-15 | $16,500 |

---

## A

### Anthropic (Claude API)

| Source     | Value   | Claimed    | Expires    | Remaining | Status    |
| ---------- | ------- | ---------- | ---------- | --------- | --------- |
| Brex Perks | $500    | —          | —          | —         | Available |
| Your VC Perk | $X,XXX | YYYY-MM-DD | YYYY-MM-DD | $X,XXX | Active |

### AWS

| Source          | Value   | Claimed    | Expires    | Remaining | Status           |
| --------------- | ------- | ---------- | ---------- | --------- | ---------------- |
| Brex Perks      | $5,000  | 2025-06-01 | 2027-06-01 | $2,340    | Expiring 2027-06 |
| Pump.co savings | $7,870+ | Active     | —          | Ongoing   | Active           |

---

## P

### PostHog

| Source  | Value   | Claimed    | Expires    | Remaining | Status |
| ------- | ------- | ---------- | ---------- | --------- | ------ |
| Lenny's | $16,500 | 2026-01-15 | 2027-01-15 | Active    | Active |

---

[Continue alphabetically...]
```

### Table Columns

| Column    | Required   | Description                                             |
| --------- | ---------- | ------------------------------------------------------- |
| Source    | Yes        | Where the perk comes from                               |
| Value     | Yes        | Original dollar value or description                    |
| Claimed   | If claimed | Date claimed (YYYY-MM-DD) or "—"                        |
| Expires   | If known   | Expiration date or "—"                                  |
| Remaining | If metered | Current balance for credits, "Active" for subscriptions |
| Status    | Yes        | Current state (see Usage Tracking above)                |

---

## Context File Format

`references/your-context-template.md` should list user's accounts:

```markdown
# My Accounts & Relationships

Last updated: YYYY-MM-DD

## Investors & Accelerators

- [Your VC] - [perks platform URL]
- [Other investor]
- [Accelerator]



## Banking & Cards

- Mercury (business banking)
- Brex (corporate card)
- Chase Sapphire Reserve (personal)
- Delta Amex Gold (personal)

## Subscriptions

- Lenny's Newsletter (annual) - lennysproductpass.com
- LinkedIn Premium
- X Premium
- Costco Executive

## Equity & HR

- Carta

## Cloud & Hosting

- [Current providers]

## Notes

- [Any special relationships or programs]
```

---

## Reference: Known Programs

### VC Portfolio Platforms

| VC/Accelerator | Perks Platform      | How to Access               |
| -------------- | ------------------- | --------------------------- |
| USV            | Proven              | usv.getproven.com           |
| YC             | YC Deals            | bookface.ycombinator.com    |
| a16z           | Portfolio Resources | Via portfolio contact       |
| Sequoia        | Arc benefits        | Via portfolio contact       |
| Most VCs       | Various             | Email your investor contact |

### Banking Perks

| Bank/Card              | Perks Page         | Notable Offers                           |
| ---------------------- | ------------------ | ---------------------------------------- |
| Brex                   | brex.com/perks     | $350K+ total (AWS, OpenAI, Retool, etc.) |
| Mercury                | mercury.com/perks  | Various partner discounts                |
| Chase Sapphire Reserve | chase.com/benefits | $300 travel, DoorDash, Lyft, lounges     |
| Amex Platinum          | amex.com/benefits  | Dell, airline, wireless credits          |

### Newsletter/Subscription Perks

| Subscription       | Perks Page            | Notable Offers                |
| ------------------ | --------------------- | ----------------------------- |
| Lenny's Newsletter | lennysproductpass.com | $25K+ (PostHog, Notion, etc.) |

### Direct Startup Programs

| Service      | Program         | Value          | Link                     |
| ------------ | --------------- | -------------- | ------------------------ |
| AWS          | Activate        | Up to $100K    | aws.amazon.com/activate  |
| Google Cloud | Startups        | Up to $350K    | cloud.google.com/startup |
| Microsoft    | Startups        | Up to $150K    | startups.microsoft.com   |
| HubSpot      | Startups        | Up to 90% off  | hubspot.com/startups     |
| Intercom     | Early Stage     | $49/mo for 1yr | intercom.com/early-stage |
| Segment      | Startup Program | $25K value     | segment.com/startup      |
| Mixpanel     | Startups        | $50K credits   | mixpanel.com/startups    |

---

## Conversation Flow

### Starting a Session

"Let me check your credits inventory.

[Read context and inventory files]

**Current status:**

- Last updated: [date]
- Total available: ~$X value
- [N] items expiring soon

Want me to:

1. Do a fresh scan for new offers?
2. Look up a specific service?
3. Update your account list?"

### After Discovery

"Found [N] new perks. Updating your inventory...

**New additions:**

- [Service]: $X via [Source]
- [Service]: $X via [Source]

**Action items:**

1. [Highest priority - include exact steps]
2. [Second priority]

Your inventory has been updated at `~/.claude/skills/credits-inventory/my-inventory.md`"

### For Specific Lookup

"Looking for deals on [SERVICE]...

**Found:**

- [Source 1]: [Value] - [How to claim]
- [Source 2]: [Value] - [How to claim]

**Not found in:**

- [Sources checked that didn't have it]

Want me to add this to your inventory watchlist?"

---

## Tips for Claude

### Discovery

- **Always read state files first** - Don't ask for info you already have
- **Search email proactively** - Many offers are buried in newsletters
- **Try to follow links** - If you can fetch a URL, do it to get specifics
- **When links require auth** - Give clear step-by-step instructions
- **Think laterally** - VC relationships unlock indirect perks

### Inventory Management

- **Update inventory after every discovery** - Keep it current
- **Be specific with claim instructions** - URLs, steps, codes
- **Prioritize by value** - Lead with high-value items
- **Flag expirations** - Surface time-sensitive offers prominently

### Usage Tracking

- **Ask about claimed status** - When showing perks, ask "have you claimed any of these?"
- **Prompt for updates** - "Let me know when you claim this so I can track it"
- **Track remaining balances** - For API credits, ask periodically about usage
- **Monitor expirations** - Start each session by checking what's expiring soon
- **Keep Dashboard current** - Update totals when status changes

### Session Flow

1. Read inventory → Check expiring items → Alert user
2. Handle user request (discovery or lookup)
3. Update inventory with findings
4. Prompt user to report any claims
5. Update Dashboard if needed

The goal: Be the knowledgeable assistant who knows all the programs AND keeps a running tally of what's available, claimed, and expiring.
