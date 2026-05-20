# Document Generation

Use this reference when the user asks for a complete patent application document, Word file, DOCX, PDF, printable application text, or direct generation instead of plain text.

## Default Deliverable


- Generate a `.docx` file as the primary deliverable.
- Generate source-faithful black-and-white SVG reference drawings, create PNG fallback drawings when possible, generate Image2-style refinement prompts, and embed visible drawings in the `.docx` for complete application requests.
- Export a `.pdf` copy when LibreOffice or an equivalent DOCX-to-PDF converter is available.
- Use Simplified Chinese and a general Chinese invention patent application layout.
- Do not use a user-specific agency, university, company, or CNIPA form template unless the user supplies one.

## Modes

- `direct`: default. Draft the patent content and generate files without asking follow-up questions when the input supports a complete document.
- `human-in-loop`: report missing information and key choices first, then generate after the user confirms.
- `text-only`: output only the five-part patent text and skip file generation.

If the user does not specify a mode, use `direct`.

## Structured Content Contract

Before calling the DOCX generator, assemble a JSON object with these fields:

```json
{
  "invention_name": "一种……方法",
  "source_title": "论文标题",
  "abstract": "说明书摘要正文",
  "abstract_drawing": "建议选取图1作为摘要附图……",
  "claims": [
    "1.一种……方法，其特征在于，包括：……。",
    "2.根据权利要求1所述的方法，其特征在于，……。"
  ],
  "description": {
    "technical_field": "技术领域正文",
    "background": "背景技术正文",
    "invention_content": "发明内容正文",
    "drawing_description": [
      "图1为一种……方法流程图。",
      "图2为一种……系统结构示意图。"
    ],
    "embodiments": "具体实施方式正文"
  },
  "drawings": [
    "图1：一种……方法流程图，包含步骤S101、S102、S103。",
    "图2：一种……系统结构示意图，包含模块A、模块B、模块C。"
  ],
  "source_figures": [
    {
      "figure_no": 1,
      "source_label": "Figure 2",
      "caption": "论文原图图注",
      "page": 4,
      "notes": "从论文原图和正文提取的节点、箭头或布局依据"
    }
  ],
  "drawing_assets": [
    {
      "figure_no": 1,
      "title": "一种……方法流程图",
      "type": "method_flow",
      "svg_path": "output/paper_图1.svg",
      "png_path": "output/paper_图1.png",
      "caption": "图1 一种……方法流程图",
      "abstract_candidate": true,
      "validation": {
        "content_width_ratio": 0.8,
        "content_height_ratio": 0.8,
        "internal_title": false,
        "passes": true
      },
      "image_model_prompt": "请生成中国发明专利申请的说明书附图图1……"
    }
  ],
  "image_model_prompts": [
    {
      "figure_no": 1,
      "prompt": "请生成中国发明专利申请的说明书附图图1……"
    }
  ],
  "drawing_validation": [
    {
      "figure_no": 1,
      "content_width_ratio": 0.8,
      "content_height_ratio": 0.8,
      "internal_title": false,
      "passes": true
    }
  ],
  "gaps": [
    "【待补充：论文未提供关键参数的确定方式。】"
  ]
}
```

Required fields for a clean final document are `invention_name`, `abstract`, `claims`, and `description`. In `direct` mode, if source material is incomplete, put explicit `【待补充：...】` placeholders in the relevant field and list each gap in `gaps`. Do not fill gaps with inferred technical content.

## Drawing Generation

For complete application documents, generate SVG drawings before DOCX generation:

```powershell
python skills/paper2patent/scripts/generate_patent_drawings.py patent_content.json --output-dir output --update-json
```

The drawing generator can infer basic `drawing_assets` from `drawings` when the JSON does not already contain them, but the `drawings` text must explicitly contain the steps, modules, nodes, or connections needed for each figure. Review the generated SVGs and PNG fallbacks for fidelity before embedding them. Generated drawings must be black-and-white patent line drawings, not copied paper figures or decorative images.
When `source_figures` is present, the generator should carry the matched source metadata into each `drawing_asset` so downstream review can trace the patent drawing back to the original paper figure.

The SVG/PNG image canvas must not contain the figure number or title. Figure captions belong in `caption`, `abstract_drawing`, and the DOCX/PDF text outside the image.

## DOCX Generation

Use the bundled script:

```powershell
python skills/paper2patent/scripts/generate_patent_docx.py patent_content.json --output output/patent_application.docx --require-drawings
```

The script creates an A4 Word document with:

- Document title.
- Source paper title when provided.
- Five application sections: 说明书摘要、摘要附图、权利要求书、说明书、说明书附图.
- Standard sub-sections inside 说明书.
- Embedded reference drawings in 摘要附图 and 说明书附图 when `drawing_assets` is present.
- Converter-compatible PNG drawings are embedded by default when `png_path` is present.
- A final 材料缺口说明 section when `gaps` is non-empty.

Use `--require-drawings` for full application requests so missing image assets fail fast instead of silently producing a text-only drawing section.

Use `--embed-svg-fallback` only when the target Word version is known to support Office SVG fallback markup. For maximum converter compatibility, keep the default PNG embedding while retaining SVG files as separate reference assets.

## PDF Export

Use the bundled script:

```powershell
python skills/paper2patent/scripts/export_patent_pdf.py output/patent_application.docx --output output/patent_application.pdf
```

If LibreOffice is unavailable, the script can render an image-based review PDF from the structured JSON when Pillow is available:

```powershell
python skills/paper2patent/scripts/export_patent_pdf.py output/patent_application.docx --output output/patent_application.pdf --content-json patent_content.json
```

Report this as an image-based fallback PDF. The DOCX remains the primary editable deliverable.

## Validation

After generation:

- Confirm the DOCX exists and is non-empty.
- Confirm the SVG drawings and any PNG fallback drawings exist and are non-empty.
- Confirm the generated drawings have no internal figure title, no unrelated text, and no excessive blank margins.
- Confirm `drawing_validation` passes or document the limitation.
- Confirm `image_model_prompts` exist when a two-stage Image2-style refinement flow is requested.
- Inspect the DOCX package when possible: `word/media/` contains embedded drawing images, `word/_rels/document.xml.rels` contains image relationships, and `word/document.xml` contains DrawingML picture references.
- If PDF export was requested, confirm the PDF exists and is non-empty.
- Render the PDF when Poppler or another renderer is available and verify that the abstract drawing and specification drawings are visible.
- Open or parse the generated content when tools are available; otherwise run a file-size check and report the converter limitation.
- Search generated text for `【待补充` and report remaining placeholders to the user.
- Keep generated patent applications, papers, and private disclosures out of the repository unless the user explicitly asks for a temporary local artifact outside version control.
