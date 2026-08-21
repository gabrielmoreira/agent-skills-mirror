---
name: pricing-and-packaging-design
description: "Sets software list price and packaging: value metric, Van Westendorp WTP, hybrid subscription-plus-usage, good-better-best tiers, and AI/compute COGS stress tests. Use when pricing a product, moving off seat-based plans, or fixing negative LLM margins. Not for unvalidated demand, positioning copy, TAM, GTM channels, deal-desk discounts, or wiring Stripe meters."
version: 1.0.1
---

## Overview

Pricing is the single highest-leverage decision in a software business. Packaging—how you slice the product into tiers and what meters the bill—decides whether a happy customer can spend more with you over time without a sales conversation. 

**Prime Directive:** *Price on value, meter on a unit that grows as the customer wins, and never let a single power user cost you more than they pay. In 2026, every price must survive a COGS stress test: if your most intensive customer's compute cost outruns their bill, you don't have a pricing problem, you have a bankruptcy schedule.*

## When to Use

**Use this skill when the request involves any of the following:**
- **Price-setting:** "How should we price [product]?", "What pricing model should we use?", "Design our pricing page / tiers / plans."
- **Model-migration:** "We're moving from seat-based to usage-based — how?", "How do we re-price without losing customers?"
- **Margin & COGS:** "Our margins are negative / our AI feature is losing money on power users.", "LLM / inference costs are eating our profit."
- **Conversion / expansion:** "Conversion is low / people stall on our pricing page.", "We're churning customers at a tier boundary.", "Our expansion revenue is flat."

**Do NOT use this skill when:**
- **Demand is not yet validated.** Route to `mvp-scoping-and-risk-test` to retire value risk first.
- **Positioning problems masquerading as price objections.** If buyers don't grasp the differentiated value, fix the frame first via `product-positioning-and-narrative`.
- **Channel & acquisition economics.** Route to `go-to-market-strategy`.
- **Market sizing / TAM.** Route to `market-sizing-and-tam-validation`.
- **Discounting tactics & deal-desk mechanics.** This skill sets list price and guardrails, not sales-ops execution.
- **Detailed financial forecasting.** Route to a financial-modeling skill.
- **Billing-system implementation.** This defines *what* to meter, not how to wire Stripe.

## Prerequisites

- Access to current usage data and fully-loaded COGS (inference, compute, API fees, storage, bandwidth) if re-pricing an existing product.
- If a `references/` directory exists, load any PSM survey templates or COGS calculation spreadsheets before executing Step 4 or Step 6.

## Procedure

### 1. Choose the Value Metric
The value metric is the unit you charge for (seats, API calls, GB stored, outcomes delivered). It determines whether revenue expands by itself.
- **Test 1: Tracks value.** As the customer gets more value, the metric goes up.
- **Test 2: Scales with success.** Grows as the customer's usage of the value grows (drives Net Revenue Retention).
- **Test 3: Predictable.** The customer can roughly anticipate their bill.
*Get the metric right and expansion is automatic; get it wrong and you're re-selling every customer every year just to stay flat.*

### 2. Anchor Price to Value
- Reject **cost-plus pricing** (anchors to your costs, gives away value, drives price toward zero as AI lowers build cost). Cost sets the floor, never the target.
- Reject **competitor-parity pricing** (cedes pricing power, triggers races to the bottom). Use competitor prices as a reference, never the anchor.
- Anchor to **quantified customer value** (money made, saved, time recovered). Capture a defensible fraction (typically 10–30% of the value created).

### 3. Select the Pricing Model (Hybrid Default)
For 2026 AI/compute-heavy products, default to a **Hybrid model**:
- **Committed subscription base:** A platform fee or included usage bucket giving both sides predictability and a revenue floor.
- **Usage-based expansion:** Overage pricing above the bucket so heavy users pay for the value and COGS they consume.
- **Buyer control:** Always offer a way to cap or predict spend (alerts, caps, committed-use discounts).

### 4. Measure Willingness-to-Pay (Van Westendorp PSM)
Replace gut guesses with data. Run the PSM survey on a representative sample asking four questions:
1. At what price is this **too expensive** (would not consider buying)?
2. At what price is this **getting expensive**, but still considered?
3. At what price is this **a good deal / bargain**?
4. At what price is this **too cheap** (doubt its quality)?
- Plot cumulative distributions to find the **acceptable range** (between Point of Marginal Cheapness and Point of Marginal Expensiveness).
- Weight the *upper* half of the range (people understate WTP). Validate against real purchase behavior wherever possible.

### 5. Design Good-Better-Best Tiers
Package around buyer personas, not arbitrary feature cuts. Default to 3 visible tiers.
- **Good (Entry):** Individual/small team. Delivers core value, priced to win adoption.
- **Better (Mainstream):** Primary ICP. The "most popular" tier where most revenue concentrates.
- **Best (Power):** Larger org. Adds advanced controls, scale, support.
- **Enterprise (Custom):** Top tier gating organizational trust (SSO, audit, SLAs).
**Feature-gating logic:** Core/utility features in every tier. Value/volume features as expansion levers. Advanced/power features in Better/Best. Enterprise/org features at the top. "Fence by who, not by what."

### 6. Margin & COGS Stress Test (The 2026 Hard Gate)
- Compute **fully-loaded gross margin per customer and per tier**, subtracting all variable COGS.
- **Stress-test the worst-case (power-user) unit economics, not the average.** Model the heaviest plausible user on each plan and confirm they are margin-positive or capped.
- Set a **margin floor** below which you will not price or discount.

### 7. Migration & Lifecycle (If Re-pricing)
- Model the migration's **revenue-vs-churn impact per cohort** before committing. Reject net-loss migrations.
- Define a **grandfathering policy** and **cohorted migration** with generous notice + a new-value story. Default to new-customers-only if the base is fragile.
- Instrument pricing as a **living system** (conversion by tier, NRR, gross margin per cohort) with an owner and review trigger.

## Pitfalls

- **The Silent Revenue Stall:** Choosing a value metric that doesn't move when the customer succeeds (e.g., pricing per login instead of per contact managed). Revenue stays flat even with happy customers.
- **The Power User Death Spiral:** Shipping a flat-priced plan on a compute-heavy AI product. The heaviest users cost more than they pay, meaning every successful user is a loss.
- **Crippling Instead of Adding:** Lower tiers that remove basic functionality breed resentment. Differentiate by *adding* value for higher personas, not by crippling the core.
- **Too Many Tiers:** More than ~4 visible tiers signals an unfocused packaging strategy and taxes conversion. Buyers can't figure out which tier is for them in 10 seconds.
- **Uncappable Surprise Bills:** Pure usage-based pricing without caps or alerts terrifies buyers and suppresses adoption. The 2026 buyer will not adopt a tool that can bankrupt them by surprise.

## Verification

Before declaring pricing and packaging complete, confirm every applicable item:

**Value metric & value alignment**
- [ ] A primary value metric is chosen and passes the three tests: tracks value, scales with success, and is predictable.
- [ ] The value metric correlates with COGS where compute-heavy.
- [ ] Pricing is anchored to quantified customer value, not cost-plus or competitor parity.

**Willingness-to-pay**
- [ ] WTP is grounded in research (PSM/Gabor-Granger), run on a representative sample.
- [ ] Target prices are stated as reasoned ranges, weighted toward the upper half, and reconciled with the margin floor.

**Pricing model**
- [ ] The model fits the value metric; compute-heavy/AI products default to hybrid (committed base + included bucket + usage overage).
- [ ] The buyer has spend predictability and control (caps, alerts).
- [ ] The overage rate exceeds unit COGS with margin.

**Packaging & tiers**
- [ ] Tiers are good-better-best (~3 visible), each targeting a distinct buyer persona.
- [ ] Tiers are differentiated by added value, not crippling; entry tier delivers genuine value.
- [ ] Features are gated by type and persona; enterprise features (SSO, RBAC, audit) at the top.
- [ ] The middle tier is designed to be the default choice.

**Margin protection**
- [ ] Fully-loaded variable COGS per unit is computed; gross-margin economics drive decisions.
- [ ] Every tier is margin-positive at typical usage; worst-case power user is stress-tested and confirmed margin-positive or capped.
- [ ] A margin floor is set; no discount or overage dips below it.

**Migration & lifecycle**
- [ ] Revenue-vs-churn impact is modeled per cohort; net-loss migrations rejected.
- [ ] Grandfathering policy and cohorted migration defined; instrumented as a living system.

> **Final gut-check — the "power user + ten-second" double test:** Find your single most intensive plausible customer on each plan. If any costs more than they pay, fix the meter and overage first. Then, show the pricing page to someone outside the company for ten seconds: can they tell you which tier is for them and roughly what they'll pay? If not, the packaging is too complex.

## Related skills

- `mvp-scoping-and-risk-test`: Use first if demand/value is not yet validated.
- `product-positioning-and-narrative`: Use if "price is too high" is actually a value-narrative failure.
- `go-to-market-strategy`: Hand off channel and acquisition economics after setting price.
- `market-sizing-and-tam-validation`: Hand off TAM sizing; pricing decisions should trigger a re-size.
