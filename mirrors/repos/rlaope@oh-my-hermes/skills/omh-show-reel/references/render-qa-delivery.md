# Render, revision, export QA and delivery

## Observable review ladder

Tools: `render.mjs --stills`/`--every` for style frames, `contact_sheet.py` for
`--every`, `--times` and `--around` cut strips, `motion_check.py` for unintended
freezes and flashes, `finish.py` for master/share/poster/SRT. The critique method,
technical checklist, how to read a sheet and the delivery report form are in
`references/craft-qa.md`.

Render actual style frames at representative script/scene states, then a moving
draft, a contact sheet and consecutive transition strips. Inspect at intended
delivery-size (including actual mobile/chat thumbnail scale when applicable),
not only full-resolution screenshots. Read essential text and brand names there;
reduce copy or simplify hierarchy before shrinking type. No tiny crowded labels.
A contact sheet checks composition/order, never pacing, flicker or audio sync.

For each segment record keep/fix/rebuild, evidence refs, reason, owner and cost;
identify the weakest scene and spend the declared revision budget there first.
After edits re-render the affected segment plus both cut boundaries, then review
the final encoded output. Stop at the time/iteration cap and report residual
defects; approval of an older draft does not certify the new export.

## Measured export: show_reel_export_manifest/v1

List actual master/share/GIF/poster/subtitle variants requested, file hashes,
bytes/filesize cap, duration, dimensions, fps/timebase, codec/profile/container,
pixel format, color range/primaries/transfer/matrix, audio presence and provenance.
Probe final encoded files and fully decode them; do not infer success from a preset
or path existence. Color metadata is not color correctness: inspect gradients,
black levels and brand colors after decode, and record source/conversion intent.
With audio measure integrated loudness, true peak and A/V sync; STT only when
speech exists. No observed listening means listening not_observed even if metrics
pass. No audio means checks not_applicable with reason, not fabricated zeros.

## QA record: show_reel_qa_report/v1

Give each check PASS/REVISE/HOLD plus artifact hash, frame/time refs, method and
limits. Inspect:

- factual claims, source revision, brand/logo identity, rights and concept labels;
- actual delivery-size text readability, safe areas, contrast, clipping and hierarchy;
- native script line breaks, glyphs/fallback, weights, mixed-script baseline,
  Arabic shaping/bidi isolation of numbers/URLs/commands, subtitle reading time;
- cut ordering, transition continuity, motion intent, unintentional freeze/flicker,
  flash suspicion and loops; distinguish an intentional hold from a stuck render;
- codec/color/filesize/channel cap and full decode; audio sync, pronunciation and
  listening only when observed. Automated flash metrics are not safety certification.

Any critical defect or unobserved required check prevents overall PASS. Missing
renderer/font/voice is HOLD; pageerror, timeout or partial export is failed/partial.
Keep incomplete frame counts, wrong dimensions, corrupt files and cancellation
cleanup visible; never relabel them successful. Re-encode oversized or unsupported
files and rerun final-file checks. Explicitly name which locale samples were
rendered and which remain contract-only; do not claim five-language fluency or
font/TTS/render support from fixtures.

## Delivery: show_reel_delivery_manifest/v1

Separate generated, attached, received and published states with exact file
hashes and target receipts. A local path is generated, not delivered. Attachment
failure remains failed with a safe retry/alternative; external upload, spend or
publication needs separate exact-target user approval and readback. Never infer
recipient receipt from an upload attempt. Include selected master/share/poster,
subtitles and source package as requested, rights/gaps and a regeneration recipe.
If a video was requested, a storyboard alone is not completion. Report the useful
prepared work and HOLD with the exact capability/evidence still missing.
