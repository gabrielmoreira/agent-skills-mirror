---
name: project-header-artwork
description: "Create, prompt, inspect, resize, and safely wire project header, banner, or hero artwork with provider-neutral capability discovery and honest Generated, PromptOnly, Blocked, or Unchanged results. Use for repository or documentation banners, including exact text overlays, alt text, crop-safe composition, stale-artwork review, and prompt-only fallback when no approved generator is available."
---

# Project Header Artwork

Create optional project header artwork without assuming an image provider, model,
cloud account, renderer, or repository host. A prompt, placeholder, URL, or
uninspected download is not generated artwork.

This workflow is for landscape banners and hero images. Do not import square-icon,
small-size legibility, SVG-master, favicon, or package-asset conventions from the
`icon-assets` skill. Preserve photographic or illustrated raster sources in their
native format.

## 1. Discover capabilities before promising output

Inventory only capabilities actually available and approved in the current
environment:

| Capability | Establish before use |
|---|---|
| Generation | Approved destination, supported input/output contract, dimensions, cost authorization, and a documented way to retrieve the result |
| Retrieval | Allowed host and redirect policy, maximum response size, and a destination inside the project |
| Inspection | A decoder/viewer that reads local bytes and exposes actual format and dimensions; visual review must also be possible |
| Processing | Crop/resize and encode support for the required final format without stretching |
| Text rendering | A renderer and installed font that can place exact supplied text independently of generation |

Do not install packages, provision paid services, obtain credentials, weaken
permissions, or invent an API/tool. A documentation-only session remains useful:
it can produce a **PromptOnly** result without proposal-specific automation.

Network retrieval and local inspection have different trust boundaries. Sending a
brief to, or downloading a URL from, a provider requires approval and must not
expose sensitive data or follow an untrusted destination. Inspecting an already
local file does not transmit project data, but the file is still untrusted input:
decode it with the available image inspector and enforce reasonable size limits.

## 2. Establish the asset contract

Inspect the current project description, README, destination directory, existing
artwork, prompt, alt text, and Markdown references. Reject destinations that are
absolute/device paths, escape the project through `..`, or traverse a reparse
point outside it.

Use dimensions supplied by the user or target. If none are required, propose
1600 x 900 landscape with a central subject and generous crop-safe margins; label
this a design default, not a portal requirement. Record:

- requested width, height, final format, and crop/aspect behavior;
- the crop-safe region and any reserved title area;
- source and final artifact basenames;
- whether replacement of each existing authored file is explicitly approved.

Never overwrite approved artwork, prompts, or alt text merely because the workflow
was repeated. Without explicit replacement permission, return **Unchanged** or use
a user-approved new basename.

## 3. Create and approve a minimal visual brief

Ask the user to approve a brief containing only:

- one-sentence project purpose and intended benefit;
- one visual metaphor, subject, composition, palette, and mood;
- requested dimensions, crop-safe area, and optional title reservation;
- exclusions: generated lettering, invented logos or product UI, personal
  likenesses, confidential identifiers, internal URLs, and unsupported claims.

Prefer conceptual artwork rather than a screenshot. Do not send repository files,
transcripts, secrets, personal data, or real private project details to a provider.
Save the approved prompt locally before generation, for example
`assets/header.prompt.txt`.

Fictional example:

```text
Project: Lantern, an offline reading-list organizer.
Visual: a paper lantern illuminating a small stack of unlabeled cards.
Composition: 1600 x 900, subject in the center 60%, calm navy and amber palette,
clear negative space at upper left, important details safe within a 120 px inset.
Exclude lettering, logos, people, screenshots, controls, and claims that features
already ship.
```

If exact title or tagline text is requested, keep it out of the generation prompt.
After the base image passes inspection, use an available renderer and installed
font to overlay the exact approved string. Reinspect spelling, contrast, clipping,
and crop safety. If no renderer is available, do not claim the overlay exists.

## 4. Generate or stop honestly

If no approved generator is available, save the useful approved prompt and return
**PromptOnly**. Do not create an image placeholder or README image link.

When generation is available:

1. Send only the approved minimal brief using documented provider behavior.
2. Retrieve only the response artifact for that request. Treat URLs, redirects,
   content type, file extension, and requested dimensions as claims, not proof.
3. Bound the download, then inspect the actual local bytes. An HTML error returned
   from `header.png` is **Blocked**, not a PNG.
4. Preserve a valid returned raster unchanged as a distinct source such as
   `header.source.jpg` or `header.source.webp`. Never rename it to another format
   or require an SVG master.
5. Crop and resize with an available processor, preserving aspect ratio and using
   the approved crop rule. Encode the final asset in the required format.
6. Inspect the final bytes again before replacing or linking anything.

If a valid source was returned but inspection, exact resizing, encoding, or visual
review cannot be completed, retain it only under the distinct source name when
safe and approved, then return **Blocked**. Do not promote it to the final asset.

## 5. Validate the final image

Validation must establish all of the following from the saved bytes:

- a decoder recognizes the required format; magic bytes and decoded format agree;
- decoded width and height equal the required final dimensions;
- aspect ratio was preserved or the approved crop was applied without stretching;
- the intended metaphor, palette, focal point, crop-safe details, and title space
  match the approved brief;
- no unwanted lettering, fabricated UI, logos, people, sensitive data, or visual
  artifacts remain;
- any exact overlay is correct, legible, high contrast, unclipped, and crop-safe.

Write concise alt text only for the inspected final image, not for the intended
prompt. Describe the useful visual meaning and omit decorative detail. A
`header.alt.txt` sidecar is acceptable when that matches the project convention.

## 6. Wire links without breaking documentation

Add a project-relative Markdown reference only after the final file exists and its
case-correct path has been checked from the document's directory:

```markdown
![A paper lantern illuminating a stack of reading cards](assets/header.png)
```

Prefer `/` in Markdown links. Percent-encode unsafe path characters or choose a
simple basename. Reject absolute local paths and traversal. Avoid duplicate image
references. For **PromptOnly** or **Blocked**, leave the README unchanged so
`![Header](assets/header.png)` cannot become a broken promise.

## 7. Report one truthful state

Use exactly one terminal state:

| State | Required evidence | Artifact meaning |
|---|---|---|
| **Generated** | Final local image was decoded, dimension-checked, visually inspected, and any requested overlay verified | Report source/final paths, requested and actual dimensions, known provider/rendering method, alt text, and link update |
| **PromptOnly** | No approved generation capability was available; an approved useful prompt was saved | State explicitly that no image was generated and no image link was added |
| **Blocked** | Generation, retrieval, inspection, resizing, encoding, or composition validation failed | Report the failed prerequisite and only files actually retained; never present a source/URL/placeholder as final |
| **Unchanged** | Existing approved artwork was retained because replacement was not requested or approved | Report the retained path and why no file/link changed |

Use `state-matrix.json` as synthetic decision examples. Concrete interpretations:

`finalImageLinked` describes the resulting document state, not permission to
add a link. The `Unchanged` fixture cases already have working references and
retain them; if an existing image is unlinked, do not create a link while
reporting that nothing changed.

- Provider returns HTML bytes with a `.png` name: **Blocked**.
- Provider returns valid WebP, but exact PNG resizing or inspection is unavailable:
  preserve `header.source.webp` if approved and report **Blocked**.
- No generator exists, but a fictional brief can be saved: **PromptOnly**.
- `assets/header.png` is approved and replacement permission is absent:
  **Unchanged**.
- The current description no longer matches `header.prompt.txt`: flag the brief as
  stale; retain approved artwork as **Unchanged** until review/replacement is
  explicitly approved.
- Requested and decoded sizes differ: resize and reinspect if capability and crop
  rules exist; otherwise **Blocked**.

The final report must list state, files actually written or retained, requested
and actual dimensions when known, provider and processing method only when
established, inspection performed, source preservation, alt text status, and
whether documentation links changed.
