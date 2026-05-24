# Web Video Presentation Skill

**把文章或口播稿做成点击驱动的 16:9 网页演示，并通过录屏产出有电影感视频的 Agent Skill。**

[English](./README.md) · [返回集合首页](../../README.zh-CN.md)

![Web Video Presentation Skill](../../dist/imgs/web-video-presentation-skill.png)

---

## 这是什么？

`web-video-presentation` 帮 Agent 构建一种 Vite + React + TypeScript 演示：它看起来不是传统幻灯片，而更像为录屏设计的视频舞台。每次点击推进一个口播节拍，每一步独占 1920×1080 舞台，进度 UI 平时隐藏，只有悬浮时出现，方便录出干净画面。

它适合：

- 把文章改写成 B 站 / YouTube / 视频号风格口播稿
- 把已有口播稿做成有节奏的网页演示
- 做产品演示、教程、keynote 式讲解、视觉 talk
- 做“动态 PPT，但不要像 PPT”的演示体验
- 在视觉 outline 对齐后，可选合成口播音频

这个 Skill 的核心是**方法论 + 协作流程**。脚手架提供 token、舞台原语、主题和示例，但每个项目仍然应该根据主题重新选择视觉语言。

---

## 核心理念

- **固定 16:9 舞台**：内容写在稳定的 1920×1080 坐标系里，再按视口缩放。
- **一个全局 step 游标**：点击或键盘推进 `(chapter, step)`，游标本地持久化。
- **一步一个想法**：每个节拍独占整屏，不堆叠项目符号。
- **口播节拍驱动结构**：讲述节奏直接映射为视觉 step。
- **隐藏 chrome**：进度控制悬浮才出现，录屏画面保持干净。
- **动效优先**：每一步都需要一个移动的视觉锚点，静态正文是坏味道。
- **主题 token**：视觉属性通过语义 token 驱动，换主题不只是换颜色。
- **可插拔 TTS**：provider-agnostic 音频 runner，**内置 2 个 provider**（MiniMax `mmx-cli` + OpenAI TTS via curl）；往 `tts-providers/` 丢一个 `.sh` 就能换成 ElevenLabs / edge-tts / Azure / Google Cloud / macOS `say` / 任何自部署 TTS。
- **硬 checkpoint**：稿子/主题、outline、音频合成前都必须停下来与用户确认。

---

## 工作流

```text
Phase 1.1  识别用户输入
Phase 1.2  文章 -> 口播稿
   |
Checkpoint A1  稿子、主题、粗略素材计划
   |
Phase 1.3  口播稿 + 原文 -> outline.md
   |
Checkpoint A2  outline 确认 + 开发模式选择
   |
Phase 2    构建 Vite / React / TS 演示
   |
Checkpoint B   询问是否合成音频
   |
Phase 3    可选音频合成
Phase 4    录屏与后期
```

这些 checkpoint 是 Skill 契约的一部分：Agent 不应该从原文一路闷头做到成品。主题选择会影响动效气质，outline 确认能避免章节节奏跑偏。

---

## 内含内容

```text
skills/web-video-presentation/
├── SKILL.md
├── README.md / README.zh-CN.md
├── references/
│   ├── PRINCIPLES.md
│   ├── CHAPTER-CRAFT.md
│   ├── OUTLINE-FORMAT.md
│   ├── SCRIPT-STYLE.md
│   ├── THEMES.md
│   ├── AUDIO.md
│   └── RECORDING.md
├── scripts/
│   └── scaffold.sh
├── templates/
│   ├── index.html
│   ├── vite.config.ts
│   ├── scripts/
│   │   ├── extract-narrations.ts
│   │   ├── synthesize-audio.sh       # provider-agnostic runner
│   │   └── tts-providers/            # 一个文件 = 一个 TTS 后端
│   │       ├── README.md             # 三函数契约 + ElevenLabs / edge-tts / Azure / Google / say 的现成片段
│   │       ├── minimax.sh            # 默认 provider（mmx-cli）
│   │       └── openai.sh             # 内置：OpenAI TTS（curl + OPENAI_API_KEY）
│   └── src/
└── themes/                    # 23 套主题，每套独立设计签名
    ├── midnight-press/
    ├── warm-keynote/
    ├── newsroom/
    ├── bauhaus-bold/
    └── ...                     # 完整列表见 references/THEMES.md
```

---

## 快速上手

把这个 Skill 复制到你的 Agent 会扫描的目录，然后让 Agent 把一篇文章或口播稿做成网页视频演示。

如果要手动脚手架：

```bash
bash skills/web-video-presentation/scripts/scaffold.sh ./presentation --theme=paper-press
```

查看可用主题：

```bash
bash skills/web-video-presentation/scripts/scaffold.sh --list-themes
```

生成的 `presentation/` 是普通 Vite + React + TypeScript 项目。启动后用录屏工具录制 16:9 舞台即可。

---

## 内置主题方向

Skill 内置 **23 套**主题，每套都有独立的设计 DNA —— 不是简单的换色版。下面按底色分两组速览，挑一套接近你目标气质的，或者作为派生新主题的起点。

### 深色（8 套）

- `midnight-press` 暗色印刷 —— 电影感编辑、暖暗底 + 火热橙
- `chalk-garden` 粉笔花园 —— 深石板黑板 + 手写体 + 粉笔黄
- `terminal-green` 终端绿 —— 80 年代磷光终端 + CRT 扫描线
- `blueprint` 工程蓝图 —— 深海军 + 制图青 + 60px 网格
- `dark-botanical` 暗夜植物 —— 暖陶 / 玫粉 / 鎏金叠层，时尚刊物封面
- `neon-cyber` 霓虹赛博 —— 电光青 + 玫红双霓虹，未来派
- `bold-signal` 焦点信号 —— 大橙色焦点色卡 + Archivo Black，pitch deck
- `creative-voltage` 电压创意 —— 饱和电光蓝 + 霓黄 + halftone

### 浅色（15 套）

- `paper-press` 亮色印刷 —— 暖奶油纸 + 火热橙
- `warm-keynote` 暖色 Keynote —— 大圆角 glass slab + 青绿 + 40px 网格
- `newsroom` 报社 —— NYT 大报、奶油 + 墨黑 + 旗红
- `bauhaus-bold` 包豪斯 —— 0 圆角 + 4px 厚边 + 偏移实色阴影
- `sunset-zine` 日落 Zine —— 暖桃 + 玫红 + Fraunces + 虚线剪贴
- `monochrome-print` 黑白印刷 —— 安静精炼，Monocle / Wallpaper 气质
- `vintage-editorial` 复古编辑 —— 俏皮 Fraunces + 几何叠层（圆 / 线 / 点）
- `pastel-dream` 柔光梦 —— 柔粉蓝灰 + 鼠尾草绿 + 右侧 pill 色条
- `split-canvas` 双拼画布 —— 蜜桃 + 薰衣草 50/50 双底色
- `electric-studio` 电光企业 —— 净白 + 电光蓝 + 贴底 4px 蓝条
- `indigo-porcelain` 靛蓝瓷 —— 靛蓝当墨（不是 accent，是字色本身）+ 瓷白
- `forest-ink` 森林墨 —— 森林绿当墨 + 象牙，旧版国家地理感
- `kraft-paper` 牛皮纸 —— 深棕当墨 + 牛皮米 + 紫铜 accent
- `dune` 沙丘 —— 炭褐 + 沙底，几乎无 accent，建筑画廊感
- `swiss-ikb` 瑞士克莱因蓝 —— 极细 200 weight + IKB + 1px 发丝网格

完整 token 契约、每套的设计签名、以及怎么基于现有主题派生新主题（包括 Swiss 黄 / 绿 / 橙变体），见 [THEMES.md](./references/THEMES.md)。

---

## Reference Map

- [PRINCIPLES.md](./references/PRINCIPLES.md)：视频感网页演示的核心原则
- [CHAPTER-CRAFT.md](./references/CHAPTER-CRAFT.md)：章节实现规则与视觉 checklist
- [OUTLINE-FORMAT.md](./references/OUTLINE-FORMAT.md)：outline 必须遵循的结构
- [SCRIPT-STYLE.md](./references/SCRIPT-STYLE.md)：文章转口播稿规则
- [PATTERNS.md](./references/PATTERNS.md)：可选视觉 primitive 配方
- [AUDIO.md](./references/AUDIO.md)：可选口播音频合成流程（provider-agnostic）
- [tts-providers/README.md](./templates/scripts/tts-providers/README.md)：TTS provider 三函数契约 + 内置 2 个 (minimax / openai) + ElevenLabs / edge-tts / Azure / Google / macOS say 的现成代码片段
- [RECORDING.md](./references/RECORDING.md)：录屏与后期注意事项

