# Architecture Reference

## Three-Layer Disambiguation Model

A Fabric data agent connected to a semantic model has three control surfaces for steering column resolution. As of March 2026, two are durable and one is deprecated.

### Layer 1: Column Descriptions (TMDL `///` comments)

**Status: DURABLE** — Copilot and data agents read column descriptions from the semantic model schema.

Column descriptions are the highest-ROI disambiguation lever. They're purely additive metadata that cannot break existing reports or DAX. The agent's reasoning layer uses descriptions when deciding which column to filter on.

**Where**: `tables/*.tmdl` files, as `///` comments immediately before the `column` keyword.

**Format**:
```
/// What it IS: classification system, granularity, example values.
/// What it is NOT: which competing columns the user might confuse it with.
/// Canonical or secondary: whether this is the preferred column for its domain.
column 'Column Name'
```

### Layer 2: AI Instructions (Prep data for AI)

**Status: DURABLE** — This is the official forward-looking mechanism for providing Copilot with business context, terminology, and disambiguation rules.

**Where**: Authored via "Prep data for AI" button in Power BI Desktop or Service → "Add AI instructions" tab. Saved on the semantic model (LSDL). Can also be edited via Git/deployment pipelines (requires model refresh to sync).

**Limit**: 10,000 characters.

**Key behaviors**:
- Instructions are advisory — the LLM interprets them, no guarantee of exact compliance
- Instructions apply to all Copilot capabilities on the semantic model
- End users cannot see or disable instructions
- The "default + disclose" pattern (pick canonical column, tell user which one, offer alternative) is the practical architecture for disambiguation

### Layer 3: AI Data Schema (Prep data for AI)

**Status: DURABLE** — Replaces "hide from Q&A" for Copilot field exclusion.

**Where**: Authored via "Prep data for AI" → "Simplify data schema" tab. Select/deselect fields.

**Key behaviors**:
- Fields hidden in the semantic model are automatically excluded when you first set up the AI data schema
- Relationships are still respected regardless of exclusions
- End users cannot see or disable the schema
- This is the right mechanism for excluding duplicate columns (e.g., Dim_Customer_Wholesale.Customer Tier when Dim_Customer.Customer Tier is canonical)

### DEPRECATED: Linguistic Metadata (Q&A features)

**Status: DEPRECATED Dec 2026** — Do not invest.

The `linguisticMetadata` JSON blob in `cultures/en-US.tmdl` contains:
- Synonyms and synonym weights
- `Visibility: Hidden` for Q&A
- `CustomInstructions` (the existing instructions field)
- Linguistic relationships/phrasings

All of this is part of the Q&A feature being retired in December 2026. The `CustomInstructions` field currently still works because Copilot reads the LSDL, but Microsoft is introducing a new file format. New work should use AI instructions via Prep data for AI.

**Source**: [Deprecating Power BI Q&A](https://powerbi.microsoft.com/blog/deprecating-power-bi-qa/) (Dec 2025), [Prep data for AI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-prepare-data-ai) (March 2026).

## The "Default + Disclose" Pattern

Prompting users for column clarification mid-query every time there is an ambiguity might degrade the experience. The agent picks a column and returns results. The architecture compensates via:

1. **Default**: Column descriptions and AI instructions steer the agent toward the canonical column for each domain
2. **Disclose**: AI instructions tell the agent to state which column it used in its response text
3. **Offer alternative**: The agent mentions the competing column so the user can follow up

Reserve **forced clarification** (agent refuses to answer, asks user to clarify) only for cases where the two interpretations have completely different scope — e.g., "Washington" as city (DC) vs state (includes Seattle/Redmond).

## Relationship to `changedProperty = IsHidden`

In TMDL files, `changedProperty = IsHidden` on a column means the column's visibility was toggled at the report/perspective layer — it is NOT the same as `isHidden` (hard model-level hide). Both affect initial AI data schema setup (hidden fields are auto-excluded), but neither prevents the column from being used in DAX or appearing in the field selection pane of the AI data schema.
