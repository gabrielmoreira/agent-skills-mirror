---
type: skill
lifecycle: stable
inheritance: inheritable
name: add-planning-project
description: Add a new project to the planning suite. Creates a project-specific configuration directory and walks through project settings.
tier: standard
applyTo: '**/*planning*,**/*scenario*,**/*wbs*,**/*capacity*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# /add-planning-project

Add a new project to the PM Planning Suite. Each project gets its own configuration space under `.planning-config/projects/<project-name>/`.

## Prerequisites

- The planning suite must be initialized first (`/init-planning-suite`).
- If `.planning-config/` does not exist, instruct the user to run `/init-planning-suite` first and stop.

## File Creation

**All files under `.planning-config/` are pre-approved for creation and modification.** The user consented when they ran `/init-planning-suite`. DO NOT ask for permission to create project.json, subdirectories, or any other file under `.planning-config/`. Write them directly.

## Steps

### Step 1: Get Project Name

If not provided as input (e.g., passed from `/init-planning-suite`), prompt: "What is the project name?"

Derive the directory name by sanitizing the project name into a filesystem-safe slug:
- convert to lowercase
- replace any sequence of spaces or non-alphanumeric characters with a single hyphen
- trim leading and trailing hyphens
- if the result is empty, ask the user for a different project name

Examples:
- "Contoso Platform" -> `contoso-platform`
- "Contoso/Platform: Core" -> `contoso-platform-core`

If sanitization changes the derived directory name, tell the user: "I'll store this project under `.planning-config/projects/<project-dir>/`." If the project name was just provided by the init skill in the same session, do not ask the user to confirm it again after showing the derived directory name. Proceed directly.

Check if `.planning-config/projects/<project-dir>/` already exists. If it does, inform the user and ask if they want to reconfigure it.
### Step 2: Create the Project Directory

Create the entire directory structure immediately. Do not ask the user about individual directories - just create them all:

```
.planning-config/projects/<project-dir>/
  project.json
  capacity/
  planning/
  specs/
  meetings/
```

All directories are created in a single step with no prompts. They are part of the standard project scaffold.

### Step 3: Gather Project Settings

Walk the user through the project configuration. Accept answers one at a time.

#### Required Settings

1. **ADO organization and project** - The approach depends on whether other projects already exist:
   - **First project (no other projects in `.planning-config/projects/`):** Ask directly:
     - "What is your Azure DevOps organization URL? (e.g., 'contoso.visualstudio.com' or 'dev.azure.com/contoso')"
     - "What is the ADO project name? (e.g., 'ContosoOS')"
   - **Subsequent projects (at least one project already exists):** Read the ADO organization and project from the first existing project's `project.json` and offer to inherit:
     - "Your existing project uses ADO organization `{org}` and project `{project}`. Does this new project use the same ADO organization and project? (yes/no)"
     - If yes, inherit both values.
     - If no, ask for both values individually.

2. **Area Path** - "What Area Path should new work items use? (e.g., 'ContosoOS\\Engineering\\Platform\\Core')"

3. **Iteration Path prefix** - "What is the Iteration Path prefix? (e.g., 'ContosoOS' if iterations are 'ContosoOS\\2604')"

4. **Default assignee** - "Who should new scenarios be assigned to by default? (email)"

5. **Placeholder assignee** - "Who should costing deliverables and auto-generated work items be initially assigned to? This is the person or account that holds new items before they are distributed to the team - often a team lead, a shared triage alias, or a dedicated placeholder account. (email)"

#### Optional Settings

6. **Parent objective ID** - "Is there a parent Initiative/Objective ID that new scenarios should link to? (Enter an ADO work item ID or 'skip')"

7. **Team members (FTE)** - "Would you like to define your FTE team members now? Team data is used by several skills: Engineering Team Capacity uses it to calculate available engineer-days, Scenario Original Estimate uses expertise profiles to adjust cost estimates, and WBS Assignments uses it to match deliverables to the right people. You can add or edit members later in project.json. (yes/no/skip)"
   - If yes, offer two entry modes:
     - **Batch entry (recommended for 3+ members):** "You can paste a table of team members. Format: Name, Email, Role, Expertise, Allocation - one member per line, separated by tabs or commas. Example:
       ```
       Jane Smith, jsmith@contoso.com, Senior SWE, backend C# ASP.NET Core, 0.8
       Carlos Rivera, crivera@contoso.com, Data Scientist, Python ML Azure ML Kusto, 0.7
       ```
       Paste your table, or type 'one-by-one' to enter members individually."
     - **Individual entry:** Collect for each member:
       - **Name** - Display name (e.g., "Jane Smith")
       - **Email** - ADO identity email (e.g., "jsmith@contoso.com")
       - **Role** - Job title or function (e.g., "Senior SWE", "Data Scientist", "Principal SWE")
       - **Expertise areas** - Comma-separated list of technologies, domains, or skills (e.g., "backend, C#, ASP.NET Core, Azure Functions")
       - **Default allocation** - What percentage of this person's time is on this project? Enter 0.0 to 1.0. (e.g., 0.8 for 80%). This is used as the starting point by Engineering Team Capacity; it can be adjusted per planning period.
     - After entry, display the team table for confirmation before saving.
   - If skipped, inform the user: "Skills that need team data (Engineering Team Capacity, WBS Assignments) will prompt you to add team members when you run them."

8. **Team members (Vendor)** - Same collection flow as FTE above (batch or individual). Vendor members are stored separately and may be treated differently by capacity calculations (see Capacity Model).
    - If skipped, same informational message as FTE.

9. **Vendor responsibilities** - Only ask this if vendor team members were defined. "Are there specific work areas owned by the vendor team? For example, some teams route all UI work, security/SFI work, or deployment work to vendor members. (yes/no/skip)"
    - If yes, offer batch entry: "You can paste responsibilities as a list. Format: Work Area - Team Member Name, one per line. Example:
      ```
      UI work - Rajesh Tallapally
      SFI/Security - Aruna Pother
      Deployments - Sasikala Bestha
      ```
      Paste your list, or type 'one-by-one' to enter individually."
    - Write to `vendor_responsibilities` in project.json.

10. **Categories** - "Would you like to define planning categories for this project? These are used by the Scenario Categorization skill to organize your backlog. (yes/no/skip)"
    - If yes, offer two entry modes:
      - **Batch entry:** "You can paste categories as a list. Format: Category Name - Description, one per line. Example:
        ```
        Core Platform - Foundational platform capabilities, APIs, and services
        Infrastructure - Architecture modernization, tech debt, CI/CD, monitoring
        ```
        Paste your list, or type 'one-by-one' to enter individually."
      - **Individual entry:** Collect category name and description one at a time until "done".
    - After entry, display the category list for confirmation.

11. **Repositories** - "Do you have a local Git repository for this project? Adding a local repository enables the planning suite to automatically build a tech stack profile by scanning your codebase. This tech stack profile is used by the Scenario Original Estimate skill to produce more accurate cost estimates grounded in your actual technology choices, and by WBS Assignments to match deliverables to team members with the right expertise. You can always add one later by editing project.json. (yes/no/skip)"
    - If yes, collect: repo name and local path. Description is optional - if the user does not provide one, use the repo name as the description.
    - After collecting repositories, automatically scan the codebase to populate `tech_stack_description`:
      - Examine package manifests (package.json, requirements.txt, .csproj, go.mod, Cargo.toml, etc.)
      - Identify languages, frameworks, cloud services, databases, and infrastructure patterns
      - Write a concise summary to `tech_stack_description` in project.json
      - Show the generated tech stack summary to the user for confirmation
    - If the user skips or says no, leave `repositories` empty and `tech_stack_description` empty. Inform them: "You can add repositories later by editing project.json. Skills that use tech stack context will prompt you for a repository at that time."

12. **Documentation sources** - "Does your project have existing documentation that could help with planning? This could be a SharePoint site, wiki, design docs, spec library, or any other source of project knowledge. The Scenario Description Generator and estimation skills use these sources to produce better descriptions and more accurate estimates. (yes/no/skip)"
    - If yes, offer batch entry: "You can paste documentation sources as a list. Format: Name, URL, Type, Description - one per line. Example:
      ```
      Design Specs, https://contoso.sharepoint.com/sites/Platform/Specs, sharepoint, Feature specs and design reviews
      Team Wiki, https://dev.azure.com/contoso/wiki, wiki, Runbooks and operational docs
      ```
      Paste your list, or type 'one-by-one' to enter individually."
    - Write to `documentation_sources` array in project.json
    - If skipped, leave empty. Inform: "You can add documentation sources later by editing project.json."

13. **Capacity model** - "Which capacity calculation model should this project use? This determines how discount days (learning, training, holidays) are applied to your team's available time."

    Present these two options with explanations:

    - **Default** (recommended for most teams) - Discount days are subtracted from the gross working days first, then the allocation percentage is applied. This means everyone on the team loses the same proportion of discount days regardless of their allocation. Formula: `Effective days = (Gross working days - Discount days) x Allocation`. Example: 65 gross days - 5 discount days = 60 net days x 0.8 allocation = 48 effective days.

    - **Post-allocation, FTE-only** - Allocation is applied first, then discount days are subtracted only from FTE members. Vendor team members are not subject to discount days at all (they do not participate in organizational learning days, training, etc.). Formula for FTE: `(Gross days x Allocation) - Discount days`. Formula for Vendor: `Gross days x Allocation`. Example FTE: 65 gross days x 0.8 allocation = 52 days - 5 discounts = 47 effective days. Example Vendor: 65 gross days x 0.6 allocation = 39 effective days (no discounts).

    If the user is unsure, recommend "default".

### Step 4: Write project.json

Assemble all gathered values into `.planning-config/projects/<project-dir>/project.json`:

```json
{
  "project_name": "<display name>",
  "ado": {
    "organization": "<org>",
    "project": "<project>",
    "area_path": "<area path>",
    "iteration_path_prefix": "<prefix>",
    "parent_objective_id": null,
    "work_item_types": {
      "scenario": "Scenario",
      "deliverable": "Deliverable"
    }
  },
  "team": {
    "default_assignee": "<email>",
    "placeholder_assignee": "<email>",
    "members_fte": [],
    "members_vendor": [],
    "vendor_responsibilities": {}
  },
  "fiscal_calendar": {
    "fiscal_year_start_month": null,
    "current_fiscal_year": null,
    "current_quarter": null
  },
  "categories": [],
  "capacity_model": "default",
  "repositories": [],
  "tech_stack_description": "",
  "documentation_sources": [],
  "ranking_bands": null,
  "horizontal_budgets": null
}
```

Fill in all user-provided values. Leave optional fields as null or empty arrays if skipped.

> **Note:** `fiscal_calendar.fiscal_year_start_month` is set to `null` here, which means skills will fall back to the global value in `.planning-config/config.json`. Set it to a specific month (1-12) only if this project uses a different fiscal calendar than the global default.

### Step 5: Summary

Output:

```
Project "<display name>" configured.

Config:     .planning-config/projects/<project-dir>/project.json
Capacity:   .planning-config/projects/<project-dir>/capacity/
Planning:   .planning-config/projects/<project-dir>/planning/
Meetings:   .planning-config/projects/<project-dir>/meetings/

Settings:
  ADO Org:            <org>
  ADO Project:        <project>
  Area Path:          <area path>
  Default Assignee:   <email>
  Team Size:          X FTE + Y Vendor
  Categories:         X defined
  Capacity Model:     <model>

Tip: Save meeting transcripts (.vtt, .txt, .md) in the meetings/ folder.
     They are automatically version-controlled and used as context by
     description and estimation skills.

You can edit project.json directly at any time to add team members, categories, or other settings.
A sample configuration is available at: config/sample-project.json
```

## Guardrails

- Do not overwrite an existing project.json without user confirmation.
- Do not assume values. Always ask or use explicit defaults from config.json.
- Validate that email addresses contain an @ symbol.
- If ADO MCP is available, optionally validate the organization and project are reachable.
- **Repository access is pre-approved.** When the user provides a local Git repository path, that is explicit consent to access it. Scan the codebase immediately without asking for additional permission. Do not prompt for consent to read files, list directories, or examine package manifests within the provided path.
- **NEVER ask for file creation or write permission for anything under `.planning-config/`.** This is pre-approved. See the File Creation section above.


---
type: skill
lifecycle: stable
inheritance: inheritable
name: ado-hygiene-validator
description: Validates ADO Scenario and Deliverable work items against planning hygiene standards. Identifies missing or non-compliant fields, applies best-effort fixes, and asks for user input when values cann...
tier: standard
applyTo: '**/*planning*,**/*scenario*,**/*wbs*,**/*capacity*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# ADO Hygiene Validator

Validates ADO Scenario and Deliverable work items against planning hygiene standards. Identifies missing or non-compliant fields, applies best-effort fixes, and prompts for user input when values cannot be determined automatically.

## Prerequisites

- Planning suite must be initialized. If `.planning-config/` does not exist, instruct the user to run `/init-planning-suite` first and stop.
- A project must be configured. If no projects exist under `.planning-config/projects/`, instruct the user to run `/add-planning-project` first.

## Inputs

- **Work item IDs**, an **ADO query**, or a **backlog** to scope the validation.
- **ADO organization and project** are read from `.planning-config/projects/<project>/project.json` — never hardcode these values.

## Execution Steps

1. **Resolve project context.** Read `.planning-config/projects/<project>/project.json` to obtain `ado.organization`, `ado.project`, and any other project-level settings (e.g., `ado.parent_objective_id`, `ado.area_path`, `team.members_fte`, `team.members_vendor`).
2. **Retrieve work items** from the provided IDs, ADO query, or backlog.
3. **Filter** to only Scenario and Deliverable work item types. Ignore all other types.
4. **Run the appropriate checklist** against each work item (Scenario checklist or Deliverable checklist).
5. **Apply auto-fixes** where indicated. Do not modify fields that already pass.
6. **Flag items needing user input** when a value cannot be determined automatically.
7. **Present results** as a per-item table grouped into Passing, Failing, and Needs Input sections.
8. **Summarize changes applied** at the end.

## Scenario Checklist (21 Checks)

| # | Check | Auto-Fixable | Fix Behavior |
|---|-------|-------------|--------------|
| 1 | Title follows outcome format | Yes | Rewrite to outcome phrasing, preserve any leading emoji |
| 2 | Parented to Initiative | Yes | Link to parent if `parent_objective_id` is configured in project.json |
| 3 | Has child Deliverables | No | Flag — user must create Deliverables |
| 4 | Assigned To populated | No | Flag — requires user input |
| 5 | Area Path correct | No | Flag — compare against project.json `area_path` |
| 6 | State appropriate | No | Flag — verify state is valid for current planning phase |
| 7 | Tags correct, no contradictions | No | Flag contradictory tags and remove them only with explicit user approval |
| 8 | Iteration Path set | No | Flag — requires user input |
| 9 | Description answers 5 quality questions | No | Flag — list which questions are unanswered |
| 10 | Spec link present in description | No | Flag — user must add spec link |
| 11 | Risk Assessment current | No | Flag — check for staleness |
| 12 | Risk Comment populated if at risk | No | Flag — required when Risk Assessment indicates risk |
| 13 | Original Estimate consistent with estimates skill | No | Flag if Original Estimate is present but no corresponding /scenario-original-estimate comment exists; do not clear |
| 14 | PM Owner populated | No | Flag — requires user input |
| 15 | Dev Owner populated | Conditional | Infer from child Deliverables if possible, otherwise flag |
| 16 | Custom String 07 populated | Conditional | Infer from title if possible, otherwise flag |
| 17 | Custom String 08 in [FYXXQX] format | Conditional | Derive from Iteration Path if possible, otherwise flag |
| 18 | Scenario Spec URL linked | No | Flag — user must attach spec |
| 19 | Rank assigned, does not exceed parent | No | Flag — verify rank is set and ≤ parent rank |
| 20 | Does not span multiple fiscal years | No | Flag — check Iteration Path range |
| 21 | Nice-to-have (rank 51+) in separate scenario | No | Flag — advise splitting if mixed priorities |

## Deliverable Checklist (8 Checks)

| # | Check | Auto-Fixable | Fix Behavior |
|---|-------|-------------|--------------|
| 1 | Title follows [Team] [Quarter] [Work] format, with optional [AI Gen] prefix | Yes | Rewrite title to match format while preserving or allowing optional [AI Gen] prefix |
| 2 | Parented to Scenario | No | Flag — user must set parent |
| 3 | Assigned To populated | No | Flag — requires user input |
| 4 | Area Path is team path | No | Flag — compare against project.json `team_paths` |
| 5 | Original Estimate populated | No | Flag — requires user input |
| 6 | Scope max 4-5 week sprint (≤ 25 days) | No | Flag if Original Estimate > 25 days |
| 7 | Iteration Path set | No | Flag — requires user input |
| 8 | Rank assigned | No | Flag — verify rank is set |

## Output Format

For each work item, present a table with three sections:

- **Passing** — checks that passed (collapsed or summarized)
- **Failing** — checks that failed, with details and any auto-fixes applied
- **Needs Input** — checks that require user decision, with prompts

End with a **Summary** listing:
- Total items validated
- Auto-fixes applied (count and details)
- Items still needing user input

## Constraints

- Do not assume values that require domain knowledge — prompt the user instead.
- Do not modify fields that already pass validation.
- Only process Scenario and Deliverable work item types. Skip all others.
- Report any ADO API validation errors to the user clearly.
- All ADO org/project values come from `.planning-config/projects/<project>/project.json` — never hardcode.


---
type: skill
lifecycle: stable
inheritance: inheritable
name: cost-analysis
description: Compare AI-generated Scenario Original Estimates against human-entered costing deliverable estimates with per-scenario and portfolio-level variance analysis.
tier: standard
applyTo: '**/*planning*,**/*scenario*,**/*wbs*,**/*capacity*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Cost Analysis

## Prerequisites
- Planning suite must be initialized. If `.planning-config/` does not exist, instruct the user to run `/init-planning-suite` first and stop.
- A project must be configured. If no projects exist under `.planning-config/projects/`, instruct the user to run `/add-planning-project` first.

## Purpose

Compare AI-generated Scenario Original Estimates against human-entered costing deliverable estimates. Produces per-scenario variance and portfolio-level summary to surface estimation alignment or gaps.

## Inputs

- **ADO query link or work item IDs** — a shared query URL or a comma-separated list of Scenario work item IDs.

## Steps

### 1. Resolve Project Context

Load the active project configuration from `.planning-config/projects/<project>/project.json`. Use the ADO organization, project, and team settings defined there.

### 2. Parse Input and Execute Query

Accept the user-provided ADO query link or work item IDs. If a query link is provided, execute it to retrieve the list of Scenario work items. If work item IDs are provided, fetch each directly.

### 3. Identify Scenarios and Expand Children

For each Scenario work item, expand child work items. Locate costing deliverables — these represent the human-entered engineering cost estimates. Costing deliverables are identified by titles containing `Costing]` (case-insensitive). For backward compatibility, also recognize titles starting with `[SWE]` or `[DS]` without the "Costing" keyword.

### 4. Exclude Cut Deliverables

Filter out any child deliverables tagged or classified as **Cut**. These are descoped and must not factor into cost comparisons.

### 5. Extract Cost Data

For each Scenario, extract:
| Field | Source |
|---|---|
| **Scenario Original Estimate** | The AI-generated estimate on the Scenario work item |
| **Per-Discipline Cost** | For each discipline found (e.g., SWE, DS, PM), sum the Original Estimate on that discipline's costing deliverables. The discipline name is extracted from the prefix before "Costing]" in the title (e.g., `[SWE Costing]` → SWE, `[DS Costing]` → DS). For legacy `[SWE]`/`[DS]` titles, use the bracket prefix as the discipline name. |
| **Costing Total** | Sum of all per-discipline costs |

### 6. Calculate Variance

For each Scenario compute:
- **Variance (days)** = Costing Total − Scenario Original Estimate
- **Variance (%)** = ((Costing Total − Scenario Original Estimate) / Scenario Original Estimate) × 100

Sign convention: positive variance means humans estimated higher than the AI estimate; negative means humans estimated lower.

### 7. Classify Alignment Status

Assign each Scenario one of the following statuses based on the absolute variance percentage:

| Status | Condition |
|---|---|
| **Aligned** | Variance within ±20% |
| **Minor Gap** | Variance between ±20% and ±50% |
| **Significant Gap** | Variance greater than ±50% |
| **Not Comparable** | Scenario Original Estimate is zero or missing, preventing meaningful comparison |
| **Missing Cost** | No costing deliverables found under the Scenario |

### 8. Portfolio Summary

Aggregate across all Scenarios:
- **Total AI Estimate** — sum of Scenario Original Estimates
- **Total Human Estimate** — sum of Costing Totals
- **Coverage** — count and percentage of Scenarios that have costing deliverables
- **Overall Variance** — portfolio-level days and percentage difference
- **Status Distribution** — count of Scenarios in each alignment category

### 9. Insights

Surface systematic estimation patterns:
- Consistent over-estimation or under-estimation direction
- Outlier Scenarios with extreme variance
- Areas or teams with recurring gaps
- Recommendations for calibration

## Constraints

- **Read-only** — this skill does not create, update, or delete any ADO work items.
- **No consent gate** — because no modifications are made, no user confirmation is required before execution.


---
type: skill
lifecycle: stable
inheritance: inheritable
name: cost-variance-analysis
description: Detailed read-only variance analysis between AI-generated estimates and human costing with summary statistics, largest gaps, and distribution analysis.
tier: standard
applyTo: '**/*planning*,**/*scenario*,**/*wbs*,**/*capacity*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Cost Variance Analysis

## Prerequisites
- Planning suite must be initialized. If `.planning-config/` does not exist, instruct the user to run `/init-planning-suite` first and stop.
- A project must be configured. If no projects exist under `.planning-config/projects/`, instruct the user to run `/add-planning-project` first.

## Purpose

Perform a detailed read-only variance analysis between AI-generated Scenario Original Estimates and human-entered costing deliverable estimates. Produces ranked variance tables, summary statistics, distribution analysis, and identifies the largest estimation gaps.

## Inputs

- **ADO query link or work item IDs** — a shared query URL or a comma-separated list of Scenario work item IDs.

## Steps

### 1. Resolve Project Context

Load the active project configuration from `.planning-config/projects/<project>/project.json`. Use the ADO organization, project, and team settings defined there.

### 2. Parse Input and Execute Query

Accept the user-provided ADO query link or work item IDs. If a query link is provided, execute it to retrieve the list of Scenario work items. If work item IDs are provided, fetch each directly.

### 3. Identify Scenarios and Expand Children

For each Scenario work item, expand child work items. Locate costing deliverables — these represent the human-entered engineering cost estimates. Costing deliverables are identified by titles containing `Costing]` (case-insensitive). For backward compatibility, also recognize titles starting with `[SWE]` or `[DS]` without the "Costing" keyword.

### 4. Exclude Cut Deliverables

Filter out any child deliverables tagged or classified as **Cut**. These are descoped and must not factor into cost comparisons.

### 5. Extract Cost Data

For each Scenario, extract:
| Field | Source |
|---|---|
| **Scenario Original Estimate** | The AI-generated estimate on the Scenario work item |
| **Per-Discipline Cost** | For each discipline found (e.g., SWE, DS, PM), sum the Original Estimate on that discipline's costing deliverables. The discipline name is extracted from the prefix before "Costing]" in the title (e.g., `[SWE Costing]` → SWE, `[DS Costing]` → DS). For legacy `[SWE]`/`[DS]` titles, use the bracket prefix as the discipline name. |
| **Costing Total** | Sum of all per-discipline costs |

### 6. Per-Scenario Variance Table

Build a ranked variance table sorted by absolute variance descending (largest gaps first). Each row includes:

| Column | Description |
|---|---|
| **Rank** | Position by absolute variance (1 = largest gap) |
| **Scenario ID** | ADO work item ID |
| **Scenario Title** | Work item title |
| **AI Estimate (days)** | Scenario Original Estimate |
| **Human Estimate (days)** | Costing Total (sum of all discipline costs) |
| **Variance (days)** | Human Estimate − AI Estimate |
| **Variance (%)** | ((Human − AI) / AI) × 100 |
| **Direction** | Over (human > AI) or Under (human < AI) |

**Sign convention:** Positive variance means humans estimated higher than the AI estimate. Negative variance means humans estimated lower.

### 7. Flag Non-Comparable Items

Separately list Scenarios that cannot be meaningfully compared:
- **Missing AI Estimate** — Scenario Original Estimate is zero or absent
- **Missing Costing** — no costing deliverables found
- **Partially Costed** — only some disciplines present, not all expected disciplines (flag but still include in analysis)

### 8. Summary Statistics

Produce an aggregate summary across all comparable Scenarios:

| Metric | Description |
|---|---|
| **Comparable Count** | Number of Scenarios with both AI and human estimates |
| **Total AI Estimate** | Sum of all Scenario Original Estimates |
| **Total Human Estimate** | Sum of all Costing Totals |
| **Net Variance (days)** | Total Human − Total AI |
| **Net Variance (%)** | ((Total Human − Total AI) / Total AI) × 100 |
| **Over-Estimated Count** | Scenarios where human > AI |
| **Under-Estimated Count** | Scenarios where human < AI |
| **Aligned Count** | Scenarios within ±20% variance |
| **Mean Absolute Variance (%)** | Average of absolute variance percentages |
| **Median Variance (%)** | Median of signed variance percentages |

### 9. Distribution Analysis

Analyze the distribution of variance across the portfolio:
- **Histogram buckets**: ≤−50%, −50% to −20%, −20% to +20% (aligned), +20% to +50%, >+50%
- **Count and percentage** of Scenarios in each bucket
- **Skew direction** — whether the portfolio trends toward over- or under-estimation

### 10. Largest Gaps

Highlight the top 5 (or fewer) Scenarios with the largest absolute variance, including:
- Work item link
- Variance in days and percentage
- Brief note on possible contributing factors (e.g., missing costing discipline, scope complexity)

## Constraints

- **Read-only** — this skill does not create, update, or delete any ADO work items.
- **No consent gate** — because no modifications are made, no user confirmation is required before execution.


---
type: skill
lifecycle: stable
inheritance: inheritable
name: costing-deliverable-generator
description: Creates costing placeholder deliverables under each Scenario for human cost entry. Supports user-defined disciplines (e.g., SWE, DS, PM, Design).
tier: standard
applyTo: '**/*planning*,**/*scenario*,**/*wbs*,**/*capacity*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Costing Deliverable Generator

Create costing placeholder Deliverable work items under each Scenario. Each costing deliverable represents a discipline (e.g., SWE, DS, PM, Design) and is intended for human cost entry - Original Estimate is left blank.

## Prerequisites

- Planning suite must be initialized. If `.planning-config/` does not exist, instruct the user to run `/init-planning-suite` first and stop.
- A project must be configured. If no projects exist under `.planning-config/projects/`, instruct the user to run `/add-planning-project` first.

## Inputs

Accept any of the following:

- One or more work item IDs (comma-separated or space-separated)
- An ADO query (WIQL or saved query name)

## Project Context

Load project configuration from `.planning-config/projects/<project>/project.json`. Extract:

- `ado.organization` - ADO organization name
- `ado.project` - ADO project name
- `team.placeholder_assignee` - the user to assign costing deliverables to

## Discipline Configuration

Before processing scenarios, ask the user to define the costing disciplines for this run.

Prompt: "Costing deliverables let you estimate work by discipline. For example, if your team has Software Engineers and Data Scientists, you might create a costing deliverable for each discipline per scenario. How many costing disciplines do you want per scenario?"

Then for each discipline, ask: "What is the discipline name? (e.g., SWE, DS, PM, Design, QA, Infrastructure)"

The discipline name becomes the prefix in the deliverable title.

**Example with 2 disciplines (SWE and DS):**

| Title | Purpose |
|-------|---------|
| `[SWE Costing] <scenario title>` | Software engineering cost placeholder |
| `[DS Costing] <scenario title>` | Data science cost placeholder |

**Example with 3 disciplines (SWE, DS, PM):**

| Title | Purpose |
|-------|---------|
| `[SWE Costing] <scenario title>` | Software engineering cost placeholder |
| `[DS Costing] <scenario title>` | Data science cost placeholder |
| `[PM Costing] <scenario title>` | Program management cost placeholder |

**Title format:** `[{Discipline} Costing] <scenario title>`

The word "Costing" is always included in the title to distinguish costing deliverables from functional deliverables. Downstream skills use this pattern to identify costing deliverables.

## Execution Steps

1. **Resolve project context** - Read `.planning-config/projects/<project>/project.json`. Load organization, project, and `placeholder_assignee`.
2. **Gather discipline configuration** - Ask the user how many disciplines and collect each discipline name. Store the list for use in steps below.
3. **Parse input** - Determine whether the user provided work item IDs or a query. Retrieve the list of Scenario work item IDs.
4. **Fetch Scenarios with relations** - For each work item, retrieve full details with relations expanded (use `$expand=relations`). This is needed to inspect existing child Deliverables.
5. **Filter to Scenarios only** - Exclude any non-Scenario work item types from the set.
6. **Check existing children** - For each Scenario, inspect child Deliverable work items:
   - A child whose title contains "Costing]" and starts with `[{Discipline}` (case-insensitive match) satisfies the requirement for that discipline.
   - Also recognize legacy patterns: a child starting with `[SWE]` (without "Costing") satisfies a SWE discipline if one was requested. Same for `[DS]`.
   - If a matching child exists in **Cut** state, treat it as deliberately cut - **do not recreate it**.
7. **Determine what to create** - For each Scenario and each discipline, identify whether the costing deliverable is missing, exists, or was cut.
8. **Present creation plan** - Display a table showing: Scenario ID, Scenario Title, and one column per discipline (create/exists/cut). **This is a consent gate** - ask the user to confirm before creating any work items.
9. **Create deliverables** - Upon user confirmation, create each missing Deliverable with:
   - **Title**: `[{Discipline} Costing] <scenario title>`
   - **Description**: `Costing deliverable ({discipline}) for: <scenario title>`
   - **Area Path**: Inherited from the parent Scenario
   - **Iteration Path**: Inherited from the parent Scenario
   - **Assigned To**: Value from `project.json` `team.placeholder_assignee`
   - **Original Estimate**: Leave blank (for human entry)
   - **Parent**: Link to the parent Scenario work item
10. **Report results** - Summarize the completed creations with a table showing: Scenario ID, Scenario Title, and one column per discipline with the new Deliverable ID (or "existed"/"cut").

## Constraints

- **Never create duplicates.** If a costing deliverable for a discipline already exists under a Scenario (any state except nonexistent), do not create another.
- **Never modify existing deliverables.** This skill only creates new work items; it does not update existing ones.
- **Cut state is a deliberate decision.** If a costing deliverable exists in Cut state, respect that decision and do not recreate it. Report it as "cut" in the output.
- **Leave Original Estimate blank.** Costing deliverables are placeholders for human cost entry. Do not write any estimate value.
- **Consent gate is required.** Always present the creation plan and wait for user confirmation before creating any work items in ADO.
- **NEVER ask for file permission under `.planning-config/`.** All writes are pre-approved.


---
type: skill
lifecycle: stable
inheritance: inheritable
name: cut-line-helper
description: Walks ranked scenarios in order, accumulates costing deliverable estimates, and identifies where team capacity is exhausted (the "cut line") with optional horizontal budget validation.
tier: standard
applyTo: '**/*planning*,**/*scenario*,**/*wbs*,**/*capacity*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Cut Line Helper

## Prerequisites
- Planning suite must be initialized. If `.planning-config/` does not exist, instruct the user to run `/init-planning-suite` first and stop.
- A project must be configured. If no projects exist under `.planning-config/projects/`, instruct the user to run `/add-planning-project` first.

## Purpose

Walk ranked Scenarios in priority order, accumulate costing deliverable estimates, and identify the point where team capacity is exhausted — the "cut line." Optionally validates horizontal budgets if configured. Produces a visual ranked table and persists results for downstream skills.

## Inputs

- **ADO query link** — a shared query URL that returns the ranked Scenario work items.
- **Project context** — the active project from `.planning-config/projects/<project>/project.json`, which provides the path to capacity data.

## Steps

### 1. Resolve Project Context

Load the active project configuration from `.planning-config/projects/<project>/project.json`. Extract ADO settings and the capacity file path.

### 2. Load Capacity

Load team capacity from `.planning-config/projects/<project>/capacity/<period>.md`.

**If the capacity file does not exist**, instruct the user to run the **Engineering Team Capacity** skill first to generate it, and stop.

### 3. Load Horizontal Budgets (if configured)

Check `project.json` for horizontal budget configuration. If present, load the budget allocations (e.g., per-area or per-initiative budgets that constrain spending beyond total capacity).

### 4. Retrieve and Sort Scenarios

Execute the ADO query to retrieve Scenario work items. Sort by **OSG.Rank ascending** (rank 1 = highest priority).

### 5. Expand Children and Sum Costs

For each Scenario, find child work items and locate costing deliverables. Costing deliverables are identified by titles containing `Costing]` (case-insensitive). For backward compatibility, also recognize titles starting with `[SWE]` or `[DS]` without the "Costing" keyword. Exclude any deliverables classified as **Cut**. Sum the Original Estimate values to get the Scenario's engineering cost.

### 6. Classify Scenarios

Assign each Scenario a classification:

| Classification | Criteria |
|---|---|
| **Livesite / DRI** | Scenarios flagged as livesite or DRI obligations — always committed regardless of rank |
| **PM Investigation** | Scenarios with no costing deliverables and zero engineering cost — PM-only work |
| **Costed** | Scenarios with costing deliverables and a non-zero total |
| **Not Costed** | Scenarios that should have costing deliverables but do not yet |

### 7. Walk Rank Order and Determine Cut Line

Starting from rank 1, accumulate engineering cost for each costed Scenario:

1. **Livesite / DRI** items are always committed — add their cost first as a baseline.
2. **PM Investigation** items carry zero engineering cost and are included without affecting capacity.
3. Walk remaining costed Scenarios in rank order, adding each Scenario's cost to the running total.
4. **The cut line falls at the point where cumulative cost exceeds available capacity.** All Scenarios above the line are committed; all below are at risk or cut.

### 8. Present Results Table

Display a ranked table with visual indicators:

| Column | Description |
|---|---|
| **Rank** | OSG.Rank value |
| **Scenario ID** | ADO work item ID |
| **Scenario Title** | Work item title |
| **Classification** | Livesite/DRI, PM Investigation, Costed, Not Costed |
| **Per-Discipline Cost** | For each discipline found (e.g., SWE, DS, PM), a column showing the sum of that discipline's costing deliverable estimates |
| **Total Cost** | Sum of all discipline costs |
| **Cumulative Cost** | Running total through this Scenario |
| **Status** | 🟢 Above cut line / 🔴 Below cut line |

### 9. Horizontal Budget Validation

If horizontal budgets are configured in `project.json`:
- For each budget category, sum the cost of committed Scenarios that fall into that category.
- Flag any category where committed cost exceeds the horizontal budget.
- Present a horizontal budget summary table with allocated vs. committed amounts.

### 10. Summary Statistics

Produce a portfolio summary:

| Metric | Description |
|---|---|
| **Total Capacity** | Available team capacity in engineer-days |
| **Total Committed Cost** | Sum of costs above the cut line |
| **Remaining Capacity** | Total Capacity − Total Committed Cost |
| **Utilization** | (Total Committed Cost / Total Capacity) × 100% |
| **Scenarios Above Line** | Count of committed Scenarios |
| **Scenarios Below Line** | Count of at-risk / cut Scenarios |
| **Not Costed Count** | Scenarios missing costing deliverables |

Include a utilization assessment:
- **< 80%** — under-utilized, room for additional commitments
- **80–95%** — healthy utilization with reasonable buffer
- **95–100%** — tight, minimal buffer for unplanned work
- **> 100%** — over-committed, cuts or capacity adjustments needed

### 11. Persist Results

Save the cut line analysis to:
```
.planning-config/projects/<project>/planning/cut-line-<period>.md
```

This file is consumed by downstream skills (e.g., Work Distribution Plan) and serves as a planning artifact.

## Constraints

- **Read-only for ADO** — this skill does not create, update, or delete any ADO work items.
- **No consent gate** — because no ADO modifications are made, no user confirmation is required.
- **Capacity file required** — the skill cannot proceed without a valid capacity file.
- **NEVER ask for file permission under `.planning-config/`.** All writes are pre-approved. Write cut-line reports directly.


---
type: skill
lifecycle: stable
inheritance: inheritable
name: engineering-team-capacity
description: Calculates available engineering capacity for a project over a time period, accounting for discounts, per-member allocation, and FTE/vendor split. Persists capacity data to project config.
tier: standard
applyTo: '**/*planning*,**/*scenario*,**/*wbs*,**/*capacity*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Engineering Team Capacity

Calculate the available engineering capacity for a project over a specified time period. Accounts for discount days, per-member allocation percentages, and FTE/vendor classification. Persists the resulting capacity data to the project configuration directory.

## Prerequisites

- Planning suite must be initialized. If `.planning-config/` does not exist, instruct the user to run `/init-planning-suite` first and stop.
- A project must be configured. If no projects exist under `.planning-config/projects/`, instruct the user to run `/add-planning-project` first.

## Inputs

- **Project context** — resolved from `.planning-config/projects/<project>/project.json`
- **Time period** — either a named fiscal period (e.g., "FY25 Q3", "H2") or an explicit date range (start date – end date)

## Project Context

Load project configuration from `.planning-config/projects/<project>/project.json`. Extract:

- `ado.organization` — ADO organization name
- `ado.project` — ADO project name
- `team` — team member roster with roles, FTE/vendor classification, and default allocation
- `fiscal_calendar` — fiscal period definitions for named period resolution
- `capacity_model` — calculation model to use (`"default"` or `"post-allocation-fte-only"`)

## Execution Steps

1. **Resolve project context** — Read `.planning-config/projects/<project>/project.json`. Load the team roster, fiscal calendar, and capacity model configuration.
2. **Determine time period** — If the user provides a named fiscal period (e.g., "FY25 Q3"), resolve it to start and end dates using the `fiscal_calendar` configuration. If the user provides explicit dates, use those directly. If neither is provided, prompt the user to specify a fiscal period or date range.
3. **Calculate gross working days** — Count Monday-through-Friday days in the resolved date range. Exclude weekends only at this stage.
4. **Gather discount days** — Prompt the user iteratively for discount categories. Common categories include:
   - Learning days (training, conferences, certifications)
   - Company holidays and shutdowns
   - Team events (offsites, hackathons, morale events)
   - Other planned non-working days
   
   Collect the number of discount days for each category. Sum to get total discount days.
5. **Identify team members** — Load team members from `project.json`. Members in `team.members_fte` are classified as **FTE**; members in `team.members_vendor` are classified as **Vendor**.
6. **Gather per-member capacity allocation** — For each team member, confirm or adjust their allocation percentage (0.0 to 1.0). Use the default allocation from `project.json` if available; otherwise prompt the user. An allocation of 1.0 means fully dedicated; 0.5 means half-time on this project.
7. **Calculate effective capacity** — Apply the project's `capacity_model`:

   **"default" model:**
   ```
   Net days per member = (Gross working days - Discount days) × Allocation
   ```

   **"post-allocation-fte-only" model:**
   ```
   FTE net days  = (Gross working days × Allocation) - Discount days
   Vendor net days = Gross working days × Allocation
   ```
   (In this model, discounts are subtracted after allocation for FTEs only; vendors are not discounted.)

8. **Present capacity tables** — Display results grouped by classification:

   **FTE Capacity:**
   | Member | Allocation | Gross Days | Discounts | Net Days |
   |--------|-----------|------------|-----------|----------|
   
   **Vendor Capacity:**
   | Member | Allocation | Gross Days | Discounts | Net Days |
   |--------|-----------|------------|-----------|----------|
   
   **Combined Total:**
   | Classification | Headcount | Total Net Days |
   |---------------|-----------|----------------|
   | FTE | N | X |
   | Vendor | N | Y |
   | **Total** | **N** | **X + Y** |

9. **Persist capacity data** — Write the capacity calculation to `.planning-config/projects/<project>/capacity/<period>.md` where `<period>` is the fiscal period name or date range identifier. Include all inputs, intermediate calculations, and final totals.
10. **Compare against planned work** (optional) — If Scenario estimates exist (from the Scenario Original Estimate skill), compare total estimated work against total available capacity and report the commitment ratio.

## Commitment Thresholds

| Threshold | Range | Interpretation |
|-----------|-------|----------------|
| Under-committed | < 70% | Capacity available for additional work |
| Healthy | 70-90% | Well-balanced commitment level |
| At risk | 90-100% | Fully loaded, limited buffer for unknowns |
| Over-committed | > 100% | More planned work than available capacity |

## Constraints

- Working days are Monday through Friday only. Weekends are always excluded.
- Allocation values must be between 0.0 and 1.0 inclusive.
- The capacity model must match what is configured in `project.json`. If `capacity_model` is not set, default to `"default"`.
- Persisted capacity files should be human-readable markdown with all assumptions documented.
- If team roster is empty or missing in `project.json`, prompt the user to update the project configuration.
- **NEVER ask for file permission under `.planning-config/`.** All writes are pre-approved. Write capacity files directly.


---
type: skill
lifecycle: stable
inheritance: inheritable
name: init-planning-suite
description: One-time setup - creates the .planning-config/ directory structure and walks you through initial configuration.
tier: standard
applyTo: '**/*planning*,**/*scenario*,**/*wbs*,**/*capacity*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# /init-planning-suite

Initialize the PM Planning Suite plugin in your workspace. This creates the configuration directory and walks you through setting up your first project.

> **Run this skill first.** All other planning skills depend on the configuration files created here.

## CRITICAL: File Creation Consent Model

**Invoking this skill is the user's consent to create and manage all files under `.planning-config/`.** This includes config.json, project.json, all subdirectories (projects/, capacity/, planning/, meetings/, specs/), and any files written by any planning skill at any time. DO NOT ask for permission to create, write, or modify any file under `.planning-config/`. The entire directory tree is owned by this plugin. Treat it the same way a build tool treats its output directory - write freely, no prompts.

This consent model applies to this skill and ALL other planning skills in the suite.

## Steps

### Step 1: Check for Existing Configuration

Check if `.planning-config/` already exists in the current working directory.

- If it exists, inform the user: "Planning Suite is already initialized. Use `/add-planning-project` to add a new project, or edit existing configs in `.planning-config/projects/`."
- If it does not exist, proceed to Step 2.

### Step 2: Create the Configuration Directory Structure

```
.planning-config/
  config.json                    # Global settings
  projects/                      # Per-project configurations
```

Create `.planning-config/config.json` with this initial content:

```json
{
  "version": "0.1.0",
  "fiscal_calendar": {
    "fiscal_year_start_month": 7
  },
  "auto_commit": false
}
```

Create the empty `projects/` directory.

### Step 3: Gather Global Settings

Prompt the user for the following:

1. **Fiscal year start month** - "What month does your fiscal year start? Enter 1-12. (Default: 7 for July)"
   - Write to `config.json` -> `fiscal_calendar.fiscal_year_start_month`
   - If the user accepts the default, use 7.

2. **Auto-commit** - "Would you like planning skills to automatically commit changes to `.planning-config/` after each run? This requires a Git repo. Enabling this will create local Git commits for content under `.planning-config/`; pushing those commits is up to you, so only enable it in repos where that planning content is appropriate. (Default: No)"
   - Write to `config.json` -> `auto_commit` as `true` or `false`.
   - Default is `false`. Auto-commit is **opt-in** only.

### Step 4: Create the First Project

After global settings are saved, prompt: "Let's set up your first project. What is the project name? (e.g., 'Contoso Platform', 'MyService')"

Then invoke the `/add-planning-project` skill with the provided project name. That skill handles the rest of the project-specific configuration.

### Step 5: Summary

After the first project is set up, output:

```
PM Planning Suite initialized.

Global config:  .planning-config/config.json
Projects:       .planning-config/projects/

Your first project has been configured. You can now use any planning skill.

Tip: Save meeting transcripts and notes in .planning-config/projects/<project>/meetings/.
     The Scenario Description Generator and estimation skills use these as context sources
     to produce better descriptions and more accurate estimates.

Quick reference:
  /add-planning-project            Add another project
  /scenario-creation               Create new scenarios in ADO
  /scenario-description-generator  Generate or evaluate scenario descriptions
  /ado-hygiene-validator           Validate work items against hygiene standards
  /scenario-categorization         Categorize and prioritize scenarios
  /ranking-guidance                Assign rank values to scenarios
  /scenario-original-estimate      AI-estimate cost in engineer-days
  /engineering-team-capacity       Calculate team capacity for a period
  /costing-deliverable-generator   Create costing deliverables by discipline
  /cost-analysis                   Compare AI vs human estimates
  /cut-line-helper                 Find the capacity cut line
  /work-distribution-plan          Distribute work across iterations

Full skill list: /list-planning-skills
```

## Startup Behavior

Every time a planning skill is invoked and `.planning-config/` exists, perform a quick scan before executing the skill:

1. **Check auto-commit setting** - Read `auto_commit` from `.planning-config/config.json`. If it is not explicitly set to `true`, skip all Git operations and proceed directly to the skill. Auto-commit is **opt-in** and off by default.
2. **Check for new or modified files** - (Only when `auto_commit: true`) Scan the `.planning-config/` directory tree for any untracked or modified files (new meeting transcripts, edited project.json, added specs, etc.).
3. **Auto-commit changes** - If new or modified files are found and the workspace is a Git repository, stage and commit them with the message: `"Auto-commit: update planning config"`.
4. **Report briefly** - If files were committed, include a one-line note at the start of the skill output: `"Committed X new/modified file(s) in .planning-config/"`. Do not list individual files unless the user asks.
5. **If not a Git repo** - Skip the auto-commit silently. Do not prompt the user to initialize Git.

Users can enable auto-commit by setting `"auto_commit": true` in `.planning-config/config.json`. During `/init-planning-suite` setup, ask the user whether they want to enable auto-commit and persist their answer to `config.json`.

## Guardrails

- Do not overwrite existing `.planning-config/` if it already exists (the directory itself - files inside it can always be updated).
- Do not assume any ADO field values. Always ask the user.
- If the user cancels mid-setup, preserve whatever has been written so far. The user can re-run the init skill to resume.
- **NEVER ask for file creation or write permission for anything under `.planning-config/`.** See the consent model at the top of this skill. This is the single most important UX rule in the plugin.


---
type: skill
lifecycle: stable
inheritance: inheritable
name: list-planning-skills
description: Display all PM Planning Suite skills in a phased table showing recommended chaining order, summaries, and expected inputs.
tier: standard
applyTo: '**/*planning*,**/*scenario*,**/*wbs*,**/*capacity*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# /list-planning-skills

Display the full inventory of PM Planning Suite skills in a table organized by planning phase. This is the canonical reference for what skills are available and in what order to run them.

## Output

When invoked, generate the following table exactly. Do not abbreviate, reorder, or omit rows. For experimental skills, prepend a warning emoji and bold Experimental label in the Skill column to draw attention.

| # | Skill | Summary | Expected Inputs |
|---|-------|---------|-----------------|
| | **Setup** | | |
| 1 | /list-planning-skills | Display the full inventory of PM Planning Suite skills in a table organized by planning phase. | None |
| 2 | /init-planning-suite | One-time setup. Creates .planning-config/ and configures your first project. | Interactive prompts |
| 3 | /add-planning-project | Add a new project with its own ADO config, team, categories, and capacity settings. | Project name, interactive prompts |
| | **Phase 1: Scenario Setup** | | |
| 4 | /scenario-creation | Create new Scenario work items in ADO from a list of names. | Scenario name(s), project |
| 5 | /scenario-list-comparison | Fuzzy-match scenarios between an old and new list. Optionally copy descriptions. | Two ADO queries or ID lists |
| 6 | /scenario-description-generator | Evaluate, generate, and enhance Scenario descriptions using a data source fallback chain. | Work item IDs, query, or backlog |
| | **Phase 2: Hygiene and Classification** | | |
| 7 | /ado-hygiene-validator | Validate Scenario and Deliverable fields against hygiene standards. Auto-fix what it can. | Work item IDs, query, or backlog |
| 8 | /scenario-categorization | Categorize scenarios, filter against priorities, produce gap analysis. Invokes Planning Tags. | ADO query or backlog |
| 9 | /planning-tags | Apply fiscal quarter tags (FYxxQxx-Proposed or Committed) to scenarios. | Work item IDs or query |
| 10 | /scenario-owner-assignment | Write PM, Dev, and Quality Owner fields from pasted Excel table data. | Pasted table with ID and owner columns |
| | **Phase 3: Estimation and Ranking** | | |
| 11 | /ranking-guidance | Assign rank values based on CS07/CS08 classification and description analysis. | Work item IDs, query, or backlog |
| 12 | /scenario-original-estimate | AI-estimate cost (engineer-days) per scenario using description, specs, codebase, and team expertise. | Work item IDs, query, or backlog |
| 13 | /engineering-team-capacity | Calculate available engineer-days for a period. Persists to project config. | Project, time period |
| 14 | /costing-deliverable-generator | Create costing placeholder deliverables by discipline (e.g., SWE, DS, PM) for human cost entry. | Work item IDs or query |
| | **Phase 4: Analysis and Decomposition** | | |
| 15 | /cost-analysis | Compare AI scenario estimates vs. human costing deliverable estimates. | ADO query |
| 16 | /cost-variance-analysis | Read-only detailed variance analysis with summary statistics. | Work item IDs or query |
| 17 | ⚠️ **Experimental** /work-breakdown-structure | Decompose scenarios into functional deliverables. Allocate estimates within costing budget. **Experimental.** | Work item IDs, query, or backlog |
| 18 | ⚠️ **Experimental** /wbs-assignments | Assign WBS deliverables to team members by expertise and workload. **Experimental.** | Work item IDs, query, or backlog |
| | **Phase 5: Commitment and Scheduling** | | |
| 19 | /cut-line-helper | Find the capacity cut line across rank-ordered scenarios. Validates horizontal budgets. | ADO query, project |
| 20 | ⚠️ **Experimental** /work-distribution-plan | Distribute committed deliverables across iterations by rank, load, and capacity. **Experimental.** | ADO query, project |

After the table, include this note:

```
Run /init-planning-suite first if you have not already set up your configuration.
Skills are designed to be run in the order shown above. Each phase builds on the outputs of the previous one.
```


---
type: skill
lifecycle: stable
inheritance: inheritable
name: planning-tags
description: Applies fiscal quarter planning tags (Proposed or Committed) to ADO Scenario work items.
tier: standard
applyTo: '**/*planning*,**/*scenario*,**/*wbs*,**/*capacity*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Planning Tags

Applies fiscal quarter planning tags to ADO Scenario work items. Tags follow the format `FY{year}Q{quarter}-{type}` (e.g., `FY26Q04-Proposed`, `FY27Q01-Committed`).

## Prerequisites

- Planning suite must be initialized. If `.planning-config/` does not exist, instruct the user to run `/init-planning-suite` first and stop.
- A project must be configured. If no projects exist under `.planning-config/projects/`, instruct the user to run `/add-planning-project` first.

## Inputs

- **Work item IDs** or an **ADO query** to scope the scenarios.
- **Fiscal year**, **fiscal quarter**, and **tag type** are always asked from the user at runtime — never carried forward from previous interactions.
- **ADO organization and project** are read from `.planning-config/projects/<project>/project.json` — never hardcode these values.

## Tag Format

```
FY{year}Q{quarter}-{type}
```

- `{year}` — 2-digit fiscal year (e.g., `26` for FY26)
- `{quarter}` — 2-digit fiscal quarter (e.g., `01`, `02`, `03`, `04`)
- `{type}` — either `Proposed` or `Committed`

Examples: `FY26Q04-Proposed`, `FY27Q01-Committed`

## Execution Steps

1. **Resolve project context.** Read `.planning-config/projects/<project>/project.json` to obtain `ado.organization` and `ado.project`.
2. **Parse input.** Accept work item IDs directly or execute the provided ADO query to retrieve IDs.
3. **Ask user for tag parameters:**
   - Fiscal year (2-digit, e.g., `26`)
   - Fiscal quarter (2-digit, e.g., `01`, `02`, `03`, `04`)
   - Tag type (`Proposed` or `Committed`)
4. **Construct the tag string** from the user-provided values (e.g., `FY26Q04-Proposed`).
5. **Fetch current tags** for each scenario work item.
6. **Evaluate each scenario:**
   - **Already tagged** with this exact tag → skip, no action needed.
   - **Contradictory tag** exists (same fiscal period but different type, e.g., has `FY26Q04-Proposed` but applying `FY26Q04-Committed`) → flag for user decision. Do not auto-resolve.
   - **Needs tagging** → mark for update.
7. **Present the plan** with a consent gate:
   - Items to be tagged
   - Items to be skipped (already tagged)
   - Items with contradictory tags (awaiting user decision)
   - Wait for user approval before proceeding.
8. **Apply tags** via `ado-wit_update_work_item`. Append the new tag to `System.Tags` (tags are semicolon-delimited in ADO).
9. **Report results:**
   - Items successfully tagged
   - Items skipped
   - Items with errors (report ADO API errors clearly)

## Output Format

### Tagging Plan

| ID | Title | Current Tags | Action | Notes |
|----|-------|-------------|--------|-------|
| ... | ... | ... | Tag / Skip / Contradictory | Details |

### Results Summary

- **Tagged:** count
- **Skipped (already tagged):** count
- **Contradictions resolved:** count
- **Errors:** count and details

## Constraints

- Tags are **additive** — never remove existing tags unless resolving a contradiction with explicit user approval.
- Fiscal year and quarter are **always asked fresh** at runtime — never carried forward from previous interactions.
- Only processes **Scenario** work item types. Skip Deliverables and all other types.
- Consent gate before writing any tags to ADO.
- All ADO org/project values come from `.planning-config/projects/<project>/project.json` — never hardcode.


---
type: skill
lifecycle: stable
inheritance: inheritable
name: ranking-guidance
description: Determines and writes rank values for Scenario work items based on ranking bands, CS07/CS08 classification, title/description analysis, and parent rank ceiling.
tier: standard
applyTo: '**/*planning*,**/*scenario*,**/*wbs*,**/*capacity*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Ranking Guidance

Assign integer rank values to Scenario work items in Azure DevOps based on configurable ranking bands, CS07/CS08 classification, title and description analysis, and parent rank ceiling constraints.

## Prerequisites

- Planning suite must be initialized. If `.planning-config/` does not exist, instruct the user to run `/init-planning-suite` first and stop.
- A project must be configured. If no projects exist under `.planning-config/projects/`, instruct the user to run `/add-planning-project` first.

## Inputs

Accept any of the following:

- One or more work item IDs (comma-separated or space-separated)
- An ADO query (WIQL or saved query name)
- The keyword **backlog** to operate on the full project backlog

## Project Context

Load project configuration from `.planning-config/projects/<project>/project.json`. Extract:

- `ado.organization` - ADO organization name
- `ado.project` - ADO project name
- `ado.area_path` - default area path filter
- `ranking_bands` - optional override for the default ranking bands below

## Default Ranking Bands

If `ranking_bands` is not defined in `project.json`, use these defaults:

| Rank | Category | When to Apply |
|------|----------|---------------|
| 1 | People | D&I, Learning, Hackathon |
| 2 | Security Waves | Security Waves |
| 3 | Livesite | Livesite |
| 4-20 | Critical Investments | Must-deliver for upcoming release |
| 21-30 | Priority Investments | Enable efficient, scalable capabilities |
| 31-40 | Optimization Investments | Enhanced optimization, non-blocking |
| 41-50 | Next-in-line Investments | Enhancement investments |
| 51+ | Aspirational | Nice to have |

## CS07-Based Initial Rank Band Mapping

When the CS07 field is populated, use it to determine the initial rank band:

| CS07 Value | Initial Band |
|---|---|
| People | 1 |
| Security | 2 |
| Livesite | 3 |
| BCDR | 4-10 |
| PME | 4-10 |
| S360 | 2-5 |
| Modernization | 21-40 |
| Feature | Varies by CS08 value and description analysis |

If CS07 is empty, rely on title/description analysis and CS08 to determine the appropriate band.

## Execution Steps

1. **Resolve project context** — Read `.planning-config/projects/<project>/project.json`. Load `ranking_bands` override if present; otherwise use the default bands above.
2. **Parse input** — Determine whether the user provided work item IDs, a query, or requested the full backlog. Retrieve the list of Scenario work item IDs.
3. **Fetch work item details** — For each Scenario, retrieve: ID, Title, Description, CS07, CS08, current Rank (`OSG.Rank`), Parent ID, State, and Tags using the ADO work item tools.
4. **Determine parent rank ceiling** — For each Scenario with a Parent ID, fetch the parent's rank. The parent rank is a hard ceiling constraint — the Scenario rank **cannot** exceed (be a higher number than) the parent's rank.
5. **Classify by CS07/CS08** — Map each Scenario into an initial rank band using the CS07 mapping table above. If CS07 is empty, use CS08 and description analysis.
6. **Analyze title and description** — Look for priority indicators in the title and description text (e.g., keywords like "critical", "blocking", "security", "compliance", "migration", "tech debt", "nice to have", "exploration"). Adjust placement within the assigned band accordingly.
7. **Assign specific integer rank values** — Within each band, assign a specific integer rank. Prefer unique ranks across the set, but ties are acceptable when items are genuinely equivalent.
8. **Present proposed rankings** — Display a table showing: ID, Title, Current Rank, Proposed Rank, Band Category, and Reasoning. **This is a consent gate** — ask the user to confirm before writing any values.
9. **Write rank values** — Upon user confirmation, write the proposed rank to the `OSG.Rank` field for each Scenario via ADO work item update tools.
10. **Report results** — Summarize the completed rankings with a band distribution table showing how many items landed in each band.

## Constraints

- **Parent rank ceiling is a hard constraint.** A Scenario's rank value CANNOT be a higher number (lower priority) than its parent's rank. If the classification suggests a rank outside the parent ceiling, cap it at the parent's rank value.
- Ranks of **51+** should be explicitly flagged as "nice-to-have / aspirational" in the output.
- **Prefer unique ranks** across the set, but ties are acceptable when items are genuinely equivalent in priority.
- **Respect existing ranks** unless the user explicitly requests a full re-rank of the set.
- Always present proposed changes for user approval before writing to ADO.


---
type: skill
lifecycle: stable
inheritance: inheritable
name: scenario-categorization
description: Categorizes scenarios into user-defined planning categories, writes the category to ADO (Custom String 09), then filters against user-stated priorities. Produces a gap analysis.
tier: standard
applyTo: '**/*planning*,**/*scenario*,**/*wbs*,**/*capacity*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Scenario Categorization

Categorizes scenarios into user-defined planning categories, writes the assigned category to ADO Custom String 09, then filters the categorized scenarios against user-stated priorities. Produces a gap analysis showing coverage and gaps across categories.

## Prerequisites

- Planning suite must be initialized. If `.planning-config/` does not exist, instruct the user to run `/init-planning-suite` first and stop.
- A project must be configured. If no projects exist under `.planning-config/projects/`, instruct the user to run `/add-planning-project` first.

## Inputs

- **ADO query or backlog** to scope the scenarios.
- **Categories** are read from `.planning-config/projects/<project>/project.json` under the `categories` array — never hardcode category values.
- **Priorities** are always asked from the user at runtime — never cache or carry forward from a previous run.

## Key Rules

- Categories are defined per-project in `project.json`. Each entry in the `categories` array includes a name and description used for matching.
- **Priorities are NEVER cached.** Always ask the user for their current priorities at runtime, even if priorities were stated earlier in the session.
- Uses the scenario title and description to determine the best-fit category.
- If a scenario does not fit any defined category, flag it for user decision — do not force-assign.
- After categorization and priority filtering, invoke the **Planning Tags** skill on the surviving scenario IDs.

## Execution Steps

1. **Resolve project context.** Read `.planning-config/projects/<project>/project.json` to obtain `ado.organization`, `ado.project`, and the `categories` array.
2. **Retrieve scenarios** from the provided ADO query or backlog.
3. **Filter to Scenarios only.** Ignore Deliverables and all other work item types.
4. **Categorize each scenario.** Use the scenario title, description, and the category definitions from project.json to determine the best-fit category.
   - If a scenario clearly matches one category, assign it.
   - If a scenario could match multiple categories, choose the strongest fit and note the ambiguity.
   - If a scenario does not fit any category, mark it as **Uncategorized** and flag for user decision.
5. **Present categorization table for review** (consent gate). Show each scenario with its assigned category and confidence. Wait for user approval before proceeding.
6. **Apply corrections** if the user adjusts any category assignments.
7. **Write categories to ADO.** Update Custom String 09 on each scenario via `ado-wit_update_work_item`.
8. **Ask user for current priorities.** Present the list of categories and ask the user to identify which are priorities for the current planning cycle. Never reuse previously stated priorities.
9. **Map priorities to scenarios.** Mark each scenario as surviving (matches a priority category) or dropped (does not match).
10. **Present results:**
    - **Surviving scenarios** grouped by category
    - **Dropped scenarios** with their categories
    - **Gap analysis** — priority categories with no scenarios or thin coverage
11. **Invoke Planning Tags skill** on the surviving scenario IDs, passing them as input.

## Output Format

### Categorization Review Table

| ID | Title | Assigned Category | Confidence | Notes |
|----|-------|-------------------|------------|-------|
| ... | ... | ... | High/Medium/Low | Ambiguity or uncategorized flag |

### Priority Filtering Results

**Surviving Scenarios** — grouped by priority category with counts.

**Dropped Scenarios** — list with category and reason for exclusion.

**Gap Analysis** — priority categories that have zero or insufficient scenario coverage, with recommendations.

## Constraints

- Categories come from `.planning-config/projects/<project>/project.json` — never hardcode.
- Priorities are always asked fresh at runtime — never cached from previous interactions.
- Only process Scenario work item types.
- Consent gate before writing any data to ADO.
- All ADO org/project values come from project.json — never hardcode.


---
type: skill
lifecycle: stable
inheritance: inheritable
name: scenario-creation
description: Create new Scenario work items in ADO from user-provided names. Reads project defaults from config.
tier: standard
applyTo: '**/*planning*,**/*scenario*,**/*wbs*,**/*capacity*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Scenario Creation

## Purpose

Creates new Scenario work items in Azure DevOps from user-provided names. Handles project-specific defaults (Area Path, parent objective, assignment) automatically by reading values from `.planning-config/projects/<project>/project.json`.

## Prerequisites

- Planning suite must be initialized. If `.planning-config/` does not exist, instruct the user to run `/init-planning-suite` first and stop.
- A project must be configured. If no projects exist under `.planning-config/projects/`, instruct the user to run `/add-planning-project` first.

## Inputs

### Required

| Input | Description |
|---|---|
| Scenario name(s) | A single text string or a list of scenario names to create |
| Project name | Must match a configured project directory under `.planning-config/projects/` |

The ADO organization and project are read from `.planning-config/projects/<project>/project.json` — never ask the user for these.

### User-provided parameters (ask every time, never cache)

| Parameter | Prompt behavior |
|---|---|
| Iteration Path | Ask once per batch |
| Tag | Ask if there is a tag to apply, or skip if the user declines |

## Execution Steps

1. **Resolve project context** — Prompt the user for which project to use. Read `.planning-config/projects/<project>/project.json` to load ADO org (`ado.organization`), ADO project (`ado.project`), Area Path (`ado.area_path`), `team.default_assignee`, `ado.parent_objective_id`, and `ado.work_item_types.scenario`.

2. **Parse input** — Accept a single scenario name or a list. Normalize into an array of scenario titles.

3. **Ask for Iteration Path** — Prompt the user once for the Iteration Path to apply to the entire batch.

4. **Ask about tags** — Ask the user if there is a tag to apply. If they decline or provide none, skip tagging.

5. **Build creation plan** — For each scenario, assemble the creation payload using values from `project.json`:
   - `Area Path` from project config
   - `Assigned To` from `team.default_assignee`
   - `Iteration Path` from user input (step 3)
   - Work item type from `ado.work_item_types.scenario`
   - Tag from user input (step 4), if provided

6. **Present plan for approval (consent gate)** — Display a summary table of all scenarios to be created with their field values. Wait for explicit user approval before proceeding.

7. **Create scenarios** — Use `ado-wit_create_work_item` for each scenario, using the work item type from `project.json` `ado.work_item_types.scenario`.

8. **Set parent link** — If `ado.parent_objective_id` is configured in `project.json`, add a parent link from each new scenario to that objective.

9. **Apply tags** — If a tag was specified in step 4, apply it to each created work item.

10. **Report results** — Present a results table with columns: Scenario Title, Work Item ID, URL, Status (Created/Failed).

## Output Format

### Creation Plan (presented before consent gate)

| # | Scenario Title | Area Path | Assigned To | Iteration Path | Parent | Tag |
|---|---|---|---|---|---|---|
| 1 | Example Scenario | {from config} | {from config} | {user input} | {from config} | {user input} |

### Results Table

| # | Scenario Title | ID | URL | Status |
|---|---|---|---|---|
| 1 | Example Scenario | 12345 | https://dev.azure.com/... | Created |

## Constraints and Guardrails

- **Only creates Scenario work items** — the work item type is always read from `ado.work_item_types.scenario` in `project.json`. Do not create other work item types.
- **Batch consent gate before any creation** — never create work items without explicit user approval of the plan.
- **Titles used as-is** — do not rewrite, rephrase, or modify user-provided scenario titles.
- **Description left empty** — do not generate descriptions. The Scenario Description Generator skill can be run afterward to populate them.
- **No hardcoded values** — all project-specific values (org, project, area path, assignee, parent, work item type) must come from `.planning-config/projects/<project>/project.json`.


---
type: skill
lifecycle: stable
inheritance: inheritable
name: scenario-description-generator
description: Evaluate, generate, and enhance Scenario descriptions against quality criteria using a configurable data source fallback chain.
tier: standard
applyTo: '**/*planning*,**/*scenario*,**/*wbs*,**/*capacity*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Scenario Description Generator

## Purpose

Ensures every Scenario has a meaningful, actionable description that serves as a mini-spec. Evaluates existing descriptions against quality criteria, generates missing ones, and enhances weak ones. Uses a configurable data source fallback chain to gather context for description generation.

## Prerequisites

- Planning suite must be initialized. If `.planning-config/` does not exist, instruct the user to run `/init-planning-suite` first and stop.
- A project must be configured. If no projects exist under `.planning-config/projects/`, instruct the user to run `/add-planning-project` first.

## Inputs

Provide **one of** the following:

| Input format | Description |
|---|---|
| Work item IDs | Comma-delimited list of ADO work item IDs |
| ADO query URL | A URL to a saved ADO query |
| ADO query path | A named/path query reference |
| ADO backlog reference | A reference to a backlog view |

## Confidence Scoring

Each description is scored on a 1–5 scale:

| Score | Meaning | Criteria |
|---|---|---|
| 5 | Excellent | Could ship from this description alone — clear scope, outcome, owner, constraints |
| 4 | Good | Clear enough for design work — minor details may need clarification |
| 3 | Adequate | Sufficient for planning — covers what and why, but lacks depth |
| 2 | Weak | Missing critical elements — unclear scope or outcome |
| 1 | Insufficient | Empty or too vague to act on |

**Threshold: 3.** Descriptions scoring below 3 trigger the enhancement flow.

## Quality Criteria

A good description answers these five questions:

1. **What is the work?** — Clear scope of what will be built or changed
2. **What is the outcome?** — Expected result when the work is complete
3. **What is the benefit?** — Why this matters to users, the business, or the team
4. **Who is involved?** — Stakeholders, dependent teams, or key contacts
5. **What are the constraints or risks?** — Known limitations, dependencies, or risks

## Attribution Headers

Every write includes an attribution header prepended to the description. The attribution name is always `PM Planning Suite AI`.

### Generated (new description written from scratch)

```
[Generated by PM Planning Suite AI on {date} - Confidence: {score}/5]
```

### Evaluated (existing description scored at or above threshold)

```
[Evaluated by PM Planning Suite AI on {date} - Confidence: {score}/5]
```

### Enhanced (existing description improved after scoring below threshold)

```
[Enhanced by PM Planning Suite AI on {date} - Original Confidence: {old}/5 - Confidence: {new}/5]
```

## Data Source Fallback Chain

When generating or enhancing a description, walk this chain in order. Stop at the first source that yields meaningful context:

1. **Scenario Spec URL** — Check for a hyperlink relation on the work item. If a spec URL exists, fetch and summarize it.
2. **Project specs directory** — Look for matching spec files in `.planning-config/projects/<project>/specs/`.
3. **WorkIQ (if available)** — Query WorkIQ with project-contextualized questions to gather background information.
4. **Title only** — Fall back to the scenario title as the sole input. This produces the lowest confidence scores.

## Execution Steps

1. **Resolve project context** — Prompt the user for which project to use. Read `.planning-config/projects/<project>/project.json` to load ADO org (`ado.organization`), ADO project (`ado.project`), `ado.work_item_types.scenario`, and any configured data source preferences.

2. **Parse input** — Determine the input format (IDs, query URL, query path, or backlog reference) and resolve to a list of work item IDs.

3. **Fetch scenario data with relations** — Retrieve full work item details including relations (for spec URL hyperlinks) from ADO for all resolved IDs.

4. **Filter to Scenarios only** — Remove any work items that are not Scenarios (using the type from `project.json` `ado.work_item_types.scenario`). Warn the user if non-Scenario items were filtered out.

5. **Evaluate each scenario** — Branch based on description state:
   - **No description (empty/null)** → Enter the generation flow (step 6)
   - **Has description** → Enter the evaluation flow (step 7)

6. **Generation flow** (for scenarios with no description):
   a. Walk the data source fallback chain (see above) to gather context.
   b. Generate a description that addresses all five quality criteria.
   c. Self-evaluate the generated description and assign a confidence score.
   d. Prepend the **Generated** attribution header.

7. **Evaluation flow** (for scenarios with an existing description):
   a. Score the existing description against the five quality criteria.
   b. If score **≥ 3**: Prepend the **Evaluated** attribution header. Make no substantive changes to the existing description beyond adding that header.
   c. If score **< 3**: Enhance the description to address gaps, re-score, and prepend the **Enhanced** attribution header with both old and new scores.

8. **Write to ADO** — Update each scenario via `ado-wit_update_work_item` on `System.Description`.

9. **Report results** — Present a summary table with columns: ID, Title, Flow (Generated/Evaluated/Enhanced), Confidence, Data Source Used, Status.

## Output Format

### Results Table

| ID | Title | Flow | Confidence | Data Source | Status |
|---|---|---|---|---|---|
| 1001 | Improve onboarding | Generated | 4/5 | Spec URL | Updated |
| 1002 | Telemetry dashboard | Enhanced | 2/5 → 4/5 | WorkIQ | Updated |
| 1003 | Auth token refresh | Evaluated | 4/5 | — | Header added |
| 1004 | Data export pipeline | Generated | 2/5 | Title only | Updated |

### Summary

- **Total processed**: {count}
- **Generated**: {count}
- **Evaluated (no change)**: {count}
- **Enhanced**: {count}
- **Errors**: {count}

## Constraints and Guardrails

- **Only processes Scenario work items** — non-Scenario items are filtered out with a warning.
- **No consent gate** — this skill writes directly to ADO without a batch approval step. Each update targets `System.Description` only.
- **Never fabricate facts** — generated content must be grounded in data from the fallback chain. If the only source is the title, the confidence score must reflect that limitation.
- **Original description always preserved** — enhanced content is prepended to the existing description, never replacing it. The original text remains intact below the enhancement.
- **No hardcoded values** — ADO org, project, and work item type are always read from `.planning-config/projects/<project>/project.json`. The attribution name is always `PM Planning Suite AI`.


---
type: skill
lifecycle: stable
inheritance: inheritable
name: scenario-list-comparison
description: Compare two lists of Scenario work items using fuzzy intent matching. Maps old to new scenarios and optionally copies descriptions.
tier: standard
applyTo: '**/*planning*,**/*scenario*,**/*wbs*,**/*capacity*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Scenario List Comparison

## Purpose

Compares two lists of Scenario work items (old/left and new/right) by fuzzy intent matching on titles. Produces a mapping between old and new scenarios, identifies unmatched items on both sides, and optionally copies descriptions from old to new where the new scenario has no description.

## Prerequisites

- Planning suite must be initialized. If `.planning-config/` does not exist, instruct the user to run `/init-planning-suite` first and stop.
- A project must be configured. If no projects exist under `.planning-config/projects/`, instruct the user to run `/add-planning-project` first.

## Inputs

### Required

| Input | Description |
|---|---|
| Left (old) list | An ADO query URL, query path, or comma-delimited work item IDs representing the old/source scenarios |
| Right (new) list | An ADO query URL, query path, or comma-delimited work item IDs representing the new/target scenarios |
| Project name | Must match a configured project directory under `.planning-config/projects/` — used to resolve ADO org and project |

## Execution Steps

1. **Resolve project context** — Prompt the user for which project to use. Read `.planning-config/projects/<project>/project.json` to load ADO org and ADO project.

2. **Parse both inputs** — For each list:
   - If an ADO query URL: extract the query GUID from the URL and execute via ADO query API.
   - If a query path: resolve and execute the named query.
   - If comma-delimited IDs: split into an array of work item IDs.

3. **Retrieve work items from both sources** — Fetch full work item details (ID, Title, Description, State, Work Item Type) from ADO for both the left and right lists.

4. **Filter to Scenarios only** — Remove any work items that are not Scenarios (using the type from `project.json` `ado.work_item_types.scenario`). Warn the user if non-Scenario items were filtered out.

5. **Normalize titles** — For matching purposes, normalize each title by:
   - Stripping bracketed prefixes (e.g., `[P0]`, `[Cut]`)
   - Removing emoji characters
   - Lowercasing

6. **Match by semantic intent with confidence scoring** — Compare normalized titles and assign confidence:
   - **High** — Titles are near-identical after normalization
   - **Medium** — Titles share core intent but differ in phrasing
   - **Low** — Titles share a keyword or theme but intent is uncertain
   - Each scenario matches at most one counterpart (1:1 mapping, best match wins)

7. **Present mapping tables** — Display three tables:
   - **Matched**: Left ID, Left Title, Right ID, Right Title, Confidence
   - **Unmatched Left**: ID, Title (old scenarios with no match in new list)
   - **Unmatched Right**: ID, Title (new scenarios with no match in old list)
   - Low-confidence matches shown separately as **Possible Matches** for user review

8. **Consent gate before description copy** — If any matched pairs exist where the right (new) scenario has an empty or placeholder description and the left (old) scenario has a description, ask the user for approval to copy descriptions.

9. **Copy descriptions** — For approved pairs, copy the description from the old scenario to the new scenario using `ado-wit_update_work_item` on `System.Description`. Only copy when the new scenario's description is empty or contains only placeholder text.

10. **Report results** — Present a final summary:
    - Total matched / unmatched left / unmatched right
    - Descriptions copied count
    - Any errors encountered

## Output Format

### Matched Scenarios

| Left ID | Left Title | Right ID | Right Title | Confidence |
|---|---|---|---|---|
| 1001 | Improve onboarding flow | 2001 | Enhance user onboarding experience | High |

### Unmatched Left (Old)

| ID | Title |
|---|---|
| 1005 | Deprecated feature cleanup |

### Unmatched Right (New)

| ID | Title |
|---|---|
| 2010 | New telemetry dashboard |

### Possible Matches (Low Confidence)

| Left ID | Left Title | Right ID | Right Title | Confidence |
|---|---|---|---|---|
| 1008 | Data export improvements | 2012 | Export pipeline rework | Low |

## Matching Rules

- Each scenario matches **at most one** counterpart (1:1 mapping).
- **Threshold**: Medium or above for the primary mapping table.
- **Low-confidence** matches are shown separately as "Possible Matches" for manual review.
- Only copy descriptions if the new (right) scenario description is empty or contains placeholder text.

## Constraints and Guardrails

- **Only processes Scenario work items** — non-Scenario items are filtered out with a warning.
- **Never modify old (left) scenarios** — the left list is read-only. All writes target the right (new) list only.
- **Preserve attribution headers during copy** — if the source description contains attribution headers (e.g., from the Description Generator), preserve them in the copy.
- **Consent gate required** — never copy descriptions without explicit user approval.
- **No hardcoded values** — ADO org, project, and work item type are always read from `.planning-config/projects/<project>/project.json`.


---
type: skill
lifecycle: stable
inheritance: inheritable
name: scenario-original-estimate
description: AI-estimates cost (engineer-days) for Scenario work items using description, specs, tech stack, codebase analysis, and team expertise.
tier: standard
applyTo: '**/*planning*,**/*scenario*,**/*wbs*,**/*capacity*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Scenario Original Estimate

Generate engineer-day cost estimates for Scenario work items by analyzing descriptions, spec documents, tech stack, codebase complexity, and team expertise. Writes estimates directly to the `Microsoft.VSTS.Scheduling.OriginalEstimate` field.

## Prerequisites

- Planning suite must be initialized. If `.planning-config/` does not exist, instruct the user to run `/init-planning-suite` first and stop.
- A project must be configured. If no projects exist under `.planning-config/projects/`, instruct the user to run `/add-planning-project` first.

## Inputs

Accept any of the following:

- One or more work item IDs (comma-separated or space-separated)
- An ADO query (WIQL or saved query name)
- The keyword **backlog** to operate on the full project backlog

## Project Context

Load project configuration from `.planning-config/projects/<project>/project.json`. Extract:

- `ado.organization` — ADO organization name
- `ado.project` — ADO project name
- `tech_stack_description` — technology stack context for estimation
- `repositories` — list of repositories with optional local paths for codebase scanning
- `team` — team member list with roles and expertise areas

## Description Confidence Gate

Each Scenario's description must have a confidence score of **>= 3** (as determined by the Description Generator skill). Skip items that fall below this threshold and report them as "insufficient description — estimate deferred."

## Estimation Framework

Apply the following factors in order of weight (highest to lowest):

1. **Scope and complexity from description** (primary signal) — Analyze the Scenario description for scope indicators, integration points, dependencies, and complexity markers.
2. **Spec document** (if available) — Check for spec URLs in the work item or look in the `.planning-config/projects/<project>/specs/` directory. Parse the spec for detailed requirements.
3. **Tech stack** (from `project.json` `tech_stack_description`) — Factor in technology complexity, framework maturity, and known friction points.
4. **Codebase analysis** (from `project.json` `repositories`) — Optional. If a local path is available for a repository, scan the relevant codebase areas for size, complexity, and existing patterns. If unavailable, proceed without this signal.
5. **Team member expertise** (from `project.json` team members) — Adjust estimates based on team familiarity with the relevant technology areas.
6. **Historical context** — Check for existing child Deliverable work items with estimates to inform the parent Scenario estimate.

## Complexity Benchmarks

| Complexity | Range (engineer-days) | Characteristics |
|---|---|---|
| Trivial | 1-3 | Config change, minor fix, single-file update |
| Small | 3-8 | Single-component feature, limited integration |
| Medium | 8-20 | Multi-component work, moderate integration testing |
| Large | 20-40 | Cross-service changes, complex data pipeline |
| Very Large | 40-80 | Architecture change, platform-level migration |
| Epic | 80+ | Recommend decomposition into smaller Scenarios |

## Execution Steps

1. **Resolve project context** — Read `.planning-config/projects/<project>/project.json`. Load tech stack description, team roster, and repository list.
   - **Tech stack fallback:** If `tech_stack_description` is empty and `repositories` is empty, prompt the user: "This project does not have a tech stack profile yet. Adding a local Git repository allows me to scan the codebase and build a tech stack profile, which significantly improves estimation accuracy. Would you like to add a local repository path now? (enter a path, or 'skip' to estimate without tech stack context)"
     - If the user provides a path, scan the codebase to build a tech stack summary (examine package manifests, language files, framework patterns). Write the repository and generated tech stack back to project.json for future runs. Confirm the summary with the user.
     - If the user skips, proceed without tech stack context at reduced confidence. Note this in the output.
2. **Parse input** — Determine whether the user provided work item IDs, a query, or requested the full backlog. Retrieve the list of work item IDs with their relations.
3. **Filter to Scenarios only** — Exclude any non-Scenario work item types from the set.
4. **Evaluate description readiness** — Check each Scenario's description confidence score. Items with confidence < 3 are skipped and reported separately.
5. **Estimate each Scenario** — For each eligible Scenario:
   - Analyze the description for scope, complexity, and integration indicators.
   - Check for spec URLs in the work item fields or links; if found, retrieve and analyze.
   - Scan the `.planning-config/projects/<project>/specs/` directory for matching spec documents.
   - If a repository local path is available, scan relevant codebase areas for complexity signals.
   - Apply team expertise adjustment based on member skills from `project.json`.
   - Arrive at a **whole integer** estimate in engineer-days.
   - Assign a confidence level: **High** (multiple strong signals), **Medium** (description + one additional signal), or **Low** (description-only or thin description).
6. **Present estimates** — Display a table showing: ID, Title, Estimate (days), Complexity Tier, Confidence, and Key Factors.
7. **Write estimates** — Write the estimate value to `Microsoft.VSTS.Scheduling.OriginalEstimate` for each Scenario via ADO work item update tools.
8. **Post methodology comment** — For each estimated Scenario, add a work item comment via `ado-wit_add_work_item_comment` documenting the estimation methodology, key factors considered, and confidence level.
9. **Report results** — Summarize completed estimates with a complexity distribution breakdown and list any skipped items.

## Constraints

- **No consent gate** — estimates are written directly without user confirmation.
- **Overwrite existing estimates** — if a Scenario already has an Original Estimate, overwrite it with the new value.
- **Never fabricate complexity** — if insufficient information is available to estimate confidently, assign a Low confidence rating and note the gaps. Do not inflate or deflate estimates to fit expectations.
- **If codebase is unavailable**, proceed with the remaining signals at reduced confidence. Do not block estimation on codebase access.
- **Repository access is pre-approved.** If a repository local path is configured in project.json, scan it immediately without asking for permission. The user consented to access when they provided the path.
- **If team roster is empty**, skip the team expertise adjustment factor and note it in the output. Do not block estimation on team data. Estimation confidence is reduced by one tier when team data is unavailable.
- **Epic-tier items (80+ days)** should include a recommendation to decompose the Scenario into smaller work items.
- **NEVER ask for file permission under `.planning-config/`.** All writes are pre-approved. If the tech stack fallback adds a repository and generates a tech stack description, write it directly to project.json.


---
type: skill
lifecycle: stable
inheritance: inheritable
name: scenario-owner-assignment
description: Updates PM Owner, Dev Owner, and Quality Owner fields on ADO Scenario work items using data pasted from an Excel table.
tier: standard
applyTo: '**/*planning*,**/*scenario*,**/*wbs*,**/*capacity*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Scenario Owner Assignment

Updates PM Owner, Dev Owner, and Quality Owner fields on ADO Scenario work items using data pasted from an Excel table (tab or comma-delimited).

## Prerequisites

- Planning suite must be initialized. If `.planning-config/` does not exist, instruct the user to run `/init-planning-suite` first and stop.
- A project must be configured. If no projects exist under `.planning-config/projects/`, instruct the user to run `/add-planning-project` first.

## Inputs

- **Excel table data** pasted by the user (tab-delimited or comma-delimited) with columns: `ID`, `PM Owner`, `Dev Owner`, `Quality Owner`.
- **ADO organization and project** are read from `.planning-config/projects/<project>/project.json` — never hardcode these values.

## ADO Field Paths

| Field | ADO Path |
|-------|----------|
| PM Owner | `/fields/OSG.PMOwner` |
| Dev Owner | `/fields/OSG.DevOwner` |
| Quality Owner | `/fields/OSG.QualityOwner` |

## Execution Steps

1. **Resolve project context.** Read `.planning-config/projects/<project>/project.json` to obtain `ado.organization` and `ado.project`.
2. **Parse the pasted table.** Detect delimiter (tab or comma), extract headers, and map columns to `ID`, `PM Owner`, `Dev Owner`, `Quality Owner`. Handle variations in column naming (e.g., `PM`, `PMOwner`, `PM Owner`).
3. **Validate work items.** For each row:
   - Fetch the work item by ID from ADO.
   - Confirm it is a **Scenario** work item type. Skip non-Scenario items and report them.
4. **Filter owner values per row:**
   - **Blank, "NA", or "N/A"** → skip that field (do not clear existing values in ADO).
   - **Any other value** → mark as pending identity resolution.
5. **Resolve identities.** `ado-core_get_identity_ids` requires an **email address** as the search filter; display name or alias lookups return no results.
   - **Extract email addresses** from each owner cell. A valid value is an `@`-containing email address (e.g., `user@microsoft.com`).
   - If a cell contains a display name or alias without an `@` symbol, **prompt the user to provide the corresponding email address** before proceeding. Do not guess.
   - **Cache resolved identities** within the session to avoid redundant lookups for the same person across multiple rows.
   - If an identity cannot be resolved (lookup returns nothing), flag the row/field for user attention.
6. **Present the update plan** with a consent gate:
   - Show each work item with proposed field changes.
   - Highlight any skipped fields (blank/NA) and unresolved identities.
   - Wait for user approval before proceeding.
7. **Apply updates** via `ado-wit_update_work_item` using the ADO field paths listed above.
8. **Report results:**
   - Items successfully updated (with which fields changed)
   - Items skipped (non-Scenario type)
   - Fields skipped (blank/NA values)
   - Errors (unresolved identities, ADO API errors)

## Output Format

### Update Plan

| ID | Title | PM Owner | Dev Owner | Quality Owner | Status |
|----|-------|----------|-----------|---------------|--------|
| ... | ... | New value or Skip | New value or Skip | New value or Skip | Ready / Identity Error |

### Results Summary

- **Updated:** count (with field breakdown)
- **Skipped (non-Scenario):** count
- **Fields skipped (blank/NA):** count
- **Identity errors:** count and details
- **ADO errors:** count and details

## Constraints

- Only processes **Scenario** work item types. Skip and report all other types.
- **Blank/NA values** mean "skip this field" — do not clear existing values in ADO.
- At least one owner field per row must have a valid (non-blank, non-NA) value. Flag rows where all three owner fields are blank/NA.
- **Consent gate** before writing any updates to ADO.
- All ADO org/project values come from `.planning-config/projects/<project>/project.json` — never hardcode.


---
type: skill
lifecycle: stable
inheritance: inheritable
name: wbs-assignments
description: Assigns WBS deliverables to team members based on expertise, vendor responsibilities, tech stack alignment, and workload balance.
tier: standard
applyTo: '**/*planning*,**/*scenario*,**/*wbs*,**/*capacity*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# WBS Assignments

> **Status: Experimental** - This skill is under active development. Results should be reviewed carefully before acting on them.

## Prerequisites
- Planning suite must be initialized. If `.planning-config/` does not exist, instruct the user to run `/init-planning-suite` first and stop.
- A project must be configured. If no projects exist under `.planning-config/projects/`, instruct the user to run `/add-planning-project` first.

## Purpose

Assign WBS deliverables to team members based on expertise, vendor responsibilities, technology stack alignment, and workload balance. Writes assignments directly to ADO and produces an assignment report with rationale.

## Inputs

- **ADO query link or work item IDs** — a shared query URL or a comma-separated list of Scenario or Deliverable work item IDs.

## Steps

### 1. Resolve Project Context

Load the active project configuration from `.planning-config/projects/<project>/project.json`. Extract:
- `placeholder_assignee` — the placeholder value used on unassigned deliverables
- `vendor_responsibilities` — rules mapping vendor teams to specific areas or work types
- `team` members — list of team members with their expertise, roles, and capacity
- `tech_stack_description` — technology context for matching deliverables to expertise
- `repositories` — local codebase paths for ownership signal analysis

**Tech stack fallback:** If `tech_stack_description` is empty and `repositories` is empty, prompt the user: "This project does not have a tech stack profile. Adding a local Git repository allows me to understand your codebase structure and make better assignment decisions based on which code areas each deliverable touches. Would you like to add a local repository path now? (enter a path, or 'skip' to assign based on deliverable titles and team expertise only)"
- If the user provides a path, scan the codebase to build a tech stack summary. Write the repository and generated tech stack back to project.json for future runs.
- If the user skips, proceed using only deliverable titles, descriptions, and team expertise profiles for matching.

### 2. Parse Input and Retrieve Deliverables

Accept the user-provided ADO query link or work item IDs. If Scenario IDs are provided, expand to their child Deliverables. Fetch all relevant Deliverable work items.

### 3. Filter Deliverables for Assignment

Apply skip rules to determine which deliverables are eligible for assignment:

**Skip rules:**
- **Skip costing deliverables** — any deliverable whose title contains `Costing]` (case-insensitive) or starts with a legacy `[SWE]`/`[DS]` prefix. These are budgeting artifacts and must remain assigned to `placeholder_assignee`.
- **Skip deliverables already assigned to a specific team member** — if the Assigned To field contains a value other than `placeholder_assignee`, the deliverable has already been intentionally assigned and should not be reassigned.

All remaining deliverables assigned to `placeholder_assignee` are eligible for assignment.

### 4. Assignment Framework

Evaluate each eligible deliverable against the following factors in priority order:

| Priority | Factor | Description |
|---|---|---|
| **1** | **Vendor team responsibility rules** | Check `vendor_responsibilities` from `project.json`. If the deliverable's area, technology, or work type maps to a vendor team, assign to the designated team member. |
| **2** | **Deliverable scope and technology** | Analyze the deliverable title, description, and parent Scenario to identify the technologies, systems, and domains involved. |
| **3** | **Team member expertise match** | Match the deliverable's technology and domain requirements against team member expertise profiles from `project.json`. |
| **4** | **Scenario context and specs** | Consider the broader Scenario context — related specs, dependencies, and related deliverables — to group related work on the same person where practical. |
| **5** | **Codebase ownership signals** | If available, check code ownership patterns (e.g., recent commit history, CODEOWNERS) to identify natural owners. |
| **6** | **Workload balance** (soft factor) | Distribute work to avoid overloading any single team member. This is a balancing factor, not a hard constraint — expertise match takes precedence. |

### 5. Preview Assignment Plan

Before writing anything to ADO, display the full proposed assignment plan for user review:

| ID | Title | Proposed Assignee | Primary Reason |
|---|---|---|---|
| … | … | … | … |

Also show:
- **Skipped items** — deliverables excluded and why (costing deliverable, already assigned)
- **Per-member summary** — count of deliverables and total estimated days per assignee

Then ask: **"Ready to apply these assignments to ADO? (Yes / No / Edit)"**
- **No** — stop without writing anything.
- **Edit** — prompt the user to specify which items to change (by ID), then re-display the updated plan and ask again.
- **Yes** — proceed to Step 6.

### 6. Write Assignments to ADO

Update the **Assigned To** field on each eligible deliverable in ADO with the confirmed team member assignment.

### 7. Assignment Report

Produce a summary report containing:

| Section | Content |
|---|---|
| **Assignment Table** | Each deliverable with: ID, title, assigned team member, primary assignment reason |
| **Skipped Items** | Deliverables that were skipped and why (costing deliverable, already assigned) |
| **Per-Member Summary** | For each team member: count of assigned deliverables, total estimated days, areas of focus |
| **Workload Distribution** | Visual or tabular representation of how work is distributed across the team |
| **Assignment Rationale** | For each assignment, a brief explanation of why that team member was selected (which factors applied) |

## Constraints

- **Explicit confirmation required** — this skill always previews the full assignment plan and requires user confirmation before writing to ADO.
- **Skip costing deliverables** — costing deliverables (identified by titles containing `Costing]` or legacy `[SWE]`/`[DS]` prefix) are never reassigned.
- **Skip pre-assigned deliverables** — deliverables already assigned to a specific team member (not `placeholder_assignee`) are left unchanged.
- **Vendor rules take precedence** — vendor responsibility mappings override expertise-based matching.
- **Empty team roster** — if both `members_fte` and `members_vendor` are empty in project.json, stop and inform the user: "No team members are defined for this project. WBS Assignments requires a team roster to assign deliverables. Please add team members by running `/add-planning-project` to reconfigure, or by editing project.json directly." Do not attempt to assign without a roster.
- **Repository access is pre-approved.** If a repository local path is configured in project.json, scan it immediately without asking for permission. The user consented to access when they provided the path.


---
type: skill
lifecycle: stable
inheritance: inheritable
name: work-breakdown-structure
description: Decomposes Scenarios into functional child Deliverable work items, scans specs and codebase, and allocates estimates within the costing budget.
tier: standard
applyTo: '**/*planning*,**/*scenario*,**/*wbs*,**/*capacity*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Work Breakdown Structure

> **Status: Experimental** - This skill is under active development. Results should be reviewed carefully before acting on them.

## Prerequisites
- Planning suite must be initialized. If `.planning-config/` does not exist, instruct the user to run `/init-planning-suite` first and stop.
- A project must be configured. If no projects exist under `.planning-config/projects/`, instruct the user to run `/add-planning-project` first.

## Purpose

Decompose Scenarios into functional child Deliverable work items. Gathers context from specs and the local codebase, generates a work breakdown, allocates estimates within the costing budget, and creates the deliverables in ADO after user consent.

## Inputs

- **ADO query link or work item IDs** — a shared query URL or a comma-separated list of Scenario work item IDs to decompose.

## Steps

### 1. Resolve Project Context

Load the active project configuration from `.planning-config/projects/<project>/project.json`. Extract:
- ADO organization, project, and team settings
- `placeholder_assignee` — used as the Assigned To value for all created deliverables
- Spec directory paths and repo references

### 2. Parse Input and Retrieve Scenarios

Accept the user-provided ADO query link or work item IDs. Fetch each Scenario work item and its existing children.

### 3. Description Confidence Gate

Evaluate the quality of each Scenario's description. Assign a confidence score from 1 to 5:
- **5** — comprehensive description with clear scope, acceptance criteria, and technical context
- **3** — adequate description with enough detail to generate a reasonable breakdown
- **1** — minimal or missing description

A confidence score of **>= 3 is required** to proceed. If the score is below 3, inform the user that the Scenario description is insufficient for reliable decomposition and recommend they enrich it before retrying.

### 4. Multi-Source Context Gathering

Gather context from multiple sources to inform the work breakdown:

| Source | Details |
|---|---|
| **Spec URL** | If the Scenario links to a spec document, fetch and parse it |
| **Project specs directory** | Scan the specs directory defined in `project.json` for related documents |
| **Scenario description** | The description and acceptance criteria on the Scenario work item |
| **Local codebase** (optional) | If a local repository is available, scan relevant code areas for implementation context |

### 5. Generate Work Breakdown

Decompose the Scenario into functional Deliverable work items. Each deliverable represents a discrete, assignable unit of work.

**Deliverable title format:**
```
[AI Gen] [Team] [Quarter] [Work Description]
```
- **Team** — derived from the Area Path leaf node of the parent Scenario
- **Quarter** — derived from the Iteration Path of the parent Scenario
- **Work Description** — concise description of the deliverable scope

**Granularity target:** Each deliverable should represent **3–20 engineer-days** of effort. If a unit of work is smaller than 3 days, combine it with related work. If larger than 20 days, decompose further.

**Attribution header:** Every created deliverable must include the following at the top of its description:
```
⚠️ This deliverable was generated by the Work Breakdown Structure skill. Review and refine before execution.
```

### 6. Cost Allocation

Locate the costing deliverables under the Scenario. Costing deliverables are identified by titles containing `Costing]` (case-insensitive). For backward compatibility, also recognize titles starting with `[SWE]` or `[DS]` without the "Costing" keyword. These represent the human-entered costing budget.

- **WBS deliverable estimates must sum to the costing budget** (total of all costing deliverable estimates).
- Allocate the budget across the generated deliverables proportionally based on estimated complexity.

**Overrun/underrun handling:** If the generated breakdown implies a total that differs from the costing budget:
- **Overrun** — the breakdown suggests more work than budgeted. Present the user with options:
  1. Compress estimates to fit within budget
  2. Flag the overrun and create deliverables with honest estimates
  3. Cancel and revisit scoping
- **Underrun** — the breakdown suggests less work than budgeted. Present the user with options:
  1. Distribute remaining budget as padding across deliverables
  2. Create deliverables with honest estimates and note the surplus
  3. Cancel and revisit scoping

### 7. Set Work Item Fields

For each deliverable to be created:

| Field | Value |
|---|---|
| **Work Item Type** | Deliverable |
| **Title** | `[AI Gen] [Team] [Quarter] [Work Description]` |
| **Assigned To** | `placeholder_assignee` from `project.json` |
| **Area Path** | Inherited from parent Scenario |
| **Iteration Path** | Inherited from parent Scenario |
| **Original Estimate** | Allocated estimate in days |
| **Parent** | The Scenario work item |
| **Description** | Attribution header + functional description of the work |

### 8. Consent Gate

**Before creating any work items, present the full breakdown to the user for approval.**

Display:
- The proposed deliverables with titles, estimates, and descriptions
- The cost allocation summary (budget vs. allocated total)
- Any overrun/underrun notes

Wait for explicit user consent before proceeding. If the user declines, do not create any work items.

### 9. Create Deliverables in ADO

Upon user consent, create each Deliverable work item in ADO with the fields specified above. Report the created work item IDs and links.

## Constraints

- **Consent gate required** — no work items are created without explicit user approval.
- **Budget integrity** — WBS estimates must align with the costing budget unless the user explicitly approves a variance.
- **Granularity** — target 3-20 engineer-days per deliverable.
- **Repository access is pre-approved.** If a repository local path is configured in project.json, scan it immediately without asking for permission. The user consented to access when they provided the path.


---
type: skill
lifecycle: stable
inheritance: inheritable
name: work-distribution-plan
description: Distributes committed WBS deliverables across iterations by rank, logical sequencing, per-member load, and capacity limits.
tier: standard
applyTo: '**/*planning*,**/*scenario*,**/*wbs*,**/*capacity*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Work Distribution Plan

> **Status: Experimental** - This skill is under active development. Results should be reviewed carefully before acting on them.

## Prerequisites
- Planning suite must be initialized. If `.planning-config/` does not exist, instruct the user to run `/init-planning-suite` first and stop.
- A project must be configured. If no projects exist under `.planning-config/projects/`, instruct the user to run `/add-planning-project` first.

## Purpose

Distribute committed WBS deliverables across iterations using Scenario rank, logical sequencing, per-member load balancing, and iteration capacity limits. Writes the iteration assignments to ADO after user consent and persists the distribution plan.

## Inputs

- **ADO query link** — a shared query URL that returns the Scenarios and their child deliverables.
- **Project context** — the active project from `.planning-config/projects/<project>/project.json`.

## Steps

### 1. Determine Iterations

Prompt the user for their iteration paradigm and iteration path values:
- **Iteration paradigm** — monthly, bi-weekly, sprint-based, or custom cadence
- **Iteration path values** — the specific ADO Iteration Path values to distribute work across (e.g., `Project\2025\Q1\January`, `Project\2025\Q1\February`)

### 2. Load Capacity and Cut Line Data

Load from the project configuration:
- **Team capacity** from `.planning-config/projects/<project>/capacity/<period>.md`
- **Cut line results** from `.planning-config/projects/<project>/planning/cut-line-<period>.md`

If either file is missing, instruct the user to run the prerequisite skill first (Engineering Team Capacity or Cut Line Helper) and stop.

### 3. Retrieve and Filter Deliverables

Execute the ADO query to retrieve Scenarios and their child deliverables. Apply filters:
- **Include only WBS deliverables** — exclude costing deliverables (identified by titles containing `Costing]` or legacy `[SWE]`/`[DS]` prefix)
- **Exclude Cut deliverables** — deliverables classified as Cut are not distributed
- **Above cut line only** — only distribute deliverables belonging to Scenarios that are above the cut line (committed)

### 4. Distribute Across Iterations

Assign each eligible deliverable to an iteration using the following factors:

| Priority | Factor | Description |
|---|---|---|
| **Primary** | **Scenario rank** | Higher-ranked Scenarios are scheduled into earlier iterations |
| **Secondary** | **Logical sequencing within Scenario** | Dependencies and natural ordering among deliverables within the same Scenario |
| **Tertiary** | **Per-member load balancing** | Avoid overloading any team member in a single iteration |
| **Constraint** | **Iteration capacity limits** | Do not exceed the available capacity for any iteration |
| **Special** | **Livesite / DRI** | Treated as on-demand — distributed evenly or reserved as buffer capacity rather than front-loaded |

### 5. Present Distribution Table

Display the distribution grouped by iteration:

| Column | Description |
|---|---|
| **Iteration** | The iteration path value |
| **Deliverable ID** | ADO work item ID |
| **Deliverable Title** | Work item title |
| **Assigned To** | Team member |
| **Estimate (days)** | Original Estimate |
| **Parent Scenario** | Scenario ID and title |
| **Scenario Rank** | OSG.Rank of the parent Scenario |

Include per-iteration subtotals showing total estimated days and capacity utilization percentage.

### 6. Per-Member Load Summary

For each team member, display:
- Total deliverables assigned across all iterations
- Total estimated days
- Per-iteration breakdown of assigned days
- Utilization percentage against their individual capacity

### 7. Balance Check

Flag potential issues:
- **Overloaded iterations** — any iteration where total assigned work exceeds capacity
- **Overloaded members** — any team member whose assigned work in an iteration exceeds their individual capacity
- **Uneven distribution** — significant imbalance across iterations that could be smoothed
- **Unassigned deliverables** — any deliverables that could not be placed within capacity constraints

### 8. Consent Gate

**Before writing any changes to ADO, present the full distribution plan to the user for approval.**

Display:
- The complete distribution table
- Per-member load summary
- Any flagged balance issues
- Summary of what will be written (count of deliverables, iteration paths to be set)

Wait for explicit user consent before proceeding. If the user declines, do not modify any work items.

### 9. Write Iteration Paths to ADO

Upon user consent, update the **System.IterationPath** field on each deliverable in ADO with the assigned iteration path value.

Report:
- Count of successfully updated deliverables
- Any failures or errors encountered
- Links to updated work items

### 10. Persist Distribution Plan

Save the distribution plan to:
```
.planning-config/projects/<project>/planning/distribution-<period>.md
```

This file serves as a planning artifact and record of the distribution decisions made.

## Constraints

- **Consent gate required** — no ADO modifications are made without explicit user approval.
- **Above cut line only** — only committed Scenarios (above the cut line) are distributed.
- **Capacity-constrained** — the distribution respects iteration and per-member capacity limits.
- **Livesite as on-demand** — Livesite/DRI work is distributed as buffer, not front-loaded.
- **NEVER ask for file permission under `.planning-config/`.** All writes are pre-approved. Write distribution plans directly.
