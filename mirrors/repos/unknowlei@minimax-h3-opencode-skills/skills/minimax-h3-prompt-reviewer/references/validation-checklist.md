# MiniMax H3 Prompt Validation Checklist

## 1. Mode and top-level structure

- A final prompt is never left as free-form natural language, a keyword list, a partial schema, or a mixture of schemas.
- Base keyframe mode is eligible only when the user explicitly declares literal first/last boundary roles and the images have no reusable identity, character, person, object, costume, scene, style, action, camera, composition, voice, or other reference responsibility.
- Every other image-based or ambiguous-image request defaults to full-reference, which may express first/key/last-frame semantics through `<Picture N>`.
- T2VA: no alignment line; use the three core fields.
- I2VA: first-frame alignment line; use the three core fields.
- FL2VA: first-and-last alignment line with 0.00 and exact `S.SS`; use the three core fields.
- L2VA: last-frame alignment line with actual final-shot number and exact `S.SS`; use the three core fields.
- Full-reference: use six ordered sections: `subject_definitions`, `summary`, `retention_analysis`, `detailed_description`, `overall_soundscape`, `non_diegetic_music`.

## 2. Timeline

- `[Shot 1]` has no timestamp.
- Later cut times use `MM:SS.mmm`, strictly increase, and remain inside the duration.
- Every cut adds meaningful subject, spatial, state, viewpoint, or time information.
- Every action has an understandable initial state, progression, and result.
- Action and cut density fit the requested duration.
- A first frame develops forward; an FL2VA path continuously narrows the difference to the last frame; an L2VA path starts earlier and converges at the endpoint.

## 3. Camera and composition

- `Zoom` changes focal length; `Push/Pull` moves the camera.
- `Pan` pivots horizontally; `Truck` translates horizontally.
- `Tilt` pivots vertically; `Pedestal` moves vertically.
- Camera movements do not conflict within the same instant.
- Movement, amplitude, and speed are expressed naturally and only with necessary specificity.
- Each shot establishes current framing, subject position, environment, and lighting before or alongside state changes.

## 4. Speech and text

- Only real vocal sources receive `(Sx)` IDs; IDs remain stable across shots.
- Identity, delivery, and action stay outside `<d>`; only `[Language]` and verbal content stay inside.
- User-provided words and punctuation remain exact in base prompts.
- Reused/reperformed reference words remain exact; `[unclear]` replaces unintelligible spans.
- Voiceover uses `says in an off-screen voiceover` and prevents on-screen lip movement.
- `<scenetrans>` marks both parts of speech crossing a cut; `<cutoff>` marks end truncation.
- Visible text uses English double quotation marks and retains its original language.

## 5. Sound

- Synchronized dialogue, singing, diegetic music, and decisive events appear in the main timeline.
- `overall_soundscape` summarizes ambience, physical action sounds, and non-verbal human sounds without repeating dialogue or singing.
- `non_diegetic_music` describes audience-only instrumentation, tempo/rhythm, and dynamics rather than abstract emotional function.
- Audio copy and audio reference are not conflated.

## 6. Full-reference labels

- `<Subject N>` is reusable visible content.
- `<Picture N>` is a concrete frame/composition/storyboard anchor, not every source image.
- `<Video N>` is a whole-video source or temporal structure, not every visible element extracted from it.
- `<Audio N>` is an intentionally copied or referenced audio signal, not automatic sound from every reference video.
- Each label is defined once, numbered independently by category, used consistently, and included in retention analysis.
- Task types match actual asset roles.
- Visual markers use only `fully_preserved`, `partially_preserved`, `attribute_transfer`, or `weak_reference`.
- Audio markers use only `fully_copy`, `partially_copy`, `reference`, or `weak_reference`.

## 7. Keyframes inside full-reference prompts

- A standalone `<Picture N>` explicitly states whether it is a first frame, keyframe, edited keyframe, last frame, composition anchor, or storyboard reference.
- `summary` includes `keyframe completion` when a concrete frame anchor exists.
- The timeline states how the shot begins from, passes through, or ends on the picture.
- API advice does not mix `first_frame`/`last_frame` roles with `reference_image`/`reference_video`/`reference_audio`. Mixed-reference requests express the anchor semantically in the prompt while passing the image as `reference_image`.

## 8. Bilingual output

- The English prompt is the only code block and contains no commentary.
- The Chinese translation is outside code blocks.
- All descriptive and instructional prose in the English prompt is English; only exact dialogue/speech/song/lyrics, visible text, proper nouns, and literal identifiers may remain in their source language.
- The translation covers every field, section, instruction, dialogue/lyric meaning, visible-text meaning, task type, and retention relationship.
- Structural fields, labels, timestamps, IDs, and tags remain recognizable alongside their Chinese explanations.
- The translation explains the same prompt rather than introducing new creative content.

## 9. Interactive direction

- Use a structured-choice tool whenever the brief is sparse, two or more major creative axes are missing, the user supplies only a generic image-motion request, genuine ambiguity remains, or creative control is delegated to the AI.
- In OpenCode, use the built-in `question` tool rather than printing Markdown choices.
- Ask as many related questions as the current stage requires, normally 1-5; three is not a per-call, per-turn, or per-session ceiling. For sparse or delegated briefs, normally ask 3-5 high-impact questions in one batch. A strict yes/no question may have two options; every other choice question must provide at least five materially different, feasible options. Before calling `question`, count the options in the actual payload and do not submit a non-binary choice with fewer than five; expand it or make it open-ended.
- Put the recommended option first with `(Recommended)`, explain every option, omit `Other`, and allow multiple selection only when choices can combine.
- Do not interrupt for minor details or defects with one objectively correct repair.
- Do not treat "improvise," "freely create," or "you decide" as permission to skip questions. Skip only when the user explicitly prohibits questions.
- After the user establishes the broad direction, infer the remaining details and complete the prompt without repetitive questioning.
