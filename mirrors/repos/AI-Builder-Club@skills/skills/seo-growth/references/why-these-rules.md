# Why these rules exist

Every rule in this skill came from a production failure or a production result on two content
properties under continuous, instrumented operation.

**On the numbers below:** absolute traffic figures are withheld. Ratios, CTRs, positions, and
thresholds are stated as actually observed, because those are the parts that transfer. A rule
without its origin is just an opinion, so each one names the specific thing that went wrong or
right.

---

## Emerging-term targeting works, and it works twice

Two separate emerging terms were landed on the same property using the same method, months
apart. The second is the cleaner demonstration: the pillar page went live and became **the
site's most-clicked page within 7 days**, holding **position 1.5 at ~39% CTR** on the exact
head term.

None of that is achievable on an established term from a mid-authority domain. It is achievable
on a three-week-old term because authority has not yet decided the SERP.

**The first term's curve is the other half of the lesson:** it went from *zero* impressions to
substantial weekly volume in about four weeks, while the site's rank sat at **~position 7 the
entire time**. Graded on clicks, that reads as failure. Graded on position and footprint, it
reads as what it was — a term maturing underneath a page already in place to catch it.

**Value is front-loaded.** Once a competitor with real authority began framing the same term,
position and CTR started normalizing down even as total impressions climbed. The window is real
and it closes.

**Day-7 read on the second term**, worth internalizing: position went **1.5 → 2.75** while
clicks and the query family both roughly doubled. The position metric got *worse* while the
term got substantially more valuable. That is why the regime flip in `measurement.md` is three
numbers, not one.

## Winning archetypes are extracted, not chosen

A 90-day Search Console read on one property produced three repeatable winning shapes and three
repeatable losers. The shapes mattered far more than the topics.

**Winners:**

| Archetype | What the data showed |
|---|---|
| **Person-attached emerging convention** | The site's best page by a wide margin, at **~2.3% CTR**. A technique named after a known person, caught early, compounds for months. |
| **"[Tool] for [profession]" guides** | Highest-CTR template on the site: **3.0%**, **4.1%**, **4.8%** across different professions. Builder-mid-workflow intent with a native next step. Repeatable, because new professions keep appearing. |
| **Named-technique guide + lead magnet** | A technique guide ranked well, and the query for its *PDF* converted at **12.3% CTR** — readers explicitly asking for a downloadable next step. |

**Losers — high impressions, no business:**

| Shape | CTR |
|---|---|
| News / "Google kills X" | 0.4% |
| New-product launch guide | 0.2% |
| "Best [category] 2026" roundup | **0.04%** |

All three pulled enormous impression volume. That is the trap: impressions feel like traction.
All three fail the CTA test — a news reader has no next step — and Search Console confirmed it
empirically before anyone reasoned it out.

## Concentration is health, not risk

On Property B a single page earned roughly **45% of all blog clicks**, with the
next page at about a third of that. The instinct to diversify away from that dependence was
wrong, and acting on it would have been expensive.

Compounding the winner instead produced **eight consecutive period-over-period rises** in blog
clicks. Over the same stretch non-brand clicks grew steadily while brand clicks stayed flat —
the mix shifted from overwhelmingly brand toward genuinely earned traffic. Non-brand is the
growth signal; total traffic can look healthy while hiding that nothing new is being won.

**The winner turned out to be position-limited, not snippet-limited** — CTR already **~9.5%** at
roughly position 5.6. No amount of title editing would have helped. The lever was inbound
internal links and depth, which is why that distinction gets its own section in `with-data.md`.

## Position is the wrong score for a mature page

One page sat at **position 6.6** converting **0.53%**, and it was the property's largest
impression generator by 2×. It went untouched for a month because no metric in use scored it as
a failure. A rising position on a page nobody clicks is not progress.

After its title and description were re-pointed at the specific angle only that property could
credibly own, CTR moved **0.53% → 0.83%** on ~19% more impressions.

**That was recorded as a hypothesis, not a fix** — the measurement window straddled the change
and ~89% of the page's impressions were anonymized by Search Console, so the honest verdict was
deferred to a clean scheduled recheck. That discipline is as much the lesson as the result.

## The CTR bottleneck is usually a naming problem

Across one property's top pages, a very large impression base converted at well under 1%. The
constraint was not ranking. It was that **titles did not contain the queries the pages ranked
for.** Canonical case: a page ranking around **position 8.5** for a one-word compound term whose
title never contained that word.

## LLM fan-out scores zero clicks by design

A templated competitor-evaluation query family ran site-wide at **0% CTR** while ranking at
**position 4.7–5.8**.

These are AI assistants decomposing a user's question into sub-searches. There is no human in
the loop to click. Ranking there means assistants are pulling the pages as sources: a genuine
win that looks like total failure to anyone grading on clicks, and that a well-meaning
optimization pass will try to "fix."

Related and equally important: pages whose *visible* impressions are a tiny fraction of the
total are undiagnosable. One page's visible impressions were **well under 1%** of its actual
total; others ran 89–93% anonymized. You cannot diagnose what the tool will not show you.

## The closed-loop failure

An automated SEO process ran for nine days doing internal improvements only — reshuffling links,
tightening pages — grounding entirely on its own pages and its own Search Console data. Its head
term **slipped to page 2.**

The industry-wide term shift it needed to react to had been sitting in the owner's own saved
bookmarks the whole time, unread: two widely-shared posts had already announced the migration
from the old term to a new one. The process had access to the answer and never looked outside
itself.

**Grounding on your own data is a closed loop.** It produces internal reshuffles that cannot move
a term you do not yet own. The fix — curated stream first, always — is why `emerging-terms.md`
specifies a sourcing *order* rather than a list of sources. The follow-on term, hunted properly,
landed at #1 site clicks within a week.

## The state-drift failure

Five articles shipped live and nobody updated their status in the tracking system. Three
consecutive automated runs reported *"nothing shipped"* and counted five phantom drafts — for two
days **after** the articles were in production. Worse, a cannibalization audit ran against that
stale mirror, so its fixes were computed against pages that no longer matched reality and changed
nothing.

**Fix:** reconcile against the live system before trusting internal state, every run, keyed on
**URL rather than title** — titles routinely get rewritten at publish time, so title-matching
fails silently exactly when it matters.

## The fabrication failure

A content-enrichment pass "grounded" a new FAQ in the target page's own existing body and shipped
**four wrong technical facts** — CLI flags that did not exist. The page's body was stale, so
grounding in it laundered the error into a freshly query-targeted answer, which is precisely
where a wrong specific does the most damage: it misleads the exact searcher you are trying to
win.

**Fix:** any *new* verifiable specific — a flag, env var, parameter, default, version behavior,
price — must be checked against a primary source in the same run, with the doc URL recorded.
Grounding in your own existing content is not verification.
