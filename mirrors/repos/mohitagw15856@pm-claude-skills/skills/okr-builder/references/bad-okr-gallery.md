# The Bad OKR Gallery

Real-shaped examples of OKRs that look fine in a planning doc and fail at quarter end — with the diagnosis and the rewrite. Use these as pattern-matching anchors when reviewing a user's existing OKRs.

## 1. The disguised roadmap

> **O:** Ship the new onboarding experience
> **KR1:** Launch redesigned signup flow · **KR2:** Release mobile onboarding · **KR3:** Migrate all users to new flow

**Diagnosis:** three project milestones wearing KR costumes. At quarter end the team "achieved" everything and the activation number didn't move — and nobody has to explain why.

**Rewrite:** *O: New users reach value fast enough to stay.* KR1: activation (first report created ≤ day 3) 42% → 60% · KR2: week-1 → week-4 retention 31% → 45% · KR3: median time-to-first-value 46min → 15min. *(The redesign is how the team plans to do it — it lives on the roadmap, not in the OKR.)*

## 2. The unfalsifiable objective

> **O:** Delight our customers
> **KR1:** Improve NPS · **KR2:** Reduce complaints · **KR3:** Be more responsive to feedback

**Diagnosis:** no baselines, no targets, one KR isn't even a metric. Scores 0.7 or 0.3 depending on who's in the room.

**Rewrite:** KR1: NPS 32 → 45 (quarterly survey) · KR2: support contacts per 100 active users 8.1 → 5.5 · KR3: median time from feedback to shipped-or-declined decision 90d → 30d.

## 3. The sandbagged banker

> **KR:** Increase MRR from $80k to $84k *(last three quarters grew 6-8% organically)*

**Diagnosis:** the target is below drift — it scores 1.0 if the team does nothing. Classic when OKRs feed performance reviews.

**Rewrite:** MRR $80k → $100k, with the stretch stated: "requires the new pricing tier to convert ≥ 3% of free accounts, on top of ~7% organic growth." Ambition is legible when the organic baseline is named.

## 4. The uncontrollable

> **KR (design team):** Company revenue grows 25%

**Diagnosis:** the team can't move it alone, so it motivates nothing and scores randomly. The inverse failure of #1 — outcome so far downstream it's weather.

**Rewrite:** pick the team's *most downstream controllable* outcome: checkout-flow conversion 2.1% → 2.8%; trial-to-paid uplift attributable to the redesigned upgrade path.

## 5. The metric zoo

> **O:** Grow the platform — with 7 KRs covering signups, MAU, retention, NPS, revenue, page speed, and hiring

**Diagnosis:** everything is a priority, so nothing is. At week 6 the team can't say which number this quarter is *about*.

**Rewrite:** pick the 3 that this quarter's work actually targets; move the rest to a health-metrics dashboard (watched, not targeted). One objective = one coherent story.

## 6. The guardrail-free speed run

> **KR:** Reduce median support response time 4h → 30min

**Diagnosis:** achievable by closing tickets prematurely. Any KR that can be gamed by degrading something unmeasured needs its counterweight.

**Rewrite:** keep the KR, add its guardrail: "…while CSAT stays ≥ 4.4 and reopen rate ≤ 7%." (Guardrails aren't scored for ambition — they're conditions for the KR to count.)

## Quick diagnostic — run any KR through these

1. Could the team score 1.0 while the user/business outcome stays flat? → it's an output (see #1).
2. Would two reasonable people score it the same? → if not, missing baseline/target (see #2).
3. Is the target above the do-nothing drift? (see #3)
4. Can this team move it without another team's quarter going right? (see #4)
5. Can it be gamed by quietly degrading something? → add the guardrail (see #6).
