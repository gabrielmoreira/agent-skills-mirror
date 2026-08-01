# Eval Format — Turning a `FrictionFinding` into a Proposed Eval

_This file is the authoring guide referenced by CONTRACT §4._

---

## 1. Why every finding carries a proposed eval

A `proposedEval` closes the feedback loop: you can't confidently accept a skill change
unless you can verify that change actually fixes the observed problem and doesn't break
anything else. The eval is the machine-checkable form of the fix criterion.

---

## 2. Category → eval form mapping

The form emitted depends on the finding's `category` and `pattern`:

| `category` | `pattern` | Emitted form |
|---|---|---|
| `trigger-problem` | `trigger-miss` | Trigger eval set item — `{query, should_trigger: true}` |
| `trigger-problem` | `false-trigger` | Trigger eval set item — `{query, should_trigger: false}` |
| All other categories | any | Task eval entry in `evals/evals.json` |

---

## 3. Task eval entry (`evals/evals.json`)

Schema authority: `anthropics/skills` → `skills/skill-creator/references/schemas.md`.

### 3a. File shape (wrapped)

```jsonc
{
  "skill_name": "container-toolkit",
  "evals": [
    {
      "id": 1,                            // INTEGER — unique per eval in this file
      "prompt": "string",                 // realistic task that exercises the fix
      "expected_output": "string",        // brief human-readable description of success
      "files": [],                        // optional paths relative to skill root
      "expectations": [                   // FLAT ARRAY OF STRINGS — verifiable statements
        "The output uses the '--region' flag",
        "The output does not use the deprecated '--deploy-region' flag"
      ]
    }
  ]
}
```

Critical rules:
- `id` is an **INTEGER** (not a string, not a hash). Assign sequentially; when merging
  into an existing file use `max(existing_ids) + 1`.
- `expectations` is a **flat array of plain strings**. Each string is a natural-language
  statement a grader agent evaluates pass/fail. **NOT `{type, value}` objects.**
- Express "must not" conditions as negative statements: `"The output does not use X"`.
- The grader produces `grading.json` with a `summary.pass_rate`.

### 3b. Portable form (convenience — NOT skill-creator native)

```jsonc
{
  "id": "ct-7e2a1f",            // string finding-id (for traceability to FrictionFinding)
  "prompt": "string",
  "must_contain":     ["X"],    // 1:1 maps → "The output contains X"
  "must_not_contain": ["Y"]     // 1:1 maps → "The output does not contain Y"
}
```

Written to `.skill-feedback/evals/<slug>.portable.json`. Works with any lightweight harness
or manual inspection; not consumed by skill-creator directly.

**Portable → expectations string mapping:**
```
must_contain: ["--region"]        → "The output uses the '--region' flag"
must_not_contain: ["--deploy-region"] → "The output does not use the deprecated '--deploy-region' flag"
```

---

## 4. Trigger eval set item

For `trigger-problem` findings, emit a **trigger eval set item** — NOT an `evals.json` entry.

The trigger eval set is a JSON array:
```jsonc
[
  { "query": "Publish the latest build artifact to the container registry", "should_trigger": true },
  { "query": "List files in the current directory", "should_trigger": false }
]
```

Run with:
```bash
python scripts/run_eval.py --eval-set <trigger-set-file>
```

`run_eval.py` tests whether the skill's DESCRIPTION causes the model to trigger/read the
skill across multiple runs and reports a trigger rate.
- `should_trigger: true` = trigger-miss finding (query should invoke the skill but currently doesn't)
- `should_trigger: false` = false-trigger finding (query should NOT invoke the skill but currently does)

---

## 5. Authoring rules

### 5.1 The `prompt` / `query` field

- Write a **realistic, task-framing prompt** — the kind a real user would send.
  Do not write a test assertion or a description of the problem.
- Must be **self-contained**: no placeholders, no assumed context.
- Strip all PII: fictional service names, synthetic paths, generic role descriptions.

### 5.2 `expectations` strings (task evals)

- Each string is a **verifiable natural-language statement** about the skill's output.
- Assert the **corrected behaviour**: the thing that should appear after the fix.
- Guard the **specific regression** with a negative statement: `"The output does not use X"`.
- Avoid asserting exact prose that may legitimately vary across model runs.

### 5.3 Stable ids

- In `evals.json`: use **sequential integers**. When merging, use `max(existing_ids) + 1`.
- In portable form: reuse the parent `FrictionFinding.id` string verbatim for traceability.
- In trigger eval set: no per-item id needed.

### 5.4 Content rules (PII / privacy)

- `prompt`, `expected_output`, `files`, and all expectation strings must be
  synthetic/paraphrased.
- Never embed real file paths, hostnames, user aliases, or token values.
- The scrubber (`scripts/scrub.py`) runs as a backstop; author-side caution is primary.

---

## 6. Worked examples

### Example A — `wrong-or-stale-guidance` · `stale-guidance` → task eval entry

**Finding (abbreviated):**
```json
{
  "id": "ct-7e2a1f",
  "skill": "container-toolkit",
  "pattern": "stale-guidance",
  "category": "wrong-or-stale-guidance",
  "summary": "Skill docs show '--deploy-region'; the flag was renamed '--region' in v3.",
  "proposedFix": "Replace '--deploy-region' with '--region' throughout the skill guidance."
}
```

**`evals/evals.json` entry:**
```json
{
  "skill_name": "container-toolkit",
  "evals": [
    {
      "id": 1,
      "prompt": "Deploy the staging container image to the eu-west zone using container-toolkit.",
      "expected_output": "Agent invokes container-toolkit with the current '--region' flag and successfully queues the deployment.",
      "files": [],
      "expectations": [
        "The output uses the '--region' flag",
        "The output does not use the deprecated '--deploy-region' flag"
      ]
    }
  ]
}
```

**Portable form (`.skill-feedback/evals/container-toolkit.portable.json`):**
```json
{
  "id": "ct-7e2a1f",
  "prompt": "Deploy the staging container image to the eu-west zone using container-toolkit.",
  "must_contain":     ["--region"],
  "must_not_contain": ["--deploy-region"]
}
```

**Mapping:**
`must_contain: ["--region"]` → `"The output uses the '--region' flag"`
`must_not_contain: ["--deploy-region"]` → `"The output does not use the deprecated '--deploy-region' flag"`

---

### Example B — `trigger-problem` · `trigger-miss` → trigger eval set item

**Finding (abbreviated):**
```json
{
  "id": "ct-1c9e5d",
  "skill": "container-toolkit",
  "pattern": "trigger-miss",
  "category": "trigger-problem",
  "summary": "User said 'publish'; skill was not triggered — agent fell through to a generic fallback.",
  "proposedFix": "Add 'publish' and 'release image' to the skill's trigger vocabulary."
}
```

**Trigger eval set item (appended to a trigger set file):**
```json
[
  {
    "query": "Publish the latest build artifact to the container registry using container-toolkit.",
    "should_trigger": true
  }
]
```

Run with `python scripts/run_eval.py --eval-set <file>`.
No `evals/evals.json` entry is emitted for `trigger-problem` findings.

---

## 7. Quick checklist before committing an eval

- [ ] `trigger-problem` findings → trigger eval set item `{query, should_trigger}`; no `evals.json` entry
- [ ] All other findings → task eval entry in `evals/evals.json` with integer `id`
- [ ] `expectations` is a **flat array of plain strings** — NOT `{type, value}` objects
- [ ] At least one positive expectation captures the corrected behaviour
- [ ] At least one negative expectation (`"The output does not …"`) guards the observed regression
- [ ] Portable form accompanies each task eval (or config disables it)
- [ ] No PII, real paths, real hostnames, real token values anywhere

