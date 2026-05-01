---
name: create-pr
description: "Create pull requests following Sentry conventions. Use when opening PRs, writing PR descriptions, or preparing changes for review. Follows Sentry's code review guidelines."
risk: safe
source: "https://github.com/getsentry/skills/tree/main/plugins/sentry-skills/skills/create-pr"
date_added: "2026-02-27"
---

# Create Pull Request

Create pull requests following Sentry's engineering practices.

## When to Use This Skill

Use this skill when:
- Opening pull requests
- Writing PR descriptions
- Preparing changes for review
- Following Sentry's code review guidelines
- Creating PRs that follow best practices

**Requires**: GitHub CLI (`gh`) authenticated and available.

## Prerequisites

Before creating a PR, ensure all changes are committed. If there are uncommitted changes, run the `sentry-skills:commit` skill first to commit them properly.

```bash
# Check for uncommitted changes
git status --porcelain
```

If the output shows any uncommitted changes (modified, added, or untracked files that should be included), invoke the `sentry-skills:commit` skill before proceeding.

## Process

### Step 1: Verify Branch State

```bash
# Detect the default branch
BASE=$(gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name')

# Check current branch and status
git status
git log $BASE..HEAD --oneline
```

Ensure:
- All changes are committed
- Branch is up to date with remote
- Changes are rebased on the base branch if needed

### Step 2: Analyze Changes

Review what will be included in the PR:

```bash
# See all commits that will be in the PR
git log $BASE..HEAD

# See the full diff
git diff $BASE...HEAD
```

Understand the scope and purpose of all changes before writing the description.

### Step 3: Write the PR Description

Use this structure for PR descriptions (ignoring any repository PR templates):

```markdown
<brief description of what the PR does>

<why these changes are being made - the motivation>

<alternative approaches considered, if any>

<any additional context reviewers need>
```

**Do NOT include:**
- "Test plan" sections
- Checkbox lists of testing steps
- Redundant summaries of the diff

**Do include:**
- Clear explanation of what and why
- Links to relevant issues or tickets
- Context that isn't obvious from the code
- Notes on specific areas that need careful review

### Step 4: Create the PR

```bash
gh pr create --draft --title "<type>(<scope>): <description>" --body "$(cat <<'EOF'
<description body here>
EOF
)"
```

**Title format** follows commit conventions:
- `feat(scope): Add new feature`
- `fix(scope): Fix the bug`
- `ref: Refactor something`

## PR Description Examples

### Feature PR

```markdown
Add Slack thread replies for alert notifications

When an alert is updated or resolved, we now post a reply to the original
Slack thread instead of creating a new message. This keeps related
notifications grouped and reduces channel noise.

Previously considered posting edits to the original message, but threading
better preserves the timeline of events and works when the original message
is older than Slack's edit window.

Refs SENTRY-1234
```

### Bug Fix PR

```markdown
Handle null response in user API endpoint

The user endpoint could return null for soft-deleted accounts, causing
dashboard crashes when accessing user properties. This adds a null check
and returns a proper 404 response.

Found while investigating SENTRY-5678.

Fixes SENTRY-5678
```

### Refactor PR

```markdown
Extract validation logic to shared module

Moves duplicate validation code from the alerts, issues, and projects
endpoints into a shared validator class. No behavior change.

This prepares for adding new validation rules in SENTRY-9999 without
duplicating logic across endpoints.
```

## Issue References

Reference issues in the PR body:

| Syntax | Effect |
|--------|--------|
| `Fixes #1234` | Closes GitHub issue on merge |
| `Fixes SENTRY-1234` | Closes Sentry issue |
| `Refs GH-1234` | Links without closing |
| `Refs LINEAR-ABC-123` | Links Linear issue |

## Guidelines

- **One PR per feature/fix** - Don't bundle unrelated changes
- **Keep PRs reviewable** - Smaller PRs get faster, better reviews
- **Explain the why** - Code shows what; description explains why
- **Mark WIP early** - Use draft PRs for early feedback

## Editing Existing PRs

If you need to update a PR after creation, use `gh api` instead of `gh pr edit`:

```bash
# Update PR description
gh api -X PATCH repos/{owner}/{repo}/pulls/PR_NUMBER -f body="$(cat <<'EOF'
Updated description here
EOF
)"

# Update PR title
gh api -X PATCH repos/{owner}/{repo}/pulls/PR_NUMBER -f title='new: Title here'

# Update both
gh api -X PATCH repos/{owner}/{repo}/pulls/PR_NUMBER \
  -f title='new: Title' \
  -f body='New description'
```

Note: `gh pr edit` is currently broken due to GitHub's Projects (classic) deprecation.

## References

- [Sentry Code Review Guidelines](https://develop.sentry.dev/engineering-practices/code-review/)
- [Sentry Commit Messages](https://develop.sentry.dev/engineering-practices/commit-messages/)

## Pre-flight Checks

Before creating a PR, check for uncommitted changes:

1. Run `git status` to check for uncommitted changes (staged, unstaged, or untracked files)
2. If uncommitted changes exist, use the Skill tool to run the `git:commit` command first:
   ```
   Skill: git:commit
   ```
3. This ensures all your work is committed before creating the PR

## Creating a New Pull Request

1. First, prepare your PR description following the template in @.github/pull_request_template.md

2. Use the `gh pr create --draft` command to create a new pull request:

   ```bash
   # Basic command structure
   gh pr create --draft --title "✨(scope): Your descriptive title" --body "Your PR description" --base main 
   ```

   For more complex PR descriptions with proper formatting, use the `--body-file` option with the exact PR template structure:

   ```bash
   # Create PR with proper template structure
   gh pr create --draft --title "✨(scope): Your descriptive title" --body-file .github/pull_request_template.md --base main
   ```

## Best Practices

1. **Language**: Always use English for PR titles and descriptions

2. **PR Title Format**: Use conventional commit format with emojis

   - Always include an appropriate emoji at the beginning of the title
   - Use the actual emoji character (not the code representation like `:sparkles:`)
   - Examples:
     - `✨(supabase): Add staging remote configuration`
     - `🐛(auth): Fix login redirect issue`
     - `📝(readme): Update installation instructions`

3. **Description Template**: Always use our PR template structure from @.github/pull_request_template.md:

4. **Template Accuracy**: Ensure your PR description precisely follows the template structure:

   - Don't modify or rename the PR-Agent sections (`pr_agent:summary` and `pr_agent:walkthrough`)
   - Keep all section headers exactly as they appear in the template
   - Don't add custom sections that aren't in the template

5. **Draft PRs**: Start as draft when the work is in progress
   - Use `--draft` flag in the command
   - Convert to ready for review when complete using `gh pr ready`

### Common Mistakes to Avoid

1. **Using Non-English Text**: All PR content must be in English
2. **Incorrect Section Headers**: Always use the exact section headers from the template
3. **Adding Custom Sections**: Stick to the sections defined in the template
4. **Using Outdated Templates**: Always refer to the current @.github/pull_request_template.md file

### Missing Sections

Always include all template sections, even if some are marked as "N/A" or "None"

## Additional GitHub CLI PR Commands

Here are some additional useful GitHub CLI commands for managing PRs:

```bash
# List your open pull requests
gh pr list --author "@me"

# Check PR status
gh pr status

# View a specific PR
gh pr view <PR-NUMBER>

# Check out a PR branch locally
gh pr checkout <PR-NUMBER>

# Convert a draft PR to ready for review
gh pr ready <PR-NUMBER>

# Add reviewers to a PR
gh pr edit <PR-NUMBER> --add-reviewer username1,username2

# Merge a PR
gh pr merge <PR-NUMBER> --squash
```

## Using Templates for PR Creation

To simplify PR creation with consistent descriptions, you can create a template file:

1. Create a file named `pr-template.md` with your PR template
2. Use it when creating PRs:

```bash
gh pr create --draft --title "feat(scope): Your title" --body-file pr-template.md --base main
```

## Related Documentation

- [PR Template](.github/pull_request_template.md)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub CLI documentation](https://cli.github.com/manual/)
