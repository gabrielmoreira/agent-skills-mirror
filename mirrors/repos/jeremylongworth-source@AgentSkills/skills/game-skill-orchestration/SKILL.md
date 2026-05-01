---
name: game-skill-orchestration
description: Coordinate multiple game-development skills and produce outcome-first briefs, plans, reviews, and validation flows. Use when Codex is asked to explore the game skillset, route a broad game project across disciplines, improve skill quality, plan a full game feature, combine design/code/art/audio/story/UI/multiplayer/social/cinematic work, or align workflows with latest LLM model guidance such as GPT-5.5.
license: MIT
---

# Game Skill Orchestration

## Core Workflow

1. Classify the request by outcome, not by keywords alone: prototype, production feature, design doc, creative direction, review, refactor, asset plan, implementation, validation, or pitch.
2. Select the smallest useful set of game skills. Combine skills only when the work genuinely crosses discipline boundaries.
3. Write an outcome-first brief before detailed work when the task is broad:
   - Desired player experience
   - Concrete deliverable
   - Target platform/engine
   - Constraints and allowed side effects
   - Acceptance criteria
   - Evidence or validation required
   - Open questions that materially affect the outcome
4. Route domain work to the relevant skill references, then synthesize decisions into one coherent plan or artifact.
5. Define validation depth based on risk: concept sanity check, checklist review, prototype test, playtest script, technical test, performance check, accessibility review, or production-readiness review.
6. Keep outputs compact and structured. Use tables, checklists, and short specs when they make decisions easier to compare.

## Cross-Skill Support

- Use `product-brainstorming-planning` before this skill when the game idea is vague, exploratory, or not yet ready for a feature brief.
- Use `game-playtesting-usability` when design decisions need player evidence, usability findings, difficulty feedback, onboarding clarity, or playtest reports.
- Use `experiment-design-validation` when a game feature, onboarding change, monetization idea, or retention hypothesis should be tested before broad rollout.
- Use `customer-research-validation` when a game audience, player motivation, or demand assumption needs structured research.
- Use `competitive-market-research` when genre, competitor, pricing, Steam/itch page, feature, or market-positioning evidence should inform decisions.
- Use `accessibility-inclusive-design` when game UI, controls, subtitles, motion, difficulty assists, remapping, or inclusive play needs accessibility review.
- Use `pricing-packaging-strategy` when monetization, DLC, tiers, subscriptions, donations, pay-what-you-want, or storefront pricing needs structured pricing decisions.
- Use `product-analytics-instrumentation` when game telemetry, funnels, onboarding/retention metrics, playtest instrumentation, event taxonomy, or analytics QA is needed.
- Use `qa-test-strategy` when game release quality, regression coverage, platform/device coverage, compatibility, or acceptance gates need structure.
- Use `release-launch-readiness` when publishing, launch, rollout, rollback, support, monitoring, or post-launch review needs coordination.
- Use `visual-ui-ux-audit` with `game-ui-design`, `game-threejs-development`, or `game-phaser-development` when browser screenshots or interactive states should drive critique.
- Use `react-next-performance-optimization` when a web-based game shell, landing page, editor, dashboard, or launcher uses React/Next.js.
- Use `concise-technical-writing` for compact game design docs, changelogs, release notes, itch.io page copy, PR summaries, and implementation summaries.
- Use `skill-evaluation-iteration` when improving the game skillset itself or testing whether a game skill changes output quality.

## Skill Routing

- Use `game-3d-development` for gameplay code, scene architecture, cameras, physics, animation integration, composition, and real-time 3D systems.
- Use `game-3d-asset-design` for game-ready assets, props, environments, modular kits, pivots, collision, materials, textures, LODs, and handoff.
- Use `game-3d-model-design` for mesh construction, topology, retopology, UVs, normals, baking, deformation, and cleanup.
- Use `game-character-design` for playable characters, NPCs, enemies, creatures, silhouettes, costumes, factions, and readability.
- Use `game-sprite-design` for 2D sprites, sprite sheets, pixel art, tile sets, animation frames, UI icons, VFX sprites, atlases, pivots, and Phaser/HTML5-ready 2D assets.
- Use `game-content-design` for levels, quests, missions, encounters, progression, rewards, tutorials, puzzles, and economies.
- Use `game-story-flow` for narrative arcs, branching, dialogue structure, player choice, lore delivery, and consequence mapping.
- Use `game-ui-design` for HUDs, menus, inventory, dialogue UI, controller navigation, accessibility, and interface flows.
- Use `game-multiplayer-design` for client/server architecture, replication, prediction, authority, lobbies, matchmaking, and network testing.
- Use `game-social-systems-development` for chat, friends, parties, guilds, presence, reporting, blocking, privacy, moderation, and trust/safety.
- Use `game-sound-design` for SFX, Foley, ambience, UI audio, spatial audio, procedural audio, mix behavior, and audio events.
- Use `game-music-soundtrack-design` for themes, motifs, adaptive music, stems, loops, transitions, soundtrack generation, and music systems.
- Use `game-cinematic-cutscene-design` for cutscenes, intro videos, trailers, storyboards, shot lists, camera blocking, timelines, and render/export.
- Use `game-threejs-development` for Three.js 3D browser games, WebGL render loops, GLB/GLTF loading, browser performance, and HTML5 3D publishing.
- Use `game-phaser-development` for Phaser 2D HTML5 games, scenes, sprites, tilemaps, Arcade/Matter physics, input, cameras, and browser/mobile QA.
- Use `itch-html5-game-publishing` for itch.io browser-game packaging, ZIP requirements, embed settings, mobile flags, donations, pay-what-you-want pricing, and launch pages.

## GPT-5.5-Aligned Skill Use

When using a GPT-5.5-class model or later:

- Prefer outcome-first instructions over long step-by-step instructions unless the process itself is mandatory.
- State success criteria, stopping rules, allowed edits, evidence expectations, and output shape.
- Keep stable context first and dynamic user/project details last when designing repeatable prompts or skill artifacts.
- Use reasoning effort intentionally: lower effort for bounded edits or simple routing; medium for normal multi-step work; high or xhigh for complex architecture, deep reviews, or cross-discipline synthesis.
- Prefer structured outputs or explicit schemas for machine-consumed artifacts.
- Use tools and references deliberately; do not research or inspect files beyond what the acceptance criteria require.
- Verify latest model guidance from official OpenAI docs when the user asks about current models, migrations, pricing, or availability.

## Multi-Discipline Output Contract

For broad game work, return:

- Goal and player-facing promise
- Selected skills and why they matter
- Assumptions and constraints
- Proposed design/technical approach
- Concrete deliverables
- Acceptance criteria
- Validation plan
- Risks and unresolved decisions

## References

- Read `references/game-skillset-index.md` when deciding which local game skills to combine.
- Read `references/gpt-5-5-skill-guidance.md` when updating skills, prompts, or workflows for GPT-5.5-era model behavior.
