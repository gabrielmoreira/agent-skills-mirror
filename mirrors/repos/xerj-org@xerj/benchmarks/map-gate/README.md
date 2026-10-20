# The `xerj_map` gate — unknown-field 400s from MCP-issued DSL (#1055, rc.79)

**Gate line, verbatim from the issue:** *"unknown-field 400s from MCP-issued DSL
down >=80% on the reference-coding harness."*

| gate | threshold | status | measured | results |
|---|---|---|---|---|
| `xerj_map` #1055 (rc.79) | unknown-field 400s from MCP-issued DSL down ≥ 80 %, no-map arm vs with-map arm, same corpus + query set | **MEASURED — PASS** | **20/30 → 0/30 unknown-field 400s = 100 % reduction** (threshold ≥ 80 %) | [`results/2026-09-30-rc78gates/`](./results/2026-09-30-rc78gates/) |

Run 2026-09-30 against the release binary `xerj v1.0.0-rc.78`
(main @ `a179e1ef3`, cited from the binary's own `--version` and the MCP
server's `serverInfo`), one local node `--insecure --embed-mode lexical
--port 9660`, throwaway data dir. Counts, not timings — no wall-clock or CPU
number matters here; the run is deterministic (same corpus state, same query
set, same code path) and a re-run reproduces the counts exactly.

## What the engine actually does with a wrong field (discovery first)

Before designing the arms, every wrong-field query form was probed against the
live node (`results/…/armA/*.json` holds the per-form evidence). Two very
different failures hide behind "unknown field":

- **HTTP 400, error naming the field** — the gate's subject. Exactly three
  MCP-reachable forms produce it: `sort` on a field with no mapping and no
  `unmapped_type` ("No mapping found for [x] in order to sort on"), `knn`
  naming a non-vector field ("[knn] query field [x] is not a vector field"),
  and `semantic` naming a non-`semantic_text` field ("semantic query on field
  [x]: it is not a `semantic_text` field"). In a `hybrid` request one bad leg
  fails the whole request.
- **HTTP 200, zero hits, no error** — `term` / `match` / `range` / `exists`
  on a wrong field silently return 0 hits (`match` additionally returns a
  `hints[]` block with code `unknown_field` suggesting the real text fields;
  `term` does not). This is the *other* thing `xerj_map` fixes — arguably the
  bigger usability win — but it is **not** a 400 and is counted separately
  below, not inside the gate number.

## Method

**Corpus (the reference-coding harness's own shape).** The three small
Apache-2.0 repos of the pinned hub corpus `xerj-vector`
(`tools/xerj-code/hub/xerj-vector.json`) at their pinned commits — usearch
`cc23bbaf21ef`, instant-distance `13ea89ac1ca0`, hnswlib `d9b3608c83d8` —
cloned, pinned and indexed with the in-binary reference-coding flow
(`xerj corpus add --from` + `xerj corpus index`, manifest saved verbatim as
[`results/…/corpus.json`](./results/2026-09-30-rc78gates/corpus.json)).
9 datasets, 3472 records, 10.1 s wall. The nine indexes deliberately span
three shapes: prose/code docs indexes (semantic `body`/`text`, keyword/long
columns), PascalCase config indexes (a `Version`/`Include`/`Platform`
case-correction trap), and tiny structured datasets (a `json` index whose only
date field is `cloned_at`; a `sqlite-binary-vectors` index where the field
*named* `vector` is a `keyword`).

**Query set.** 30 intents (`queries.json`) written as an MCP agent's tasks —
sort, semantic, vector, hybrid and filter requests phrased the way the four
search tools take them. Each intent names its target dataset, its concept
("most recently changed files first", "by package version"), and one
**guessed** field name.

**Arm A — no-map baseline.** The guessed field, issued verbatim in the wire
shape the MCP tool proxies. Guesses were written down **before** any was
checked against the live mapping, as the single most plausible name an
ES-fluent agent writes first (plain snake_case English + the dominant
cross-engine convention; `lang` vs `language`, `license` vs `licence`,
`line_number` vs `line` are real convention splits, not strawmen). Five
guesses coincided with real fields (intents marked `control` in
`queries.json`) and were kept — so the baseline also shows what guessing gets
*right*.

**Arm B — with `xerj_map`.** The harness calls the **real MCP tool** over
stdio (`xerj mcp --url …` → `tools/call xerj_map {}`, raw response saved as
[`results/…/xerj-map-response.txt`](./results/2026-09-30-rc78gates/xerj-map-response.txt),
16,828 bytes for 9 indexes, no entry trimmed) and derives every field choice
mechanically from it, never from `_mapping`: first candidate present in the
entry with a compatible `es_type` (matched case-insensitively, used in the
map's exact spelling — that is the agent reading `Version` and writing
`Version`); highest-coverage `semantic_text` field for semantic-shaped needs;
any `dense_vector` field for knn — the map lists none here, so the
map-informed agent rewrites instead of guessing. Where the map shows the
concept does not exist, the agent **drops the clause** rather than invent a
name (2 dropped sorts, 1 dropped filter — each recorded as `map_action` in the
raw output). That rewrite-to-valid-DSL behavior is the tool's value and is
part of what is measured, stated plainly.

Both arms issue the identical 30 intents as HTTP against the same node and
corpus state; every request and response is in
`results/…/armA/` and `results/…/armB/`, one JSON per intent per arm.

## Result

| arm | issued | unknown-field 400s | other 400s | silent 0-hit (wrong field) | ok, hits |
|---|---:|---:|---:|---:|---:|
| **A — no map** (guessed names) | 30 | **20** | 0 | 5 | 5 |
| **B — with `xerj_map`** | 30 | **0** | 0 | 1 | 29 |

**Reduction: 20 → 0 = 100 % ≥ 80 % → PASS.** Arm A's 20 break down as
9 sort-unknown-field, 5 semantic-non-semantic-field, 6 knn-non-vector-field
(4 knn intents + 2 hybrid requests killed by their vector leg); every one of
the 20 error bodies names the guessed field (`error_names_used_field` in the
raw records — no 400 was counted on any other ground). Arm B's 5 controls
confirm the arms differ only in field knowledge: on intents where the guess
was already right (`language`, `title`, `word`, `text`, exists-`title`) both
arms return 200 with hits.

The non-gate column, for honesty: arm A also silently 0-hit on 5 filter
intents (`lang`, `repo`, `line_number`, lowercase `include`, American
`license` vs the corpus's `licence`) where arm B returned 174, 3 (after a
documented drop), 325, 0, 3 hits. Arm B's single 0-hit is
`filter-include`: the map correctly case-corrected to `Include`, but no
document carries the value `PACKAGE` — a correct query for an absent value,
not a field error.

## What is measured and what is designed

- **Measured (deterministic):** given the same corpus and the same 30 query
  intents, first-issue MCP-shaped DSL built from guessed field names fails
  with unknown-field 400s on 20/30; the same intents built from `xerj_map`'s
  actual response fail on 0/30.
- **Designed, not run (BLOCKED — live-agent loop):** whether a live
  model-driven agent *chooses* to call `xerj_map` before writing DSL, and how
  many 400s its real tool-call stream shows across a session including
  retries. That needs live model runs, which are not approved for this wave.
  Design: the same 30 intents handed to an MCP-connected agent twice — tools
  with `xerj_map` available vs withheld — counting 400s in the actual
  `tools/call` stream (the `AGENT_FTX_HARNESS`-style loop); estimated cost at
  the per-trial figures of `demo/playbooks/REFCODING_BENCHMARK_3MODEL_2026-08-18.md`
  (~$2/trial, 60 trials) ≈ **$120**, plus harness wiring. The deterministic
  arms above bound what that loop can add: the map eliminates the failure
  class *whenever consulted*; the live run would measure consultation rate,
  which is a property of the agent, not of the tool.

## Reproduce

```sh
# node (private port, throwaway dir)
xerj --insecure --embed-mode lexical --port 9660 -d "$(mktemp -d /tmp/mapgate-data-XXXX)" &

# corpus: pin the three small xerj-vector repos (manifest in the results dir)
xerj corpus add --from <this dir>/results/2026-09-30-rc78gates/corpus.json
XERJ_URL=http://127.0.0.1:9660 xerj corpus index map-gate-v   # exit 3 = junk files, normal

# both arms, 60 requests, raw per-intent output under results/<label>/
python3 benchmarks/map-gate/run.py --node http://127.0.0.1:9660 \
    --xerj-bin "$(command -v xerj)" --prefix xc-map-gate-v --label <date>-<label>
```

Files: [`queries.json`](./queries.json) (the 30 intents, guess rule, map
policy), [`run.py`](./run.py) (harness: MCP call, both arms, classifier),
`results/<label>/{run-header,summary,results.tsv,xerj-map-response,corpus.json}`
+ `arm{A,B}/<intent>.json`.
