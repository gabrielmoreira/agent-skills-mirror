---
name: godot-version-migration
description: "Incremental Godot 4.x version migration hub. Use when upgrading a Godot project hop-by-hop from 4.0 toward the library target (currently 4.7), migrating APIs after a minor engine release, or finding Domain Skill-scoped migration notes. Trigger keywords: upgrade Godot, migrate 4.0 to 4.1, upgrading_to_godot, version migration, breaking changes, TileMapLayer, AnimationMixer, RichTextLabel ImageUnit, Jolt Physics, stretch mode, area_mask."
---

# Godot Version Migration

Orchestrator for **incremental** Godot 4.x upgrades. Domain Skills document **current** APIs; this hub owns the upgrade path.

**Library target:** Godot **4.7+**

## NEVER Do

- **NEVER skip hops** — upgrade `4.0 → 4.1 → 4.2 → … → 4.7` one minor at a time; stabilize after each hop.
- **NEVER** treat Domain Skill bodies as migration changelogs — load `references/<topic>.md` (mirrored from each skill’s `references/migration-notes.md`).
- **NEVER** mix server/client Godot minors for high-level multiplayer (especially across 4.2→4.3 SceneMultiplayer protocol changes).
- **NEVER** choose Mesh “Restart & Upgrade” without VCS backup (4.1→4.2 mesh format).
- **NEVER** assume 4.6 AudioStreamPlayer `area_mask` or stretch defaults still apply after opening in 4.7.

## Workflow router (MANDATORY)

| Branch | Load | Do NOT Load |
|--------|------|-------------|
| Detect version / plan hops | This `SKILL.md` + [hop-index.md](references/hop-index.md) | All module notes at once |
| Single hop API breaks | Official guide for that hop + module notes for systems you touch | Unrelated genre notes |
| Godot 3.x project | Official [3→4 guide](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html) first | Jumping into 4.6→4.7 notes |
| Discover peer Domain Skills | [godot-master](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-master/SKILL.md) | Treating this hub as a coding tutorial |

### Steps

1. Read `project.godot` / user-stated engine version.
2. If `< 4.0`, complete 3→4 migration, then continue from 4.0.
3. While `current < 4.7`, perform **exactly one** hop to `current + 0.1`:
   - Open the official upgrading page for the destination version.
   - From [hop-index.md](references/hop-index.md), open only module notes for subsystems present in the project.
   - Apply code/scene/project-setting fixes; open the project in the new editor; run playtests.
4. Repeat until on 4.7+.
5. Resume Domain Skills for feature work (current-API guidance).

## Hop table

| Hop | Official guide |
|-----|----------------|
| 4.0 → 4.1 | https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html |
| 4.1 → 4.2 | https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html |
| 4.2 → 4.3 | https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html |
| 4.3 → 4.4 | https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html |
| 4.4 → 4.5 | https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html |
| 4.5 → 4.6 | https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html |
| 4.6 → 4.7 | https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html |

Cross-skill checklist: [references/hop-index.md](references/hop-index.md)

## Module directory

Mirrored Domain Skill migration notes live at `references/<topic>.md` (e.g. `references/2d-physics.md`). After Domain Skill waves, maintainers sync with:

```text
sync_godot_version_migration.py --all
```

## Reference

### Official docs

- [Migrating to a new version](https://docs.godotengine.org/en/stable/tutorials/migrating/index.html)
- [Docs changelog](https://docs.godotengine.org/en/stable/about/docs_changelog.html)

### Related Skills

#### Master
- [godot-master](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-master/SKILL.md) — Library router for current Domain Skill modules after migration is complete.

#### Complements
- [godot-project-foundations](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-project-foundations/SKILL.md) — Project settings / structure once on the target version.
- [godot-export-builds](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-export-builds/SKILL.md) — Re-validate exports after each hop that touches platforms.
