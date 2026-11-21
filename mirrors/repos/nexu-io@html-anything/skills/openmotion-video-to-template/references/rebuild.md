# Native source and useful editing boundaries

Use the pinned HyperFrames authoring guide for its actual runtime contract. Choose composition and component boundaries with the shared [editable representation](../../openmotion-production/references/reference-video.md#choose-an-editable-representation) rules. This page adds what a reusable template must record and keep working; it is not a replacement engine or mandatory project architecture.

## Group by behavior

A composition can own a coordinated scene; independent captions or graphics can remain peers. One object can contain SVG subpaths, nested geometry or code-defined children. Preserve useful identity through names, IDs, source functions or asset references. Studio selects existing native elements; code-defined subobjects remain editable in source even when they lack separate Studio controls. Explain that distinction in `TEMPLATE.md`.

In HyperFrames 0.9.7 a Canvas/WebGL host without a GSAP timeline uses `data-no-timeline`; time-driven rendering listens to the documented seek mechanism. Wall-clock playback must not make exported frames change unpredictably.

## Use assets and text appropriately

Photos, screenshots, textures, logos and extracted independent figures can remain local assets. Record their source and useful crop/mask relationship in `TEMPLATE.md`.

Text and fonts follow the shared [text and fonts](../../openmotion-production/references/reference-video.md#text-and-fonts) rules. Bundle a stable font in a portable project when the project uses it. Fonts use the existing phase-one batch asset Tool, with parsed metadata and optional license retention; arbitrary binary imports remain unsupported. Preserve its version guards. When a logo or calligraphic artwork stays an image or vector asset, document its replacement location and limitation in `TEMPLATE.md`.

## Rebuild mixed-media shots

- Identify the shots where media carries the product, subject, materials, environment or performance. Note visible subject, framing, start/end states, action, cut, usable duration and graphic-safe areas from the source; do not redesign the sequence. Read adjacent frames where cuts look like wipes or camera moves, and keep foreground cut-masking objects on a local foreground layer when practical so later media swaps preserve the transition.
- Apply the shared [generation timing ladder](../../openmotion-production/references/materials.md#generation-timing-ladder), [cross-shot consistency](../../openmotion-production/references/materials.md#cross-shot-consistency) and [mixed-media recreation boundaries](../../openmotion-production/references/materials.md#mixed-media-recreation-boundaries). Prefer approved clean assets that preserve the reference; delegate missing media roles through [openmotion-media](../../openmotion-media/SKILL.md). If no suitable source is available, finish the supported layers and record in `TEMPLATE.md` which slot needs a supplied asset or approximation.
- For reusable templates, keep every repeated product or hero subject tied to one reusable project source (layered still, clean cut-out or controllable 3D/anchor asset) whenever later users are expected to swap it across shots. If footage already carries product marks the template promises to make editable, require a clean or replacement asset rather than hiding marks with an unrelated overlay. Check objects revealed after the first frame and keep entering identity/mask objects as separate replaceable assets.
- For a difficult shot, validate one representative short segment before spending the approved batch on the remaining shots; when comparing authorized model candidates, hold starting asset, shot brief and output target constant, and adopt only footage that preserves identity, motion and editability through the cut.
- Keep selected media as project-relative, replaceable clips or stills at their intended trim, duration and layer, with promised text/UI/brand overlays kept native. Preserve approved source sound with independent stems when available; if only a mixed track exists, note in `TEMPLATE.md` what later edits would affect.

In `TEMPLATE.md`, note the source role, relative path, crop/timing constraints and how to replace each meaningful asset. Label supplied, extracted, generated and approximated content; for generated assets keep enough provenance to identify the selected version without requiring its provider, URL, workspace or credentials to render the template.

## Make common edits discoverable

Use root variables for common content when useful, with labels the user understands. Do not require every object or decorative property to be a variable. Source edits can also change structure, layout, media and timing. The shared [edit dependencies](../../openmotion-production/references/reference-video.md#check-fidelity-and-edit-dependencies) say what each common change affects.

`TEMPLATE.md` connects observed reference objects/behaviors to their reconstruction and differences, and identifies source/asset entry points, common edits and related effects on layout/timing. Record meaningful systems, not every decorative subpath. Keep existing variable shortcuts functional or remove stale declarations; direct source editing remains available.

## Inspect actual results

Choose static frames for layout, consecutive frames for entrances or shape changes, and playback for rhythm. Native lint/timeline/info and optional diff diagnostics help locate problems. Use the native CLI in the supplied project directory for lint/timeline/info; managed preview/export perform their own lint/technical checks, with export status read through openmotion_get_project. There is no standalone public inspection Tool. CLI/shell access is a host capability, not a guarantee of MCP-only access.

If results lose texture, depth, blur or a hard cut, inspect how the reference produces that observable effect before choosing a correction. Do not prescribe fixed glow/blur values. Human review decides whether the overall result is acceptable; report technical problems and concrete remaining differences separately.
