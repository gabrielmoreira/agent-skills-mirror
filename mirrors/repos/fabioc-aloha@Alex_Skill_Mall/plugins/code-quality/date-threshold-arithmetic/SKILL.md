---
type: skill
lifecycle: stable
inheritance: inheritable
name: date-threshold-arithmetic
description: Date comparisons at thresholds fail due to fractional days:
tier: standard
applyTo: '**/*date*,**/*threshold*,**/*arithmetic*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Date Threshold Arithmetic

## The Problem

Date comparisons at thresholds fail due to fractional days:

```javascript
const daysBetween = (Date.now() - someDate.getTime()) / (1000 * 60 * 60 * 24);

// someDate is "exactly 7 days ago"
// daysBetween = 7.000012 (due to milliseconds)
// if (daysBetween > 7) { ... } // TRUE — unexpected!
```

## The Solution

Always `Math.floor()` before threshold comparison.

```javascript
function daysSince(date) {
  const ms = Date.now() - new Date(date).getTime();
  return Math.floor(ms / (1000 * 60 * 60 * 24));
}

// Now "exactly 7 days" = 7, not 7.000012
if (daysSince(lastCheck) > 7) {
  // Truly more than 7 full days
}
```

## Common Traps

| Code | Bug |
|------|-----|
| `days > 7` | Triggers on 7.0001 |
| `days >= 7` | Doesn't trigger on 6.9999 |
| `days === 7` | Never true for fractional values |

## Safe Patterns

```javascript
// Days since (full days only)
const fullDays = Math.floor((now - then) / MS_PER_DAY);

// Is it past the threshold?
if (fullDays > threshold) { ... }

// Is it on or past the threshold?
if (fullDays >= threshold) { ... }

// Is it exactly N days?
if (fullDays === threshold) { ... }
```

## For Cron-Style Checks

```javascript
// "Run if last run was more than 24 hours ago"
const lastRun = new Date(stored.lastRunTime);
const hoursSince = (Date.now() - lastRun.getTime()) / (1000 * 60 * 60);

// Use Math.floor for "full hours"
if (Math.floor(hoursSince) >= 24) {
  runTask();
}
```

## Verification

```javascript
// Test edge case
const exactlySevenDaysAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
console.log(daysSince(exactlySevenDaysAgo)); // Should be 7, not 7.xxx
```

## When to Apply

- Cache expiration checks
- "Last N days" filters
- Scheduled task triggers
- Any date-based threshold

## Tags

`quality` `dates` `javascript` `bugs`
