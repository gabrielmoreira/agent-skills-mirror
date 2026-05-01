# Ontology Design Template

Use this template to plan your ontology before creating it in Fabric IQ.

## Ontology Name

**Name**: `_______________` (letters, numbers, underscores only)

**Purpose**: Brief description of what this ontology represents.

**Domain**: (e.g., Retail, Manufacturing, Healthcare, Supply Chain)

---

## Entity Types

Define the core business concepts:

| # | Entity Type Name | Description | Source Table | Key Property | Key Type |
|---|-----------------|-------------|-------------|--------------|----------|
| 1 | | | | | String / Integer |
| 2 | | | | | String / Integer |
| 3 | | | | | String / Integer |
| 4 | | | | | String / Integer |
| 5 | | | | | String / Integer |

---

## Properties per Entity Type

### Entity Type 1: _______________

| Property Name | Source Column | Data Type | Binding Type | Notes |
|--------------|-------------|-----------|-------------|-------|
| | | String / Integer / Double / Boolean / DateTime | Static / Time Series | |
| | | | | |
| | | | | |

### Entity Type 2: _______________

| Property Name | Source Column | Data Type | Binding Type | Notes |
|--------------|-------------|-----------|-------------|-------|
| | | | | |
| | | | | |

### Entity Type 3: _______________

| Property Name | Source Column | Data Type | Binding Type | Notes |
|--------------|-------------|-----------|-------------|-------|
| | | | | |
| | | | | |

*(Copy for additional entity types)*

---

## Relationship Types

| # | Relationship Name | Source Entity | Target Entity | Linking Table | Source Key Column | Target Key Column |
|---|------------------|--------------|---------------|---------------|-------------------|-------------------|
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |

---

## Data Sources

| Source Type | Location (Workspace/Item) | Tables Used | Notes |
|-----------|--------------------------|-------------|-------|
| Lakehouse | | | Static data |
| Eventhouse | | | Time series data |
| Semantic Model | | | (For generation) |

---

## AI Agent Integration

| Setting | Value |
|---------|-------|
| Create data agent? | Yes / No |
| Agent name | |
| Custom instructions | |
| Operations agent? | Yes / No |

---

## Checklist

- [ ] Entity type names follow naming rules (1-26 chars, alphanumeric + hyphens + underscores)
- [ ] No GQL reserved words used as entity type names
- [ ] Each entity type has a unique key property defined
- [ ] Property names are unique across entity types for the same data type
- [ ] All source data is in managed lakehouse tables (no OneLake security, no column mapping)
- [ ] Time series data is in columnar format
- [ ] Relationship source/target entity types are always different
- [ ] Linking tables contain key columns for both source and target entities
- [ ] Tenant settings are enabled (run Validate-FabricIQPrereqs.ps1)
