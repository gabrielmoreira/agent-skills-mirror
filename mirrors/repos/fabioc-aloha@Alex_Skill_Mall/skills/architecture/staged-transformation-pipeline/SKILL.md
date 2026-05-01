---
type: skill
lifecycle: stable
inheritance: inheritable
name: staged-transformation-pipeline
description: Monolithic transformations are hard to test and debug:
tier: standard
applyTo: '**/*staged*,**/*transformation*,**/*pipeline*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Staged Transformation Pipeline

## The Problem

Monolithic transformations are hard to test and debug:

```javascript
// Bad: everything in one function
function processInput(input) {
  // 200 lines of parsing, validation, transformation, formatting
  return output;
}
```

When something breaks, you don't know which stage failed.

## The Solution

Input flows through discrete stages. Each stage is independently testable.

```javascript
// Define stages
const stages = {
  parse: (input) => JSON.parse(input),
  validate: (data) => {
    if (!data.id) throw new Error('Missing id');
    return data;
  },
  transform: (data) => ({
    ...data,
    processedAt: new Date().toISOString()
  }),
  format: (data) => JSON.stringify(data, null, 2)
};

// Pipeline runner
function runPipeline(input, stageOrder = ['parse', 'validate', 'transform', 'format']) {
  let result = input;
  for (const stageName of stageOrder) {
    try {
      result = stages[stageName](result);
    } catch (err) {
      throw new Error(`Pipeline failed at stage '${stageName}': ${err.message}`);
    }
  }
  return result;
}
```

## Benefits

### 1. Independent Testing

```javascript
// Test each stage in isolation
describe('validate stage', () => {
  it('rejects missing id', () => {
    expect(() => stages.validate({})).toThrow('Missing id');
  });
  
  it('passes valid data through', () => {
    expect(stages.validate({ id: 1 })).toEqual({ id: 1 });
  });
});
```

### 2. Stage Replacement

```javascript
// Swap out a stage without touching others
stages.format = (data) => yaml.dump(data);  // Now outputs YAML
```

### 3. Debugging

```javascript
// Log between stages
function debugPipeline(input, stageOrder) {
  let result = input;
  for (const stageName of stageOrder) {
    console.log(`[${stageName}] Input:`, result);
    result = stages[stageName](result);
    console.log(`[${stageName}] Output:`, result);
  }
  return result;
}
```

## Stage Design Rules

1. **Pure functions** — no side effects within stages
2. **Single responsibility** — one transformation per stage
3. **Typed contracts** — each stage has clear input/output types
4. **Fail fast** — validate early, don't propagate bad data

## Verification

- Each stage has unit tests
- Pipeline produces correct final output
- Errors identify which stage failed

## When to Apply

- Data import/export
- Content transformation (markdown → HTML)
- ETL pipelines
- Build systems
- Any multi-step processing

## Tags

`architecture` `pipeline` `testing` `transformation`
