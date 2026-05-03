---
type: skill
lifecycle: stable
inheritance: inheritable
name: config-transcription-verification
description: When extracting hardcoded data to JSON, field values silently drift:
tier: standard
applyTo: '**/*config*,**/*transcription*,**/*verification*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Config Transcription Verification

## The Problem

When extracting hardcoded data to JSON, field values silently drift:

```javascript
// Original code
const buttons = [
  { icon: 'play', label: 'Start', action: 'start' },
  { icon: 'stop', label: 'Stop', action: 'stop' }
];
```

```json
// Transcribed JSON (with typos)
{
  "buttons": [
    { "icon": "play", "label": "Start", "action": "begin" },
    { "icon": "pause", "label": "Stop", "action": "stop" }
  ]
}
```

Two errors: `action: "begin"` instead of `"start"`, `icon: "pause"` instead of `"stop"`.

## The Solution

Cross-check every field against the source.

### Manual Verification Checklist

```markdown
## Transcription Verification

Source: `src/buttons.js` lines 12-18

| Field | Original | JSON | ✓ |
|-------|----------|------|---|
| button[0].icon | play | play | ✅ |
| button[0].label | Start | Start | ✅ |
| button[0].action | start | start | ✅ |
| button[1].icon | stop | stop | ✅ |
| button[1].label | Stop | Stop | ✅ |
| button[1].action | stop | stop | ✅ |
```

### Automated Verification Script

```javascript
// scripts/verify-transcription.cjs
const source = require('../src/buttons.js').buttons;
const transcribed = require('../config/buttons.json').buttons;

source.forEach((srcItem, i) => {
  const jsonItem = transcribed[i];
  Object.keys(srcItem).forEach(key => {
    if (srcItem[key] !== jsonItem[key]) {
      console.error(`Mismatch at [${i}].${key}: "${srcItem[key]}" vs "${jsonItem[key]}"`);
      process.exitCode = 1;
    }
  });
});

if (!process.exitCode) console.log('Transcription verified ✓');
```

## High-Risk Fields

| Field Type | Risk | Verification |
|------------|------|--------------|
| Icon names | High — typos render wrong icon | Visual check |
| Action strings | High — breaks functionality | Unit test |
| Labels | Medium — visible to users | Spell check |
| IDs | High — breaks references | Grep for usage |

## Verification

1. Every field in original has matching field in JSON
2. No extra fields added
3. Order preserved where it matters
4. Verification script passes

## When to Apply

- Extracting config from code
- Migrating between formats
- Manual data entry from specs
- Any transcription task

## Tags

`build` `configuration` `verification` `migration`
