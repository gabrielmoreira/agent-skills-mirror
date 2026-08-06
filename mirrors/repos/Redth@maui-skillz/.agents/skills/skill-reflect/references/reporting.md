# Reporting

Formats for analysis-mode chat output, local artifacts, previews, and remote reports.
Use this file during Step 6 of the workflow.

Destination routing (which repo to offer for GitHub issue filing) is determined per
`references/provenance-routing.md`. The `proposedEval` block in each finding is authored
per `references/eval-format.md`.

---

## Analysis-mode response

Analysis mode returns findings directly in chat and creates no file. Use this compact shape:

```markdown
**Scope:** `<skill>` · <session scope> · <install scope> · provenance <source/confidence>

<1–3 sentence summary>

### <#> <short title> · <severity> / <confidence> / <outcome>
- **Pattern / category:** <pattern> / <category>
- **Evidence:** <paraphrased signal>
- **Proposed fix:** <concrete change>
- **Proposed eval:** <trigger item or task/portable block>

**Limitations:** <source/attribution limitations, if any>
```

Apply the selected detail policy and deterministic scrub before returning it. Do not add
artifact frontmatter, preview the answer a second time, ask a routing question, or offer a
remote send unless the user requested one.

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
schema: 2
date: <YYYY-MM-DD>
skill: <skill-name>
source_repo: <owner/repo|unknown>
install_scope: <project|user|vendored|unknown>
provenance_source: <frontmatter|manifest|marketplace|vendored|registry|unknown>
provenance_confidence: <Confirmed|Likely|Possible|None>
sessions_reviewed: <n>
review_mode: artifact
detail_level: <strict|technical-local>
remote_eligible: <true|false>
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
<strict or technical-local privacy statement from the field guide>

## Routing
Suggested destination: <local | owner/repo issue>. Not sent unless the user approves.
````

---

## Field-filling guide

### Frontmatter

| Field | How to fill |
|---|---|
| `generated_by` | Always literal `skill-reflect`. |
| `schema` | Always `2` for new artifacts. Readers must continue accepting schema-1 artifacts, where the v2-only fields are absent. |
| `date` | UTC date the artifact is written, `YYYY-MM-DD`. |
| `skill` | The attributed skill name, exactly as identified in the session (not the slug). |
| `source_repo` | Resolved via `references/provenance-routing.md`. Use `unknown` if unresolvable. |
| `install_scope` | `project`, `user`, `vendored`, or `unknown`, from metadata preflight. |
| `provenance_source` | Resolver source label, or `unknown`. Never an installation path. |
| `provenance_confidence` | `Confirmed`, `Likely`, `Possible`, or `None`. |
| `sessions_reviewed` | Integer count of sessions examined. Use `1` for single-session; `0` if only the current conversation was available (Tier C). |
| `review_mode` | Always `artifact` for a written report. |
| `detail_level` | `strict` or explicitly authorized `technical-local`. |
| `remote_eligible` | `false` for technical-local detail or provenance below `Likely`; otherwise `true`. |
| `consent` | Always start as `review-only`. Change to `sent:<destination>` only after remote-send authorization and successful filing. |

---

### Summary section

Write 1–3 sentences that describe:
1. What distributed or explicitly requested local/user-owned skill(s) were reviewed.
2. How many findings were identified and their aggregate severity.
3. A one-phrase description of the dominant friction pattern observed.

In strict mode, do not name the user, project, product/app or its type, include paths, or
quote output verbatim. In technical-local mode, the bounded detail allowed by
`privacy-scrub.md` §2b may be retained; unconditional privacy rules still apply.

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
| **What happened** | `summary` | 1–2 paraphrased sentences. Strict mode uses an invented analogous scenario. Technical-local mode may retain only the bounded local detail allowed by `privacy-scrub.md` §2b. |
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

For `detail_level: strict`, use:

```markdown
## Privacy
This report was scrubbed of names, paths, secrets, product/domain specifics, and
verbatim excerpts. Values are paraphrased and any reproduction details are recast as
an invented, analogous scenario. Reviewed by the user before creation.
```

Do not add user names, project names, or any identifying information here. If the scrubber
(`scripts/scrub.py`) was run, you may append the redaction summary as a parenthetical:
`(Scrubber: <N> categories redacted.)` — using only the count, never the redacted values.

For `detail_level: technical-local`, use:

```markdown
## Privacy
This local-only report was scrubbed of names, absolute paths, secrets, private URLs,
runtime values, and verbatim transcript excerpts. It retains only the repository-relative
technical detail explicitly authorized for this review and is not eligible for remote send.
```

---

### Routing section

Fill based on the destination resolved by `references/provenance-routing.md`:

- If source repo is resolved: `Suggested destination: <owner/repo> issue. Not sent unless the user approves.`
- If source repo is unknown or local-only mode: `Suggested destination: local only. No remote filing suggested.`
- After remote-send authorization and filing: update `consent` in frontmatter to `sent:<destination>` and optionally append the issue URL (which is not PII).

---

## Summary-first preview protocol

Before writing a local artifact:

1. Assemble the full artifact text in memory.
2. Run `scripts/scrub.py - --report --fail-on-secret` and collect the redaction summary.
   If it fails, emit/write nothing; redraft.
3. Show the user:
   - The intended path, scope, detail level, and remote eligibility.
   - A compact summary of each finding.
   - The scrub summary (categories and counts, not the redacted values).
   - An option to show the full scrubbed artifact.
4. If the original request explicitly asked to save/capture the report, the announced write
   is already authorized. Otherwise ask once before writing.
5. Write exactly the scrubbed artifact represented by the preview.

Before a remote send, summary-first is insufficient: regenerate strict content if necessary,
show the exact scrubbed issue body and destination, then obtain fresh remote-send
authorization. `privacy.redactionPreview` remains hard-`true`.

---

## Multi-skill sessions

If findings span multiple skills in one session:
- Write a separate artifact file per skill.
- Each file covers only the findings attributed to that skill.
- The `Summary` section in each file refers only to that skill.
- The `sessions_reviewed` count is the same in all files (same session).

---

## Remote issue filing

When the user explicitly requests remote filing:

1. Require provenance confidence `Likely` or better and `remote_eligible: true`.
2. If the source artifact is technical-local, discard its rendering and regenerate strict
   content under `privacy-scrub.md` §2a.
3. Render `skill-reflect/templates/github-issue.md` and run the scrubber.
4. Show the exact scrubbed body, title, destination, and redaction counts.
5. Obtain fresh destination-specific remote-send authorization.
6. File via `gh issue create`; never auto-file.
7. Update `consent` to `sent:<owner/repo>` and optionally append the issue URL.
