# Measurement — which metric, and the traps

Read this before trusting any number. Most stalled SEO efforts are not doing the wrong work;
they are grading it with the wrong metric, and the metric quietly points them at the wrong
work forever.

---

## The regime question: position or clicks?

**Score an emerging term on POSITION. Score a mature one on CLICKS.** Getting this backwards
is the single most expensive metric error in the method, and it fails in both directions.

### Why clicks is the wrong score for an emerging term

One property's emerging head term went from **zero impressions to substantial weekly volume in
about four weeks**, while its rank sat at ~position 7 the whole time. Graded on clicks that
reads "barely any traffic, meh" — and tells you to abandon the land-grab **exactly as the
ground is becoming valuable**. You never rank an emerging keyword if you wait for its clicks
first.

While land-grabbing, score on:
- **exact-head position** (target: hold ≤3), and
- **family footprint** — how many queries in the term's family you rank for, and the
  impressions they throw.

Clicks are demoted to a **graduation tripwire**: when the term starts throwing real click
volume, it has matured, and *that* is the trigger to shift weight toward conversion.

### Why position is the wrong score for a mature page

One property had a page at **position 6.6** — healthy by any rank metric — converting
**0.53%**, and it was the site's largest impression generator by 2×. It sat untouched for a
month because nothing scored it as a failure. A rising position on a page nobody clicks is not
progress.

Once mature, score on **clicks**, and keep position only as a diagnostic for trend continuity.
Say so explicitly wherever you record it, or the number will start deciding work again.

### The flip gate — make it computable, not a vibe

"The families are all owned" cannot be read off GSC directly (GSC only shows queries you
already appear for). So judge saturation with three numbers, and state all three every time
you review:

> Flip from land-grab to harvest when **`family_top3_share` ≥ 85%** AND **`family_queries` grew
> <10% vs the prior read** AND **`family_weak` ≤ 2**.
>
> - `family_top3_share` — share of family *impressions* sitting at position ≤3
> - `family_queries` — count of family queries you rank for
> - `family_weak` — family queries at position >5 with ≥50 impressions (the improvement backlog)

Until all three hold, stay in land-grab. Written down as numbers, the regime is never
re-argued from scratch; written as prose, it softens into a vibe within three reviews.

---

## The four query families that never click

Screen every low-CTR page against these **before** calling it a problem. This is what stops a
clicks KPI from lying to you.

1. **LLM fan-out.** An AI assistant decomposed a user's question into sub-searches. There is no
   human in the loop, so these score zero clicks *by design, permanently*. A verified templated
   competitor-evaluation query family recorded **0% CTR** at position 4.7–5.8. Ranking there
   means assistants are pulling your page as a source. **It is a win that will look like failure
   to anyone grading on clicks.** Track it on an AI-visibility scorecard instead, never on the
   clicks KPI.
2. **Competitor-navigational.** "[competitor] by [parent company]" — the user wants the
   competitor's own site. Unwinnable, no matter what you do to the page.
3. **Brand-navigational.** Your own brand terms where the homepage should win. A blog page
   "underperforming" on your brand name is correct behavior.
4. **Anonymized tail.** GSC withholds long-tail queries for privacy. When a page's *visible*
   impressions are <10% of its total, its tail is undiagnosable — one page's visible impressions
   were well under 1% of its real total. You cannot diagnose what you cannot see.

**Never delete, retitle, or count these against a page.** Write your own verified list down, or
every review will rediscover and re-triage the same non-problems.

---

## GSC gotchas that produce false conclusions

| Trap | What actually happens | What to do |
|---|---|---|
| **Data lag** | GSC is 2–3 days behind | End every window 3 days back |
| **Position is impression-weighted** | A great position on 12 impressions is real but meaningless | Ignore rows under ~50 impressions |
| **Query clicks < page clicks** | Anonymized queries are missing from the query dimension | Trust the **page** dimension for totals |
| **apex vs www counted separately** | Both hosts get indexed; each shows partial numbers | Fold them together before reporting |
| **Metric mis-binding** | Reporting page-dim total where exact-query was meant | Bind each metric to a named number in writing. One real dashboard spiked 10× from this. |
| **Cached reports** | A saved report is a snapshot, not the truth | Always re-query the live system |

---

## Naming your KPI honestly

Pick **one** KPI. Label everything else a diagnostic, in writing, or it will start deciding
work.

Then name the KPI's **successor** and park it honestly. On one property the chain is
clicks → signups, and signups are *not* instrumented because Google referrers are
path-stripped, so a signup cannot be attributed to a blog page from referrer data alone. That
is written into the spec along with the instruction: **do not fake it from what GSC can
reach.** An honestly-parked metric beats a fabricated one, and it tells the next person what
to build.

---

## Attribution hygiene

You can only learn from a change you can attribute.

- **One edit per page per window.** Two changes inside 14 days and neither result is readable.
- **Cooldowns:** breadwinner 14 days, other live pages 7 days.
- **An unmerged PR is not live.** It cannot rank or pass link equity. While anything is
  unmerged, a flat position is **expected**, not evidence of failure — and definitely not
  grounds for a strategy change. Count and surface unmerged work every cycle.
- **Stamp every change** with its applied date and a verify-after date, and actually check it.
