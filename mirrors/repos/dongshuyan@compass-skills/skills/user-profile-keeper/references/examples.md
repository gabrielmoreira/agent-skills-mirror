# Examples

## Initialize The Default User

```bash
# macOS / Linux
python3 <user-profile-keeper-dir>/scripts/profile_store.py init --user default

# Windows
py -3 <user-profile-keeper-dir>\scripts\profile_store.py init --user default
```

## Read Low-Sensitivity Summary For task-clarifier

```bash
python3 <user-profile-keeper-dir>/scripts/profile_store.py read --user default --view clarification_summary
```

## Read The Internal Profile Overview

```bash
python3 <user-profile-keeper-dir>/scripts/profile_store.py read --user default --view profile_overview
```

`profile_overview` can show low/private active assertions. It omits sensitive, intimate, secret, and raw evidence text. Other skills should not read this view.

## Generate Candidate Updates From The Current Session

For first-run profile setup, apply the Context Adequacy Gate. If no active profile exists, recommend the onboarding questionnaire. If the user declines, continue with the current task and create proposals for durable candidates.

The agent extracts candidate JSON from the current session, then runs:

```bash
python3 <user-profile-keeper-dir>/scripts/profile_store.py update-from-session \
  --user default \
  --session-summary "The user explicitly requires confirmation before high-impact actions such as deletion, overwrite, publishing, or installation." \
  --candidate-json '[{"category":"risk_boundary","claim":"confirm_high_impact_actions","value":{"summary":"Confirm before high-impact actions such as deletion, overwrite, publishing, or installation."},"scope":"global","source_type":"self_report","confidence":0.95,"sensitivity":"low","evidence":{"summary":"User explicitly requested confirmation before high-impact actions.","context":"current session","raw_excerpt":"Confirm before deleting, overwriting, publishing, or installing."}}]' \
  --auto-apply-safe
```

## Self-Reported Background Becomes A Proposal

Age range, education, field, role, experience stage, and long-term goals default to `private`, even when the user states them clearly:

```bash
python3 <user-profile-keeper-dir>/scripts/profile_store.py update-from-session \
  --user default \
  --session-summary "The user filled background information in the onboarding questionnaire." \
  --candidate-json '[{"category":"education_background","claim":"major_or_specialty","value":{"summary":"The user self-reported a field or research direction."},"scope":"global","source_type":"self_report","confidence":0.9,"sensitivity":"private","evidence":{"summary":"Onboarding questionnaire background answer.","context":"local onboarding questionnaire"}}]' \
  --propose
```

## Inferred Profile Data Becomes A Pending Proposal

Inference needs confidence, basis, counter-evidence, and a review question:

```bash
python3 <user-profile-keeper-dir>/scripts/profile_store.py update-from-session \
  --user default \
  --session-summary "The user repeatedly asked for a plan before complex changes, then confirmed before execution." \
  --candidate-json '[{"category":"clarification_style","claim":"prefers_plan_before_structural_changes","value":{"summary":"The user may prefer seeing a complete plan before structural changes.","basis":["The user asked for cause, scope, and verification before changes.","The user asked to execute after confirming the plan."],"reasoning":"This may be a durable collaboration preference, with current-task-only context as an alternative explanation.","counter_evidence":["The user sometimes asks for direct execution on low-risk tasks."],"usefulness":"Helps decide when to present a plan before high-impact changes.","review_question":"Should this be saved as a long-term collaboration preference?"},"scope":"global","source_type":"inferred","confidence":0.55,"sensitivity":"private","evidence":{"summary":"Repeated pattern in complex-change discussions.","context":"current session"}}]' \
  --propose
```

## Review And Apply Proposals

```bash
python3 <user-profile-keeper-dir>/scripts/profile_store.py proposal-list --user default
python3 <user-profile-keeper-dir>/scripts/profile_store.py proposal-apply --user default --proposal-id <id>
```

## Correct A Profile Assertion

```bash
python3 <user-profile-keeper-dir>/scripts/profile_store.py correct \
  --user default \
  --assertion-id <id> \
  --note "This assertion is inaccurate; I only needed a detailed plan for that task."
```

## Start The Local Questionnaire

```bash
python3 <user-profile-keeper-dir>/scripts/onboarding_webui.py --user default
```

Multiple-choice questions must include a mutually exclusive custom-answer option. Show the text box only after that option is selected. Submit only the text box content as the answer. Questionnaire output creates proposals. Suspected credentials are redacted.
