# Input Requirements

## Minimum Input

Require enough source material to identify the invention:

- Paper title.
- Abstract or problem statement.
- Core method, system architecture, algorithm steps, or implementation flow.
- Any figure or table descriptions that define the technical process.
- Source paper figures, figure captions, architecture descriptions, or figure screenshots when the application requires drawings.

Do not infer technical details merely to complete a patent structure.


For `direct` mode, generate the requested file with explicit `【待补充：...】` placeholders and a material gap section when minimum input is missing. For `human-in-loop` mode, ask for missing parts before drafting if the gap affects the technical solution or claim scope.

## Preferred Input Format

Ask users to provide source material in this structure when possible:

```text
【论文标题】：
【论文摘要】：
【核心技术方法】：
【系统架构/流程图说明】：
【论文原图/图注】：如有，请粘贴图注、页码、截图说明或提供可解析 PDF
【实验结果或技术效果】：
【需要输出】：Word + PDF / 完整专利文本 / 权利要求书 / 附图规范 / 忠实性检查
【输出模式】：direct / human-in-loop / text-only
```

PDFs are acceptable when the environment can read them. If the PDF cannot be accessed or parsed, request pasted text for the abstract, method section, and key figures.

## Input Assessment

Before conversion, assess:

- Completeness: whether the material supports a full patent draft.
- Patentability clues: concrete technical means, step flow, module architecture, data processing, or system interaction.
- Fidelity risk: places where the paper is silent and drafting would require speculation.
- Drawing readiness: whether the source paper figures, captions, method text, or generated patent text contain enough modules, steps, labels, and flow direction for drawings.
- Source-figure priority: use paper figures, figure captions, and nearby method text before relying on the generated patent text alone.

## Handling Gaps

When information is incomplete in `human-in-loop` mode, prefer a short gap report:

```text
当前材料不足以完成完整专利文本。请补充：
1. 核心方法步骤或系统模块；
2. 关键输入、输出和中间结果；
3. 与现有技术相比的区别点和技术效果；
4. 需要绘图时补充论文原图、图注或架构/流程说明。
```

When information is incomplete in `direct` mode, keep file generation moving but mark every unsupported part explicitly:

```text
【待补充：论文未提供核心方法的关键输入。】
【待补充：论文未说明该模块与后续步骤的数据关系。】
```

Also add a `材料缺口说明` section to the structured document content. Placeholders are allowed only to mark missing source material; they must not be used as a license to add guessed modules, effects, parameters, devices, datasets, or application scenarios.

For drawings, missing source material must not be filled with sample flowchart nodes or generic module names. If a figure specification lacks explicit steps, modules, nodes, or connections, mark the drawing as a gap or fail drawing generation for that figure.
