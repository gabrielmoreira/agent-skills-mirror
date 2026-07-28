# Playbook B — Existing site, with data

**You are here if:** GSC has real rows. Something ranks, something earns clicks, and the
question is where to point effort next.

**The one thing to understand:** with data, **what to double down on is derived, not chosen.**
Your own Search Console already knows which page shapes work for your audience and which
don't. Most sites never read it that way and instead pick topics from intuition, competitor
blogs, or keyword-tool volume — all of which are guesses about a question you can answer
exactly.

The sequence below is: read → find the winner → extract the shape → diagnose → compound →
protect → verify.

---

## 1. Read your data properly

Pull a 28-day window ending **3 days back** (GSC lags 2–3 days). You need three views:

- **Page dimension** — clicks, impressions, CTR, position per page. This ranks your work.
- **Query dimension** — the same, per query.
- **Query mix for a specific page** — queries filtered to one page. This is the view that
  prevents the most common expensive mistake (see §4).

Read `measurement.md` before trusting any of it. GSC has specific traps — impression-weighted
position, anonymized long tails, apex vs www counted separately — that produce confident wrong
conclusions.

## 2. Find your breadwinner

**The breadwinner is the single page earning ≥30% of your clicks.** Most sites that work have
one. On one property it was ~45% of all blog clicks, with the next page at about a third of that.

**Concentration is not a problem to fix.** The instinct to "diversify away from dependence on
one page" is wrong at this stage and expensive: it moves effort off the one asset that is
demonstrably working, onto pages that have not earned it. **Compound the winner first.**
Breadth gets attention only once the winner is fully compounded.

## 3. Extract your winning archetypes — this is the real answer to "what do we double down on"

Do not double down on a *page*. Double down on the **shape** that page belongs to, then repeat
the shape.

Sort your pages by clicks and CTR and ask what the top ones have structurally in common — who
the searcher is, what they were doing, what form the page takes. Then do the same for the
bottom. You are looking for repeatable *templates*, not topics.

Worked example — the archetypes one property extracted from a 90-day Search Console read:

**Winners:**

| Archetype | Evidence |
|---|---|
| **Person-attached emerging convention** | The site's best page by a wide margin at ~2.3% CTR. A technique named after a known person, caught early, compounds for months. |
| **"[Tool] for [profession]" guides** | Highest-CTR template on the site: 3.0%, 4.1%, 4.8% across different professions. Builder-mid-workflow intent, natural funnel. Repeatable — new professions keep appearing. |
| **Named-technique guides you can own** | A technique guide ranked well, and the query for its **PDF** converted at 12.3% CTR — readers explicitly asking for a downloadable next step. When a technique guide ships, add a checklist/PDF CTA. |

**Losers — do not pick these even when they look emerging and rankable:**

| Shape | CTR |
|---|---|
| News / announcement ("Google kills X") | 0.4% |
| Launch guide for a new product | 0.2% |
| "Best [category] 2026" roundup | **0.04%** |

That last table is GSC empirically confirming the CTA test: massive impressions, near-zero
clicks, no funnel value. A news reader has no next step.

**Your archetypes will differ.** The transferable part is the method — read your own top and
bottom pages for structural commonality, write the list down, and check every future candidate
against it.

## 4. Diagnose before you touch anything

A page with impressions and few clicks is one of **three** different problems with three
different treatments. Getting this wrong wastes the effort and can lose you the page.

Pull the page's **query mix**, then classify:

### (a) Not broken — leave it alone

The single most common misdiagnosis. Four query families score ~zero clicks **by design**:

- **LLM fan-out** — an assistant decomposed a question into sub-searches. No human, no click,
  ever. One verified templated competitor-evaluation query family recorded **0% CTR** while
  ranking position 4.7–5.8, which means AI assistants are finding and citing the pages. That is
  a win that scores zero forever.
- **Competitor-navigational** — "[competitor] by [parent company]" means they want the
  competitor's own site. Unwinnable.
- **Brand-navigational** — your homepage should win it, not this page.
- **Anonymized tail** — GSC hides long-tail queries. A page whose *visible* impressions are
  <10% of its total is undiagnosable; one page's visible impressions were well under 1% of the real total.

**Never "fix", retitle, or delete these, and never count them against a page.** Screening
first is what stops a clicks-based KPI from lying to you.

### (b) Snippet-limited — the page ranks, the listing doesn't sell

Query mix is **human**, position is decent (≤15), CTR is poor, and the title/H1/meta **fail to
name the exact query the page ranks for.**

The canonical case: a page ranking ~position 8.5 for a one-word compound term whose title never
contained that word.

**Treatment, roughly by leverage:** query-match the title / H1 / meta description to the exact
human query · add a fresh PAA-style FAQ in question-form heading with a tight extractable
answer · tighten the actual answer into the first 30% of the page · add honest structured data.

### (c) Position-limited — the listing is fine, the rank isn't

CTR is already healthy (say >8%) but position sits at 5–7. Editing the page does almost
nothing here; the constraint is authority, not copy.

**Treatment:**
- **Internal link equity.** One contextual, intent-matched link per cycle from a
  high-impression page of yours *into* the target, with descriptive anchor text. This is the
  highest-leverage move available when a winner is position-limited, and it isn't on the page
  at all. Run it as a campaign: work down your high-impression pages one at a time, then log
  it **exhausted** when no untouched source page remains.
- **Depth a thin competitor cannot match.** Interactive or tool-like assets, honest comparison
  tables, first-party specifics, real diagrams. This is what you spend the winner's cooldown
  windows building.

## 5. Protect the winner — canary and cooldowns

**A winning page is production.** Treat edits to it the way you would treat a deploy.

- **Canary, every cycle:** if the breadwinner's position drops ≥3, or its clicks drop >30%
  window-over-window, **stop and investigate before doing anything else**, and make no edits to
  it that cycle.
- **Cooldowns:** breadwinner **14 days**, every other live page **7 days** between edits. One
  edit per page per window — otherwise you cannot attribute the result to the change, and you
  lose the ability to learn anything.
- A page inside its cooldown is off-limits even for a "small" tweak. Route the idea elsewhere
  or hold it.
- **It is correct to leave clicks on the table rather than perturb the page that earns half of
  them.**

## 6. Verify — a ship is not an outcome

Every change gets a scheduled verdict, or you are just doing activity.

Stamp each applied change with the date and a **verify-after date 14 days out**. When it comes
due, compare that page's clicks **7 days after** vs **7 days before** the change. If a page
with real *human* traffic dropped **>30%**, that is a **revert candidate** — name the change,
the page, the numbers, and the exact commit. Otherwise mark it verified and move on.

An applied change that was never verified is an open loop, not a done item.

For a newly shipped article, two extra checks at ~4 weeks: did its target query family
actually form (near-zero → refresh or merge it into the pillar), and did it *hurt* the pillar
(pillar position degraded >2 while the new page absorbs the pillar's old queries → consolidate).

## 7. Keep a front open

A mature cluster still saturates. Once you own every intent worth owning in a territory,
further effort there returns little — that is when a site plateaus despite consistent output.
The answer is not more pages in the saturated cluster; it is **a new front**.

Go back to `emerging-terms.md` and hunt. A site with authority hunting an emerging term is the
strongest position in this entire method: you get the thin-competition window *and* the domain
strength. That is how one property's second emerging term landed at #1 site clicks within 7 days
of launch, while its first term was still being defended.

---

## The cycle, compressed

1. Reconcile what is actually live against what you think is live (state drifts; verify against
   the live site, not your notes).
2. Read the score. One KPI, everything else labeled a diagnostic.
3. Check the canary; respect cooldowns.
4. Pick the single highest click-opportunity move; screen it for human intent first.
5. Run the gates: cannibalization, CTA, fact-check any new technical specific against a primary
   source, queue depth.
6. Ship one thing. Stamp it with a verify date.
7. When the cluster saturates, open a new front.

To make this run without you, see `operationalize.md`.
