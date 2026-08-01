# Skill Improvement Taxonomy

The six `category` values used in `FrictionFinding`, with definitions, typical fixes, and
the canonical `pattern` → `category` mapping. Use this file during Step 4 of the workflow.

---

## Category definitions

### `missing-case`

**Definition:** The skill works correctly for its common cases but lacks handling for a
specific variant the agent (or user) needed. The skill's guidance is silent on this case —
not wrong, just incomplete.

**Distinguishing feature:** There is no guidance to follow (not stale or incorrect guidance),
and the missing scenario is a plausible, real-world use of the skill's advertised capability.

**Typical fix:**
Add a new section, step, or example to the skill's SKILL.md (or referenced doc) that covers
the missing case. If the missing case requires a new tool or command, document it and add a
worked example. Update trigger phrases if the new case represents a distinct invocation
pattern.

---

### `wrong-or-stale-guidance`

**Definition:** The skill's guidance is present but factually incorrect or out of date
relative to the current version of the tool/API/service the skill uses.

**Distinguishing feature:** Following the skill's documented steps produced an error or wrong
result — the guidance exists but is wrong, not absent.

**Typical fix:**
Correct the specific command, flag, API call, or output description that is wrong. Add a
version note if the guidance is version-dependent. Consider adding a validation step or a
pointer to the upstream changelog if the underlying tool changes frequently.

---

### `missing-detail`

**Definition:** The skill's guidance is directionally correct but underspecified — a step
that requires more precision to execute reliably (e.g. a prerequisite not mentioned, an
ambiguous pronoun, a missing parameter type, or an example that does not reflect a real
invocation).

**Distinguishing feature:** The agent needed to make an assumption or ask the user for
clarification in order to proceed, even though the skill claimed to cover this case.

**Typical fix:**
Expand the relevant step with the missing precision: name the prerequisite, show the full
command with all required parameters, add a concrete example, or clarify the expected input
format. Where appropriate, add a "before you start" section that lists prerequisites
explicitly.

---

### `missing-or-failing-asset`

**Definition:** The skill references or depends on an external asset (a file, script, API
endpoint, template, binary, or companion resource) that is absent, broken, or inaccessible.

**Distinguishing feature:** The skill's guidance itself may be correct, but execution fails
because a required asset is not available in the expected form.

**Typical fix:**
Bundle the asset into the skill distribution, add a setup/install step that fetches or
creates it, or replace the hard dependency with a graceful fallback. If the asset is
external and outside the skill's control, document the dependency explicitly and add an
early pre-flight check step.

---

### `unclear-routing`

**Definition:** The skill's description, trigger phrases, or overlap with sibling skills
makes it unclear when to invoke this skill versus another — causing the agent to pick the
wrong skill, invoke multiple skills for the same task, or ask the user for disambiguation.

**Distinguishing feature:** The failure is navigational, not functional. The skill itself may
work correctly once invoked; the problem is knowing *when* to invoke it.

**Typical fix:**
Sharpen the trigger phrase description in SKILL.md to narrow the invocation boundary.
Add a "Use this / Don't use this" table listing sibling skills and distinguishing criteria.
If there is genuine overlap with another skill, coordinate with its author on a shared
routing note or a canonical disambiguation heuristic.

---

### `trigger-problem`

**Definition:** The skill's trigger phrases or description either (a) fail to match natural
user phrasings, causing `trigger-miss`, or (b) match too broadly, causing `false-trigger`.

**Distinguishing feature:** The mismatch is between user language and the skill's stated
invocation phrases — not between the skill's documented steps and the tool's behaviour.

**Typical fix:**
For `trigger-miss`: add the unmatched phrasing variants as synonyms in the skill's
description or trigger list. Test with at least 3 natural variants.
For `false-trigger`: narrow the description to exclude the out-of-scope case; add a "NOT
for…" clause. If the overlap is systematic, consider a disambiguation step at the start of
the skill.

---

## `pattern` → `category` mapping

Use this table to select `category` once `pattern` is assigned. Where two categories are
listed, choose the one that better matches the specific evidence.

| `pattern` | Primary `category` | Secondary `category` (if primary doesn't fit) |
|---|---|---|
| `advertised-feature-failed` | `wrong-or-stale-guidance` | `missing-or-failing-asset` |
| `repeated-command-loop` | `wrong-or-stale-guidance` | `missing-detail` |
| `workaround-chain` | `missing-case` | `wrong-or-stale-guidance` |
| `stale-guidance` | `wrong-or-stale-guidance` | — |
| `unclear-routing` | `unclear-routing` | `trigger-problem` |
| `trigger-miss` | `trigger-problem` | `unclear-routing` |
| `false-trigger` | `trigger-problem` | `unclear-routing` |

### Disambiguation notes

- **`advertised-feature-failed` → `missing-or-failing-asset`**: use this secondary mapping
  when the feature's description is correct but a dependency (file, tool, endpoint) is what
  is actually missing or broken, not the guidance itself.

- **`repeated-command-loop` → `missing-detail`**: prefer `missing-detail` when the loop
  arises because the agent was unsure of the correct parameter form (i.e. it tried variants)
  rather than because the guidance was wrong.

- **`workaround-chain` → `wrong-or-stale-guidance`**: prefer `wrong-or-stale-guidance` when
  each workaround step was a direct substitute for a skill-documented step that failed, not
  just an absent case.

- **`unclear-routing` ↔ `trigger-problem`**: if the confusion is between skills
  (inter-skill), use `unclear-routing`. If the confusion is about when to invoke this skill
  at all (user vs. skill mismatch), use `trigger-problem`.
