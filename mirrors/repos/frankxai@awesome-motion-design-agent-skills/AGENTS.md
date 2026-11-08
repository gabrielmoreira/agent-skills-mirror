# Repository Instructions

This repo is the public motion-agent discovery and authority layer for FrankX, Starlight, and Arcanea.

## Scope

- Maintain curated rankings, playbooks, skills, MCP notes, and rubrics for AI agents doing motion design.
- Prefer official sources, active repos, clear licenses, and examples that improve shipped output.
- Keep this repo public-safe: no private brand strategy, internal credentials, paid assets, client work, non-public memory, or local machine paths (CI enforces the last one).

## Quality Bar

- Rank by usefulness to real agent workflows, not by hype or stars alone.
- Separate product UI motion, creative web motion, interactive assets, video generation, capture/QA, and MCP/design-tool context.
- Every new tool entry should answer: when to use it, why it matters, agent fit, risk, and source/license notes.
- Avoid giant unsorted lists. Curate aggressively.

## Maintenance

- Refresh external links and rankings at least monthly.
- Prefer primary links: official docs, official GitHub repos, vendor MCP docs, and standards.
- Keep `skills-lock.json` aligned with third-party skills actually referenced by the repo.
- Do not commit installed third-party skill folders unless the source license and purpose are explicit.

## Verification

- Before publishing, scan for broken Markdown links, stale dates, placeholders, and private/internal paths.
- If adding setup commands, verify they are current and make clear whether they are global, repo-local, or agent-environment-specific.

## Design Taste Kernel

For any site, app, landing page, dashboard, visual identity, brand, motion, media, social, or frontend task, apply the maintainer's Design Taste Kernel (design taste, web experience standard, motion taste rubric, multi-agent design council, visual QA gate) before handoff. Those documents live in the maintainer's private estate and are intentionally not referenced by path here.

When motion, scroll, generated media, GIF/video, or premium polish matters, route through the skills in `skills/` and verify the result visually.


<!-- PREMIUM-WEB-OS:START -->
## Premium Intelligence Web OS Adoption

This repo participates in the Starlight Premium Intelligence Web OS.

For any website, app, landing page, dashboard, brand surface, visual asset, motion system, 3D/WebGL scene, generated media, or public-facing UI work:

- When the private Premium Web OS is present in the operator environment, read it first and treat it as the source of truth for taste, motion, WebGL, copy, assets, and quality gates.
- Use `/pwo` or the `premium-web-os` skill for full builds; use `/mad` for a design council pass.
- Use `/pwo review-pr` before absorbing another agent's PR or branch.
- Use `/pwo absorb-assets` before using external, generated, scientific, audio, video, or 3D assets.
- Use `/pwo motion-score` before shipping cinematic scroll, sound-paired motion, or complex choreography.
- Build static composition first, add Track A local motion second, add Track B GSAP/Lenis scroll only when earned, and add 3D only with fallback and reduced-motion behavior.
- Record asset provenance, rights, and publication status for every generated or external asset.
- Do not copy reference sites or agencies. Deconstruct principles and create original execution.
- Do not ship without responsive, accessibility, performance, reduced-motion, and visual QA checks appropriate to the change.

Repo-local instructions remain authoritative when stricter.
<!-- PREMIUM-WEB-OS:END -->
