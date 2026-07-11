# Onboarding Questionnaire

The onboarding questionnaire accelerates user understanding. The user may skip it or leave any question unanswered.

## WebUI Rules

- Listen only on `127.0.0.1`.
- Use a random high port, with a quiet fallback port if needed.
- Load no CDN assets, tracking images, external fonts, or analytics.
- Form submission creates proposals. It does not write sensitive content directly to active profile data.
- User-provided age range, education, field, role, experience stage, and long-term goals default to `private` proposals.
- Let the user choose a setting that requires confirmation before saving sensitive content.
- Every question must allow no answer.
- Every multiple-choice question must include a mutually exclusive custom-answer option. Options are hints and must not limit the user's answer.
- Show and enable the text box only after the user chooses the custom-answer option.
- When the user chooses the custom-answer option, the text box content is the answer. Do not write UI labels such as "custom answer" into proposals.
- When the user chooses a preset option, ignore hidden text box content even if it is submitted.
- Before submission, check locally for obvious credential patterns. Suspected secrets must be redacted; store only a redaction event and placeholder.

## Answer Model

Questionnaire answers have three states:

- `blank`: the user left it empty or chose no answer; create no candidate.
- `selected`: the user chose a preset option; the option text is the answer.
- `custom`: the user chose the custom-answer option and filled the text box; the text box content is the answer.

For multiple-choice questions, store only the final answer text in the summary. If custom content is sensitive or high-impact, route it through `privacy-boundary.md` and `update-policy.md` to pending or redaction.

If the custom-answer option is selected and the text box is empty, treat it as `blank`.

## First-Run Use

The questionnaire is the main first-run path when no active profile exists. Recommend it before profile initialization.

If the user asks for the questionnaire or WebUI, run it. If the user declines, continue with the current task and create proposals for any durable candidates. Current-session AGENTS rules, skill operating rules, privacy instructions, and task constraints do not initialize active profile data.

## Question Modules

1. Basic collaboration: name preference, primary language, timezone if the user wants to share it, domain, common task types.
2. Background: age range, education, field/major/research direction, role/current identity, experience stage, long-term goals, or long-term help direction.
3. Communication preference: concise/detailed, conclusion-first/evidence-first, citation needs, and how the agent should point out issues, challenge assumptions, or warn about risk.
4. Requirement alignment: quick clarification, evidence-first, one-question-at-a-time, or best guess with labeled assumptions.
5. Capability boundary: areas the user can discuss directly and areas where more explanation or examples help.
6. Common omissions: acceptance criteria, non-goals, evidence boundary, audience, output format, or risk boundary.
7. Risk confirmation: delete, overwrite, install, publish, remote write, credential use, and public material confirmation preferences.
8. Privacy boundary: content that must never be stored and content that requires confirmation before storage.
9. Sensitive-expression preference: optional topics the user may phrase indirectly; never require details.
10. Anti-bubble: scenarios where the agent should ask a profile-challenging question.

Use wording such as "point out issues, challenge assumptions, or warn about risk." Make clear that this targets tasks, plans, evidence, and assumptions.

Questionnaire answers become proposals. Apply them only after user confirmation.
