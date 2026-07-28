# Hunting emerging terms — the wedge

**This is the highest-leverage skill in the whole method**, and the only one that works from
zero authority. Both playbooks need it: Playbook A lives on it entirely, and a site with data
uses it to open the next front once a cluster saturates.

**Why it works:** ranking is a competition. On an established term you are competing against
domains with years of authority and you lose. On a term that surfaced three weeks ago, nobody
has authority yet — the SERP is decided by who shows up with the best page first. Authority
stops being the deciding variable. That window closes as the term matures, so **value is
front-loaded: ship while you own it.**

---

## The pattern to look for

The **person-attached emerging-artifact pattern** produced one property's crown-jewel page —
its best performer by a wide margin at ~2.3% CTR.

The shape:

> A **new term, tool, file format, or convention** — usually attached to a **named person or
> artifact** — that appeared or spiked in the last ~30 days, where people have started asking
> "what is X" / "how do I X", and no dedicated well-optimized article ranks for it yet.

Person-attached and artifact-attached terms are the strongest signal because they are
**nameable**: people search the exact string, which means the intent is unambiguous and a
single page can own it.

---

## Where to hunt — sourcing order matters

Run these **in this order**, every hunt. The order is not cosmetic; it was derived from a
documented failure.

### 1. Your own curated stream — FIRST, and not optional

Whatever you already save because it interests you: bookmarks, saved threads, a reading list,
a Slack channel you dump links in. This is the freshest, highest-signal corpus you have, and
it is where a term shift shows up before it is anywhere else.

**The named failure:** an automated SEO process ran for nine days grounding only on its own
pages and its own Search Console data, shuffling internal links, while its head term slipped to
page 2. The entire industry term shift it needed to react to was sitting unread in the owner's
own saved bookmarks, added days earlier. The process had the answer and never looked at it.

**Grounding on your own data is a closed loop.** It produces internal reshuffles that cannot
move a term you do not yet own.

### 2. Repo and release feeds — the outside gap

GitHub trending repos and recent releases in your territory; X threads and framings from the
last ~2 weeks. This surfaces new tools and new terminology before search volume exists.

### 3. Social listening — corroboration, not discovery

One input, not the only one. Pull what people are actually saying and asking across Reddit, X,
Hacker News, and YouTube over the last ~30 days. Use it to confirm intent is forming and to find
the exact phrasing people use — the phrasing matters more than the topic, because it is what
they will type.

*Practical note:* whatever tool you use for this, broad topics tend to be slow or time out. When
that happens, drop to a few scoped web searches rather than re-running the broad pull.

### 4. Diff against your own coverage

grep your existing pages. **The delta is the target.** New framings, new tools, term shifts,
uncovered sub-questions. Cite the specific bookmark, repo, or thread that motivated the pick,
so the source trail is auditable and a future you can tell a real signal from a hunch.

---

## The validation gates — ALL must pass

A candidate that fails any one of these is dropped, and dropping is the common outcome. Log
rejections with reasons; a rejected-candidate list stops you re-pitching the same loser.

| Gate | Test | Fail = drop |
|---|---|---|
| **Emerging** | Term surfaced or spiked in the last ~30 days | An old term means an established SERP |
| **Intent forming** | People visibly asking "what is X" / "how to X" | A term nobody searches is a blog post, not SEO |
| **Rankable** | No dedicated, well-optimized article dominating | If one exists, you are back to authority competition |
| **In-domain** | Your audience would genuinely search this | Off-domain traffic does not convert and dilutes the site |
| **You can answer it** | You have first-party substance, not a rewrite | A page anyone could regenerate will not hold |
| **CTA test** | The reader has a native next step into your funnel | "Close the tab" = fail, no exceptions |
| **No cannibalization** | No page of yours already ranks pos <15 for it | You would split your own click equity — link instead |

### The cannibalization pre-check, concretely

Before committing to a target term, query GSC by **page** dimension filtered to that term. If
one of your own pages already ranks **position <15**, do not build a second page for it. Pick
a distinct long-tail the existing page does not own, and **link to** the existing page instead
of competing with it. Two of your pages on one query is not coverage, it is splitting.

---

## Validating demand when there is no volume data yet

The trap: keyword tools show ~0 volume for a genuinely emerging term, because volume data lags
weeks to months. **Absence of volume is not absence of demand** at this stage — it is the
signal you are early.

So validate on **leading indicators** instead:
- Are related queries already appearing in your own GSC impressions? (Even a handful.)
- Is engagement visible in the raw discourse — thread replies, repo stars, video comments?
- Is the term being used *as a term* by more than one independent person? (One person's coinage
  is not a term yet; three is a wave.)

Then let day-7 / day-21 measurement settle it (see `cold-start.md`).

---

## Cadence

Run the hunt on a **weekly** rhythm, not continuously. Emerging terms do not appear daily, and
hunting more often just produces forced picks.

**A week where nothing clears the bar is a valid, correct outcome.** Log "no qualifying
candidate" with the rejected list and why. A forced thin article actively hurts the cluster it
attaches to — it is worse than nothing, not neutral.

**Saturation cooldown:** once a topic's hunt reads "saturated" (you already own every intent
worth owning), do not re-mine it for ~14 days. Saturation is a healthy steady state, not a
shortfall. One property read saturated across seven consecutive runs; the correct response was
to stop paying for the same answer, not to invent new angles.

---

## After it lands

Emerging terms mature. Watch for the **graduation tripwire**: when the term starts throwing
real click volume and its family stops widening, the land-grab is over and the work shifts to
compounding and conversion. The computable version of that flip is in `measurement.md`.
