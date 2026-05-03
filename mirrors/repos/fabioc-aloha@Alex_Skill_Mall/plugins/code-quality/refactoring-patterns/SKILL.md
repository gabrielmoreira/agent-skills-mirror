---
type: skill
lifecycle: stable
inheritance: inheritable
name: refactoring-patterns
description: Safe transformations — same behavior, better structure.
tier: standard
applyTo: '**/*refactoring*,**/*patterns*'
currency: 2026-04-20
lastReviewed: 2026-04-30
---

# Refactoring Patterns Skill


> Safe transformations — same behavior, better structure.

## Golden Rule

Tests pass before AND after. Never refactor and add features in the same commit.

## When to Refactor

| Trigger | Action |
| ------- | ------ |
| Feature is hard to add | Refactor first, then add feature |
| Same bug twice | Refactor to prevent recurrence |
| "I don't understand" | Refactor for clarity |
| Duplicate code | Extract and reuse |
| Long function (>30 lines) | Extract logical units |

## When NOT to Refactor

- No tests + time pressure
- Code won't change again
- Right before release (deadline pressure)
- Should rewrite instead (>70% changes needed)
- Exploratory/prototype code

## Core Refactoring Moves

### Extract Function

When a block does one logical thing, give it a name.

```typescript
// Before
function processOrder(order: Order) {
  // Validate order
  if (!order.items.length) throw new Error('Empty order');
  if (!order.customer) throw new Error('No customer');
  if (order.total < 0) throw new Error('Invalid total');
  
  // Calculate tax
  const taxRate = order.region === 'EU' ? 0.20 : 0.10;
  const tax = order.total * taxRate;
  
  // Apply discount
  const discount = order.customer.isPremium ? 0.15 : 0;
  const finalTotal = order.total + tax - (order.total * discount);
  
  return finalTotal;
}

// After
function processOrder(order: Order) {
  validateOrder(order);
  const tax = calculateTax(order);
  const discount = calculateDiscount(order);
  return order.total + tax - discount;
}

function validateOrder(order: Order): void {
  if (!order.items.length) throw new Error('Empty order');
  if (!order.customer) throw new Error('No customer');
  if (order.total < 0) throw new Error('Invalid total');
}

function calculateTax(order: Order): number {
  const taxRate = order.region === 'EU' ? 0.20 : 0.10;
  return order.total * taxRate;
}

function calculateDiscount(order: Order): number {
  return order.customer.isPremium ? order.total * 0.15 : 0;
}
```

### Extract Variable

Name complex expressions to reveal intent.

```typescript
// Before
if (user.age >= 18 && user.country === 'US' && !user.banned && user.emailVerified) {
  allowAccess();
}

// After
const isAdult = user.age >= 18;
const isUSResident = user.country === 'US';
const isInGoodStanding = !user.banned && user.emailVerified;
const canAccess = isAdult && isUSResident && isInGoodStanding;

if (canAccess) {
  allowAccess();
}
```

### Rename for Intent

Names should reveal what, not how.

```typescript
// Before
const d = new Date().getTime() - start;
const arr = users.filter(u => u.a);

// After
const elapsedMs = new Date().getTime() - startTime;
const activeUsers = users.filter(user => user.isActive);
```

### Replace Conditional with Polymorphism

```typescript
// Before
function calculatePay(employee: Employee): number {
  switch (employee.type) {
    case 'hourly':
      return employee.hours * employee.rate;
    case 'salaried':
      return employee.salary / 12;
    case 'commission':
      return employee.sales * employee.commissionRate + employee.basePay;
  }
}

// After
interface PayStrategy {
  calculate(employee: Employee): number;
}

class HourlyPay implements PayStrategy {
  calculate(emp: Employee): number {
    return emp.hours * emp.rate;
  }
}

class SalariedPay implements PayStrategy {
  calculate(emp: Employee): number {
    return emp.salary / 12;
  }
}

class CommissionPay implements PayStrategy {
  calculate(emp: Employee): number {
    return emp.sales * emp.commissionRate + emp.basePay;
  }
}
```

### Guard Clauses (Replace Nested Conditionals)

```typescript
// Before
function getPayAmount(employee: Employee): number {
  let result: number;
  if (employee.isSeparated) {
    result = 0;
  } else {
    if (employee.isRetired) {
      result = employee.pension;
    } else {
      result = employee.salary;
    }
  }
  return result;
}

// After
function getPayAmount(employee: Employee): number {
  if (employee.isSeparated) return 0;
  if (employee.isRetired) return employee.pension;
  return employee.salary;
}
```

## Code Smells → Refactoring

| Smell | Symptoms | Refactoring |
| ----- | -------- | ----------- |
| Long function | >30 lines, multiple comments explaining sections | Extract Function |
| Long parameter list | >4 parameters | Introduce Parameter Object |
| Duplicate code | Same logic in 2+ places | Extract Function, Pull Up Method |
| Feature envy | Method uses another object's data more than its own | Move Function |
| Large class | Class does too many things | Extract Class |
| Primitive obsession | Using primitives instead of small objects | Replace Primitive with Object |
| Data clumps | Same group of variables appear together | Introduce Parameter Object |
| Switch statements | Type-based conditionals | Replace Conditional with Polymorphism |
| Temporary field | Field only used sometimes | Extract Class |
| Refused bequest | Subclass ignores inherited methods | Replace Inheritance with Delegation |

## Refactor vs Rewrite Decision

| Refactor | Rewrite |
| -------- | ------- |
| Core design is sound | Fundamental design is wrong |
| Tests exist and pass | Code is untestable |
| <30% of code changes | >70% of code changes |
| Incremental improvement | Complete replacement |
| Low risk | Higher risk |
| Keep shipping features | Pause feature work |

## Safe Refactoring Workflow

```text
1. Commit current state (safety net)
2. Run all tests (establish baseline)
3. Make ONE small change
4. Run tests
5. Commit with descriptive message
6. Repeat steps 3-5
```

**Never**: Refactor while adding features. Refactor OR feature, never both.

## IDE Refactoring Support

Most refactorings are automated in VS Code:

| Refactoring | VS Code Shortcut |
| ----------- | ---------------- |
| Rename Symbol | F2 |
| Extract Function | Ctrl+Shift+R → Extract Function |
| Extract Variable | Ctrl+Shift+R → Extract Variable |
| Inline Variable | Ctrl+Shift+R → Inline Variable |
| Move to File | Ctrl+Shift+R → Move to new file |

**Prefer IDE refactoring over manual edits** — fewer mistakes, automatic reference updates.
