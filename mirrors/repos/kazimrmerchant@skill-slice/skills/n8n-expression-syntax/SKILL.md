---
name: n8n-expression-syntax
description: "Writes and debugs n8n node-parameter expressions in {{ }} with $json, $node, $now, and $env. Use when fixing n8n expression errors, webhook field mapping, or Luxon date formatting in parameters. Not for n8n Code-node JavaScript (n8n-code-javascript) or Python (n8n-code-python)."
version: 1.0.1
risk: unknown
source: community
---

## Overview
Expert guide for writing correct n8n expressions in workflows. All dynamic content in n8n uses double curly braces: `{{expression}}`.

## When to Use
- You need to write or debug n8n expressions using `{{ ... }}` syntax.
- The task involves `$json`, `$node`, webhook payloads, or expression-related workflow errors.
- You want syntax-correct dynamic values inside n8n nodes and parameters.

## Prerequisites
- Access to an n8n instance or workflow JSON file.
- (Optional) n8n MCP tools for validation.

## Procedure

### 1. Expression Format
All dynamic content in n8n uses **double curly braces**:
```javascript
{{expression}}
```

**Examples**:
```javascript
✅ {{$json.email}}
✅ {{$json.body.name}}
✅ {{$node["HTTP Request"].json.data}}
❌ $json.email  (no braces - treated as literal text)
❌ {$json.email}  (single braces - invalid)
```

### 2. Core Variables

#### $json - Current Node Output
Access data from the current node:
```javascript
{{$json.fieldName}}
{{$json['field with spaces']}}
{{$json.nested.property}}
{{$json.items[0].name}}
```

#### $node - Reference Other Nodes
Access data from any previous node:
```javascript
{{$node["Node Name"].json.fieldName}}
{{$node["HTTP Request"].json.data}}
{{$node["Webhook"].json.body.email}}
```
**Important**:
- Node names **must** be in quotes
- Node names are **case-sensitive**
- Must match exact node name from workflow

#### $now - Current Timestamp
Access current date/time:
```javascript
{{$now}}
{{$now.toFormat('yyyy-MM-dd')}}
{{$now.toFormat('HH:mm:ss')}}
{{$now.plus({days: 7})}}
```

#### $env - Environment Variables
Access environment variables:
```javascript
{{$env.API_KEY}}
{{$env.DATABASE_URL}}
```

### 3. Common Patterns

#### Access Nested Fields
```javascript
// Simple nesting
{{$json.user.email}}

// Array access
{{$json.data[0].name}}
{{$json.items[0].id}}

// Bracket notation for spaces
{{$json['field name']}}
{{$json['user data']['first name']}}
```

#### Combine Variables
```javascript
// Concatenation (automatic)
Hello {{$json.body.name}}!

// In URLs
https://api.example.com/users/{{$json.body.user_id}}

// In object properties
{
  "name": "={{$json.body.name}}",
  "email": "={{$json.body.email}}"
}
```

### 4. Advanced Patterns

#### Conditional Content
```javascript
// Ternary operator
{{$json.status === 'active' ? 'Active User' : 'Inactive User'}}

// Default values
{{$json.email || 'no-email@example.com'}}
```

#### Date Manipulation
```javascript
// Add days
{{$now.plus({days: 7}).toFormat('yyyy-MM-dd')}}

// Subtract hours
{{$now.minus({hours: 24}).toISO()}}

// Set specific date
{{DateTime.fromISO('2025-12-25').toFormat('MMMM dd, yyyy')}}
```

#### String Manipulation
```javascript
// Substring
{{$json.email.substring(0, 5)}}

// Replace
{{$json.message.replace('old', 'new')}}

// Split and join
{{$json.tags.split(',').join(', ')}}
```

### 5. Expression Helpers

**String**:
- `.toLowerCase()`, `.toUpperCase()`
- `.trim()`, `.replace()`, `.substring()`
- `.split()`, `.includes()`

**Array**:
- `.length`, `.map()`, `.filter()`
- `.find()`, `.join()`, `.slice()`

**DateTime** (Luxon):
- `.toFormat()`, `.toISO()`, `.toLocal()`
- `.plus()`, `.minus()`, `.set()`

**Number**:
- `.toFixed()`, `.toString()`
- Math operations: `+`, `-`, `*`, `/`, `%`

## Examples
Webhook, HTTP-to-email, and timestamp examples follow.

### Example 1: Webhook to Slack
**Webhook receives**:
```json
{
  "body": {
    "name": "John Doe",
    "email": "john@example.com",
    "message": "Hello!"
  }
}
```
**In Slack node text field**:
```
New form submission!

Name: {{$json.body.name}}
Email: {{$json.body.email}}
Message: {{$json.body.message}}
```

### Example 2: HTTP Request to Email
**HTTP Request returns**:
```json
{
  "data": {
    "items": [
      {"name": "Product 1", "price": 29.99}
    ]
  }
}
```
**In Email node** (reference HTTP Request):
```
Product: {{$node["HTTP Request"].json.data.items[0].name}}
Price: ${{$node["HTTP Request"].json.data.items[0].price}}
```

### Example 3: Format Timestamp
```javascript
// Current date
{{$now.toFormat('yyyy-MM-dd')}}
// Result: 2025-10-20

// Time
{{$now.toFormat('HH:mm:ss')}}
// Result: 14:30:45

// Full datetime
{{$now.toFormat('yyyy-MM-dd HH:mm')}}
// Result: 2025-10-20 14:30
```

## Pitfalls
Use this section when troubleshooting expression errors.

### 🚨 CRITICAL: Webhook Data Structure
**Most Common Mistake**: Webhook data is **NOT** at the root!
Webhook node wraps incoming data under `.body` property to preserve headers, params, and query parameters.
```javascript
❌ WRONG: {{$json.name}}
❌ WRONG: {{$json.email}}

✅ CORRECT: {{$json.body.name}}
✅ CORRECT: {{$json.body.email}}
✅ CORRECT: {{$json.body.message}}
```

### When NOT to Use Expressions

#### Code Nodes
Code nodes use **direct JavaScript access**, NOT expressions!
```javascript
// ❌ WRONG in Code node
const email = '={{$json.email}}';
const name = '{{$json.body.name}}';

// ✅ CORRECT in Code node
const email = $json.email;
const name = $json.body.name;

// Or using Code node API
const email = $input.item.json.email;
const allItems = $input.all();
```

#### Webhook Paths
```javascript
// ❌ WRONG
path: "{{$json.user_id}}/webhook"

// ✅ CORRECT
path: "user-webhook"  // Static paths only
```

#### Credential Fields
```javascript
// ❌ WRONG
apiKey: "={{$env.API_KEY}}"

// ✅ CORRECT
Use n8n credential system, not expressions
```

### Validation Rules
1. **Always Use {{}}**: Expressions **must** be wrapped in double curly braces.
2. **Use Quotes for Spaces**: Field or node names with spaces require **bracket notation**.
3. **Match Exact Node Names**: Node references are **case-sensitive**.
4. **No Nested {{}}**: Don't double-wrap expressions.

### Quick Fixes
| Mistake | Fix |
|---------|-----|
| `$json.field` | `{{$json.field}}` |
| `{{$json.field name}}` | `{{$json['field name']}}` |
| `{{$node.HTTP Request}}` | `{{$node["HTTP Request"]}}` |
| `{{{$json.field}}}` | `{{$json.field}}` |
| `{{$json.name}}` (webhook) | `{{$json.body.name}}` |
| `'={{$json.email}}'` (Code node) | `$json.email` |

## Verification

### Test in Expression Editor
1. Click field with expression
2. Open expression editor (click "fx" icon)
3. See live preview of result
4. Check for errors highlighted in red

### Common Error Messages
**"Cannot read property 'X' of undefined"**
→ Parent object doesn't exist
→ Check your data path

**"X is not a function"**
→ Trying to call method on non-function
→ Check variable type

**Expression shows as literal text**
→ Missing {{ }}
→ Add curly braces

## Related Skills
- **n8n MCP Tools Expert**: Learn how to validate expressions using MCP tools
- **n8n Workflow Patterns**: See expressions in real workflow examples
- **n8n Node Configuration**: Understand when expressions are needed

## Limitations
- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
