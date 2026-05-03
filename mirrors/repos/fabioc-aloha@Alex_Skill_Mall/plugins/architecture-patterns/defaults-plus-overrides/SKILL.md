---
type: skill
lifecycle: stable
inheritance: inheritable
name: defaults-plus-overrides
description: Provide sensible defaults with user-overridable configuration — reduce boilerplate without limiting flexibility
tier: standard
applyTo: '**/*defaults*,**/*plus*,**/*overrides*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Defaults Plus Overrides

**Category**: Architecture
**Time Saved**: 2+ hours avoiding configuration complexity
**Battle-tested**: Yes — user preference systems, role-based config

---

## The Problem

You're building a system with configurable behavior — user preferences, role-based permissions, or tenant-specific settings. You need sensible defaults but also flexibility. You end up with either rigid presets OR overwhelming configuration options.

## Why It's Hard

- **Too rigid**: Users can't customize what they need
- **Too flexible**: Users must configure everything
- **Presets only**: Edge cases require workarounds
- **Full config**: Decision fatigue, misconfiguration risk

## The Rule

**Provide role/archetype defaults, allow partial overrides, clamp to safe bounds.**

## The Pattern

```
Archetype Default + User Overrides + Bounds Clamping = Final Config
```

### Step 1: Define Archetypes

```javascript
const ARCHETYPES = {
  developer: {
    verbosity: 'detailed',
    theme: 'dark',
    shortcuts: true,
    maxTokens: 4000,
    autoSave: true,
  },
  executive: {
    verbosity: 'concise',
    theme: 'light',
    shortcuts: false,
    maxTokens: 1000,
    autoSave: false,
  },
  researcher: {
    verbosity: 'detailed',
    theme: 'auto',
    shortcuts: true,
    maxTokens: 8000,
    autoSave: true,
  },
};
```

### Step 2: Define Bounds

```javascript
const BOUNDS = {
  maxTokens: { min: 100, max: 16000 },
  verbosity: ['concise', 'normal', 'detailed'],
  theme: ['light', 'dark', 'auto'],
};
```

### Step 3: Merge with Clamping

```javascript
function resolveConfig(archetype, overrides = {}) {
  // Start with archetype defaults
  const base = { ...ARCHETYPES[archetype] };
  
  // Apply user overrides
  const merged = { ...base, ...overrides };
  
  // Clamp to bounds
  return clampConfig(merged, BOUNDS);
}

function clampConfig(config, bounds) {
  const result = { ...config };
  
  for (const [key, constraint] of Object.entries(bounds)) {
    if (constraint.min !== undefined) {
      // Numeric bound
      result[key] = Math.max(constraint.min, Math.min(constraint.max, result[key]));
    } else if (Array.isArray(constraint)) {
      // Enum bound
      if (!constraint.includes(result[key])) {
        result[key] = constraint[0]; // Default to first option
      }
    }
  }
  
  return result;
}
```

### Step 4: Usage

```javascript
// User selects archetype, optionally overrides specific values
const userConfig = resolveConfig('developer', {
  theme: 'light',        // Override: prefer light theme
  maxTokens: 50000,      // Will be clamped to 16000
});

// Result:
// {
//   verbosity: 'detailed',  // From archetype
//   theme: 'light',         // User override
//   shortcuts: true,        // From archetype
//   maxTokens: 16000,       // Clamped from 50000
//   autoSave: true,         // From archetype
// }
```

## JSON Schema Example

```json
{
  "type": "object",
  "properties": {
    "archetype": {
      "type": "string",
      "enum": ["developer", "executive", "researcher"],
      "default": "developer"
    },
    "overrides": {
      "type": "object",
      "properties": {
        "verbosity": {
          "type": "string",
          "enum": ["concise", "normal", "detailed"]
        },
        "maxTokens": {
          "type": "integer",
          "minimum": 100,
          "maximum": 16000
        }
      }
    }
  }
}
```

## UI Pattern

```
┌─────────────────────────────────────┐
│ Profile: [Developer ▾]             │
├─────────────────────────────────────┤
│ ☑ Use defaults                      │
│                                     │
│ Customize:                          │
│   Theme: [Light ▾]                  │
│   Max Tokens: [====|====] 4000      │
│   ☐ Auto-save                       │
│                                     │
│ [Reset to defaults]                 │
└─────────────────────────────────────┘
```

## When to Use

| Scenario | Defaults-Plus-Overrides? |
|----------|-------------------------|
| User preferences | ✅ Yes |
| Role-based permissions | ✅ Yes |
| Tenant configuration | ✅ Yes |
| Feature flags | ⚠️ Maybe (often boolean) |
| Security settings | ❌ No (strict policy) |

## Anti-Patterns

| Anti-Pattern | Problem |
|--------------|---------|
| No defaults | Users must configure everything |
| No overrides | Power users can't customize |
| No bounds | Invalid configurations possible |
| Archetype-only | Can't handle edge cases |
| Everything configurable | Decision paralysis |

## Verification Checklist

- [ ] Archetypes cover 80% of users out of the box
- [ ] Overrides are partial (don't require full config)
- [ ] Bounds prevent invalid/dangerous values
- [ ] Reset-to-defaults option exists
- [ ] Configuration is validated at load time

## Related Skills

- `universal-audit-pattern` — Validating configuration
