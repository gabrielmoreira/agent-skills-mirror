# Query remediate

Diagnose and resolve issues where the Fabric Data Agent generates incorrect, empty, or failing SQL, DAX, or KQL queries.

## How Query Generation Works

Understanding the pipeline helps isolate where failures occur:

1. **User asks question** → natural language input
2. **Schema access** → agent reads data source schema using user credentials
3. **Prompt construction** → combines question + schema + instructions + example queries
4. **Tool selection** → agent picks NL2SQL, NL2DAX, or NL2KQL based on data source type
5. **Query generation** → tool creates structured query from the prompt
6. **Query validation** → tool validates syntax and security compliance
7. **Query execution** → runs against data source with user permissions
8. **Response formatting** → results returned in conversational format

## Issue: Agent Returns Wrong or Irrelevant Results

### Check Table and Column Names

The AI relies heavily on descriptive names. Ambiguous names cause misinterpretation.

| Bad Name | Better Name | Why |
|----------|------------|-----|
| `TableA` | `SalesTransactions` | Describes content |
| `C1` | `CustomerEmail` | Self-documenting |
| `ActCu` | `IsActiveCustomer` | Clear boolean intent |
| `Val` | `OrderTotalAmount` | Unambiguous numeric field |

**Action**: Rename tables and columns to be self-describing. The agent uses names as its primary signal for understanding data structure.

### Check Agent Instructions

Navigate to the agent and select **Data agent instructions** to review:

- Are instructions clear about which data source to use for which question types?
- Have you defined domain-specific terms, acronyms, or business jargon?
- Are instructions in English? (Non-English is not supported)
- Is the instruction text within the 15,000 character limit?

### Check Example Queries

Navigate to **Setup** → select a data source → **Example queries**:

- Each example must have both a natural language **Question** and a valid **SQL/KQL query**
- Queries must use valid syntax and match the current schema exactly
- Invalid or unvalidated queries are silently ignored by the agent
- Provide diverse examples covering different question patterns
- Maximum 100 example queries per data source

**Validation test**: Copy each example query and run it directly against the data source. If it fails there, the agent will ignore it.

### Check Selected Tables

In the Explorer pane, verify:

- The correct tables are checked (enabled) for each data source
- No essential tables have been accidentally unchecked
- If you recently added tables, click **Refresh** on the data source context menu

## Issue: Agent Returns Empty Results

1. **Data exists?** Run the query manually to confirm rows exist.
2. **Permissions?** The agent uses YOUR credentials. If you cannot query the data directly, neither can the agent.
3. **Schema refresh needed?** If tables or columns were recently changed, right-click the data source → **Refresh**.
4. **Initialization delay?** After creating a new agent, wait 2-3 minutes before querying.

## Issue: Agent Cannot Generate Query at All

### Out-of-Scope Questions

The agent only handles questions translatable to SQL/DAX/KQL reads. These will fail:

- "Why did sales drop?" → requires causal reasoning
- "What is the root cause?" → requires ML/statistical analysis
- "Predict next quarter revenue" → requires forecasting models
- "Update the sales table" → write operations are blocked

### Supported Question Patterns

These patterns work well:

- "What were total sales in California in 2023?"
- "What are the top 5 products by revenue?"
- "How many customers purchased more than 3 items?"
- "Show me all orders from last month"

## Issue: Cross-Region Capacity Error

**Error**: Agent cannot execute queries when data source capacity region differs from agent capacity region.

**Diagnosis**: Check the capacity region for both:
1. The workspace containing the data agent
2. The workspace containing the data source

**Resolution**: Both must be in the same region. Either:
- Move the data agent to a workspace on a capacity in the same region as the data source
- Move the data source to a capacity in the same region as the agent
- Contact your Fabric admin to align capacity regions

## Issue: Specific Query Language Problems

### NL2SQL (Lakehouse/Warehouse)

- Verify tables are Delta tables (not standalone files)
- Check T-SQL compatibility of your warehouse schema
- Ensure column data types are correct (mistyped columns cause cast errors)

### NL2DAX (Power BI Semantic Models)

- XMLA endpoints must be enabled (see tenant settings)
- User needs Read permission on the semantic model (Write not required)
- Example queries cannot be added for PBI semantic models (current limitation)
- Verify the semantic model is published and accessible

### NL2KQL (KQL Databases)

- Verify the KQL database is accessible in the workspace
- Ensure the Kusto database contains data in the expected tables
- KQL syntax in example queries must match the database schema exactly

## Improving Query Accuracy Checklist

1. Add 5-10 diverse example queries per data source
2. Write clear agent instructions specifying data source routing rules
3. Use descriptive table and column names
4. Define acronyms and business terms in instructions
5. Test queries across different question phrasings
6. Use the "steps" dropdown in responses to see generated queries and debug
7. Evaluate programmatically using the [Fabric Data Agent Python SDK](https://learn.microsoft.com/en-us/fabric/data-science/evaluate-data-agent)
