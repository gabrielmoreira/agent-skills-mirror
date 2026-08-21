---
name: bug-hunter
description: "Hunts bugs with reproduce-then-evidence debugging: logs, bisect, and a regression test before claiming a fix. Use when the user reports a crash, error, flake, or asks to debug or fix a bug. Not for greenfield feature design. Do not use as a substitute for the project's test runner or typecheck."
version: 1.0.1
category: development
risk: safe
source: community
date_added: "2026-03-05"
---

# Bug Hunter

Systematically hunt down and fix bugs using proven debugging techniques. No guessing—follow the evidence from symptom to root cause, implement the fix, and prevent regression.

## When to Use

- User reports a bug, error, or crash.
- Something isn't working as expected.
- User says "fix the bug", "debug this", or "why is this broken".
- Intermittent failures or weird, hard-to-explain behavior.
- Production issues need investigation.
- A test is failing and the cause is unclear.

## Prerequisites

- Access to the codebase and ability to run it locally.
- Access to relevant logs (application, system, browser console).
- Git history available for diff and bisect debugging.
- On Windows host (primary), use **PowerShell** for all shell commands. Adjust path separators accordingly (e.g., `~\agent-skills\library\bug-hunter\`).
- This folder does not ship a `references/` pack. Keep the eight-step procedure in this file.

## Procedure

### 1. Reproduce the Bug

Make it happen consistently before attempting any fix.

1. Get exact steps to reproduce from the user or reporter.
2. Try to reproduce locally.
3. Note what triggers it—input, state, timing, environment.
4. Document the full error message and/or unexpected behavior.
5. Determine if it happens every time or randomly.

If you **cannot** reproduce it, gather more info:
- What environment? (dev, staging, prod)
- What browser/device/OS?
- What user actions preceded it?
- Any error logs, stack traces, or screenshots?

> **HARD RULE:** Never attempt a fix until you can reproduce the bug or have a concrete, evidence-backed explanation of why it occurs. Guessing wastes time and introduces regressions.

### 2. Gather Evidence

Collect all available information before forming a hypothesis.

**Check logs (PowerShell on Windows):**

```powershell
# Application logs (tail equivalent)
Get-Content -Path "logs\app.log" -Wait -Tail 50

# Filter for errors
Get-Content "logs\app.log" | Select-String -Pattern "ERROR|Exception"

# System event logs
Get-EventLog -LogName Application -Newest 50 -EntryType Error
```

**Browser console:**
- Open DevTools → Console tab. Note all errors and warnings.
- Open DevTools → Network tab. Check failed API calls and responses.

**Check error messages:**
- Full stack trace (copy it verbatim).
- Error type and message.
- Line numbers and file names.
- Timestamp and request ID if available.

**Check state:**
- What data was being processed?
- What was the user trying to do?
- What's in the database?
- What's in local storage / cookies / session?

### 3. Form a Hypothesis

Based on evidence, write a single-sentence hypothesis:

```
"The login times out because the session cookie expires before the auth check completes."

"The form fails because email validation regex doesn't handle plus signs."

"The API returns 500 because the database query has a syntax error with special characters."
```

Write it down. You will prove or disprove this specific statement.

### 4. Test the Hypothesis

Prove or disprove your guess with targeted instrumentation.

**Add logging:**

```javascript
console.log('Before API call:', userData);
const response = await api.login(userData);
console.log('After API call:', response);
```

**Use a debugger breakpoint:**

```javascript
debugger; // Execution pauses here in DevTools or VS Code
const result = processData(input);
```

**Isolate the problem by commenting out code:**

```javascript
// const result = complexFunction();
const result = { mock: 'data' }; // Use mock data to narrow scope
```

> **HARD RULE:** Remove all temporary `console.log` and `debugger` statements before committing the fix. Never leave debug instrumentation in production code.

### 5. Find Root Cause

Trace back from symptom to the actual problem. Do not stop at the first "why"—keep asking until you reach a single actionable cause.

**Common root causes:**
- Null / undefined values
- Wrong data types
- Race conditions
- Missing error handling
- Incorrect logic
- Off-by-one errors
- Async/await issues (missing await, unhandled promises)
- Missing or incorrect validation

**Example trace:**

```
Symptom: "Cannot read property 'name' of undefined"
↓
Where: user.profile.name
↓
Why: user.profile is undefined
↓
Why: API didn't return profile
↓
Why: User ID was null
↓
Root cause: Login didn't set user ID in session
```

### 6. Implement Fix

Fix the **root cause**, not the symptom.

**Bad fix (patches symptom, hides real bug):**

```javascript
// Just hide the error
const name = user?.profile?.name || 'Unknown';
```

**Good fix (addresses root cause):**

```javascript
// Ensure user ID is set on login
const login = async (credentials) => {
  const user = await authenticate(credentials);
  if (user) {
    session.userId = user.id; // Fix: Set user ID
    return user;
  }
  throw new Error('Invalid credentials');
};
```

> **HARD RULE:** Never suppress an error without understanding and fixing its root cause. Silent catches and blanket fallbacks hide bugs and make future debugging harder.

### 7. Test the Fix

Verify the fix actually works.

1. Reproduce the original bug scenario.
2. Apply the fix.
3. Try to reproduce again—it should now fail to reproduce (i.e., work correctly).
4. Test edge cases: null inputs, empty strings, special characters, large data, concurrent requests.
5. Test related functionality to ensure no regressions.
6. Run existing test suite.

```powershell
# Run tests (example for Node.js)
npm test

# Run a specific test file
npx jest --testPathPattern="login.test.js"
```

### 8. Prevent Regression

Add a test so the bug doesn't come back.

```javascript
test('login sets user ID in session', async () => {
  const user = await login({ email: 'test@example.com', password: 'pass' });

  expect(session.userId).toBe(user.id);
  expect(session.userId).not.toBeNull();
});
```

Write the prevention test in the project's existing test runner. Do not invent a missing templates file.

### 9. Document the Fix

After fixing, document it for the team:

```markdown
## Bug: Login timeout after 30 seconds

**Symptom:** Users get logged out immediately after login.

**Root Cause:** Session cookie expires before auth check completes.

**Fix:** Increased session timeout from 30s to 3600s in config.

**Files Changed:**
- config/session.js (line 12)

**Testing:** Verified login persists for 1 hour.

**Prevention:** Added test for session persistence.
```

## Debugging Techniques

### Binary Search

Cut the problem space in half repeatedly:

```javascript
// Does the bug happen before or after this line?
console.log('CHECKPOINT 1');
// ... code ...
console.log('CHECKPOINT 2');
// ... code ...
console.log('CHECKPOINT 3');
```

### Rubber Duck Debugging

Explain the code line by line out loud. Often you'll spot the issue while explaining it to someone (or something) else.

### Print Debugging

Strategic, temporary `console.log` statements at transformation boundaries:

```javascript
console.log('Input:', input);
console.log('After transform:', transformed);
console.log('Before save:', data);
console.log('Result:', result);
```

### Diff Debugging

Compare working vs broken:
- What changed recently? (`git log --oneline -20`)
- What's different between environments?
- What's different in the data?

### Time Travel Debugging (Git Bisect)

Use git to find exactly when the bug was introduced:

```powershell
git bisect start
git bisect bad          # Current commit is broken
git bisect good abc123  # This old commit worked
# Git will check out commits for you to test
git bisect reset        # When done, return to original branch
```

## Common Bug Patterns

### Null / Undefined

```javascript
// Bug
const name = user.profile.name;

// Fix (defensive)
const name = user?.profile?.name || 'Unknown';

// Better fix (fail fast with clear error)
if (!user || !user.profile) {
  throw new Error('User profile required');
}
const name = user.profile.name;
```

### Race Condition

```javascript
// Bug
let data = null;
fetchData().then(result => data = result);
console.log(data); // null - not loaded yet

// Fix
const data = await fetchData();
console.log(data); // correct value
```

### Off-by-One

```javascript
// Bug
for (let i = 0; i <= array.length; i++) {
  console.log(array[i]); // undefined on last iteration
}

// Fix
for (let i = 0; i < array.length; i++) {
  console.log(array[i]);
}
```

### Type Coercion

```javascript
// Bug
if (count == 0) { // true for "", [], null

// Fix
if (count === 0) { // only true for 0
```

### Async Without Await

```javascript
// Bug
const result = asyncFunction(); // Returns Promise
console.log(result.data); // undefined

// Fix
const result = await asyncFunction();
console.log(result.data); // correct value
```

## Debugging Tools

### Browser DevTools

```
Console:     View logs and errors
Sources:     Set breakpoints, step through code
Network:     Check API calls and responses
Application: View cookies, storage, cache
Performance: Find slow operations
```

### Node.js Debugging

```powershell
# Built-in debugger
node --inspect app.js

# Then open chrome://inspect in Chrome
```

### VS Code Debugging

```json
// .vscode/launch.json
{
  "type": "node",
  "request": "launch",
  "name": "Debug App",
  "program": "${workspaceFolder}/app.js"
}
```

## When You're Stuck

1. Take a break—walk away for 10 minutes.
2. Explain it to someone else (or a rubber duck).
3. Search for the exact error message (quoted).
4. Check if it's a known issue (GitHub issues, Stack Overflow).
5. Simplify: create a minimal reproduction.
6. Start over: delete and rewrite the problematic code.
7. Ask for help—provide context, what you've tried, and the full error.

## Pitfalls

- **Fixing the symptom, not the root cause.** If you patch a crash with a try/catch or optional chaining without understanding why the value is null, the bug will resurface elsewhere.
- **Skipping reproduction.** If you can't reproduce the bug, you cannot verify the fix. Gather more evidence instead of guessing.
- **Leaving debug instrumentation in production.** Remove all `console.log`, `debugger`, and temporary logging before committing.
- **Silent error suppression.** Never catch an error and do nothing. At minimum, log it.
- **Not testing edge cases.** A fix that works for the reported input may break for null, empty, or special-character inputs.
- **Not running the full test suite.** Your fix may fix the bug but break unrelated functionality.
- **Forgetting to add a regression test.** Without a test, the same bug can be reintroduced later.
- **Assuming the environment is the same.** Bugs that only appear in staging/prod may be caused by environment-specific config, data, or load.

## Verification

After completing the fix, verify each of the following:

1. **Bug is fixed:** Reproduce the original scenario—the error no longer occurs.
2. **No regressions:** Run the full test suite and confirm all tests pass.

   ```powershell
   npm test
   ```

3. **Regression test exists:** A new test covers the specific bug scenario and fails without the fix.

   ```powershell
   npx jest --testPathPattern="login.test.js"
   ```

4. **No debug artifacts remain:** Search for temporary debug code.

   ```powershell
   # Check for leftover debugger statements and temporary console.logs
   Select-String -Path "src\*.js" -Pattern "debugger;"
   ```

5. **Documentation updated:** The bug fix is documented with symptom, root cause, fix, files changed, and prevention test.

## Key Principles

- Reproduce first, fix second.
- Follow the evidence, don't guess.
- Fix root cause, not symptoms.
- Test the fix thoroughly.
- Add tests to prevent regression.
- Document what you learned.

## Related Skills

- `@systematic-debugging` — Advanced debugging workflows.
- `@test-driven-development` — Testing practices.
- `@codebase-audit-pre-push` — Pre-push code review.

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
