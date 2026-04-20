# git-commit

Use this skill when writing git commit messages, PR descriptions, changelogs, or release notes.

---

## Commit Message Format

Always use Conventional Commits:

```
<type>(<scope>): <subject>

<body - optional>

<footer - optional>
```

### Type

| Type | When to use |
|---|---|
| `feat` | New feature visible to users |
| `fix` | Bug fix |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `perf` | Performance improvement |
| `test` | Adding or fixing tests |
| `docs` | Documentation only |
| `chore` | Build, tooling, dependency updates |
| `ci` | CI/CD pipeline changes |
| `revert` | Reverting a previous commit |

### Subject Line Rules

- Imperative mood: "add login" not "added login" or "adds login"
- No capital first letter
- No period at the end
- Max 72 characters
- Must complete the sentence: "If applied, this commit will **<subject>**"

### Body Rules

- Wrap at 72 characters
- Explain *what* and *why*, not *how* (the diff shows how)
- Separate from subject with a blank line
- Use only when the change needs explanation beyond the subject

### Footer

- `BREAKING CHANGE: <description>` for breaking API changes
- `Closes #123`, `Fixes #456` for issue references
- `Co-authored-by: Name <email>` for pair work

---

## Examples

**Simple fix:**
```
fix(auth): prevent token refresh loop on 401 response
```

**Feature with body:**
```
feat(api): add pagination to /users endpoint

Previously the endpoint returned all users in a single response,
which caused timeouts for accounts with > 10k users.

Adds cursor-based pagination with a default page size of 50.
Existing clients are unaffected - the endpoint returns all results
when no cursor param is provided.

Closes #892
```

**Breaking change:**
```
refactor(config): rename DATABASE_URL to DB_CONNECTION_STRING

BREAKING CHANGE: The DATABASE_URL environment variable is no longer
read. Rename it to DB_CONNECTION_STRING in all deployment configs.
```

---

## PR Description Format

```
## What

One paragraph: what this PR does and why.

## How

Brief explanation of the approach taken. Link to relevant docs or
prior art if the approach is non-obvious.

## Testing

How you verified it works. "Tested manually" is acceptable for small
changes; describe the steps.

## Screenshots (if UI change)

Before / after where helpful.

## Checklist
- [ ] Tests added or updated
- [ ] Docs updated (if public API changed)
- [ ] No unrelated changes included
```

---

## Changelog Entry Format (Keep a Changelog)

```
### Added
- New feature description (#PR or commit hash)

### Changed
- What changed and how it affects users

### Fixed
- Bug description (what it was, what it is now)

### Removed
- What was removed and migration path if needed

### Breaking
- Description + migration instructions
```

Group under the version heading: `## [1.4.0] - 2025-04-01`
