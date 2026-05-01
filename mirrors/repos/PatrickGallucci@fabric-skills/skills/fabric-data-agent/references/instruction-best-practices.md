# Instruction Best Practices for Fabric Data Agents

Effective instructions are the single biggest lever for improving data agent accuracy. The Fabric data agent supports up to 15,000 characters of plain English instructions at two levels: agent-level (applies across all data sources) and data-source-level (scoped to a specific dataset).

## Where to Place Instructions

**Agent-level instructions** — Use for definitions and rules that apply across all data sources and queries. Examples: what a "quarter" represents, how fiscal year maps to calendar year, general response formatting.

**Data source instructions** — Use for definitions specific to how a term is used within a particular dataset. Example: "sales" might mean something different in the CRM lakehouse versus the finance warehouse.

## Writing Effective Instructions

### 1. Define Ambiguous and Domain-Specific Terms

Terms that may be ambiguous, organization-specific, or domain-specific should be explicitly defined. These definitions help the agent apply consistent logic and generate accurate responses when user questions reference internal terminology.

**Examples of what to define:**

- Similar concepts: `"calendar year"` vs. `"fiscal year"`
- Common business terms: `"quarter"`, `"sales"`, `"SKU"`, `"shoes"`
- Abbreviations or acronyms: `"NPS"` (Net Promoter Score), `"MAU"` (Monthly Active Users)

**Example instruction:**

```text
"Quarter" always refers to fiscal quarter. Our fiscal year starts in July:
- Q1 = July-September
- Q2 = October-December
- Q3 = January-March
- Q4 = April-June

"Active customer" means a customer with at least one transaction in the last 90 days.
```

### 2. Use Leading Words to Nudge Query Generation

Include hints or fragments of SQL/DAX/KQL syntax within data source instructions to guide the model toward generating queries in a specific format.

**Less effective:**
```text
Find all the products with names containing "bike".
```

**Better:**
```text
Find all the products with names containing "bike"
LIKE '%bike%'
```

Including syntax fragments like `LIKE '%...%'` helps the model recognize that a pattern-matching clause is expected. This improves accuracy especially when handling partial matches, filters, or joins.

### 3. Specify Data Source Routing

When the agent has multiple data sources, instruct it which source to use for which type of question:

```text
For financial metrics and revenue queries, use the PowerBI_FinanceModel semantic model.
For raw transactional data and customer-level analysis, use the SalesLakehouse.
For operational monitoring and real-time metrics, use the OpsKQLDatabase.
```

### 4. Write Clear, Focused Instructions — Avoid Unnecessary Detail

Instructions should be concise and purposeful. Include only the information needed to help the agent generate accurate responses. Avoid vague, outdated, or overly broad content that could confuse the model or dilute effective guidance.

**Less effective:**
```text
We have a lot of data in our systems. Sales data is important for the company. 
Try to be accurate. Our data comes from many sources over the years.
```

**Better:**
```text
The "revenue" column in the Sales table represents net revenue after returns.
When calculating total revenue, always exclude rows where OrderStatus = 'Cancelled'.
```

### 5. Handle Common Misinterpretations

If the agent consistently gets certain queries wrong, add explicit correction instructions:

```text
When asked about "employee count" or "headcount", use the HR.ActiveEmployees view,
not the HR.AllEmployees table which includes terminated employees.

"Last month" means the most recently completed calendar month, not the last 30 days.
```

### 6. Set Response Formatting Expectations

```text
When returning financial figures, always format as currency with two decimal places.
When asked about trends, include the comparison period (e.g., month-over-month, year-over-year).
Limit result sets to 50 rows unless the user explicitly asks for more.
```

## Anti-Patterns to Avoid

| Anti-Pattern | Why It Hurts | Better Approach |
|-------------|-------------|----------------|
| Overly long, essay-style instructions | Dilutes key guidance in noise | Use concise, specific statements |
| Repeating the same instruction | Wastes character budget | State each rule once, clearly |
| Vague instructions like "be accurate" | Not actionable for the model | Specify exact columns, tables, conditions |
| Including outdated schema references | Causes query failures | Keep instructions in sync with actual schema |
| Instructing the agent to modify data | Not supported — agent is read-only | Focus on query and retrieval patterns |
