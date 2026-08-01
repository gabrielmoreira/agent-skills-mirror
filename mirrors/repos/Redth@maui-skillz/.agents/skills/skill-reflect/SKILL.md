---
name: skill-reflect
description: >
  Use this skill to reflect on the skills I used this session, review this session for
  skill feedback, how did the skills perform, improve the skills I just used, capture
  skill friction from this session, check which skills had problems, give feedback on
  the skills I used, review skill performance, surface skill issues from today's work.
license: MIT
---

# skill-reflect

Universal cross-agent skill for post-session reflection on **distributed skill performance**.
Detects friction, classifies it, proposes a concrete fix and a verifiable eval, scrubs PII,
and writes a local Markdown artifact. GitHub issue filing is available on an explicit second
consent only.

> **Distributed skills** = skills installed from a plugin, marketplace, or external repo —
> those with resolvable provenance outside the user's own project.

---

## Purpose

Skills shipped via plugins or marketplaces have no feedback loop once deployed. When an
agent follows stale guidance, retries a broken command, or works around a missing case, that
signal disappears. `skill-reflect` captures it — with consent — and routes structured,
PII-safe findings back to the skill's author. Evals are emitted alongside every finding so
the author can verify a fix actually helps.

---

## When to use

- At or near the end of a session in which one or more **distributed** skills were invoked.
- In response to a user request to review skill performance (explicit invocation).
- When a nudge from `skill-reflect-auto` surfaces a pending-review marker at session start.

## When NOT to use

- For the user's **own in-repo skills** — unless the user explicitly scopes them in (e.g.
  `scope.skills` in `skill-reflect.config.json` or a direct verbal instruction to include
  them).
- For `skill-reflect` and `skill-reflect-auto` — always excluded (`scope.excludeSkills`).
- When no distributed skills were invoked in the session (nothing to review).
- To **fix the skill yourself** — produce feedback for the author; do not modify the skill.

---

## Two consent gates

**Gate 1 — Review consent.** Before examining any session data, tell the user what you will
read (skill names, tool outcomes, friction signals — never secrets or values) and what you
will produce. Proceed only on explicit approval.

**Gate 2 — Send consent.** After the local artifact is drafted and the redaction preview is
shown and confirmed, offer to file a GitHub issue. Ask once; if the user declines, write the
local artifact and stop. Never auto-file.

---

## 6-Step Workflow

### Step 1 · Consent + scope

Introduce the review. Describe the skills you intend to cover (default: all distributed
skills in scope) and what the output will be. If a calling skill injected its own identity
or a specific session id into the nudge, acknowledge that context and honor it as the scope;
attribution confidence is higher when the caller self-identifies. Confirm the user wants to
proceed before doing anything else. (See `references/session-sources.md` §Scope injection.)

### Step 2 · Locate sessions and skill usage

Identify which distributed skills were active and their approximate time windows. On
**Copilot CLI** this means querying the session store; on **Claude Code / Gemini CLI** it
means reading the transcript JSONL; on **Cursor and other Tier C hosts** it means reflecting
on the visible conversation only. Collect skill names and invocation counts only — never
read secrets, credential values, or private file contents. See `references/session-sources.md`
for host-specific recipes and generic skill-usage signals.

### Step 3 · Detect friction

For each skill's active window, scan for friction signals: tool failures, repeated retries
of the same call, error names (not values), workaround chains, and escalation to manual
steps. Attribute a signal to a skill by proximity in the session timeline. Consult the
pattern catalog before asserting a finding — friction may be the task's fault, not the
skill's. See `references/friction-rubric.md` for all pattern definitions and detection
heuristics.

### Step 4 · Classify

For each confirmed friction signal, construct a `FrictionFinding` object (CONTRACT §3).
Assign a `pattern` from the catalog, map it to a `category`, and score `severity`,
`confidence`, and `outcome`. Apply the false-attribution caution: when causal attribution is
uncertain, downgrade confidence to `Possible` and note the uncertainty in `evidence`. See
`references/friction-rubric.md` (false-attribution caution) and
`references/skill-improvement-taxonomy.md` (pattern→category mapping).

### Step 5 · Propose fix and eval

For every `FrictionFinding`, write a `proposedFix` (a concrete, actionable change the skill
author can make — add a case, correct a command, clarify a step) and a `proposedEval` in
both the **skill-creator `evals.json`** format and the **portable** `must_contain` /
`must_not_contain` form. The eval prompt should be a realistic task that exercises the
proposed fix. See `references/eval-format.md` for authoring rules and worked examples.

### Step 6 · Scrub → preview → report

Paraphrase all findings (no PII, no verbatim excerpts, no absolute paths, no secrets). Run
`scripts/scrub.py` as a deterministic backstop if available. Show the **full artifact text
and a redaction summary** to the user before writing anything; ask for explicit confirmation.
Resolve the routing for each finding per `references/provenance-routing.md`. Write the local
artifact to `.skill-feedback/<YYYY-MM-DD>-<skill-slug>.md`. Then, if destination mode is
`issue` or `ask`, offer Gate 2. See `references/privacy-scrub.md` for scrubbing rules and
`references/reporting.md` for the full artifact template and field-filling guide.

---

## Default output

```
.skill-feedback/<YYYY-MM-DD>-<skill-slug>.md
```

`<skill-slug>` = skill name lowercased, non-alphanumerics collapsed to `-`.
Example: `my-ci-helper` → `.skill-feedback/2025-07-07-my-ci-helper.md`

Config key `artifactDir` overrides the `.skill-feedback/` base directory. Nothing is written
until Step 6 confirmation is given.

---

## Safety rules (enforced regardless of config)

| Rule | Detail |
|---|---|
| No PII | Names, emails, tokens, keys, absolute paths, machine names, private URLs, verbatim transcript excerpts — never in any artifact |
| Redaction preview mandatory | Always show the full proposed artifact and a scrub summary before writing. `privacy.redactionPreview` is hard-`true`. |
| Verbatim excerpts forbidden | `privacy.allowTranscriptExcerpts` is hard-`false`. All content is paraphrased. |
| Consent before every write | Nothing written to disk; nothing filed as an issue until the relevant gate is passed. |
| Paraphrase, don't quote | Refer to tool/variable/error names, never their runtime values. |

---

## Session store and transcript availability (by host)

On **Copilot CLI**: the session store is queryable from inside the agent. Skill invocations
appear as `tool_requests` rows; the store enables richer multi-session signals.

On **Claude Code / Gemini CLI**: a transcript JSONL is typically available via
`transcript_path`. Parse it for `SKILL.md` loads, Skill tool calls, and nearby failures.

On **Cursor, Windsurf, Codex CLI, cloud agents (Tier C)**: no store or transcript is
accessible. Reflect on the **visible conversation only**. Findings may be fewer; lower
confidence is normal.

Details and fallback rules: `references/session-sources.md`.

---

## Reference files

| File | Authored by | Contents |
|---|---|---|
| `references/session-sources.md` | M1 | Host recipes, generic signals, scope injection |
| `references/friction-rubric.md` | M1 | Severity/confidence/outcome; pattern catalog; false-attribution caution |
| `references/skill-improvement-taxonomy.md` | M1 | Category definitions, typical fixes, pattern→category table |
| `references/privacy-scrub.md` | separate agent | Scrubber spec, redaction categories, paraphrase protocol |
| `references/eval-format.md` | separate agent | Eval authoring rules, both format examples |
| `references/reporting.md` | M1 | Artifact template, field-filling guide, file naming |
| `references/provenance-routing.md` | separate agent | Skill-name→repo resolution; registry; fallback |
