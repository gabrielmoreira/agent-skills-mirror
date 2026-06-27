# Style System

Paper Deck 的风格不是“换配色”，而是一整套视觉导演规则：字体气质、构图密度、图像真实感、图表语言、留白、页面节奏必须一致。

## Presets

| Preset | 适合 | 视觉锚点 |
|---|---|---|
| `journal-minimal` | 内部讨论、组会、论文答辩、公开学术汇报 | Nature/IEEE-inspired 论文图风格，简明、清晰、投稿级配色 |
| `business-research` | 商业化研究、行业报告、投资汇报、客户分享 | 高级研究 briefing，结构化标题、数据证据、杂志式商业质感 |
| `warm-notes` | 知识课、科普、论文学习笔记、教育内容 | 温暖手记风，明亮纸感、手绘注释、柔和高亮 |
| `liquid-glass` | AI 产品、工程系统、视觉章节页、高级发布感内容 | Apple-inspired 透明玻璃质地，丰富柔和色彩、半透明层次、高级流光 |

## Default Recommendation

- 论文组会 / 答辩 / 技术公开分享：优先 `journal-minimal`
- 商业研究 / 行业趋势 / 投资人或客户分享：优先 `business-research`
- 教程 / 科普 / 学习笔记 / 知识内容：优先 `warm-notes`
- AI 产品 / 工程系统 / 高级视觉章节页：优先 `liquid-glass`

## Preset Details

### journal-minimal

目标：简约但不简陋，像 Nature / IEEE 论文图、投稿图和正式学术汇报的结合。它可以用于内部讨论，也可以直接拿去答辩或公开汇报。

- Background: white / near-white / very light cool gray, with subtle panel separation only when needed
- Color: black, cool gray, one clear scientific accent (Nature blue, teal, muted red, or IEEE blue)
- Typography: clean sans-serif, compact labels, figure-caption discipline
- Visuals: publication-style method figure, pipeline, matrix blocks, equation callouts, small data inset, real paper figure crop when useful
- Layout: dense enough to feel useful; main diagram should occupy 65-80% of the slide, not float in excessive whitespace
- Feel: submission-quality clarity, credible, direct, no decoration for decoration's sake
- Avoid: cartoon, heavy texture, fake 3D, glossy SaaS illustration, decorative stickers, giant empty hero whitespace
- Text density: medium; title + 3-8 short labels

Prompt phrase:

```text
Nature / IEEE-inspired minimal academic presentation slide, publication-quality scientific figure aesthetic, clean white or light gray background, precise method diagram, clear restrained scientific color palette, compact readable labels, credible paper submission visual style
```

### business-research

目标：商业化研究分享能用，结构强，有数据证据，也有高级传播感。

- Background: white / pale gray / subtle grid
- Color: charcoal + navy/teal/gold single accent, occasional full-bleed editorial photo if needed
- Typography: executive briefing, compact but clean; large section titles and small source notes
- Visuals: 2x2, timeline, evidence wall, market map, metric callout, before/after, strategic thesis
- Feel: premium consulting research + serious magazine feature
- Avoid: colorful startup gradients, decorative blobs, fake dashboards, random business stock photos
- Text density: medium

Prompt phrase:

```text
premium business research presentation slide, structured evidence layout, consulting-grade clarity, restrained color, elegant editorial data visualization, credible strategic briefing aesthetic
```

### warm-notes

目标：亲和、有手作感，但不是幼稚。

- Background: warm cream paper, clean and bright
- Color: ink black + soft blue/coral/olive/yellow
- Typography: clear handwritten-style labels, readable
- Visuals: sketchnote, flow, analogy, small helpful icons
- Avoid: old parchment, dirty texture, childish cartoon
- Text density: medium

Prompt phrase:

```text
warm research notebook slide, clean cream paper, hand-drawn but precise, soft highlighter colors, readable handwritten-style labels, thoughtful educational design, polished human study notes
```

### liquid-glass

目标：舍弃普通科技风，改成更有辨识度的透明玻璃质地。参考 Apple 式 Liquid Glass / translucent material 的高级感：不是全透明，也不是廉价赛博，而是有折射、柔和色彩和层次的玻璃版式。

- Background: soft luminous gradient field or deep blurred color field; no flat empty black screen
- Color: richer but controlled palette: icy blue, violet, cyan, soft magenta, pearl white, translucent charcoal
- Typography: Apple-like clean sans-serif, large calm title, minimal body
- Visuals: frosted glass panels, translucent cards, subtle refraction, soft highlights, layered depth, precise figure fragments under glass
- Layout: 2-4 meaningful glass layers; avoid one giant empty glass rectangle
- Feel: premium Apple keynote material study, colorful but elegant, tactile, high-end visual chapter page
- Avoid: cheap neon cyberpunk, excessive glow, random 3D objects, plastic buttons, SaaS dashboard pile, fake robot cliches, unreadable low contrast
- Text density: low-medium; best for cover, section divider, conceptual overview, not dense method proof

Prompt phrase:

```text
Apple-inspired liquid glass presentation slide, premium translucent frosted glass material, soft colorful refraction, layered depth, pearl white and icy blue violet highlights, clean Apple keynote typography, elegant high-end visual design, not cyberpunk
```

## Consistency Rules

- 一份 deck 只选一个 preset。
- 一个 preset 只允许 1-2 个强调色。
- 封面图可以更有冲击力，机制页必须更清楚。
- `journal-minimal` 不追求炫，追求论文图一样的清楚。
- `liquid-glass` 不追求科技模板，追求真实玻璃材质和高级色彩。
- 如果用户提供参考图，先提取可复用的设计语言，不要照抄具体作品。
