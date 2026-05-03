---
type: skill
lifecycle: stable
inheritance: inheritable
name: game-design
description: Game mechanics, level design, player psychology, systems balancing, and narrative design for game developers.
tier: extended
applyTo: '**/*game*,**/*design*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# Game Design Skill


> Game mechanics, level design, player psychology, systems balancing, and narrative design for game developers.

## Core Principle

A great game teaches you how to play it without telling you. Every mechanic, level layout, and narrative beat exists to create player agency — the feeling that choices matter and mastery is earned.

## Core Mechanics

### MDA Framework

| Layer | Stands For | Perspective |
|-------|-----------|-------------|
| **Mechanics** | Rules, systems, algorithms | Designer builds |
| **Dynamics** | Behaviors that emerge from mechanics | Player experiences |
| **Aesthetics** | Emotional responses | Player feels |

Design flows: Mechanics → Dynamics → Aesthetics
Player experiences: Aesthetics ← Dynamics ← Mechanics

### Eight Kinds of Fun (Aesthetics)

| Aesthetic | Description | Example Games |
|-----------|-------------|---------------|
| Sensation | Sensory pleasure | Journey, Flower |
| Fantasy | Make-believe, immersion | Skyrim, Mass Effect |
| Narrative | Story as drama | The Last of Us, Disco Elysium |
| Challenge | Obstacle course, mastery | Dark Souls, Celeste |
| Fellowship | Social framework | Among Us, MMOs |
| Discovery | Exploration, curiosity | Breath of the Wild, Outer Wilds |
| Expression | Self-discovery, creativity | Minecraft, Dreams |
| Submission | Pastime, zone-out | Stardew Valley, idle games |

## Game Loops

### Core Loop

The repeatable cycle that forms the foundation of gameplay:

```text
Action → Reward → Progression → New Action
```

### Game Design Document (GDD) Structure

```yaml
title: "Game Name"
genre: "Action RPG"
platform: ["PC", "Console"]
target_audience: "16-35, hardcore gamers"
core_loop:
  action: "Combat encounter"
  reward: "XP, loot drops"
  progression: "Level up, unlock skills"
pillars:
  - "Player agency in story outcomes"
  - "Deep crafting system"
  - "Challenging but fair combat"
aesthetics: ["Challenge", "Fantasy", "Discovery"]
```

### Nested Loops

| Loop Level | Timescale | Example (RPG) |
|-----------|-----------|---------------|
| **Micro** | Seconds | Combat: attack → dodge → counter |
| **Core** | Minutes | Quest: accept → explore → complete → reward |
| **Meta** | Hours | Character build: level up → unlock skills → tackle harder content |
| **Macro** | Days/Weeks | Seasonal events, guild wars, leaderboard resets |

## Level Design

### Design Pillars

1. **Readability** — Player understands the space and objectives at a glance
2. **Flow** — Smooth navigation, no dead ends without purpose
3. **Pacing** — Tension and release cycle (combat → exploration → puzzle → reward)
4. **Teaching** — Introduce mechanics in safe spaces before testing them

### Level Design Process

1. **Paper design** — Sketch layout, define critical path, mark encounters
2. **Graybox** — Blockout in engine with primitive geometry
3. **Playtest graybox** — Test flow, pacing, sightlines before art investment
4. **Art pass** — Replace primitives with final art, lighting, audio
5. **Polish** — VFX, particles, ambient audio, secondary animations
6. **QA** — Bug testing, boundary testing, performance profiling

### Spatial Communication

| Technique | Purpose |
|-----------|---------|
| **Weenies** (landmarks) | Draw player toward objectives (Disney's castle principle) |
| **Breadcrumbs** | Pickups/lights along intended path |
| **Gating** | Lock progression behind ability/key acquisition |
| **Chokepoints** | Funnel players through narrative beats |
| **Vistas** | Reward exploration with visual payoff |

## Player Psychology

### Flow State (Csikszentmihalyi)

- **Challenge ≈ Skill** — Too easy = boredom; too hard = frustration
- Dynamic difficulty adjustment (DDA) keeps players in the flow channel
- Provide clear goals, immediate feedback, and sense of control

### Motivation Frameworks

| Theory | Components | Design Implication |
|--------|-----------|-------------------|
| **Self-Determination** | Autonomy, Competence, Relatedness | Player choice, skill growth, social features |
| **Bartle Types** | Achiever, Explorer, Socializer, Killer | Content for each player type |
| **Operant Conditioning** | Reinforcement schedules | Reward timing (variable ratio is most engaging) |

### Onboarding Best Practices

1. Let players do before telling them
2. One mechanic per tutorial section
3. Safe failure — let players fail without punishment in early areas
4. Contextual prompts, not text walls
5. Veteran players can skip or fast-track tutorials

## Systems Design & Balancing

### Economy Design

| Currency Type | Earnable By | Sinks |
|--------------|-------------|-------|
| **Soft currency** | Normal gameplay | Common items, upgrades |
| **Hard currency** | Premium purchase or rare earn | Premium cosmetics, time skips |
| **Energy** | Time-gated regeneration | Play sessions (mobile) |

### Balancing Methodology

1. **Spreadsheet modeling** — Define formulas for damage, health, progression curves
2. **Power budget** — Each item/character gets a fixed power budget; trade-offs within budget
3. **Internal playtesting** — Team plays the game, not just tests it
4. **Telemetry** — Track win rates, pick rates, engagement per feature
5. **Iterative tuning** — Small changes, measure impact, repeat

### Progression Curves

| Curve Type | Shape | Player Feeling |
|-----------|-------|----------------|
| Linear | Constant rate | Predictable, can feel grindy |
| Exponential | Slow start, fast growth | Power fantasy, late-game trivialization |
| Logarithmic | Fast start, diminishing returns | Accessible, respects veteran time |
| S-Curve | Slow → fast → slow | Best of both worlds, natural pacing |

## Narrative Design

### Environmental Storytelling

- Tell stories through objects, placement, and state (not cutscenes)
- "What happened here?" is more engaging than "Here's what happened"
- Every room should tell a micro-story through its contents

### Quest Design Patterns

| Type | Structure | Player Agency |
|------|-----------|--------------|
| **Main quest** | Critical path, mandatory | Low (must complete) |
| **Side quest** | Optional, character-driven | Medium (player chooses when/whether) |
| **Radiant/procedural** | Auto-generated | Low (filler, use sparingly) |
| **Branching** | Player choices affect outcome | High (consequences matter) |
| **Environmental** | Discovered through exploration | High (player-driven discovery) |

### Dialogue Systems

- **Branching trees** — Explicit choices, clear consequences
- **Hub and spoke** — Central topic, player explores branches
- **Parser-driven** — Text input interpreted (niche but immersive)
- **Contextual barks** — NPC reactions to player state/actions

## Monetization Ethics

### Ethical Monetization

- Cosmetics over power (avoid pay-to-win)
- Transparent odds for randomized rewards
- No dark patterns targeting vulnerable populations
- Age-appropriate controls and spending limits
- Value proposition: players should feel good about purchases

### Anti-Patterns to Avoid

| Pattern | Why It's Harmful |
|---------|-----------------|
| Loot boxes with opaque odds | Gambling mechanics, regulatory risk |
| Pay-to-win advantage | Destroys competitive integrity |
| Artificial scarcity pressure | FOMO manipulation |
| Energy paywalls | Punishes engagement |
| Targeting whales | Exploits vulnerable spending habits |
