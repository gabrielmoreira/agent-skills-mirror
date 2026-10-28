---
name: input-token-overheads
description: "Use when the context window fills too fast, per-turn input token cost is too high, or the aggregate input token bill needs explaining and fixing. Two audits: (1) overhead — tool schemas, skills index, system fixed text, user profile, memory recall measured live, ranked, reduced; (2) cost accounting — total input token volume across sessions, cron fires, and tool traffic, with cache-aware interpretation, pre-checked config levers, and scheduled delta checks. scripts/audit_overheads.py for per-turn overhead, scripts/audit.py for totals."
license: MIT
metadata:
  version: 1.9.0
  author: moonlight-lupin
  platforms: [linux, macos, windows]
  tags: [tokens, overhead, context, cost-accounting, optimization, agent-ops]
  related_skills: [hermes-compression-tuning, hermes-agent-skill-authoring]
---

# Input Token Overheads

Audit every source of input token cost on a Hermes Agent instance, at two scopes. Measure each, rank by cost, act on the top consumers.

- **Per-turn overhead audit** — what the system prompt costs every turn: tool schemas, skills index, system fixed text, user profile, memory recall. Script: `scripts/audit_overheads.py`.
- **Aggregate cost-accounting audit** — total input token volume across sessions, cron fires, and tool traffic: where the tokens went, which consumers dominate, what config or prompt change reduces them. Script: `scripts/audit.py`. (Merged from the former `input-token-analysis` skill; v1.9.)

Per-turn context-window health is the overhead audit's job; provider billing disputes need the provider's usage dashboard — local telemetry cannot see provider-side caching.

## When to Use

- User says "token overhead", "context too large", "why is input so expensive"
- Model output quality degrades from context dilution
- Cost optimization — fewer input tokens per turn means lower API spend
- After adding skills, plugins, or tools — verify the overhead delta
- Monthly/weekly input token bill is large and unexplained (e.g. "2.4B tokens in 30 days") — aggregate audit
- After applying token-saving changes — measure the delta against a baseline — aggregate audit
- A cron job is suspected of runaway token use — aggregate audit

## The Overhead Map

Verified on a live build (2026-10), cli surface, 44 tools:

| Category | Independent (rough tok) | Budget (bytes/4 tok) | Notes |
|---|---|---|---|
| Tool schemas | ~17.9k | ~17.9k | **Largest block.** Full JSON schema per enabled tool; builtin/mcp/subagent split available independently |
| Skills index | ~5.4k | ~5.4k | Full index, always-on in the **volatile** tier (moved there so skill edits don't invalidate the cached stable prefix). NOT top-K — top-K tuning does not reduce it |
| System fixed text | ~4.2k | ~4.1k | Identity/guidance; fixed cost |
| User profile | ~0.8k | ~0.8k | Injection cap 3,000 chars — over-cap tail is **silently cut every turn** |
| Memory (own facts) | 0 | 0 | 0 B when Mnemosyne owns recall; its per-turn recall injections sit outside the prompt-size budget — the live measured total includes them |
| Provider-measured input | — | ~25.1k tok | ~3.2k BELOW the sum of estimates — the provider tokenizer counts the JSON tool schemas tighter than chars/4 |

**On-demand (not per-turn):** full SKILL.md via `skill_view`, deferred tool schemas via `tool_describe`, reference files via `skill_view(file_path=...)`.

Three-way measurement (v1.8), category by category:

1. **Measured** (ground truth): `scripts/audit_overheads.py` starts a REAL prompt (`hermes -z "Reply with OK" --usage-file ...`) and reads the provider's actual `input_tokens` for a fresh session. Providers report totals only.
2. **Independent** (per category): the script builds Hermes' own offline inspection agent, renders the real system prompt parts, and measures each category with the build's rough tokenizer — system fixed text, skills index, memory, user profile, builtin/MCP/subagent tool schemas. It re-derives categories from the rendered prompt; it does not read prompt-size output.
3. **Budget**: `hermes prompt-size --json` byte accounting (bytes/4 estimator), used only as the comparison column.

Plus the context-doctor port (jzOcb/context-doctor, MIT; concepts only, script native): injection-cap checks — `TRUNCATED` (over cap, silently cut every turn), `MISSING` (broken reference). Exit 1 when any injected file needs attention.

## Health Ratio

The health metric is **overhead ratio**: measured (or estimated) overhead tokens divided by the model's context window. The absolute number matters for cost; the ratio matters for quality.

| Ratio | Rating | Notes |
|-------|--------|-------|
| < 5% | Excellent | Most of the window available for conversation |
| 5-15% | Healthy | Normal for a capable agent with tools, skills, memory |
| 15-25% | Acceptable | Approaching the limit. Consider trimming. |
| > 25% | Unhealthy | Eats conversation capacity. Cost and quality risk. |

**Why the ratio matters:** Three studies confirm that input length degrades model performance independent of content quality:

1. **Lost in the Middle** (Liu et al., TACL 2023) — Models follow a U-shaped curve: best recall at the start and end of context, severe degradation in the middle. Overhead sits at the top of every turn, but it pushes conversation history into the degradation zone. [arxiv.org/abs/2307.03172](https://arxiv.org/abs/2307.03172)

2. **Same Task, More Tokens** (Levy et al., ACL 2024) — Reasoning performance degrades at input lengths far shorter than the model's stated maximum. The degradation appears even when the extra tokens are padding with no distracting content. The model's technical context window is not its effective context window. [aclanthology.org/2024.acl-long.818](https://aclanthology.org/2024.acl-long.818/)

3. **Context Length Alone Hurts** (Du et al., EMNLP 2025) — Performance degrades 14-85% as input length increases, even when retrieval is perfect, irrelevant tokens are replaced with whitespace, or all tokens except relevant ones are masked. The sheer length of the input is itself a limitation. [aclanthology.org/2025.findings-emnlp.1264](https://aclanthology.org/2025.findings-emnlp.1264/)

**Cost compounding:** Overhead is paid every turn. At 10k tokens over 100 turns, that is 1M input tokens spent on overhead alone. Reducing overhead by 2k tokens saves 200k tokens per 100-turn session.

**Mitigations from the research:**

| Finding | Source | Action |
|---------|--------|--------|
| Models recall start and end of context best; middle degrades | Liu et al. 2023 | Keep overhead at the top (Hermes already does this). Avoid pushing critical conversation history into the middle — lower compression threshold if history is being compressed too aggressively |
| Reasoning degrades well below the stated context window maximum | Levy et al. 2024 | Treat the effective context window as 50-70% of the advertised maximum. Target an overhead ratio under 10% of the advertised window, not the effective one |
| Sheer input length hurts even with perfect retrieval and no distraction | Du et al. 2025 | Reduce overhead aggressively. Every 1k tokens of overhead removed improves reasoning quality, not just cost. The study's mitigation: prompt the model to recite key evidence before solving — equivalent to Hermes compression summarizing relevant context |
| Tool calling degrades 7-85% as tool catalog grows from 8k to 120k tokens | LongFuncEval (arxiv 2505.10570) | Keep the enabled toolset count low. Prefer deferred tools (loaded on demand) over always-on schemas. Disable unused toolsets |

## Procedure

### 1. Measure each overhead source

```bash
python3 scripts/audit_overheads.py     # from the input-token-overheads skill dir
```

One run: starts the live one-shot prompt (one inference call), then prints the category-by-category comparison table:

```
category                     indep est    budget    delta
system fixed text                4,177     4,065      112
skills index                     5,379     5,357       22
memory (own facts)                   0         0        0
user profile                       820       816        4
tool schemas (all)              17,885    17,884        1
TOTAL                           28,261    28,124      137
provider measured                   25,077
```

- **indep est** — re-derived from the rendered prompt with the build's rough tokenizer (no prompt-size output involved)
- **budget** — `hermes prompt-size` bytes/4
- **provider measured** — the real fresh-session `input_tokens`; the honest denominator for the health ratio
- Per-category deltas over a few hundred tokens = drift between what you think ships and what ships — investigate that category
- Tool split (builtin/mcp/subagent) prints under the table

Flags: `--platform cli|telegram|discord|...` (inspection + budget surface), `--skip-live` (no inference call; measured row reads "unmeasured"), `--json`, `--chart out.png`, `--ctx <window>`, `--live-timeout`. Exit 1 = an injected file needs attention.

Also measure what neither estimate sees: memory-provider recall size per turn (in-session: read a fresh turn's injected recall blocks) — it rides on top of the measured fresh-session total and grows with facts.

**Done:** category table read; health ratio computed from the provider-measured total; every injected-file status checked.

### 2. Rank by cost

The table ranks. Typical ranking:

1. **Tool schemas** — largest block. Scales with enabled toolset count.
2. **Skills index** — always-on full index. Scales with indexed-skill count.
3. **System fixed text** — fixed stable tier.
4. **User profile** — capped, but usually near budget on long-lived agents.
5. **Memory-provider recall** — dynamic, per-turn, outside the budget; measure in-session, trim facts if it grows.

**Done:** top 3 identified — these are the optimization targets.

### 3. Act on top consumers

**Tool schemas (largest block):**
- Prefer deferred tools (loaded on demand) over always-on tools — each deferral replaces a full JSON schema with a ~150 B catalog row
- Disable unused toolsets; check `requires_toolsets` in every skill's frontmatter before removing a toolset a skill depends on
- Use `platform_toolsets.<platform>` in config.yaml to control per-surface access (a Telegram surface needs fewer tools than the CLI)

**Truncated files (script exit 1):**
- A TRUNCATED user profile is a correctness problem, not a cost problem — the tail is lost every turn. Trim under cap (batch-shorten or remove stale entries) and re-run until `OK`

**Skills index:**
- Disable unused skills in `config.yaml` under `skills.disabled` — each removal drops ~200-300 chars from the always-on index
- Trim descriptions over ~200 chars — they waste index budget without improving routing

**Memory provider (if installed):**
- Run consolidation to move working to episodic, reducing the recall budget per turn
- Invalidate stale facts; lower the recall `limit` if context is tight

**Compression:** load `skill_view(name='hermes-compression-tuning')` for threshold and target-ratio tuning.

**Done:** at least one optimization applied to each top-3 source, every truncated file trimmed under cap.

### 4. Verify the delta

Re-run the audit script (live). Compare each category's delta and the provider-measured total before/after; confirm all injected files read `OK`.

**Done:** before/after per-category delta reported. If no meaningful reduction, the remaining overhead is structural (tool schemas + skills index) and needs config changes, not content trims.

## Aggregate Spend Audit (cost accounting)

Explain aggregate input token consumption. Answer three questions with numbers: where did the tokens go, which consumers dominate, what config or prompt change reduces them. This audit covers total volume across sessions, cron fires, and tool traffic; the per-turn procedure above covers system-prompt overhead.

### Run it

```bash
python3 scripts/audit.py --days 30     # from the input-token-overheads skill dir
# other profiles: --db ~/.hermes/profiles/<name>/state.db
# custom cron ledger: --cron-audit /path/to/usage_audit.jsonl --jobs /path/to/jobs.json
```

Read-only, pure stdlib. The script prints: totals by task/model/provider, cache-read and cache-write columns, weighted per-call averages (long sessions and short-session floor), top sessions, cron offenders, active-only tool-result volume with the tool-share percentage, and oversized-result counts. Everything is derived from real DB rows — never estimate by hand when the script can measure.

### Pre-Check Discipline

Verify before advising. Advice formed from memory is not acceptable.

1. **Config keys and current values** — read the live value first: `hermes config get <key>`. Never state a current value from memory or assume the default is in force.
2. **Defaults and mechanisms** — confirm a key exists and what it does against the installed build (`hermes_cli/config_defaults.py`) or the Hermes docs. If the installed build and docs disagree, say so.
3. **Provider behavior** — do not assume a provider reports cache fields, honors a pricing tier, or counts tokens a certain way. Probe it or check its current docs before claiming.
4. **Unverifiable claims** — mark them UNVERIFIED in the report. A labeled unknown beats a confident guess.

A proposal that cites an unverified key, value, or mechanism is incomplete. Complete the pre-check or drop the proposal.

### Procedure

**1. Establish the baseline.** Run the script for the window in question. Record: total input, per-task breakdown, top-10 sessions, cron offender stats, tool-char share, cache columns, cost totals. Save the output next to the changes you plan to make.

Done when: every number in the final report traces to a script line.

**2. Pre-check each candidate lever.** Before any lever enters a proposal, verify it on the live instance: key exists (`hermes config get`), current value known, mechanism matches the installed build or docs. Check the provider's reporting behavior before making cache-related claims.

Done when: every lever in the draft proposal has a verified key + current value, or is marked UNVERIFIED with what is missing.

**3. Rank and map.** Order consumers by tokens AND by estimated cost (they can disagree). For each of the top 3, name the pre-checked lever. If a consumer maps to no lever, say so explicitly instead of inventing one.

Done when: top 3 consumers each have a pre-checked lever or an explicit "no local lever" verdict.

**4. Propose changes.** Proposals in impact order, each with: config key or prompt edit, expected saving, revert path. Compute expected saving per billing_provider with that provider's cache discount applied; where the provider does not report cache fields, state the estimate is bounded and verify on the provider dashboard. Config edits go through `hermes config set` — direct file edits to config.yaml are blocked by the tooling (verified 2026-09-02). Cron prompt edits: back up the old prompt first, edit, then verify shape (`{"jobs": [...], "updated_at": ...}`) and schedules survived.

Done when: the user approved each change and it is applied AND read back verified.

**5. Schedule the delta check.** Create a one-shot cron ~30 days out that re-runs this audit with the old baseline in its prompt. Include: baseline numbers, the list of applied changes, and per-change pass criteria (e.g. "job X avg prompt_tokens/fire >2M = not fixed").

Done when: the delta-check cron exists (`hermes cron list` shows it) and its prompt contains the baseline numbers, applied-change list, and pass criteria.

### Interpretation

Rank consumers, then map each to a pre-checked lever:

| Finding | Signal | Lever |
|---------|--------|-------|
| Long sessions dominate | Top sessions >200 api_calls, >40M input | First check the provider's cache discount. With caching, a warm session re-reads history cheaply; reset only when uncached dead weight dominates. Every reset re-pays the full prefix at full price. Check compression actually fires (compact count >0) |
| background_review large | task='background_review' >5% of total | `auxiliary.background_review.max_input_tokens` (default 600000) or `enabled: false`; manual `/refine` still works. Also route `auxiliary.background_review.model` to a cheaper model — a different model replays a compact digest instead of the full transcript |
| One cron job dominates | avg prompt_tokens/fire in the millions | Rewrite its prompt with a read budget: date-bounded source data, skip oversized items, narrow scroll windows, stop-at-cap and defer |
| Cron cost at the floor | avg tokens/fire near the per-call floor (25-30k) | The fixed scaffolding floor times fire count dominates: reduce fire frequency or merge jobs rather than shrinking prompts |
| Tool results dominate context | tool chars >70% of STORED active content (upper bound on sent; script prints the share) | `tool_output.max_bytes` (default 50000), `file_read_max_chars` (default 100000), spillover budget. Under provider caching, savings concentrate on the first turn a result appears and on compression avoidance — stable results re-read via cache are cheap. Oversized results spill to `$HERMES_HOME/cache/spillover/` as preview + path |
| Duplicate skill loads | same skill body loaded N times per session | Behavioral rule: never re-call skill_view for a skill already in context. Under caching the direct re-read is discounted; the real damage is context pressure triggering earlier compression, which busts the cache |
| High per-call floor at short sessions | script's weighted avg for <50-call sessions (typically 25-40k) | Fixed baseline (system prompt + tool schemas) — reduce via the per-turn overhead procedure above, not this audit |
| Subagent fan-out heavy | many delegate_task spawns; each re-pays the full system prompt + tool schemas uncached | Route `delegation.model` to a cheaper model for mechanical subtasks; batch tool calls into one execute_code call instead of fanning out; cap concurrent subagents |
| Compression firing often | compression events per session high; `compression_ineffective_count` >0 | Each compression rewrites history into a new prefix = full-price cache miss for everything after. Weigh `compression.threshold` against the provider's cache discount; route the compression summarizer (`auxiliary.compression.model`) to a cheap model — it reads the entire conversation |
| cache_read ≈ 0 on a provider | provider emits no cached-token field at all (then local input IS the full prompt and share is unmeasurable — check the provider's billing dashboard), vs provider reports the field but it is 0 (caching genuinely off: short sessions, unstable prefix, or TTL expiry — investigate) |
| Cheap-task traffic on premium models | title_generation/approval/vision rows on the main model | Route each `auxiliary.<task>.model` to a flash-class model; near-free savings on frequent small calls |
| Token ranking ≠ cost ranking | a cheap model consumes 10x the tokens of a premium one | Rank by `estimated_cost_usd`/`actual_cost_usd` per billing_provider; exclude `billing_mode='subscription_included'` rows (zero marginal cost) from optimization effort |

### Aggregate Pitfalls

1. **Open state.db read-only** (`file:...?mode=ro`, uri=True, URL-encode the path). It is live and can be hundreds of MB; a writer connection risks locks.
2. **input_tokens semantics differ by provider wire format.** Anthropic-style wires report `cache_read_tokens` IN ADDITION to input (true prompt ≈ input + cache_read + cache_write); OpenAI-style `prompt_tokens` includes cached tokens as a subset. Empirical check: if cache_read > input_tokens for a row, that provider excludes cache from input. Never compare raw input_tokens across providers; compute effective prompt per billing_provider. The cache-share ratio is only meaningful within one convention.
3. **jobs.json has two observed shapes** — `{"jobs": [...], "updated_at": ...}` and a bare list. Handle both before and after editing; verify the container shape after any write.
4. **Cache-share 0 does not prove no caching.** Some providers return no cached-token field in `usage` at all (one such provider verified 2026-09-02 — its usage object carried only prompt/completion/total), so local telemetry is blind to their caching. Others report cache reads per call. Check each provider's docs and billing dashboard for ground truth.
5. **sessions.input_tokens and session_model_usage differ by attribution**, not just timing: task rows are cumulative per session and attributed by last_seen (pulling pre-window spend into the window), while per-session ranking uses start/activity dates. State the skew direction when totals do not reconcile; never mix the two totals in one sum.
6. **token_count column is often NULL** — measure content size with LENGTH(), and remember chars ≈ tokens/4 only as a rough proxy.
7. **Compaction and inactivity skew stored content.** Filter messages by `active=1`: compacted rows were replaced by summaries and inactive rows are no longer sent. Stored active content is still an upper bound on sent content (truncation already applied at capture time). Live-vs-compacted splits explain why a session's DB size can exceed its context.
8. **A single fire can dwarf everything** — scan for max(prompt_tokens) in the cron ledger before averaging; one multi-million-token fire hides inside a healthy-looking mean.
9. **Cron ledger prompt_tokens semantics are per-fire and under-documented** — one line per fire, but an agentic fire makes many API calls with context re-sent each call. Treat avg tokens/fire as a lower bound on true cron input and verify against a fire's session rows when precision matters.
10. **Per-call averages must be weighted** — SUM(input)/SUM(calls), never AVG of per-session ratios; a 200-call session and a 10,000-call session count equally otherwise.
11. **tool_output.max_bytes caps TERMINAL output only** (verified config_defaults.py: "terminal_tool output cap in chars"). Do not grade read_file/skill_view/web-result overages against it; read_file has its own `file_read_max_chars` (default 100k). The script's "active results over 50k" line counts ALL tools, so most of its count lies outside the terminal cap's mechanism — split the overage by tool_name before calling the cap failed.
12. **skill_view stored results have two shapes** — raw JSON (carries `"name": "…"`) and compaction-demoted placeholders (`[skill_view output demoted at compaction …]`). Extract names only from the JSON field; placeholders cannot be name-matched. A measured duplicate-load rate is therefore a LOWER bound; report the unparsed count alongside.
13. **Never confirm a cron job exists by substring on the raw jobs.json text** — another job's prompt can reference the id (an audit job's prompt cites baseline job ids). Parse the container and match on each job's `id` field; a missing id means the job was deleted (check the ledger for its historical fires).

### Verification (aggregate)

- [ ] Script ran read-only against every relevant profile DB (default + any active profiles)
- [ ] Totals cross-checked with attribution skew stated (task rows by last_seen vs sessions by start/activity)
- [ ] Each top consumer mapped to a pre-checked lever or marked "no local lever"
- [ ] Every proposed lever pre-checked: key exists, current value read live, mechanism confirmed
- [ ] Applied changes read back verified (`hermes config get`, cron jobs.json re-parse)
- [ ] Old prompts/config backed up with paths recorded
- [ ] Delta-check cron scheduled with baseline + pass criteria in its prompt

## Common Pitfalls

| Problem | Cause | Fix |
|---------|-------|-----|
| Measured row reads "unmeasured" | Run with `--skip-live`, or the one-shot failed to write its usage file | Run without `--skip-live`; check the live-run error line |
| Skills index independent estimate reads 0 while budget shows thousands | The render's `<available_skills>` block was searched in the wrong tier | The script searches volatile first, then stable (current layout keeps the index in volatile) |
| Provider measured ~3k below the sum of estimates | Tokenizer difference: chars/4 and the rough estimator both over-count JSON tool schemas | Trust the provider number for ratios; use category deltas for drift detection, not absolute truth |
| Memory block 0 B but recall text arrives every turn | Provider (Mnemosyne) injects recall outside the prompt-size budget | Measure recall in-session; trim memory facts, not the block |
| Skills index cost ignores top-K settings | Current builds inject the full index | Optimize via `skills.disabled` and description length, not top-K |
| User profile flagged TRUNCATED | Over the 3,000-char injection cap | Trim under cap; until then the tail is lost every turn |
| Disabling a toolset breaks a workflow | A skill depends on that toolset | Check `requires_toolsets` in the skill's frontmatter before disabling |
| Memory pruning removes a needed fact | Aggressive removal without checking last-used | Check recall_count and last_recalled before removing |
| Compression triggers too early / too late | `threshold` set too low / too high | Tune with `hermes-compression-tuning`; compression summaries themselves cost tokens |
| Mandatory skill overhead seems unavoidable | Configured in behavioral rules | Accept the cost, or remove the mandatory load requirement in config |

## Verification

- Audit script (live) prints a full category table with a provider-measured TOTAL row
- Re-run audit script — per-category deltas and the measured total dropped
- `hermes tools` — confirm only needed toolsets enabled
- Monitor next session: quality should not degrade from reduced context