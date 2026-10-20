# Second-brain demo — corpus + verification harness

One command turns a folder of notes into a queryable, replayable link index
with a dashboard. This directory holds the demo vault generator and the
scripts that PROVE the three claims against a live server — nothing here is
mocked, and every number the scripts print is read from a live response.

> XERJ doesn't understand your notes — it makes the structure you wrote
> queryable, timestamped, and evidence-backed, deterministically. It is a
> search engine with a graph-shaped index over its own documents, **not a
> graph database** and not a brain.

## The demo vault

`gen-corpus.sh` writes a realistic 39-file personal knowledge base (bread
baking + a bakery-launch project) shaped so every link detector has honest
work to do:

| folder | files | what it exercises |
|---|---|---|
| `notes/` | 15 | `[[wikilinks]]` — authored links between zettels (one deliberately dangling: counted, never invented) |
| `projects/bakery-launch/` | 6 | relative markdown links, incl. external URLs that must NOT become links |
| `clippings/` | 4 | saved HTML pages with `<a href>` to corpus files |
| `journal/` | 12 | **no authored links at all** — every edge is structural (files sitting together), the corner of the vault that makes the dashboard's AUTHORED vs STRUCTURAL split honest |
| `reading/` | 1 | one long note that splits into sections → section-order links |

File bytes and mtimes are pinned, and detector links take their
believed-since time from mtime — so regenerating the corpus and re-running
`xerj brain` reproduces the **same edge ids every time**. (Only `created_at`
— when the brain learned each link — is wall clock, by contract.)

## Run it

```bash
./boot-and-brain.sh   # generate the vault (if absent), run `xerj brain`,
                      # verify the server answers      → ports 9331-9333
./transcript.sh       # the API proof (see below)      → PASS/FAIL summary
./mcp-smoke.sh        # the agent surface over MCP     → PASS/FAIL summary
```

Defaults: working root `${TMPDIR:-/tmp}/xerj-second-brain-demo`, es-compat
port `9331` (override with `XERJ_BRAIN_DEMO_ROOT` / `XERJ_BRAIN_DEMO_PORT`),
binaries from `engine/target/release/`. All scripts are idempotent; stop the
booted server with `kill $(cat <root>/data/server.pid)`.

These three are also what CI runs, via `.github/scripts/usecase-smoke.sh` — so
the gate on every PR is this exact harness, not a separate copy of it.

## What the transcript proves

1. **Overview** — brain exists, live/retired counts, all five detectors
   fired, the `lexical-feature-hash` honesty marker, `not_shown` accounting.
2. **Ego** — one note's neighborhood: every link annotated with hop,
   direction, and the evidence that taught it; node previews hydrated;
   clipping honestly counted.
3. **Link** — assert a manual edge *with the quote you are relying on*;
   identical re-assert returns `created:false` with the same edge id
   (deterministic identity ⇒ safe to retry).
4. **Unlink** — retire, never delete: the response carries both clocks
   (when it stopped being true vs. when the system recorded that).
5. **Replay** — ask again with `as_of` inside the belief interval: the
   retired link is still there in the past, absent now, and the exclusion is
   *counted* in `not_shown.expired_excluded`.
6. **Refusals** — `hops=3` → 400 with the not-a-graph-database wording;
   self-links → 400; unknown brain → 404 `exists:false`.

## What this demo does NOT claim

- No semantic understanding: detectors are lexical, the embedder is
  feature hashing — never "neural".
- No hidden-connection discovery: authored links are re-indexed from what
  you wrote; same-folder/section-order links are structural priors and are
  labeled as such.
- No graph-database features: no path queries, no PageRank, no unbounded
  traversal — expansion is capped at 2 hops per call, by design.
- No performance numbers: this harness measures correctness, not speed.
  Anything not measured here is "not measured".
