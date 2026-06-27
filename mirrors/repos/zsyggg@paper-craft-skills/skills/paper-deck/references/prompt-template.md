# Prompt Template

每页 prompt 先保存为 `prompts/NN-slide-{slug}.md`，再调用生图模型。

## Template

```markdown
---
slide: NN
title: "Slide title"
role: "cover | problem | method-overview | mechanism-detail | evidence | takeaway"
style_preset: "journal-minimal"
language: "zh"
aspect_ratio: "16:9"
output: "images/NN-slide-slug.png"
---

Create one complete 16:9 presentation slide image.

Purpose:
[This slide's single message.]

Style:
[Use the selected preset phrase from style-system.md.]

Composition:
[Describe the layout spatially: left/right/top/bottom/center, main visual size, hierarchy.]

Content:
- [Short label or title text that may appear on the slide]
- [Diagram elements and their relationships]
- [Data/evidence if needed]

Visual Details:
- [Color, line, texture, typography, background]
- [How to render diagrams, arrows, cards, figure callouts]

Constraints:
- The output must be a polished 16:9 slide, not a poster mockup.
- Keep all text short and readable.
- Do not generate page numbers, logos, watermarks, signatures, browser chrome, app chrome, or decorative borders.
- Do not use fake brand logos, fake UI details, meaningless microtext, plastic 3D, generic AI robot imagery, neon cyberpunk effects, gradient blobs, or stock-template decorations.
- Keep enough whitespace for hierarchy, but do not leave the slide feeling empty; the main visual/evidence area should usually occupy 60-80% of the slide.
```

## With Source Visuals

When using real screenshots, paper figures, tables, plots, or user-provided images, add this block:

```markdown
Source Visual:
- Use source image: [path or figure/table/page number]
- Crop/focus: [exact region or semantic target]
- Placement: [left/right/center/full-width panel]
- Treatment: [clean frame / glass panel / figure callout / side annotation / zoom inset]
- Fidelity: preserve the real visual content; do not invent new labels, fake UI, fake plots, or fake numbers
```

## Chinese Slide Text

中文页尽量让图片内文字短：

- 标题不超过 16 个汉字。
- 标签不超过 8 个汉字。
- 不要让模型写长句、段落、公式推导。
- 复杂文字放到备注或后续可编辑文字层。

## Paper Figure Remix

如果重画论文图：

- 不要照抄原图布局。
- 保留事实关系：模块名、输入输出、关键公式、实验结论。
- 改善视觉层级：先让观众看懂主流程，再看细节。
- 标注来源：在 outline 的 Evidence 中写 Figure/Table 编号；不要把长引用塞进图里。

## Repair Prompt Pattern

返修第 N 页时，在原 prompt 末尾追加：

```text
Revision request:
[User's requested change.]

Keep:
[Elements that must stay the same.]

Change:
[Elements that should change.]

Avoid:
[Problems observed in previous image.]
```

不要只写“更高级一点”。要翻译成具体视觉修改：减少装饰、控制留白、改成白底、换成真实论文图截图、缩短标签、放大主流程等。
