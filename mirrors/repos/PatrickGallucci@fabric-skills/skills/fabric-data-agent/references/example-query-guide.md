# Example Query Guide for Fabric Data Agents

Example queries (also called "few-shot examples") give the Data Agent concrete patterns to learn from. They are sample questions and their corresponding query logic that guide how the agent should respond. The Data Agent automatically retrieves the most relevant examples — typically the top four — and feeds them into its generation process.

## Supported Data Sources for Example Queries

| Data Source | Example Queries Supported | Query Language |
|-------------|--------------------------|----------------|
| Lakehouse | Yes | T-SQL |
| Warehouse | Yes | T-SQL |
| KQL Database | Yes | KQL |
| Power BI Semantic Model | No (not yet supported) | — |
| Ontology | No (not yet supported) | — |

## Structure of an Example Query

Each example query consists of two parts:

1. **Question** (max 500 characters) — A natural language question as a user would ask it
2. **SQL/KQL query** (max 1,000 characters) — The corresponding query that answers the question

Every example query is validated against the schema of the selected data source. Queries that don't pass validation aren't sent to the agent.

## Writing Effective Examples

### 1. Cover Diverse Query Patterns

Provide examples that cover different query structures and operations:

```text
Question: What were total sales last quarter?
SQL query:
SELECT SUM(Amount) AS TotalSales
FROM dbo.SalesTransactions
WHERE OrderDate >= DATEADD(QUARTER, -1, DATEADD(QUARTER, DATEDIFF(QUARTER, 0, GETDATE()), 0))
  AND OrderDate < DATEADD(QUARTER, DATEDIFF(QUARTER, 0, GETDATE()), 0)
```

```text
Question: Which customers placed more than 10 orders this year?
SQL query:
SELECT c.CustomerName, COUNT(o.OrderID) AS OrderCount
FROM dbo.Customers c
INNER JOIN dbo.Orders o ON c.CustomerID = o.CustomerID
WHERE YEAR(o.OrderDate) = YEAR(GETDATE())
GROUP BY c.CustomerName
HAVING COUNT(o.OrderID) > 10
ORDER BY OrderCount DESC
```

```text
Question: What are the top 5 products by revenue?
SQL query:
SELECT TOP 5 p.ProductName, SUM(s.Revenue) AS TotalRevenue
FROM dbo.Products p
INNER JOIN dbo.Sales s ON p.ProductID = s.ProductID
GROUP BY p.ProductName
ORDER BY TotalRevenue DESC
```

### 2. Include Business Logic in Examples

Show the agent how your organization interprets specific business concepts:

```text
Question: How many active customers do we have?
SQL query:
SELECT COUNT(DISTINCT CustomerID) AS ActiveCustomers
FROM dbo.Orders
WHERE OrderDate >= DATEADD(DAY, -90, GETDATE())
  AND OrderStatus <> 'Cancelled'
```

### 3. Demonstrate Join Patterns for Your Schema

If your schema uses specific join relationships, show them:

```text
Question: What is the average order value by region?
SQL query:
SELECT r.RegionName, AVG(o.TotalAmount) AS AvgOrderValue
FROM dbo.Orders o
INNER JOIN dbo.Customers c ON o.CustomerID = c.CustomerID
INNER JOIN dbo.Regions r ON c.RegionID = r.RegionID
GROUP BY r.RegionName
ORDER BY AvgOrderValue DESC
```

### 4. KQL Examples for KQL Database Sources

```text
Question: How many errors occurred in the last 24 hours?
KQL query:
AppEvents
| where TimeGenerated > ago(24h)
| where EventLevel == "Error"
| summarize ErrorCount = count()
```

```text
Question: What are the top 10 slowest API endpoints this week?
KQL query:
ApiRequests
| where Timestamp > ago(7d)
| summarize AvgDuration = avg(DurationMs) by Endpoint
| top 10 by AvgDuration desc
```

## Validation Checklist

Before saving example queries, verify each one:

- [ ] SQL/KQL syntax is valid and executable
- [ ] All table and column names match the actual schema
- [ ] The query returns results that correctly answer the question
- [ ] The question is phrased as a user would naturally ask it
- [ ] Each question is unique — don't duplicate similar questions
- [ ] Complex joins reference the correct foreign key relationships

## Importing and Exporting Examples

The Fabric data agent supports bulk operations through the UI:

- **Import from JSON** — Upload a JSON file with question/query pairs
- **Export all** — Download all examples as JSON for backup or migration
- **Add** — Create individual examples one at a time

## Tips for Maximum Impact

A diverse set of 5-10 well-crafted examples per data source typically provides the best balance of coverage without overwhelming the retrieval mechanism. Focus on the types of questions your users ask most frequently, and on query patterns where the agent's default performance needs adjustment.
