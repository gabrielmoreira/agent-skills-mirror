# Workflow templates

Starting shapes only. Copy one per asset with
`tongflow_workflow_new({ path: '<OWNER>_<PASS>', fromTemplate: '<name>' })`, then patch the
concrete prompt / `tf://` refs into its nodes. Plugins are filled with the installed default
for each slot when copied. Multi-step templates: delete the steps a given asset does not need.

- `character-sheet` — text → reference image (REF).
- `location-plate` — text → establishing plate (REF).
- `storyboard-panel` — prompt → storyboard panel (SB). Inputs: prompt.
- `shot-keyframe` — reference images + prompt → keyframe (KF) via image fusion. Inputs: refs, prompt.
- `shot-keyframe-hd` — image fusion → upscale (KF). Inputs: refs, prompt.
- `dub-line` — voice reference + line → dialogue audio (DLG). Inputs: voice, text.
- `voice-preset` — line → preset-voice speech (VO / DLG). Inputs: text.
- `shot-i2v` — keyframe + motion prompt → animation (ANI). Inputs: image, prompt.
- `shot-i2v-lipsync` — image-to-video → lip-sync with the dialogue audio (ANI). Inputs: image, prompt, audio.
- `episode-music` — mood prompt → music (MUS). Inputs: prompt.
- `assemble-episode` — concatenate the circled ANI takes, then merge the music (CUT). Inputs: clips ← tf://EP01/ANI, music ← tf://EP01/MUS.

After a shot's parts exist, `tongflow_workflow_compose({ owner })` (or the button on the shot in the Studio)
joins them into `<SHOT>_ALL.tongflow.json` for review and one-shot re-runs; the same works for an episode.
