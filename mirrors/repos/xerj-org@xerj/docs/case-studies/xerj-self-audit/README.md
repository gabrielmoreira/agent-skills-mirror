# Case study: XERJ audits its own Rust with XERJ

**What this is.** A reproducible whitebox security audit of **XERJ's own engine**
(197 Rust files, ~201k lines across 16 crates) performed by an AI agent using
XERJ as its retrieval and reasoning substrate — the [WordPress
audit](../wordpress-security-audit/README.md) method turned on XERJ itself. XERJ
had no Rust parser, so the substrate is a tree-sitter-rust extractor
([`../../examples/rust-ast-audit/`](../../examples/rust-ast-audit/)) that turns
the source into three queryable indices: functions, call-edges, and routes.

Every number here is reproducible; see [REPRODUCE.md](REPRODUCE.md). The one
confirmed vulnerability is in [FINDINGS.md](FINDINGS.md), proven by crashing a
real server, not by argument.

The point is **not** "we 0-day'd our own engine." It is the **method and its
credibility**: what an AI-assisted Rust audit costs, what the call graph catches
that grep cannot, and — the part most demos skip — a **ground-truth recall test**
that measures whether the substrate actually finds real bugs before we trust it
on unknown ones.

## Detection quality, measured against known ground truth

The day before this audit, PR #69 fixed **six** real, network-reachable
vulnerabilities in this exact codebase, at known locations — a labelled test set.
Full methodology and per-bug numbers: **[DETECTION-QUALITY.md](DETECTION-QUALITY.md)**.

| | XERJ substrate | grep baseline |
|---|---|---|
| **Bugs found (recall)** | **6 / 6** | 4 / 6 |
| **Tokens to triage all candidates** | **84,122** | 2,715,003 (**32×** more) |
| **Unit of a hit** | a function | a whole file |

Two findings, not one. **Recall:** grep cannot find F7 or F8 *even in principle* —
both are **missing code** (an absent limit check, an absent action cap), and you
cannot grep for code that is not there; `grep max_actions_per_bulk` on the pre-fix
tree returns 0 lines. **Triage cost** is the bigger result: grep's literal recall
is fine, but triaging `grep with_capacity` for F6 means reading 56 whole files
(1.34M tokens) versus 27 functions (17.9K).

**The caveat that matters: 6/6 is in-sample.** The first run scored **XERJ 3/6 —
worse than grep.** The test set exposed three real defects in the *extractor*
(argument parsing truncating `a.len() * b.len()` at the first paren; taint
provenance not following one hop into locals; validator detection being
presence-only rather than order-aware). Fixing those took it to 6/6, and each fix
was verified to **go quiet on the patched code** — so it discriminates rather than
merely matching. The genuinely out-of-sample result is the `/_sql` Critical below:
not in the test set, found on current `main`, proven by crashing a server.

Precision is the weak axis and is stated plainly in DETECTION-QUALITY.md: the true
positive lands at rank 6 of 186, 12 of 13, 18 of 27, 19 of 21. The substrate is a
strong *filter* and a mediocre *ranker*.

## The headline: XERJ-assisted vs. "the agent reads all 197 files"

| | Agent reads all files | XERJ-assisted audit |
|---|---|---|
| **Tokens to reach the `/_sql` finding** | **1,805,277** (every `.rs` under `engine/`) | **10,533** (cycle-finder output + 4 parser fns read + route lookup) |
| **Ratio** | — | **171× fewer tokens**, measured, to the same bug |
| **Fits one context?** | No — ~9× a 200k window; must chunk | Yes — targeted queries return tens of candidates |
| **Interprocedural reach** | Lost at chunk boundaries | 87,137 call edges preserved across all files |
| **Finds a recursion *cycle*?** | Only if the whole cycle lands in one chunk | One query over the call graph |
| **Grounded?** | Skimming 1.8M tokens → guesses | Every finding cites a real `file:line`, verified by reading it |
| **Reproducible?** | No | Yes — extractor + queries reproduce exactly |

Both token figures are **measured with tiktoken (`cl100k_base`)**, a public
GPT-4-class BPE used as an LLM-token proxy — not a chars÷4 estimate. Read-all =
every `.rs` file under `engine/` tokenized (197 files, 8,025,201 bytes). The
XERJ-assisted figure is the actual path to *this* finding: the cycle-finder's
stdout (7,511 tok) + the four SQL parser function bodies the auditor read (3,002
tok) + the route lookup (20 tok). Substrate build: **~3.2s extract + ~1.9s
ingest**, 31 MB on disk.

## Coverage (the explicit goal was 100%)

- **197/197 files parsed, 0 tree-sitter ERROR nodes.**
- **5,095 / 5,095 function nodes emitted — 100.0% function coverage.** (Verified
  by counting `function_item` AST nodes independently of emitted records; a first
  cut hit 97.2% because nested `fn` items were skipped — that gap is now closed
  and asserted in `coverage.json`.)
- 299 axum-handler-shaped functions, 477 route registrations, 21 functions
  containing `unsafe` (see below).

What the AST substrate **cannot** see is stated in [COVERAGE.md](COVERAGE.md):
macro-generated code, trait-object dynamic dispatch, and `build.rs` codegen are
out of reach, and callee resolution is name-based (method calls are deliberately
excluded from the call graph — see the note below).

## What the audit found

**One confirmed, empirically-proven Critical**, plus an unsafe inventory that came
back clean:

- **`POST /_sql` stack-overflow DoS** (Critical, unauthenticated). The SQL WHERE
  parser (`parse_or_expr → parse_and_expr → parse_condition → parse_or_expr`)
  recurses on every `(` with **no depth guard**. This is the *same class* as F1,
  which PR #69 fixed — in the query_string parser only. The SQL parser is the
  unfixed sibling. A single `POST /_sql` with ~50k nested parens aborts the
  process:

  ```
  thread 'xerj-rt' has overflowed its stack
  fatal runtime error: stack overflow, aborting
  ... Aborted (core dumped)
  ```

  Found by the call-graph **cycle** query (a grep cannot express "mutually
  recursive functions with no depth bound"), traced to the `/_sql` route via the
  routes index, and **proven by killing a live server** (exit 134 / SIGABRT).
  Full reproduction in [FINDINGS.md](FINDINGS.md).

### Complete `unsafe` inventory — 21 functions, all reviewed, all sound

Completeness was an explicit ask, so the full table is in
[FINDINGS.md](FINDINGS.md#unsafe-inventory). Breakdown: 12 FFI syscalls
(`statvfs`/`sysconf`/`clock_gettime`), 4 `MaybeUninit` for those FFI structs, 2
`Vec::from_raw_parts` in a CLI arg shim, 1 raw-pointer prefetch in HNSW, 1
`from_utf8_unchecked` in the SIMD tokenizer, and a raw-pointer JSON-tree walk.
Each carries a documented SAFETY invariant; on review each invariant holds. "0
unsound sites" is the honest result — and the inventory is the deliverable.

## Honest limits of this pass

This is a **single-agent** audit of the highest-value lenses (recursion/DoS,
unsafe, path-traversal), run while the multi-agent verification fleet was
unavailable. The broader lenses — full auth-flow mapping, business-logic
invariants, every `as`-cast triage — are scoped but not exhausted here; the
extractor emits the fields for them (`has_narrowing_cast`: 375 non-test sites,
`lock_across_await`: 15) and the queries are in the
[cookbook](../../examples/rust-ast-audit/QUERY_COOKBOOK.md), ready for the
adversarial-verification fleet to grind through. What is published here is only
what was **proven** or **completely enumerated** — not everything the substrate
flagged.

## Why this beats reading-all *and* beats grep

- **vs reading-all:** the codebase does not fit one context; chunking destroys
  the interprocedural reach that found the SQL cycle, and skimming 2M tokens
  invites hallucinated findings. Here every claim cites code that was read.
- **vs grep:** grep is line-scoped. It cannot express "a recursion *cycle* across
  three functions with no depth guard anywhere in it," or "a `.join()` of a
  request parameter with no containment check in the same function." The call
  graph makes both a single query.

## Five-stage methodology (second pass)

A second, deeper pass (24 Fable-5 agents, adversarially verified) replaced the
category checklist with a single organizing principle and ran five stages against
it. Full reusable playbook — principle, taxonomy, the XERJ query and the grep
baseline for every stage: **[METHODOLOGY.md](METHODOLOGY.md)**. All eight findings,
severity-ranked: **[FINDINGS-V2.md](FINDINGS-V2.md)**. Issue drafts:
**[ISSUES.md](ISSUES.md)**.

> **A function is dangerous when INSTRUCTION and DATA share one channel with no
> separator** — and a filter is only real if it removes the instruction power
> from the data channel. "It calls `escape()`" is not enough.

The strongest findings are failures of that corollary rather than missing filters:
in F-PATH-02 all three filters guarding the snapshot *name* are real, well-written
and tested, and the vulnerability is in the un-validated sibling field (the repo
*location*) none of them look at.

| Stage | XERJ query returns | XERJ tokens | grep lines | grep files | grep tokens | ratio |
|---|---:|---:|---:|---:|---:|---:|
| 1 · Flag dangerous sinks | 318 functions | 40,623 | 1,132 | 110 | 1,585,177 | **39×** |
| 2 · Trace to user input | 13 caller edges | 1,232 | 23 | 5 | 374,872 | **304×** |
| 3 · Privilege model + flows | 477 routes + 24 auth fns | 40,218 | 874 | 73 | 1,271,510 | **32×** |
| 4 · Validate filters for bypass | 18 functions | 1,940 | 711 | 66 | 1,317,109 | **679×** |
| 5 · State machines (TOCTOU/locks) | 16 functions | 1,814 | 3,377 | 96 | 1,381,258 | **761×** |
| **Total, per-stage sum** | | **85,827** | **6,117** | — | **5,929,926** | **69×** |
| **Total, deduplicated file union** | | **85,827** | | **153** | **1,685,346** | **19.6×** |

All figures measured with tiktoken `cl100k_base`. Two totals on purpose: the
per-stage sum (69×) is what an auditor working stage by stage pays; the
deduplicated union (**19.6×**) is the honest floor, and it carries the sharper
point — the five grep sweeps together touch **153 of 197 `.rs` files, 93% of the
engine's 1,805,277 tokens**. Grepping the five stages *is* reading the codebase,
in a worse order and without the call graph.

**Result: 8 confirmed, 8 refuted (a 50% cull).** By verifier-corrected severity:
**4 High** (INJ-01 search-template injection, F-PATH-02 snapshot-location
traversal, S5-1 session-revocation lost-update, DESER-EGRESS-01 unauthenticated
Raft control messages), **2 Medium** (S5-4 `x-forwarded-for` trust, S5-3
magic-link TOCTOU), **1 Low** (S5-5 field-limit bypass on the explicit path), **1
Info** (AUTHZ-2 unauth `cluster/info` disclosure). The three application-layer
Highs are **fixed** on this branch (`58fc73f`, with regression tests and live
before/after proof); DESER-EGRESS-01 is tracked as the cluster Raft-auth Phase-2
item.

An honesty note carried into [FINDINGS-V2.md](FINDINGS-V2.md): the workflow's
auto-synthesis under-reported this as "2 confirmed, 1 refuted." The eight
per-finding verifiers had actually confirmed eight; the gap was caught by
reconciling the synthesis against the raw verdicts, and each High was re-verified
by hand before publication — a reminder that the synthesis layer needs auditing
too.

The refuted half is load-bearing: the most instructive miss (`F-PATH-01`) had
every code observation correct and was still wrong, because the guard it thought
was missing lived in the caller. A finder without an independent,
refutation-first verifier would have shipped it.
