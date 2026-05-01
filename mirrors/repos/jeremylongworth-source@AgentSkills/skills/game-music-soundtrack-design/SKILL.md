---
name: game-music-soundtrack-design
description: Compose, generate, direct, implement, and review game music and soundtracks. Use when Codex is asked about themes, motifs, adaptive music, interactive scores, soundtrack generation, stems, loops, transitions, vertical layering, horizontal resequencing, combat music, exploration music, boss themes, ambience beds, licensed music, music prompts, FMOD, Wwise, Unreal MetaSounds, or Unity music systems.
license: MIT
---

# Game Music Soundtrack Design

## Core Workflow

1. Identify the game genre, tone, player fantasy, world, emotional arc, platform, loop length, implementation tool, and whether the score is linear, adaptive, procedural, or hybrid.
2. Define the music's design job: orient the player, sustain flow, signal danger, reward progress, express character, shape pacing, support combat, mask repetition, or create memory.
3. Establish a sonic identity: instrumentation, harmony, rhythm, tempo range, texture, production style, cultural references, motif rules, and forbidden cliches.
4. Decide the adaptive model before composing final assets: loops, stems, layers, states, switches, transitions, stingers, one-shots, procedural generation, or playlist logic.
5. Compose and export in implementation-ready pieces: clean loop points, stems aligned to bar/beat, transition tails, intensity layers, stingers, alternate endings, and metadata.
6. Integrate with game parameters such as biome, threat, combat phase, player health, stealth, time of day, boss state, narrative beat, or fail/retry loop.
7. Review in gameplay over time. Check fatigue, repetition, emotional mismatch, transition timing, mix clashes, memory, and whether silence would be stronger.

## Creative Priorities

- Motifs: use short, recognizable musical ideas for characters, factions, places, mechanics, or emotional promises.
- Arrangement: make intensity changes through orchestration, rhythm density, register, harmony, percussion, texture, and silence rather than only volume.
- Interactivity: compose for clean transitions, re-entry points, fail states, pausing, menu returns, victory/defeat, and player-controlled pacing.
- Identity: choose a score language that belongs to the game's world and mechanics, not only its genre label.
- Fatigue control: provide enough variation, rests, and contextual restraint for repeated play.
- Diegesis: decide whether music comes from the world, the interface, the player's emotional state, or cinematic scoring.

## Generation Guidance

When using AI or procedural tools for music/soundtrack generation:

- Write prompts as music direction, not only genre tags: mood, tempo, instrumentation, arrangement, loop length, dynamic range, references by broad style, and implementation format.
- Generate multiple variations and curate by gameplay function, not novelty.
- Check rights, licensing, platform policy, dataset restrictions, and commercial-use terms before treating generated output as shippable.
- Preserve editable stems, MIDI, project files, prompts, seeds/settings, and provenance when possible.
- Avoid copying living artists, specific copyrighted tracks, or protected signatures. Describe general musical traits instead.
- Expect manual editing for loop points, mix balance, stem separation, transitions, and game-state responsiveness.

## Freshness Rule

Verify current middleware, platform, and generation-tool terms before giving tactical advice about FMOD/Wwise implementation, engine music systems, AI music licensing, platform policy, commercial use, soundtrack release rights, or content provenance.

## Implementation Priorities

- Vertical layering: use synchronized stems or layers for intensity, stealth, combat, weather, corruption, health, or location changes.
- Horizontal resequencing: use segments, playlists, transition rules, and stingers for section changes.
- Beat-aware transitions: align switches to beats, bars, phrases, or custom markers unless abrupt interruption is the intended effect.
- Mix ownership: define how music yields to dialogue, SFX, UI, voice chat, accessibility cues, and cutscenes.
- Memory and streaming: decide which music is loaded, streamed, preloaded, or banked for transitions.

## Deliverable Shape

For music/soundtrack work, provide:

- Music function and emotional target
- Sonic identity and motif direction
- Adaptive model and game parameters
- Cue/stem/loop/transition plan
- Generation or composition prompts if needed
- Rights/provenance and implementation notes
- Gameplay review criteria

## References

- Read `references/music-soundtrack-checklist.md` when composing, prompting, implementing, or reviewing game music and adaptive soundtrack systems.
