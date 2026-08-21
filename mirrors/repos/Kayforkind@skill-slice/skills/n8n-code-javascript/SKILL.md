---
name: n8n-code-javascript
description: "Writes JavaScript in n8n Code nodes: $input.all/$json/$node, $helpers.httpRequest, DateTime/Luxon, $jmespath, and All Items vs Each Item modes. Use when transforming items, calling HTTP from a Code node, or troubleshooting Code node errors. Not for {{ }} expression fields (n8n-expression-syntax) or Python Code nodes (n8n-code-python)."
version: 1.0.1
risk: unknown
source: community
---

## When to Use

Use this skill when writing JavaScript in n8n Code nodes, specifically when:
- Performing complex transformations requiring multiple steps.
- Implementing custom calculations or business logic.
- Parsing API responses with complex structures.
- Aggregating data across multiple items.
- Using `$input`, `$json`, or `$node` syntax.
- Making HTTP requests with `$helpers.httpRequest()`.
- Working with dates using `DateTime` (Luxon).
- Troubleshooting Code node errors or choosing between Code node modes.

**Trigger keywords:** n8n, Code node, JavaScript, `$input`, `$json`, `$node`, `$helpers`, `DateTime`, Luxon, `$jmespath`.

## Prerequisites

- Access to an n8n instance.
- Basic understanding of JavaScript (ES6+).
- Data-access, aggregation, error, and built-in-function patterns are in Procedure and Pitfalls of this file.

## Procedure

### 1. Choose Execution Mode

The Code node offers two execution modes. Choose based on your use case:

- **Run Once for All Items (Recommended - Default):** Code executes once regardless of input count. Use `$input.all()` or `items` array. Best for 95% of use cases: aggregation, filtering, batch processing, transformations.
  ```javascript
  const allItems = $input.all();
  const total = allItems.reduce((sum, item) => sum + (item.json.amount || 0), 0);
  return [{ json: { total, count: allItems.length } }];
  ```
- **Run Once for Each Item:** Code executes separately for each input item. Use `$input.item` or `$item`. Best for item-specific logic or independent operations.
  ```javascript
  const item = $input.item;
  return [{ json: { ...item.json, processed: true } }];
  ```

**Decision Shortcut:**
- Need to look at multiple items? → Use "All Items" mode.
- Each item completely independent? → Use "Each Item" mode.
- Not sure? → Use "All Items" mode (you can always loop inside).

### 2. Access Input Data

- **Pattern 1: `$input.all()`** - Most common. Use for processing arrays, batch operations, aggregations.
  ```javascript
  const allItems = $input.all();
  const valid = allItems.filter(item => item.json.status === 'active');
  return valid.map(item => ({ json: { id: item.json.id } }));
  ```
- **Pattern 2: `$input.first()`** - Very common. Use for single objects, API responses.
  ```javascript
  const firstItem = $input.first();
  return [{ json: { result: firstItem.json } }];
  ```
- **Pattern 3: `$input.item`** - Each Item mode only.
  ```javascript
  const currentItem = $input.item;
  return [{ json: { ...currentItem.json, itemProcessed: true } }];
  ```
- **Pattern 4: `$node`** - Reference other nodes in the workflow.
  ```javascript
  const webhookData = $node["Webhook"].json;
  return [{ json: { webhook: webhookData } }];
  ```

### 3. Implement Business Logic

Use built-in functions and helpers as needed:

- **`$helpers.httpRequest()`**: Make HTTP requests from within code.
  ```javascript
  const response = await $helpers.httpRequest({
    method: 'GET',
    url: 'https://api.example.com/data',
    headers: { 'Authorization': 'Bearer YOUR_KEY' }
  });
  return [{ json: { data: response } }];
  ```
- **`DateTime` (Luxon)**: Date and time operations.
  ```javascript
  const now = DateTime.now();
  const tomorrow = now.plus({ days: 1 });
  return [{ json: { today: now.toFormat('yyyy-MM-dd'), tomorrow: tomorrow.toFormat('yyyy-MM-dd') } }];
  ```
- **`$jmespath()`**: Query JSON structures.
  ```javascript
  const data = $input.first().json;
  const adults = $jmespath(data, 'users[?age >= `18`]');
  return [{ json: { adults } }];
  ```

### 4. Return Data in Correct Format

**CRITICAL RULE**: Always return an array of objects with a `json` property.

```javascript
// ✅ Single result
return [{ json: { field1: value1 } }];

// ✅ Multiple results
return [{ json: { id: 1 } }, { json: { id: 2 } }];

// ✅ Empty result
return [];
```

## Pitfalls

### #1: Empty Code or Missing Return (Most Common)
Code must always return data. If you process items but forget the `return` statement, the node will fail.
```javascript
// ❌ WRONG: No return statement
const items = $input.all();
// ... processing code ...

// ✅ CORRECT: Always return data
const items = $input.all();
return items.map(item => ({ json: item.json }));
```

### #2: Incorrect Return Wrapper
Returning an object instead of an array, or an array without the `json` wrapper, will cause execution failure.
```javascript
// ❌ WRONG: Returning object instead of array
return { json: { result: 'success' } };

// ❌ WRONG: Array without json wrapper
return [{ result: 'success' }];

// ✅ CORRECT: Array wrapper required
return [{ json: { result: 'success' } }];
```

### #3: Webhook Data Structure
Webhook data is nested under `.body`. Accessing `$json.email` directly will return `undefined`.
```javascript
// ❌ WRONG: Direct access to webhook data
const email = $json.email;

// ✅ CORRECT: Webhook data under .body
const email = $json.body.email;
```

### #4: Expression Syntax Confusion
Do not use n8n expression syntax (`{{ }}`) inside Code nodes. Use JavaScript template literals.
```javascript
// ❌ WRONG: Using n8n expression syntax in code
const value = "{{ $json.field }}";

// ✅ CORRECT: Use JavaScript template literals
const value = `${$json.field}`;
```

### #5: Missing Null Checks
Crashes occur if fields don't exist. Use optional chaining or guard clauses.
```javascript
// ❌ WRONG: Crashes if field doesn't exist
const value = item.json.user.email;

// ✅ CORRECT: Safe access with optional chaining
const value = item.json?.user?.email || 'no-email@example.com';
```

## Verification

Before deploying Code nodes, verify the following checklist:

1. **Return statement exists**: Ensure the code explicitly returns an array of objects.
2. **Proper return format**: Each item must be structured as `{json: {...}}`.
3. **Data access correct**: Confirm usage of `$input.all()`, `$input.first()`, or `$input.item` based on the selected mode.
4. **No n8n expressions**: Ensure no `{{ }}` syntax is present; use JS template literals.
5. **Error handling**: Verify guard clauses for null/undefined inputs.
6. **Webhook data**: If data comes from a Webhook node, ensure access via `.body`.
7. **Mode selection**: Confirm "All Items" is selected for most cases.
8. **Output consistency**: Ensure all code paths (including error branches) return the same structure.

**Debugging:**
Use `console.log()` to output debug statements to the browser console.
```javascript
const items = $input.all();
console.log(`Processing ${items.length} items`);
```

## Related skills

- **n8n Expression Syntax**: For using `{{ }}` syntax in other nodes.
- **n8n MCP Tools Expert**: For finding nodes (`search_nodes`) and validating operations.
- **n8n Node Configuration**: For mode selection and property dependencies.
- **n8n Workflow Patterns**: For integrating Code nodes into larger workflows.
- **n8n Validation Expert**: For validating Code node configuration and auto-fixing issues.
