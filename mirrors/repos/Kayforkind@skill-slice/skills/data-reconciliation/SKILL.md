---
name: data-reconciliation
version: 1.1.1
description: "Derives a missing workbook cell from a fully determined constraint: row/column remainder, YoY invert, share x total, CAGR endpoints, weighted-average sleeve, then tolerance-checked cross-tab sums. Invoke when auditing statements or reconstructing a redacted export that still contains those anchors. Do not use on under-determined blanks, conflicting totals with no priority rule, or curve-fit recovery."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# Data Reconciliation for Spreadsheets

Techniques for recovering missing values from financial and tabular data using mathematical constraints, modern spreadsheet logic, and data integrity standards.

The guiding idea: a blank cell is only *recoverable* when the surrounding data over-constrains it. A row total, a published growth rate, or a stated percentage share each removes a degree of freedom. When enough constraints exist that exactly one value can satisfy them, you are not *guessing* the number — you are *deriving* it. Everything in this skill is about finding those fully-determined cells, solving them in a safe order, and then proving the result is consistent.

The reference code below is written in TypeScript with explicit types, argument validation, and defensive errors so that the same logic can run inside a script, a serverless function, or a spreadsheet add-on without silently producing `NaN` or `Infinity` in a financial report.

## When to Use

Use this skill when you need to recover missing values in spreadsheets based on known totals, percentage shares, year-over-year changes, CAGR relationships, and cross-sheet constraints. This is essential for auditing financial statements, cleaning legacy datasets, and reconstructing incomplete reports.

**Trigger keywords:** reconciliation, missing values, spreadsheet recovery, row total, column total, percentage share, YoY change, CAGR, cross-sheet validation, weighted average, financial audit, data integrity, blank cell recovery.

The common thread is that the *answer already exists implicitly* in the data — it has just been deleted, redacted, or lost in an export. Reconciliation recovers it deterministically rather than estimating it, which is what makes the output defensible in an audit.

### When NOT to Use

Reconciliation produces a single correct answer only when the math forces one. Avoid it in the following situations:

- **Under-determined systems** — the data lacks sufficient constraints. With more unknowns than independent equations, infinitely many value sets satisfy the constraints, so any single answer is arbitrary. Gather more anchors first, or label the cell as genuinely unknown.
- **Undefined or inconsistent relationships** — the relationships between data points are not explicitly stated or contradict each other. Reconciliation is only as trustworthy as the constraint it is built on; an assumed relationship that turns out to be wrong silently corrupts every downstream cell.
- **Over-determined systems without a priority rule** — contradictory constraints exist (e.g., a stated total that disagrees with the sum of its parts) and no rule says which one wins. You would have to choose which source to trust, silently hiding a real data-quality problem that a human should adjudicate.
- **Trend guessing** — attempting to interpolate or extrapolate without a defined trend. Picking a curve (linear, geometric, seasonal) is a modeling assumption, not a recovery; presenting an extrapolation as a "recovered" fact misrepresents its certainty.

## Prerequisites

- **Runtime:** Node.js 18+ with TypeScript support, or any environment that can execute TypeScript (e.g., Deno, Bun, ts-node).
- **Windows host (primary):** PowerShell 5.1+ or PowerShell 7+. All file paths use Windows conventions (`~`). On macOS/Linux, adapt paths accordingly.
- **No external dependencies:** All functions use pure TypeScript with no npm packages. The `Math` object is the only runtime API required.
- **Reference files:** If this skill is installed from the agent-skills library, check for `references/` and `scripts/` subdirectories:
  - `references/` — load any supplementary documentation on spreadsheet formula patterns or financial reporting standards before beginning a complex multi-sheet reconciliation.
  - `scripts/` — load pre-built reconciliation scripts (e.g., `reconciliation.ts`) if available, rather than re-implementing from scratch. These scripts contain the exact functions documented below.

## Procedure

### Step 1: Inventory All Constraints

Before writing any formula or code, map out every mathematical relationship in the target spreadsheet:

1. **Identify sum constraints** — rows or columns with a known total and exactly one blank component.
2. **Identify ratio constraints** — published percentage shares, YoY changes, or growth rates.
3. **Identify multi-period constraints** — CAGR relationships spanning multiple years with known endpoints.
4. **Identify weighted-average constraints** — blended rates or portfolio returns with one missing component.
5. **Identify cross-sheet equalities** — values that must match across tabs (Detail → Summary, lookup targets).

Record each constraint with its type, location (sheet + cell), and which values are known vs. unknown.

### Step 2: Identify Solvable Cells

Locate "anchor" cells (known values) and any cell whose constraint contains exactly one unknown. Those are the only cells you may solve in the current pass. If a constraint has two or more unknowns, it is not solvable yet — wait until a prior recovery fills in one of them.

### Step 3: Solve in Dependency Order

1. Solve a value using the appropriate function (see below).
2. Treat the recovered value as a new anchor.
3. Re-scan for cells that just became single-unknown.
4. Repeat until no more cells can be solved.

This turns a tangle of constraints into a safe, linear sequence. Solving cells in the wrong order either blocks you (a formula references a still-blank cell) or produces a plausible-but-wrong number that contaminates the rest of the sheet.

### Step 4: Validate All Recoveries

Run a closing "circular check" — feed every recovered value back through the original constraints and confirm they still hold. If a constraint now fails, an earlier assumption was wrong. See the **Verification** section for the full checklist.

### Shared Validation Helpers

Every recovery function is defensive about its inputs, because a single `NaN`, `Infinity`, or unexpected `undefined` flowing into a financial total can corrupt an entire report without throwing. Centralizing the guards keeps each function readable and guarantees a consistent, descriptive error that names the offending argument. Treat the following as the top of a single module (e.g., `reconciliation.ts`); the later functions reuse these helpers by name.

```typescript
/**
 * Throws if `value` is not a finite number. NaN and Infinity are rejected
 * because they propagate silently through arithmetic and poison every
 * dependent cell instead of failing loudly at the source.
 */
function assertFiniteNumber(value: number, name: string): void {
  if (typeof value !== "number" || Number.isNaN(value) || !Number.isFinite(value)) {
    throw new TypeError(`"${name}" must be a finite number, received: ${String(value)}`);
  }
}

/**
 * Throws if `values` is not a non-empty array of finite numbers. An empty
 * array almost always signals an upstream selection or filter bug, so we treat
 * it as an error rather than quietly returning a zero-length reduction.
 */
function assertFiniteNumberArray(values: readonly number[], name: string): void {
  if (!Array.isArray(values) || values.length === 0) {
    throw new TypeError(`"${name}" must be a non-empty array of finite numbers.`);
  }
  values.forEach((value: number, index: number): void => {
    assertFiniteNumber(value, `${name}[${index}]`);
  });
}

/**
 * Sums an array of finite numbers with an explicitly typed reducer so the
 * accumulator can never be inferred as `any`.
 */
function sumFiniteNumbers(values: readonly number[]): number {
  return values.reduce(
    (accumulator: number, value: number): number => accumulator + value,
    0,
  );
}
```

### Recovery Technique 1: Row/Column Sum Constraints

When a total is provided and only one component is blank, that component is fully determined — there is exactly one value that makes the parts add up to the whole. This is the safest recovery of all, so solve these cells first: they create new anchors that unlock dependent calculations. In a live spreadsheet the same relationship is usually expressed with `SUM` or `SUBTOTAL`.

**Relationship:** `missing = total − Σ(known values)`

```typescript
/**
 * Recovers the single missing component of a collection that must add up to a
 * known total. Use only when exactly one value is blank; with two or more
 * blanks the system is under-determined and the result would be meaningless.
 */
function recoverMissingFromSum(total: number, knownValues: readonly number[]): number {
  assertFiniteNumber(total, "total");
  assertFiniteNumberArray(knownValues, "knownValues");

  const knownSum: number = sumFiniteNumbers(knownValues);
  return total - knownSum;
}

// If a row sums to 1,000 and three of four cells are known (200, 300, 400):
const recoveredCell: number = recoverMissingFromSum(1_000, [200, 300, 400]);
// recoveredCell === 100
```

### Recovery Technique 2: Year-over-Year (YoY) Change Recovery

A published period-over-period change links two adjacent values by a multiplicative factor. Knowing any two of {previous value, current value, percent change} determines the third. Recovering *backward* (deriving the previous period from the current one) is the common audit case, and it is the one that can divide by zero — a stated change of −100% drives the prior value to infinity, so it must be guarded explicitly. Percent changes are passed as fractions (`0.20` means +20%, `-0.05` means −5%) to avoid the ambiguity of mixing 20 and 0.20 in the same codebase.

**Relationships:** `current = previous × (1 + change)` and `previous = current ÷ (1 + change)`

```typescript
/**
 * Projects a value forward one period given a fractional growth rate.
 */
function applyYoYForward(previous: number, fractionalChange: number): number {
  assertFiniteNumber(previous, "previous");
  assertFiniteNumber(fractionalChange, "fractionalChange");

  return previous * (1 + fractionalChange);
}

/**
 * Recovers the prior-period value from the current value and the fractional
 * change. Guards against a -100% change, which would otherwise divide by zero
 * and emit Infinity into the dataset.
 */
function recoverYoYPrevious(current: number, fractionalChange: number): number {
  assertFiniteNumber(current, "current");
  assertFiniteNumber(fractionalChange, "fractionalChange");

  const growthFactor: number = 1 + fractionalChange;
  if (growthFactor === 0) {
    throw new RangeError(
      "Cannot recover the previous value: a fractionalChange of -1 (-100%) implies division by zero.",
    );
  }
  return current / growthFactor;
}

// Current value 1,200 after a +20% year: the prior year was 1,000.
const priorYear: number = recoverYoYPrevious(1_200, 0.20);
// priorYear === 1000
```

### Recovery Technique 3: Percentage Share Recovery

When a component's share of a total is published, the component is `total × share`. The inverse — deriving the share from a part and a total — is equally useful for cross-checking, but it divides by the total, so a zero total must be rejected rather than allowed to produce `NaN`. Shares are validated to the `[0, 1]` range because a share outside that band signals that the caller has confused a percentage point value (`20`) with a fraction (`0.20`), one of the most common reconciliation bugs.

**Relationship:** `part = total × share` and `share = part ÷ total`

```typescript
/**
 * Recovers a component value from a total and that component's fractional
 * share. Rejects shares outside [0, 1] to catch the common "20 vs 0.20" mistake.
 */
function recoverShareValue(total: number, share: number): number {
  assertFiniteNumber(total, "total");
  assertFiniteNumber(share, "share");

  if (share < 0 || share > 1) {
    throw new RangeError(`"share" must be a fraction in the range [0, 1], received: ${share}`);
  }
  return total * share;
}

/**
 * Derives the fractional share a part represents of a total. A zero total has
 * no defined share, so it is rejected rather than returning NaN.
 */
function recoverShareFraction(part: number, total: number): number {
  assertFiniteNumber(part, "part");
  assertFiniteNumber(total, "total");

  if (total === 0) {
    throw new RangeError('Cannot derive a share from a "total" of zero (division by zero).');
  }
  return part / total;
}

// A 20% share of a 50,000 budget is 10,000.
const departmentBudget: number = recoverShareValue(50_000, 0.20);
// departmentBudget === 10000
```

### Recovery Technique 4: Compound Annual Growth Rate (CAGR)

CAGR collapses an entire multi-year span into the single constant growth rate that connects the start and end values. It is useful when the intermediate years are missing but the endpoints and the number of periods are known. It is defined only for *positive* start and end values (the geometric mean of a ratio involving a non-positive number is not meaningful for currency) and a *positive integer* period count, so all three are validated. Once you have the rate you can project any endpoint forward or backward.

**Relationship:** `CAGR = (end ÷ start)^(1 / periods) − 1`, with `end = start × (1 + CAGR)^periods`

```typescript
/**
 * Computes the compound annual growth rate that connects a positive start
 * value to a positive end value over a positive integer number of periods.
 */
function computeCAGR(startValue: number, endValue: number, periods: number): number {
  assertFiniteNumber(startValue, "startValue");
  assertFiniteNumber(endValue, "endValue");
  assertFiniteNumber(periods, "periods");

  if (startValue <= 0) {
    throw new RangeError(`"startValue" must be greater than zero, received: ${startValue}`);
  }
  if (endValue <= 0) {
    throw new RangeError(`"endValue" must be greater than zero, received: ${endValue}`);
  }
  if (!Number.isInteger(periods) || periods <= 0) {
    throw new RangeError(`"periods" must be a positive integer, received: ${periods}`);
  }
  return Math.pow(endValue / startValue, 1 / periods) - 1;
}

/**
 * Projects a start value forward by a constant CAGR over a number of periods.
 * A CAGR below -1 (worse than total loss) is rejected as economically invalid.
 */
function projectWithCAGR(startValue: number, cagr: number, periods: number): number {
  assertFiniteNumber(startValue, "startValue");
  assertFiniteNumber(cagr, "cagr");
  assertFiniteNumber(periods, "periods");

  if (!Number.isInteger(periods) || periods < 0) {
    throw new RangeError(`"periods" must be a non-negative integer, received: ${periods}`);
  }
  const growthFactor: number = 1 + cagr;
  if (growthFactor < 0) {
    throw new RangeError(`A cagr below -1 (-100%) is not economically meaningful, received: ${cagr}`);
  }
  return startValue * Math.pow(growthFactor, periods);
}

/**
 * Recovers the start value from a known end value, CAGR, and period count by
 * inverting the compounding. Rejects (1 + cagr) <= 0, which would divide by
 * zero or take a root of a negative base.
 */
function recoverStartFromCAGR(endValue: number, cagr: number, periods: number): number {
  assertFiniteNumber(endValue, "endValue");
  assertFiniteNumber(cagr, "cagr");
  assertFiniteNumber(periods, "periods");

  if (!Number.isInteger(periods) || periods < 0) {
    throw new RangeError(`"periods" must be a non-negative integer, received: ${periods}`);
  }
  const growthFactor: number = 1 + cagr;
  if (growthFactor <= 0) {
    throw new RangeError(`Cannot recover a start value when (1 + cagr) <= 0, received cagr: ${cagr}`);
  }
  return endValue / Math.pow(growthFactor, periods);
}

// Year 1 = 1,000 and Year 5 = 1,500 spans 4 periods of growth.
const annualGrowth: number = computeCAGR(1_000, 1_500, 4);
// annualGrowth ≈ 0.1067 (about 10.67% per year)
```

### Recovery Technique 5: Cross-Sheet and Cross-Reference Validation

A recovered value is only trustworthy once it agrees with every place it appears. Modern reconciliation therefore verifies that a "Detail" tab sums to its "Summary" tab, and that a value derived in one sheet matches a lookup in another (`XLOOKUP` or `INDEX/MATCH` in a live workbook). The critical subtlety is that floating-point sums almost never match to the last bit, so comparisons must use a tolerance rather than strict equality — otherwise correct data is flagged as broken. The function below returns a structured result so callers can both branch on success and log the exact discrepancy.

```typescript
interface ReconciliationResult {
  readonly reconciled: boolean;
  readonly detailTotal: number;
  readonly summaryTotal: number;
  readonly difference: number;
  readonly tolerance: number;
}

/**
 * Checks whether the sum of detail rows reconciles with a summary total within
 * an absolute tolerance. A direct === comparison is avoided because binary
 * floating point makes exact equality of two independently-summed totals
 * unreliable, producing false "mismatch" alarms on correct data.
 */
function reconcileTotals(
  detailValues: readonly number[],
  summaryTotal: number,
  tolerance: number = 1e-6,
): ReconciliationResult {
  assertFiniteNumberArray(detailValues, "detailValues");
  assertFiniteNumber(summaryTotal, "summaryTotal");
  assertFiniteNumber(tolerance, "tolerance");

  if (tolerance < 0) {
    throw new RangeError(`"tolerance" must be non-negative, received: ${tolerance}`);
  }
  const detailTotal: number = sumFiniteNumbers(detailValues);
  const difference: number = Math.abs(detailTotal - summaryTotal);
  return {
    reconciled: difference <= tolerance,
    detailTotal,
    summaryTotal,
    difference,
    tolerance,
  };
}

// Detail rows should reconcile with the published summary total of 723,000.
const integrity: ReconciliationResult = reconcileTotals([210_000, 245_000, 268_000], 723_000);
// integrity.reconciled === true, integrity.difference === 0
```

### Recovery Technique 6: Weighted-Average Component Recovery

When a *weighted* average is published (e.g., a blended interest rate or a portfolio-weighted return) and one component value is missing, the missing value is determined as long as every weight and the other component values are known. The naive formula `(weightedAvg − Σ wᵢvᵢ) / w_missing` is only correct when the weights happen to sum to 1; the implementation below makes no such assumption and works for arbitrary weights by reconstructing the full weighted total. The missing weight must be strictly positive — a zero weight contributes nothing to the average and so cannot be back-solved.

**Relationship:** with total weight `W = Σ wᵢ` (including the missing component's weight `w_m`), the missing value is `v_m = (weightedAverage × W − Σ_known wᵢvᵢ) ÷ w_m`

```typescript
interface WeightedComponent {
  readonly weight: number;
  readonly value: number;
}

/**
 * Recovers the single missing component value of a weighted average, given the
 * known (weight, value) pairs and the missing component's weight. Works for any
 * weights (they need not sum to 1) because it rebuilds the full weighted total
 * rather than assuming normalized weights.
 */
function recoverWeightedComponent(
  weightedAverage: number,
  knownComponents: readonly WeightedComponent[],
  missingWeight: number,
): number {
  assertFiniteNumber(weightedAverage, "weightedAverage");
  assertFiniteNumber(missingWeight, "missingWeight");

  if (!Array.isArray(knownComponents) || knownComponents.length === 0) {
    throw new TypeError('"knownComponents" must be a non-empty array of { weight, value } pairs.');
  }
  knownComponents.forEach((component: WeightedComponent, index: number): void => {
    assertFiniteNumber(component.weight, `knownComponents[${index}].weight`);
    assertFiniteNumber(component.value, `knownComponents[${index}].value`);
  });
  if (missingWeight <= 0) {
    throw new RangeError(`"missingWeight" must be greater than zero, received: ${missingWeight}`);
  }

  const knownWeightSum: number = knownComponents.reduce(
    (accumulator: number, component: WeightedComponent): number => accumulator + component.weight,
    0,
  );
  const knownWeightedSum: number = knownComponents.reduce(
    (accumulator: number, component: WeightedComponent): number =>
      accumulator + component.weight * component.value,
    0,
  );
  const totalWeight: number = knownWeightSum + missingWeight;

  return (weightedAverage * totalWeight - knownWeightedSum) / missingWeight;
}

// A portfolio with a blended 5% return: two known sleeves and one missing sleeve.
const missingSleeveReturn: number = recoverWeightedComponent(
  0.05,
  [
    { weight: 0.5, value: 0.04 },
    { weight: 0.3, value: 0.06 },
  ],
  0.2,
);
// missingSleeveReturn === 0.06 (the 20%-weighted sleeve returned 6%)
```

### Chain Dependencies: Multi-Sheet Recovery

Values frequently must be solved across several sheets in sequence, where each result feeds the next. Mapping the dependency graph *before* writing formulas is what prevents `#REF!` and circular-reference (`#CIRCULAR!`) errors, and it makes the recovery reproducible. The example below recovers a quarter from an annual total, uses it to derive an implied growth rate, and finally proves the detail tab still reconciles with the summary tab — using the functions defined above.

```typescript
// Sheet 1 — recover Q4 from the published annual total of 1,000,000.
const q4: number = recoverMissingFromSum(1_000_000, [210_000, 245_000, 268_000]);
// q4 === 277_000

// Sheet 2 — derive the implied YoY growth of Q4 versus the prior year's Q4.
const priorYearQ4: number = 250_000;
const q4YoYGrowth: number = recoverShareFraction(q4 - priorYearQ4, priorYearQ4);
// q4YoYGrowth === 0.108 (a 10.8% increase)

// Sheet 3 — confirm the detail tab reconciles with the summary tab before trusting the chain.
const crossCheck: ReconciliationResult = reconcileTotals(
  [210_000, 245_000, 268_000, q4],
  1_000_000,
);
if (!crossCheck.reconciled) {
  throw new Error(
    `Detail and summary tabs disagree by ${crossCheck.difference} ` +
      `(tolerance ${crossCheck.tolerance}); halt before propagating q4 downstream.`,
  );
}
// crossCheck.reconciled === true, so q4 and q4YoYGrowth are safe to publish.
```

### Quick Reference: Constraint → Function Mapping

| Constraint Type | Reference function | When to use |
|-----------------|--------------------|-------------|
| Sum to total | `recoverMissingFromSum(total, known)` | Exactly one component of a sum is blank |
| YoY forward | `applyYoYForward(previous, change)` | Know the prior period and the change |
| YoY backward | `recoverYoYPrevious(current, change)` | Know the current period and the change |
| Share of total | `recoverShareValue(total, share)` | Know the total and the component's share |
| Share derivation | `recoverShareFraction(part, total)` | Know the part and total, need the share |
| CAGR | `computeCAGR(start, end, periods)` | Multi-year span with known endpoints |
| CAGR projection | `projectWithCAGR(start, cagr, periods)` | Fill intermediate or future years |
| CAGR backward | `recoverStartFromCAGR(end, cagr, periods)` | Recover start from end, CAGR, and periods |
| Weighted average | `recoverWeightedComponent(avg, known, weight)` | One component of a weighted average is blank |
| Cross-sheet check | `reconcileTotals(detail, summary, tol)` | Verify detail sums to summary within tolerance |

## Examples

Each example calls the typed functions above and asserts the expected result, so they double as smoke tests for the module.

### Example 1: Row/Column Sum Constraints

A row sums to 1,000 and three of four values are known (200, 300, 400), so the fourth is forced to 100.

```typescript
const missing: number = recoverMissingFromSum(1_000, [200, 300, 400]);
console.assert(missing === 100, `expected 100, received ${missing}`);
```

### Example 2: Year-over-Year (YoY) Change Recovery

A current value of 1,200 followed a +20% year, so the prior year was 1,000.

```typescript
const previous: number = recoverYoYPrevious(1_200, 0.20);
console.assert(previous === 1_000, `expected 1000, received ${previous}`);
```

### Example 3: Percentage Share Recovery

A department holds a 20% share of a 50,000 budget, which is 10,000.

```typescript
const departmentValue: number = recoverShareValue(50_000, 0.20);
console.assert(departmentValue === 10_000, `expected 10000, received ${departmentValue}`);
```

### Example 4: Compound Annual Growth Rate (CAGR)

Growing from 1,000 to 1,500 over 4 periods implies a CAGR of about 10.67% per year.

```typescript
const cagr: number = computeCAGR(1_000, 1_500, 4);
console.assert(
  Math.abs(cagr - 0.1067) < 1e-4,
  `expected approximately 0.1067, received ${cagr}`,
);
```

### Example 5: Weighted-Average Component Recovery

A portfolio with a blended 5% return has two known sleeves (50% weight at 4%, 30% weight at 6%) and one missing sleeve (20% weight). The missing sleeve returned 6%.

```typescript
const missingReturn: number = recoverWeightedComponent(
  0.05,
  [
    { weight: 0.5, value: 0.04 },
    { weight: 0.3, value: 0.06 },
  ],
  0.2,
);
console.assert(missingReturn === 0.06, `expected 0.06, received ${missingReturn}`);
```

## Pitfalls

- **Solving cells out of order** — recovering a cell before its dependencies are anchored produces a plausible-but-wrong number that contaminates every downstream cell. Always map the dependency graph first and solve in topological order.
- **Mixing percentage points and fractions** — passing `20` (meaning 20%) where `0.20` is expected silently inflates results by 100×. The `recoverShareValue` function guards against this by rejecting shares outside `[0, 1]`, but `applyYoYForward` and `recoverYoYPrevious` do not — be disciplined about units.
- **Division by zero in YoY backward recovery** — a fractionalChange of `-1` (−100%) makes `1 + change = 0`, causing division by zero. The guard in `recoverYoYPrevious` throws a `RangeError`, but if you bypass the guard (e.g., in a raw spreadsheet formula), you will get `#DIV/0!` or `Infinity`.
- **Floating-point equality in cross-sheet checks** — two independently summed totals that are mathematically equal will almost never be bit-identical in IEEE 754 floating point. Always use `reconcileTotals` with a tolerance (default `1e-6`) rather than `===`. A strict equality check will flag correct data as broken.
- **Assuming weights sum to 1** — the naive weighted-average formula `(avg − Σ wᵢvᵢ) / w_missing` only works when weights are normalized. The `recoverWeightedComponent` function handles arbitrary weights correctly, but if you write a raw spreadsheet formula, you must account for the total weight explicitly.
- **CAGR with non-positive values** — `computeCAGR` rejects start or end values ≤ 0 because the geometric mean of a ratio involving a non-positive number is not meaningful for currency. If you bypass this guard, `Math.pow` may return `NaN` for negative bases with fractional exponents.
- **Rounding for display breaking totals** — applying `ROUND` to individual cells for display can cause the visible values to no longer sum to the published total. Apply rounding consistently and verify against a tolerance, or round only at the presentation layer.
- **Circular references in multi-sheet chains** — when a recovery on Sheet 2 depends on a value from Sheet 1 that itself depends on Sheet 2, you get `#CIRCULAR!`. Map the dependency graph before writing formulas to detect cycles. If a cycle exists, the system is under-determined and cannot be solved by sequential recovery.
- **Over-determined systems with conflicting totals** — if a stated total disagrees with the sum of its parts, do not silently pick one. This is a real data-quality problem that a human should adjudicate. The `reconcileTotals` function will report the discrepancy but will not resolve it.
- **NaN/Infinity propagation** — a single `NaN` or `Infinity` in a financial total corrupts the entire report without throwing. The `assertFiniteNumber` guard catches this at the source, but if you bypass it (e.g., in raw spreadsheet formulas), the corruption is silent.

## Verification

Run these checks after every reconciliation pass; each one targets a distinct way a recovery can be wrong:

1. **Constraint check** — do all recovered values sum back to the original totals? Confirms the core arithmetic, not just an individual cell.
   ```typescript
   // Verify: recoveredCell + knownValues === total
   const checkSum: number = recoverMissingFromSum(1_000, [200, 300, 400]);
   console.assert(200 + 300 + 400 + checkSum === 1_000, "Sum constraint violated");
   ```

2. **Consistency check** — do recovered YoY percentages match the provided growth rates? Catches a recovery that satisfies one constraint while violating another.
   ```typescript
   const priorYear: number = recoverYoYPrevious(1_200, 0.20);
   console.assert(priorYear * 1.20 === 1_200, "YoY consistency violated");
   ```

3. **Cross-reference check** — do values agree across all related sheets/tabs (within tolerance)? Surfaces stale lookups and out-of-sync summaries.
   ```typescript
   const result: ReconciliationResult = reconcileTotals(
     [210_000, 245_000, 268_000, 277_000],
     1_000_000,
   );
   console.assert(result.reconciled, `Cross-sheet mismatch: difference ${result.difference}`);
   ```

4. **Edge-case check** — are there any division-by-zero, non-positive, or negative inputs in the YoY, share, CAGR, or weighted-average paths? These are exactly the inputs the guards above reject, so a thrown error here is a real data problem to escalate, not a bug to suppress.
   ```typescript
   // These should all throw — if they don't, the guards are broken:
   // recoverYoYPrevious(100, -1)        → RangeError (division by zero)
   // recoverShareValue(100, 1.5)         → RangeError (share > 1)
   // computeCAGR(-100, 200, 4)          → RangeError (startValue <= 0)
   // recoverWeightedComponent(0.05, [], 0) → TypeError / RangeError
   ```

5. **Precision check** — does rounding for display ever break a total? Compare against a tolerance (and apply `ROUND` consistently) so a cosmetic rounding does not appear to violate a constraint.
   ```typescript
   const tolerance: number = 1e-6;
   const roundedSum: number = Math.round(210_000.0000001 + 245_000.0000001 + 268_000.0000001);
   console.assert(Math.abs(roundedSum - 723_000) < tolerance, "Precision check failed");
   ```

## Related Skills

- **data-validation** — for validating data types, ranges, and formats before reconciliation begins.
- **financial-analysis** — for interpreting recovered values in the context of financial statements and ratios.
- **spreadsheet-automation** — for automating reconciliation across large workbooks with scripts and macros.
- **data-cleaning** — for handling missing, malformed, or inconsistent data that cannot be recovered by mathematical constraints alone.
