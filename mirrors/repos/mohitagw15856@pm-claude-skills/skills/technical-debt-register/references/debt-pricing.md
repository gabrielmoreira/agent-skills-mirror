# Pricing Debt: Turning "It's Bad" Into a Number Someone Can Rank

Debt registers die as guilt lists — everything feels important, nothing gets scheduled. The fix is pricing: every entry carries its *interest rate* (ongoing cost) so debt competes with features in the same currency.

## The interest-rate framing

Debt principal (cost to fix) matters less than interest (cost of NOT fixing, recurring):
- **Velocity tax** — "every feature touching billing takes ~30% longer" → hours/quarter at loaded rate
- **Incident interest** — "this flaky queue causes ~2 pages/month" → on-call hours + risk-adjusted incident cost
- **Onboarding drag** — "new engineers need 3 extra weeks because of the God-object" → weeks × frequency of hiring
- **Option foreclosure** — "we can't do multi-region until this is untangled" → priced by the blocked initiative's value, and dated

Estimates are ranges with stated assumptions — a defensible "~40-80 eng-hours/quarter" beats false precision, and beats "high" by a mile.

## Classification that drives different treatments

- **Load-bearing debt** (interest compounds: everyone touches it) → schedule as a project with the interest math as the business case
- **Contained debt** (ugly but isolated, interest ≈ 0) → document, fence, and deliberately LEAVE — fixing zero-interest debt is vanity refactoring wearing a virtue costume
- **Decaying debt** (interest rising: scale/team growth will inflame it) → date the tripwire ("at 2× traffic this becomes load-bearing") and revisit on schedule
- **Expiring debt** (the system it lives in is being replaced) → never fix; note the expiry

## Register hygiene

Every entry: symptom → root debt → interest (priced) → principal (sized: S/M/L) → class → owner. Review quarterly: reprice interest (it changes), close what expired, and *celebrate deliberate non-fixes* — a register that only grows teaches the org it's a graveyard. Cap active entries (~20); below-the-line items live in an icebox, not in the meeting.

## Getting it scheduled

The pitch that works is never "code quality": it's "this specific debt costs [interest] per quarter; [principal] fixes it; payback in [n] months — it outranks feature X by its own math." Debt that can't win that argument honestly should stay in the register, unfixed, without shame.
