# Rebuild the reference

This page carries openmotion-recreate's rebuilding decisions. Reading the reference, measuring it, choosing an editable representation and checking fidelity follow the shared [reference reading and measurement](../../openmotion-production/references/reference-video.md) method. The host Agent writes native source and saves it through the project Tools. During default creation, use reference observations to plan and implement the complete film, then follow [export and requested review](verify.md). Default creation uses the single focused preview pass defined in delivery. Detailed unit validation and further visual repair apply to explicitly requested review or revision. Source analysis and material preparation belong to authoring.

## Read the whole reference

[Obtain](../../openmotion-production/references/reference-video.md#obtain-the-reference) and [read the whole reference](../../openmotion-production/references/reference-video.md#read-the-whole-reference) before choosing an implementation. This route has no separate analysis stage: the observations feed authoring directly. Keep source observations, unverified intervals and their reasons in the project's existing working notes.

## Measure with the pinned CLI

Run the [shared measurements](../../openmotion-production/references/reference-video.md#measure-specific-questions) with the `hyperframesCli` path from `openmotion_get_project` for the recreation project. Media tools and this Skill's own helpers locate Node and FFmpeg through the [shared runtime paths](../../openmotion-production/references/reference-video.md#locate-the-pinned-cli-and-media-tools). Import extracted photos, screenshots and logos with `openmotion_import_assets`.

## Choose an editable representation

Apply the shared [editable representation](../../openmotion-production/references/reference-video.md#choose-an-editable-representation) rules and build the user's requested version directly in it. Keep observations with the responsible source controls in existing implementation notes, and fit the complete mechanism from this evidence in the first implementation.

## Establish a difficult visual system

Dense multi-shot work, unfamiliar visual mechanisms and movement under requested revision that still differs after a repair follow [difficult visual reconstruction](reconstruction.md). Read it before authoring those passages. It covers [Plan shot and action units](reconstruction.md#plan-shot-and-action-units), [Turn observations into driving data](reconstruction.md#turn-observations-into-driving-data), [Prepare material in its actual use states](reconstruction.md#prepare-material-in-its-actual-use-states), [Validate and repair the local implementation](reconstruction.md#validate-and-repair-the-local-implementation) and [Integrate the units](reconstruction.md#integrate-the-units).

## Assets, text and fonts in this package

- Images, footage and sound go through `openmotion_import_assets` (PNG, JPEG, WebP, GIF, MP4, WebM, WAV, MP3, OGG, FLAC, AAC, M4A). Import does not place media on the timeline; reference the returned path.
- SVG logos and vector artwork are text: save them with `openmotion_edit_project`.
- Fonts follow the shared [text and fonts](../../openmotion-production/references/reference-video.md#text-and-fonts) rules. Import a permitted font through `openmotion_import_assets`, retain its license and use the returned actual metadata and relative @font-face CSS. Record any substitution in the working notes.

## Rebuild and compare while working

Hard-cut verification and edit dependencies from the shared [fidelity checks](../../openmotion-production/references/reference-video.md#check-fidelity-and-edit-dependencies) apply during default creation. Comparison during default creation stays within the single focused preview pass in [delivery](verify.md#1-default-delivery).

An explicitly requested visual revision follows [requested review or revision](verify.md#3-requested-visual-review-or-revision).
