# Workflow: Data Source Configuration Issues

## Table of Contents

- [Three Configuration Layers](#three-configuration-layers)
- [Diagnosing Routing Problems](#diagnosing-routing-problems)
- [Writing Effective Agent Instructions](#writing-effective-agent-instructions)
- [Writing Data Source Instructions](#writing-data-source-instructions)
- [Data Source Refresh](#data-source-refresh)

## Three Configuration Layers

Fabric Data Agents use a layered configuration model. All three layers must be correctly
configured for accurate query generation:

### Layer 1: Agent Instructions (Global Routing)

- **Purpose:** Guide the agent to the best data source for each topic
- **Location:** Agent Instructions pane in the Fabric portal
- **Format:** Markdown
- **Scope:** Applies across all data sources attached to the agent

**Template:**
```markdown
# Objective
You are a virtual data analyst that helps [audience] answer questions about [domain].

## When asked about
1. When asked about **sales**, use the "SalesLakehouse" data source.
2. When asked about **customer profiles**, use "CustomerDB".
3. When asked about **support tickets**, use the DailySupport database.

## Procedures
*0. NEVER change the [entity] provided by the user when restating the question.*
1. When a user asks for a "[entity] profile", do the following steps in order:
   - Use **CustomerDB** and the [entity] name to answer: ...
```

### Layer 2: Data Source Instructions (Schema Context)

- **Purpose:** Provide schema-specific context for each data source
- **Location:** Data source instructions within each attached data source
- **Format:** Markdown
- **Scope:** Applied when the agent routes a question to that specific data source

**Template:**
```markdown
## General knowledge
// Background information the agent should consider for this data source.

## Table descriptions
// Describe key tables and important columns within those tables.

## When asked about
// Provide query-specific logic or table preferences for certain topics.
```

### Layer 3: Example Queries (Few-Shot Learning)

- **Purpose:** Teach the agent correct SQL/KQL/DAX patterns via examples
- **Location:** Example queries tab for each data source
- **Scope:** Top 3 most relevant examples are injected into query generation

See [workflow-example-queries.md](./workflow-example-queries.md) for detailed guidance.

## Diagnosing Routing Problems

**Symptom:** Agent queries the wrong data source for a given question.

**Diagnostic steps:**

1. Open the **Test your agent** panel in the Fabric portal.
2. Ask the question that produces incorrect results.
3. Observe which data source the agent selected (shown in the response metadata).
4. Compare against your Agent Instructions routing rules.
5. If the routing is wrong, update the `## When asked about` section with clearer rules.

**Common mistakes:**
- Ambiguous keywords that match multiple data sources
- Missing routing rules for edge-case topics
- Overly generic instructions that don't disambiguate sources

## Writing Effective Agent Instructions

**Do:**
- Use numbered rules with explicit data source names in bold
- Include specific keywords that trigger each routing rule
- Define procedures for multi-step queries (e.g., "first get X, then lookup Y")
- Include a catch-all rule for unrouted questions

**Don't:**
- Write vague instructions like "use the appropriate data source"
- Assume the agent knows your business domain without explicit guidance
- Skip edge cases that span multiple data sources

## Writing Data Source Instructions

**Do:**
- Describe every table the agent might query
- List important columns with data types and business meaning
- Specify join relationships between tables
- Note any columns with encoded values (explain the encoding)
- Mention date/time column formats

**Don't:**
- Assume the agent can infer column meanings from names alone
- Skip tables that seem obvious
- Forget to mention partitioning or filtering columns

**Example:**
```markdown
## Table descriptions
The **Orders** table contains all customer orders. Key columns:
- `OrderID` (INT) — Primary key
- `CustomerID` (INT) — Foreign key to Customers.CustomerID
- `OrderDate` (DATETIME) — UTC timestamp of order placement
- `Status` (VARCHAR) — Values: 'Pending', 'Shipped', 'Delivered', 'Cancelled'
- `TotalAmount` (DECIMAL) — Order total in USD

## When asked about
- **Order volume**: Use `Orders` table, group by `OrderDate`
- **Customer orders**: JOIN `Orders` with `Customers` on `CustomerID`
```

## Data Source Refresh

The Data Agent uses metadata (description, schema, example queries) to determine which
data source to use. When you update data sources:

1. Right-click the data source in the Explorer pane.
2. Select **Refresh** to sync the latest schema.
3. Verify that table names and columns are current.
4. Update data source instructions if the schema has changed.
5. Re-validate example queries against the updated schema.

**Note:** The agent also considers metadata such as description, schema, and example queries
to determine which data source to use for a particular question.
