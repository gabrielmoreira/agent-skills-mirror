# End-to-End Research — Worked Examples

> **Data disclaimer:** the concrete values in these examples (prices, versions, counts, dates) are **illustrative of format and method only**. They show what a correct run looks like — never reuse a figure from this file as evidence in a real deliverable.

---

## Example 1 — Technology evaluation: vector store for a solo-dev RAG feature

**Input:** "Research vector DB options for my RAG feature — Node/TS app, ~5M vectors, self-host or cheap managed, minimal ops. I want a recommendation."

### Intake

```
QUESTION: Which vector store best fits a Node/TS RAG feature at ~5M vectors for a solo dev minimizing ops?
DECISION SUPPORTED: pick one and integrate this month
SUCCESS CRITERIA: ranked shortlist of 3 with tradeoffs + one recommendation with exit cost
CONSTRAINTS: Node/TS client required; budget <$50/mo managed OR self-host on one box
RECENCY WINDOW: ≤12 months (this space moves fast)
DEPTH TIER: standard
OUT OF SCOPE: embedding model choice; chunking strategy
```

### Plan (excerpt)

- SQ1 — Which stores are credible candidates for this scale/stack? (docs, comparison threads)
- SQ2 — Does each fit the constraints (TS client, 5M vectors, ops burden)? (T1 docs per candidate)
- SQ3 — What do practitioners report going wrong at this scale? (adversarial; HN/Reddit via `multi-platform-agent-reach`)
- SQ4 — What's the exit cost per candidate? (export paths, API surface)

```
Q1.1 [broad]       vector database self-hosted small scale 2026
Q1.2 [narrow]      pgvector vs qdrant vs dedicated 5 million vectors
Q3.1 [adversarial] "moved off" OR "migrated away" pgvector qdrant problems
Q3.2 [platform]    HN: pgvector (12mo, top threads) — comment gold
```

### Source registry (excerpt)

| id | source | tier | group | notes |
|---|---|---|---|---|
| S-001 | pgvector README + docs | T1 | G1 | capability ground truth |
| S-002 | Qdrant docs — capacity planning | T1 | G2 | |
| S-004 | HN thread: "pgvector in production" (dated, 140 comments) | T3 | G3 | practitioner failure reports |
| S-006 | Vendor X benchmark blog | T3 | G4 | `conflict_of_interest: vendor benchmark of own product` |

### Claims table (excerpt)

| id | statement | type | grade | evidence |
|---|---|---|---|---|
| C-001 | pgvector supports HNSW indexes; 5M vectors is within documented usage | fact | B | S-001 supports (docs quote) |
| C-002 | Practitioners report index build memory spikes at multi-million scale on default settings | claim | C | S-004 supports (2 independent commenters, same thread → still one group; flagged single-group) |
| C-003 | Vendor X is 4× faster than pgvector | claim | **D** | S-006 supports — downgraded: vendor benchmark, defaults for competitor, no replication |
| C-004 | Choosing pgvector adds zero new infrastructure if Postgres is already deployed | inference | B | reasoned from S-001 + user's stack |

### Gate notes

- C-003 nearly shipped at C; §7 benchmark rules forced D. It appears in the memo only as "vendor-claimed, unverified."
- C-002 needed a second independence group; a dated engineering blog post (S-009) was found on a follow-up query, raising it to B.

### Deliverable excerpt (decision memo)

> **Recommendation:** pgvector (confidence MODERATE-HIGH). You already run Postgres; 5M vectors is inside its documented envelope [C-001], and the ops cost of a second datastore is the constraint that dominates for a solo dev [C-004]. **What would change this:** >20M vectors, heavy payload-filtered queries, or sub-10ms P99 requirements → Qdrant. **Exit cost:** low — vectors export via SQL; embedding regeneration is the real cost and is store-independent.

---

## Example 2 — Competitive snapshot: game-analytics vendor

**Input:** "Competitive snapshot of GameAnalytics — I'm deciding whether to build my own telemetry or use theirs."

### Intake (condensed)

Standard tier. Success criteria: snapshot per §5 checklist + build-vs-buy input. Out of scope: full market survey.

### Method highlights

- **Pricing history:** Wayback on `/pricing` — three snapshots over 24 months to detect model changes (volatile → `recheck_after` set 90 days out).
- **Roadmap leak:** open engineering roles scraped from the careers page — two data-platform roles → inference: batch pipeline investment.
- **Customer truth:** review-site 1–2★ text (not star averages) + two dated forum threads via platform routing.

### Claims table (excerpt)

| id | statement | type | grade | notes |
|---|---|---|---|---|
| C-001 | Free tier exists with event-volume caps | fact | A | pricing page (T1) + docs (T1), spot-checked |
| C-002 | Company claims >100k games instrumented | claim | C | self-reported marketing figure — attributed, not asserted |
| C-003 | Recent negative reviews cluster on export limitations | inference | B | pattern across S-007..S-010, two independence groups |
| C-004 | Revenue is $X M | — | — | **not included**: private company, no credible source → Open Questions |

### Gate notes

The revenue figure circulating in two blog posts traced to a single estimation site (provenance trace, §9.2) — one independence group, methodology unstated → excluded rather than shipped at D.

### Deliverable excerpt

> **Snapshot verdict:** mature free tier suits prototyping [C-001]; the recurring export-limitation complaints [C-003] matter specifically for your build-vs-buy question — if you'll want raw event data later, the exit cost is front-loaded. **Couldn't verify:** revenue, active-customer count (private; self-reported only).

---

## Example 3 — Claim verification: "Godot 5 announced with a 2027 release date?"

**Input:** "Someone in my Discord said Godot 5 was announced for 2027. True?"

### Intake

Quick tier, fact-check protocol (§9). Decompose: (a) has "Godot 5" been announced at all? (b) by whom? (c) with a 2027 date?

### Provenance trace

```
Q1 [exact]        "Godot 5" announcement                      → forum posts, one YouTube video
Q2 [origin hunt]  "Godot 5" 2027 (sorted oldest first)        → earliest hit: speculation video, not an official source
Q3 [primary]      site:godotengine.org "Godot 5" OR roadmap   → no announcement post
Q4 [adversarial]  "Godot 5" fake OR rumor OR "not announced"  → thread debunking the video
```

Chain reconstructed: speculation video (T4) → reposted to two forums (same group G1) → Discord paraphrase added the confident date. Official blog and repo milestones (T1): no such announcement; development communication references 4.x minor releases.

### Verdict (deliverable, executive brief)

> **Verdict: Unsupported.** No official announcement exists [S-003: godotengine.org blog, checked to <date>; S-004: repo milestones]. The claim traces to a single speculation video [S-001, T4] whose date was invented downstream. This is the first-report trap (§9.6): three "sources" were one independence group. **Recheck:** volatile by nature — recheck if a GodotCon keynote or official blog post appears.

**Teaching point:** the deliverable states what *was* found (T1 silence + T4 origin), not just "false." Negative provenance is evidence.

---

## Example 4 — API/docs landscape: Godot 4 GDExtension for a C++ module decision

**Input:** "Survey the field on GDExtension — I'm deciding whether to move a performance-critical system from GDScript to a C++ GDExtension. What's the state of docs, tooling, and community knowledge?"

### Intake (condensed)

Standard tier, literature-review-lite (§8 applied to docs instead of papers). Success criteria: annotated bibliography of the load-bearing resources + a gap map (what's undocumented) + go/no-go input.

### Source map

| Class | Targets | Tier |
|---|---|---|
| Official | godotengine.org docs GDExtension section; godot-cpp repo + its examples | T1 |
| Code | godot-cpp tests; 2–3 mature published extensions as reference implementations | T1 |
| Community | dated tutorials (≤12mo only — API churn), HN/Reddit migration threads | T2–T4 |

### Findings shape (excerpt)

- **Annotated bibliography, top entries:** official docs (T1 — covers registration/build, thin on debugging workflows); godot-cpp examples (T1 — the real quickstart); one maintained third-party template repo (T2 — fills the CI gap, verify `pushed:` date).
- **Gap map (the deliverable's core):** debugging story under-documented; version-pinning between engine and bindings is folklore spread across issue threads [C-005, grade B, three independent issue threads]; hot-reload behavior documented only in a PR description [C-007, grade C — single T1-adjacent source].
- **Recency trap caught at the gate:** two popular tutorials predated a breaking bindings change — excluded from the bibliography with a dated warning note rather than silently dropped.

### Deliverable excerpt

> **State of the field:** viable but folklore-heavy. Core registration and build paths are well documented [C-001, A]; operational knowledge (debugging, version pinning, hot reload) lives in issues and PRs, not docs [C-005..C-007]. **Implication for your decision:** budget the first week for toolchain, not code; pin engine + bindings versions from day one.

---

## Example 5 — Market sizing (light-touch): browser-based wellness games

**Input:** "Rough market size for browser-based wellness/casual-wellness games — deciding if this niche justifies a paid tier."

### Intake (condensed)

Standard tier. Success criteria: an order-of-magnitude range with stated assumptions, not a point estimate. Expectation set at intake: **no grade A numbers exist in this category** — the deliverable will say so.

### Method (per §6)

- **Definition first:** browser-delivered, wellness-positioned casual games, consumer-paid (subscriptions/one-time), EN-speaking markets, annual.
- **Top-down attempt:** "wellness apps market $X B" figures traced to two analyst firms; both counted meditation apps, wearables, and B2B corporate wellness — definition mismatch → recorded, then discarded for sizing (kept as ceiling context, grade C).
- **Bottom-up:** proxy chain — casual-wellness community sizes × plausible conversion bands × observed price points from 6 comparable products' public pricing pages (T1 for prices; the conversion band is explicitly an assumption, not a claim).
- **Triangulation:** bottom-up range checked against one comparable's self-reported revenue (T3, single group, labeled).

### Claims table (excerpt)

| id | statement | type | grade | notes |
|---|---|---|---|---|
| C-001 | Comparable products price at $4–12/mo | fact | A | six pricing pages (T1), independent |
| C-002 | Broad "wellness app" market figures are definitionally unusable for this niche | inference | B | methodology reading of both analyst summaries |
| C-003 | Niche annual consumer spend is plausibly $Xm–$Ym (order of magnitude) | inference | C | bottom-up arithmetic shown in full; assumption bands stated |
| C-004 | The niche is growing | claim | D | only T3/T4 sentiment — labeled, not load-bearing |

### Deliverable excerpt

> **Range:** $Xm–$Ym annual consumer spend (grade C inference — arithmetic and assumptions in §Method; attack the assumptions, not the midpoint). **Honesty note:** no independent market report covers this niche as defined; the broad wellness figures you'll see quoted [C-002] include categories that don't apply. **Decision framing:** at even the low bound, a paid tier clears your revenue bar if conversion hits the middle assumption band — the sensitive variable is conversion, not market size. **Recheck:** 6 months (C-003 volatile).

---

## Pattern summary across examples

| Pattern | Shown in |
|---|---|
| Vendor benchmark downgraded at the gate | Ex. 1 (C-003) |
| Independence collapse → figure excluded, not shipped weak | Ex. 2 (C-004) |
| Provenance trace to a T4 origin → "Unsupported" verdict with evidence | Ex. 3 |
| Recency trap: popular-but-stale sources excluded with dated warning | Ex. 4 |
| Assumptions labeled as inference; arithmetic shown; range not point | Ex. 5 |
| Empty/negative result treated as a finding | Ex. 2, 3 |
