# MiniMax H3 Keyframe Rules

## Eligibility gate

Use these base keyframe rules only when the user explicitly declares each relevant image as a literal first frame, last frame, or first-and-last-frame pair and none of those images also supplies reusable identity, character, person, object, costume, scene, style, action, camera, composition, voice, or other reference traits. If either condition is absent or uncertain, use the full-reference skill and encode any frame role through a `<Picture N>` prompt-level anchor.

## Mandatory structure and language

- Always produce the exact alignment instruction for the selected mode followed by the official three core fields. Never use a free-form natural-language prompt as the final deliverable.
- Write descriptive and instructional prose in English.
- Preserve original wording only for exact dialogue, speech, singing, lyrics, visible text, proper nouns, and literal identifiers.
- Translate the entire finished prompt into Chinese after the English prompt, including verbal and visible text meanings, while keeping structural identifiers recognizable.

## Exact alignment instructions

### I2VA

```text
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.
```

`<Picture 1>` is the actual first frame at 0.00 seconds and belongs to `[Shot 1]`.

### FL2VA

```text
How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot N) aligns with the S.SS-second mark of the target video.
```

Replace `N` with the actual final-shot number and `S.SS` with the effective duration formatted to exactly two decimal places. Picture 1 is the opening frame and Picture 2 is the ending frame.

### L2VA

```text
How the reference pictures align with the target video — <Picture 1> (from [Shot N]) aligns with the S.SS-second mark of the target video.
```

Replace `N` with the actual final-shot number and `S.SS` with the duration formatted to exactly two decimal places. `<Picture 1>` belongs to the final shot, not inherently to Shot 1.

## Shared base rules

- Start `[Shot 1]` with style and initial composition; do not timestamp it.
- Format later cuts as `[Shot N] At MM:SS.mmm, ...` with strictly increasing times inside the duration.
- Prefer camera movement over a cut for modest angle or distance changes.
- Use mechanically correct camera terms: Zoom versus Push, Pan versus Truck, Tilt versus Pedestal.
- Assign stable `(Sx)` IDs only to actual vocal sources.
- Put exact dialogue or lyrics inside `<d>[Language] ...</d>`.
- Preserve visible text in English double quotation marks without translation.
- Put synchronized dialogue, singing, diegetic music, and decisive sound events in the main timeline.
- Summarize ambience, physical action sounds, and non-verbal human sounds in `overall_soundscape`.
- Describe audience-only music by instrumentation, tempo/rhythm, and dynamics in `non_diegetic_music`.

## API boundary

The current MiniMax H3 API treats keyframe generation and multimodal reference generation as mutually exclusive input combinations. A request containing any `reference_image`, `reference_video`, or `reference_audio` role cannot also contain `first_frame` or `last_frame` roles. Use the full-reference prompt skill when references and semantic picture anchoring must be combined.
