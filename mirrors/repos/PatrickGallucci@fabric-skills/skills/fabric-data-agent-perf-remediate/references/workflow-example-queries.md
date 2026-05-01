# Workflow: Example Query Validation

## Table of Contents

- [How Example Queries Work](#how-example-queries-work)
- [Validation Rules](#validation-rules)
- [Common Validation Failures](#common-validation-failures)
- [Writing Effective Example Queries](#writing-effective-example-queries)
- [Testing Queries](#testing-queries)

## How Example Queries Work

Example queries (also called few-shot examples) are pairs of natural language questions and
corresponding SQL/KQL/DAX queries. When a data source is used, the agent:

1. Receives the user's question.
2. Searches example queries for the most relevant matches.
3. Passes the top 3 examples into the query generation context.
4. Generates a new query informed by these examples.

**Critical:** Only queries that have completed validation are used. Queries that fail validation
are silently ignored — the agent will not tell you they were skipped.

## Validation Rules

The Fabric Data Agent validates example queries against two criteria:

1. **Syntax validity** — The query must be valid SQL, KQL, or DAX syntax.
2. **Schema match** — All referenced tables and columns must exist in the data source schema.

If either check fails, the query is excluded from the agent's example pool.

## Common Validation Failures

| Failure | Cause | Fix |
|---------|-------|-----|
| Table not found | Typo in table name or table removed | Correct table name, refresh schema |
| Column not found | Column renamed or dropped | Update column references |
| Syntax error | Missing comma, unmatched parentheses | Fix SQL/KQL syntax |
| Schema mismatch | Query written for old schema version | Rewrite against current schema |
| Wrong query language | SQL used on KQL data source or vice versa | Match language to data source type |

## Writing Effective Example Queries

### Structure

Each example query consists of:
- **Question** (max 500 characters) — Natural language question the user might ask
- **SQL query** (max 1000 characters) — The correct query to answer that question

### Best Practices

**Do:**
- Cover the most common question types for each data source
- Use fully qualified column names when tables have ambiguous columns
- Include JOIN patterns that the agent should follow
- Show aggregation patterns (GROUP BY, COUNT, SUM, AVG)
- Demonstrate date filtering patterns used in your data
- Include WHERE clause patterns for common filters

**Don't:**
- Write overly complex queries that combine too many operations
- Use database-specific functions that may not be recognized
- Reference views or stored procedures (use base tables)
- Include comments in the SQL (can cause validation issues)
- Exceed the character limits (500 for question, 1000 for query)

### Example Pairs

**Question:** Which players might churn?
```sql
SELECT a.accountID, p.firstName, p.lastName
FROM Accounts a
JOIN Players p ON a.accountID = p.accountID
WHERE a.churnRisk = 'High'
```

**Question:** Who are the top 10 players by total hours for The Lord of the Rings?
```sql
SELECT TOP 10 p.customerID, p.firstName, p.lastName, SUM(s.totalHours) AS TotalHours
FROM Players p
JOIN Sessions s ON p.customerID = s.customerID
JOIN Games g ON s.gameID = g.gameID
WHERE g.gameName = 'The Lord of the Rings: The Two Towers'
GROUP BY p.customerID, p.firstName, p.lastName
ORDER BY TotalHours DESC
```

## Testing Queries

### Manual Validation in Portal

1. Navigate to the Data Agent > **Setup** tab.
2. Select the data source > **Example queries**.
3. Each query shows a validation status indicator.
4. Queries without a green checkmark are not being used.

### Automated Validation with Script

Use the [Test-ExampleQueries.ps1](../scripts/Test-ExampleQueries.ps1) script to validate
all example queries against the current schema programmatically.

### Validation Checklist

- [ ] Every example query has both a question and SQL/KQL query
- [ ] All table names exist in the current data source schema
- [ ] All column names exist in the referenced tables
- [ ] SQL/KQL syntax is valid (no missing commas, unmatched brackets)
- [ ] Query language matches the data source type (SQL for Lakehouse, KQL for Kusto)
- [ ] No queries exceed character limits (500/1000)
- [ ] Queries cover the most common user question patterns
- [ ] Each data source has at least 3-5 validated example queries
