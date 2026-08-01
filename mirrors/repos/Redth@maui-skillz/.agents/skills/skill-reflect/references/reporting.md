# Reporting

The local artifact template, field-filling guide, and file naming convention.
Use this file during Step 6 of the workflow.

Destination routing (which repo to offer for GitHub issue filing) is determined per
`references/provenance-routing.md`. The `proposedEval` block in each finding is authored
per `references/eval-format.md`.

---

## File naming

```
.skill-feedback/<YYYY-MM-DD>-<skill-slug>.md
```

- `<YYYY-MM-DD>` — the date the artifact is generated (UTC, ISO 8601 date only).
- `<skill-slug>` — the attributed skill's name, lowercased, with all non-alphanumeric
  characters collapsed to a single `-`. Leading and trailing `-` are trimmed.

**Examples:**

| Skill name | Slug | Example path |
|---|---|---|
| `my-ci-helper` | `my-ci-helper` | `.skill-feedback/2025-07-07-my-ci-helper.md` |
| `GitHub Actions` | `github-actions` | `.skill-feedback/2025-07-07-github-actions.md` |
| `@scope/my.tool` | `scope-my-tool` | `.skill-feedback/2025-07-07-scope-my-tool.md` |

The base directory `.skill-feedback/` is overridden by `artifactDir` in
`skill-reflect.config.json`. Create the directory if it does not exist.

One artifact file per skill per session run. If a session produced findings for multiple
skills, write separate files — one per skill.

---

## Artifact template (exact per CONTRACT §5)

The template below must be followed exactly. Do not add extra top-level sections. Content
notes in `<angle brackets>` are instructions, not literal text.

````markdown
---
generated_by: skill-reflect
schema: 1
date: <YYYY-MM-DD>
skill: <skill-name>
source_repo: <owner/repo|unknown>
sessions_reviewed: <n>
consent: review-only            # becomes "sent:<destination>" after a send
---

# Field feedback for `<skill-name>`

## Summary
<1–3 sentence paraphrased overview. No PII.>

## Findings
### <#> <short title>  ·  <severity> / <confidence> / <outcome>
- **Category:** <category>
- **What happened:** <paraphrased summary>
- **Signal:** <paraphrased evidence>
- **Proposed fix:** <concrete change>
- **Proposed eval:**
  ```json
  { ...portable form... }
  ```

## Privacy
This report was scrubbed of names, paths, secrets, and verbatim excerpts. Values are
paraphrased. Reviewed by the user before creation.

## Routing
Suggested destination: <local | owner/repo issue>. Not sent unless the user approves.
````

---

## Field-filling guide

### Frontmatter

| Field | How to fill |
|---|---|
| `generated_by` | Always literal `skill-reflect`. |
| `schema` | Always `1` (CONTRACT schema version). |
| `date` | UTC date the artifact is written, `YYYY-MM-DD`. |
| `skill` | The attributed skill name, exactly as identified in the session (not the slug). |
| `source_repo` | Resolved via `references/provenance-routing.md`. Use `unknown` if unresolvable. |
| `sessions_reviewed` | Integer count of sessions examined. Use `1` for single-session; `0` if only the current conversation was available (Tier C). |
| `consent` | Always start as `review-only`. Change to `sent:<destination>` (e.g. `sent:owner/repo`) only after Gate 2 consent is given and the issue is filed. |

---

### Summary section

Write 1–3 sentences that describe:
1. What distributed skill(s) were reviewed.
2. How many findings were identified and their aggregate severity.
3. A one-phrase description of the dominant friction pattern observed.

**Do not** name the user, name the project, include any paths, or quote any output verbatim.

**Example (synthetic):**
> Reviewed `my-ci-helper` across one session. Found two Medium findings: one instance of
> stale guidance (a documented flag no longer accepted by the target tool) and one
> missing-case gap around multi-environment pipelines. No high-severity blockers observed.

---

### Findings section

One `###` subsection per `FrictionFinding`. Number them sequentially starting at 1.

**Heading format:**
```
### <#> <short title>  ·  <severity> / <confidence> / <outcome>
```

The short title is a ≤8-word noun phrase describing the finding (no PII, no values).

**Fields:**

| Field | Source in `FrictionFinding` | Notes |
|---|---|---|
| **Category** | `category` | One of the 6 values from `references/skill-improvement-taxonomy.md`. |
| **What happened** | `summary` | 1–2 sentences, paraphrased. Describe what the agent was trying to do and where it stumbled. No tool output values. |
| **Signal** | `evidence` | The observable signal that led to this finding (e.g. "the advertised `--foo` flag produced an unknown-flag error; agent retried 3 times then used a manual alternative"). Refer to flag/tool names, not their values. |
| **Proposed fix** | `proposedFix` | A specific, actionable change the skill author can make. E.g. "Update the `setup` step to remove the `--foo` flag, which is no longer valid in v3+." |
| **Proposed eval** | `proposedEval` (portable form) | A fenced `json` block containing the portable eval. See `references/eval-format.md` for the format. |

**Proposed eval block (portable form):**
```json
{
  "id": "<finding-id>",
  "prompt": "<a realistic task that exercises the proposed fix>",
  "must_contain": ["<expected behaviour keyword or phrase>"],
  "must_not_contain": ["<behaviour that should no longer occur>"]
}
```

The `id` field should match `FrictionFinding.id` (a stable hash of `{skill, pattern,
normalized-summary}`; for v1, a short descriptive slug is acceptable).

---

### Privacy section

Use this section verbatim (it is fixed text):

```markdown
## Privacy
This report was scrubbed of names, paths, secrets, and verbatim excerpts. Values are
paraphrased. Reviewed by the user before creation.
```

Do not add user names, project names, or any identifying information here. If the scrubber
(`scripts/scrub.py`) was run, you may append the redaction summary as a parenthetical:
`(Scrubber: <N> categories redacted.)` — using only the count, never the redacted values.

---

### Routing section

Fill based on the destination resolved by `references/provenance-routing.md`:

- If source repo is resolved: `Suggested destination: <owner/repo> issue. Not sent unless the user approves.`
- If source repo is unknown or local-only mode: `Suggested destination: local only. No remote filing suggested.`
- After Gate 2 consent and filing: update `consent` in frontmatter to `sent:<destination>` and optionally append the issue URL (which is not PII).

---

## Redaction preview protocol

Before writing the file:

1. Assemble the full artifact text in memory.
2. Run `scripts/scrub.py` (if available) and collect the redaction summary.
3. Show the user:
   - The complete artifact text as it will be written.
   - The scrub summary (categories and counts, not the redacted values).
4. Ask the user to confirm before writing. If they request changes, apply them and re-show.
5. Only after explicit confirmation: write the file.

**Never skip the redaction preview.** `privacy.redactionPreview` is hard-`true` regardless
of config.

---

## Multi-skill sessions

If findings span multiple skills in one session:
- Write a separate artifact file per skill.
- Each file covers only the findings attributed to that skill.
- The `Summary` section in each file refers only to that skill.
- The `sessions_reviewed` count is the same in all files (same session).

---

## After Gate 2 (GitHub issue filing)

When the user approves filing a GitHub issue:

1. Use the template in `skill-reflect/templates/github-issue.md`.
2. File via `gh issue create` (never auto-file; always show the command to the user first).
3. Update `consent` in the local artifact frontmatter to `sent:<owner/repo>`.
4. Optionally append the issue URL to the `## Routing` section.
5. The issue body must pass the same privacy rules as the local artifact.
