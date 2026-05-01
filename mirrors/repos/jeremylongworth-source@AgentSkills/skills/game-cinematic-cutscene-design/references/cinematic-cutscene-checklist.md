# Cinematic Cutscene Checklist

Use this checklist for game cutscenes, intro videos, trailers, dialogue cinematics, boss reveals, level flythroughs, and prerendered or real-time cinematic sequences.

## Story And Purpose

- The scene has one clear job in the player journey.
- The beat sheet identifies what changes by the end of the scene.
- The cutscene does not repeat information the player already understands unless repetition creates emotion or contrast.
- The scene ends with a clear next playable objective or emotional state.

## Shot Design

- Every shot has a subject, action, camera intent, and duration.
- Staging preserves geography, eyelines, screen direction, and action continuity.
- Camera motion has motivation and does not fight character/action readability.
- Silhouettes, focal points, lighting, and contrast guide attention.
- Shot length matches the complexity of the information shown.

## Gameplay Integration

- Player control, camera control, UI, time scale, physics, AI, and input mappings are locked and restored intentionally.
- Entry and exit positions are safe and coherent.
- Gameplay events triggered by the timeline are documented and idempotent where possible.
- Skip behavior leaves the game in the same valid state as watching the scene.
- Save/load, checkpoint, reconnect, and replay behavior are defined where relevant.

## Audio, Subtitles, And Accessibility

- Dialogue, music, SFX, ambience, and silence are timed to the edit.
- Subtitles are available for dialogue and important non-dialogue audio where required.
- Text duration supports reading speed and localization expansion.
- Camera shake, flashes, motion, and volume spikes respect accessibility settings where relevant.

## Production

- Required animations, mocap, facial performance, VFX, props, lighting, sets, UI, and audio are listed.
- Timeline, sequence, camera, actor, and event names are clear.
- Aspect ratios, safe areas, platform capture, compression, storage, and patch-size impact are considered.
- Real-time sequences are tested on target hardware; prerendered videos are tested for decode, loading, and color/audio consistency.

## Review

- Watch before and after gameplay, not only in isolation.
- Review once with subtitles on and once with audio low or muted.
- Review at target resolution and frame rate.
- Cut any shot that does not clarify, escalate, contrast, reveal, or transition.
