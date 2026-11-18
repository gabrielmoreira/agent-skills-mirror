---
name: openmotion-video-to-template
description: 使用 OpenMotion 将参考动效视频或链接重建为可反复换内容的可编辑模板，交付源码、素材、预览、编辑说明与文件夹或 ZIP。仅在用户要求可复用模板时使用；按参考制作本次成片走 openmotion-recreate，使用已有模板出片或替换内容走 openmotion-template-to-video，原创走 openmotion-director。
---

# OpenMotion Video to Template

This is the openmotion-video-to-template production entry, selected for a requested reusable template. Read [shared context](../openmotion-production/references/context.md) for the current scope and reuse available bodies without returning to the router. MCP-only clients use resources/read `openmotion://workflow/video-to-template/start` for this same file; follow supporting references only when needed. Revisions to an existing template draft use the [shared edit workflow](../openmotion-production/references/edit.md). A request to recreate a finished video without a reusable-template deliverable stays with [openmotion-recreate](../openmotion-recreate/SKILL.md).

Deliver the requested reusable template as a native HyperFrames project with local assets and an actual preview. Phase one covers Motion graphics. Preserve supplied sound when relevant; do not introduce live-action, voice, music or multimodal generation services to complete this workflow.

Closely match the reference's pictures, composition, motion and pacing while preserving editability. Reproduce texture, depth and lighting present in the reference; do not add decorative effects merely to make it look more polished.

A reference plus change requests is not a phase-one workflow of this Skill. Deliver the faithful template first and report that requested changes belong to `openmotion-template-to-video` applied to the delivered template; do not mix changes into the rebuild.

When selecting, obtaining or replacing source assets, read the [shared material policy](../openmotion-production/references/materials.md) within this workflow's supported media scope. Preserve the reference's identity and fidelity requirements; this does not authorize content substitutions or new generation services.

## Understand the requested result

Obtain and read the whole reference through the shared [reference reading and measurement](../openmotion-production/references/reference-video.md) method before choosing implementation. Preserve the link's URL and the local copy's checksum.

Preserve the reference's content, wording, brand, composition and motion as they are; do not pre-substitute them. Content replacement happens later with `openmotion-template-to-video`.

Work from start to finish without asking questions. Where the reference is ambiguous, choose the most faithful reasonable option, finish it, and record the choice and trade-off in `TEMPLATE.md`. Stop only when the work cannot proceed, such as an inaccessible link or an undecodable file; then report that specific blocker instead of asking for preferences.

## Choose an editable representation

Apply the shared [editable representation](../openmotion-production/references/reference-video.md#choose-an-editable-representation) and [text and fonts](../openmotion-production/references/reference-video.md#text-and-fonts) rules. A template's content stays editable for later replacement: keep wording, brand, images and named objects easy to locate, declare common edits as root variables, and make distinctive lettering settable for new words. Record font substitutions and other approximations in `TEMPLATE.md`.

## Make and check the work

Read the pinned native authoring guide and [runtime adapter](../openmotion-production/references/production.md). For a portable folder, create a separate working directory and use the pinned native CLI; this requires host filesystem/shell capabilities. For a managed project, reuse its projectId or create a carrier with `openmotion_create_project`: use projectType=reference_video with an actual HTTP(S) referenceUrl or known referenceVideoId; for a local video use projectType=natural_language and record the local reference/checksum in requirements. Include requestId, title and requirements. Creation records the source but does not analyze or recreate the video. Read sources/current versions with `openmotion_get_project`, import supported image/audio/video files with `openmotion_import_assets`, and save native text through `openmotion_edit_project` with projectId, requestId, expectedRevision and expectedVersionId. Read the new version after imports or GUI changes. Do not assume a catalog ID exists, write reserved metadata, or bypass managed-project version protection with direct filesystem writes.

Read the guide via resources/read `openmotion://engine/SKILL.md`; managed project details return authoringGuide/hyperframesCli paths. Do not call `openmotion_open_preview` just to obtain paths: it runs lint and selects an existing project in Studio. Initial template packaging can run in the background; follow-up content edits apply the shared [continuing-edit preview rules](../openmotion-production/references/native.md#continuing-edits), with explicit background requests taking precedence. The public Tools do not download/analyze video, compare videos or package ZIPs. Use available host capabilities for those steps, and report a concrete capability gap instead of inventing a Tool or claiming a portable package was delivered.

Use the shared [measurements](../openmotion-production/references/reference-video.md#measure-specific-questions) for questions that need exact timing, dimensions or layout, and [record them](references/measure.md) in `TEMPLATE.md`. Use [rebuild guidance](references/rebuild.md) for grouping, media and edit dependencies. For an unfamiliar or difficult visual system, a short representative segment can establish a useful approach before expanding the film; this is advice, not a mandatory extra stage.

Compare actual frames with the reference while developing, and apply the shared [fidelity checks](../openmotion-production/references/reference-video.md#check-fidelity-and-edit-dependencies): bounded repair, hard cuts and edit dependencies. Record an issue that bounded repair does not resolve in `TEMPLATE.md` and move on.

Finish with [technical checks and packaging](references/verify.md) and the [portable project contract](../openmotion-production/references/portable-project.md). Deliver the complete folder/ZIP, preview and cover, with one `TEMPLATE.md` inside. Do not require registration, a template ID or a custom content schema. Keep the reply short and in the user's words: absolute-path links to the preview, the template and the original-versus-template comparison; what can be changed; and where it still differs from the original. Technical check results stay in `TEMPLATE.md`; mention one in the reply only when it affects the user, such as a silent tail or a substituted font. Humans decide visual acceptance. Do not reject or repeatedly rework a deliverable solely because of a similarity score or your own taste.

Keep two checks separate: reference-to-rebuild uses diagnostics and human visual judgment; the package check confirms the unpacked ZIP renders elsewhere without missing files or creator-machine paths, with the frame rate, frame count and duration of `preview.mp4`. It is not a pixel comparison; do not spend repair rounds on invisible differences.

[Guidance sources](references/rule-sources.md) separates reviewed material, observed evidence and advice. Do not treat one sample or another product's documentation as a universal effect guarantee.
