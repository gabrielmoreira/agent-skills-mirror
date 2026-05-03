---
type: skill
lifecycle: stable
inheritance: inheritable
name: semantic-overlap-detection
description: Analyze a semantic model (via MCP or TMDL) to find columns whose value domains overlap, classify ambiguity types, generate proposed descriptions/rules/exclusions, and produce a review Excel for domain experts. Use when a semantic model has columns whose values overlap across tables or hierarchies, when Copilot picks the wrong column for ambiguous queries, when preparing a model for Prep data for AI, or when auditing a model for attribute collisions before connecting a data agent.
tier: standard
applyTo: '**/*semantic*,**/*overlap*,**/*detection*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Semantic Overlap Detection

Analyze a semantic model (via MCP connection or TMDL export) to find columns whose value domains overlap, classify ambiguity types, generate proposed fixes, and produce a review Excel workbook for domain expert review. This skill covers the full analysis pipeline through Excel generation and async handoff.

**Next step after this skill**: Once the domain expert has reviewed the Excel, use the **semantic-disambiguation** skill to apply approved changes to the live model.

## When to Use

- A semantic model has multiple columns that could plausibly match the same natural-language query
- A Fabric data agent or Copilot is silently picking the wrong column
- You need to prepare a model for the "Prep data for AI" workflow
- You want to audit a TMDL export for disambiguation gaps before connecting a data agent

## Procedure

### Phase 0: Read Model Metadata via MCP (preferred) or TMDL files

> **MCP tool naming**: This skill references tools by their VS Code MCP integration names (`mcp_powerbi-modeling-mcp_*`). In other environments (Agency CLI, Claude Code), find the equivalent Power BI Modeling MCP server tools — the operations and parameters are the same, only the tool name prefix may differ.

**If MCP tools are available**, connect to the live model and read metadata directly. This is preferred over TMDL file parsing because it reflects the current model state, includes runtime metadata (hidden flags, descriptions), and avoids stale exports.

1. **Connect** via `mcp_powerbi-modeling-mcp_connection_operations`:
   - Fabric: `ConnectFabric` with workspace and dataset names
   - Desktop: `Connect` with port number

2. **List all tables** via `mcp_powerbi-modeling-mcp_table_operations` (operation: `List`). For each table, record:
   - `name`, `isHidden`, `description`
   - Skip tables where `isHidden = true`

3. **List columns per table** via `mcp_powerbi-modeling-mcp_column_operations` (operation: `List`, filter by `tableNames`). For each column, record:
   - `name`, `tableName`, `dataType`, `isHidden`, `description`, `sourceProviderType`
   - Skip columns where `isHidden = true` or `dataType` is not string/text

4. **List relationships** via `mcp_powerbi-modeling-mcp_relationship_operations` (operation: `List`). Record:
   - `fromTable`, `fromColumn`, `toTable`, `toColumn`, `crossFilteringBehavior`, `isActive`
   - This reveals join paths and bridge tables — critical for identifying Class D (cross-table duplicates via different security bridges)

5. **List measures** via `mcp_powerbi-modeling-mcp_measure_operations` (operation: `List`). Record:
   - `name`, `tableName`, `description`, `expression`
   - Measure expressions reveal which columns are actively used — columns referenced in key measures are higher priority for disambiguation

**If MCP is not available**, fall back to reading TMDL files from the `tables/` folder as described in Phase 1.

### Phase 1: Discover Overlaps

Use the metadata collected in Phase 0 (or from TMDL files if MCP is unavailable):

1. **Start from the table/column inventory** — if Phase 0 was used, you already have filtered non-hidden tables and non-hidden string columns. If using TMDL files, read all `tables/*.tmdl` files and filter to non-hidden tables (skip `isHidden` at table level or `changedProperty = IsHidden` outside any column block), then extract non-hidden string columns.
2. **Record for each column**: table name, column name, dataType, existing description (from `///` comments or Phase 0 metadata)
3. **Use relationship metadata** (from Phase 0 step 4 or `relationships.tmdl`) to identify bridge table patterns — columns that exist on two tables joined via different bridge paths are Class D candidates
4. **Classify each column into a semantic domain** using the [domain taxonomy](./references/domain-taxonomy.md) as a starting point — adapt domain names to the model's actual business context
5. **Systematic overlap family scan** — after domain classification, scan column names to find overlap groups you may have missed. For each column, identify:
   - The **root concept** (core term, e.g., `Country`, `Region`, `Category`)
   - Any **modifier** (prefix/qualifier that scopes it, e.g., `Ship-To`, `Bill-To`, `Wholesale`, `Retail`)
   - Any **representation suffix** (format/level indicator, e.g., `Group`, `Summary`, `Value`, `Sort`, `Code`)

   Group all columns sharing the same root concept into an **overlap family** (same table and related tables). Each family with 2+ members is a candidate overlap group to classify using the [domain taxonomy](./references/domain-taxonomy.md) and [ambiguity classes](./references/ambiguity-classes.md).

   Watch for these modifier patterns — they often indicate independent classification systems on the same concept:
   - Scope: `Ship-To X` vs `Bill-To X`, `Retail X` vs `Wholesale X`
   - Access tier: `Internal X` vs `X`
   - Cross-table roles: `Sold-To X` / `Delivered-To X` / `Billed-To X` vs `X`
   - Derived: `Product X Mapping`, `X Indicator`

   Watch for these representation suffixes — they indicate hierarchy levels or redundant formats:
   - Hierarchy: `X Detail`, `X Summary`, `X Group`
   - Parallel cuts: `X Region`, `X Territory`, `X Market`
   - Redundant: `X Value`, `X Code`, `X Sort`

6. **Family completeness check**: When any member of a family is identified, enumerate ALL members. Don't stop at 2–3 representative members — check for all level variants, parallel cuts, representation variants, and cross-table role variants. Incomplete families cause missed overlaps.
7. **Entity/attribute used in one overlap group may still be used in another** — e.g., `Customer Region` could overlap with `Sales Region` (Class A) and also have multiple hierarchy levels (`Customer Region` vs `Customer Region Group`) that overlap (Class B). The same column can be in multiple groups and classes.
8. **Classify temporal and entity-role variants as Class E** — columns differentiated by a temporal qualifier or entity role belong to [Class E (Context-Resolvable Variants)](./references/ambiguity-classes.md). Identify them by these patterns:
   - Temporal variants: `Current X` / `Prior X` / `Post X` / `Effective X` / `Original X`
   - Entity role variants: `Employee` / `Manager` / `Reports To` / `Superior`; `Primary Contact` / `Account Owner` / `Sales Rep` / `Billing Contact`
   - State-transition variants: `Open Date` / `Close Date` / `Reopen Date`

   Class E columns:
   - **Get column descriptions** (Phase 3) — describe the temporal scope or entity role clearly
   - **Do NOT get business rules** (Phase 4) — the LLM resolves these from query context
   - **Do NOT appear in Schema Exclusions** (Phase 5) — both columns are independently useful
   - **Are removed from all other overlap families** — once classified as Class E, these columns must not appear in any Class A–D overlap group for the same root concept. This prevents duplicate analysis and unnecessary routing rules.
9. **Report the remaining hard cases**

### Phase 1b: Verify and Quantify Overlaps

Phase 1 identifies overlaps from metadata. There are two kinds, and data verification only helps with one:

- **Value overlaps**: the same string literal exists in two columns. Data verification (INTERSECT queries) confirms and quantifies these.
- **Conceptual overlaps**: two columns represent the same real-world concept but with different value encodings. A user asking about "North America" could target `Sales Region` = "Americas" or `Customer Region` = "NA" — zero string intersection, but the disambiguation problem is real. Data verification returns 0 for these but they **remain in the analysis**.

**If MCP tools are available** (connection already established in Phase 0), run DAX to quantify value overlaps:

1. Run a single batch query — concatenate counts into one string to work around resource-URI readability:
```dax
EVALUATE ROW(
  "Result",
  "PairA=" & COUNTROWS(INTERSECT(DISTINCT(T1[ColA]), DISTINCT(T2[ColB])))
  & "|PairB=" & COUNTROWS(INTERSECT(DISTINCT(T3[ColC]), DISTINCT(T4[ColD])))
)
```
2. Classify each overlap group:

| Type | INTERSECT count | Severity | Action |
|---|---|---|---|
| Value overlap, 0 | N/A | Check if conceptual overlap — if no, drop | — |
| Value overlap, 1–10 | Targeted | List exact collision values in AI instructions | — |
| Value overlap, 11–50 | Significant | Column descriptions + default+disclose rules | — |
| Value overlap, 50+ | Pervasive | Exclude secondary column from AI data schema | — |
| Conceptual overlap (INTERSECT = 0 BUT same domain) | Conceptual | Column descriptions are the primary lever — they must explain the semantic difference between the two columns. AI instructions should route by user-intent keywords. | — |

3. For targeted overlaps, enumerate actual shared values for precise AI instruction rules:
```dax
EVALUATE TOPN(20, INTERSECT(DISTINCT(T1[ColA]), DISTINCT(T2[ColB])))
```

4. For columns being profiled for descriptions (Phase 3), extract distinct values:
```dax
EVALUATE DISTINCT('Table'[Column])
```

**If no MCP connection is available**, generate the DAX queries as output for the user to run manually. Conceptual overlaps should still be flagged from metadata analysis alone.

### Phase 2: Classify Ambiguity

For each overlap group (verified or high-confidence unverified), classify into one of the [5 structural ambiguity classes](./references/ambiguity-classes.md). If a group doesn't fit any class, document it as a new one — the taxonomy is extensible.

### Phase 3: Generate Column Descriptions

For every column in an overlap group, write a `///` TMDL description following the **IS / IS NOT / CANONICAL** pattern. Use the [description templates](./references/description-templates.md) for consistent phrasing.

**Every column that appears in Schema Exclusions (Phase 5) ALSO gets a description.** The description should explain what the column is and recommend the preferred alternative using a class-appropriate template (e.g., Template 5 for redundant numeric columns, Template 3 for cross-table duplicates). This ensures reviewers understand what each excluded column represents.

#### Data profiles in descriptions

Enrich descriptions with value metadata based on column cardinality. This helps the LLM match user terms to actual column values at reasoning time without runtime queries:

| Cardinality | Strategy | Example |
|---|---|---|
| ≤ 20 values | Enumerate all values | `/// Sales region (5 values: Americas, EMEA, Greater China, Japan, Asia).` |
| 21–100 values | Top examples + count | `/// Product subcategory (~20 values: Laptops, Headphones, Keyboards, ...).` |
| 100+ values | Count + representative examples | `/// Ship-to city (2,800+ values, e.g., New York, London, Tokyo, Sydney, ...).` |

> **Data sensitivity**: Before extracting sample values, ask the user whether the model contains PII, confidential, or restricted data. If it does (or if uncertain), default to **counts only** (e.g., "2,800+ distinct values") and omit example values from descriptions. Only embed sample values when the user explicitly confirms the data classification permits it. Values extracted via DAX end up in the analysis JSON, the review Excel, and column descriptions — all of which may be shared with reviewers or persisted in model metadata.

If MCP is connected, extract distinct values via DAX (Phase 1b step 4). Otherwise, note the column as needing profile data.

**Output**: `| TMDL file | Column name | Current description | New description |`

### Phase 4: Generate AI Instructions

Write disambiguation rules for the AI instructions feature (Prep data for AI → Add AI instructions). Follow the **"default + disclose" pattern**: the agent picks the canonical column, tells the user which one it used, offers the alternative. Reserve forced clarification only for cases with completely different scope.

Stay within the 10,000 character limit. Read [architecture-reference.md](./references/architecture-reference.md) if unsure which authoring surface to use.

**Output**: Markdown text block ready to insert into AI instructions.

### Phase 5: Generate AI Data Schema Exclusions

List columns to exclude from the AI data schema (Prep data for AI → Simplify data schema). Use the **severity from Phase 1b** to guide decisions:

- **Pervasive overlap (50+)**: Strongly consider excluding the secondary column — with near-complete value overlap, two columns provide zero disambiguation signal and double the confusion surface
- **Cross-table duplicates (Class D)**: Always exclude the secondary table's columns
- **Redundant numeric/value columns (Class B)**: Exclude only when a display/canonical sibling exists on the same table (e.g., `Discount Band Value` when `Discount Band` exists). Do not exclude columns named `X Value` or `X Code` that have no corresponding display column — they may be the only representation.
- **Targeted overlap (1-10)**: Usually keep both columns — the collision is limited enough to handle with AI instructions

**Output**: `| Table | Column | Overlap count | Reason for exclusion |`

Each exclusion should also specify an **Exclusion Scope** recommendation:
- **AI Data Schema Only** (default, safer): Hides the column only from AI/Copilot queries via Prep data for AI → Simplify data schema. The column remains visible in reports. User applies manually in Fabric UI.
- **Model Level (isHidden)**: Sets `isHidden = true` on the column — hides it from reports AND AI schema. Agent can apply automatically via MCP. Use only when the column is truly redundant and not referenced by any report or measure.

### Phase 6: Persist Results

Save all outputs to the semantic model export folder for review and audit trail.

#### 6a. Build analysis JSON

Collect all analysis results from Phases 1–5 into a single JSON object. This is the input for the Excel generator script (`./scripts/generate_disambiguation_excel.py`):

```json
{
  "model_name": "My_Semantic_Model",
  "workspace": "My_Workspace",
  "overlap_groups": [
    {
      "domain": "Country",
      "overlap_group": "Country",
      "ambiguity_class": "A – Competing Classifications",
      "when_user_says": "a country name (\"India\", \"US\") or \"by country\"",
      "default_column": "Dim_Customer.Ship-To Country",
      "priority": "High",
      "columns": [
        {
          "table": "Dim_Customer",
          "column": "Ship-To Country",
          "current_description": "",
          "proposed_description": "Shipping destination country. Primary column for country-level analysis.",
          "suggested_synonyms": "country, shipping country, destination country",
          "when_to_prefer": "Default for all country queries."
        },
        {
          "table": "Dim_Customer",
          "column": "Bill-To Country",
          "current_description": "",
          "proposed_description": "Billing/invoicing address country.",
          "suggested_synonyms": "billing country, invoice country",
          "when_to_prefer": "When user says 'billing address' or 'invoice country'."
        }
      ]
    }
  ],
  "schema_exclusions": [
    {
      "overlap_group": "Discount",
      "ambiguity_class": "B – Granularity Levels",
      "table": "Dim_Product",
      "column": "Discount Band Value",
      "reason": "Redundant sortable representation of Discount Band"
    }
  ]
}
```

Save this JSON to `<plugin_root>/output/disambiguation_analysis.json` (where `<plugin_root>` is the `semantic-model-disambiguation` plugin directory). This file is:
- The input to the Excel generator
- A version-controlled record of the analysis
- Diffable across runs to detect new overlaps

#### 6b. Generate Excel workbook for business review

Use the generic script at `./scripts/generate_disambiguation_excel.py` to generate the workbook:

```python
from generate_disambiguation_excel import generate_workbook
from pathlib import Path
import json

# All paths relative to the plugin output/ directory
output_dir = Path(__file__).resolve().parent.parent.parent.parent / "output"
output_dir.mkdir(parents=True, exist_ok=True)

data = json.loads((output_dir / "disambiguation_analysis.json").read_text())
generate_workbook(data, output_dir / "disambiguation_results.xlsx")
```

Or from the command line:
```bash
python generate_disambiguation_excel.py --input output/disambiguation_analysis.json --output output/disambiguation_results.xlsx
```

The script generates a 4-sheet workbook with styling, dropdowns, alternating row shading, and auto-filters. Each sheet has a distinct header color for quick identification. It is **model-agnostic** — all model-specific data comes from the JSON input.

**Sheet 1 — Column Descriptions** (blue header): One row per column that needs a description update. Sorted by overlap group and ambiguity class to surface related columns together.

| Column | Content |
|---|---|
| Overlap Group | Name of the overlap family this column belongs to |
| Ambiguity Class | Dropdown: A – Competing Classifications / B – Granularity Levels / C – Multiple Representations / D – Cross-Table Duplicates / E – Context-Resolvable Variants |
| Table | Table containing this column |
| Column | Column name |
| Current Description | Existing description from the model (may be blank) |
| Proposed Description | New description following IS / IS NOT / CANONICAL pattern |
| Suggested Synonyms | Comma-separated natural-language terms users might say |
| Review Status | Dropdown: Pending / Approved / Rejected / Needs Discussion |
| Reviewer | Name of domain expert |
| Reviewer Comments | Free-text feedback |

**Sheet 2 — Business Rules** (teal header): One row per disambiguation routing rule. Each rule defines the default column for a domain and conditions for preferring alternatives.

| Column | Content |
|---|---|
| Overlap Group | Name of the overlap family this rule belongs to |
| Ambiguity Class | Dropdown: A–E (same as Sheet 1) |
| Domain | Semantic domain (e.g., Country, Region, Organization) |
| When User Says... | Natural-language trigger phrases that activate routing for this group |
| Default Column | The canonical/default column to use when user triggers this domain |
| Table | Table containing the default column |
| When to Prefer Alternative | Condition for preferring an alternative column |
| Alternative Columns | Comma-separated list of alternative columns |
| Priority | Dropdown: Critical / High / Medium / Low |
| Review Status | Dropdown |
| Reviewer | Name |
| Reviewer Comments | Free text |

**Sheet 3 — Schema Exclusions** (orange header): One row per column to hide from the AI data schema.

| Column | Content |
|---|---|
| Overlap Group | Name of the overlap family this exclusion belongs to |
| Ambiguity Class | Dropdown: A–E (same as Sheet 1) |
| Table | Table name |
| Column | Column name |
| Reason for Exclusion | Why this column should be hidden from AI queries |
| Action (Post-Approval) | Pre-filled: "Hide from AI data schema" |
| Review Status | Dropdown |
| Reviewer | Name |
| Reviewer Comments | Free text |

**Sheet 4 — Implementation Checklist** (purple header): Sequenced post-review execution steps. This sheet defines the order in which approved changes should be applied to the model. Uses a `Status` dropdown (Not Started / In Progress / Done / Blocked) instead of Review Status.

| Column | Content |
|---|---|
| Step | Sequential step number |
| Action | What to do (e.g., "Hide attributes from AI data schema", "Update column descriptions") |
| Source Sheet | Which review sheet feeds this step |
| Details | Detailed instructions for executing the step |
| Status | Dropdown: Not Started / In Progress / Done / Blocked |
| Owner | Person responsible |
| Notes | Free text |

The standard implementation steps are:
1. **Hide attributes** from AI data schema (source: Schema Exclusions)
2. **Update column descriptions** in semantic model (source: Column Descriptions)
3. **Add synonyms** to columns (source: Column Descriptions — Suggested Synonyms column)
4. **Update AI instructions** in Prep data for AI (source: Business Rules)
5. **Validate end-to-end** with test queries (source: All sheets)

#### 6c. Async review handoff

After generating the Excel workbook, **pause and hand off to the user for async review**.

1. **Tell the user** the Excel file location and what to do:
   - Open the workbook in Excel
   - Review each row on Sheets 1–3
   - Set Review Status to `Approved`, `Rejected`, or `Needs Discussion` for every row
   - Edit Proposed Descriptions, Suggested Synonyms, or routing rules as needed
   - Save and close the file

2. **Ask for confirmation**:
   - If `vscode_askQuestions` is available (VS Code Copilot), use it:
     ```
     header: "Review Complete?"
     question: "Have you finished reviewing the disambiguation Excel and set Review Status on all rows?"
     options: ["Yes, apply approved changes", "Not yet, I'll let you know when ready"]
     ```
   - Otherwise, ask in plain text and wait for the user's next message.

3. **If the user confirms "Yes, apply approved changes"**: Immediately proceed to the **semantic-disambiguation** skill procedure and execute it in the same conversation turn. Pass the Excel path as the argument. Do NOT ask the user to rephrase or re-invoke — chain directly.

4. **If not yet**: Acknowledge and end. Tell the user: *"When you're ready, say 'apply my reviewed disambiguation Excel at `<path>`' and I'll apply the approved changes."* The **semantic-disambiguation** skill will match that intent in a future session via its description.

#### Purpose

This approach serves four needs:
1. **Review**: Domain experts open the Excel, filter/sort/comment, and validate recommendations
2. **Reproducibility**: The JSON analysis file is diffable and version-controlled
3. **Rerun**: Comparing JSON across runs shows whether model changes introduced new overlaps
4. **Execution**: The **semantic-disambiguation** skill reads back the reviewed Excel and applies approved changes

## Scripts

This skill includes one script in the `./scripts/` folder:

| Script | Purpose | Input | When to use |
|---|---|---|---|
| `generate_disambiguation_excel.py` | Generate the 4-sheet review workbook | JSON file (analysis results) | Phase 6b — after analysis is complete |

### How the agent uses this script

The agent does NOT run this script as a subprocess. Instead, it:
1. Builds the analysis JSON from Phases 1–5 results
2. Calls `generate_workbook(data, output_path)` directly or writes the JSON and runs the script

## Examples

### Example input

User provides a workspace name and dataset, or a path to a TMDL export:
- `"Analyze the Regional_Sales_Analytics model in workspace Sales-Insights"`
- `"Identify overlaps in the Sales model and save results to the plugin output folder"`

### Example overlap finding (Phase 1 output)

> **Overlap Group: Country** (Severity: High)
> `Ship-To Country` (Dim_Customer) vs `Bill-To Country` (Dim_Customer) vs `Sales Region` (Dim_Store)
> Shipping destination vs billing address vs commercial territory — "India" means different things in each.
> **Default**: `Ship-To Country`

### Example column description (Phase 3 output)

```
/// Shipping destination country (200 values: India, United States, Germany, ...).
/// NOT Bill-To Country (billing address) or Sales Region (commercial territory).
/// Primary column for country-level analysis.
column 'Ship-To Country'
```

### Example AI instruction rule (Phase 4 output)

```
When user mentions a country name ("India", "US", "Germany"):
- Default to Ship-To Country. Disclose: "I filtered by Ship-To Country (shipping destination)."
- If user says "billing address" or "invoice country" → use Bill-To Country instead.
```

### Example Excel output (Phase 6)

A 4-sheet workbook with Column Descriptions (proposed descriptions and synonyms per column, grouped by overlap group and ambiguity class), Business Rules (routing logic with default + disclose pattern), Schema Exclusions, and Implementation Checklist — each with distinct header colors, alternating row shading, filterable with Review Status dropdowns, and sequenced post-approval actions.

### Example async handoff (Phase 6c)

After generating the Excel, the agent says:

> The disambiguation workbook has been saved to `plugins/semantic-model-disambiguation/output/disambiguation_results.xlsx` with:
> - 44 column descriptions across 8 overlap groups to review
> - 8 business rules to review (routing logic)
> - 26 schema exclusions to review
>
> Please open the file in Excel, review each row, and set the Review Status column. When you're done, say "apply my reviewed disambiguation Excel" and I'll apply the approved changes to the model.

## Gotchas

- **Prefer MCP over TMDL files**: MCP reflects the live model state and enables data verification (INTERSECT queries, value profiling). TMDL exports can be stale. Always try Phase 0 MCP connection first.
- **`changedProperty = IsHidden` ≠ `isHidden`**: `changedProperty = IsHidden` means the visibility was toggled at the report layer — the column is still in the model and can appear in the AI data schema. Only `isHidden` on the column definition truly hides it. Both affect initial AI data schema setup (hidden fields are auto-excluded), but the behavior is different.
- **Tables with `changedProperty = IsHidden` at table level** (outside any column block) are hidden tables. Don't confuse table-level hidden with column-level hidden.
- **Linguistic metadata edits are wasted work**: The `linguisticMetadata` JSON in `cultures/en-US.tmdl` (synonyms, weights, visibility) is part of the Q&A feature being retired Dec 2026. Do not invest in synonym edits. See [architecture-reference.md](./references/architecture-reference.md).
- **AI instructions ≠ CustomInstructions**: The existing `CustomInstructions` field inside `linguisticMetadata` currently works but is being decoupled. New instructions should be authored via the Prep data for AI → Add AI instructions UI (10,000 char limit).
- **Column descriptions with "NOT" phrasing work**: Copilot reads `///` descriptions from the semantic model schema. Stating what a column is NOT helps the LLM avoid false matches. This is the highest-ROI disambiguation lever.
- **TMDL exports contain no data — but MCP can query it**: The `tables/*.tmdl` files define schema only. Use `mcp_powerbi-modeling-mcp_dax_query_operations` to run `INTERSECT`/`DISTINCT` queries against the live model when available. This turns metadata-inferred candidates into confirmed overlaps with actual shared values.
- **MCP DAX results are returned as resource URIs**: The powerbi-modeling-mcp MCP server returns query results as `vscode-chat-response-resource://` URIs rendered in the chat UI. These cannot be read back by the agent via `read_file`. Work around this by concatenating results into a single string inside the DAX query itself (use `&` concatenation and pipe delimiters), so the result appears as one readable cell rather than a multi-row CSV.
- **Hidden tables may still matter**: Tables with `changedProperty = IsHidden` at table level (e.g., Fact_Sales, Dim_Returns) are hidden from reports but their columns may be actively referenced by existing AI instructions or measures. Check existing instructions before excluding hidden tables from analysis.
