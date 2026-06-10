# Beautiful Article Skill —— 把任意素材编辑成一篇精美的文章

> 一个面向 AI Agent 的 Skill：把任意素材（URL / PDF / DOCX / Markdown / 纯文本 / 截图 / 粘贴材料）**编辑、设计**成一篇**比原文更易读、更便于分享和归档的精美文章**。

[English](./README.md) · [返回集合首页](../../README.zh-CN.md)

![Beautiful Article Skill](https://cdn.jsdelivr.net/gh/ConardLi/assets@main/imgs/article/banner.webp)

### 主题预览

<table>
<tr>
<td width="25%" align="center"><img src="https://cdn.jsdelivr.net/gh/ConardLi/assets@main/imgs/article/tufte.webp" alt="tufte" width="100%"><br/><sub><b>tufte</b></sub></td>
<td width="25%" align="center"><img src="https://cdn.jsdelivr.net/gh/ConardLi/assets@main/imgs/article/press.webp" alt="press" width="100%"><br/><sub><b>press</b></sub></td>
<td width="25%" align="center"><img src="https://cdn.jsdelivr.net/gh/ConardLi/assets@main/imgs/article/bayer.webp" alt="bayer" width="100%"><br/><sub><b>bayer</b></sub></td>
<td width="25%" align="center"><img src="https://cdn.jsdelivr.net/gh/ConardLi/assets@main/imgs/article/bodoni.webp" alt="bodoni" width="100%"><br/><sub><b>bodoni</b></sub></td>
</tr>
<tr>
<td width="25%" align="center"><img src="https://cdn.jsdelivr.net/gh/ConardLi/assets@main/imgs/article/vignell.webp" alt="vignelli" width="100%"><br/><sub><b>vignelli</b></sub></td>
<td width="25%" align="center"><img src="https://cdn.jsdelivr.net/gh/ConardLi/assets@main/imgs/article/sottsass.webp" alt="sottsass" width="100%"><br/><sub><b>sottsass</b></sub></td>
<td width="25%" align="center"><img src="https://cdn.jsdelivr.net/gh/ConardLi/assets@main/imgs/article/freddie.webp" alt="freddie" width="100%"><br/><sub><b>freddie</b></sub></td>
<td width="25%" align="center"><img src="https://cdn.jsdelivr.net/gh/ConardLi/assets@main/imgs/article/andy.webp" alt="andy" width="100%"><br/><sub><b>andy</b></sub></td>
</tr>
</table>

---

## 这个 Skill 干什么

`beautiful-article` 把原本枯燥、线性、难以消化的文字材料变成视觉体验更漂亮、阅读节奏更清晰、也更便于审阅和分享的**文章**。它**不是**网页应用生成器 —— 注意力永远在"文章"本身：更好的阅读、更好的节奏、更好的美学。最终交付物是一份自包含、可离线打开的文件（可选随附 PDF），但那是交付细节、不是目标。

适合的场景：

- 把一篇长 URL / PDF / DOCX / Markdown 编辑成一篇**网页长文**
- 决策摘要 briefing、概念解释 explainer、教学步骤 tutorial、复盘 review、方案分析
- 视觉随笔 visual essay、对话 / 访谈 / 播客转写、交互式学习解释器
- 任何时候你希望**比 Markdown 更好的阅读载体** —— 表格、SVG、代码、公式、复制 / 导出按钮一条龙

Skill 本质上是一个**方法论 + 协作 harness**。它附带一个 Vite + React + TypeScript 脚手架，基于 [`reacticle`](https://www.npmjs.com/package/reacticle) 组件协议 —— Agent 不手写裸 HTML / CSS，而是用 prose-first 的语义组件 + 主题约束的 `Raw` 自由层来组合。

---

## 核心思想

- **首先是一篇文章，不是应用** —— 注意力永远在文章。Raw 自由层、SVG、小工具必须服务阅读 / 解释 / 节奏 / 审美，不能喧宾夺主。
- **Source → Plan → Build → Review 小型 harness** —— 每个项目走 6 个有编号的 phase，中间有 3 个硬 checkpoint。
- **`reacticle` 组件协议** —— 语义化的 prose 组件（Hero / Lead / Section / Quote / Callout / Image / Formula / CodeBlock / Table …）+ 一个必须用主题 token（`--ra-*`）的 `Raw` 自由层。
- **主题驱动设计** —— 内置 11 套 authoring profile（`tufte` / `press` / `bayer` / `bodoni` / `vignelli` / `sottsass` / `freddie` / `andy` / `fuller` / `knuth` / `shannon`），每套是给 Agent 看的 Markdown 契约，不是 CSS 文件。
- **默认 100% 信息保留** —— 文章类型自带推荐保留比例（longform `~100%` / briefing `~50%` / visual-essay `~40%` …），用户可一句话覆盖。
- **硬协作 checkpoint** —— Plan、首屏样张、最终交付前 Agent 必须停下来；**每个决策必须逐项独立确认，不允许打包一个"全部 OK 吗"**。
- **默认带封面** —— 一个 3:4 书封式题图位于 TOC 之上，外壳锁死、只能用主题 token、不允许远程图片。
- **PDF 导出可选** —— 主交付物是一份自包含的 HTML 文件；PDF 只在用户在 Checkpoint 3 主动选择时通过零依赖的 `html-to-pdf.sh` 生成。

---

## 工作流

```text
Phase 0  Intake
   │
Phase 1  Source → Markdown      （URL / PDF / DOCX / MD / 文本 → source.md）
   │
Phase 2  Editorial Planning     （一份 plan.md：Brief / Outline / Theme / Assets）
   │
★ Checkpoint 1  Plan            （5 个独立决策逐项确认）
   │
Phase 4  First Spread           （封面 + Hero + 第一节 + 一个代表性视觉块）
   │
★ Checkpoint 2  First Spread    （验收 + 后续开发模式 A/B）
   │
Phase 5  Full Article Build     （单 Agent 顺序 / 多 Agent 并行）
   │
Phase 6  Final Review           （Editorial / Visual / Technical 三视角）
   │
Phase 7  Repair                 （只允许最小切片修复）
   │
★ Checkpoint 3  Delivery        （HTML，或 HTML + PDF，或暂停修订）
   │
Phase 8  Delivery               （article.html，可选 article.pdf）
```

每个项目都有自己的工作区目录，作为 Agent 的**长期记忆**：

```text
<workspace>/
  source/   original.*   source.md   source.<lang>.md（需翻译时）   extraction-notes.md
  plan/     plan.md
  article/  Cover.tsx   Article.tsx   sections/   raw-blocks/   assets/   article.html（产物）
  review/   first-spread-review.md   final-review.md
            （source-review.md 仅复杂源；repair-log.md 仅有修复时）
  index.html  package.json  vite.config.ts  tsconfig*.json   （构建工装）
```

---

## Skill 目录结构

```text
skills/beautiful-article/
├── SKILL.md                            主 Skill 文件（frontmatter name: beautiful-article）
├── manifest.json                       发布清单
├── README.md  /  README.zh-CN.md       本文档
├── references/
│   ├── article-types.md                文章类型路由
│   ├── article-types/                  briefing / dialogue / essay / explainer / full-report
│   │                                    interactive-explainer / longform / review / tutorial / visual-essay
│   ├── information-density.md          保留比例与组件 / 视觉比例的关系
│   ├── plan-template.md                单一 plan.md 模板（Brief / Outline / Theme / Assets）
│   ├── theme-selection.md              主题选择，density 与 theme 解耦
│   ├── layout.md                       版式宽度、TOC 默认值
│   ├── cover.md                        3:4 书封封面指南（5 条自检 + 5 个构图模板）
│   ├── asset-policy.md                 配图策略（none / user-assets / placeholders / ai-generated）
│   ├── component-policy.md             Reacticle 组件契约、prose-first
│   ├── raw-policy.md                   Raw 允许 / 禁止表、token 驱动、自检
│   ├── section-build.md                一节一文件铁律、subagent prompt 模板
│   ├── source-to-markdown.md           各类输入抽取规则 + 5 条自检
│   ├── scaffold.md                     脚手架行为、工作区结构
│   ├── html-output.md                  dev / build / 单文件 HTML 命令
│   ├── pdf-output.md                   html-to-pdf.sh 用法 + print CSS 覆盖
│   ├── review-checklist.md             各阶段 reviewer 清单与 sub-agent prompt
│   ├── repair-policy.md                最小切片修复对照表
│   └── harness.md                      Skill-as-harness 视角
├── theme-profiles/
│   ├── index.json                      主题注册表
│   └── andy / bayer / bodoni / freddie / fuller / knuth / press / shannon / sottsass / tufte / vignelli
├── scripts/
│   ├── scaffold.sh                     一键创建工作区
│   ├── html-to-pdf.sh                  可选 HTML → PDF（headless 浏览器，零 npm 依赖）
│   ├── pdf-print-overrides.css         注入 HTML 的 @media print 覆盖
│   ├── source-to-markdown-markitdown.py  主路径抽取（PDF / DOCX / HTML）
│   └── source-to-markdown.py           轻量 fallback（Markdown / TXT / 简单 HTML）
└── assets/
    └── scaffold-template/              脚手架脚本拷贝的 Vite + React + TS 模板
```

---

## 它是怎么工作的（要点）

### 1. 各节点的质检协议

不同 phase 用不同的质检方式 —— 滥开 SubAgent、滥写 review 文件是首要性能问题，所以 Skill 把规则写明：

| 节点 | 怎么检 | 产物 |
|---|---|---|
| Phase 1 Source（默认） | 主 Agent 内联 5 条 checklist | 无文件 |
| Phase 1 Source（仅复杂 / 低置信源） | Source Reviewer SubAgent（对照 `original.*` diff） | `review/source-review.md` |
| Phase 2 Plan / Checkpoint 1 前 | **主 Agent 内联自查（禁开 SubAgent、禁写文件）** | 无文件 |
| Phase 4 First Spread / Checkpoint 2 前 | First Spread Reviewer SubAgent | `review/first-spread-review.md` |
| Phase 5 每个 Section | Section Reviewer SubAgent —— 以消息返回 pass/fail | 无（不写每节文件） |
| Phase 6 终审 / Checkpoint 3 前 | Editorial + Visual + Technical Reviewer SubAgent | `review/final-review.md` |

### 2. 禁止静默替用户选择

每个 Checkpoint 的每一项决策必须**独立**问 —— Agent 可以推荐，但不能"我已经替你定了 X，不对再说"。Plan Checkpoint 5 项独立决策：文章类型（含推荐保留比例）/ 主题 / 版式宽度 / 配图模式 / 封面开关。

### 3. 文章类型 → 保留比例打包

10 种文章类型都自带推荐保留比例：`longform · ~100%` / `tutorial · ~90%` / `full-report · ~80%` / `explainer · ~80%` / `dialogue · ~80%` / `review · ~70%` / `essay · ~70%` / `briefing · ~50%` / `visual-essay · ~40%` / `interactive-explainer · ~25% 摘录 + 75% AI 重构`。用户可一句话覆盖。

### 4. 一节一文件铁律

每个 Section 都是 `article/sections/NN-*.tsx` 单文件组件。`Article.tsx` 只是 assembler —— 由主 Agent 拥有，负责 import 与排序、跑 typecheck / build、解决主题漂移。这是后续多 Agent 并行的前提。

### 5. 全程主题 token

`Raw` 块必须只用 `--ra-*` 主题 token —— 不允许野生颜色 / 字体。换主题时所有 Raw 块一处生效。每个主题都有一份 Markdown authoring profile，告诉 Agent 在该主题下怎么写、怎么排版。

---

## 创建一个项目

Skill 不预先创建工作区 —— 每个项目自己开。来自 Phase 4 的命令：

```bash
# 默认开封面
bash <path-to-skill>/scripts/scaffold.sh ./my-article --theme=tufte

# 关闭封面
bash <path-to-skill>/scripts/scaffold.sh ./my-article --theme=press --no-cover

# 查看可用主题
bash <path-to-skill>/scripts/scaffold.sh --list-themes
```

脚手架会拉起 Vite + React + TS 工作区，从 npm 装最新 `reacticle`，并放好 `source/ plan/ review/` 三个目录 + `article/Article.tsx` / `article/Cover.tsx` / `article/sections/01-opening.tsx` 三份起点文件。

Phase 5 完成后 Agent 跑构建产出单文件 HTML：

```bash
npm run build           # → article/article.html（CSS + JS 全内联）
```

可选 PDF 导出（仅当 Checkpoint 3 用户选了 HTML + PDF）：

```bash
bash <path-to-skill>/scripts/html-to-pdf.sh
```

---

## 最佳实践

### 推荐

1. **先定文章类型** —— 它的保留比例锚定整个 plan。
2. **信任 harness 的 phase** —— 不要因为"答案显而易见"就跳过 Plan checkpoint。
3. **Raw 块只用主题 token** —— `--ra-*`，禁止裸颜色 / 字体名。
4. **一节一文件** —— 哪怕这一节很短，也要隔离。review 与修复阶段会回报这点投入。
5. **封面要呼应主题 + 文章主旨** —— 不是一个占位渐变。

### 避免

1. ❌ 把 Skill 当成"帮我做个 HTML 页面" —— 交付物是**文章**。
2. ❌ 把多个 Checkpoint 决策打包成一个 yes/no。
3. ❌ Raw 块自带颜色 / 字体（主题漂移）。
4. ❌ 把所有 Section 都写进 `Article.tsx`（杀死 sub-agent 并行）。
5. ❌ 删除 colophon / 封面外壳（这些是契约的一部分）。

---

## 常见问题

**Q1：什么时候不应该用这个 Skill？**
当用户其实想要的是网页应用 / dashboard / 表单 / 原型 / 通用 landing page —— 这些去找 `web-design-engineer`，不是这里。不确定时 Skill 会停下来澄清，而不是默默生成错的产物。

**Q2：是不是总是 100% 信息保留？**
不是 —— 那只是 `longform` 类型的默认值。文章类型决定推荐比例，用户可以在 Checkpoint 1 覆盖。

**Q3：文章语言可以与源材料不同吗？**
可以。如果用户指定的目标语言与源不一致，Phase 1 会先产出地道翻译版 `source/source.<lang>.md`，Phase 2+ 据此编写。

**Q4：如果 Agent 运行时没有 SubAgent / Task 工具怎么办？**
Skill 显式照顾了这种情况：主 Agent 兜底承担 SubAgent 的工作，并在 review 文件首注明"无 SubAgent 环境，主 Agent 兜底"。

**Q5：为什么用 React + Vite + reacticle 而不是裸 HTML？**
因为 Agent 需要一个稳定的、prose-first 的组件契约 —— 它要扛住多 Section 并行写作、主题切换、Raw 自由层这些场景。`npm run build` 时所有依赖会全部内联回单文件 HTML 交付。

---

## 工具要求

Skill 假设 Agent 运行时可以：

- 启动 shell 命令（用于 `scaffold.sh` / `html-to-pdf.sh` / `npm` 构建）
- 在工作区读写文件
- （可选）开启 sub-agent 来跑 First Spread / Section / Final review
- （可选）调用 `MarkItDown`（Python）做高保真 PDF / DOCX / HTML 抽取；不可用时由轻量 fallback 脚本处理 Markdown / TXT / 简单 HTML

---

## 许可证

MIT
