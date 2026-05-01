# Music Soundtrack Checklist

Use this checklist for game music, adaptive scores, generated soundtrack concepts, stems, loops, and implementation plans.

## Creative Direction

- The score has a defined emotional role in the game loop.
- Main motifs connect to characters, factions, places, mechanics, or themes.
- Instrumentation and production style fit the world and avoid unsupported cliches.
- Tempo, meter, harmonic language, texture, and density support the intended pacing.
- Silence and low-density music are used intentionally, not as an afterthought.

## Adaptive Structure

- The implementation model is chosen: linear track, loop, vertical stems, horizontal segments, procedural system, playlist, or hybrid.
- Transition points are bar/beat/phrase-aware where musical continuity matters.
- Stingers, transition tails, intros, outros, alternate endings, and fail/retry behavior are planned.
- Game parameters driving music are explicit and bounded.
- Repeated play has enough variation to avoid fatigue.

## Export And Assets

- Stems share the same start point, tempo map, sample rate, and loop length.
- Loop points are clean and tested.
- File names include cue, state, intensity, stem, BPM, key if relevant, and version.
- Mix versions are available for implementation, trailer/cinematic use, and soundtrack release if needed.
- Source sessions, MIDI, stems, bounces, prompts, seeds/settings, and licensing notes are preserved.

## Integration

- Music bus routing, ducking, snapshots/states, and player volume controls are defined.
- Music yields appropriately to dialogue, critical SFX, UI, voice chat, and accessibility cues.
- Memory, streaming, preloading, and bank organization support fast transitions.
- Debug controls let designers force states, intensities, transitions, and stingers.

## Generation And Rights

- AI-generated or procedurally generated music is checked for license, commercial rights, platform policy, and provenance.
- Prompts avoid copying specific copyrighted tracks or living artists' signatures.
- Generated output is edited and tested for loopability, mix quality, musical coherence, and gameplay fit before use.
