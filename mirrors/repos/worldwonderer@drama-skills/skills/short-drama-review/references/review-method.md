# Evidence-Based Review Method

## Contents

1. Independence and target freeze
2. Mechanical-before-taste pass
3. Evidence anatomy
4. Cross-layer synthesis
5. Revision and re-review
6. Anti-template review

## Rule classification

- `structural_invariant`: objectively checkable artifact integrity; validators
  may block it.
- `reviewed_invariant`: semantic integrity that requires cited evidence and an
  independent reviewer.
- `craft_default`: a recommended method that may change for a stated craft
  reason.
- `taste_option`: a creator choice that stays non-blocking unless it conflicts
  with an accepted constraint.

## Governing know-how

- `REV-01` — Run mechanical integrity checks before spending attention on taste.
- `REV-02` — Every finding names artifact/hash, bounded evidence, impact,
  required outcome, owner, severity, and status.
- `REV-03` — A semantic-invention finding pairs the authoritative source fact
  with the conflicting downstream fact; suspicion alone is not evidence.
- `REV-04` — Final approval requires a fresh reviewer context that did not author
  the targets; self-check/unattested review stays provisional, and reviewers report
  and route findings but do not edit owner source.
- `REV-05` — Diagnose generic/repeated mechanisms at exact locations and explain
  audience or production impact instead of applying an “AI-ish” label.
- `REV-06` — Alternative preferences remain non-blocking notes unless the
  current choice violates an accepted creator constraint.
- `REV-07` — An end-to-end drafting request does not sign later artifacts;
  preview chains remain provisional, creator-pending, and delivery-blocked.

## Independence and target freeze

The same context that authored an artifact may run a self-check, but it cannot
issue final approval. A final reviewer starts from accepted artifacts, creator
constraints, and hashes—not the author's explanation of why the output is good.

When the host supports agents or isolated sessions, start a fresh reviewer and
pass only the frozen artifact paths/hashes, accepted constraints, selected
rubrics, and output schema. Do not pass the owner's intended fix, self-score, or
an answer key. Record `requested_review_mode: independent_agent` and the actual
`effective_review_mode`. A fresh reviewer records its runtime context ID and
attests that it did not author any reviewed target. When isolation is unavailable,
record `self_check` or `unattested`, keep `independent:false`, and issue only
`PROVISIONAL`; changing a role label inside the same context is not independence.
The deterministic project tool validates the attestation shape and bound bytes,
not the truth of host runtime identity; it records that limited verification
scope explicitly. Host orchestration remains responsible for actual isolation.

Freeze the review set. If a file changes during review, mark affected findings
stale and restart only the dependent scopes.

## Mechanical-before-taste pass

Scripts handle facts they can prove. They do not judge whether a scene feels
alive or an action is generally filmable.

Mechanical examples:

- missing/duplicate IDs or unresolved references;
- unknown asset variant;
- missing coverage disposition;
- explicit segments not totaling exactly the declared duration, in either direction;
- mutually exclusive structured camera flags;
- readable text with a global no-text policy;
- prompt text/hash not matching its accepted spec and recipe;
- owner writing outside its authority;
- delivery including a private path or unapproved artifact.

Semantic examples requiring review:

- downstream action changes story meaning;
- a scene has no meaningful opposition/turn;
- a keyframe prose description implies several moments;
- an untimed action load crowds out performance;
- escalation merely repeats humiliation louder;
- a prompt is specific but preserves the wrong identity.

## Evidence anatomy

A valid finding contains:

1. **Diagnostic identity:** stable catalog code, know-how rule ID, canonical
   classification, and enforcer (`validator | reviewer | creator`).
2. **Target:** artifact path, ID, hash, and field/block/shot.
3. **Evidence:** a bounded quotation or two conflicting structured facts.
4. **Impact:** what the audience, creator, continuity, or production loses.
5. **Required change:** outcome/constraint, not ghostwritten replacement prose.
6. **Owner:** the only skill allowed to make the source change.
7. **Severity/status:** and whether it blocks the requested checkpoint.

“The dialogue is weak” is invalid. “SC003 lines 12–16 repeat facts both speakers
already used as leverage, so neither agenda nor power changes before the exit;
write owner must give one speaker a costly move or cut the scene” is actionable.

The structured finding uses `target_ref` for the artifact to revise and
`evidence_refs[]` for the source/consumer sides of the conflict; do not hide a
second citation in free prose. A verdict binds exact `reviewed_artifacts`, its
`findings_ref`, reviewer-independence proof, and open-blocker count. The referenced
JSONL is authoritative for blocking-finding reconciliation: every open fatal/error
ID is listed, and every listed ID exists and is still open. Delivery may trust
approval only while those exact target and evidence hashes remain current. The
`reviewer` value is a structured object with owner, kind, explicit independence,
and the exact excluded source owner; a bare owner string is not independence
evidence and cannot issue or preserve approval.

## Cross-layer synthesis

Trace important story moves end to end. Sample questions:

- Is the promised evidence actually shown or only mentioned in a prompt?
- Does the shot preserve who knows what and who controls the prop?
- Does the keyframe depict the shot start rather than an attractive unrelated
  portrait?
- Does motion realize the accepted boundary, or invent a grab, transfer, injury,
  relationship change, or location transition?
- Does the end report reconcile with the next shot start?

Resolve upstream first. Do not polish video wording when the shot or asset binding
is wrong.

## Revision and re-review

Synthesize duplicate findings and route by owner. A revision request includes
target outcome, preserved facts, affected dependents, acceptance need, and review
scope to rerun.

On re-review:

1. verify the semantic diff addresses the finding;
2. ensure preserved facts remain intact;
3. reject stale prior approval;
4. rerun exact structural and semantic dependents;
5. close, supersede, or retain every finding explicitly.

## Anti-template review

Do not use a banned-word list as a quality verdict. Look for mechanisms:

- every episode uses the same hook/turn/cliffhanger with renamed nouns;
- all characters share sentence length, vocabulary, and emotional escalation;
- action paragraphs stack abstract intensity without playable behavior;
- prompts lead with generic quality adjectives and bury identifying facts;
- every line gets an unnecessary reaction close-up;
- camera movement is used as decoration rather than attention or power;
- repeated boilerplate contradicts the specific scene.

Cite locations and impact. Preserve deliberate genre rhythm and creator choices.
