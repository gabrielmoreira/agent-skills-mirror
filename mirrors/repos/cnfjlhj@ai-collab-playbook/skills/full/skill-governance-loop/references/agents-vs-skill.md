# AGENTS.md vs Skill

Use this note before moving content between `AGENTS.md` and a skill.

## Put it in AGENTS.md when

- the rule is stable across many tasks
- the rule should be always-on
- the rule is short enough to justify permanent context cost
- violating the rule causes repeated damage across domains

Examples:

- explore before asking
- verify before claiming success
- dangerous operations require stronger confirmation
- mixed user input must be triaged before acting

## Put it in a skill when

- the workflow is task-specific
- the detail is too large for always-on context
- the process needs scripts, templates, or references
- multiple valid variants exist and selection depends on context

Examples:

- paper review workflow
- video summary formatting
- skill quality review workflow
- domain-specific document generation

## Strong smell: wrong layer

If any of these are true, the content is probably in the wrong place:

- `AGENTS.md` keeps growing with niche procedures
- a skill contains a rule that should govern almost every task
- multiple skills repeat the same core safety or reasoning instruction
- a skill exists only to say something that could fit in one short AGENTS line

## Default rule

Use this split:

- `AGENTS.md` = stable iron laws + compact routing hints
- `skill` = heavy workflow + domain detail + optional resources

Do not use a skill to hide missing global discipline.
Do not use `AGENTS.md` as a dumping ground for every specialized pattern.
