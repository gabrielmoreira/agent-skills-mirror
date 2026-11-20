# Native source and useful editing boundaries

Use the pinned HyperFrames authoring guide for its actual runtime contract. Choose composition and component boundaries with the shared [editable representation](../../openmotion-production/references/reference-video.md#choose-an-editable-representation) rules. This page adds what a reusable template must record and keep working; it is not a replacement engine or mandatory project architecture.

## Group by behavior

A composition can own a coordinated scene; independent captions or graphics can remain peers. One object can contain SVG subpaths, nested geometry or code-defined children. Preserve useful identity through names, IDs, source functions or asset references. Studio selects existing native elements; code-defined subobjects remain editable in source even when they lack separate Studio controls. Explain that distinction in `TEMPLATE.md`.

In HyperFrames 0.9.7 a Canvas/WebGL host without a GSAP timeline uses `data-no-timeline`; time-driven rendering listens to the documented seek mechanism. Wall-clock playback must not make exported frames change unpredictably.

## Use assets and text appropriately

Photos, screenshots, textures, logos and extracted independent figures can remain local assets. Record their source and useful crop/mask relationship in `TEMPLATE.md`.

Text and fonts follow the shared [text and fonts](../../openmotion-production/references/reference-video.md#text-and-fonts) rules. Bundle a stable font in a portable project when the project uses it. Fonts use the existing phase-one batch asset Tool, with parsed metadata and optional license retention; arbitrary binary imports remain unsupported. Preserve its version guards. When a logo or calligraphic artwork stays an image or vector asset, document its replacement location and limitation in `TEMPLATE.md`.

## Rebuild mixed-media shots

- Identify the shots where media carries the product, subject, materials, environment or performance. For those shots, note the visible subject, framing, start and end states, action, cut, usable duration and areas reserved for graphics. Link repeated subjects and lighting across cuts. Make the shot list from the source; do not use the model to redesign the sequence. Read adjacent frames where cuts look like wipes or camera moves. If a foreground object conceals the cut, carry that occlusion through the edit, using a local foreground layer when practical so replacement media does not break the transition.
- Prefer approved clean assets that preserve the reference. Delegate a missing media role to [openmotion-media](../../openmotion-media/SKILL.md) and follow its [planning](../../openmotion-media/references/planning.md) and [inspection](../../openmotion-media/references/inspection.md) guidance. If no suitable asset source is available, continue the supported layers and record which shot needs a supplied asset or an approximation.
- Choose the least complex input that preserves the shot's function. For a static product or background, use an approved image and add controllable native animation if it reproduces the movement. For camera/subject motion, changing reflections, parallax or occlusion that a still cannot reproduce, evaluate a video model with compatible reference input, duration and framing. Prefer the clean product or first frame where supported. Keep the same approved starting appearance for repeated product shots and inspect it at the start, through the action and at the cut. Check objects that the camera reveals after the first frame; use a separate approved asset when an entering object carries product identity or masks the cut. For a difficult shot, validate a representative short segment before spending the approved batch on the remaining shots. When comparing authorized model candidates, hold the starting asset, shot brief and output target constant. Adopt the footage only if it preserves the required identity, motion and editability through the cut. Keep clean local media or native reconstruction in that role when no candidate meets it. Record model-specific observations in the test evidence.
- When the same product appears in several shots and its shape, color or branding must stay coherent, keep one reusable product source in the project (for example a layered image or a controllable 3D object) and vary the camera, pose and lighting around it. Use generation for the parts whose appearance or motion that source cannot reproduce. If footage already contains product marks that the template promises to change, require suitable clean or replacement assets; an overlay elsewhere does not make those marks editable.
- Keep the selected media as project-relative, replaceable clips or stills. Verify that each adopted file appears in the authored timeline at the intended trim, duration and layer. Keep any overlays the template promises to expose as editable native layers. Use approved product material when exact product identity is required and record any approximation.
- Preserve approved source sound when it serves the reference. Keep music, speech and sound effects independently replaceable when clean stems are available. If only a mixed track is available, identify what a future edit would affect. Align the duration and audio events of adopted sound to the reference. Record any substitute sound or omitted role.

In `TEMPLATE.md`, note the source role, relative path, crop/timing constraints and how to replace each meaningful asset. Label supplied, extracted, generated and approximated content; for generated assets keep enough provenance to identify the selected version without requiring its provider, URL, workspace or credentials to render the template.

## Make common edits discoverable

Use root variables for common content when useful, with labels the user understands. Do not require every object or decorative property to be a variable. Source edits can also change structure, layout, media and timing. The shared [edit dependencies](../../openmotion-production/references/reference-video.md#check-fidelity-and-edit-dependencies) say what each common change affects.

`TEMPLATE.md` connects observed reference objects/behaviors to their reconstruction and differences, and identifies source/asset entry points, common edits and related effects on layout/timing. Record meaningful systems, not every decorative subpath. Keep existing variable shortcuts functional or remove stale declarations; direct source editing remains available.

## Inspect actual results

Choose static frames for layout, consecutive frames for entrances or shape changes, and playback for rhythm. Native lint/timeline/info and optional diff diagnostics help locate problems. Use the native CLI in the supplied project directory for lint/timeline/info; managed preview/export perform their own lint/technical checks, with export status read through openmotion_get_project. There is no standalone public inspection Tool. CLI/shell access is a host capability, not a guarantee of MCP-only access.

If results lose texture, depth, blur or a hard cut, inspect how the reference produces that observable effect before choosing a correction. Do not prescribe fixed glow/blur values. Human review decides whether the overall result is acceptable; report technical problems and concrete remaining differences separately.
