---
name: skill-creator
description: Create, modify, evaluate, package, and upload skills. Use when users want to create a skill from scratch, edit or optimize an existing skill, run evals to test a skill, benchmark skill performance, optimize a skill's description for better triggering accuracy, package a skill into a zip, or upload a skill to their skill library. Also use when user asks to "capture this workflow as a skill", "make a skill for X", "turn this into a reusable skill", "package this skill", or "upload to my skill library".
---

# Skill Creator

Helps users design, build, evaluate, and persist Skills. Your core job is not "doing the task" but "teaching AI how to do a class of tasks".

High-level workflow: Capture Intent → Interview → Plan (write `<skill>_plan.md` + show in chat, wait for confirm) → **Check Conflicts** → Write SKILL.md → Test → Iterate → Optimize → Package.
Assess where the user is and jump in from there.

---

## Language Awareness

- Always use the language the user is currently speaking in, unless the user explicitly requests a different language
- Generate skill content (SKILL.md body, comments, examples) in the same language as the current conversation
- Default to single-language skill content. If the user explicitly requests multiple languages, write ordinary multilingual sections and do not use HTML comment annotations in SKILL.md.
- Keep `description` in English (triggering relies on English semantics)

---

## Tool Call Format in SKILL.md

Tools in SKILL.md fall into two categories with different formats:

1. **Tools listed in `references/system-tools.md`**: These run inside Python code snippets (via `run_sdk_snippet`) and must be shown as Python code:

```python
from sdk.tool import tool

result = tool.call('tool_name', {
    "param1": "value1",
    "param2": "value2"
})

if result.ok and result.data:
    output = result.data['field_name']
```

2. **Basic tools** (e.g. `read_files`, `read_skills`, `shell_exec`, `run_python_snippet`): Call them directly, no need to wrap in Python code:

```
read_files(files=[{"file_path": "path/to/file.md"}])
```

Before specifying tools in the skill, read the reference file `references/system-tools.md` for the full list of available tools and usage examples.

Common tool categories — quick reference (see `references/system-tools.md` for details and examples):
- Web search & fetch: `web_search`, `read_webpages_as_markdown`; external file downloads use the `download` skill with `run_sdk_snippet`
- Vision: `visual_understanding`, `visual_understanding_webpage`, `video_understanding`
- Code execution: `shell_exec`, `run_python_snippet`
- Image generation & search: `generate_images`, `image_search`

---

## Full Skill Creation Workflow

### Phase 1: Capture Intent

Understand what the user wants. If the conversation already contains a workflow (e.g., "turn this into a skill"), extract from history: tools used, step sequence, corrections made, input/output formats.

Then confirm:
1. What should this skill enable AI to do?
2. When should it trigger? (what user phrases/contexts)
3. **What is the final output form?** (see "Output Form Decision" below — must be decided here)
4. Should we set up test cases?

### Output Form Decision (Required in Capture Intent Phase)

This is critical for high-quality skills. Determine the output form and write it explicitly into the generated SKILL.md.

| Scenario | Recommended Output Form |
|---------|------------|
| Multi-section content: itineraries, reports, analysis | Write file (Markdown / HTML) |
| Charts, visualizations | Write HTML file (ECharts) |
| Multiple generated resources | Write files to a dedicated directory |
| Short reply, status confirmation | Direct conversation output |
| User explicitly says "just tell me" | Direct conversation output |

Example: a "travel planning skill" should clearly produce an HTML itinerary report, not dump text into the chat.
Ask and confirm during the interview, then write an explicit "Output Spec" section in the generated SKILL.md.

```markdown
## Output Spec

The final output of this skill is an HTML itinerary report saved to `.workspace/<project_name>/itinerary.html`.
Do not output content directly into the conversation, even if it is short.
```

---

### Phase 2: Interview & Research

Proactively ask about edge cases, input/output formats, example files, success criteria, dependencies.
Use `web_search` and `read_webpages_as_markdown` to research best practices and API docs.
Wait until the interview is done before writing test cases.

**Note**: This environment has no browser, but `web_search` and `read_webpages_as_markdown` are available.
Use them to research best practices, tool docs, and description patterns for similar skills.

---

### Phase 3: Output Plan Document

After the interview, write the plan to `<workspace-skills-dir>/<skill-name>_plan.md` (at the root of `<workspace-skills-dir>/`, not inside the skill subdirectory — this avoids pre-creating the skill directory). Also present the plan in chat for the user to read.

Plan document contents:
- Skill scope and boundaries (what it can/cannot do)
- Tool list with selection rationale (with code format examples)
- Expected SKILL.md structure outline
- Whether `scripts/`, `references/`, `assets/` subdirectories are needed
- Final output form (from Phase 1 decision)
- Evaluation plan (test prompts, expected outputs)

**Wait for user confirmation before proceeding to Phase 4.**

---

### Phase 4: Check Conflicts and Write Files

After user confirms the plan, **check for name conflicts first**, then create files.

**Conflict check** — look at the `<available_skills>` block already in the system prompt to see if a skill with the same name already exists. No tool call or shell command is needed for this step.

**Conflict rules:**
- Same name is a built-in skill (system level, `can_override: false`): **Cannot overwrite**.
  - Ask the user to pick a **new** name, re-confirm, then write to `skills/<new-name>/`.
- Same name already exists at `<workspace-skills-dir>/<name>/`: Ask user for confirmation.
  - If confirmed: delete the entire directory first, then recreate from scratch (do not edit in place).
- No conflict: proceed to write files directly.

**Writing SKILL.md:**

SKILL.md **must** start with YAML frontmatter — the packaging validator rejects files without it.

```markdown
---
name: skill_name
description: "One sentence on what this skill does. Use when [specific trigger conditions — what the user is trying to accomplish]. Also use when user says [example phrases like 'do X', 'help me with Y', 'turn this into Z']."
---

# Skill Name

...body content...
```

Frontmatter fields:
- **name** (required): lowercase letters/digits/underscores only; must not be empty; must start with a letter; no trailing underscore; no consecutive underscores (`__`); length 2–64 chars; must exactly match the directory name
- **description** (required): English, max 1024 chars, no angle brackets `<` `>`.
  Must contain two parts:
  1. **Capability summary**: what this skill does (one sentence)
  2. **Trigger conditions**: when the AI should load it ("Use when...") and example user phrases ("Also use when user says...")
  The more specific the trigger conditions, the more accurately the AI will recognize when to load this skill. A description with no trigger guidance causes the skill to either never load or trigger on the wrong requests.
- Other common optional keys: `license`, `allowed-tools`, `metadata`, `compatibility`; you may add any extra YAML keys as needed

**Note:** Packaging validation only requires `name` and `description` in frontmatter; there is no fixed whitelist of keys.

**MCP config templates:** If a skill should let other users register the same MCP server, it may include an MCP config template in SKILL.md. Use environment variable placeholders for sensitive values. Do not duplicate the field-level rules or examples here; refer to the `using-mcp` skill for supported fields, examples, and workflow.

Directory structure (paths relative to `.workspace/`, i.e. use `<workspace-skills-dir>/<skill-name>/...` with file tools):

```
<workspace-skills-dir>/<skill-name>/
├── SKILL.md          (required)
├── (no plan.md here — plan file lives at <workspace-skills-dir>/<skill-name>_plan.md)
├── evals/
│   └── evals.json    (test cases)
├── scripts/          (executable scripts, optional)
├── references/       (reference docs loaded on demand, optional)
└── assets/           (templates, icons, fonts, optional)
```

**Progressive loading principle**:
1. Metadata (name + description): always in context (~100 words)
2. SKILL.md body: loaded when triggered (ideally < 500 lines)
3. Subdirectory resources: loaded on demand (no size limit)

Keep SKILL.md concise. Move complex content to `references/`, with clear pointers in the body about when to read them.

**Merge-first principle**: Before splitting, check — if a reference file must be read every time the Skill triggers (e.g. persona definitions, voice rules, core examples), merge it into SKILL.md. The `references/` directory is only for "consult on demand" content that most requests don't need. An extra file read = an extra LLM request; don't split when merging works.

**Write skill_config.yaml:**

After all skill files are written, immediately write (overwrite if exists) `<workspace-skills-dir>/skill_config.yaml` with YAML content.

Only write the `dir` field — this file tracks which skill directory was most recently created:

```yaml
skill:
  dir: "my-skill"
```

---

### Phase 5: Test

Write 2-3 realistic test prompts — the kind a real user would actually say. Share with the user first.

Save test cases to `<workspace-skills-dir>/<skill-name>/evals/evals.json` (relative to `.workspace/`):

```json
{
  "skill_name": "my-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description of expected result",
      "assertions": []
    }
  ]
}
```

**Running tests (using `using-llm` to simulate with_skill / baseline):**

This environment has no sub-agents. Use `using-llm` to call an LLM programmatically:
1. Load `using-llm` skill and read the SKILL.md content
2. For each test case, make two LLM calls:
   - **with_skill**: system prompt includes the full SKILL.md content
   - **baseline**: system prompt is a generic task description only, no SKILL.md
3. Write results to `<workspace-skills-dir>/<skill-name>/evals/iteration-N/case-N-with_skill.json` and `case-N-baseline.json`
4. Grade outputs against assertions, write `grading.json`

Results directory: `<workspace-skills-dir>/<skill-name>/evals/iteration-N/` (relative to `.workspace/`)

**Grading and aggregation:**

```python
# <workspace-eval-path>: absolute path to this iteration's eval directory in the workspace
#   e.g. /app/.workspace/<workspace-skills-dir>/<skill-name>/evals/iteration-N
shell_exec(
    command='python scripts/aggregate_benchmark.py <workspace-eval-path> --skill-name <skill-name>'
)
```

**Generating eval report (no browser — output static HTML):**
This environment has no browser. Use `--static` mode to output a standalone HTML file.

```python
# All paths are absolute workspace paths
shell_exec(
    command='python eval-viewer/generate_review.py <workspace-eval-path> --skill-name <skill-name> --benchmark <workspace-eval-path>/benchmark.json --static <workspace-reports-path>/<skill-name>-eval-iteration-N.html'
)
```

After generation, tell the user the report path so they can open it in the frontend file manager.

---

### Phase 6: Iterate

Improve the skill based on user feedback:
1. Apply improvements to SKILL.md
2. Put new test results in `iteration-N+1/` directory
3. Regenerate the report, pass `--previous-workspace` pointing at the previous iteration

Continue until: user is satisfied, all feedback is empty, or no meaningful progress.

**When improving, keep in mind:**
- Generalize from feedback — the skill must work for a million future prompts, not just your test cases
- Keep SKILL.md lean — remove things not pulling their weight
- Explain the "why" — LLMs respond better to reasoning than rigid rules

---

### Phase 7: Description Optimization

After creating or improving a skill, offer to optimize the `description` field for better triggering accuracy.

This project uses the `using-llm` skill for description evaluation:
1. Generate 20 test queries (mix of should-trigger / should-not-trigger); have user confirm
2. Load `using-llm` skill; use LLM to simulate "would AI load this skill given this description?"
3. Test different description versions, compare trigger rates
4. Update SKILL.md frontmatter with the best-performing description

See `references/system-tools.md` for the detailed procedure.

---

### Optional: Security Review

If the user wants to verify the security of the newly created skill before packaging or sharing — for example, to confirm it contains no dangerous patterns — load `skill-vetter` to run a review:

```
read_skills(skill_names=["skill-vetter"])
```

---

### Phase 8: Ask About Packaging and Upload

After the skill is done and user-confirmed, always ask:

> "Would you like to package this skill and upload it to your skill library? Or just package without uploading?"

**Important:** If the user only asks to "package", "pack only", or "build the .zip file" without clearly requesting upload to the skill library, you **must** use the package-only command (do **not** pass `--upload`). Only use `--upload` when the user explicitly agrees to upload or uses phrasing like "package and upload" / "upload to my skill library".

`package_skill.py` automatically runs `quick_validate.py` before packaging. Checks include:
1. Directory name and `name` field must contain only English letters, digits, and underscores — no hyphens, Chinese characters, spaces, or other special characters
2. `name` field must exactly match the directory name

If validation fails, fix the issues and retry.

**Package only (default CLI; use when user asks only to package):**

```python
# <workspace-skill-path>: absolute path to this skill under the workspace skills directory
#   e.g. /app/.workspace/<workspace-skills-dir>/<skill-name>
# Without output_dir, defaults to the skill directory's parent: <workspace-skills-dir>/<skill-name>-v1.0.0.zip
# --no-upload can be omitted (equivalent to default behavior)
shell_exec(
    command='python scripts/package_skill.py <workspace-skill-path> --version 1.0.0'
)
```

**Package and upload to skill library (only when user explicitly wants upload; requires `--upload`; this runs `package_skill.py` then `upload_skill.py` in sequence):**

```python
# Optional args: --name-zh "Chinese Name" --name-en "English Name" (passed to upload_skill.py)
shell_exec(
    command='python scripts/package_skill.py <workspace-skill-path> --version 1.0.0 --upload'
)
```

**Package first, upload later (two separate steps):** Run packaging only first; when the user wants to upload, call `upload_skill.py` with the path to the generated `.zip` file.

```python
shell_exec(
    command='python scripts/upload_skill.py <absolute-path-to-.zip-file>'
)
```

Optional: `python scripts/upload_skill.py <path> --name-zh "..." --name-en "..."`

- `--version` is optional but recommended for first release
- `--name-zh` / `--name-en` are optional i18n name overrides when uploading (`--upload` or standalone `upload_skill.py`); if omitted the name from SKILL.md frontmatter is used
- Do not package by default. Do not skip this step.

---

---

---

## Reference Files

- `references/system-tools.md` — Detailed descriptions and Python call examples for all available project tools
- `references/schemas.md` — JSON schemas for evals.json, grading.json, etc.
