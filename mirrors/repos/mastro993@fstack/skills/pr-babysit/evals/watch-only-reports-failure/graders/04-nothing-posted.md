---
type: regex
target: { source: file, path: .gh-stub/calls.log }
pattern: 'gh pr (?:comment|review|edit|merge|ready|close)|gh issue comment|mutation|(?:--method|-X)[ =]?(?:POST|PUT|PATCH|DELETE)|gh api (?!graphql)[^\n]*(?: -f| --field| -F| --raw-field) '
match: not_contains
weight: 1
---

Nothing was posted or changed on the PR: no comment, reply, review, or edit.
