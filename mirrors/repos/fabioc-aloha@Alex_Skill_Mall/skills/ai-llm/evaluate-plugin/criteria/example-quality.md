---
id: example_quality
name: Example Quality
---

# Example Quality

Evaluates whether the plugin includes concrete examples that anchor the LLM's behavior
and ensure consistent results across invocations.

## What to look for

- **Concrete examples** — Are there realistic input/output examples?
- **Workflow walkthroughs** — Does it show a full interaction from start to finish?
- **Sample output** — Does the LLM know what its response should look like?
- **Edge case examples** — Are there examples of unusual or boundary inputs?
- **Before/after** — For transformation tasks, are before and after states shown?

## Scoring rubric

| Score | Criteria |
|-------|----------|
| **5** | ≥2 realistic walkthroughs showing input → actions → output. Includes edge case examples. Shows expected output format verbatim. |
| **4** | ≥1 complete walkthrough. Output format demonstrated with sample. Common scenarios covered. |
| **3** | Examples exist but are fragments — no complete input-to-output flow. LLM can infer behavior but output format will vary between runs. |
| **2** | Only trivial examples ("say hello") or examples that don't match the actual task complexity. |
| **1** | No examples. LLM has no anchor for expected behavior or output format. |

## What a 5 looks like

- Full conversation flow showing user request → agent actions → final output
- Example output formatted exactly as expected
- "Given this input: ... the agent should produce: ..."
- Examples covering both simple and complex scenarios

> **Note:** Negative examples ("what NOT to output") are NOT required. They can
> be useful in some contexts but can also prime models toward the wrong behavior.
> Do not penalize plugins that omit them.

> **Reference and documentation plugins:** For plugins whose primary function is
> information lookup, troubleshooting, or documentation generation (rather than
> interactive conversation), "walkthroughs" may take the form of scenario
> descriptions with expected output structure, per-skill usage tables, or
> annotated response templates. These count toward the walkthrough requirement
> as long as they demonstrate realistic input → expected output for the
> plugin's actual use case.

## Scoring examples

### Score 5 — validate-md-links

```markdown
## Examples

# Current directory (default)
powershell -File "scripts/validate-md-links.ps1"

# Specific directories
powershell -File "scripts/validate-md-links.ps1" -Include "docs", "README.md"

# Plugin isolation check
powershell -File "scripts/validate-md-links.ps1" -Include "plugins/my-plugin" -Root "plugins/my-plugin"

## Output

Shows line numbers for each broken reference:
  README.md:42  [broken link](missing-file.md)  — file not found
  docs/api.md:15  [section](#setup)  — anchor not found
```

Why it scores 5: Multiple realistic usage examples covering different scenarios,
expected output format shown verbatim with exact formatting, includes both simple
and complex invocations.

### Score 1 — hello-skills

The plugin contains no examples whatsoever. The LLM has no anchor for what
the greeting should look like, how ASCII art should be formatted, or what
"friendly and encouraging" means in practice.
