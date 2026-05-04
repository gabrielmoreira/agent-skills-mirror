# Modes

Use this file when the user's wording leaves room for multiple valid asset plans.

## Asset Types

- `player`: controllable overworld hero
- `npc`: role-readable town or field character
- `creature`: monster, beast, spirit, boss, summon
- `character`: side-view or non-overworld humanoid unit that is not specifically a player or NPC
- `spell`: castable magic or skill sequence
- `projectile`: loopable traveling object such as orb, arrow, fireball, bullet, beam segment
- `impact`: hit burst, explosion, contact FX
- `prop`: item, weapon, shrine object, pickup, deployable
- `summon`: conjured unit or creature entrance asset
- `fx`: generic visual effect sheet

## Actions

- `single`: one static sprite
- `idle`: looped breathing / stance / aura cycle
- `cast`: spell or skill wind-up / release
- `attack`: attack-only animation
- `shoot`: ranged attack body action; projectile and muzzle flash should usually be separate assets
- `jump`: airborne takeoff / rise / fall / landing action
- `hurt`: damage reaction
- `combat`: combined attack + hurt sheet
- `walk`: travel loop
- `run`: faster travel loop
- `hover`: airborne idle / travel loop
- `charge`: power-up or dash prep
- `projectile`: loopable travel motion
- `impact`: contact burst
- `explode`: stronger impact or destruction burst
- `death`: defeat / vanish / collapse sequence

## Bundle Presets

- `single_asset`: one sprite or one sheet
- `unit_bundle`
  - default: `idle` + `combat`
  - optional: `walk`
- `spell_bundle`
  - default: `cast` + `projectile` + `impact`
- `combat_bundle`
  - default: `idle` + `attack` + `hurt`
- `line_bundle`
  - default: 1-3 forms
  - per form, choose only the needed sheets
- `hero_action_bundle`
  - default: one sheet per action, often `idle` + `run` + `attack` or `shoot` + `jump`
  - keep projectiles, muzzle flashes, impacts, and dust as separate assets unless tightly attached to the body action
  - assemble an engine atlas only after each action passes QC
- `engine_atlas`
  - delivery format only when it combines unrelated actions
  - build from processed action sheets, not from one mixed-action raw image

## Sheet Presets

- `1x4`
  - projectiles
  - simple looping FX
- `2x2`
  - standard idle
  - attack / hurt / impact
  - compact side-view walk
- `2x3`
  - cast sequences
  - death sequences
  - slightly richer combat actions
- `3x3`
  - large creature idle
  - boss aura loops
  - high-value showcase idles
- `4x4`
  - topdown 4-direction player walk sheet
  - non-directional 16-frame action sequence when the user asks for richer casting, summoning, charging, transformation, or death animation
- `5x5` or `custom_grid`
  - use as raw generation only for one coherent long action sequence, prop packs, tileset-like atlases, or another single action family
  - use as a delivery atlas for mixed actions only after separate action sheets have been generated and QC'd

## Agent-First Mapping Hints

- `"make a 4-direction main hero"` -> `player` + `player_sheet`
- `"make a side-view hero with idle, run, shoot, and jump"` -> `player` + `hero_action_bundle`; generate one action sheet per action and keep projectile/impact assets separate
- `"make a healer npc"` -> `npc` + `single_asset`, `role=healer`
- `"make a healer npc walk sheet"` -> `npc` + `walk`
- `"make a boss idle"` -> `creature` + `idle`; prefer `3x3`
- `"make a wizard throwing a magic orb"` -> `spell_bundle`
- `"make a fireball projectile"` -> `projectile` + `projectile`; prefer `1x4`
- `"make a hit explosion"` -> `impact` + `impact`; prefer `2x2`
- `"make a summon entrance"` -> `summon` + `cast` or `impact`
- `"make a full fire samurai creature line"` -> `line_bundle`; plan 1-3 forms, then choose sheets per form

## Legacy Compatibility

Keep these mappings working:

- `player_sheet`: 4-direction overworld walk
- `player_walk`: 2x2 down-facing walk
- `npc_walk`: 2x2 down-facing walk
- `combat`: 2x2 attack + hurt
- `evolution`: legacy concept sheet

## Processor Defaults

- use `shared_scale=true` for any multi-frame sheet unless inconsistent scale is intentional
- use `align=bottom` or `feet` for grounded actors
- use `align=center` for floating effects, projectiles, and detached FX
- use `component_mode=largest` when raw sheets contain detached sparkles or edge debris
- use `component_mode=all` when detached effects are an intentional part of the asset silhouette
- for body-only controllable hero actions, prefer `component_mode=largest`; for projectile, impact, aura, or intentionally attached FX sheets, use `component_mode=all`
- use a layout guide for prop packs, tileset-like atlases, fixed atlas rows, and non-directional 16-frame VFX-heavy action sequences; avoid making it the default for 4-direction walk sheets

## Output Shape

- any sheet mode: transparent sheet + per-frame PNGs + GIF
- `player_sheet`: plus direction strips and four GIFs
- `single_asset`: cleaned transparent PNG
- `hero_action_bundle`: per-action folders, per-action GIFs, separate projectile/impact assets when needed, and optional assembled engine atlas
- bundles: one output folder per asset inside the bundle root
