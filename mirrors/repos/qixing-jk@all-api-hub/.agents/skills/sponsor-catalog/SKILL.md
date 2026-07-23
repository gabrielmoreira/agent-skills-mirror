---
name: sponsor-catalog
description: Use when adding, updating, removing, reordering, or auditing sponsors, affiliate links, sponsor copy, logos, public sponsor-catalog JSON files, README sponsor sections, or documentation-site sponsor listings in all-api-hub.
---

# Sponsor Catalog

## Core principle

Treat sponsor content as coordinated production configuration. Discover the current surfaces, verify operational claims, and update every still-served catalog schema that can safely represent the campaign.

## Workflow

1. Inspect repository state and current ownership before editing.
   - Run `git status --porcelain` and preserve unrelated work.
   - Inspect `src/features/AccountManagement/sponsors/`, every `public/sponsor-catalog*.json`, the existing catalog test, and nearby sponsor entries.
   - Search the whole repository for the sponsor name, domain, asset name, and neighboring sponsors with `rg`.
   - Inspect recent sponsor commits with `git log --all --oneline -- <paths>` and compare a complete recent rollout. Do not assume the first matching commit defines the full scope.

2. Load compatibility guidance when software or public JSON is in scope.
   - Read [references/catalog-compatibility.md](references/catalog-compatibility.md) before choosing schema coverage, support status, actions, or rank.
   - Prefer current code, public artifacts, tests, and release tags over stale design documents.

3. Separate campaign facts from product integration facts.
   - Preserve user-supplied copy, affiliate URLs, and promotion terms in production surfaces only.
   - Verify any inferred site type, authentication type, API base URL, key-console URL, or direct-support claim against the target deployment, upstream source, or current repository behavior.
   - Keep the affiliate destination separate from operational URLs. Do not derive an API base URL or account origin from a marketing link.
   - Do not probe live affiliate URLs unless the user requests it.

4. Update the complete discovered surface.
   - Treat root READMEs, the Chinese docs source, relevant docs pages, public catalogs, and `resources/partners/` as the starting checklist, then let repository search and history determine the final set.
   - Follow the repository translation policy. Treat `docs/docs/` Chinese pages as source and avoid manual generated-locale edits unless explicitly requested or required by the established workflow.
   - Inspect the supplied image format, pixel dimensions, aspect ratio, and existing presentation classes or attributes. Rename it to the established slug convention and align displayed dimensions without unnecessary re-encoding or new CSS.
   - Keep prose order, physical JSON order, and runtime rank as separate decisions. Implement each ordering request explicitly.

5. Validate and hand off.
   - For data, copy, and asset-only changes, do not add tests by default. Run the existing focused catalog test:
     `pnpm vitest tests/features/AccountManagement/sponsors/publicCatalog.test.ts --run`
   - When docs surfaces change and dependencies are available, run `pnpm --dir docs run docs:check-links` and `pnpm --dir docs run docs:build` as risk warrants.
   - Run `git diff --check`, inspect the task-scoped diff, stage only task files, and run `pnpm run validate:staged` before committing.
   - Use `docs(sponsors): ...` for copy, catalog-data, and asset-only changes. Choose `feat` or `fix` only when the final diff changes executable behavior.
   - Report every intentionally omitted catalog version with its concrete compatibility reason. For data-only changes, record that existing sponsor analytics are reused and browser E2E is unnecessary because no runtime flow changed.

## Common mistakes

- Treating a sponsor's absence from an older catalog as proof of incompatibility.
- Copying a V5 item verbatim into a strict older schema.
- Marking a provider supported from marketing compatibility alone.
- Updating Markdown order while forgetting rank-based software order.
- Stopping after README or docs edits without checking shipped public JSON.
- Encoding one sponsor's temporary placement, offer, or copy as a durable rule.
