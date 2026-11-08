# Automated reviewers

How the common review bots behave, checked November 2026. Bots change: when one acts differently from this table, go by what it does on the PR and by its docs (linked below).

REST shows a bot as `<login>[bot]`; GraphQL's `author.login` drops the `[bot]`.

| Bot (login) | Ask for a review | Reviews on its own | Clean result | Installed if |
|---|---|---|---|---|
| CodeRabbit (`coderabbitai`) | `@coderabbitai review` (changes since its last review); `@coderabbitai full review` starts over | on open and every push; skips drafts | `CodeRabbit` check finishes; summary says "No actionable comments were generated in the recent review." A clean pass may post no review at all | `.coderabbit.yaml` |
| Pullfrog (`pullfrog`) | comment `@pullfrog` | on open and every push; skips drafts | COMMENTED review starting `✅ No new issues found.`; `pullfrog` check "Pullfrog run completed" | workflow using `pullfrog/pullfrog` |
| Claude Code Review app (`claude`) | new top-level comment `@claude review` (whole PR) | per repo: once, every push, or manual; skips drafts | `Claude Code Review` check ends neutral "Code review found no issues"; "skipped — no new changes" when the diff didn't change | no file; its check on earlier PRs |
| claude-code-action (`claude`, maybe `github-actions` under a GITHUB_TOKEN) | comment with its `trigger_phrase` (default `@claude`), e.g. `@claude review this PR` | only on the events in the workflow's `on:` | no fixed wording: read its comment | workflow using `anthropics/claude-code-action` |
| GitHub Copilot (`copilot-pull-request-reviewer`) | `gh pr edit <n> --add-reviewer @copilot` (gh 2.88+) | only if a ruleset turns it on; pushes and drafts are opt-in | COMMENTED review "…generated no new comments."; listed in requested reviewers while pending | ruleset only |
| OpenAI Codex (`chatgpt-codex-connector`) | `@codex review` | opt-in, on open and draft → ready | 👍 on the PR and no comments; 👀 while running. Its review body names the reviewed commit | no file |
| Cursor Bugbot (`cursor`) | `cursor review` or `bugbot run` | every push; skips drafts | `Cursor Bugbot` check succeeds (neutral while findings are open); no review posted | `.cursor/BUGBOT.md` |
| Greptile (`greptile-apps`) | `@greptileai` (`@greptileai review this draft` on a draft) | on open; pushes only with `triggerOnUpdates`; skips drafts | `Greptile Review` check; summary with a confidence score and "Last reviewed commit" | `greptile.json`, `.greptile/` |
| Gemini Code Assist (`gemini-code-assist`) | `/gemini review` | on open, drafts included | COMMENTED "## Code Review" review with no inline comments | `.gemini/` |
| Sourcery (`sourcery-ai`) | `@sourcery-ai review` | on open and every push, up to 5 re-reviews, then its check says "Skipped"; skips drafts | `Sourcery review` check succeeds; a "look great" review | web settings only |
| Qodo (`qodo-code-review`) | `/agentic_review` | on open, reopen, and ready | "Code Review by Qodo" comment with every counter at zero | `.pr_agent.toml` |

## Reading a round

- A review counts only for the head it covered. Match its `commit_id` (`gh api --paginate repos/<owner>/<repo>/pulls/<n>/reviews --jq '.[] | [.user.login, .state, .commit_id] | @tsv'`), its check run's head, or the commit its summary names against the PR head.
- Bots that finish without posting a review (CodeRabbit, Bugbot) say so in their check run or in a summary comment they edit in place, so a quiet bot may still be done.
- Bots ignore commands posted by other bots; comment as the authenticated user.
- `@claude review` starts both Claude Code Review and claude-code-action when both are installed: one comment, two reviewers.
- Plan limits run out (CodeRabbit's hourly allowance, Bugbot usage, Copilot quota). A rate-limit or usage-limit reply ends that bot's part in the round; tell the user instead of retrying.

## Docs

[CodeRabbit](https://docs.coderabbit.ai/guides/commands) · [Pullfrog](https://docs.pullfrog.com/pr-reviews.md) · [Claude Code Review](https://code.claude.com/docs/en/code-review-pull-requests.md) · [claude-code-action](https://github.com/anthropics/claude-code-action/blob/main/docs/usage.md) · [Copilot](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/request-a-code-review/use-code-review) · [Codex](https://learn.chatgpt.com/docs/third-party/github) · [Bugbot](https://cursor.com/docs/bugbot) · [Greptile](https://www.greptile.com/docs/code-review-bot/trigger-code-review.md) · [Gemini](https://docs.cloud.google.com/gemini/docs/code-review/use-code-assist-github) · [Sourcery](https://docs.sourcery.ai/reviews/commands.md) · [Qodo](https://docs.qodo.ai/code-review/use-qodo-in-prs/code-review)
