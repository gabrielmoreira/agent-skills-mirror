---
type: skill
lifecycle: stable
inheritance: inheritable
name: vscode-configuration-validation
description: Validate VS Code extension manifest against runtime code usage
tier: standard
applyTo: '**/*vscode*,**/*configuration*,**/*validation*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# VS Code Extension Configuration Validation


**Domain**: VS Code extension development, configuration management, quality assurance  
**Complexity**: Intermediate  
**Prerequisites**: Understanding of VS Code extension manifest (package.json), TypeScript

## Decision Table

| Symptom | Root Cause | Fix |
|---------|------------|-----|
| Config value not persisting | Key not in `contributes.configuration` | Register in package.json |
| Command "not found" error | Command not in `contributes.commands` | Add command declaration |
| View not rendering | View ID mismatch | Match `id` in viewsContainers/views |
| Context menu missing | `when` clause fails | Fix context key expression |
| Activation too late | Missing activation event | Add `onCommand:*` or `onView:*` |
| Runtime config error | Try-catch missing | Wrap config access in try-catch |

## Problem

VS Code extensions fail at runtime when:

- Configuration keys are updated without being registered in `package.json`
- Commands are invoked but not declared in manifest
- Views/webviews reference unregistered IDs
- Context keys are set but not documented

These misconfigurations don't cause compile-time errors and only surface when users interact with specific features.

## Solution

Systematic validation of VS Code extension manifest against runtime code usage.

### 1. Configuration Registration Validation

**Check**: All `workspace.getConfiguration().update()` calls reference registered properties.

```typescript
// ❌ WRONG - config key not registered
await vscode.workspace.getConfiguration('alex.skillRecommendations')
  .update('code-review.accepted', count + 1, ConfigurationTarget.Global);

// ✅ RIGHT - key registered in package.json or wrapped in try-catch
try {
  await vscode.workspace.getConfiguration('alex.skillRecommendations')
    .update('code-review.accepted', count + 1, ConfigurationTarget.Global);
} catch (error) {
  console.log(`Skip tracking: ${error}`);
}
```

**Audit Pattern**:

```bash
# Find all config.update() calls
grep -r "getConfiguration.*\.update\(" src/

# Cross-reference with package.json properties section
# Each update() key must exist in "configuration.properties"
```

### 2. Command Registration Validation

**Check**: All `commands.registerCommand()` calls match declared commands in manifest.

```typescript
// Code registration
vscode.commands.registerCommand('alex.validateHeir', async () => {...});

// Must have package.json declaration
{
  "contributes": {
    "commands": [{
      "command": "alex.validateHeir",
      "title": "Validate as Heir Project"
    }]
  }
}
```

**Audit Pattern**:

```bash
# Find all command registrations
grep -r "registerCommand\(['\"]alex\." src/

# Extract command names and verify each exists in package.json
```

### 3. Configuration Read Validation

**Check**: All `getConfiguration().get()` calls match registered properties.

```typescript
// This config read should have a registered property
const enabled = vscode.workspace.getConfiguration('alex.voice').get('enabled', false);

// Check package.json has "alex.voice.enabled"
```

**Warning Pattern**: Configuration reads with no defaults are risky:

```typescript
// ⚠️ No fallback - will be undefined if not registered
const value = config.get('someKey');

// ✅ Better - always provide default
const value = config.get('someKey', defaultValue);
```

### 4. Error Handling Patterns

**For Dynamic Configuration Keys** (skill recommendations, user preferences):

Option A: Register schema with dynamic pattern (complex)
Option B: Graceful try-catch (simple, recommended)

```typescript
// Pattern: Non-critical dynamic config
async function trackUserPreference(key: string, value: any) {
  try {
    await vscode.workspace.getConfiguration('alex.dynamic')
      .update(key, value, ConfigurationTarget.Global);
  } catch (error) {
    // Log but don't fail - tracking is optional
    console.log(`[the AI assistant] Skipping preference tracking: ${error}`);
  }
}
```

**For Critical Configuration**:

```typescript
// Pattern: Essential config must be registered
await vscode.workspace.getConfiguration('alex.globalKnowledge')
  .update('remoteRepo', repo, ConfigurationTarget.Global);
// No try-catch - failure should bubble up
```

## Validation Checklist

### Pre-Publish Review

- [ ] Search code for `getConfiguration().update()` calls
- [ ] Verify each updated key exists in `package.json` properties OR has try-catch
- [ ] Search for `registerCommand()` calls
- [ ] Verify each command exists in `contributes.commands`
- [ ] Check for dynamic config patterns (user tracking, etc.)
- [ ] Apply graceful degradation pattern for non-critical features

### Automated Audit Script

```text
Pseudocode: validate-manifest
1. Search src/**/*.ts for getConfiguration('section').update('key') calls
2. Load contributes.configuration.properties from package.json
3. For each config update found in source code:
   If the full key (section.key) is NOT in package.json properties:
     Flag as unregistered config write (potential runtime error)
4. Report all mismatches
```

    $issues += "⚠️  $fullKey - not registered (verify try-catch exists)"
  }
}

if ($issues.Count -gt 0) {
  Write-Host "Configuration validation issues:" -ForegroundColor Yellow
  $issues | ForEach-Object { Write-Host $_ }
  exit 1
}

```

## Common Pitfalls

1. **Dynamic Configuration Keys**: User preferences, tracking counters
   - **Solution**: Either register dynamic schema or use try-catch pattern

2. **Namespaced Configuration**: `alex.skill.subkey.value`
   - **Solution**: Register full dotted path: `"alex.skill.subkey.value": {...}`

3. **Multi-Target Updates**: Workspace vs Global vs WorkspaceFolder
   - **Solution**: Test configuration across all scopes

4. **Configuration Migration**: Deprecated settings
   - **Solution**: Use `deprecationMessage` in property definition

## Real-World Example: Skill Recommendations

**Problem**: Tracking skill usage without bloating package.json with hundreds of dynamic keys.

**Solution**: Graceful degradation pattern
```typescript
async function trackRecommendation(skillId: string, accepted: boolean) {
  try {
    const context = 'alex.skillRecommendations';
    const key = `${skillId}.${accepted ? 'accepted' : 'dismissed'}`;
    const current = vscode.workspace.getConfiguration(context).get<number>(key, 0);
    await vscode.workspace.getConfiguration(context).update(
      key, 
      current + 1, 
      vscode.ConfigurationTarget.Global
    );
  } catch (error) {
    // Feature degrades gracefully - recommendations still work
    console.log(`[the AI assistant] Skipping recommendation tracking: ${error}`);
  }
}
```

**Why This Works**:

- Feature works with or without tracking
- No user-facing error for unregistered config
- Logging helps debug if tracking is important
- Simple implementation vs complex dynamic schema

## Integration with Existing QA

Add to `.github/instructions/extension-audit-methodology.instructions.md`:

```markdown
### Configuration Validation

Before each release:
1. Run `node scripts/release-preflight.cjs`
2. Review any warnings for try-catch coverage
3. Test configuration updates in clean VS Code instance
4. Verify error messages are user-friendly
```

## Resources

- [VS Code Extension Manifest](https://code.visualstudio.com/api/references/extension-manifest)
- [Configuration API](https://code.visualstudio.com/api/references/vscode-api#workspace.getConfiguration)
- [Package.json Contribution Points](https://code.visualstudio.com/api/references/contribution-points)

---

**Sources of Truth**:

- Incident: Skill recommendations broken due to unregistered config (2026-02-15)
- Root Cause: `alex.skillRecommendations.*` keys not in package.json
- Fix: Try-catch wrapper in `src/chat/skillRecommendations.ts`
