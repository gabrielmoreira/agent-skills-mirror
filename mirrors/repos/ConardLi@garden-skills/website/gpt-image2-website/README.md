<div align="center">

# gpt-image-2-101

**一份用来"看完就会用" GPT‑Image‑2 的可视化案例库。**

161 条真实可复用的 prompt × 79 个结构化模板 × 17 个大类，配套生图 Skill 与对话调用范例，用一个静态网站全部呈现。

[![License: MIT](https://img.shields.io/badge/License-MIT-1F2937?style=flat-square)](./LICENSE)
[![React](https://img.shields.io/badge/React-19-149ECA?style=flat-square&logo=react&logoColor=white)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-8-646CFF?style=flat-square&logo=vite&logoColor=white)](https://vitejs.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-6-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Companion: garden-skills](https://img.shields.io/badge/Skill-garden--skills-0A6E96?style=flat-square)](https://github.com/ConardLi/garden-skills)

</div>

---

## 它是什么

`gpt-image-2-101` 是一个**纯前端、可静态部署**的 GPT‑Image‑2 案例画廊。它解决一个很具体的问题：

> "新模型出来了，我知道它能画图，但我不知道怎么用它画好图。"

我们把"该写什么样的 prompt"这件事拆成了 17 个大类、79 个可复用模板，每个模板配 1–3 条已经跑过、出图效果稳定的真实案例。打开任意一张图，你能同时看到：

- 高清成品图
- **完整原始 prompt**（一字不动可复制）
- 它属于哪个 [Skill](https://github.com/ConardLi/garden-skills) 模板，模板原文是什么
- 「如果用对话怎么从零调出这张图」的完整对话示例

它既是一份**学习材料**（看着就能学会怎么写 prompt），也是一份可以**直接 fork 当作"私人 prompt 库"**的工程脚手架。

## 截图

> 先放占位。准备 3 张图就够了：Hero / 瀑布流 / 详情页。
>
> ```text
> docs/
> ├─ screenshot-hero.png
> ├─ screenshot-gallery.png
> └─ screenshot-detail.png
> ```

| Hero | Gallery (Masonry) | Case Detail |
| :--: | :--: | :--: |
| ![hero](./docs/screenshot-hero.png) | ![gallery](./docs/screenshot-gallery.png) | ![detail](./docs/screenshot-detail.png) |

## 特性

- **多图浮动 Hero** — 14 张案例图在背景错落漂浮、随机交叉淡入淡出，鼠标驱动视差，遵守 `prefers-reduced-motion`。
- **两种画廊视图** — Masonry 瀑布流 + 按 17 个分类聚合视图，可按关键字 / 模板 / 格式筛选。
- **沉浸式案例详情** — 左侧大图 + 同模板缩略图带，右侧三栏 Tab：成品 prompt、Skill 模板、对话用法。可键盘 ←/→ 翻页。
- **零后端 / 零 API** — 全部数据在构建期编入 `cases.json`，可托管在 GitHub Pages / Vercel / Netlify / 任何静态 CDN。
- **可贡献的数据架构** — 加新案例只需要：丢图 → 写 JSON prompt → 改 `_mapping.json`，热更新会自动重建索引。
- **生产级前端工程** — Vite 8 + React 19 + TypeScript 6，自定义 Vite 插件、ESLint、严格 tsconfig，全程类型安全。
- **图片节流** — `loading="lazy"` + `decoding="async"`，详情页主图 `fetchpriority="high"`，避免一次性下载几百 MB 流量。
- **打包硬化** — 自动排除 `public/` 中的 `.git`、`.DS_Store` 等噪声目录，避免跨平台 `EPERM` 拷贝事故。

## 数据规模

| 项目 | 数量 | 说明 |
| --- | ---: | --- |
| Categories | 17 | UI / 产品 / 海报 / 人物 / 信息图 / 学术 / 技术架构图 / 编辑工作流 / … |
| Templates | 79 | 每个模板对应 [garden-skills](https://github.com/ConardLi/garden-skills) 中的一个 Skill 子模块 |
| Cases | 161 | 每条都包含可直接喂给模型的 prompt + 真实出图 |

数字来自当前仓库的 `src/data/cases.json`，每次 `npm run build:data` 都会刷新。

## 技术栈

| 层 | 选型 |
| --- | --- |
| 视图框架 | React 19 + TypeScript 6 |
| 构建工具 | Vite 8（自定义 Plugin: `safePublicCopy`, `casesDataWatcher`）|
| 路由 | 自研 hash router (`src/lib/router.ts`)，使用 `history.pushState` 避免浏览器自动滚动 |
| 样式 | CSS Custom Properties + 手写动画，无 UI 框架 |
| 字体 | `Instrument Serif` / `Plus Jakarta Sans` / `JetBrains Mono`（Google Fonts）|
| 数据 | 构建期由 `scripts/build-data.mjs` 把分散的 JSON / TXT / Markdown 聚合成两个 manifest |
| Lint | ESLint 10 + typescript-eslint 8 |

## 快速开始

```bash
# 1. clone
git clone https://github.com/<your-org>/gpt-image-2-101.git
cd gpt-image-2-101

# 2. install
npm install

# 3. run dev (会先自动跑 build:data 生成 cases.json)
npm run dev
# http://localhost:5173

# 4. build for production
npm run build

# 5. preview production build
npm run preview
```

> **要求**：Node ≥ 18，建议 Node 20+。
>
> 项目已配置 `predev` / `prebuild` 钩子，所以你不需要手动跑 `build:data`。开发期改 prompt / 加图 / 改模板 MD 也会被监听并自动重建。

## 项目结构

```
.
├─ public/
│  └─ case/                       # 真正的案例资产（PNG / JSON / TXT），按 category/template/idx 组织
│     ├─ _mapping.json            # 索引（哪些模板下有哪些案例）
│     └─ <category>/<template>/   # 每个模板一个目录，1.json / 1.png / 2.json / 2.png …
├─ scripts/
│  └─ build-data.mjs              # 把 case + Skill 元信息聚合成 cases.json / docs.json
├─ src/
│  ├─ components/
│  │  ├─ hero/                    # 大字 Hero、ModelCard 模型详情卡
│  │  ├─ gallery/                 # 画廊主体、瀑布流、分类视图、详情 Overlay
│  │  ├─ skills/                  # Skill 介绍页（隐藏路由）
│  │  └─ shared/                  # Header / Footer
│  ├─ data/                       # 构建产物：cases.json / docs.json（不要手改）
│  ├─ lib/                        # router、data accessor
│  ├─ styles/                     # tokens.css 设计令牌 + globals.css
│  └─ types/                      # 全局 TS 类型
├─ vite.config.ts                 # 自定义插件：safePublicCopy、casesDataWatcher
└─ package.json
```

## 数据流水线

整个站点的"内容大脑"是 `scripts/build-data.mjs`，它把三个数据源聚合成两个客户端 manifest：

```
public/case/_mapping.json                          ┐
public/case/<cat>/<tpl>/<idx>.{json|txt}           ├─►  src/data/cases.json
public/case/<cat>/<tpl>/<idx>.png                  │     └─ 161 cases × 79 templates × 17 categories
.claude/skills/gpt-image-2/references/<cat>/*.md   ┘

.claude/skills/gpt-image-2/SKILL.md                ┐
doc/img2.md                                        ├─►  src/data/docs.json
                                                   ┘     └─ Skill 介绍页内容
```

**触发时机**

| 时机 | 行为 |
| --- | --- |
| `npm run dev` / `npm run build` 之前 | `pre*` 钩子自动跑 `build:data` |
| 开发期改动 `public/case/**` 或 `references/**/*.md` | `casesDataWatcher` Vite 插件 250ms debounce 后增量重建，HMR 同步 |
| 手动触发 | `npm run build:data` |

**生产构建时的拷贝策略**

我们用 `safePublicCopy` 接管了 Vite 默认的 `publicDir → dist` 拷贝，原因是 `public/case/` 是一份带 `.git` 的 snapshot —— 默认 `cp -r` 会因 git pack 文件的只读权限触发 `EPERM`。这个插件会按白名单过滤掉 `.git`、`.DS_Store`、`Thumbs.db` 等。

## 添加 / 修改一个案例

1. 选好分类与模板，比如 `product-visuals/lifestyle-product-scene`。
2. 在 `public/case/<category>/<template>/` 下放：
   - `<n>.json`（推荐）或 `<n>.txt`：完整 prompt
   - `<n>.png`：成品图
3. 编辑 `public/case/_mapping.json`，把新案例追加到对应模板的 `cases` 数组里。
4. 如果引入了新模板：
   - 在 `.claude/skills/gpt-image-2/references/<category>/<template>.md` 写模板说明
   - `_mapping.json` 中相应模板项的 `template_md` 指向它
5. 开发期保存即可，Vite 会自动重建 `cases.json` 并热更新页面。

JSON 案例文件期望字段：

```json
{
  "title": "中文短标题",
  "brief": "一句话告诉读者它在做什么",
  "format": "png | jpg | webp"
}
```

> 实际可生效的字段以 `scripts/build-data.mjs` 与 `src/types/index.ts` 为准。

## 性能 & 体验细节

- **图片懒加载**
  - 画廊缩略图：`loading="lazy"` + `decoding="async"`
  - Hero 拼贴：前 4 张 `eager`，其余 `lazy`
  - 详情页主图：`eager` + `fetchpriority="high"`，打开时优先抢带宽
  - 详情页同模板缩略图条：`lazy`
- **滚动恢复**
  - 路由切换走 `history.pushState`，绕开浏览器空 hash 自动滚顶
  - 进入 / 关闭详情 Overlay 时通过 `useRef` 精确保存与还原 `scrollY`，并在下一帧二次校正
- **动画与可访问性**
  - Hero 入场：错峰位移 + 缩放 + 模糊解除（`tileEnter` keyframes）
  - 案例图轮播：随机选位、避免重复，`@media (prefers-reduced-motion: reduce)` 全部关闭
- **构建产物**
  - JS / CSS 走 Vite 默认压缩；图片资产即时从 `dist/case/` 提供
  - 没有 service worker、没有运行时数据请求：开第一屏 = 一个 HTML + 一个 JS + 视口内的若干 PNG

## Roadmap

- [ ] 自动生成 `webp` 缩略图（多分辨率 srcset）进一步节流
- [ ] 详情页"复制 prompt"一键命令 + 历史浏览缓存
- [ ] 站内全文搜索（FlexSearch / lunr）
- [ ] 暗色模式 / 主题切换
- [ ] i18n（中文 / English 双语切换）
- [ ] 与 `garden-skills` 自动同步（CI 拉取最新 Skill MD）
- [ ] 单测（Vitest）+ 视觉回归（Playwright + Storycap）

欢迎 PR / Issue 一起补完。

## 鸣谢

- 模板与 Skill 设计：[ConardLi/garden-skills](https://github.com/ConardLi/garden-skills)
- 字体：[Instrument Serif](https://fonts.google.com/specimen/Instrument+Serif) / [Plus Jakarta Sans](https://fonts.google.com/specimen/Plus+Jakarta+Sans) / [JetBrains Mono](https://www.jetbrains.com/lp/mono/)
- 灵感来源：OpenAI GPT‑Image‑2 系统报告与开发者社区里的优秀 prompt 实践

## License

[MIT](./LICENSE) © 2026 — 案例图片由 GPT‑Image‑2 生成；prompt 文本与本项目源码以 MIT 协议开放使用。

> **使用说明**：本仓库内的所有 prompt 文本和源码可在 MIT 协议下自由使用、修改与再发布；案例图片仅作 GPT‑Image‑2 模型能力展示，请遵守 OpenAI 使用条款，避免用于侵权 / 误导性 / 受限场景。
