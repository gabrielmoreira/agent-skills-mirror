---
name: agent-prompt-engineering
description: Load when writing prompts for sub-agents, generation CLIs (jules, agy, claude-code, opencode, codex), or any model emitting structured artifacts (SVG, JSON specs/ops, code files). Turns vague instructions into machine-checkable contracts with mandatory verification gates. Not for casual chat with no artifact deliverable, and not for authoring a new skill file (create-skill).
version: 1.0.1
alwaysApply: false
---

## Overview

This skill generalizes the fix proven in the svg-vault audit: agent-generated output rots when prompts express quality as adjectives and command no verification. The audit found, in one corpus:

| Defect | Count | Root cause in the prompt |
|---|---|---|
| Literal `\n` / `\t` / `\"` escapes in file bodies | **747 files** | "Write the SVG file" — no serialization contract, model pasted a JSON-escaped string as bytes |
| LLM commentary leaked after `</svg>` | **94 files** | No "output ends at `</svg>`, nothing after" rule and no gate to catch it |
| Duplicate attributes | **23 files** | No attribute rules, no validator commanded |
| Mismatched tags | **12 files** | Model hand-wrote XML text; no parse check required |

Every defect traces to the same prompt shape: **artifact written as free text, quality expressed as adjectives ("clean", "premium", "consistent"), zero verification commanded.** The fix that worked: models emit JSON specs/ops validated by ajv, ONE canonical serializer writes bytes, Gate0+Gate2 run on every write. This skill codifies that fix into a repeatable prompt-writing method.

**Core principle:**

> Describe OUTPUT CONSTRAINTS + VERIFICATION, not ADJECTIVES.

An agent cannot act on taste words. "Premium", "clean", "high quality", "consistent", "polished" compile to nothing — the model nods and does whatever it was going to do anyway. A constraint it can *check itself against* compiles to behavior.

Test every sentence of your prompt with: **"Could a validator script enforce this?"** If no, either rewrite it until yes, or delete it. A prompt where every requirement is machine-checkable is a prompt whose output is machine-checked.

Corollary: **the prompt is a contract, not a mood board.** Contracts have (a) an exact deliverable spec, (b) an acceptance test, (c) defined behavior on failure. Your prompt needs all three.

**Operational note for this repo:** `agy` (Gemini) is the default heavy-lift CLI, with `claude-code`, `opencode`, `codex` as alternates. **jules and agy need heavy hand-holding** — assume the agent will do the laziest thing your prompt technically permits.

## When to Use

Load this skill when:

- Writing prompts for sub-agents spawned via `delegate_task` or similar delegation mechanisms.
- Writing prompts for generation CLIs: `agy`, `jules`, `claude-code`, `opencode`, `codex`.
- Commissioning any model to emit structured artifacts (SVG, JSON specs/ops, YAML frontmatter, code files, batch icon sets).
- Reviewing or debugging a delegated prompt that produced defective output (escaped characters, commentary leaks, duplicates, missing files).
- Designing a verification gate or serializer for a new artifact type.

Do NOT load this skill for casual conversational prompts with no artifact deliverable.

## Prerequisites

- **Windows host (primary):** PowerShell is the default shell. Use `Get-Content` / `Read` for spot-reading artifacts. Path separators in commands should use forward slashes for Node.js scripts (`node gate.mjs`) but Windows backslash paths (`~`) for filesystem references.
- **Node.js:** Required for gate scripts, serializers, and ajv validation. Ensure `node` is on `PATH`.
- **ajv:** Install if validating JSON schemas: `npm install -g ajv` or use a local `node_modules` copy.
- **Gate scripts:** If a gate does not yet exist for the artifact type you are commissioning, **write the gate before writing the prompt.** A 20-line parser/linter script is cheaper than one triage pass over 747 broken files.
- **Project gates:** Inspect gate/serializer files in the target project when you need the svg-vault case study, ajv pipeline, or serializer architecture. This folder does not ship those helpers — write them in the project before the prompt.

## Procedure

### Step 1 — Replace every adjective with a machine-checkable constraint

Go through your draft prompt. For each quality word ("clean", "premium", "consistent", "robust", "polished"), replace it with one of:

- A **limit**: "Max 2 stop-colors per gradient."
- An **allowlist**: "Allowed elements: `svg, g, path, circle, rect, line, polyline, polygon, defs, linearGradient, stop, title`."
- A **forbidden pattern**: "No `<filter>`, no `<foreignObject>`, no `<script>`. Contains NO literal two-character sequences `\n`, `\t`, or `\"`."
- A **gate command**: "After writing, run `node validate.mjs <file>`; if it exits non-zero, fix and re-run until it passes."

If a sentence cannot be converted to any of these, delete it. It is padding that the agent will ignore.

**Before (produced the 747-file disaster):**

> Generate 20 SVG icons for the mythology theme. Make them clean, consistent, and premium quality. Save them in assets/mythology/.

Nothing here is checkable. No viewBox rule, no encoding rule, no filename rule, no gate.

**After (bulletproof):**

> Generate 20 SVG icons for the mythology theme into `assets/mythology/`.
>
> **Output contract — every file MUST satisfy all of these (a validator will check):**
> - File starts with exactly `<svg` and ends with exactly `</svg>` followed by a single trailing newline. Zero bytes of prose, markdown, or code fences before or after.
> - Contains NO literal two-character sequences `\n`, `\t`, or `\"` — real newlines and real quotes only. If your output pipeline JSON-encodes strings, you are doing it wrong; use the write path below.
> - Root: `viewBox="0 0 24 24"`, `xmlns="http://www.w3.org/2000/svg"`. No `width`/`height` attributes.
> - No element may repeat an attribute name. Allowed elements: `svg, g, path, circle, rect, line, polyline, polygon, defs, linearGradient, stop, title`. Everything else (including `filter`, `image`, `script`, `style`, `foreignObject`) is forbidden.
> - Gradients: max 2 `<stop>` elements. Colors from this palette only: `#1A1B2E #4F5D95 #C9A227 #F4F1E8`.
> - Filenames: `myth-{subject}.svg`, lowercase kebab-case, ASCII.
>
> **Write path:** do NOT write SVG text directly. Emit a JSON spec per icon and run `node serialize.mjs spec.json` — the serializer owns the bytes.
>
> **Gate (mandatory):** after each write, run `node gate.mjs assets/mythology/`. Exit code non-zero = you are not done. Read the errors, fix, re-run. Do not report completion until the gate passes on all 20 files.

### Step 2 — Embed labeled GOOD/BAD examples for every critical rule

Agents pattern-match examples far more reliably than they interpret adjectives. For every critical rule, embed one GOOD and one BAD sample — the bad one drawn from a real failure.

```
GOOD (real newlines, single attributes, ends at </svg>):
<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 2L2 22h20z" fill="#4F5D95"/>
</svg>

BAD — REJECT if your output looks like either of these:
1) Escaped whitespace leaked into the file (this is a JSON string pasted as bytes):
<svg viewBox=\"0 0 24 24\">\n  <path d=\"M12 2L2 22h20z\"/>\n</svg>

2) Duplicate attribute + commentary after the close tag:
<svg viewBox="0 0 24 24" viewBox="0 0 24 24">...</svg>
Here is your icon! Let me know if you'd like any changes.
```

Rules for the examples themselves:

- Label them `GOOD:` / `BAD — REJECT:` explicitly. Unlabeled examples get imitated indiscriminately, including the bad ones.
- Keep the bad example *realistic* — copy an actual defective file from a past run, not a strawman. The model needs to recognize its own failure mode.
- One pair per critical rule. Ten pairs for one rule is padding; zero pairs for a rule the agent keeps breaking is negligence.

### Step 3 — Command a verification gate with a bounded loop

"Check your work" and "double-check the output" are adjectives in disguise — the agent will "check" by rereading its own text and approving it. The prompt must command an executable gate with a loop:

```
After writing each file, RUN:
    node gate.mjs <file>
- Exit 0: proceed to the next file.
- Exit non-zero: read stderr, fix THAT file, re-run the gate. Repeat until exit 0.
- If the same file fails the gate 3 times, STOP, do not write more files, and
  report the file path + full gate stderr as your final output.
Never report success without pasting the final passing gate command + its output.
```

Key properties:

1. **A command, not an intention.** Name the exact executable and arguments.
2. **A loop, not a glance.** Fix → re-run → until pass, with a bounded retry (3) and a defined stop.
3. **Proof of execution.** Requiring the agent to paste the gate's output in its report makes "I validated it" falsifiable.
4. **Generate via script, don't write text directly.** For any structured format (SVG, JSON, YAML frontmatter), the strongest gate is architectural: the agent emits a *spec*, a canonical serializer emits *bytes*. The model never touches the byte stream, so escape/encoding/tag-balance bugs become impossible rather than merely detected. This is the svg-vault's ajv-spec + single-serializer + Gate0/Gate2 design — reuse the pattern anywhere.

### Step 4 — Add a dedup / idempotency rule for batch prompts

Batch prompts without a dedup instruction produce duplicates — the agent doesn't know the corpus exists unless told to look. Every batch/generation prompt must state:

1. **The check:** "Before creating each item, list existing outputs: `ls assets/consolidated/` (or run `node manifest.mjs list`)."
2. **The dedup key:** the exact identity function. E.g. "Two icons are duplicates if they share the same `theme` + `subject` slug, regardless of filename casing or visual differences. Key: `${theme}-${subject}` lowercase."
3. **The action on hit:** "If the key exists: SKIP (do not overwrite, do not create `-2`/`-final`/`-new` variants) and log `SKIP <key>` in your report."

Without a stated key, the agent invents one per run ("well, *this* griffin faces left...") and you get near-duplicates. Idempotency is the acceptance test: **running the same prompt twice must change nothing on the second run.** Say that sentence verbatim in batch prompts — it collapses a whole class of ambiguity.

### Step 5 — Define failure behavior explicitly

Unspecified failure handling means the agent proceeds and improvises — it pads malformed input with invented data, skips broken steps silently, and reports success. Every prompt needs a failure clause:

```
FAILURE RULES:
- Malformed/missing input (spec doesn't parse, referenced file absent, schema
  mismatch): do NOT guess or fabricate values. Skip that item, record it in a
  `failures` list with the exact error, continue with the rest.
- A required command fails (serializer, gate, git): retry ONCE. Second failure:
  STOP the whole run — do not attempt workarounds or alternative tools.
- Final report ALWAYS includes: items succeeded, items skipped (with reasons),
  items failed (with errors). "Done" with zero counts is not a valid report.
- NEVER delete or overwrite files not listed in this prompt's scope.
```

Tune stop-vs-continue per task: a batch of 200 independent icons → skip-and-continue; a 4-step pipeline where step 2 feeds step 3 → stop. The point is that *you* chose, not the agent.

### Step 6 — Make the prompt self-contained

Sub-agents spawned via `delegate_task` have **no parent memory**. CLI agents (`agy`, `jules`, `codex`, `opencode`) see **only the prompt text and the filesystem** — none of your conversation, none of your mental context, no "as discussed". Pronouns and references like "the usual format", "same as last time", "our palette" resolve to nothing.

Bundle all six blocks into every delegated prompt:

```
┌─ BULLETPROOF PROMPT TEMPLATE ────────────────────────────────────────────┐

## GOAL (1–3 sentences)
Generate <N> <artifact type> for <purpose> into <exact path>.

## INPUTS
- <path/to/input1> — <what it is, exact schema/format>
- (Paste small inputs inline; give absolute paths for large ones.)

## OUTPUT CONTRACT (machine-checkable — a gate will verify every rule)
- Exact file format, first/last bytes, encoding, filename pattern
- Frontmatter/schema fields with types and allowed values
- Forbidden patterns (escapes, extra prose, forbidden elements/keys)
- Numeric limits (max stops, max size, max depth)

## EXAMPLES
GOOD:
<one complete, minimal, passing artifact>
BAD — REJECT:
<one real past failure, labeled with what's wrong>

## PROCEDURE
1. Dedup: run <list command>; skip any item whose key <exact key> exists.
2. For each remaining item: emit spec → run <serializer command>.
3. Gate: run <gate command>; on failure fix and re-run (max 3 tries/file).

## FAILURE RULES
- Malformed input → skip + record, never fabricate.
- Command fails twice → stop entire run, report.

## REPORT (your final output — exactly this, nothing else)
- created: [...], skipped: [...], failed: [{item, error}]
- Paste the final passing gate command and its full output.
└──────────────────────────────────────────────────────────────────────────┘
```

Litmus test: could a competent stranger with no repo access beyond the filesystem execute this prompt correctly on the first try? If they'd have to ask you a question, the agent will instead *guess* the answer to that question.

### Step 7 — For JSON-mode pipelines, use the spec/op + ajv pattern

For models that emit structured specs/ops (the svg-vault `apply-animation` and `edit-op` flows are the reference), the pipeline is fixed:

1. **Force JSON-only output** in the prompt:
   > Output a single JSON object conforming to the schema below. No markdown fences, no prose before or after, no comments inside. First character `{`, last character `}`.

2. **Paste the actual JSON Schema** into the prompt (not a description of it — the schema itself, `required` arrays and `enum`s included). The schema *is* the constraint spec.

3. **Strip defensively anyway:** models add ```` ```json ```` fences despite instructions. Before parsing: trim, strip leading/trailing fences, extract the outermost `{...}`.

4. **Validate with ajv** (`allErrors: true`) against the same schema you pasted.

5. **One retry with the errors appended:**
   > Your previous output failed validation:
   > `<ajv errors JSON>`
   > Previous output:
   > `<the bad JSON>`
   > Emit a corrected JSON object. Fix ONLY the listed violations; change nothing else.

6. **Second failure → hard fail.** Log both attempts + errors, surface to the caller. Do not loop indefinitely and do not hand-patch the JSON — a model that fails schema twice is confused about the task, and patching hides that.

The validated spec then goes to the canonical serializer/applier. **The model never authors artifact bytes** — that division of labor is what took escape bugs from 747 to 0.

### Step 8 — Verify the agent's run yourself (after delegation)

Trust nothing in the agent's self-report until you've confirmed the gate actually fired:

1. **Run the gate yourself on a sample** — e.g. `node gate.mjs assets/mythology/` on 3–5 of the new files. The agent saying "all gates passed" is a claim; your terminal output is evidence.
2. **Confirm the gate *fired*, not just exit 0.** Exit 0 on zero files scanned, a mocked command, or a gate run against the wrong directory all look like success in a report. Check that the gate's output names the actual new files. If your gate has verbose mode, demand it in the report (`--list` / per-file lines).
3. **Spot-read one artifact raw** (`Get-Content` / `Read`) — look for the classic tells: `\n` literals, prose after the terminator, fences.
4. **Re-run the dedup check:** did the batch create keys that already existed?
5. **Diff the file count** against the report's `created` count. Mismatch = silent skips or silent extras.

If any of these fail, the fix goes into the *prompt* (a new constraint, a new BAD example, a tighter gate) — not into a one-off manual cleanup. Every manual cleanup you do without updating the prompt will be repeated by the next run.

## Examples

### Minimal bulletproof prompt for a single SVG file

```
## GOAL
Generate 1 SVG icon (mythology: griffin) into assets/mythology/myth-griffin.svg.

## OUTPUT CONTRACT
- File starts with exactly `<svg` and ends with exactly `</svg>` + single newline.
- No literal `\n`, `\t`, or `\"` sequences. Real newlines and quotes only.
- Root: viewBox="0 0 24 24", xmlns="http://www.w3.org/2000/svg". No width/height.
- Allowed elements: svg, g, path, circle, rect, line, polyline, polygon, defs, linearGradient, stop, title.
- No element may repeat an attribute name.
- Colors from: #1A1B2E #4F5D95 #C9A227 #F4F1E8. Max 2 stops per gradient.

## EXAMPLES
GOOD:
<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 2L2 22h20z" fill="#4F5D95"/>
</svg>

BAD — REJECT (escaped whitespace + commentary after close):
<svg viewBox=\"0 0 24 24\">\n  <path d=\"M12 2L2 22h20z\"/>\n</svg>
Here is your icon!

## PROCEDURE
1. Emit a JSON spec for the icon.
2. Run: node serialize.mjs spec.json
3. Gate: node gate.mjs assets/mythology/myth-griffin.svg
   - Non-zero exit: read stderr, fix, re-run. Max 3 tries.
   - 3 failures: STOP, report path + stderr.

## FAILURE RULES
- Command fails twice → stop, report.
- NEVER delete or overwrite files not listed in this prompt's scope.

## REPORT
- created: [...], skipped: [...], failed: [{item, error}]
- Paste the final passing gate command and its full output.
```

### JSON-mode prompt fragment with ajv validation

```
Output a single JSON object conforming to the schema below. No markdown fences,
no prose before or after, no comments inside. First character `{`, last character `}`.

<schema>
{ "type": "object", "required": ["theme","subject","paths"],
  "properties": {
    "theme": { "type": "string", "enum": ["mythology","nature","abstract"] },
    "subject": { "type": "string", "pattern": "^[a-z0-9-]+$" },
    "paths": { "type": "array", "items": { "type": "string" }, "minItems": 1 }
  }, "additionalProperties": false }
</schema>
```

After receiving the JSON: strip fences, extract outermost `{...}`, validate with ajv (`allErrors: true`). On failure, send one retry with errors appended. Second failure → hard fail, log both attempts.

## Pitfalls

1. **Adjective prompting.** "Clean/premium/consistent/robust" → unenforceable → ignored. Replace every adjective with a limit, an allowlist, or a gate. (Cause of the original svg-vault corpus rot.)

2. **Model writes artifact bytes directly.** Hand-authored XML/JSON text through a chat pipeline yields escape leaks (747 files), commentary after the terminator (94), duplicate attrs (23), mismatched tags (12). Use spec → canonical serializer instead.

3. **"Check your work" instead of a gate command.** The agent rereads and approves itself. Name the executable, require the loop, require pasted proof.

4. **No dedup key in batch prompts.** Guaranteed duplicates and `-final-2` variants. State check command + identity key + skip behavior; require idempotency.

5. **Undefined failure behavior.** The agent fabricates missing data and reports green. Write skip/stop/report rules explicitly.

6. **Context by reference.** "Use our standard format" — the sub-agent has no memory of your standards. Paste the schema, the palette, the paths.

7. **Trusting exit 0 / the self-report.** Gates that scanned nothing, reports that claim untested success. Verify the gate fired on the real files, yourself.

8. **Unbounded retry loops.** "Fix until it passes" with no cap = an agent burning an hour rewriting the same broken file, or "fixing" the validator. Cap retries (3), define the stop state.

## Verification

### Pre-send checklist (run before sending ANY delegated prompt)

- [ ] **CONSTRAINT** — every requirement machine-checkable; zero unbacked adjectives; exact format/frontmatter/filename/encoding spec; forbidden patterns listed.
- [ ] **EXAMPLE** — ≥1 labeled GOOD + ≥1 labeled BAD (from a real failure) per critical rule.
- [ ] **GATE** — exact validator command; fix-and-rerun loop; retry cap + stop state; proof-of-run pasted in report; serializer-writes-bytes where possible.
- [ ] **DEDUP** — existing-output check command; explicit dedup key; skip-don't-variant; idempotent on re-run.
- [ ] **FAILURE** — malformed input → skip+record, never fabricate; command failure → retry once then stop; report always lists created/skipped/failed.
- [ ] **CONTEXT** — self-contained: goal, inputs, full schema, examples, commands, report format all pasted; no pronouns pointing outside the prompt.

If any box is unchecked, the prompt is not done. The 747 files were cheaper to prevent than to repair.

### Post-run verification (you, after delegation)

Run these commands yourself to confirm the agent's self-report:

```powershell
# 1. Run the gate on a sample of new files
node gate.mjs assets/mythology/

# 2. Spot-read one artifact raw — look for \n literals, prose after </svg>, fences
Get-Content assets/mythology/myth-griffin.svg -Raw

# 3. Re-run the dedup check — did the batch create keys that already existed?
node manifest.mjs list

# 4. Diff the file count against the report's created count
(Get-ChildItem assets/mythology/*.svg).Count
```

Expected gate output (success): per-file lines naming each actual new file, exit code 0. If the gate output is empty or names zero files, it scanned nothing — investigate. If `Get-Content` shows literal `\n` or `\t` sequences or prose after `</svg>`, the serializer was bypassed — the prompt needs a tighter write-path constraint.

If any verification fails, the fix goes into the *prompt*, not into manual cleanup.

## Related skills

- **svg-vault** — the source case study; load for the full ajv-spec + single-serializer + Gate0/Gate2 architecture and its gate/serializer implementations in the target project.
- **agent-delegation** — if available, for the `delegate_task` mechanics and sub-agent lifecycle.
