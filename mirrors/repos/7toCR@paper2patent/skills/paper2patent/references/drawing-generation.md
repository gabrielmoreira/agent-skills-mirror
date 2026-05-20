# Drawing Generation

Use this reference when the user asks for patent drawings, drawing prompts, drawing descriptions, or consistency checks between drawings and patent text.

## Drawing Types


Select only drawings supported by the source paper figures, captions, method text, claims, and specification:


- Method flowchart: covers all steps of an independent method claim.
- System block diagram: covers supported system modules and data/control relationships.
- Data flow diagram: shows input, intermediate products, and output when the paper describes data transformation.
- Detail diagram: expands a dependent claim or key sub-step when source material supports it.

## Visual Constraints

- Use pure black-and-white line drawings.
- Use a white background.
- Do not use color, gradients, shadows, textures, photos, 3D renders, cartoons, or decorative effects.
- Keep lines clear, even, and continuous.
- Use Simplified Chinese labels.
- Keep labels short: module names, step numbers, component names, or key terms only.
- Avoid long sentences and complex formulas inside drawings.
- Do not draw the figure number or figure title inside the image canvas. Keep captions outside the image in the patent document.
- Do not include unrelated titles, watermarks, logos, UI chrome, explanatory paragraphs, or labels unsupported by the source material.
- Keep the content tightly framed. The technical content should occupy about 80% or more of both canvas width and canvas height; avoid large blank margins, while preserving enough edge space to prevent clipping.

## Source-Figure Priority

For complete patent applications, generate the first reference drawings from the original paper material before using image-generation models:

1. Prefer paper figures, figure captions, and nearby method text as the source of layout, nodes, arrows, and technical relationships.
2. Use the patent claims and specification to normalize legal terminology, step numbers, module names, and figure captions.
3. If no source figure exists, derive a drawing only from explicit source-supported method steps, modules, or data-flow descriptions.
4. If the available text does not identify enough steps, modules, nodes, or connections, mark a material gap or fail that figure generation; do not fill with generic examples.

## Numbering and Consistency

- Method steps use `S101`, `S102`, `S103` when a procedural format is needed.
- Figure numbers follow the order used in the specification.
- Module names, step names, component numbers, and arrows must match the claims and specification.
- Do not add components, steps, links, or terms not present in the patent text.
- If a drawing cannot be created from the available text, request the missing architecture or step information.
- Captions may contain "图1" or a descriptive title, but the image file itself must not contain the figure number or title.

## Required Output for Full Applications

For complete Word/PDF patent application requests, generate drawing specifications, black-and-white SVG reference drawings, and converter-compatible PNG fallback drawings when Pillow is available. Drawing specifications alone are acceptable only in `text-only` mode or when the user explicitly accepts a no-image fallback.

The default generator is:

```powershell
python skills/paper2patent/scripts/generate_patent_drawings.py patent_content.json --output-dir output --update-json
```

The script writes SVG files, writes PNG fallback files when possible, and updates `drawing_assets` in the JSON. The DOCX generator embeds a visible drawing for each asset, using PNG fallback by default for Word/PDF compatibility.

## Drawing Specifications

Always keep drawing specifications in the generated application text:

```text
图1：一种[发明名称]方法流程图
包含步骤S101...、S102...、S103...，各步骤按照从上到下的顺序连接。

图2：一种[发明名称]系统结构示意图
包含[模块A]、[模块B]、[模块C]，数据流方向为...
```

For image-generation environments or external drawing tools, provide one prompt per figure and require independent image outputs for each figure. Embed generated images only after checking that they are black-and-white line drawings with no extra modules, labels, arrows, or visual effects.

For Image2 or similar two-stage refinement, use the local SVG/PNG as the structural reference. The prompt must require strict structural copying, no internal title, no extra content, and tight framing. Image-generation output is not a source of new technical disclosure.

## SVG Asset Contract

Each figure asset should be represented in `drawing_assets`:

```json
{
  "figure_no": 1,
  "title": "一种……方法流程图",
  "type": "method_flow",
  "svg_path": "output/paper_图1.svg",
  "png_path": "output/paper_图1.png",
  "caption": "图1 一种……方法流程图",
  "source_figure": {
    "figure_no": 1,
    "source_label": "Figure 2",
    "caption": "paper figure caption",
    "page": 4,
    "notes": "source-supported modules and arrows"
  },
  "abstract_candidate": true,
  "validation": {
    "content_width_ratio": 0.8,
    "content_height_ratio": 0.8,
    "internal_title": false,
    "passes": true
  },
  "image_model_prompt": "请生成中国发明专利申请的说明书附图图1……"
}
```

Supported `type` values are `method_flow`, `system_block`, and `data_flow`. Use `method_flow` when uncertain and the drawing specification is step-based. Do not create decorative or conceptual figures.
When `source_figures` is present, the generator should attach the matching source-paper metadata to each `drawing_asset` and use it as the first reference for layout, prompts, and consistency checks.

When available, keep source-paper figure metadata in `source_figures`:

```json
{
  "figure_no": 1,
  "source_label": "Figure 2",
  "caption": "paper figure caption",
  "page": 4,
  "notes": "source-supported modules and arrows"
}
```

## Word/PDF Generation Policy

- Always include the abstract drawing choice or statement in `abstract_drawing`.
- Always include drawing specifications in `drawings`.
- For a full application document, run the SVG drawing generator before DOCX generation.
- The DOCX must embed the selected abstract drawing in `摘要附图`.
- The DOCX must embed every generated figure in `说明书附图`.
- Prefer PNG fallback for the embedded visible image when the target Word/PDF converter cannot reliably render SVG.
- If compliant image files cannot be produced, state the limitation clearly and do not present the file as a complete application with drawings.
- Reject or regenerate drawings that have internal titles, excessive blank margins, unsupported modules, visual decorations, or text overlaps.
