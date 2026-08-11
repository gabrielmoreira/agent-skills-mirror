---
name: crew-creator
description: |
  Manage and optimize custom agent definition files (IDENTITY.md, AGENTS.md, SOUL.md, TOOLS.md).
  Also handles first-time employee initialization when .workspace/ has no IDENTITY.md.
  Use when users want to edit agent identity, modify workflow instructions, adjust personality,
  add/remove tools, optimize prompts, or initialize a new employee from scratch.
  Trigger signals: 'modify prompt', 'change identity', 'add tool', 'remove tool', 'optimize workflow',
  'adjust personality', 'initialize employee', '修改提示词', '改身份', '加工具', '去掉工具',
  '优化能力', '调性格', '初始化员工', '创建员工'.
  Do NOT use for: skill creation (use skill-creator), skill searching (use find_skills tool).
---

# Agent Prompt Manager

Manages the 4 core employee definition files under `.workspace/`, helping users view, edit, and optimize their employee's identity, instructions, personality, and tool configuration.
Also handles first-time employee initialization when the workspace has no definition files.

## Language Generation Strategy

The system injects `<user_preferred_language>` indicating the user's preferred language. Follow these rules when generating employee files:

**Default single-language mode**: Generate all content in the user's preferred language. YAML header uses single-language fields only.

**Only enable multilingual mode when the user explicitly requests multiple languages**. Use clear language-specific sections or fields. Do not use HTML comment annotations for translations.

## Employee Initialization Flow

When `.magic/IDENTITY.md` does not exist, the workspace has no employee yet and you should guide the user through initialization.

### Detection

Use `list_dir` to check `.magic/`. If `IDENTITY.md` is missing, enter the initialization flow.

### Information Gathering (ask the user conversationally)

Collect information in rounds; you may combine questions but don't overwhelm the user.

**Before gathering, check user's preferred language**: Look at `<user_preferred_language>`. Communicate and collect information in that language.

**Round 1 (required)**:
1. **Employee name**: Ask in the user's preferred language (e.g., for English users: "What name would you like to give your employee?")
2. **Employee role**: (e.g., "What role will this employee take on?")
3. **One-line description**: What does this employee mainly do?

**Only ask for translations when the user explicitly requests multiple languages** (e.g., "need bilingual support").

**Round 2 (recommended but optional)**:
4. **Role definition**: A richer description of capabilities, expertise, and working style (goes into IDENTITY.md body)
5. **Workflow / rules**: What workflow should this employee follow? Any special rules? (goes into AGENTS.md)

**Round 3 (optional, user may skip)**:
6. **Personality and communication style**: What personality should the employee have? (e.g. rigorous, lively, concise) (goes into SOUL.md)

If the user signals intent to skip (e.g., "later", "that's fine for now"), proceed immediately with whatever has been collected.

### Generating Files

After collecting info, write a JSON config and call the init script:

**Single-language mode (default)**:
```python
# 1. Write collected info as JSON config (no _en suffix variants needed)
write_file(
    path=".crew_init_config.json",
    content='{"name": "Research Assistant", "role": "Academic Researcher", "description": "A professional research assistant", "role_body": "You are an academic researcher...", "instructions": "...", "personality": "..."}'
)

# 2. Call the init script
shell_exec(
    command="python scripts/init_crew.py --config .workspace/.crew_init_config.json"
)
```

**Only when the user explicitly requests multiple languages**, supplement with auxiliary language fields (e.g., `name_cn`, `role_body_cn`, etc.):
```python
write_file(
    path=".crew_init_config.json",
    content='{"name": "Research Assistant", "name_cn": "<translated name>", "role": "Academic Researcher", "role_cn": "<translated role>", "description": "A professional research assistant", "description_cn": "<translated description>", ...}'
)
```

The script generates files based on the config (TOOLS.md and SKILLS.md are intentionally not created — the system uses defaults):
- `IDENTITY.md` — always generated (YAML header + role definition body)
- `AGENTS.md` — generated if workflow instructions were provided
- `SOUL.md` — generated if personality was provided

### After Initialization

1. Show the generated files to the user via `read_files`
2. Ask if they want any adjustments
3. Clean up the temp config: `delete_files(path=".crew_init_config.json")`
4. Inform the user: TOOLS.md and SKILLS.md were not generated (system defaults apply); they can be added later through employee management

## File Responsibility Mapping

| File | Dimension | Responsibility | Required |
|------|-----------|----------------|----------|
| `IDENTITY.md` | WHO — Identity | Name, role, description + role definition body | **Required** |
| `AGENTS.md` | WHAT — Instructions | Workflow, rules, special directives | Recommended |
| `SOUL.md` | HOW — Personality | Core personality, communication style, behavior guidelines | Optional |
| `TOOLS.md` | WITH WHAT — Tools | Tool whitelist (YAML) + usage preferences | Optional |

## Editing Workflow

### General Flow (applies to all files)

1. **Read current content**: Use `read_files` to read the target file's existing content
2. **Load quality guide**: Read reference file `references/prompt-engineering-guide.md`
3. **Load format spec**: Read reference file `references/crew-file-format.md`
4. **Write/modify content**: Edit following the format spec and quality guide
5. **Show quality assessment**: Present the modified content with a quality assessment summary
6. **Write after confirmation**: After user confirms, use `write_file` or `edit_file` to save

### Quality Assessment Summary Format

After each edit, present:

```
## Quality Assessment

| Check Item | Status | Notes |
|------------|--------|-------|
| Role clarity | pass | ... |
| Instruction specificity | pass | ... |
| Language consistency (check if multilingual) | pass | ... |
| Format compliance | pass | ... |
| ... | ... | ... |
```

## File-Specific Editing Guides

### IDENTITY.md — Identity Definition

Contains YAML header (metadata) and body (role definition).

**YAML header fields**: `name`, `role`, `description` in the user's preferred language. Only in multilingual mode, add auxiliary language variants: `name_cn`/`name_en`, `role_cn`/`role_en`, `description_cn`/`description_en`.

**Body**: Write directly in single-language mode. In multilingual mode, use `<!--xx -->` comment format with the user's preferred language as active content.

**Key points**:
- Role definition must be specific; avoid vague descriptions like "you are an AI assistant"
- Define expertise domains, target users, and usage scenarios
- In multilingual mode, all language versions must be semantically equivalent

### AGENTS.md — Workflow Instructions

Pure Markdown, no YAML header. Defines this employee's specific workflow and rules.

**Key points**: Prioritized instructions, numbered lists, decision logic (if/then/else), output format specs.

### SOUL.md — Personality and Behavior

Pure Markdown, no YAML header. Defines the employee's personality and behavior guidelines.

**Key points**: Core traits (3-5 keywords + behavioral descriptions), communication style, behavior boundaries.

### TOOLS.md — Tool Management

Contains YAML header (tool whitelist) and optional body (tool usage preferences).

**Key points**:
- Tools can only be selected from the project's available tool list — use `scripts/tools.py` to query dynamically
- Recommend tool combinations based on employee function
- Special tool usage preferences go in the body section

## Tool Management Workflow

When users want to add or remove tools:

1. **Query available tools**: Use the script to dynamically scan (see "Tool Query Script" section)
2. Read current TOOLS.md tool list
3. Evaluate tool needs based on employee function
4. Present tool change comparison to user
5. Write to TOOLS.md after user confirmation

## Tool Query Script

Use `scripts/tools.py` to dynamically scan all registered tools in the project (data source: `config/tool_definitions.json`).

### List all available tools

```python
shell_exec(
    command="python scripts/tools.py list"
)
```

### View details of a specific tool (parameters, description)

```python
shell_exec(
    command="python scripts/tools.py detail web_search"
)
```

### Search tools by keyword

```python
shell_exec(
    command="python scripts/tools.py search image"
)
```

## Multilingual Content Format

**Default single-language mode**: Write staff files directly in the user's preferred language. Do not use HTML comment annotations for translations.

**Only when the user explicitly requests multiple languages**, use ordinary language-specific sections. Keep the user's preferred language first, then add the auxiliary language below it with a clear heading:

```markdown
## English

English content.

## Chinese

Chinese content.
```

## Reference Documents

Reference documents with detailed guides:

- **crew-file-format** — Complete format specs and examples for each definition file
- **prompt-engineering-guide** — Prompt engineering best practices (structure templates, quality checklists, anti-pattern detection)
- **available-tools** — Tool combination recommendations by function (fallback reference; prefer `scripts/tools.py` for dynamic queries)
