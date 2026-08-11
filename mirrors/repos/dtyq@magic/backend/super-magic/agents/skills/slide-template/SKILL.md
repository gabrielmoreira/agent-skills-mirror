---
name: slide-template
description: "Use when the user asks to create slides with a specific style, wants to use or inspect a slide template by code, wants to see platform-provided slide template options before creating, describes a custom template style, provides a PPTX/PPT file to convert into a platform template, or wants to extract a template from an existing Super Magic slide project."
---

# Slide Template Manager

Use this skill to retrieve platform templates by exact code, create a custom template from a style description, extract one from a PPTX/PPT file, or extract one from an existing Super Magic slide project.

## Template Metadata

Every downloaded or generated template package should use `template.json` as the metadata entry. Current template packages use the HTML slide template project format:

- `schema_version`: fixed to `"1.0"`.
- `template_id`: `PPT-xxxx` format.
- `category_code`: optional `PPT-CATE-xxxx` format from the platform category list. It may be omitted when classification is maintained outside the template.
- `label.zh_CN`, `label.en_US`, `description.zh_CN`, and `description.en_US`: display metadata.
- `files.theme_css`, `files.slides_dir`, and `files.images_dir`: shared CSS, reusable slide pages, and local assets. `files.visual_spec` is optional in a draft and should be added after the visual spec is generated.
- `slides[].file`, `slides[].title`, `slides[].layout`, and `slides[].description`: reusable page index and default order.
- `source.kind`: `original`, `converted`, or `derived`, with a 1920x1080 canvas.

Do not write or rely on legacy fields such as `name`, `template_dir`, `package_type`, `slides[].slots`, `slides[].source_slide`, `slides[].best_for`, or `slides[].risks`. Use the paths declared by `template.json`; do not assume a fixed directory layout beyond the metadata.

## Template Source

- This skill does not bundle built-in templates. Do not read, list, or copy templates from `<skill_dir>/assets/templates/`.
- Platform templates are external resources identified by exact template `code`.
- Template `code` must come from a platform-provided template list, a user selection, a user-provided value, or explicit upstream context. Do not invent codes, rewrite casing, or map old local directory names to codes.
- If the user asks to see templates and no platform template list or code is available in context, ask the user to select a template in the UI or provide the template code. Do not fabricate local options.

## Decision

- Explicit template `code`: install the template package with `install_slides_template`, then inspect the installed template files.
- Platform template list is available but no template is selected: recommend 3-5 suitable options with `ask_user`. Each option must include name, short description, and exact `code`, plus "no template/default style".
- User only describes scenario/topic/audience without enough visual specs and no platform template list is available: ask for a platform template code or confirm no template/default style.
- User provides a PPTX/PPT/presentation template file or URL and asks to convert it into a platform template: read `references/pptx-template-workflow.md` and follow the PPTX Template Workflow first.
- User provides an existing Super Magic slide project directory that contains `magic.project.js` with `type: "slide"` and asks to convert or extract it into a reusable template: read `references/project-template-workflow.md` and follow the Project Template Workflow. Do not modify the source project, and do not create the final ZIP until the user confirms.
- User describes a concrete visual style (colors, materials, layout, decorative elements, and visual keywords): generate a custom template first, then use it.
- Editing/fixing/refactoring existing slides does not trigger template selection unless the user asks for a new PPT/project.

## Platform Template Retrieval

When a template code is selected and you need to read the template package, first call `install_slides_template` through Code Mode, then inspect the installed directory.

```python
from sdk.tool import tool

result = tool.call("install_slides_template", {
    "code": template_code
})

installed_directory = result.data["installed_directory"]
```

After receiving `installed_directory`:

1. Use the returned `installed_directory`; the tool extracts the package into a temporary directory to avoid occupying workspace storage.
2. Read `template.json` from `installed_directory` first.
3. Read all available resources declared by `template.json` that are useful for the deck:
   - Always read `files.theme_css` when present.
   - Read `files.visual_spec` for design rules, typography, layout types, chart rules, and image guidance when present.
   - Read representative `slides[].file` files or representative HTML files under `files.slides_dir`, when present.
4. Treat `theme.css` as the authoritative CSS. Treat `template.json`, `visual-spec.md`, and `slides/*.html` as complementary sources for reusable layouts, edit hints, components, composition patterns, visual rhythm, and asset references.
5. Read image paths or assets only when needed for the target deck.
6. Do not link to installed template files from generated slides. Copy the required CSS and assets into the PPT project after `create_slide_project`.

## PPTX-Derived Template Contract

This skill owns the template package contract and conversion/refinement guidance. It may describe how a PPTX-derived template should signal reuse intent, but detailed page-by-page slide authoring belongs to the slide creation agent.

Identify a PPTX-derived template with these rules:

- Strong signal: `template.json.source.kind` is `"converted"` and `template.json.source.file` ends with `.pptx`, `.ppt`, `.potx`, `.pot`, or `.ppsx` case-insensitively.
- Medium signal: `visual-spec.md`, the template description, or the package notes explicitly say the template was converted from PPTX/PPT.
- Weak signals such as absolute-positioned HTML, `data-slot*` attributes, local image-heavy pages, or page-level converted styles can support the decision, but must not trigger PPTX-derived handling by themselves.

When a template is PPTX-derived, preserve and document this reuse contract:

- Treat `slides/*.html` as concrete page masters, not loose visual inspiration.
- Make page selection possible through specific `template.json.slides[].title`, `layout`, and `description`; descriptions should mention visible structure, content areas, image/chart/table roles, and notable constraints.
- Keep `data-slot`, `data-slot-type`, and `data-slot-role` in slide HTML as downstream editing hints, but do not add `template.json.slides[].slots`.
- Preserve source DOM structure, page-level CSS, local asset references, image/SVG/chart containers, absolute positioning, typography hierarchy, color system, and visual elements unless they are broken, sensitive, or clearly renderer-only noise.
- Document locked elements and editable boundaries in `visual-spec.md`, especially backgrounds, decorative images, textures, hero visuals, SVGs, shapes, page positioning, typography scale, palette, text fitting, content-image replacement, and chart-data replacement.
- Template-preserving reuse does not bypass sanitization. Logos, QR codes, screenshots, real-person photos, internal dashboards, and other ambiguous sensitive assets still require user confirmation before final packaging.

## Template Application Workflow

1. Resolve the selected template code from user choice or upstream context. If there is no exact code, ask for it or proceed with no template if the user confirms.
2. Call `install_slides_template` with the exact code, then use `result.data["installed_directory"]`.
3. Read `template.json` from the installed directory, then read the available resources it declares (`theme_css`, `visual_spec`, `slides_dir`, `images_dir`, and `slides[].file`) before creating slide pages.
4. Decide whether the package is PPTX-derived using the rules above. If yes, preserve the PPTX-derived template contract for downstream slide creation.
5. Before writing slides, summarize internally: package resources, palette roles, typography, layout inventory, reusable components, slot/page patterns, composition rules, asset dependencies, adaptation rules, and whether the selected package is PPTX-derived.
6. Create the slide project with `create_slide_project`.
7. Copy `theme.css` and any required assets from the installed template into the PPT project. Keep all slide references local to that project.
8. Each slide HTML must include the local CSS:

```html
<link rel="stylesheet" href="theme.css" />
```

9. For PPTX-derived templates, downstream slide creation should apply the template-preserving contract instead of treating converted pages as loose style references.
10. For non-PPTX-derived templates, load `creating-slides` and generate slides. Keep every slide fixed at 1920x1080; do not use responsive design. Use only the installed template's CSS variables, components, dedicated layout patterns, chart colors, and image guidance inferred from the template package. If no installed layout fits, compose the page from template components, decorations, and layout helpers instead of generic centered text.
11. Each slide should have one clear visual anchor, such as an image area, chart, matrix, large number, color block, or template-specific decoration.
12. Use `data-slot`, `data-slot-type`, and `data-slot-role` from slide HTML as editing hints when present, but do not expect slot metadata in `template.json`.

## Image Rules

- First decide whether the page needs images. Use images for visual layouts, cover/section/closing pages, specific person/product/scene/case, or sparse text.
- Skip image search for dense comparison, card grid, timeline/process, data dashboard, or chart pages.
- When the selected template includes local image or illustration assets and the target slide needs an image, or the user has not provided a required image, inspect and reuse suitable assets from the template first. Prefer these assets for decorative illustrations, cover/section visuals, backgrounds, motifs, and style-consistent placeholders.
- Use `image_search` only after checking template assets, or when the slide needs a factual photo, specific person/product/place, screenshot, brand mark, or another exact image the template cannot supply. Try at least 2 content-relevant keyword groups and include style keywords inferred from the installed template.
- If search results are poor, use `generate_images` and save output under the PPT project `images/` folder.
- Apply template style only to creative illustrations (concept visuals, atmosphere, decorative or abstract images). Do not stylize factual photos, real people, real places, products, history/science references, brand marks, screenshots, QR codes, or data graphics.
- Images should occupy meaningful visual space; do not use them as tiny icons.
- Images can be used as local section backgrounds with an overlay when they support the content and template style.
- If a slide skips images, use a non-image visual anchor instead of leaving sparse text floating in empty space.
- Do not repeat the same background-image treatment on most consecutive slides.

## Custom Template Workflow

Use when the user describes a style in text, provides screenshots, or provides an existing template package. Read `<skill_dir>/references/custom-template-workflow.md` and follow it before generating custom template files.

## PPTX Template Workflow

Use when the user provides a presentation file such as `.pptx`, `.ppt`, `.potx`, `.pot`, `.ppsx`, a WPS presentation, or a URL to a presentation template and asks to convert it into this platform's reusable template format. Read `<skill_dir>/references/pptx-template-workflow.md`, then call `convert_pptx_to_slide_template`. After the tool returns, keep working: analyze the converted content, write `visual-spec.md`, sanitize obvious sensitive content, confirm ambiguous sensitive assets through `ask_user`, refine `template.json`, `theme.css`, `images/`, and `slides/*.html`, run lightweight QA, then ask whether to package the refined draft as the final template ZIP. Do not call the old raw HTML renderer tool or run this skill's old PPTX extraction scripts.

## Project Template Workflow

Use when the user provides an existing Super Magic slide project directory that contains `magic.project.js` with `type: "slide"` and asks to convert or extract it into a reusable platform template. Read `<skill_dir>/references/project-template-workflow.md` and follow it before creating template draft files.

## Style Specificity & Template Scope

- `theme.css` must only contain template-specific styles: color variables, background decorations, typography, template components, and visual helpers. It must NOT contain structural layout properties (padding, flex, grid) on framework-level selectors like `.slide-container`.
- `.slide-container` in `theme.css` should only set: dimensions (`width`/`height`), `position`, `overflow`, `box-sizing`, and template-specific backgrounds/colors. Layout properties (`padding`, `margin`, `display: flex`, `flex-direction`) must be defined in each slide page's own `<style>` block.
- Page-level `<style>` in each slide HTML has higher specificity than `theme.css` by nature of source order (page styles load after `theme.css`). If needed, use more specific selectors (e.g., `.slide-container.my-page`) to ensure page styles override template defaults.
- When writing slide pages, always define layout (padding, flex, grid) directly in the page `<style>` rather than relying on `theme.css`, to avoid cross-page style conflicts.

## Output

- Platform template workflow output: a complete template package generated through `creating-slides`, using template files installed through `install_slides_template`.
- Built-in local template workflow output: none; local bundled templates are no longer supported.
- Custom workflow output: a complete template package generated through `creating-slides`.
- PPTX template conversion output: first create a draft template folder containing `template.json`, optional `magic.project.js`, `theme.css`, `images/`, and `slides/*.html`; use the model to analyze the converted visual style, write `visual-spec.md`, sanitize obvious sensitive content, confirm ambiguous sensitive assets through `ask_user`, refine the folder, run lightweight QA, then ask the user whether to create the final sibling `<template-id>-template.zip`. If a ZIP is created, exclude `magic.project.js` and unconfirmed sensitive assets.
- Project template conversion output: first create a new standalone draft template folder containing `template.json`, `visual-spec.md`, `theme.css`, `images/`, and deduplicated `slides/*.html`; sanitize sensitive content and ask the user through `ask_user` before keeping ambiguous sensitive assets such as logos or internal screenshots. Only after user confirmation, create the sibling `<template-id>-template.zip`.
- Preview images may be generated by a script from `slides/*.html`, but they must be stored in build or publishing artifacts and must not be included in the template ZIP.
- Do not paste raw HTML in chat.
