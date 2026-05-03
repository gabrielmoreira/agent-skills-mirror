---
type: skill
lifecycle: stable
inheritance: inheritable
name: default-fast-opt-slow
description: AI/LLM features default to verbose responses, causing:
tier: standard
applyTo: '**/*default*,**/*fast*,**/*opt*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Default to Fast, Opt Into Slow

## The Problem

AI/LLM features default to verbose responses, causing:

- Long wait times for simple queries
- Token/cost waste
- User frustration

Users who want depth will ask for it.

## The Solution

Default to the shortest useful response length. Let users opt into more.

```javascript
// Default: concise
const DEFAULT_RESPONSE_LENGTH = 'concise';

// User can select
const responseLengths = {
  concise: { maxTokens: 150, instruction: 'Be brief. One paragraph max.' },
  standard: { maxTokens: 500, instruction: 'Provide a clear explanation.' },
  detailed: { maxTokens: 2000, instruction: 'Explain thoroughly with examples.' }
};

// Persist preference
function getResponseConfig(userId) {
  const pref = localStorage.getItem(`response-length-${userId}`);
  return responseLengths[pref] || responseLengths[DEFAULT_RESPONSE_LENGTH];
}
```

### UI Pattern

```html
<!-- Simple toggle in UI -->
<select id="response-length">
  <option value="concise" selected>Quick (default)</option>
  <option value="standard">Standard</option>
  <option value="detailed">Detailed</option>
</select>
```

## Persist Preference

Once a user selects "detailed," remember it:

```javascript
// Save on change
select.addEventListener('change', (e) => {
  localStorage.setItem('response-length', e.target.value);
});

// Restore on load
const saved = localStorage.getItem('response-length');
if (saved) select.value = saved;
```

## Verification

1. Fresh user gets concise responses
2. User can switch to detailed
3. Preference persists across sessions
4. Response length actually changes

## When to Apply

- LLM-powered features
- API responses with variable depth
- Documentation generation
- Any feature where "more" costs time/resources

## Tags

`architecture` `ux` `llm` `performance`
