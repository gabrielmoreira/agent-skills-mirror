# Update Policy

Profile updates must preserve evidence, confidence, sensitivity, and reversibility. A single session does not create a permanent character judgment.

## Evidence Types

- `durable_profile_evidence`: explicit long-term or default collaboration preferences, risk boundaries, privacy boundaries, capability boundaries, recurring omissions, or anti-bubble rules stated by the user.
- `operational_instruction`: current task instructions, repository rules, AGENTS rules, skill operating steps, privacy rules, and tool-use constraints. These guide the current task and do not prove a durable profile by themselves.
- `agent_observation`: the agent's observation of the current session. Use it only as a proposal unless it is repeated, direct, low-ambiguity, and limited to collaboration process.

## Auto Apply

The script may write a candidate as `active` only when all conditions hold:

- The user explicitly self-reported a long-term/default collaboration preference, or the session contains repeated, direct, low-ambiguity observation.
- `sensitivity` is `low`.
- `confidence >= 0.75`.
- The candidate does not conflict with an existing active assertion.
- The assertion affects communication, need alignment, workflow, evidence preference, privacy boundary, or risk confirmation.
- The evidence is not AGENTS rules, system/developer instructions, skill operating steps, repository constraints, or current task constraints.

User-provided background information, including age range, education, field, role, experience stage, and long-term goals, starts as a pending proposal with `sensitivity=private`.

`--auto-apply-safe` asks the script to consider active write. It is a safety-gated path. Candidates that fail the checks become proposals when proposal mode is enabled.

## First-Run Gate

Use one first-run gate:

- If an active profile exists, handle the request as an incremental update.
- If no active profile exists, recommend the onboarding questionnaire.
- If the user asks for the questionnaire or WebUI, run it.
- If the user declines the questionnaire, continue with the current task and create proposals for durable candidates.

Do not skip the questionnaire by counting how many questionnaire modules the current session appears to cover. Do not initialize active profile data from operational instructions.

Current task constraints can govern the current task. If they may have durable value, create a pending proposal and let the user confirm.

## Session Inference

Inference candidates must satisfy:

- `source_type=inferred`.
- Default `sensitivity=private`; identity, health, finance, legal, political, religious, family, intimate, or location claims are at least `sensitive` and should usually be avoided.
- Default status is pending proposal.
- `value` contains `summary`, `basis`, `reasoning`, `counter_evidence`, `usefulness`, and `review_question`.
- Evidence comes from concrete current-session behavior or explicit text, not model stereotypes, path guessing, timezone guessing, or language guessing.

Confidence caps:

- Single weak signal: `confidence <= 0.4`.
- Multiple consistent session signals with alternative explanations: `confidence <= 0.6`.
- User-confirmed inference can be rewritten as `self_report` or `correction` with confidence above `0.75`.

Never silently write these claims as active:

- real location, ethnicity, political/religious position, health, finance, legal risk, or intimate relationship;
- strong labels about ability, personality, values, psychological state, or morality;
- high-impact judgments that could change how the system treats or evaluates the user.

## Pending Proposal

Use pending proposal for:

- `source_type=inferred`;
- `sensitivity` of `private`, `sensitive`, `intimate`, or `secret`;
- self-reported background information such as age range, education, field, role, experience stage, and long-term goals;
- conflict with an existing active assertion;
- claims that could affect how the user is treated or judged;
- uncertain user phrasing;
- sources that are mainly current task constraints, skill operating rules, or one-off context, when the agent sees possible durable value.

## Conflict Handling

If a new candidate differs from an active assertion with the same `category + claim + scope`:

1. Keep the existing active assertion.
2. Create a pending proposal.
3. Mark the conflicting assertion.
4. Supersede only after user confirmation.

## Correction

User correction has highest priority:

- Set the old assertion to `retracted` or `superseded`.
- Save the new assertion with `source_type=correction`.
- Record the correction in the audit log.

## Anti-Staleness

Preferences, boundaries, work style, and risk tolerance can change. When reading the profile, use this order:

1. Current session explicit statements.
2. Recent user corrections.
3. High-confidence active assertions.
4. Older or lower-confidence observations.

Current explicit requirements override stored profile data.
