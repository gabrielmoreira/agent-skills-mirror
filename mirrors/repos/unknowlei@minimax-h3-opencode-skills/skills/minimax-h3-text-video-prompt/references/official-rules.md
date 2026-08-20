# MiniMax H3 T2VA Rules

## Mandatory structure and language

- Always produce the official three-field prompt. Never use a free-form natural-language prompt as the final deliverable.
- Write all descriptive and instructional prose in English.
- Preserve original language only for exact dialogue, voiceover, speech, singing, lyrics, visible on-screen text, exact proper nouns, and literal identifiers.
- After the English prompt, translate the complete prompt into Chinese for comprehension, including the meaning of verbal and visible text. Keep structural tokens identifiable in the translation.

## Timeline and shots

- Start directly with the three core fields; T2VA has no picture-alignment instruction.
- Begin the first field with `[Shot 1]` and no timestamp.
- Format later cuts as `[Shot N] At MM:SS.mmm, the camera cuts to...`.
- Keep cut times strictly increasing and within the target duration.
- Use cuts only to introduce new information. Use camera movement for a modest framing or angle change.

## Camera vocabulary

- `Zoom In / Zoom Out`: change focal length while the camera body stays still.
- `Push In / Pull Out`: move the camera forward or backward.
- `Pan Left / Pan Right`: pivot the lens horizontally from a fixed camera position.
- `Truck Left / Truck Right`: translate the camera horizontally.
- `Tilt Up / Tilt Down`: pivot the lens vertically from a fixed camera position.
- `Pedestal Up / Pedestal Down`: move the whole camera vertically.
- `Arc Shot`: move around the subject on an arc.
- `Tracking Shot`: follow a moving subject.
- `Static Shot`: keep camera position and lens still.
- `POV`: show a subject's point of view.
- `Roll Clockwise / Roll Counterclockwise`: rotate around the lens axis.
- Add `with small/large amplitude` or `at slow/fast speed` only when meaningful. Omit ordinary amplitude and speed.
- Integrate camera movement into natural prose; never append a disconnected list of camera tags.

## Speech, lyrics, and visible text

- Assign `(Sx)` only to a person, character, narrator, or other actual vocal source.
- Reuse each ID across all shots. Use `(S1,S2)` when already identified speakers vocalize together.
- Put identity, delivery, and action outside `<d>`; put only `[Language]` and exact verbal content inside it.
- For voiceover, use `says in an off-screen voiceover` and immediately state that the corresponding on-screen character's lips remain completely closed.
- Use `<scenetrans>` in both connected dialogue segments when one line crosses a cut, and explicitly state continuous audio.
- Use `<cutoff>` when the video ending truncates speech.
- Put visible text in English double quotation marks and preserve its original language and punctuation.

## Sound layers

- Keep shot-synchronized dialogue, singing, diegetic music, and decisive sound events in `integrated_multimodal_description`.
- Use one continuous paragraph of roughly 1-4 sentences in `overall_soundscape` to summarize ambience, physical action sounds, and non-verbal human sounds. Use `N/A` only when the user explicitly requests complete silence.
- Use roughly 1-3 sentences in `non_diegetic_music` for audience-only score. Describe instruments, tempo/rhythm, and dynamic evolution instead of abstract emotional purpose. Use `N/A` when no such music is present.
