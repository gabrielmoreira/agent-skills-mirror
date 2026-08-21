---
name: mvp-scoping-and-risk-test
description: "Defines the smallest product slice and cheapest experiment to test a startup's core value hypothesis before heavy engineering. Use when a founder is scoping an MVP, validating demand, designing a smoke/concierge/Wizard-of-Oz test, or fighting over-engineering. Not for post-PMF growth, live A/B statistical readout, or writing the production implementation; never treat opinions as a substitute for behavioral pass/fail bars."
version: 1.0.1
---

# MVP Scoping and Risk Test

An MVP is not a smaller version of the product — it is the cheapest possible *experiment* that produces a real signal about whether the product should exist at all. The mistake this skill exists to prevent is the most expensive one in startups: building a polished, well-engineered answer to a question nobody asked. Code is the most expensive way to test a hypothesis; a conversation, a landing page, or a manually-delivered service is almost always cheaper and faster. The job here is to find the *single assumption that, if false, kills the whole idea*, and to design the cheapest honest test of that assumption before a line of production code is written.

> **Prime Directive:** *Test the riskiest assumption with the cheapest experiment, and measure behavior, not opinions. The goal of an MVP is to maximize validated learning per dollar and per day — not to ship features. If you can answer the question without building, don't build. If you must build, build the least that answers it, and define what "pass" and "fail" mean before you run the test, so a result you wanted can't rewrite the bar you set.*

---

## When to Use

### Idea-validation triggers (someone has a hypothesis, not yet a product)

- "I have an idea for [product] — how do I test if it's real / worth building?"
- "How do I validate demand / validate this idea before building it?"
- "What's the MVP for [concept]?" / "How do I scope an MVP?"
- "Is there a market for this?" / "Will anyone actually pay for / use this?"
- "What's the riskiest assumption here / what could kill this idea?"
- "Design a pre-launch experiment / a landing-page test / a waitlist test."

### Scoping triggers (a product or feature is about to be over-built)

- "We're planning a big new feature — how do we de-risk it before committing the roadmap?"
- "How do we cut scope to the minimum?" / "What's the smallest thing we can ship to learn?"
- "We've been building for months without launching — help us scope down."
- "Is this feature worth building?" / "How do we know this is what users want?"

### Experiment-design triggers (what test, what threshold)

- "Should this be a smoke test, concierge, or Wizard of Oz MVP?"
- "What signal counts as proof people want this?"
- "How do I set a pass/fail bar for a demand test?"
- "Should we pivot, persevere, or kill this?"

### When NOT to use this skill

- **Post-PMF growth and scaling.** Once the value hypothesis is *already validated* — you have real retained, paying users and the question is "how do we get more of them faster" — the work is acquisition, funnel optimization, and scaling, not MVP validation. Route demand-capture optimization to a **conversion-funnel-optimization** skill and channel strategy to a **GTM/growth** skill. This skill is for *before* you know it works.
- **Statistical readout of a live, instrumented experiment.** Computing sample sizes, significance, sequential-testing boundaries, and SRM for a running A/B test belongs to an **ab-testing-design-and-analysis** skill. This skill decides *what cheap test to run and what behavioral signal to look for*; it borrows just enough statistics to set an honest threshold, then hands off rigorous inference. (MVP demand tests are usually too low-volume and too early for formal significance anyway — see Pitfalls.)
- **Detailed engineering implementation.** Architecture, framework choice, and how to actually *build* the validated product are out of scope. This skill's output is a *scope cut and an experiment design*, and its frequent recommendation is "don't build yet." Hand the build to the relevant engineering skill once a risk is retired.
- **Pitch-deck / fundraising narrative.** Turning validated learning into an investor story is a **pitch-deck-storytelling** skill. This skill *produces* the traction evidence that deck cites; it does not write the deck.
- **Pure UX/usability redesign of an existing, wanted product.** If users already want and use the product and the issue is *they can't figure out the new flow*, that's usability work, not value-risk validation. (Caveat: this skill *does* cover usability risk as one of the Four Risks at the scoping stage — but a standalone usability overhaul of a proven product is a different job.)
- **Qualitative pre-idea discovery with no hypothesis yet.** If the user doesn't yet have a value hypothesis to test — they're still doing open-ended customer discovery to *find* a problem — that's upstream problem-discovery interviewing. This skill takes a stated hypothesis as input; if there's no hypothesis, help them form one first (the workflow's Step 1 does this), then proceed.

When a request straddles a boundary ("validate this *and* tell me how to build it"), run the scoping and risk test here, retire the value risk first, and explicitly hand off the build only for what survives the test. State the handoff rather than quietly drifting into implementation.

---

## Prerequisites

No tooling, environment, or codebase is required to use this skill. It is a methodology and decision framework. The only prerequisites are:

1. **A stated idea or hypothesis** to evaluate. If the user has only a vague domain interest with no hypothesis, help them form one first (Step 1 of the Procedure covers this).
2. **Access to the target customer segment** — at minimum, the ability to reach 20–50 representative prospects through some channel (community, ad audience, email list, personal network). If no channel exists, finding one becomes the first task (Step 0).
3. **A willingness to kill the idea.** If the founder is emotionally committed to building regardless of results, the validation exercise is theater. Name this honestly upfront.

---

## Procedure

Follow the steps in order. Do not design an experiment (Step 4) before the riskiest assumption is identified (Step 2) — testing the wrong assumption cheaply is still a wasted experiment.

### Core Principles (apply as defaults throughout)

The cost structure of building has collapsed. AI-assisted development means a founder can ship a working prototype in a weekend, which has *inverted* the bottleneck: the scarce resource is no longer engineering capacity, it is **validated demand**. When building is cheap, the temptation to skip validation and "just build it" is stronger than ever — and more dangerous, because a polished AI-built product that nobody wants looks exactly like a real business until you check whether anyone is actually using it.

**P1 — Validate the riskiest assumption, and it is almost always Value Risk.** Marty Cagan / SVPG's **Four Risks** framework is the organizing lens:

| Risk | The question it asks | Who owns it | How to test it cheaply |
|---|---|---|---|
| **Value Risk** | *Will they buy it or choose to use it?* | Product / founder | Demand experiments — smoke test, concierge, pre-order, LOI |
| **Usability Risk** | *Can they figure out how to use it?* | Design | Prototype + 5-user usability test |
| **Feasibility Risk** | *Can we actually build it (tech, time, cost)?* | Engineering | Technical spike / proof-of-concept |
| **Viability Risk** | *Does it work for our business — margins, legal, channel, model?* | Business | Unit-economics model, margin/inference-cost math, legal check |

Value Risk is the default killer and the default focus. In 2026, with feasibility risk shrinking (AI makes most things buildable), the *relative* weight of value risk is higher than ever. Spend validation budget there first.

**P2 — Behavior is evidence; opinions are noise.** A person saying "yes, I'd totally use that" costs them nothing and predicts nothing. Design every experiment so that "interested" requires the user to *do* something with a real cost, not *say* something free.

**P3 — The Skin-in-the-Game ladder (Savoia).** Weight signals by what they cost the user:

```
SKIN-IN-THE-GAME LADDER  (low signal → high signal)
─────────────────────────────────────────────────────────────────
  Weakest │ A verbal "that's a great idea"            → ~zero weight
          │ A like / follow / upvote                  → near-zero weight
          │ An email signup (one click, no cost)      → low weight
          │ A detailed survey / giving real data      → moderate weight
          │ Booking a call / spending 30+ minutes      → moderate-high weight
          │ A refundable deposit / pre-order           → high weight
  Strongest│ Non-refundable payment / signed LOI       → highest weight
─────────────────────────────────────────────────────────────────
```

Practical rule: **an email address is a weak signal; a credit card is a strong one.** A waitlist of 10,000 emails can convert to near-zero paying customers, while 20 pre-orders or 3 signed letters of intent (for B2B) can validate a business.

**P4 — The four lean MVP formats.** Ordered roughly by build cost:

- **Smoke test (landing page + capture/pre-order):** A page that describes the value proposition as if it already exists, with a single CTA that captures a signal. Tests value risk / demand at the top of the funnel. Cheapest and fastest; build in hours. Push the CTA up the skin-in-the-game ladder.
- **Concierge MVP:** You deliver the value proposition manually and openly, by hand, to real customers. The customer knows it's manual. Tests whether the value is real *and* teaches you the workflow you'd automate.
- **Wizard of Oz MVP:** The front-end looks automated, but a human does the work behind the curtain invisibly. The customer thinks it's automated. Tests demand and the real end-to-end experience without building the hard backend. Use when the experience must feel automated to be valid.
- **Single-feature MVP:** A real but ruthlessly narrow product that does one thing — the single core value action — and nothing else. Use when the value genuinely requires working software and can't be faked, *and* you've already retired demand risk more cheaply. Most expensive option; reach for it last.

**Decision heuristic:** Can you test demand *without building*? → Smoke test. Can you deliver value *by hand*? → Concierge. Must it *feel* automated? → Wizard of Oz. Must it *be* real software and the value can't be faked? → Single-feature MVP, but only after cheaper tests de-risked it.

**P5 — "Minimum" means minimum *learning vehicle*, not minimum *product*.** The MVP is the minimum thing that produces a valid signal about the riskiest assumption. Often that is not software at all.

**P6 — Pre-register the decision rule.** Before launching, write down: the hypothesis, the metric, the pass/fail threshold, the timeline, and the decision each outcome triggers (pivot / persevere / kill). A demand test with no pre-committed bar is not an experiment — it's a search for a flattering number.

**P7 — Timebox hard.** Default to days-to-weeks, not months. A smoke test should be live within a week; a concierge test should start with the next customer you can reach.

**P8 — Honest pretotyping respects the user.** Fake the product, never defraud the person. Pre-orders must be refundable and clearly labeled. Honor privacy and consent on captured data. A validation win built on a deception you couldn't defend to the customer is a liability, not traction.

---

### Step 0 — Establish ground truth (before scoping)

Resolve these inputs once, in a batch. If unknown, ask the user:

1. **The idea in one sentence:** what is being offered, to whom, to solve what problem?
2. **The target customer:** a *specific* persona or segment, not "everyone" — you need real people you can reach to test.
3. **The core value proposition:** the single most important benefit the customer is supposed to get.
4. **What's already built (if anything)** and how much has been invested — this calibrates how much sunk-cost bias you're fighting.
5. **Reachable channel to test customers:** can you get in front of 20–50 of the target persona this week? If not, finding the channel is the first task.
6. **Constraints:** budget for the test, timeline, regulatory/legal sensitivities, and what cannot be faked (e.g., regulated financial or medical claims).

### Step 1 — Extract the value hypotheses

Turn the idea into a small set of explicit, falsifiable assumptions.

1. **Decompose the idea into "we believe" statements.** Write each as a falsifiable claim: *"We believe that [specific customer] has [specific problem] painfully enough that they will [specific costly action] to solve it."*
2. **Separate the leap-of-faith assumptions from the safe ones.** Most assumptions are probably true (people use phones, businesses want to save money). One or two are the load-bearing leaps the whole thing collapses without. Name them explicitly.
3. **Write the single core value hypothesis in standard form:**
   > *We believe that [target customer] will [adopt / pay for / repeatedly use] [solution] because [problem] is acute enough that they will [costly action] — and we will know this is wrong if [observable behavioral failure].*

   The clause after "wrong if" is mandatory: a hypothesis you can't imagine being falsified isn't a hypothesis, it's a hope.

### Step 2 — Map and rate the risks (the Four Risks pass)

Score each of the four risks for *this specific idea* to find where to spend the validation budget.

1. **Rate each risk High / Medium / Low** on two axes: *likelihood it's fatal* and *how much it's currently un-tested*. Use the framework table from Core Principle P1.
   - **Value:** Is there real evidence anyone wants this, or just the founder's conviction? (Usually High and untested — default focus.)
   - **Usability:** Is the interaction novel or confusing? (Often deferrable until value is proven.)
   - **Feasibility:** Is there genuine technical uncertainty, or is it "just work"? (In 2026, usually Low — beware over-weighting it.)
   - **Viability:** Do the economics close — margin after costs (including AI inference), legal/channel constraints, does it fit the business model? (Sometimes the silent killer — a wanted product with broken unit economics.)
2. **Identify the single Riskiest Assumption Test (RAT) target.** This is the one assumption that is both most likely to be fatal and least validated. It is the *only* thing this round of experiment should test. Resisting the urge to test everything at once is the discipline here.
3. **Sequence the rest.** Order the remaining risks so each experiment retires the next-most-fatal unknown. You retire risks in series, cheapest-fatal-first — not all at once.

### Step 3 — Define the "minimum" (the scoping cut)

Cut scope to the smallest vehicle that produces a valid signal on the RAT target.

1. **List every feature/component anyone has proposed.** Get the full wish-list on the table.
2. **For each, ask: does this feature retire the risk under test in *this* experiment?** If no, it is out of scope for now — not "later," just *out of this experiment*. Be ruthless. The default answer is cut.
3. **Find the single core action** — the one interaction that delivers the core value — and scope to *only* that. Everything that surrounds, polishes, scales, or generalizes it is deferred.
4. **Challenge whether software is needed at all.** Can the value be delivered by hand (concierge) or faked (Wizard of Oz) for the test? If yes, that *is* the minimum — building software here is over-engineering.
5. **State the scope explicitly as in/out lists**, so "just one more feature" pressure has a written line to violate. The out-list is as important as the in-list.

### Step 4 — Design the experiment

Specify the test so precisely that the result can't be argued with afterward.

1. **Choose the MVP format** using the Core Principle P4 heuristic (smoke test / concierge / Wizard of Oz / single-feature), justified by the RAT target and what can be ethically faked.
2. **Choose the skin-in-the-game metric and push it up the ladder.** Decide the *costly action* that counts as a "yes," and make it cost enough to be meaningful (Core Principle P3). Prefer a deposit, pre-order, LOI, booked call, or handed-over data over a bare email. State *why* the chosen rung is high enough to be evidence.
3. **Set the pass/fail threshold *before* launch.** Define the metric and the number that means pass vs. fail, with reasoning tied to the eventual business. Example: *"We need ≥10% of landing-page visitors who reach the pricing CTA to click 'Reserve' and leave a card; below 4% we kill; 4–10% we iterate the offer and retest."* For B2B/LOI tests, the bar may be a small absolute count: *"3 of 10 target accounts signing a non-binding LOI."*
4. **Define the decision each outcome triggers:** persevere (pass → build toward the next risk), iterate (borderline → change one variable and retest), or kill (fail → stop, save the money). Write this down before launch.
5. **Specify the audience and channel.** Who exactly will you put this in front of, and how? Friends, family, and teammates are excluded from the signal — they are biased. You need representative target customers reached through a real channel.
6. **Set the timeline.** Default: days to weeks. State the launch date and the readout date. If the experiment can't be live within ~2 weeks, the scope is still too big — go back to Step 3.

### Step 5 — Run the experiment and collect behavioral data

1. **Build the artifact at minimum viable fidelity** — believable enough that a "no" means "no demand," not "your test looked broken." A janky landing page produces false negatives. But don't over-polish: the artifact needs to be credible, not beautiful.
2. **Instrument the costly action and the funnel step before it.** You must be able to distinguish "no demand" (people saw it and didn't act) from "broken funnel" (people couldn't find the CTA, or the page didn't load). At minimum: traffic source → page view → CTA impression → costly action completion.
3. **Hold the design fixed during the run.** Changing the offer, the page, or the audience mid-test contaminates the result. If you must change something, restart the clock and treat it as a new experiment. Don't merge pre- and post-change data.
4. **Collect behavior, not opinions.** If you talk to users during the test, their comments are color commentary — the score is what they *did*, not what they *said*. Log both, but decide on the behavior.

### Step 6 — Read the result and decide

1. **Compare the result to the pre-registered threshold.** Not to a vibe, not to "it's actually pretty good," not to a number you rationalized after seeing it. The number you wrote down in Step 4 is the bar.
2. **Rule out false negatives before killing.** Before declaring "no demand," verify:
   - The artifact was believable (not obviously broken or unprofessional).
   - The audience was representative (not the wrong segment).
   - The funnel worked (people reached the CTA and could act).
   - Traffic volume was sufficient for a directional read (not 11 visitors).
3. **Make the pre-committed decision:**
   - **Persevere (pass):** The riskiest assumption survived. Move to the next risk in your sequence (Step 2, item 3). Do not jump to building the full product — retire the next risk with the next cheapest test.
   - **Iterate (borderline):** Change exactly one variable (the offer, the price, the audience, the format) and retest. Don't change everything at once — you won't know what moved the result.
   - **Kill (fail):** Stop. A kill is a *successful* experiment — it saved you from building something nobody wanted. Record what you learned: which assumption was fatal, why, and what (if anything) you'd test differently next time.
4. **Record the decision in a decision log.** Hypothesis, test design, metric vs. threshold, decision, and transferable learning. This is institutional memory and future fundraising evidence.

---

## Pitfalls

### The most common and most expensive mistakes

| Pitfall | What it looks like | How to avoid it |
|---|---|---|
| **Testing opinions instead of behavior** | "We talked to 20 people and they all said they'd use it" | A verbal "yes" costs nothing and predicts nothing. Design the experiment so "interested" requires a costly action — a deposit, a booked call, handed-over data. See Skin-in-the-Game ladder. |
| **The Mom Test failure** | Friends and family validate your idea because they care about you, not because they're customers | Ask about *past behavior* ("how did you solve this last time?"), not future intent. Exclude warm contacts from the signal. Read *The Mom Test* (Rob Fitzpatrick) for question technique. |
| **Building the single-feature MVP first** | Jumping straight to "real software" MVP | Exhaust cheaper formats first — could a concierge or Wizard of Oz answer the same question this week? Code is the most expensive way to test a hypothesis. |
| **No pre-set threshold (moving goalposts)** | "That's actually a decent result" decided *after* seeing data | Pre-register pass/fail in Step 4. HARKing (deciding success after the fact) invalidates the experiment. |
| **Over-rotating on one loud detractor/fan** | One strong reaction drives the decision | Look at the distribution of *behavior*, not the loudest voice. A single anecdote is hypothesis-generating, not conclusive. |
| **Confusing a pivot with a kill** | Throwing out the whole idea when one assumption failed | Isolate *which* assumption failed. Change only that and retest (pivot) before abandoning everything. |
| **Testing the wrong assumption** | Spending weeks testing feasibility when value is unproven | Always identify the RAT target (Step 2) before designing the experiment (Step 4). Value Risk is the default killer. |
| **Scope creep during the build** | "Just one more feature" keeps appearing | The in/out list from Step 3 is your defense. Every feature must justify its existence by the risk it retires *in this experiment*. |
| **False negative from a janky artifact** | "Nobody wanted it" — but the landing page looked broken | The artifact must be believable enough that a "no" means "no demand," not "your test looked broken." Invest in minimum viable fidelity. |
| **Reading noise from tiny traffic** | "We got 11 visitors and 2 signed up — that's 18%!" | 11 visitors is not a verdict. Either solve the channel problem first or use a higher-touch format where each data point carries more weight. |

### The ethics and legality of smoke testing

Cheap demand tests deliberately advertise something that doesn't fully exist yet, which creates real obligations — get this wrong and a "validated" idea becomes a refund nightmare or a legal problem.

- **Never take non-refundable money for something you can't deliver.** Use clearly-labeled *refundable* deposits, pre-orders, or "reserve your spot" language. If you collect payment, be able and ready to refund every cent.
- **Don't misrepresent identity or make false claims**, especially in regulated domains (health, finance, safety). "Coming soon" is honest; a fake clinical or financial guarantee is not.
- **Respect data and consent.** Captured emails and data are subject to privacy law and the promise you made when collecting them; don't repurpose them, and honor opt-outs.
- **Disclose appropriately for concierge/Wizard of Oz.** Doing work by hand behind the scenes is fine; misleading a customer about *material* facts that affect their decision or safety is not. When in doubt, the test should be one you'd be comfortable explaining to the customer afterward.

### Edge cases

**B2B / enterprise (low volume, high value):** Landing-page conversion math doesn't apply when there are 30 possible customers, each worth six figures. The skin-in-the-game signal shifts to **Letters of Intent**, paid pilots, and design-partner agreements. The "sample" is tiny, so read it qualitatively: *3 of 10 target accounts signing a non-binding LOI* is strong validation; a high pass bar on a small absolute count, not a percentage on thousands of visitors.

**Regulated, safety-critical, or hardware products:** Some value cannot be ethically or legally faked (medical claims, financial products, anything physical that could harm). Validate demand and willingness to pay abstractly (smoke test for interest, pre-orders, LOIs) while being scrupulous not to make a claim or deliver a service you're not authorized to. Feasibility and viability risk may legitimately need a real technical/regulatory spike earlier than usual — but still test demand in parallel, not after.

**Genuinely novel product (no comparison, hard to describe):** When customers can't evaluate the idea because nothing like it exists, a static landing page under-tests it. Use a **concierge or Wizard of Oz** format so people experience the value rather than imagining it from a description, and weight observed re-engagement heavily.

**Very low reachable traffic:** If you can't get enough representative customers in front of the test for even a directional read, the bottleneck is *channel*, not idea. Solve distribution first (find or borrow an audience), or use a higher-touch format (concierge with a handful of real customers) where each data point carries more weight. Don't read noise from 11 visitors as a verdict.

**Founder is emotionally committed / heavy sunk cost:** When months and money are already invested, every result gets rationalized as positive. Counter it by pre-registering the kill threshold in writing *before* the test, ideally witnessed by a co-founder or advisor, and by framing a kill as the experiment *succeeding* at saving future waste. Name the sunk-cost bias explicitly.

---

## Verification

Before declaring the MVP scope minimized and the risk test sound, confirm every applicable item. Treat any unchecked box as a blocking defect — fix it or flag it explicitly.

**Hypothesis & risk targeting**
- [ ] The core value hypothesis is written in standard, *falsifiable* form, including an explicit "we'll know it's wrong if [observable behavior]" clause.
- [ ] All four risks (Value, Usability, Feasibility, Viability) were rated, and the single **Riskiest Assumption** to test this round is named — with Value Risk explicitly considered as the default focus.
- [ ] The experiment tests **one** assumption (the RAT target), not several at once; the remaining risks are sequenced for later cheap tests.

**Scope minimization**
- [ ] Scope is expressed as explicit **in / out lists**, and every in-scope element demonstrably retires the risk under test.
- [ ] The "could we deliver this by hand or fake it?" question was asked; software is included *only* if the value genuinely can't be faked for the test.
- [ ] The scope is the **minimum learning vehicle**, not a small complete product — no feature survives that isn't load-bearing for the hypothesis.

**Experiment design (behavioral & honest)**
- [ ] The MVP **format** (smoke / concierge / Wizard of Oz / single-feature) is justified by the RAT target and by what can be ethically faked.
- [ ] The success metric is a **costly action** (behavior), pushed up the Skin-in-the-Game ladder as far as the context allows — not a free opinion, like, or bare email — with a stated reason the chosen rung is meaningful.
- [ ] A **pass/fail threshold** and the **decision each outcome triggers** (pivot / persevere / kill) were written down *before* launch, tied to eventual business reality.
- [ ] The test audience is **representative target customers** recruited through a real channel; friends/family/team are excluded from the signal.
- [ ] The artifact's fidelity is high enough to be **believable** (no false negative from a janky test) but no more polished than necessary.

**Execution & integrity**
- [ ] The experiment is **timeboxed to days–weeks**, not months, and launched within that box.
- [ ] The **costly action and the funnel step before it** are instrumented, so "no demand" is distinguishable from "broken funnel."
- [ ] The design was **held fixed** during the run; mid-test changes restarted the clock rather than being read as one result.
- [ ] The test is **ethically and legally clean**: refundable/clearly-labeled pre-orders, no false claims, consented data handling, nothing you couldn't explain to the customer.

**Readout & decision**
- [ ] The result was judged against the **pre-registered threshold** on the **behavioral** metric — not on encouraging comments or a number rationalized after the fact.
- [ ] False-negative causes (unbelievable artifact, wrong audience, broken funnel, too little traffic) were **ruled out** before any "kill" decision.
- [ ] The **pre-committed decision** (pivot / persevere / kill) was made, with a kill treated as a successful, money-saving outcome rather than a failure.
- [ ] The hypothesis, test, metric-vs-threshold, decision, and transferable learning are recorded in a **decision log** for institutional memory and future fundraising evidence.

> **Final gut-check — the "would they cry?" test** (Savoia's spirit): for every "yes" you collected, ask *"did this person give up something they'd miss — money, real time, their data, their name on an LOI?"* If the strongest signal you have cost the user nothing, you have measured politeness, not demand. Either push the next test up the skin-in-the-game ladder until a "yes" costs something real, or don't yet believe the idea is validated. The cheapest possible mistake in a startup is killing a bad idea this week; the most expensive is building it for a year first.
