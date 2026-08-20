# MiniMax H3 Full-Reference Rules

## Default image routing

Use full-reference for every image-based request unless the user explicitly declares pure first/last boundary images and no image also supplies reusable reference traits. An ambiguous image role, ordinary "animate this image" request, or image that establishes a person, character, object, costume, scene, style, action, camera, or composition stays in full-reference. A picture may simultaneously preserve those traits and serve as a prompt-level first/key/last-frame anchor.

## Mandatory structure and language

- Always produce the official six sections in order. Never use a free-form natural-language prompt or the base three-field structure as the final full-reference deliverable.
- Write all definitions, analyses, descriptions, camera instructions, and sound instructions in English.
- Preserve source wording only for exact dialogue, voiceover, speech, singing, lyrics, visible text, proper nouns, and literal identifiers.
- After the English prompt, translate every section and every verbal or visible element into Chinese for comprehension while keeping structural identifiers recognizable.

## Label ontology

### `<Subject N>`

Use for reusable visible content: people, animals, objects, environments, clothing, props, interfaces, effects, styles, actions, expressions, or poses. One subject may combine contributions from multiple assets. A source video's visible person or action is still a subject, not a video label.

### `<Picture N>`

Use as a standalone label only when the image itself is a concrete first frame, keyframe, last frame, edited keyframe, composition anchor, or storyboard/planning reference. If an image only defines a subject's appearance, cite it inside the subject definition instead of creating a separate picture entry.

### `<Video N>`

Use for a whole-video relationship: direct editing source, continuation source, or source of camera, cuts, pacing, or temporal structure. Do not use it as a substitute for subjects extracted from the video.

### `<Audio N>`

Use for a copied or referenced audio signal: complete or partial reuse, voice timbre, music style, dialogue or lyric content, sound texture, beat, rhythm, or continuity. A reference video does not automatically create an audio label merely because it contains sound.

Number each category independently and keep meanings stable across all sections.

## Task types

- `keyframe completion`: an image is a concrete first, key, edited, or last frame anchor.
- `reference generation`: an asset guides identity, scene, style, action, camera, storyboard, sound, or other generation characteristics without being directly edited or continued.
- `video editing`: directly modify an existing source video.
- `video continuation`: continue, extend, resume, or transition from an existing source video.
- `audio reuse`: copy the same audio signal in full or part.
- `audio reference`: reference timbre, style, words, texture, beat, or continuity without directly copying the signal.

Combine applicable types inside one square-bracketed prefix separated by ` + ` and without duplicates. For direct video editing, begin the summary after the prefix with `The target video is an edited version of <Video 1>.`

## Retention markers

Use only these visual markers:

- `fully_preserved`: preserve the complete defined role.
- `partially_preserved`: retain the content but alter or omit some defined characteristics.
- `attribute_transfer`: move referenced characteristics to a different identifiable target subject.
- `weak_reference`: retain only broad style, category, composition, or atmosphere.

Use only these audio markers:

- `fully_copy`: the complete source audio becomes the complete final audio track.
- `partially_copy`: copy only part of the timeline/layers or modify copied layers.
- `reference`: do not copy the signal; reference timbre, rhythm, style, words, or texture.
- `weak_reference`: retain only broad audio category or atmosphere.

Do not count new target actions, backgrounds, or plot events as reference-fidelity losses unless they alter a defined reference role.

## Timeline and speakers

- Establish style in one or two English sentences before `[Shot 1]`.
- Do not timestamp `[Shot 1]`. Format later cuts as `[Shot N] At MM:SS.mmm, ...`.
- At a subject's first clear appearance, describe its referenced characteristics, frame position, and current action.
- Phrase anchors naturally: `the shot begins from <Picture 1>`, `the shot's keyframe corresponds to <Picture 2>`, or `the shot ends on <Picture 3>`.
- Use `<Subject N> (Sx)` when a referenced subject physically speaks. Keep the same `(Sx)` for off-screen speech by that source.
- Use `<Audio N>` rather than inventing `(Sx)` when verbal content is only a cue embedded in a directly reused complete soundtrack or BGM.
- Keep exact reused or explicitly reperformed words inside `<d>[Language] ...</d>`. Use `[unclear]` rather than guessing.
- Use `<scenetrans>` for dialogue crossing a cut and `<cutoff>` for speech truncated by the video ending.

## Sound sections

- Keep synchronized dialogue, singing, and decisive sound events in `detailed_description`.
- Summarize ambience and physical sounds in `overall_soundscape`; cite copied or referenced audio there when it supplies those layers.
- Describe audience-only score in `non_diegetic_music`; cite copied or referenced audio there when it supplies that layer.
- Do not repeat complete dialogue or lyrics in the two summary sound sections.

## API role constraint

The current official API documents keyframe and multimodal-reference inputs as mutually exclusive. If any `reference_image`, `reference_video`, or `reference_audio` role appears in `content[]`, do not also use `first_frame` or `last_frame`, and vice versa. To combine reference generation with a first/last-frame intention, keep the asset's API role as `reference_image` and encode its concrete frame function through `<Picture N>` and the prompt. This is a semantic prompt anchor, not the API's hard keyframe role.
