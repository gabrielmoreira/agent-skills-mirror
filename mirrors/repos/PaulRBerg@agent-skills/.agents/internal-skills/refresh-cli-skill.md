---
name: refresh-cli-skill
description:
  Review browser dependencies weekly and refresh cli-* skills when installed versions advance. Use stable upstream
  evidence and preserve local safety rules.
---

# Refresh CLI Skill

Refresh `skills/cli-*` when an installed CLI is newer than its `references/version.txt` marker. Review
`skills/chromium-browser` against Chrome DevTools MCP every week, even when the installed version has not changed.

Circadian's weekly maintenance job runs `jobs/refresh-cli-skills.sh` in an isolated clone of this repository. The job
commits, pushes, and publishes the result after validation. It can also request guidance reviews for explicitly named
skills whose watched upstream sources changed.

## Arguments

- Accept arguments as `<skill>=<version>`, for example `cli-just=1.43.0` or `chromium-browser=1.10.1`.
- Treat each version as an already-normalized semver with no leading `v`.
- Accept version pairs only for `cli-*` and `chromium-browser` skills.
- Also accept explicit upstream review names and source notes supplied alongside the pairs. The scheduler says
  `Also review <space-separated names> against them` and appends notes from `SKILL_REFRESH_UPSTREAM_NOTES`.
- Confirm that every additional name has an existing `skills/<name>/SKILL.md`. Reject unknown names.
- Upstream-only reviews need no version pair or `references/version.txt` marker. Do not invent either.
- If neither valid skill/version pairs nor explicit upstream review names are supplied, stop.

## Workflow

1. Work in the current checkout. In an isolated clone, never touch the shared `~/projects/agent-skills` worktree.
2. Before editing, confirm the worktree is clean. If it is dirty, stop and report the dirty paths.
3. For each requested CLI skill:
   - Confirm `skills/<cli-skill>/SKILL.md` exists.
   - Map `cli-<name>` to binary `<name>`. Map `cli-coingecko` to `cg`.
   - Confirm the binary's `--version` output still reports the requested version. If evidence is missing, stop with
     failure.
   - Read current docs and references that mention versioned features, flags, or upstream links.
   - Inspect official stable release notes and tagged manuals or CLI docs for the requested version.
   - Use installed CLI help to confirm compatibility.
   - Update stale or missing facts. Keep edits terse and preserve local safety rules.
   - Write `skills/<cli-skill>/references/version.txt` with exactly the requested semver and one trailing newline.
4. For `chromium-browser`, complete these steps even when the installed version has not changed:
   - Confirm `skills/chromium-browser/SKILL.md` exists.
   - Read `~/.agents/skills/chromium-browser/scripts/chrome-devtools-mcp.sh` without changing it. Use
     `skills/chromium-browser/scripts/chrome-devtools-mcp.sh` in this checkout as its catalog source.
   - Verify the wrapper's installed executable version through package metadata or its `--version` output. Never start
     the MCP server for this check.
   - Inspect official stable Chrome DevTools MCP release notes and tagged documentation. Compare them with the installed
     version and wrapper flags.
   - Update compatible skill guidance and link to the installed release's tagged tool reference. No browser version
     marker is required.
   - Report stable upstream releases newer than the installed version and wrapper incompatibilities. Never present
     unreleased or unavailable features as available.
   - Preserve attach-only operation, privacy and header redaction, negotiated-root restrictions, screenshot caps, and
     shared-browser ownership.
   - Treat the wrapper audit as read-only. Never change wrapper flags, settings, client configuration, or installed
     copies.
5. For each additional upstream review name:
   - Read its source notes and affected skill guidance. Inspect every supplied source and the relevant stable changes.
   - Check official documentation and source evidence before changing guidance. Confirm installed compatibility when the
     proposed guidance depends on an installed tool or dependency.
   - Change only guidance affected by those sources. Preserve local behavior and safety rules.
   - Do not update dependencies or merge external skill forks through this review. Follow `@rebase-skill` only under its
     separate invocation policy.
   - Do not create or advance a version marker for an upstream-only review.
6. Edit only the requested skill directories. Never edit generated lockfiles, unrelated skills, installed copies under
   `~/.agents`, or global Claude/Codex configuration.
7. Run `just prettier-write <changed Markdown files>`. Then run `just prettier-check <changed files>` and
   `just skill-check`. Complete the local gate for any changed helper or behavior.
8. If the scheduled weekly job invoked you, stop without committing or publishing. The job performs both steps.
   Otherwise, commit and publish per `AGENTS.md`.
9. Report evidence sources, compatible documentation changes, newer upstream releases, and configuration
   incompatibilities. If a required check or evidence source fails, report failure instead of claiming success.

   For the scheduled review, return structured output with `status` and `summary`. Set `status` to `succeeded` only when
   all required review evidence and checks are complete. Otherwise, set `status` to `failed` and give an actionable
   `summary`. The job owns later publication. A publication phase must return `failed` if any required publication work
   is incomplete.

## Version Metadata

For CLI version refreshes, `references/version.txt` is the weekly maintenance job's contract. `ai-skillet doctor` also
enforces it. Upstream-only reviews do not require this marker. The file must contain exactly one normalized semver:

```text
1.2.3
```

The file must have no leading `v`, prose, comments, ranges, prerelease labels, or extra lines.
