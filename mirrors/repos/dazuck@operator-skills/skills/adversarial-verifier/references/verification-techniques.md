# Verification Techniques

> **Note**: These techniques are for **finding hidden errors**, not for fixing them or assessing quality. The goal is to expose issues that pass surface inspection.

## Code Verification Techniques

### 1. Execution Path Tracing

**Purpose**: Find logic that looks right but branches wrong

**Method**:

1. Pick an input scenario
2. Trace exactly which lines execute
3. Compare actual path to expected path
4. Check: Does it go where the author intended?

**What it catches**:

- Conditions that evaluate opposite to expectation
- Early returns that skip important logic
- Branches that look symmetric but aren't
- Dead code that should be live

**Example**:

```javascript
// Looks correct:
if (user.isAdmin || user.hasPermission("edit")) {
  allowEdit();
}
// But trace with: user = { isAdmin: false, hasPermission: undefined }
// hasPermission is not a function -> throws, never reaches allowEdit OR
// hasPermission returns undefined -> truthy in some contexts
```

### 2. Boundary Analysis

**Purpose**: Find off-by-one errors and boundary condition failures

**Method**:

1. Identify all boundaries (0, 1, -1, max, max+1, empty, full)
2. Trace code with exactly-at-boundary inputs
3. Check behavior at boundary±1

**Critical boundaries to test**:

- Array: index 0, index length-1, index length
- String: empty, single char, very long
- Number: 0, -1, 1, MAX_SAFE_INTEGER, NaN, Infinity
- Collection: empty, single element, many elements
- Time: midnight, end of month, DST transitions, leap years

### 3. State Mutation Tracking

**Purpose**: Find side effects that corrupt data

**Method**:

1. Identify all mutable state (variables, objects, arrays, globals)
2. Track every mutation
3. Check: Is any state modified unexpectedly?
4. Check: Is state read after it's been modified elsewhere?

**What it catches**:

- Functions that mutate their arguments
- Shared references that cause spooky action at a distance
- Caching that serves stale data
- Global state corruption

### 4. Error Path Analysis

**Purpose**: Find errors that are caught and swallowed

**Method**:

1. Find all try/catch blocks
2. Trace what happens in catch block
3. Check: Is the error truly handled or just hidden?
4. Find all error callbacks and check their implementations

**Red flags**:

- `catch (e) { /* empty */ }`
- `catch (e) { console.log(e); }` then continues normally
- `.catch(() => null)` that converts errors to falsy values
- Error handlers that return "success" status

### 5. Type Coercion Traps

**Purpose**: Find implicit conversions that change meaning

**Method**:

1. Find all comparisons (==, !=, <, >, etc.)
2. Check if operands could have unexpected types
3. Find all string concatenations and arithmetic
4. Check for null/undefined in arithmetic contexts

**Common traps**:

```javascript
// These are all true:
"" == false
"0" == false
[] == false
null == undefined
NaN !== NaN

// These produce unexpected results:
"5" + 3      // "53"
"5" - 3      // 2
[] + {}      // "[object Object]"
{} + []      // 0
```

### 6. Async Flow Tracing

**Purpose**: Find race conditions and missing awaits

**Method**:

1. Find all async operations
2. Trace order of execution
3. Check: Can operations complete out of order?
4. Find all await statements and check if any are missing

**What it catches**:

- Missing await before using result
- Operations that assume sequential completion
- Race conditions in shared state
- Fire-and-forget that silently fails

### 7. Null Propagation Analysis

**Purpose**: Find undefined behavior hiding in optional chains

**Method**:

1. Find all `?.` and `??` operators
2. Trace what happens when values are nullish
3. Check: Does the code handle the nullish case correctly?
4. Check: Is a nullish result ever used as if it were valid?

---

## Analysis/Data Verification Techniques

### 1. Data Transformation Tracing

**Purpose**: Find values that get silently corrupted

**Method**:

1. Start with known input data
2. Trace through each transformation step
3. Verify output at each step matches expectation
4. Check for precision loss, type changes, truncation

### 2. Aggregation Validation

**Purpose**: Find sums that double-count or averages that exclude

**Method**:

1. Hand-calculate expected result for small dataset
2. Compare to actual calculated result
3. Check grouping/partitioning logic for overlaps or gaps
4. Verify null handling in aggregations

**Common issues**:

- SUM over a join that creates duplicates
- AVG that includes nulls in count but not sum
- COUNT that counts rows instead of distinct values
- GROUP BY that creates unexpected partitions

### 3. Join Semantics Check

**Purpose**: Find data silently dropped by inner joins

**Method**:

1. Check join type (inner, left, right, full)
2. Verify cardinality expectations
3. Count records before and after join
4. Check for null keys that don't match

### 4. Filter Logic Audit

**Purpose**: Find filters that exclude valid cases

**Method**:

1. List all filter conditions
2. For each filter, find a valid case it might exclude
3. Check filter order (are some applied too early?)
4. Verify AND/OR logic is correct

### 5. Calculation Step Verification

**Purpose**: Find math that seems right but isn't

**Method**:

1. Break complex calculations into steps
2. Verify each step independently
3. Check units and scales match
4. Test with known values where answer is obvious

### 6. Conclusion Traceability

**Purpose**: Verify conclusions actually follow from data

**Method**:

1. Identify the stated conclusion
2. Trace back to the data/evidence supporting it
3. Check: Does this evidence actually support this conclusion?
4. Check: Are there alternative explanations not considered?

---

## Architecture Verification Techniques

### 1. Dependency Mapping

**Purpose**: Find hidden coupling and circular dependencies

**Method**:

1. Map all component dependencies
2. Check for cycles
3. Identify components that depend on many others
4. Find implicit dependencies (shared state, timing, etc.)

### 2. Failure Cascade Analysis

**Purpose**: Find single points of failure

**Method**:

1. For each component, ask: "What if this fails?"
2. Trace the failure through dependent components
3. Identify cascading failure paths
4. Check for circuit breakers and isolation

### 3. State Consistency Audit

**Purpose**: Find distributed state that can diverge

**Method**:

1. Identify all state stores (databases, caches, local state)
2. Check synchronization mechanisms
3. Verify what happens during network partition
4. Check for eventual consistency gaps

### 4. Interface Contract Verification

**Purpose**: Find mismatched expectations between components

**Method**:

1. Document expected interface for each boundary
2. Verify both sides agree on the contract
3. Check error handling expectations match
4. Verify version compatibility assumptions

### 5. Resource Exhaustion Analysis

**Purpose**: Find leaks and pool exhaustion

**Method**:

1. Track all resource acquisition (memory, connections, handles)
2. Verify all resources are released
3. Check behavior under sustained load
4. Find resources that grow without bound

---

## Cross-Domain Techniques

### 1. Assumption Surfacing

**Purpose**: Make implicit assumptions explicit so they can be verified

**Method**:

1. Ask: "For this to work, what must be true?"
2. List all assumptions
3. For each assumption, ask: "Is this validated or just hoped?"
4. Identify assumptions most likely to be violated

### 2. Adversarial Input Generation

**Purpose**: Find inputs that cause incorrect behavior

**Method**:

1. Identify input boundaries and constraints
2. Generate inputs at/beyond boundaries
3. Try inputs the author didn't anticipate
4. Include malformed, empty, huge, nested inputs

### 3. Temporal Verification

**Purpose**: Find timing-dependent bugs

**Method**:

1. Identify operations with timing assumptions
2. Check: What if these happen in different order?
3. What if there's a delay between operations?
4. What if operations run concurrently?

### 4. Scale Factor Analysis

**Purpose**: Find things that work in dev but fail at scale

**Method**:

1. Identify all O(n) or worse operations
2. Calculate behavior at 10x, 100x, 1000x scale
3. Check memory growth patterns
4. Identify operations that must stay constant-time

### 5. Consistency Cross-Check

**Purpose**: Find internal contradictions

**Method**:

1. Find related claims/values that should be consistent
2. Verify they actually are consistent
3. Check: Do totals match sums of parts?
4. Do timestamps form valid sequences?
