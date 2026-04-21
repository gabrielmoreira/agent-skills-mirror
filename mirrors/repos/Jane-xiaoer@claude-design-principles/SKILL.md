---
name: claude-design-principles
description: Distilled design judgment from Claude Design's system prompt. Use BEFORE any HTML/UI/slide/prototype/poster/deck task to gather context, avoid AI slop, and produce multiple grounded variations instead of a single guessed "perfect" version. Triggers on design, UI, prototype, slide deck, poster, landing page, wireframe, mockup work.
version: 1.2.0
author: Jane-xiaoer
source: Distilled from the Claude Design system prompt as publicly archived in elder-plinius/CL4R1T4S (https://github.com/elder-plinius/CL4R1T4S/blob/main/ANTHROPIC/Claude-Design-Sys-Prompt.txt). All rights to the original prompt belong to Anthropic. This skill is a learning/interpretation layer, not a redistribution.
---

# Claude Design Principles

> **核心认知**：优秀的设计不是从零猜出来的，是从现有语境里"长"出来的。这个 skill 把 Claude Design 的判断力压缩成可执行 checklist。

---

## 🚦 何时触发（必读）

**只要任务属于以下任一类，必须先加载本 skill 的三条硬规则**（见下），再动手：

- 网页、落地页、组件库
- 幻灯片、演示稿、汇报文档
- App / 网页原型、交互 demo
- 海报、视觉稿、信息图
- 品牌物料、卡片、徽标
- 任何要"看起来不像 AI 生成"的 HTML/SVG 输出

触发词（中英）：设计、design、UI、mockup、prototype、原型、slide、deck、poster、landing、wireframe、mock、界面、页面、演示、演示稿

---

## ⛔ 三条硬规则（违反就算失败）

### 规则 1：**设计前必须先采集语境**

不存在"我脑子里有个好主意就开干"。动手前必须至少拿到**一项**：

- 现有 UI kit / design system 文件
- 品牌 tokens（色板、字体栈、间距、圆角规范）
- 参考站点/产品的截图
- 现有代码库里的组件
- 明确的品牌描述文档（如 Equation 品牌手册）

**没有以上任何一项 → 必须先问 Jane 要**，或一起确定"视觉 DNA 锚点"（比如"像 Aesop 那种米白 + 衬线字 + 留白"）。

> 从零 mock 是 **last resort**，一旦发生会产出通用 AI slop。

### 🆘 如果实在没有 context（last resort 路径）

遇到用户完全没提供 design system、也说不出参考的情况：

1. **先调 `ui-ux-pro-max` skill** 拿 50 种视觉风格 / 21 种调色板 / 50 种字体组合作为弹药库
2. **口头/书面 vocalize 假设**：明确告诉用户"我打算采用 X 字体 + Y 色温 + Z 版式节奏"，**等用户点头**再动手
3. 即使做了，也在文件顶部标注"这是临时视觉假设，请提供实际品牌资产后替换"

**核心立场**：从零 mock 是**最后选项**，产出只能是"勉强及格"的通用风格，绝不出精品。

---

### 规则 2：**一次至少给 3 个方案，基础 → 前卫渐进**

不允许只给一个方案。每次输出至少：

- **方案 A（规范版）** — 严格遵循已有 design system，零冒险
- **方案 B（进阶版）** — 在 system 基础上加一点变化（配色、版式、排版节奏）
- **方案 C（前卫版）** — 允许跳出 system，尝试新隐喻、novel layout、大胆 typography

把这些作为不同幻灯片 / tabs / 并排 cards 展现，让 Jane mix and match。

### 规则 3：**AI Slop 清单全部拉黑**

这些模式一看就是 AI 生成，**禁止使用**（完整清单见 `ai-slop-avoid.md`）：

- ❌ 大面积渐变背景（紫蓝、粉橙等）
- ❌ 圆角容器 + 左边 4px 色块 accent
- ❌ 用 SVG 自己画插画
- ❌ Inter / Roboto / Arial / Fraunces / 系统字体
- ❌ 堆砌 emoji（除非品牌明确用）
- ❌ 为填充而填充的数据、icon、stat
- ❌ 虚构的"用户评价"、placeholder 肖像
- ❌ 每个 section 都加"信任标记" / "客户 logo"

---

## 📐 执行流程（7 步）

```
1. 读需求     → 识别是否触发本 skill
2. 采集语境   → 要 UI kit / 品牌资产 / 参考；没有就问 Jane
3. 提问清单   → 按 question-templates.md 至少问 10 个
4. 定视觉系统 → 口头/书面说清"我将采用 X 字体 + Y 色板 + Z 版式节奏"
5. 构建多方案 → 至少 3 个变体，exposed as tabs/tweaks/slides
6. 自检       → 过一遍 ai-slop-avoid.md 清单
7. 交付       → 打开文件给 Jane 看 + open -R 弹 Finder
```

---

## 🕐 工作流节奏细则

- **早出文件给用户看**：不要憋大招。在第 3 步 plan 阶段就用 HTML 写出**假设 + 上下文 + 设计推理**（像初级设计师在跟 manager 解释思路），加 placeholder 画面，早早 show 给用户。
- **累进构建**：写好 React 组件嵌入 HTML 后**再 show 一次**，末尾附上"接下来打算怎么做"的 next steps。
- **单一主文件 + Tweaks 切换 > 多文件并列**：用户要新版本时，**默认追加到已有主文件作为 Tweak**，不要每次新建一个 v2/v3 文件堆积。
- **只在用户明确要求"留个旧版"时**才 copy 文件保留（`My Design.html` → `My Design v2.html`）。

---

## 🎛️ Tweaks 实时调参模式（可选但推荐）

在 HTML 输出里留一个 JSON 配置块，标记如下：

```html
<script>
const TWEAKS = /*EDITMODE-BEGIN*/{
  "primaryColor": "#D97757",
  "fontSize": 16,
  "radius": 8,
  "dark": false
}/*EDITMODE-END*/;
</script>
```

**作用**：后续要改色/改字号时，我可以精确替换这段 JSON，不用搜遍整份 HTML。Jane 也能自己手改再刷新预览。完整模板见 `starter-components/tweaks-block.html`。

### Tweaks 协议硬规则（3 条）

1. **监听器必须先注册，再发 `__edit_mode_available` 通告**：否则 host 的 activate 消息可能先到，toggle 静默失效。
2. **`__edit_mode_set_keys` 支持 partial update**：只发改了的 key，不要每次全量发送整个配置对象。
3. **`EDITMODE-BEGIN/END` 块必须是合法 JSON**：双引号 key，双引号 string value。host 会 parse 它然后写回文件，格式错误会导致解析失败。

---

## 📊 硬性尺度（不讨论）

| 载体 | 最小字号 | 最小 hit target |
|------|---------|----------------|
| 1920×1080 幻灯片 | 24px | — |
| 打印文档 | 12pt | — |
| 手机端 mockup | 14px | 44px |
| 桌面网页正文 | 16px | — |

- 幻灯片必须带 `data-screen-label` 属性，1-indexed，格式 `"01 Title"`（用户说"第 5 页"指 label `"05"`，不是 array[4]）
- 所有**有播放位置**的内容（幻灯片、视频时间轴）必须把当前位置写入 localStorage，刷新后自动恢复。用户 dev 场景会频繁刷新页面，不保存位置会崩溃他们的工作流。

---

## 🔧 PAI 侧配套 skill（补运行时）

本 skill 只解决"设计判断力"。实际动手时组合：

| 需求 | 用什么 |
|------|-------|
| 视觉方向参考（50 styles / 21 palettes） | `ui-ux-pro-max` |
| 前端结构 / 组件代码质量 | `frontend-design:frontend-design` |
| 启动 dev server + 浏览器验证 | `webapp-testing` / `Browser` MCP |
| HTML → PPTX | `pptx` / `nano-ppt-generator` |
| 插画 / 图标 placeholder 真做 | `nano-image-generator-skill` / `Art` |
| 幻灯片 HTML 结构 | `ppt` / `html-ppt-designer` |

---

## 📎 附件（v1.1.0 扩充）

### 📚 规则文档（需要时按场景加载）

| 文件 | 什么时候读 |
|------|----------|
| `ai-slop-avoid.md` | **每次设计前过一遍** — 25 条反模式 + 替代方案 |
| `question-templates.md` | 任务刚开始、需要列问题给 Jane 时 |
| `typography-system.md` | 决定字号/字重/行高/字体组合时 |
| `color-system.md` | 配色、检查 WCAG 对比度、调 oklch 时 |
| `spacing-rhythm.md` | 决定间距/圆角/阴影/对齐时 |
| `design-heuristics.md` | 排版出 bug、不知道"为什么感觉不对"时 — Gestalt/Fitts/Hick 对照 |

### 🧩 Starter Components（一键复制脚手架）

| 文件 | 用途 |
|------|------|
| `starter-components/deck-stage.html` | 幻灯片舞台（1920×1080 + 键盘导航 + 自适应缩放）|
| `starter-components/design-canvas.html` | 多方案并排画布（规范版/进阶版/前卫版）|
| `starter-components/tweaks-block.html` | Tweaks 实时调参样板 + postMessage 协议 |
| `starter-components/ios-frame.html` | iPhone 16 Pro 设备边框 + 状态栏 + Home Indicator |
| `starter-components/browser-window.html` | 浏览器窗口（Safari/macOS 风格 + 标签栏）|
| `starter-components/animations.html` | 时间轴动画引擎（Stage + Sprite + 50 行核心）|
| `starter-components/android-frame.html` | Android 14 设备框（Material You 风格）|
| `starter-components/macos-window.html` | macOS 风格窗口 chrome（sidebar + main 两栏）|
| `starter-components/react-babel-pins.md` | React/Babel 版本锁定 + styles 命名规则 + 常见报错修复 |

### 🎬 Animations 选择顺序

做视频/motion design 输出时：

1. **优先**：用 `starter-components/animations.html`（Stage + Sprite + timeline + Easing）—— 已经是 50 行极简核心，覆盖 90% 场景
2. **Fallback**：如果需要更复杂的物理动画 / spring 动画 / 拖拽交互，再引入 Popmotion（`https://unpkg.com/popmotion@11.0.5/dist/popmotion.min.js`）
3. **禁止直接上 Framer Motion / GSAP** —— 它们体积过大，且脚手架已经够用

---

## 🧭 决策树：接到任务后先读哪个？

```
接到设计任务
    ↓
 必读：SKILL.md（本文件）三条硬规则
    ↓
 ┌─────────────────────────────────┐
 │  任务类型 → 读对应子文件         │
 ├─────────────────────────────────┤
 │ 动手写代码前  → ai-slop-avoid     │
 │ 要问 Jane    → question-templates │
 │ 定字体       → typography-system  │
 │ 配色          → color-system       │
 │ 定间距/圆角   → spacing-rhythm     │
 │ 做 PC 网页    → 配 browser-window  │
 │ 做 App/手机   → 配 ios-frame       │
 │ 做 PPT/Deck   → 配 deck-stage      │
 │ 多方案展示    → 配 design-canvas   │
 │ 要交互动效    → 配 animations      │
 │ 要实时调参    → 配 tweaks-block    │
 │ 感觉不对说不出哪 → design-heuristics│
 └─────────────────────────────────┘
```

---

## 📁 文件管理规范

- **描述性命名**：`Landing Page.html`、`Dashboard Variants.html`、`iPhone App Prototype.html` —— 不要 `design.html` / `test.html`
- **大修改前 copy 保留旧版**：只有在用户明确要求对比新旧版本时才这么做。命名 `My Design.html` → `My Design v2.html`。
- **默认不要 v2/v3 堆积**：常规迭代用 Tweaks 在主文件切换（见 Tweaks 章节）
- **文件 > 1000 行就拆**：把 React 组件拆成多个 JSX 子文件，主文件 import 组合

---

## 💬 给未来自己的话

设计失败的 90% 来源不是审美不够，是**没问清楚 + 语境不够 + 只给一个方案**。
把这份 skill 当 checklist，每一步都过。
不要把"快速产出"和"好设计"混为一谈。
