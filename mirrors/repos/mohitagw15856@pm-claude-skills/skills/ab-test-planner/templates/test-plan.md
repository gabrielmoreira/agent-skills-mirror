# Test plan: [name] — pre-registered [date] · owner: [name]

## Hypothesis
Because we observed [evidence], we believe [change] for [segment] will [effect].

## The decision this test feeds
Ship / iterate / kill [feature] — decided by [role] on [date].

## Design (locked before launch — references/test-validity-traps.md)
- **Primary metric (value event):** … · current baseline: …
- **Guardrails (veto power):** [retention / refunds / latency / …]
- **Randomisation unit:** [user/workspace/session] — because experience coheres at this level
- **Minimum detectable effect at our traffic:** [x]% in [n] weeks *(power calc attached)* → plausible? ✅/❌
- **Horizon:** [n] weeks (≥2 weekly cycles) — no early stopping on significance
- **Ship threshold:** effect ≥ [x]% AND guardrails clean

## Variants
Control: … · Treatment: … *(one change; if two, that's two tests)*

## Validity checks scheduled
- [ ] SRM check automated from day 1
- [ ] Early-vs-late cohort comparison at readout (novelty check)
- [ ] Pre-registered segments (analysable): […] — everything else = hypothesis-generation only

## Readout appointment
[date] · attendees · the pre-written decision rule applied as written
