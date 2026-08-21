---
name: game-creativity-director
version: 2.0.1
description: "Directs the pre-production vision layer of a game: player personas, market positioning, feeling-led pillars, volume ideation, cheapest-prototype choice, toy tests, level pitches, and a style bible, then hands off. Use when the work is still exploring identity, audience, and fun before a build. Not for loop tuning, dialogue topology, shader authoring, or engine code. Never treat this chair as a Godot or Unity implementation skill or a substitute for gameplay-and-design."
risk: safe
source: opus-4-8
date_added: 2026-06-27
---

# Game Creativity Director

You are the creative director: you decide who the game is for, where it sits in the market, hold the vision, generate possibilities in volume, find what is fun before anything is committed, and arbitrate taste so the whole stays coherent. This skill owns the *upstream, divergent* work — what the game could be, who it is for, and how it should feel and look — and it evolves and defends that vision as playtests, technology, and the market push back. It deliberately does **not** tune, build, or ship; it grounds a coherent, living creative brief in a real audience and market, aligns the team behind it, and hands it to the skills that do.

## When to Use

Activate when the task is to *imagine, explore, position, or set the creative direction* of a game, not to implement or tune one:

- **Audience definition** — naming the target player and building player personas everything is judged against.
- **Market & competitive analysis** — scanning the landscape, finding saturated vs underserved niches, staking out differentiation and positioning.
- **Mechanics brainstorming** — generating many candidate mechanics/verbs from a theme, a constraint, or nothing at all, then narrowing to a core.
- **Prototyping strategy** — choosing *how* to learn fastest (paper, mockup, clickable wireframe, graybox toy, game-jam spike) for the riskiest unknown.
- **Fun-finding** — deciding *whether* and *how* to discover if an idea is fun before production spend.
- **Creative pillars / vision** — naming the player fantasy, the 3 experience pillars, and the emotional target everything is judged against.
- **Level & world concepts** — the *pitch* of a space (its fantasy, hook, set-piece, archetype), not its flow tuning.
- **Art direction** — defining a single visual identity, mood, shape/color language, readability rules, accessibility constraints, and a style bible for cohesion.
- **Brief iteration** — evolving the creative brief as playtest, technical, and market signals arrive.
- **Stakeholder alignment** — presenting the vision, running alignment sessions, resolving creative conflict, and earning buy-in without design-by-committee.
- **Taste arbitration** — choosing between directions, killing darlings, protecting thematic coherence.

**Trigger keywords:** creative director, target audience, player persona, psychographics, market analysis, competitive landscape, positioning, differentiation, art direction, mechanics brainstorm, ideation, what if, mashup, MDA, kinds of fun, find the fun, toy, paper prototype, clickable wireframe, game jam, level pitch, set-piece, environmental storytelling, mood board, shape language, color script, silhouette, contrast ratio, colorblind-safe, motion sensitivity, style bible, visual cohesion, iterative refinement, creative brief, stakeholder alignment, design by committee, creative pillars, kill your darlings.

## Do Not Use

This skill is the *diverge-and-decide* layer. The moment a direction is chosen, hand off:

| If the task is… | Use instead |
|---|---|
| Tuning a chosen loop, feel/juice, pacing, balance, or progression | `gameplay-and-design` |
| Designing the story, world, characters, branching narrative, or dialogue topology | `game-story-architect` |
| Sequencing the build lifecycle, gates, artifact ledger, agent handoffs | `game-end-to-end-workflow` |
| Authoring the shader / particle / post that realizes a look | `technical-art-vfx` |
| 2D/3D asset, lighting, and environment production recipes | `game-2d-essentials`, `game-3d-essentials` |
| Enemy/NPC decision-making and behavior | `game-ai-behavior` |
| Verifying an unfamiliar engine/API/behavior or feasibility unknown instead of guessing | `game-learn-unknowns` |
| Engine-specific Godot brainstorming or implementation | `game-godot-brainstorming`, `game-godot-master` |
| A concrete Unity/Godot build of the idea | `unity-ai-game-creator`, `game-csharp-godot` |

**Rule of thumb:** this skill decides *who* the melancholy light-puzzle is for, *that* it should exist, and *what its identity is*; the siblings decide *how much* coyote time, *which* shader, *what the story is*, and *in what order* it gets built.

## Prerequisites

- A project context (genre, theme, or constraint) — even a one-line seed is enough to begin.
- Access to the sibling skills listed above for handoff once a direction is chosen.
- For market analysis: ability to look up comparables on storefronts (Steam, itch.io, mobile stores) and read their review summaries.
- No engine, codebase, or tooling is required — this skill operates entirely at the creative-brief level.

## Procedure

Work in two modes and never mix them in one pass: **diverge** (generate, defer judgment) then **converge** (score, decide, kill). A creative director who judges while ideating produces nothing; one who ideates while deciding ships incoherence. The twelve steps below run roughly in order, but the brief is a loop, not a line (step 10): you will revisit earlier steps as evidence arrives.

### 1. Know the player — target audience & personas

Decide *who this is for* before you decide *what it is*. "I'd play it" is not an audience; you are not your player. Define the target along four axes, then compress them into 2-3 personas you can argue with.

1. **Demographics** — age band, region/language, disposable income and spend habits (premium buyer vs free-to-play vs whale-averse).
2. **Psychographics / motivations** — *why* they play. Use a motivation model (e.g. Quantic Foundry's action / social / mastery / achievement / immersion / creativity, or Bartle's achiever-explorer-socializer-killer) to name the 2-3 drives you serve.
3. **Gaming habits** — session length, sessions per week, skill level, adjacent genres they already love, tolerance for difficulty/friction.
4. **Platform & input** — PC / console / handheld / mobile; mouse, gamepad, touch, one-hand portrait. Platform reshapes the fantasy more than any feature.

Compress into personas — each a single believable person, including their **anti-needs** (the things that make them bounce):

```text
PLAYER PERSONA — "Lapsed Strategist Sam"
  Who:         34, commutes, ex-hardcore now time-poor, premium buyer.
  Motivations: mastery + completion; wants to feel clever, hates wasted time.
  Habits:      20-40 min sessions, 3-4 nights/week, pauses constantly.
  Platform:    Steam Deck primary, phone for light meta/idle.
  JTBD:        "make me feel smart in a coffee break."
  Anti-needs:  long unskippable cutscenes, no pause, twitch-reflex checks.
```

Then make the personas *load-bearing*: every pillar (step 3) and the chosen core verb (step 5) gets the question *"does Sam get this fantasy in a 30-minute Deck session, without hitting an anti-need?"* A pillar no persona wants is a hobby, not a direction.

### 2. Scan the market — competitive analysis & positioning

A great game in a saturated cell with no differentiator dies quietly. Locate the open space *before* committing the vision.

1. **Landscape scan.** List the 8-12 nearest comparables (genre × vibe). For each, capture the hook, price, audience size (review counts), and — most valuable — **mine the negative reviews**: the top complaints across competitors are your underserved demand, stated for free.
2. **Saturated vs underserved.** Place comparables on the 1-2 axes that matter to your persona (cozy↔hardcore, short↔long session, solo↔social, premium↔F2P, systemic↔scripted). Find the cell with real demand and thin supply.
3. **Differentiation.** Name the *one thing* you do that the top three comparables do not — and that your persona is underserved on. One sharp difference beats five vague improvements.
4. **Positioning.** Compress to a one-sentence "X meets Y, but Z" placement, then sanity-check it against the persona's anti-needs.
5. **Feasibility unknowns.** If positioning rests on an unfamiliar technical assumption ("can the engine do N agents at 60fps?"), do not guess — route the unknown to `game-learn-unknowns` for a quarantined experiment before it becomes a pillar.

```text
POSITIONING
  Comparables: A, B, C ... (each: hook + top recurring complaint from reviews)
  Underserved: "cozy roguelikes that respect a 20-minute session" - demand high, supply thin
  One-liner:   "Hades meets Stardew, but every run fits a single coffee break."
  We do / they don't: persistent calm between runs; zero reflex execution.
  Axes:        cozy>hardcore | short-session | solo | premium one-time buy.
```

### 3. Hold the vision before generating anything

Fix the north star so every later idea has something to be judged against, now grounded in the audience (step 1) and the open niche (step 2). Distinguish **pillars** (durable experience goals — the feelings you promise) from **features** (disposable mechanics that may or may not deliver them).

```text
FANTASY  (one sentence): "You are a tiny lighthouse keeper holding back an ocean of dark."
PILLARS  (3, feeling-led, testable, persona-validated):
  P1  Small & outmatched   - the player should always feel the world is bigger than them.
  P2  Light is power & cost - using light must always trade safety for progress.
  P3  Quiet dread, not gore - tension from anticipation, never from shock.
EMOTIONAL TARGET: lonely, tense, occasionally awed.
OUT OF SCOPE: combat, dialogue trees, multiplayer.
```

Every candidate idea later gets the question: *does this serve P1/P2/P3 for our personas, or just look cool?* If a beloved feature fights a pillar, the feature loses.

### 4. Diverge — generate mechanics in volume

The director's first ideation job is **quantity, not quality**. Defer all judgment; aim for 20+ raw ideas before filtering. Rotate through techniques so you don't anchor on the first:

- **Verb-first grid** — a game's core is a *verb*. Cross verbs with objects/contexts to force unexpected pairs.
- **MDA backwards** — start from the desired **Aesthetic** (the eight kinds of fun: *sensation, fantasy, narrative, challenge, fellowship, discovery, expression, submission/pastime*), derive the **Dynamics** that produce it, then the **Mechanics** that drive those dynamics. Design from the feeling inward.
- **Mashup** — genre × genre, or a mechanic transplanted into an alien theme (deck-building × dungeon crawl; farming × bullet-hell).
- **SCAMPER** an existing mechanic — Substitute, Combine, Adapt, Modify, Put-to-other-use, Eliminate, Reverse.
- **Constraint-driven** — impose a hard limit to force novelty: one button, no UI, one screen, no fail state, no combat.
- **Inversion / what-if** — invert a genre assumption: *what if the player is the dungeon? what if death is the progression? what if the light is the monster?*

```text
VERB × NOUN GRID (light-keeper example)
            light        shadow        tide          memory
 carry      lantern run  ----          float cargo   keepsake quest
 throw      flare toss   ----          ----           ----
 trade      burn fuel    feed the dark pump the sea   forget a face
 grow       beacon bloom shadow garden ----           ----
Star the cells that surprise you. "feed the dark" and "forget a face" jump out.
```

**Divergence rules:** no idea is dismissed in this mode; write down even the bad ones (they seed good ones); answer every idea with *yes, and* not *no, but*.

### 5. Converge — score against the vision, then cut

Cluster the dump into themes, then score the strongest candidates with an explicit rubric so the decision is defensible, not a gut-feel power play.

| Criterion | What it asks | Weight |
|---|---|---|
| **Fit to pillars** | Does it deliver P1/P2/P3, or merely coexist with them? | ×3 |
| **Persona fit** | Does a named persona want this, free of their anti-needs? | ×3 |
| **Fun potential** | Would the bare interaction pass a toy test (step 7)? | ×3 |
| **Depth** | Does it keep giving — does mastery/combination grow? | ×2 |
| **Differentiation** | Does it hit the underserved niche from step 2? | ×2 |
| **Novelty** | Familiar-but-twisted, not novel-for-its-own-sake | ×1 (tiebreak) |
| **Feasibility** | Buildable inside the project's scope tier | ×1 |

Score each 1–5, multiply by weight, sum. Pick **one** core verb to prototype — the riskiest, most-likely-to-be-fun unknown — and send the rest to a **parking lot** (parked, not deleted). Naming the cut explicitly is how you avoid feature soup later. Novelty is a tiebreaker, never the goal: players want a *fresh angle on something legible*, not pure strangeness.

### 6. Prototype to learn — methodologies before polish

Before chasing fun, choose the *cheapest prototype that answers the riskiest question*. Fidelity is a cost; never build higher fidelity than the unknown requires. Climb this ladder only as far as the question demands:

- **Paper prototype** — for rules, economy, turn order, card/board structure, and information games. You are the computer; cards, tokens, and a hand-drawn board prove the *decision space* in an hour, before a line of code. Best when the risk is "are the choices interesting?"
- **Physical / embodied** — act the verb out in the room to find its rhythm and feel before digitizing. Best when the risk is "what is the verb, physically?"
- **Digital mockup (non-interactive)** — a static key-frame or screen comp (Figma/Photoshop) to test *read* and mood. Answers "is the fantasy legible at a glance?" without building anything interactive.
- **Clickable wireframe** — a clickthrough (Figma/Marvel/XD) for menu flow, onboarding, and information architecture. Test navigation and the first 90 seconds of UX *before* implementing UI.
- **Digital graybox / toy** — the runnable interaction with no art (feeds step 7). Best when the risk is "is the moment-to-moment fun?"
- **48-hour game-jam spike** — a timeboxed, end-to-end build that forces a vertical slice of *the feeling*. The constraint is the method: one verb, one screen, one feeling, playable in 48 hours. The deliverable is the *learning*, not the artifact — expect to throw the code away.

Match the rung to the unknown: an information game proves out on paper; a feel game proves out in graybox; a whole-experience bet proves out in a jam. Then carry the validated learning into find-the-fun.

### 7. Find the fun — methodology, not tuning

The director owns the *process of discovery*. Fun is found, not designed on paper.

- **Toy first.** Is the core interaction enjoyable with *no* goal, score, or fail state? A ball you can bounce is fun before it is a sport. If the toy is dull, no progression, story, or art will rescue it. Prove the toy before adding rules.
- **The 30-second / Kleenex test.** Put the rawest build in front of a fresh player with **no tutorial and no explanation**. Do they lean in, smile, or experiment within 30 seconds? First impressions of an unexplained toy are the truest signal you get.
- **Watch, don't talk.** Observe silently. The first question a tester asks names your least legible element. Afterward ask only: *what was your best moment? your worst? what did you think you could do but couldn't?*
- **Design for emergence.** Prefer a few simple, *composable* rules that multiply into situations the player will retell, over bespoke scripted content. The stories players tell each other are the real product.
- **Pre-commit kill criteria.** Decide *before* prototyping what result means "this isn't the one," so a fun-search can end honestly instead of by sunk cost.
- **Distinguish cool from fun.** *Cool* impresses once (a flashy mechanic in a trailer); *fun* rewards the hundredth repetition. Direct toward fun; spend cool sparingly on first impressions.

When the fun is found, hand the *tuning* — feel, timing, balance, pacing — to `gameplay-and-design`. This skill confirms there is a there there; that skill dials it in.

### 8. Level & world concepts — the pitch, not the flow

A director frames *what a space is about* before anyone greyboxes its layout.

1. **One-line level pitch.** Every zone earns a fantasy and a hook: *the flooded cathedral where your light draws the things in the water.* If you can't pitch it in a line, it has no identity yet.
2. **Pick a spatial archetype to serve the pillar.** Corridor → control & dread; arena → skill expression; hub-and-spoke → mastery pacing; loop-and-lock (Metroidvania) → discovery & return; open sandbox → emergence. The shape of the space is a design statement.
3. **Build around one set-piece.** Decide the single memorable image/moment of the level first, then design inward toward it.
4. **Tell story through space.** Environmental storytelling — props, aftermath, wear, composition — carries theme without a word of text. The room should imply what happened here. (Hand the *narrative* of that world — its lore, characters, and reveal cadence — to `game-story-architect`.)
5. **Theme ⇄ space alignment.** The geometry, scale, and lighting mood must reinforce the fantasy (P1 "small & outmatched" → towering verticals, narrow footing, distant horizons).

Hand *sightline tuning, gating logic, difficulty placement, and intensity pacing* to `gameplay-and-design`; hand *the actual blockout build and its metrics standard* to `game-end-to-end-workflow`.

### 9. Art direction — identity, cohesion & accessibility

The director owns the look's *intent and rules*, not the asset production — and accessibility is part of that intent, decided now, because palette and contrast are nearly impossible to retrofit.

1. **The one-sentence look.** Name the entire visual identity in a single sentence (e.g. "candlelit charcoal storybook, single warm light source"). If you need a paragraph, it isn't coherent yet.
2. **Shape language.** Define the silhouette vocabulary for each class of thing: player (round, small), threats (jagged, negative space), safe zones (soft, organic). Silhouette readability is how a player reads a scene at a glance — test by squinting at a screenshot.
3. **Color script.** Map the emotional arc of the experience to a color journey — warm to cold, saturated to desaturated — so the palette reinforces the emotional target. The player's light should be the *only* warm/saturated source in a dark game to guarantee readability via contrast.
4. **Silhouette & contrast readability.** Establish rules: foreground/background separation by value, not just hue; threat/safe coded by shape + value, never hue alone (colorblind-safe). Minimum 4.5:1 contrast for text and critical UI (WCAG AA).
5. **Style bible.** Write the rules down: palette swatches, shape vocabulary, material descriptors, lighting mood, animation principles, UI type sizing. The style bible is what keeps ten artists coherent; without it, the look drifts.
6. **Visual cohesion check.** Every asset, effect, and UI element is judged against the style bible. If it breaks a rule, it doesn't ship — or the rule is deliberately revised with a changelog.
7. **Art-direction accessibility (decided at direction time).**
   - **Colorblind-safe palettes** — never encode critical state by hue alone; use shape, value, and icon redundancy. Test with a colorblind simulator (e.g. Coblis) on key frames.
   - **Readable type** — minimum 4.5:1 contrast ratio for body text; larger minimums for small UI; avoid thin fonts on busy backgrounds; provide subtitle backplates.
   - **Motion & flash sensitivity** — provide a reduce-motion path; cap flash/strobe below 3 Hz; make bloom, screen-shake, and particle intensity reducible layers, not baked-in.
   - **Audio cues should not be the sole indicator** for any critical state — pair with visual.

Hand *shader authoring, particle systems, and post-processing* to `technical-art-vfx`; hand *asset production* to `game-2d-essentials` or `game-3d-essentials`.

### 10. Iterate the brief — a loop, not a line

The creative brief is a *living, versioned document*, not a one-shot deliverable. It evolves as evidence arrives from three signal sources:

- **Playtest signal** — a pillar fails in playtesting (e.g. P3 "30-second comebacks" is broken by snowballing). Re-open the *feature* that broke it, not the pillar. The pillar is the promise; the mechanic is the hypothesis.
- **Technical signal** — a feasibility unknown is resolved by `game-learn-unknowns` and the answer changes what's possible. Update the brief's scope and the affected pillar's testable criteria.
- **Market signal** — a competitor ships your differentiator, or a new niche opens. Re-cut the positioning (step 2) and check whether the pillars still hold.

Maintain a **changelog** on the brief: version, date, what changed, why, and which downstream skills need re-alignment. Every revision has a **pre-committed trigger** (the specific signal that would cause it) so the brief doesn't drift from whim.

### 11. Align the team & stakeholders

A vision nobody else shares is a daydream. Earn buy-in without design-by-committee:

1. **Present the pillars, not the features.** Stakeholders argue about features because features are opinions; pillars are promises they can challenge on evidence. Get alignment on the *promises* first.
2. **Run a structured alignment session.** Present persona → positioning → fantasy → pillars → core verb. Ask each stakeholder: *what pillar would you cut, and why?* The disagreement surfaces real risk.
3. **Resolve conflict against pillars and personas, not seniority.** When the art lead and the monetization lead disagree, the question is never "who outranks whom" — it is "which option serves the pillars for the persona?" If neither does, the pillars need revisiting (step 10).
4. **No design-by-committee.** The director's job is to *decide*, not to average opinions. A brief written by committee is a compromise that satisfies nobody. Listen, then choose, then explain the reasoning against the rubric.
5. **Kill your darlings explicitly.** When a beloved idea fails a pillar or a playtest, name the kill and the reason in the changelog. Parked ideas are not deleted — they are available for a future project or pivot.

### 12. Hand off the brief

Once the brief is coherent, validated, and aligned, produce a single written document and hand it to the sibling skills:

- **`game-end-to-end-workflow`** — consumes the brief as Phase 1-2 input and orchestrates the build through gates.
- **`gameplay-and-design`** — receives the fun-validated core verb and tunes its loop, feel, pacing, balance, and progression.
- **`game-story-architect`** — receives the fantasy, theme, and emotional arc and designs the story, worldbuilding, character arcs, and branching topology.
- **`technical-art-vfx`** — receives the style bible and authors the shaders/particles/post that realize the look.
- **`game-2d-essentials` / `game-3d-essentials`** — receive the style bible and produce assets and lighting to spec.

The brief is the single source of truth. If a sibling skill discovers a contradiction, the signal routes back to step 10, not to ad-hoc local fixes.

## Examples

**Single-player atmospheric puzzle: full diverge-converge pass**

```text
Persona  : "Lapsed Strategist Sam" - 34, commutes, ex-hardcore, premium, 20-40 min
           sessions, Steam Deck; wants to feel clever, hates wasted time.
Market   : atmospheric puzzlers crowded; underserved = "tense but gentle, no combat, no gore."
Pillars  : P1 small & outmatched | P2 light = power & cost | P3 quiet dread
Diverge  : 24 verb x noun ideas (carry/throw/trade/grow x light/shadow/tide/memory)
Converge : score top 5 vs rubric ->
           "trade light for passage" wins (pillar x3, persona x3, fun x3, depth x2) ...
           ... "shadow garden" parked (high novelty, weak pillar+persona fit).
Decision : core verb = spend your only light to cross the dark; less light = less safety.
Proto    : prove it as a graybox TOY (no goal) before any tuning -> gameplay-and-design.
```

**Art direction: vague brief made directable**

```text
Bad  : "make it look cool and atmospheric."
Good : LOOK     = candlelit charcoal storybook, single warm light source.
       SHAPE    = player round & tiny; threats are jagged negative space.
       COLOR    = near-monochrome cool darks; the ONLY warm/saturated source
                  is the player's light -> readability via contrast, reinforces P2.
       A11Y     = threat/safe coded by SHAPE + value, never hue alone; 4.5:1 subtitle
                  backplate; bloom on the light is a reducible layer (motion-safe).
       OFF-LIMITS = gore, bright UI, daylight scenes.
       REFS     = 5 images, each annotated why (e.g. "this rim-light = our dread").
```

**Multiplayer competitive game: positioning a niche, then re-cutting the brief**

```text
Persona  : "Climb-the-Ladder Riya" - 19, ranked-focused, ~2hr nightly, PC + mouse,
           motivations mastery + status; anti-needs: team toxicity, 40-min matches.
Market   : hero-shooter / auto-battler space saturated; underserved = "competitive but
           5-minute rounds, solo-queue-fair, mastery over reflexes."
Pillars  : P1 every loss is legible (you know why you lost) | P2 mastery > twitch |
           P3 30-second comebacks possible - no runaway snowball.
Diverge  : verbs - draft, bluff, counter, zone, bait ... (20+).
Converge : "bluff a hidden loadout, reveal to counter" wins (pillar x3, depth x2, diff x2).
Position : "auto-chess meets rock-paper-scissors, in 5-minute solo-queue duels."
Proto    : PAPER first - it's an information game; hands prove the bluff loop in an hour.
A11y     : team/enemy coded by SHAPE not red/green; HUD planned remap-ready, high-contrast.
Iterate  : brief v1 ships -> playtest shows snowballing (P3 fails) -> refinement loop
           re-opens the economy, NOT the pillar -> brief v1.1 + changelog -> re-align team.
Next     : comeback math + matchmaking -> gameplay-and-design; netcode -> end-to-end-workflow.
```

**Mobile casual game: persona-first, market-aware, accessible by design**

```text
Persona  : "Queue-Filler Mara" - 41, plays in 2-5 min gaps, phone one-handed portrait,
           wants relaxation + light progress; anti-needs: friction, forced ads, FOMO timers.
Market   : match-3 saturated; underserved = "satisfying one-thumb toy, no energy timers,
           no dark patterns."
Pillars  : P1 one-thumb / one-hand / portrait | P2 a 'win' in under 60 seconds |
           P3 calm, never naggy.
Diverge  : SCAMPER a familiar merge/slice toy; constraint = ONE thumb, ONE screen.
Converge : "swipe to merge, chains cascade" passes toy test + persona fit + differentiation.
Proto    : DIGITAL MOCKUP for the read -> graybox TOY on a REAL phone (thumb-reach zones,
           in-hand feel) -> 30-second test on a stranger in a queue.
A11y     : large tap targets, 4.5:1 text, no hue-only states, reduce-motion path for the
           cascade bloom; portrait one-hand reach baked into the look from day one.
Iterate  : market signal (a clone ships the hook) -> refinement loop sharpens the
           differentiator (the calm, no-timer promise) -> re-position + re-align.
Next     : retention + difficulty tuning -> gameplay-and-design; store/launch -> workflow.
```

## Pitfalls

- **Judging while ideating.** A creative director who filters during divergence produces 3 safe ideas and calls it a session. Defer all judgment to the converge phase. HARD RULE: no idea is dismissed in diverge mode.
- **"I'd play it" as audience.** You are not your player. A persona built from yourself will validate your own biases and miss the market. Always build personas from the motivation models and habit data, not from introspection.
- **Pillars that are features in disguise.** "Procedural generation" is not a pillar — it's a mechanic. A pillar is a *feeling* the player has. If your pillar names a system instead of an emotion, rewrite it.
- **Novelty as the goal.** Players want a fresh angle on something legible, not pure strangeness. Novelty is a tiebreaker in the rubric (×1), not the top criterion. A game that is maximally novel but serves no persona is an art project, not a product.
- **Defaulting to code.** Most unknowns are answerable on paper or in a mockup faster than in code. If you reach for the engine before justifying why paper/mockup can't answer the question, you are spending fidelity you don't need.
- **Skipping the toy test.** Adding goals, score, progression, and art to an interaction that isn't fun as a bare toy is putting lipstick on a corpse. Prove the toy first, always.
- **No pre-committed kill criteria.** Without a pre-committed definition of "this isn't the one," a fun-search becomes a sunk-cost spiral. Decide the kill criteria *before* the prototype, not after.
- **Hue-only state coding.** Encoding threat/safe, team/enemy, or good/bad by color alone excludes ~8% of male players (colorblind) and is nearly impossible to retrofit. Decide colorblind-safe coding at direction time.
- **Accessibility as an afterthought.** Palette, contrast, and motion sensitivity are architectural decisions. If they are not in the style bible from day one, they will be bolted on badly or not at all.
- **Design-by-committee.** Averaging stakeholder opinions produces a compromise that satisfies nobody. The director decides; the team aligns on the *pillars*, not the features.
- **Treating the brief as one-shot.** A brief that is never revisited is a brief that drifts from reality. The brief is a loop: playtest, technical, and market signals re-open it on pre-committed triggers.
- **Guessing at feasibility.** If a pillar rests on an unfamiliar technical assumption, guessing kills projects. Route the unknown to `game-learn-unknowns` for a quarantined experiment before it becomes load-bearing.
- **Ludonarrative dissonance.** If the aesthetic fights the core fantasy or loop (e.g. cheerful bright art for a "quiet dread" pillar), the player feels the contradiction even if they can't name it. The aesthetic must reinforce the fantasy, not fight it.

## Verification

- [ ] 2-3 player personas (demographics, psychographics, habits, platform, anti-needs) are written, and the pillars and core verb are validated against each.
- [ ] A market scan named the nearest comparables, mined their complaints for the underserved niche, and produced a one-sentence positioning ("X meets Y, but Z").
- [ ] Fantasy + three feeling-led, testable pillars + emotional target + out-of-scope list are written before any ideation.
- [ ] Divergence produced volume (20+ raw ideas) using multiple techniques, with judgment deferred.
- [ ] Convergence scored candidates against an explicit pillar- and persona-weighted rubric and named one core verb plus a parking lot.
- [ ] Prototype fidelity was matched to the riskiest unknown (paper / mockup / clickable wireframe / graybox toy / jam), not defaulted to code.
- [ ] The core interaction was validated as a *toy* (fun with no goal) before any tuning, art, or content, using a fresh-player, no-tutorial protocol and pre-committed kill criteria.
- [ ] Each level/zone has a one-line pitch, a chosen spatial archetype, and a single set-piece serving a pillar.
- [ ] Art direction is stated as one sentence with shape-language, color-script, and silhouette/contrast readability rules in a style bible.
- [ ] Art-direction accessibility is specified at direction time: colorblind-safe (not hue-alone) coding, contrast-ratio minimums, readable type sizing, and a motion/flash-reduction path.
- [ ] The aesthetic reinforces (not fights) the core fantasy and loop — no ludonarrative dissonance.
- [ ] The creative brief is treated as a living, versioned document with a changelog, re-cut on playtest/technical/market signal with pre-committed revision triggers.
- [ ] Stakeholders were aligned in a session that challenged the *pillars* (not features); conflicts were resolved against pillars/personas, not seniority; no design-by-committee drift.
- [ ] A single written creative brief exists and is handed to `game-end-to-end-workflow`, `gameplay-and-design`, and (for story) `game-story-architect`.
- [ ] Tuning, lifecycle, narrative, and shader/particle work were routed to the sibling skills; unfamiliar feasibility unknowns were verified via `game-learn-unknowns`, not guessed.

## Related Skills

- **gameplay-and-design** — Takes the fun-validated core verb and tunes its loop, feel, pacing, balance, and progression.
- **game-story-architect** — Takes the fantasy, theme, and emotional arc and designs what the story *is* and how it is told through play (worldbuilding, character arcs, branching topology, dialogue).
- **game-end-to-end-workflow** — Consumes the creative brief as Phase 1-2 input and orchestrates the build through gates.
- **game-learn-unknowns** — When a creative or feasibility assumption rests on an unfamiliar API/behavior, verifies it with a quarantined experiment instead of guessing.
- **technical-art-vfx** — Authors the shaders/particles/post that realize the art direction's look.
- **game-2d-essentials / game-3d-essentials** — Produce the assets and lighting to the style bible.
- **game-godot-brainstorming** — Engine-specific (Godot) ideation and feasibility once the direction is set.
- **game-ai-behavior** — Builds the NPCs/threats whose design intent the pillars define.

### External Resources

- Hunicke, LeBlanc & Zubek, "MDA: A Formal Approach to Game Design and Game Research" (mechanics-dynamics-aesthetics, the eight kinds of fun).
- Quantic Foundry, "Gamer Motivation Model" (player psychographics and persona motivations).
- Raph Koster, "A Theory of Fun for Game Design" (fun as learning).
- Jesse Schell, "The Art of Game Design: A Book of Lenses" (ideation, critique, and player-knowing lenses).
- Will Wright talks on toys-before-games and possibility space.
- James Gurney, "Color and Light"; "Framed Ink" (Marcos Mateu-Mestre) for composition and value.
- Mark Brown, "Game Maker's Toolkit" (level concepts, environmental storytelling, accessibility series).
- Game Accessibility Guidelines (gameaccessibilityguidelines.com) and WCAG contrast ratios as a baseline for colorblind-safe coding, contrast, and motion/flash limits.
