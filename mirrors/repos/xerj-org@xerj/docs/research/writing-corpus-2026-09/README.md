# How the best product and engineering posts are built

**Study date: 2026-09-22. Corpus: 6,545 posts / 1.9 GB of raw HTML from 51 publishers;
5,234 parsed as articles, 7.34 M words measured.**
Measured, not asserted. Every number here comes from `scripts/` run over
`~/.xerj-write/corpora`; the per-post table is in `data/reference-structure.csv`.

The distribution has converged: growing the corpus from 5,147 to 5,234 parsed
posts moved exactly one median in the table below (headings, 8 → 7) and left every
other one unchanged. More crawling will not change the targets.

This is the prose counterpart to the reference-coding mandate: before rewriting a
page, look at how people who do this well actually build one. It exists because the
xerj.org copy was described as unreadable, and "unreadable" needed a measurement
before it could be fixed.

---

## 1. What the corpus is, and the rule attached to it

51 publishers, crawled from their own sitemaps at ~1 req/s with robots.txt honoured:

| group | who | what it teaches |
|---|---|---|
| `ai-labs` | Anthropic, OpenAI, DeepMind, Mistral, Cohere, Hugging Face, xAI, TypeSafe | launch and research writing |
| `search` | ClickHouse, Elastic, Qdrant, Weaviate, Meilisearch, Typesense, Algolia | our own category |
| `devtools` | Cloudflare, Fly, Stripe, Supabase, Vercel, Linear, Sentry, Honeycomb, PlanetScale, Grafana, GitHub, Railway, Neon, Turso, Modal, Netlify, Tailwind | product + engineering posts |
| `evidence` | Jepsen, Dan Luu, Brendan Gregg, Marc Brooker, Julia Evans, Simon Willison, TigerBeetle, CockroachDB, Materialize, incident.io, Figma, Notion, Discord, Dropbox, Netflix, Zed, Warp, Ghost | measurement-led writing — the closest match to our benchmark pages |
| `essays` | Paul Graham, Signal v Noise, First Round Review | structure and voice |

**REFERENCE ONLY.** Every page is someone else's copyrighted writing. It is here so
we can read how a good writer solved a problem before we solve ours. Never paste a
sentence from it into XERJ copy, docs, the site or a post — the same rule as the
AGPL and GPL entries in the code corpora: read the approach, write your own words.
Nothing from this corpus is redistributed; only the measurements in `data/` are
committed.

---

## 2. The shape of a post (the targets)

Median, with the p25–p75 band. Aim inside the band; leaving it needs a reason.

| what | target | band |
|---|---|---|
| length | **1,000 words** (≈4.4 min) | 610–1,600 |
| headings | **7** | 4–12 |
| **words between headings** | **118** | 76–197 |
| paragraph | **35 words** median, 65 at p90 | 26–45 |
| lead paragraph | **36 words** | 22–55 |
| sentence | **18 words** median, 32 at p90 | 16–21 |
| sentence-length spread (sd) | **9.6** | 8.0–11.8 |
| links | **17 per 1,000 words** | 9–29 |
| numbers | **0.6 per 100 words** | 0.2–1.4 |
| lists | **2**, 7 items total | 1–4 |
| images / figures | **4** | 1–9 |
| code blocks | 0 median; **37% of long posts carry one** | 0–1 |
| "we / our / us" | **12 per 1,000 words** | 4–25 |
| "you / your" | **12 per 1,000 words** | 4–25 |

Length classes, and what changes with them:

| class | share | headings | words/section | carry code | carry an image |
|---|---|---|---|---|---|
| short (<600w) | 24% | 5 | 74 | 18% | 73% |
| standard (600–1,200w) | 36% | 7 | 110 | 29% | 83% |
| long (1,200–2,500w) | 32% | 10 | 143 | 37% | 89% |
| deep (>2,500w) | 9% | 12 | 252 | 33% | 79% |

The section length grows with the post. Long posts do **not** get more fragmented —
they get *more* words between landmarks, because a reader who has committed to
2,000 words is reading, not scanning.

## 3. Evidence: less than you would guess, and placed deliberately

- **90%** of posts contain at least one number.
- Median density is **0.6 numbers per 100 words** — roughly one every three sentences.
- Median count in the first 150 words: **1**. Only **24%** open with three or more.
- Density is flat across the post (0.63 overall vs 0.55 body-only): numbers are
  spread through the argument, not stacked in a results block.

So the good posts are *evidence-led* without being *number-dense*. One number lands
in the opening as the claim; the rest arrive one at a time, each attached to the
sentence that needs it. A paragraph with six numbers in it has stopped being prose
and become a table that forgot to be a table.

## 4. How they open

First sentence of 5,362 article bodies:

| opening move | share |
|---|---|
| straight into the subject, no throat-clearing | 60% |
| a number or a measured claim | 15% |
| a definition of the thing | 8% |
| an announcement | 7% |
| a scene — when this happened | 4% |
| a question | 2% |
| second person ("if you have ever…") | 2% |
| a problem statement | 2% |

Lead paragraph: median **37 words**, and **55% are 40 words or fewer**.

Three-fifths open by simply starting. There is no hook paragraph, no "in today's
fast-moving landscape", no restating the title. The first sentence is already the
first claim. Two that show the move:

> Last week we hit send on our 222nd consecutive weekly changelog. — Railway
>
> 2021 was a difficult year for Typesense, but not in the way you would imagine. — Typesense

## 5. Rhythm — the tell that survives a blocklist

| metric | reference (p25 / median / p75) |
|---|---|
| mean sentence length | 17.5 / **19.8** / 22.3 |
| sentence-length sd (burstiness) | 8.0 / **9.6** / 11.8 |
| sd ÷ mean | 0.43 / **0.49** / 0.57 |
| sentences starting the / it / this / these | 10 / **16%** / 23 |
| "is not just X" constructions | 0 / **0** / 0.82 per 1kw |
| "not X but Y" | 0 / **0** / 0 |

Human prose varies its beat: a 9-word sentence next to a 31-word one. The
distribution is wide *on purpose* — that variance is what makes a paragraph feel
written. Generated prose converges on one length and holds it, which is why
burstiness separates the two better than any vocabulary list does.

Word blocklists are close to worthless here. A site-wide scan for the usual
markers found **29 hits across 8 files** — and three of those are `brand.html`
listing the words we tell ourselves to avoid. The real total is 26, almost all
of it `unlock` (17, mostly `playground.html`) and `robust` (7). The buzzwords are
not our problem.

A blocklist also lies in the other direction: the first version of this scan
reported 364 hits because the pattern `enter ` matched inside "data center". The
fix (word-boundary matching) is in `scripts/audit_site.py`; the lesson is that a
phrase count is only evidence after you have read what it matched.

---

## 6. What this says about xerj.org

131 of 158 pages parsed as articles. Two populations, so they are reported apart:
the 77 generated `/answers/` pages, and the 55 hand-written ones.

| metric | reference | `/answers/` | rest of site |
|---|---|---|---|
| words | 1,001 | 701 | 732 |
| headings | 7 | **16** | 9 |
| **words between headings** | **118** | **41** | **62** |
| **images in the body** | **4** | **0** | **0** |
| numbers per 100 words | 0.6 | **3.4** | 1.8 |
| numbers in the first 150 words | 1 | **6** | 1 |
| sentence length (median) | 18 | 14 | 15.5 |
| sentence-length sd | 9.6 | **6.2** | 6.2 |
| sentences under 12 words | 20% | **36%** | 33% |
| sentences over 30 words | 12.5% | **0%** | 12% |
| links per 1,000 words | 17 | 8.4 | 12 |
| "we / our / us" per 1,000 words | 12.1 | **0** | **0** |
| "you / your" per 1,000 words | 12.5 | 4.5 | 8.4 |
| em-dashes per 1,000 words | 0 | 0 | **13.3** |

Six defects, ordered by how much they cost a reader:

**D1 — Nothing to look at. One page in 158 has an image in its body; 82% of
reference posts do.** The 9.9 MB of images in the repo is one demo page carrying 19
screenshots, plus brand-book assets and OG cards. Every argument on the site is
made in unbroken prose. A benchmark page with no chart is asking the reader to hold
a table in their head.

**D2 — Chopped into confetti.** 41 words between headings on `/answers/`, 62 on the
rest, against 118 in the corpus. At that spacing a heading arrives every second
paragraph and stops being a landmark: the reader gets a list of fragments instead
of an argument that develops.

**D3 — Flat rhythm.** sd 6.2 against 9.6, and on `/answers/` **0% of sentences run
past 30 words** while 36% are under 12. Everything is the same short length, so
nothing is emphasised and the prose reads as a stream of assertions. This is the
single strongest machine-written signal on the site, and all twelve of the flattest
pages are in `/answers/`.

**D4 — Number-dumping.** 3.4 per 100 words on `/answers/` (5.7× the corpus), six in
the first 150 words against a median of one. The honest-claims rule made us
*attach* a number to everything; it never said to put them all in one paragraph.

| page | nums/100w | em-dash/1kw | words |
|---|---|---|---|
| `landing/benchmarks/elasticsearch.html` | **6.56** | 19.8 | 2,072 |
| `landing/demo/index.html` | 6.13 | 14.3 | 767 |
| `landing/use-cases.html` | 6.11 | 22.9 | 524 |
| `landing/docs/recipes/document-folder-index.html` | 3.43 | **26.3** | 874 |

**D5 — Nobody wrote it.** "we/our/us" is **0 per 1,000 words** across the entire
site, against 12.1 in the corpus — and the sources with the strongest voices run
higher still (Supabase 31, Zed 30, Railway 29, Dropbox 35). Our pages describe a
system that apparently assembled itself. No one takes responsibility for a claim,
which is exactly the wrong posture for a project whose pitch is measured honesty.

**D6 — Em-dash habit.** p75 of 13.3 per 1,000 words on hand-written pages against a
corpus p75 of 2.7; `docs/recipes/document-folder-index.html` hits 26.3. Each one is
a clause that dodged deciding whether it was a sentence.

---

## 7. The rewrite rules

Derived from the numbers above; each one is checkable by `scripts/`.

1. **Every page that argues from data gets one figure.** A chart, a table, or a
   terminal capture. Benchmark pages first. Body images, not OG cards.
2. **One heading per ~120 words.** On a 700-word page that is five or six, not
   sixteen. Merge sections that are one paragraph long.
3. **Vary the sentence.** Target sd ≥ 8. Concretely: allow long sentences back in —
   about one in eight should run past 30 words, and today that share is zero.
4. **One number in the opening, the rest spread out.** Cap any page at ~1.5 numbers
   per 100 words in prose; a paragraph needing more becomes a table.
5. **Write as "we".** Around 12 per 1,000 words. "We measured", "we were wrong
   about", "we have not tested". Keep "you" for instructions.
6. **Em-dashes under 3 per 1,000 words.** Most become a full stop.
7. **Open with the claim.** 36-word lead, no hook paragraph, no restating the title.
8. **More links.** 17 per 1,000 words against our 8–12: link the issue, the run, the
   file.

`/answers/` is the worst population on every metric and it is generated, so the
generator template is the fix, not 77 page edits.

## 8. What is actually on the site

180 pages, **230,541 words**. Where the words are:

| section | pages | words |
|---|---|---|
| `answers/` | 77 | 104,660 |
| `docs/` | 45 | 41,823 |
| `compare/` | 17 | 27,562 |
| `use-cases/` | 9 | 12,689 |
| `benchmarks/` | 2 | 9,635 |
| root | 9 | 8,417 |
| `case-studies/`, `blog/`, `demo/`, `brandbook/`, `industries/`, other | 21 | 25,755 |

Two things in that table are worth arguing about, and neither is a writing problem:

- **`answers/` and `compare/` are 94 pages and 57% of the words.** They are
  long-tail SEO surface. That is a legitimate strategy, but it means the majority
  of the site is pages no human chose to read, and they are also the population
  that measures worst on every readability metric.
- **`brandbook/` is 3,818 words of internal brand guidance on the public site.**
  It is not a product page and does not need a public URL.

**The brand name disagrees with itself.** All 180 canonical URLs and OG tags say
`xerj.org`, while **64 pages show "XERJ.ai" to the reader**, mostly in the title
("XERJ.ai — Benchmarks"). `xerj.ai` is the separate commercial site. A reader who
notices is being told two different names for the same thing.

Checked and *not* defects, so nobody re-reports them: there is no mojibake in any
file (the stray `â` in earlier output was a terminal artifact), and
`playground/index.html` is a deliberately-unindexed app shell, not an empty page.

### The `/answers/` heading problem is in the template, not the prose

76 Markdown sources, median **653 body words with 7 authored `##` headings** —
already 82 words per section, below the 118 target. The builder then appends
`## FAQ` (with an `<h3>` per question), `## Evidence` and `## Related`, which is
how a 653-word page arrives at **16 rendered headings and 41 words between them**.

So the single highest-leverage edit on the site is in
`scripts/seo/build_articles.py:619-661`: render the FAQ as a definition list or
`<details>` rather than one `<h3>` per question, so the appended furniture stops
competing with the author's own landmarks. That is one change covering 77 pages.
Merging the authored 7 headings down to 4–5 is a second pass over the sources.

## 9. Running it

```sh
# structure of the reference corpus (or any HTML dir)
python3 scripts/analyze_structure.py --json out.json
python3 scripts/analyze_structure.py --dir landing

# rhythm, opening moves, prose vs corpus, and the site audit
python3 scripts/rhythm.py
python3 scripts/openings.py
python3 scripts/compare_style.py landing
python3 scripts/audit_site.py landing

# extend the corpus (respects robots.txt, ~1 req/s)
python3 scripts/fetch_corpus.py evidence --limit 200
```

Corpus lives in `~/.xerj-write/corpora/<group>/{raw,text}` and persists across
reboots — never put it under `/tmp`. `raw/` is what the structural scripts read;
`text/` is the extracted prose, which drops every structural signal and is only
useful for the style metrics.
