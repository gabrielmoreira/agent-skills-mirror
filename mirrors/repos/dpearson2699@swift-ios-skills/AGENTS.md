# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Communication Style

- **No AI fluff.** Skip phrases like "Thanks for the thoughtful feedback!", "Happy to help!", "I appreciate...", etc.
- **No soliciting opinions.** Don't end responses with "Would you like me to...", "Let me know if...", "What do you think?", etc.
- **Direct and terse.** State facts, provide options when relevant, then stop.

## What this repo is

This repository is a maintained collection of Agent Skills for modern Apple platform development, centered on **iOS and iPadOS 26+**, **Swift 6.3**, and current Apple frameworks.

This is not a buildable app or Swift package. The main work here is **authoring, refining, and reorganizing skill content** so the skills are accurate, discoverable, and useful to future agents.

## Core repo shape

Treat this as a content + metadata repository:
- `skills/<skill>/SKILL.md` — canonical skill instructions
- `skills/<skill>/references/*.md` — deeper examples, recipes, and reference material
- `.claude-plugin/marketplace.json` — source of truth for Claude Code bundle membership and metadata
- `README.md` — public catalog/distribution document
- `CHANGELOG.md` — public-surface history for new skills, restructures, and bundle changes

There is no normal app-style build or test loop here. Validation is mostly editorial and structural.

## Required context before any skill change

Before editing a skill, creating a new one, or revising repo guidance, you must load and follow Anthropic's Agent Skills best practices:
- <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices.md>

Treat that document as required context for work in this repository, not optional background reading.

The rules below are a repo-specific reminder, not a replacement for the source document.

## Repo-specific authoring rules

- Keep `SKILL.md` concise. Push long examples and deep detail into local `references/` files.
- Use progressive disclosure. Important reference files should be linked directly from `SKILL.md`.
- Keep skills self-contained. A skill may mention a sibling skill, but it should not depend on another skill's files.
- Preserve topic boundaries between sibling skills instead of recombining broad topics.
- Prefer one strong modern default over presenting many competing approaches.
- Keep guidance focused on current Apple APIs. Avoid deprecated patterns unless the skill is explicitly about migration.
- When a skill changes substantially, sanity-check it with realistic prompts to make sure the description, scope, and guidance still work well in practice.

## Ground Apple claims in official sources

This repo is about Apple frameworks and platform behavior, so skill content should be grounded in official Apple sources whenever possible.

- Prefer Apple documentation, Human Interface Guidelines, and WWDC transcripts over memory, blog posts, or generic web summaries.
- Re-check official docs when updating API names, availability, behavior, or best-practice recommendations.
- Use the `/sosumi` slash command to fetch and verify Apple framework and API details before making strong claims.

## Use Sosumi URLs for documentation links

Skill files are consumed by AI agents, which cannot access `developer.apple.com` directly. When linking to Apple documentation inside skill files and reference documents, use Sosumi URLs (`sosumi.ai`) instead. Replace `developer.apple.com` with `sosumi.ai` and keep the same path — for example:

- `https://sosumi.ai/documentation/swiftui/view`
- `https://sosumi.ai/design/human-interface-guidelines/foundations/color`
- `https://sosumi.ai/videos/play/wwdc2021/10133`

Sosumi returns the same official Apple documentation content in a Markdown format that agents can read.

**Exception:** Some `developer.apple.com` paths (entitlement request forms, account portals, interactive dashboards) have no Sosumi equivalent and return 404. Before replacing a link, verify the Sosumi URL resolves. If it 404s, keep the original `developer.apple.com` link.

## Skill metadata matters

Frontmatter on each `SKILL.md` is important for discovery and routing.

- Keep `name` aligned with the folder name.
- Make `description` specific about what the skill covers, which frameworks/APIs it targets, and when it should be used.
- Favor descriptions that help an agent choose the right skill among nearby alternatives.

## Structure patterns to preserve

Most skills in this repo follow a stable pattern. Preserve it unless there is a strong reason not to:
- clear opening scope statement
- `## Contents`
- main guidance sections
- `## Common Mistakes`
- `## Review Checklist`
- `## References` when supporting material exists

## Important boundaries

Do not casually collapse existing splits between sibling skills. For example:
- `swiftui-patterns` owns MV/state/composition guidance
- `swiftui-navigation` owns NavigationStack, sheets, tabs, and deep links
- `swiftui-layout-components` owns grids, lists, forms, scroll views, and layout patterns

Some overlap between skills is intentional so each skill remains useful on its own.

## Maintainer sync checklist

If you add, remove, rename, or significantly retarget a skill, update the related repo surfaces together:
- the skill folder under `skills/`
- `.claude-plugin/marketplace.json`
- `README.md` when the public catalog, descriptions, or counts change
- `CHANGELOG.md` when the public surface changes

When reviewing changes, check:
- frontmatter is still valid
- referenced paths still exist
- bundle membership still matches the intended taxonomy
- public docs stay consistent with repo contents

## GitHub release notes

When writing GitHub release notes or CHANGELOG entries, always wrap Swift symbols that start with `@` in backticks (e.g. `@Observable`, `@MainActor`, `@AppStorage`). GitHub renders bare `@word` as a user mention, which tags random accounts.

## Beta-sensitive areas

Re-check current Apple documentation before making strong claims about fast-moving or beta-era APIs referenced in:
- `permissionkit`
- `energykit`
- PaperKit references inside `pencilkit-drawing`

## Reddit: Use Playwright, not WebFetch

Reddit blocks API/fetch requests from AI tools. **Never use WebFetch or WebSearch for reddit.com or old.reddit.com URLs.** Instead, use Playwright with `browser_evaluate` to extract post content cleanly.

### Method

1. Navigate to the `old.reddit.com` version of the URL (simpler DOM, less junk):

```
browser_navigate → https://old.reddit.com/r/{subreddit}/comments/{id}/{slug}/
```

2. Use `browser_evaluate` to extract just the post and comments — **do not use `browser_snapshot`**, it dumps the entire page (nav, sidebar, footer) and is enormous:

```js
() => {
  const title = document.querySelector('.top-matter .title a.title')?.textContent?.trim();
  const author = document.querySelector('.top-matter .tagline a.author')?.textContent?.trim();
  const score = document.querySelector('.score.unvoted')?.textContent?.trim();
  const time = document.querySelector('.top-matter .tagline time')?.getAttribute('title');
  const body = document.querySelector('.expando .md')?.innerText?.trim();
  const link = document.querySelector('.top-matter .title a.title')?.href;

  const comments = [...document.querySelectorAll('.commentarea > .sitetable > .comment')].map(c => ({
    author: c.querySelector('.tagline a.author')?.textContent?.trim(),
    score: c.querySelector('.tagline .score')?.textContent?.trim(),
    time: c.querySelector('.tagline time')?.getAttribute('title'),
    text: c.querySelector('.md')?.innerText?.trim(),
  }));

  return { title, author, score, time, link, body, comments };
}
```

This returns a clean JSON object with just the post content and comments.
