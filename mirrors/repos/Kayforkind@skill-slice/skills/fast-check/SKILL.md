---
name: fast-check
description: Adds JavaScript and TypeScript property-based tests with fast-check (randomized inputs, shrinking, roundtrips, custom arbitraries, fc.assert). Use when verifying invariants across generated inputs rather than single examples. Not for Vitest/Jest checks of fixed API fixtures, component rendering, or process-crash fuzzing.
version: 1.0.1
risk: safe
last_verified: '2026-05-30'
self_updating: true
---

# Fast-Check Property-Based Testing

Verify programmatic properties and logic invariants by generating randomized inputs and automatically shrinking failing assertions to their minimal reproducing case.

## When to Use

- Use when designing property-based tests, boundary verification suites, and fuzz testing parameters for parsers, calculators, algorithms, codecs, or critical business domains.
- Use when you need to verify that an invariant holds for all valid inputs (e.g., sort preserves length, encode/decode roundtrips, discount never produces negative pricing).
- Use when you want automated shrinking to reduce a failing case to its minimal reproduction.
- Route elsewhere (e.g., standard Vitest/Jest unit tests) when validating fixed API responses, rendering components, or checking exact integration scenarios.

## Prerequisites

- Node.js installed and available on PATH.
- A JavaScript or TypeScript project with a test runner (Vitest recommended).
- Windows host is primary. Use PowerShell for all shell commands. Adjust path separators if running on macOS/Linux.

## Procedure

### 1. Install fast-check and runner integration

```powershell
npm install -D fast-check @fast-check/vitest
```

For Jest-based projects, install `@fast-check/jest` instead:

```powershell
npm install -D fast-check @fast-check/jest
```

### 2. Write a basic invariant test

Assert a property that must hold for all generated inputs. Example: sorting preserves array length and produces ordered elements.

```typescript
import fc from "fast-check";
import { describe, it, expect } from "vitest";

describe("sorting algorithm logic", () => {
  it("maintains the original array length after sorting", () => {
    fc.assert(
      fc.property(fc.array(fc.integer()), (arr) => {
        const sorted = [...arr].sort((a, b) => a - b);
        return sorted.length === arr.length;
      })
    );
  });

  it("produces sequentially ordered elements", () => {
    fc.assert(
      fc.property(fc.array(fc.integer()), (arr) => {
        const sorted = [...arr].sort((a, b) => a - b);
        for (let i = 1; i < sorted.length; i++) {
          expect(sorted[i]).toBeGreaterThanOrEqual(sorted[i - 1]);
        }
      })
    );
  });
});
```

### 3. Write a roundtrip verification test

Test codec, serialization, and translation functions by executing encode-decode and comparing against the original input.

```typescript
import fc from "fast-check";
import { encode, decode } from "./codec";

it("ensures decode(encode(val)) strictly equals val for all strings", () => {
  fc.assert(
    fc.property(fc.string(), (original) => {
      const encoded = encode(original);
      const decoded = decode(encoded);
      expect(decoded).toEqual(original);
    })
  );
});

it("ensures JSON serialization preserves complex objects", () => {
  fc.assert(
    fc.property(fc.jsonValue(), (value) => {
      const json = JSON.stringify(value);
      const parsed = JSON.parse(json);
      expect(parsed).toEqual(value);
    })
  );
});
```

### 4. Build custom arbitrary generators

Construct complex domain objects by combining base arbitraries with `fc.record`.

```typescript
import fc from "fast-check";

const userArbitrary = fc.record({
  id: fc.uuid(),
  name: fc.string({ minLength: 1, maxLength: 100 }),
  email: fc.emailAddress(),
  age: fc.integer({ min: 13, max: 120 }),
  role: fc.constantFrom("admin", "user", "viewer"),
  createdAt: fc.date({ min: new Date("2020-01-01"), max: new Date() }),
});

const moneyArbitrary = fc.record({
  amount: fc.integer({ min: 0, max: 1_000_000 }), // represented in cents
  currency: fc.constantFrom("USD", "EUR", "GBP"),
});

it("ensures coupon discount calculations never produce negative pricing", () => {
  fc.assert(
    fc.property(
      moneyArbitrary,
      fc.integer({ min: 0, max: 100 }),
      (price, discountPercent) => {
        const discounted = applyDiscount(price, discountPercent);
        expect(discounted.amount).toBeGreaterThanOrEqual(0);
      }
    )
  );
});
```

### 5. Use preconditions to filter invalid inputs

Filter out input combinations that violate initial system prerequisites using `fc.pre`.

```typescript
import fc from "fast-check";

it("calculates correct ratios for non-zero denominators", () => {
  fc.assert(
    fc.property(fc.integer(), fc.integer(), (numerator, denominator) => {
      fc.pre(denominator !== 0); // skip zero denominators
      const ratio = numerator / denominator;
      expect(Number.isFinite(ratio)).toBe(true);
    })
  );
});
```

### 6. Configure run limits

Scale testing size with `numRuns`. Default is 100 runs per assertion. Increase to 1,000 or 10,000 for critical pathways.

```typescript
fc.assert(fc.property(fc.string(), (val) => { /* ... */ }), { numRuns: 1000 });
```

### 7. Reproduce failures using seeds

On failure, fast-check logs the exact seed and path (e.g., `seed: 12345678, path: "0:2:1"`). Feed these back into options to debug the minimal reproduction.

```typescript
fc.assert(fc.property(/* ... */), { seed: 12345678, path: "0:2:1" });
```

### 8. Run the tests

```powershell
npx vitest run
```

## Pitfalls

- **Excessive `fc.pre` filtering**: Fast-check errors out with "too many runs skipped" when precondition rejection rates are high. Instead of `fc.pre(val !== 0)`, generate values using `fc.integer().map(x => x === 0 ? 1 : x)` or restrict bounds directly with `fc.integer({ min: 1 })`.
- **Test timeouts with slow functions**: Large datasets or slow synchronous functions can cause runner timeouts. Adjust `{ numRuns: N }` down or run CPU profile checks to identify performance bottlenecks.
- **Unconstrained large objects**: Large generated objects can cause out-of-memory overhead. Constrain sizes with `minLength`, `maxLength`, `min`, and `max` options.
- **CommonJS vs ESM import paths**: In legacy Node.js CommonJS setups, ensure correct import paths when migrating to pure ES modules. Use `fc.assert` explicitly if integration-level runner extensions are absent.
- **Thinking in examples instead of properties**: Property-based tests assert behavior that remains invariant under any input (e.g., `x + y === y + x`), not exact outputs for specific inputs. Combine property suites with edge-case example tests—use examples to pin known boundaries and properties to surface unknown gaps.
- **Fuzzing vs property testing confusion**: Use property testing to assert strict output constraints (`expect`). Use fuzzing to verify that input parsing does not crash the Node/V8 process.

## Verification

- Confirm the package is installed:

```powershell
npm ls fast-check @fast-check/vitest
```

- Run the test suite and confirm all property tests pass:

```powershell
npx vitest run
```

- On failure, confirm fast-check logs the counterexample values, original seed, path index, and failure trace. Copy the seed and path into the assertion options to reproduce deterministically.

- Quality checklist:
  - [ ] Seeds logged on failure are added to a regression unit test.
  - [ ] No `fc.pre` calls are used where direct constraint configuration (e.g., `fc.integer({ min: 1 })`) is possible.
  - [ ] Large objects are constrained to reasonable sizes to prevent out-of-memory overhead during generation.

## Related Skills

- **vitest** — Standard unit and integration test runner; pair with fast-check for combined example and property suites.
- **jest** — Alternative test runner; use `@fast-check/jest` integration package.

## Source Anchors

- [Official Fast-Check Site](https://fast-check.dev)
- [Fast-Check GitHub Repository](https://github.com/dubzzz/fast-check)

## Changelog

- **2026-05-30**: Modernized skill documentation, updated setup steps for Vitest runner integration (`@fast-check/vitest`), converted all instructional paragraphs to imperative style, and compiled to Developer-Tools.
