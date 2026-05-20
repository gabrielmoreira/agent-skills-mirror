# Quality Checklist

Run this checklist internally before final output or when reviewing a draft. Report only user-relevant issues unless the user explicitly asks for the checklist.

## Fidelity

- Every technical feature is supported by the paper or supplied patent text.
- No unsupported hardware, deployment scenario, training strategy, application domain, metric, or result was added.
- Experimental conclusions are not overstated as universal technical effects.
- Paper wording has been transformed into patent language rather than copied verbatim.
- Generated drawings are traceable to source paper figures, figure captions, method text, claims, or specification, not to generic sample nodes.


## Patent Logic

- Difference point, technical problem, technical solution, and technical effect form a coherent chain.
- The invention name is consistent throughout the document.
- Claims and specification support each other.
- Drawing descriptions correspond to the claimed steps or modules.
- Source-paper figures, patent captions, claims, specification, and drawing labels use consistent terminology.

## Claims

- Independent claims cover a complete technical solution.
- Dependent claims have valid citation basis.
- Claims contain no uncertain words such as "等", "大约", "优选", "可以", "比如", or "不限于".
- Each claim ends with exactly one final period and has no internal period.
- Total claim count is reasonable for the requested scope.

## Specification

- Technical background includes definitions, existing methods, existing problems, causes, and consequences.
- Invention content includes summary, detailed solution, and technical effects.
- Embodiments are sufficiently detailed for a skilled person to implement the solution.
- Terms remain consistent across abstract, claims, specification, and drawings.

## Document Files

- A full direct-generation request creates a DOCX unless the environment prevents file writing.
- A full direct-generation request creates SVG reference drawings, creates PNG fallback drawings when possible, and embeds visible drawings in the DOCX.
- PDF export is attempted when LibreOffice or an equivalent converter is available.
- The generated document contains all five sections: 说明书摘要、摘要附图、权利要求书、说明书、说明书附图.
- The 摘要附图 section contains the selected reference drawing, not only a text statement.
- The 说明书附图 section contains every generated figure with a centered caption.
- Image files do not contain internal figure numbers or figure titles; captions appear outside the image.
- Drawing canvases are tightly framed around the technical content, with no excessive blank margins.
- Drawings contain no unrelated title text, explanatory paragraphs, logos, watermarks, decorative elements, colors, grayscale, shadows, or unsupported labels.
- `image_model_prompts` require strict structural copying, no internal title, tight framing, and no unsupported modules when Image2-style refinement is used.
- The DOCX package contains embedded drawing image files under `word/media/`, image relationships under `word/_rels/document.xml.rels`, and DrawingML picture references in `word/document.xml`.
- Rendered PDF pages show the drawings clearly without blank image placeholders, clipped labels, or overlapping text.
- Any remaining `【待补充：...】` placeholders are also listed in 材料缺口说明.
- Generated files are not committed to the repository unless the user explicitly requests a tracked example.
- File paths in the final response do not expose private local user data beyond the workspace path needed for access.

## If Issues Remain

If the issue is caused by missing source material, do not fabricate. State the missing material and request it. If the issue is caused by an unsupported addition, remove or qualify it.
