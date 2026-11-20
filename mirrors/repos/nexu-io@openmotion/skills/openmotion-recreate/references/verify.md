# Export and requested review

## 1. Default delivery

Use one focused preview pass before the first export. Select up to four corresponding moments from the source observations already gathered, covering a clear composition, a defining movement or interaction, the most demanding transition and the ending as applicable. Reuse current native preview captures and group them into one view. Aim to complete this comparison in about a minute.

Check requested content, recognizable geometry, crop/occlusion, event phase and conspicuous missing or excessive light. Judge a shot produced as generated media by the match standard in [Role and goal](../SKILL.md#role-and-goal), not by pixel or identity match; native text, logos and UI above it get the same checks as everywhere else. When the recreated film requires captions (and does not carry those lines solely as synchronized on-screen display typography), verify with `caption_tracks` that a populated editable native caption track exists (`kind: "caption"` and `cueCount > 0`), confirm speech sync from audio timing evidence or audible preview playback, and check clearance from focal UI, display titles and CTA through preview or rendered frames. Correct clear omissions, wrong wording, broken assets, clipping, misplaced objects or a substantially wrong transition in one source batch. Inspect only the affected moment once after that correction. Preserve the reference's story, motion and appearance while accepting small residual differences in texture, random trajectories or microtiming within this bounded pass. State any material remaining difference at handoff.

When preview capture is unavailable, report that limitation and proceed through the available technical delivery path. Detailed review follows the requested scope in §§2–3.

After implementing the requested film, complete the [editable preview handoff](../../openmotion-production/references/native.md#editable-preview-handoff). Read `openmotion_get_project({projectId,workId})` for the current revision and version, retaining this turn's workId from the shared production workflow. Request `openmotion_export_request({projectId,workId,requestId,versionId,expectedRevision,audio})` with `audio: "required"`, or `"silent"` for a silent reference or requested silent film. Reuse an applicable export job before submitting another. Poll `openmotion_get_project({projectId,workId,exportJobId})` to completion or failure.

Use the completed job's automatic technical verification for that exact file. Recover render, missing-asset or technical verification failures from the reported cause and retry the affected operation. Once technical verification passes, complete the [shared final-video delivery](../../openmotion-production/references/production.md#final-video-delivery) for the same editor version and workId, presenting the final chat video once. Choose the viewing route through that shared contract; additional downloadable files follow the requested scope or its timeout fallback. State known limitations and any unconfirmed editor display truthfully.

Default creation finishes here. Numeric comparisons, full playback-review sessions, review documents and further visual repair/re-export cycles follow an explicitly requested review, evaluation or revision. The technical receipt establishes export integrity. Describe visual fidelity according to the evidence actually available.

## 2. Measure the selected checkpoints

Use this section for an explicit review, evaluation or visual revision request. Choose checkpoints that answer the requested question, using existing reference observations. A read-only review or evaluation records findings for the inspected version. An authorized revision can use those findings to change source.

```sh
node <skill directory>/scripts/measure_frame.mjs reference.mp4 output.mp4 --t <output seconds> --ref-t <reference seconds> [--region x,y,w,h --ref-region x,y,w,h]
```

For brief events, use zero-based decoded indices with `--frame <output index> --ref-frame <source index>`. A preview PNG uses `--frame 0` with its actual source time or `--ref-frame`. Keep resolution, capture time and source revision explicit. The helper needs Node and ffmpeg/ffprobe from the shared [runtime paths](../../openmotion-production/references/reference-video.md#locate-the-pinned-cli-and-media-tools). Batch independent measurements when useful.

For shots produced as generated media, whole-frame brightness, detail and accent values are diagnostic, not pass/fail gates or reasons to regenerate; keep the numeric checks for native text, logos, UI and other regions meant to match the reference.

Whole-frame output reports brightness, detail and colour coverage. Region output also reports content bounds and size. Investigate failed or blocked `region_status`, `height_ratio` below 0.8, unintended clipping, or false `brightness_ok`, `detail_ok` or `accent_ok` values. Check region selection and requested content adaptations when interpreting them. Record unresolved findings with their observed cause and scope.

## 3. Requested visual review or revision

Apply [shared review](../../openmotion-production/references/review.md) and the [shared verification guidance](../../openmotion-production/references/verification.md) to the requested scope. Compare actual output with corresponding reference moments. Cover requested content, shapes, layout, internal movement, joins, brief events and coupled interactions where relevant. Existing region/unit notes and the [local diagnosis guidance](reconstruction.md#validate-and-repair-the-local-implementation) help connect a visible discrepancy to its source control.

For a revision request, collect independent findings into one source repair batch. Reinspect affected intervals, neighboring joins and dependent appearances. Use the shared [bounded repair guidance](../../openmotion-production/references/reference-video.md#check-fidelity-and-edit-dependencies) when an issue stops improving, and keep its record in the working notes. Export the resulting version through §1 when a rendered delivery is requested. Bind any retained review result to the version actually inspected, and record remaining differences honestly. A dedicated evaluation reports results without adding a visual revision cycle unless the user requests it.
