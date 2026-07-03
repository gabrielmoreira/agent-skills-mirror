# Calibrating Review Depth: Not Every PR Deserves the Same Eyes

Uniform review rigour is a bug: it over-taxes trivial changes (training reviewers to skim) and under-protects the dangerous ones. Depth should be set by blast radius, not by diff size — a 3-line auth change outranks a 400-line test refactor.

## The risk classifier (set depth BEFORE reading the diff)

| Class | Touches | Depth |
|---|---|---|
| **Critical** | authn/authz, payments, data deletion/migration, crypto, PII flows, public API contracts | Line-by-line + hand-trace inputs + a second reviewer; no same-day-merge pressure |
| **Elevated** | shared utilities, concurrency, caching, error handling paths, performance-sensitive code | Full read + targeted verification of the risky mechanism |
| **Standard** | feature code on established patterns | Normal pass: correctness, tests, conventions |
| **Light** | docs, copy, config-with-precedent, generated files | Sanity scan; rubber-stamping here is FINE and frees budget for critical PRs |

Diff size modifies within class, never across: a large Standard PR gets more time, not Critical treatment; a tiny Critical PR never gets Light treatment.

## Where reviewers' attention actually pays

In order of bugs-caught-per-minute (industry-consistent): **boundary/error paths** (what happens on empty, null, duplicate, timeout) → **state changes** (what else reads what this writes) → **concurrency assumptions** → **the tests' ability to fail** → naming/style (last, and linters should own most of it).

## Comment discipline

- Prefix severity so authors can triage: `blocking:` / `consider:` / `nit:` — a review of 14 unmarked comments is a mood, not a signal
- One systemic comment beats five instances ("this error-swallowing pattern appears 5×; here's the first") 
- Questions before verdicts on unfamiliar code ("what happens if X arrives twice?") — half the time the answer teaches you; half the time asking teaches them

## The reviewer's honest outs

"I reviewed the logic but not the domain math — needs eyes from [team]" and "approved on pattern-trust; did not hand-verify the migration SQL" are professional statements, not weaknesses. Silent partial review is the dangerous kind.
