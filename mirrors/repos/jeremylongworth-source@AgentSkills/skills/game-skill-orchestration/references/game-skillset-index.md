# Game Skillset Index

Use this index when a request spans more than one game-development domain.

## Core Implementation

- `game-3d-development`: runtime 3D gameplay systems, scene architecture, cameras, controls, physics, animation integration, composition, and verification.
- `game-threejs-development`: Three.js 3D browser games, render loops, WebGLRenderer, GLB/GLTF loading, controls, shaders, browser performance, and mobile/browser QA.
- `game-phaser-development`: Phaser 2D HTML5 games, scenes, sprites, tilemaps, Arcade/Matter physics, input, cameras, UI, scaling, and browser/mobile QA.
- `game-multiplayer-design`: authority, replication, prediction, rollback, lobbies, matchmaking, anti-cheat risk, and network testing.
- `game-social-systems-development`: player social features, privacy, reporting, moderation, presence, parties, guilds, chat, voice, and trust/safety.

## Visual And Asset Production

- `game-3d-asset-design`: game-ready assets, props, environments, modular kits, materials, textures, LODs, collision, pivots, naming, and engine handoff.
- `game-3d-model-design`: topology, retopology, UVs, normals, baking, deformation, rig-readiness, and mesh cleanup.
- `game-character-design`: silhouette, shape language, role, costume, props, faction identity, gameplay readability, and character production notes.
- `game-sprite-design`: 2D sprites, sprite sheets, pixel art, tile sets, UI icons, VFX sprites, animation frames, atlases, pivots/origins, hitboxes, and Phaser/HTML5-ready 2D assets.

## Player Experience Design

- `game-content-design`: levels, missions, quests, encounters, enemies, items, rewards, progression, tutorials, puzzles, biomes, factions, economies, and live content.
- `game-story-flow`: narrative arcs, branching, dialogue, lore delivery, scene beats, character arcs, and consequence tracking.
- `game-ui-design`: HUDs, menus, overlays, inventory, controller navigation, accessibility, onboarding, settings, and game interface flows.
- `game-playtesting-usability`: playtest plans, player observation, onboarding clarity, control usability, difficulty, balance, fun/enjoyability, feedback synthesis, and retest criteria.

## Research And Validation

- `customer-research-validation`: player/customer interviews, surveys, demand validation, motivation research, JTBD, voice-of-customer analysis, and structured evidence synthesis.
- `competitive-market-research`: genre, competitor, category, pricing, storefront, feature, review, and market-positioning research.
- `experiment-design-validation`: game, growth, onboarding, monetization, retention, UX, or marketing experiments with hypotheses, metrics, guardrails, and decision rules.
- `accessibility-inclusive-design`: WCAG, keyboard, screen-reader, contrast, motion, captions, control remapping, subtitles, game accessibility, and inclusive-design QA.
- `pricing-packaging-strategy`: monetization, pricing, tiers, DLC, subscriptions, donations, pay-what-you-want, storefront pricing, and pricing experiments.

## Audio And Cinematics

- `game-sound-design`: SFX, Foley, ambience, UI sounds, spatial audio, procedural audio, audio events, middleware, and mix behavior.
- `game-music-soundtrack-design`: themes, motifs, adaptive music, stems, loops, transitions, soundtrack generation, and music implementation.
- `game-cinematic-cutscene-design`: cutscenes, intro videos, trailers, storyboards, animatics, shot lists, camera blocking, timelines, and render/export.

## Publishing

- `itch-html5-game-publishing`: itch.io HTML5 ZIP packaging, iframe/fullscreen setup, mobile-friendly settings, case-sensitive paths, HTTPS asset constraints, donations, pay-what-you-want pricing, creator page readiness, and update QA.

## Common Skill Combinations

- Prototype a playable 3D feature: `game-skill-orchestration`, `game-3d-development`, `game-ui-design`, `game-sound-design`.
- Build a Three.js browser game: `game-threejs-development`, `game-3d-development`, `game-ui-design`, `game-sound-design`, `itch-html5-game-publishing`.
- Build a Phaser browser game: `game-phaser-development`, `game-content-design`, `game-ui-design`, `game-sound-design`, `itch-html5-game-publishing`.
- Create a 2D character sprite set: `game-sprite-design`, `game-character-design`, `game-phaser-development`.
- Design a boss encounter: `game-content-design`, `game-character-design`, `game-3d-development`, `game-sound-design`, `game-music-soundtrack-design`, `game-cinematic-cutscene-design`.
- Build a multiplayer co-op loop: `game-multiplayer-design`, `game-social-systems-development`, `game-ui-design`, `game-content-design`.
- Create a character from concept to engine: `game-character-design`, `game-3d-model-design`, `game-3d-asset-design`, `game-3d-development`.
- Create an opening sequence: `game-story-flow`, `game-cinematic-cutscene-design`, `game-music-soundtrack-design`, `game-sound-design`, `game-ui-design`.
- Design a level with narrative and rewards: `game-content-design`, `game-story-flow`, `game-3d-asset-design`, `game-ui-design`, `game-sound-design`.
- Validate a confusing tutorial: `game-playtesting-usability`, `game-content-design`, `game-ui-design`.
- Research market fit for an indie game: `competitive-market-research`, `customer-research-validation`, `itch-html5-game-publishing`, `game-skill-orchestration`.
- Design accessibility for a web game: `accessibility-inclusive-design`, `game-ui-design`, `game-phaser-development` or `game-threejs-development`, `game-playtesting-usability`.
- Choose monetization for an itch.io game: `pricing-packaging-strategy`, `itch-html5-game-publishing`, `competitive-market-research`, `customer-research-validation`.

## Selection Rule

Use the domain skill that owns the primary deliverable first. Add secondary skills only for explicit dependencies, review gates, or cross-discipline risks.
