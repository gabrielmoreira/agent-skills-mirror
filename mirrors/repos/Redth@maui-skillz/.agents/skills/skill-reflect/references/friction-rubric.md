# Friction Rubric

Definitions for all enum fields in `FrictionFinding`, the full pattern catalog with
detection heuristics, and the false-attribution caution. Use this file during Steps 3 and 4
of the workflow.

---

## Enum definitions

### `severity`

How badly the friction affected the agent's ability to complete the task.

| Value | Definition |
|---|---|
| **High** | The skill failed to deliver its core promise; the task could not be completed (or was significantly degraded) because of the friction. Likely to affect many users. |
| **Medium** | The friction caused a visible delay, extra work, or a workaround, but the task was ultimately completed with acceptable quality. |
| **Low** | The friction was minor — a confusing step, a cosmetic error, or a slight inefficiency — with minimal impact on the task outcome. |
| **Unknown** | Severity cannot be determined from available signals (e.g. the task outcome itself is unknown). Use sparingly; prefer a best-effort Low over Unknown when there is any signal. |

---

### `confidence`

How certain you are that the attributed skill actually caused the friction.

| Value | Definition |
|---|---|
| **Confirmed** | The friction is directly and unambiguously traceable to the attributed skill (e.g. a tool call to a skill-owned tool failed with an error naming the skill's feature; the calling skill self-identified). |
| **Likely** | Strong circumstantial evidence — the friction occurred immediately after a skill invocation, the skill advertises the feature that failed, and no other plausible cause exists. |
| **Possible** | Friction was observed near a skill's active window but the causal link is uncertain — the task context, a host bug, or another skill may be responsible. |

Default to **Possible** unless you have concrete evidence to justify a higher level. See the
false-attribution caution below for mandatory downgrade rules.

---

### `outcome`

What happened to the task after the friction was encountered.

| Value | Definition |
|---|---|
| **Solved** | The friction was overcome using only what the skill provides (e.g. following a different path documented in the skill). |
| **Worked-around** | The task was completed, but only by deviating from the skill's guidance (e.g. using a manual step, a different tool, or a hard-coded value). |
| **Unresolved** | The task was not completed, or a significant degradation persisted to the end of the session. |

---

## Friction pattern catalog

Each `pattern` value names a recognizable shape of friction. Assign the most specific
matching pattern; if multiple apply, choose the one with the strongest evidence.

---

### `advertised-feature-failed`

**Definition:** The skill's documentation, trigger description, or SKILL.md advertises a
capability, but invoking that capability produced an error or incorrect output.

**Detection heuristics:**
- A tool call that a skill's SKILL.md explicitly describes exits with a failure status.
- The error name/type matches a step or command shown in the skill's guidance.
- The agent retried the same call and received the same failure.

**Typical severity:** High or Medium.

---

### `repeated-command-loop`

**Definition:** The agent (or user) repeated the same sequence of tool calls 3 or more times
without meaningful variation, suggesting the skill's guidance did not lead to a stable
resolution.

**Detection heuristics:**
- 3+ identical or near-identical tool invocations within a short session span.
- Each iteration does not materially change the inputs or approach (distinguishable from a
  legitimate polling pattern).
- No successful outcome separates the repetitions.

**Typical severity:** Medium.

---

### `workaround-chain`

**Definition:** The agent accumulated 2 or more consecutive deviations from the skill's
prescribed path in order to complete the task — indicating the skill's guidance was
insufficient or incorrect for this case.

**Detection heuristics:**
- Sequence of non-standard tool calls following a skill invocation.
- Agent explicitly declines to use a skill-recommended approach and chooses an alternative.
- User message requests a manual approach after the skill's approach failed.

**Typical severity:** Medium.

---

### `stale-guidance`

**Definition:** The skill's guidance refers to a command, flag, API, or behaviour that no
longer exists or has changed in the version the agent is using.

**Detection heuristics:**
- Error message names a flag/command as "unknown" or "deprecated".
- The skill's documented command exists but produces different output from what the skill
  describes.
- Agent falls back to documentation outside the skill after the skill's step fails.

**Typical severity:** High (if blocking) or Medium (if a workaround exists).

---

### `unclear-routing`

**Definition:** The agent was unsure which skill (or which step within a skill) to invoke
for a given task, resulting in invocation of the wrong skill, a failed trigger, or an
explicit request to the user for clarification.

**Detection heuristics:**
- Agent invokes multiple skills in sequence for the same sub-task before settling on one.
- Agent asks the user which skill to use.
- Agent's reasoning explicitly notes ambiguity in which skill applies.

**Typical severity:** Low or Medium.

---

### `trigger-miss`

**Definition:** The user's request was a natural match for a skill but the agent did not
invoke it — either because the skill's description did not match the phrasing, or the agent
was unaware the skill applied.

**Detection heuristics:**
- User request that semantically matches a skill's stated trigger phrases, but the skill was
  not invoked and no skill-produced output appeared.
- Agent completed the task manually in a way that a skill would have covered.
- User later explicitly names the skill that should have been used.

**Typical severity:** Medium (the skill is underutilised; value is lost).

---

### `false-trigger`

**Definition:** The skill was invoked for a task it was not designed to handle, leading to
incorrect or irrelevant output.

**Detection heuristics:**
- Skill invoked; output does not address the user's actual request.
- Agent immediately abandons the skill's output and starts over.
- User explicitly says the skill's output was not what they needed.

**Typical severity:** Low or Medium (usually a description/routing issue, not a
catastrophic failure).

---

## ⚠ False-attribution caution

**Friction may be the task's fault, not the skill's.**

Before asserting a finding, apply these checks:

1. **Task complexity:** Was the task outside the skill's stated scope? If yes, reduce
   confidence to `Possible` and note "task may be out of scope" in `evidence`.

2. **Host or environment cause:** Could the error be from a host-side bug, a missing
   dependency, or an environment variable — not the skill's guidance? If so, reduce
   confidence to `Possible` or drop the finding.

3. **User error:** Did the user provide an input that the skill reasonably could not handle
   and does not claim to handle? If yes, reduce confidence to `Possible`.

4. **Temporal proximity only:** Is the sole evidence that friction occurred *near* the
   skill's window? Proximity alone → `Possible`, not higher.

5. **User disputes attribution:** If the user says the finding is wrong, immediately downgrade
   or remove it. Record the user's position in a `note` field in `evidence` (paraphrased).
   Never override the user's explicit correction.

### Confidence downgrade rules (apply the first matching rule)

| Condition | Maximum confidence |
|---|---|
| Calling skill self-identified + direct tool failure on skill-owned tool | Confirmed |
| Direct tool failure with error naming skill's feature; no other plausible cause | Likely |
| Temporal proximity + skill's feature matches the failure description | Possible |
| Only evidence is the user's paraphrased description | Possible |
| User disputes attribution | Possible (or remove) |
| Environment/host cause plausible | Possible |

### Optional: local A/B confidence boost

If the session store is available (Copilot CLI), an optional autoresearch-style check can
raise confidence before asserting `Confirmed` or `Likely`: compare sessions where the same
skill was invoked successfully for the same task type against sessions where it failed. If
the failure pattern is isolated to a specific skill version or usage pattern, confidence may
be raised by one level. This check is optional and must not block the workflow.

### Summary

When in doubt, **under-claim**. A `Possible` finding with a good `proposedFix` and a
`proposedEval` is far more useful to a skill author than a confidently wrong `Confirmed`
finding. The author's eval harness will verify the fix — attribution perfection is not
required.
