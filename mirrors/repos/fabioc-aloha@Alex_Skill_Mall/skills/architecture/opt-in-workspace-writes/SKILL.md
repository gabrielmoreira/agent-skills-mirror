---
type: skill
lifecycle: stable
inheritance: inheritable
name: opt-in-workspace-writes
description: Extensions/tools that auto-write to user workspaces without consent:
tier: standard
applyTo: '**/*opt*,**/*workspace*,**/*writes*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Opt-In for Workspace Writes

## The Problem

Extensions/tools that auto-write to user workspaces without consent:

- Create `.vscode/` folders unexpectedly
- Add config files that get committed accidentally
- Scaffold structures the user didn't want
- Violate the principle of least surprise

## The Solution

Get explicit consent before any workspace mutation.

### 1. Ask First

```typescript
const choice = await vscode.window.showInformationMessage(
  'Initialize Alex configuration in this workspace?',
  { modal: true },
  'Yes, create .github/',
  'No, skip'
);

if (choice !== 'Yes, create .github/') {
  return; // User declined, do nothing
}
```

### 2. Show What Will Be Created

```typescript
const files = [
  '.github/copilot-instructions.md',
  '.github/config/settings.json'
];

const choice = await vscode.window.showInformationMessage(
  `This will create ${files.length} files:\n${files.join('\n')}`,
  { modal: true, detail: files.join('\n') },
  'Create Files',
  'Cancel'
);
```

### 3. Provide Undo/Remove

```typescript
// After creating files
vscode.window.showInformationMessage(
  'Configuration created.',
  'Undo'
).then(selection => {
  if (selection === 'Undo') {
    // Delete the created files
    files.forEach(f => fs.unlinkSync(path.join(workspaceRoot, f)));
  }
});
```

## Never Auto-Write These

| Path | Why It's Dangerous |
|------|-------------------|
| `.vscode/` | Shared via git, affects all developers |
| `.github/` | Shared via git, affects CI/CD |
| `package.json` | Changes dependencies/scripts |
| `.gitignore` | Affects what's tracked |
| Root config files | `.eslintrc`, `tsconfig.json`, etc. |

## Acceptable Auto-Behavior

- Reading files (no consent needed)
- Writing to temp directories
- Writing to user-global config (already your data)
- Writing to extension storage area

## Verification

1. Fresh install → no files created until user opts in
2. User can decline and extension still works
3. Created files are clearly attributed to the extension

## When to Apply

- Extension activation
- Command that generates files
- Any feature that modifies workspace

## Tags

`architecture` `extension-development` `ux` `consent`
