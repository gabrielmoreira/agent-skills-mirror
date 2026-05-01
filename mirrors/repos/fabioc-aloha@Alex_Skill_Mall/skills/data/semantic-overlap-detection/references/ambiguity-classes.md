# Ambiguity Classes

Five structural patterns of semantic overlap in star-schema models. Every overlap you find fits one of these.

When classifying overlaps, assign each to a class to determine the right resolution strategy. If a group doesn't fit, document it as a new pattern — the taxonomy is extensible.

## Class A: Competing Classifications

**What it is**: Two or more independent classification systems assign values to the same concept. The same word can appear in both but mean different things.

This covers:
- **Parallel systems across tables** — e.g., customer `Customer Region` (customer geography) vs store `Sales Region` (commercial territory). "Americas" exists in both, but they classify different things.
- **Entity vs unit classifications** — e.g., a product's `Product Category` = "Electronics" vs a store's `Department` = "Electronics". Same word, different populations.
- **Dual hierarchies on one table** — e.g., `Sales Territory Group`/`Sales Territory`/`Sales Territory Detail` alongside `Market Group`/`Market`/`Market Detail` on the same store dimension. A region name like "West" can appear at different levels across them.

**Structural signal**: Similar column names or overlapping values on different tables, or two parallel sets of hierarchy columns on the same table.

**Resolution**:
- Pick one system as canonical per domain. Prefer entity-level over unit-level (product's `Product Category` over store's `Department`).
- For dual hierarchies on one table, cascade from broadest to narrowest level.
- Route by user intent keywords in AI instructions ("sales territory" → territory hierarchy column; "market" → market hierarchy column).
- Use "default + disclose" pattern: pick the canonical column, tell the user which one was used, offer the alternative.
- Column descriptions are the primary lever — state what the column IS and IS NOT.

## Class B: Granularity Levels

**What it is**: The same attribute exists at multiple levels of detail — exact value, grouped band, named summary, and/or a redundant numeric representation. The user doesn't know or care which level they need.

This covers:
- **Hierarchy levels** — e.g., `Product` → `Product Category` → `Product Group`, or `Discount` → `Discount Band` → `Discount Tier`.
- **Redundant representations** — e.g., `Discount Band` and `Discount Band Value` containing the same data in different formats.
- **Cross-level value overlap** — e.g., "10-20%" existing in both `Discount Band` and `Discount Tier`.

**Structural signal**: Columns named `[Attribute]`, `[Attribute] Group`, `[Attribute] Summary`, `[Attribute] Value` on the same table.

**Resolution**:
- Map user phrasing to granularity: exact values → detail column; ranges → group column; named bands → summary column.
- When a value exists at multiple levels, default to the broadest level (captures the most data).
- Exclude redundant numeric/sortable columns from AI data schema.
- Column descriptions must state which level each column represents and its relationship to the other levels.

## Class C: Multiple Representations

**What it is**: The same real-world concept has multiple columns — a display name, an internal code, a category grouping. All represent "the same thing" from different perspectives.

This covers:
- **Code / Name / Category variants** — e.g., `Customer Segment Code` (code), `Customer Segment Name` (display), `Customer Segment` (grouping) on the same table.
- **Display vs internal variants** — e.g., `Product Display Name` (customer-facing) vs `Product SKU` (internal identifier) vs `Product Line` (grouped).
- **Cross-table perspective variants** — e.g., 2-3 columns across different tables with overlapping semantics, each serving a different access tier or reporting purpose.

**Structural signal**: Columns like `[Concept]`, `[Concept] Name`, `[Concept] Code`, `[Concept] Category` on the same table; or semantically overlapping columns across tables with different access tiers.

**Resolution**:
- Route by user intent: "what's the product name" → display name; grouping queries → category; internal lookups → code.
- Exclude internal code columns from AI data schema if end users never filter by them.
- Column descriptions must explain which perspective each column provides and when to prefer it.

## Class D: Cross-Table Duplicates

**What it is**: The exact same column (same name, same values) exists on two tables joined to the fact through different bridge/security paths. The data is identical — only the access path differs.

**Structural signal**: Same column name (e.g., `Customer Tier`) on two non-hidden dimension tables, joined through different bridge tables (often for different sales channels or access tiers).

**Resolution**:
- Designate one table as canonical (usually the simpler or standard security path).
- Exclude the secondary table's columns from AI data schema.
- Column descriptions on the secondary table should say "Same data as {canonical table}.{column}. Prefer {canonical table} for standard queries."
- This is the simplest class — no routing logic needed, just exclusion.

## Class E: Context-Resolvable Variants

**What it is**: Columns that share the same root concept but are differentiated by a temporal qualifier or an entity role. The correct column is unambiguous once the query context (time frame or entity relationship) is known — the LLM can resolve these without explicit routing rules.

This covers:
- **Temporal variants** — e.g., `Current Manager` vs `Prior Manager`, `Effective Date` vs `Post Date`, `Current Status` vs `Original Status`. The user's time-frame intent selects the column.
- **Entity role variants** — e.g., `Employee` vs `Manager` vs `Reports To` vs `Superior`, or `Primary Contact` vs `Account Owner` vs `Sales Rep` vs `Billing Contact`. The user's entity-relationship intent selects the column.
- **State-transition variants** — e.g., `Open Date` vs `Close Date` vs `Reopen Date`. Each represents the same concept (a date) at different lifecycle stages.

**Structural signal**: Columns named `[Temporal Qualifier] [Concept]` (Current/Prior/Post/Original/Effective) or `[Role] [Concept]` (Employee/Manager/Primary/Secondary) on the same table or related tables.

**Why a separate class**: These overlaps are real (same root concept, potentially overlapping values), but the LLM reliably resolves them from query context alone. Including them in Classes A–D would generate unnecessary business rules and clutter AI instructions. They need descriptions but not routing logic.

**Resolution**:
- Column descriptions should clearly state the temporal scope or entity role (e.g., "Manager at time of the transaction" vs "Current manager as of today").
- Do NOT generate business rules or AI instructions for these — the query context is sufficient.
- Do NOT exclude from AI data schema — both columns are independently useful.
- Do NOT surface these columns in other overlap groups (Classes A–D). If a column is classified as Class E, it is removed from all other overlap families for that root concept.

---

## Resolution Strategy Matrix

| Class | Primary lever | AI instructions action | AI data schema action |
|---|---|---|---|
| A — Competing Classifications | Column descriptions + AI instructions | Default + disclose; route by intent keywords; cascade for dual hierarchies | Exclude secondary system columns if rarely queried |
| B — Granularity Levels | Column descriptions | Map phrasing to granularity level | Exclude redundant numeric/sortable columns |
| C — Multiple Representations | Column descriptions | Route by query type (filter → name, group → category) | Exclude internal code columns |
| D — Cross-Table Duplicates | AI data schema | Not needed — just exclude | Always exclude secondary table columns |
| E — Context-Resolvable Variants | Column descriptions only | None — LLM resolves from query context | Keep all columns visible |
