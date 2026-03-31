# Common Hidden Errors

> A catalog of errors that **pass surface inspection** but cause problems. These are the pernicious bugs that look correct at a glance.

## Code Errors That Look Correct

### 1. The Silent Swallow

**What it looks like**: Proper error handling
**What it does**: Hides failures

```javascript
// Looks like good error handling:
try {
  await riskyOperation();
} catch (error) {
  logger.error("Operation failed:", error);
}
// Continues happily...

// Hidden problem: Failure is logged but not propagated.
// Caller thinks it succeeded.
```

**Why it's hidden**: The code looks defensive and responsible.

**How to catch**: Ask "What does the caller see when this fails?"

---

### 2. The Optimistic Parse

**What it looks like**: Parsing input data
**What it does**: Assumes format is always correct

```javascript
// Looks reasonable:
const [name, email] = line.split(",");
user.name = name;
user.email = email;

// Hidden problem: If line has no comma, email is undefined.
// If line has extra commas, email contains garbage.
```

**Why it's hidden**: Works perfectly for well-formed input.

**How to catch**: Ask "What if the input isn't what we expect?"

---

### 3. The Friendly Default

**What it looks like**: Providing sensible defaults
**What it does**: Masks missing required data

```javascript
// Looks helpful:
const config = {
  timeout: options.timeout || 30000,
  retries: options.retries || 3,
  apiKey: options.apiKey || process.env.API_KEY || "",
};

// Hidden problem: If API key is genuinely missing, we continue
// with empty string instead of failing fast.
```

**Why it's hidden**: Code appears to handle all cases gracefully.

**How to catch**: Ask "Should this really have a default, or should it fail?"

---

### 4. The Almost-Atomic Operation

**What it looks like**: Transactional operation
**What it does**: Can leave partial state on failure

```javascript
// Looks transactional:
async function transferFunds(from, to, amount) {
  await debit(from, amount);
  await credit(to, amount);
}

// Hidden problem: If credit() fails after debit() succeeds,
// money has vanished.
```

**Why it's hidden**: Code structure implies atomicity.

**How to catch**: Ask "What if this fails halfway through?"

---

### 5. The Truthiness Trap

**What it looks like**: Checking if value exists
**What it does**: Treats valid values as missing

```javascript
// Looks like good null checking:
function process(value) {
  if (!value) {
    return defaultBehavior();
  }
  return doSomething(value);
}

// Hidden problem: If value is 0, '', or false, those valid
// inputs get treated as missing.
```

**Why it's hidden**: Works for most inputs.

**How to catch**: Ask "What if the value is zero, empty string, or false?"

---

### 6. The Shallow Clone

**What it looks like**: Making a safe copy
**What it does**: Shares nested references

```javascript
// Looks like we're being careful:
const safeCopy = { ...original };
safeCopy.nested.value = "changed";

// Hidden problem: original.nested.value is also 'changed'
// because nested objects are not cloned.
```

**Why it's hidden**: Top-level properties are independent.

**How to catch**: Ask "What about nested objects?"

---

### 7. The Async Fire-and-Forget

**What it looks like**: Kicking off background work
**What it does**: Loses errors and results

```javascript
// Looks like background processing:
function handleRequest(data) {
  processAsync(data); // Note: no await
  return { status: "accepted" };
}

// Hidden problem: If processAsync throws, nobody knows.
// We returned success but work might have failed.
```

**Why it's hidden**: Code runs, response is sent.

**How to catch**: Ask "Where do errors from this async call go?"

---

### 8. The Floating Point Trap

**What it looks like**: Normal arithmetic
**What it does**: Accumulates precision errors

```javascript
// Looks like simple math:
let total = 0;
for (const item of items) {
  total += item.price;
}

// Hidden problem: 0.1 + 0.2 = 0.30000000000000004
// Financial calculations drift over many operations.
```

**Why it's hidden**: Works fine for small numbers, few operations.

**How to catch**: Ask "Is floating point precision acceptable here?"

---

### 9. The Timing Assumption

**What it looks like**: Sequential operations
**What it does**: Races with concurrent activity

```javascript
// Looks sequential:
const exists = await fileExists(path);
if (exists) {
  await processFile(path);
}

// Hidden problem: File could be deleted between check and use
// (TOCTOU: time-of-check to time-of-use)
```

**Why it's hidden**: Works in testing where nothing else is happening.

**How to catch**: Ask "What if something changes between these operations?"

---

### 10. The Magic Index

**What it looks like**: Array access
**What it does**: Assumes array has expected length

```javascript
// Looks reasonable:
const firstName = parts[0];
const lastName = parts[1];
const middleName = parts[2] || "";

// Hidden problem: If parts has only one element,
// lastName is undefined (not '').
```

**Why it's hidden**: Works when array has expected elements.

**How to catch**: Ask "What if the array is shorter than expected?"

---

## Analysis Errors That Look Correct

### 11. The Double-Count Join

**What it looks like**: Combining related data
**What it does**: Inflates metrics

```sql
-- Looks like getting order totals:
SELECT SUM(order_value)
FROM orders
JOIN order_items ON orders.id = order_items.order_id

-- Hidden problem: If orders have multiple items,
-- order_value is summed once per item.
```

**Why it's hidden**: Query syntax is correct, results seem plausible.

**How to catch**: Ask "Does this join change the cardinality?"

---

### 12. The Survivorship Bias

**What it looks like**: Analyzing successful cases
**What it does**: Ignores failures that would change conclusions

```
Analysis: "Companies that adopted X grew 20% faster"

-- Hidden problem: Only looked at companies still in business.
-- Companies that adopted X and failed are not in the data.
```

**Why it's hidden**: Data appears comprehensive.

**How to catch**: Ask "What's missing from this dataset?"

---

### 13. The Aggregation Mixup

**What it looks like**: Summary statistics
**What it does**: Computes wrong measure

```sql
-- Looks like average order value:
SELECT AVG(total) as avg_order_value
FROM orders
WHERE total > 0

-- Hidden problem: Excludes $0 orders, inflating the average.
-- If trying to understand "average order", zeros matter.
```

**Why it's hidden**: Query runs, produces a number.

**How to catch**: Ask "Should this filter be applied before or after aggregation?"

---

### 14. The Correlation Causation

**What it looks like**: Identifying drivers
**What it does**: Confuses correlation with cause

```
Finding: "Users who complete onboarding have 3x retention"
Recommendation: "Force all users through onboarding"

-- Hidden problem: Causation might be reversed.
-- Users who were going to retain anyway complete onboarding.
```

**Why it's hidden**: The correlation is real.

**How to catch**: Ask "Could the causation run the other direction?"

---

### 15. The Missing Denominator

**What it looks like**: Percentage or rate
**What it does**: Uses wrong base for comparison

```
Metric: "Conversion rate increased 50%"

-- Hidden problem: Went from 2% to 3%.
-- Sounds impressive but actual impact is 1 percentage point.
```

**Why it's hidden**: Percentage increase is mathematically correct.

**How to catch**: Ask "50% of what? What are the absolute numbers?"

---

## Architecture Errors That Look Correct

### 16. The Implicit Order Dependency

**What it looks like**: Independent components
**What it does**: Only works if initialized in specific order

```javascript
// Looks modular:
await initializeDatabase();
await initializeCache();
await initializeAPI();

// Hidden problem: Cache reads from database config.
// If order changes, cache uses stale or missing config.
```

**Why it's hidden**: Works when initialized in original order.

**How to catch**: Ask "What if these ran in different order?"

---

### 17. The Optimistic Retry

**What it looks like**: Resilient error handling
**What it does**: Masks persistent failures

```javascript
// Looks robust:
async function reliableCall() {
  for (let i = 0; i < 5; i++) {
    try {
      return await makeCall();
    } catch (e) {
      await sleep(1000 * i);
    }
  }
  return null; // Give up silently
}

// Hidden problem: Returns null for both "succeeded" and
// "failed 5 times". Caller can't distinguish.
```

**Why it's hidden**: Handles transient failures well.

**How to catch**: Ask "How does the caller know if this eventually succeeded?"

---

### 18. The Infinite Growth

**What it looks like**: Efficient caching
**What it does**: Memory grows without bound

```javascript
// Looks like smart caching:
const cache = {};
function getCached(key) {
  if (!cache[key]) {
    cache[key] = expensiveCompute(key);
  }
  return cache[key];
}

// Hidden problem: Cache never evicts.
// Over time, memory grows until crash.
```

**Why it's hidden**: Works great until it doesn't.

**How to catch**: Ask "What's the maximum size of this?"

---

### 19. The Missing Timeout

**What it looks like**: Making external call
**What it does**: Can hang forever

```javascript
// Looks normal:
const response = await fetch(url);

// Hidden problem: If server never responds,
// this waits forever, blocking everything.
```

**Why it's hidden**: Works when external service responds.

**How to catch**: Ask "What if this never completes?"

---

### 20. The Config That Works In Dev

**What it looks like**: Configuration management
**What it does**: Uses dev-only defaults in production

```javascript
// Looks reasonable:
const config = {
  database: process.env.DATABASE_URL || "localhost:5432",
  apiEndpoint: process.env.API_URL || "http://localhost:3000",
};

// Hidden problem: If env vars aren't set in production,
// code silently uses localhost and appears to work but
// connects to nothing real.
```

**Why it's hidden**: Works perfectly in development.

**How to catch**: Ask "What if the env var is missing in production?"

---

## How to Use This Catalog

1. **During verification**: Scan for patterns that match
2. **Generate questions**: Each pattern suggests verification questions
3. **Train intuition**: Over time, recognize these patterns faster
4. **Expand it**: Add new patterns when you find them

**Key insight**: These errors persist because they pass basic testing. They fail at boundaries, under load, or in production—exactly when it matters most.
