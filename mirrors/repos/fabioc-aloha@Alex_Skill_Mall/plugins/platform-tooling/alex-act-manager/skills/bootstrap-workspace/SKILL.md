---
name: bootstrap-workspace
description: "Bootstrap repository-scoped VS Code workspace files for a plugin-native Alex ACT workspace. Use when a new repository lacks Markdown Preview CSS, the current workspace needs the explicit /alex-act-manager bootstrap-workspace repair path, or a repo needs deterministic .vscode/settings.json and .gitignore setup without touching user settings."
lastReviewed: 2026-08-02
---

# Bootstrap Workspace

Provision the current repository's workspace files for plugin-native Alex ACT use. This skill owns repository scope only.

## When to fire

- A new plugin-native workspace has no `.vscode/markdown-light.css`
- A repository is missing workspace-scoped Markdown Preview CSS wiring
- The heir asks for `/alex-act-manager bootstrap-workspace`
- A workspace needs deterministic repair after manual drift in `.vscode/settings.json` or `.gitignore`

## Scope

- Current repository by default, or an explicit `--target` repository path
- Repository files only: `.vscode/markdown-light.css`, `.vscode/settings.json`, and `.gitignore` when a broad `.vscode` ignore rule hides managed files
- Never user settings
- Never network access

## Runtime

The deterministic runtime is shared at `../plugin-management/scripts/manager-operations.cjs` so Manager owns one lifecycle runtime instead of duplicating scripts across commands.

Command surface:

```text
node <plugin-management-skill>/scripts/manager-operations.cjs bootstrap-workspace [--target <path>] [--refresh-css] [--apply]
```

Rules:

- No `--apply` means preview only
- `--refresh-css` changes a differing existing CSS action from `preserve` to `refresh`; it still writes only with `--apply`
- Unknown arguments or a missing `--target` value fail fast
- Default target is `process.cwd()`
- The script prints the exact JSON plan before any write

## Preview contract

Run preview first. The preview output is the decision surface.

The plan must remain a JSON object with this shape:

```json
{
  "target": "<absolute workspace path>",
  "apply": false,
  "css": {
    "action": "create | preserve | refresh",
    "source": "<absolute source path>",
    "destination": "<absolute destination path>",
    "bytes": 0,
    "sha256": "<hex>",
    "currentSha256": "<hex-or-null>",
    "matchesSource": false
  },
  "settings": {
    "action": "create | merge | preserve",
    "destination": "<absolute settings path>",
    "changes": [],
    "skipped": [],
    "hadComments": false
  },
  "gitignore": {
    "action": "none | narrow-vscode-rule",
    "file": "<absolute gitignore path>",
    "changes": []
  }
}
```

Show this exact JSON plan to the user before asking for consent.

## Apply contract

Only run `--apply` after an explicit yes.

### CSS behavior

- Source is the bundled `resources/markdown-light.css` in this skill
- If `.vscode/markdown-light.css` is absent, create it
- If it already exists, preserve it byte-for-byte
- If it differs, report both hashes; refresh it only after explicit approval by rerunning with `--refresh-css --apply`
- Verify the destination SHA-256 after a copy

### Settings behavior

- Use `set-if-absent` semantics for `markdown.styles`
- Parse `.vscode/settings.json` as JSONC
- Preserve unrelated keys semantically
- Stop on malformed JSON or JSONC before any write
- Add `"markdown.styles": [".vscode/markdown-light.css"]` only when the key is absent
- Preserve any existing `markdown.styles` value exactly, including custom arrays and `null`
- Do not replace comments with model-authored prose; the merger owns the parse and rewrite behavior

### .gitignore behavior

- Only act when a broad `.vscode` ignore rule hides `settings.json` or `markdown-light.css`
- Narrow that single broad rule to tracked-file exceptions
- Preserve unrelated `.gitignore` rules exactly
- Never widen tracking beyond the two managed workspace files

### Write discipline

- Create `.vscode/` only when needed
- Use atomic sibling temp files plus rename for `.vscode/settings.json` and `.gitignore`
- No network fetch, no remote version lookup, no user-scope side effects

## Verification

After apply, report deterministic evidence:

- target path
- CSS action and destination
- settings action and destination
- `.gitignore` action and destination
- CSS byte count
- CSS SHA-256
- settings changes
- settings skips
- whether the run was idempotent or wrote files

If a second apply would change nothing, say so explicitly.

## Rollback

Rollback is repository-local:

- remove `.vscode/markdown-light.css` only if this skill created it and the heir wants it removed
- restore `.vscode/settings.json` and `.gitignore` from version control or local backups if the heir wants to undo the merge
- never attempt rollback in user settings, because this skill never mutates them

## Distinction from configure-vscode

`bootstrap-workspace` owns repository scope.

`configure-vscode` owns user scope.

Rules:

- Workspace-relative local CSS such as `.vscode/markdown-light.css` is supported here
- User-scope guidance must not recommend absolute local file paths for `markdown.styles`
- User-scope CSS guidance must use HTTPS if a user-level stylesheet is needed
- If the heir asks for user settings, route to `/alex-act-manager configure-vscode`

## Anti-patterns

| Anti-pattern | Correction |
| --- | --- |
| Applying without preview | Preview first, always show the JSON plan, then ask for explicit consent. |
| Replacing an existing workspace stylesheet | Preserve existing CSS byte-for-byte. |
| Hiding CSS drift behind `preserve` | Report both hashes and offer the explicit `--refresh-css` preview. |
| Overwriting a custom or null `markdown.styles` value | Set the key only when absent; preserve existing values exactly. |
| Rewriting `.gitignore` broadly | Narrow only the broad `.vscode` rule that blocks the two managed files. |
| Treating this as a user-settings repair | Repository scope only. Route user-scope work to `configure-vscode`. |
| Pulling CSS or settings from the network | Use only bundled local assets. |
| Reporting a package failure when the host only lacks generic skill-tool exposure | Read the installed `SKILL.md` directly and continue with the deterministic steps. |

## Related

- `configure-vscode.prompt.md` for user-scope VS Code settings
- Markdown and Mermaid authoring remains a Core capability; Manager bundles only the CSS asset needed for workspace setup
- [`plugin-management`](../plugin-management/SKILL.md) for namespaced command fallback discipline

## Would Revise If

- The preview plan stops matching the runtime contract by **2026-11-02**
- A second run is not idempotent by **2026-11-02**
- The skill mutates user settings or reaches the network even once by **2026-11-02**
- The JSONC-safe merge fails to preserve an existing custom or `null` `markdown.styles` value by **2026-11-02**
- Heirs report that the repo-scope and user-scope boundary remains unclear after using this skill by **2026-11-02**
