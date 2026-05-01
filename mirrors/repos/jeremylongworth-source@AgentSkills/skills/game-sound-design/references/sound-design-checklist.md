# Sound Design Checklist

Use this checklist for game SFX, ambience, UI audio, Foley, weapons, creatures, procedural audio, and generated sounds.

## Creative Function

- The sound has a clear job: feedback, warning, reward, navigation, atmosphere, identity, or state communication.
- The sound's scale matches the event's gameplay importance.
- The palette fits the game world, UI language, and player fantasy.
- The sound remains readable with music, dialogue, ambience, and other SFX active.
- Silence or restraint has been considered where constant sound would cause fatigue.

## Construction

- Transient, body, texture, tail, and sweetener layers can be tuned separately where useful.
- Timing matches animation, hit frames, input response, VFX, and gameplay state changes.
- Variations exist for repeated sounds.
- Surface, material, size, distance, velocity, health, and intensity variants are defined where relevant.
- Loops have clean loop points and release behavior.

## Implementation

- Event, file, bus, and parameter names are clear and consistent.
- Routing supports player settings and mix control.
- Voice limits, priority, cooldowns, and virtualization are set for spam-prone sounds.
- Spatialization, attenuation, occlusion, reverb, and environmental sends fit the gameplay camera and world scale.
- Runtime parameters are documented for engineers or technical sound designers.

## Technical QA

- Levels avoid clipping and excessive loudness.
- Compression format, sample rate, streaming/loading, and memory use fit the target platform.
- The sound works on headphones, TV speakers, small speakers, and mono/downmix where relevant.
- Audio profiler or middleware profiler checks do not show runaway voices or memory spikes.

## Rights And Provenance

- Recording, library, generated, or third-party sources have clear commercial-use rights.
- Prompts, seeds/settings, source files, and edit history are retained when generated assets are used.
