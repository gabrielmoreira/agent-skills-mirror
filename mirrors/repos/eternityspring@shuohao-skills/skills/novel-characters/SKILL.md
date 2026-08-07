---
name: novel-characters
version: 1.0.0
description: |
  从小说或短故事里拆出角色表、人物画像、卡通形象提示词、音色提示词，
  并给主要角色出三视图，产出 JSON + Markdown + 可交互的 report.html。
  零依赖、零 API key，用当前会话额度；出图走 codex 内置 $imagegen（可选）。
  Use when asked to 拆小说角色、分析人物、生成角色卡、character sheets from a novel。
allowed-tools:
  - Read
  - Write
  - Bash
  - Task
  - Glob
triggers:
  - novel-characters
  - 拆角色
  - 拆书角色
  - 小说角色
  - 人物画像
  - 角色卡
  - 三视图
  - character sheet from novel
metadata:
  license: Apache-2.0
  requires:
    bins:
      - node          # >= 18，只用标准库，无 npm 依赖
    optional:
      - codex         # 有才出三视图；没有就只交提示词，其余照常
  runtimes:
    - claude-code
    - codex
---

## novel-characters

输入一篇小说/短故事，输出每个角色的：人物画像、卡通形象提示词、音色提示词、三视图。

`{baseDir}` = 本文件所在目录。脚本 `{baseDir}/scripts/novel-characters.mjs`，零依赖，`node` 直接跑。

**运行环境**：Claude Code 和 codex 都能跑。差别只在第 8 步出图——见 `references/turnaround.md`。

---

### Step 1 — 定位输入

用户给文件路径就直接用。直接粘正文的，**先落到一个临时 .txt**——后面校验「引文是否逐字」要拿原文比对，没有原文文件这步就没法做。

确定输出目录：用户指定就用；没指定就用原书同级目录。

### Step 2 — 分块

```bash
node {baseDir}/scripts/novel-characters.mjs chunk <book.txt> <workdir>
```

打印 `{"chunks": N, ...}`。

- **N == 1**：跳过 Step 3，直接在当前会话读原文做第一趟，结果自己写成 `<workdir>/roster-00.json`
- **N > 1**：进 Step 3
- `truncated: true`：明确告诉用户尾部没扫到，别闷着

### Step 3 — 第一趟扫描（仅 N > 1）

**当前环境支持子代理就并发**（Claude Code 的 Task、codex 的 subagent）：每块一个子代理，**所有调用放在同一条消息里**才是真并发。不支持就一块一块串行读，结果一样，只是慢。

每个子代理的任务：
1. 读 `{baseDir}/references/roster-pass.md`，照它执行
2. 读 `<workdir>/chunk-NN.txt`
3. 把 roster JSON 写到 `<workdir>/roster-NN.json`
4. 只回一句「done NN，抽到 X 个角色」

### Step 4 — 归并

```bash
node {baseDir}/scripts/novel-characters.mjs merge <workdir>
```

按名字+别名收敛（`陆行远`/`陆`/`姑娘` 会收敛成一个人），notes 累加、quotes 去重，按出现块数降序——出现的块越多戏份越重。

### Step 5 — 选角

取前 N 位。默认 10，用户说了就听用户的。剩下的角色在最后汇报里提一句「还识别出 X 位没做画像」。

### Step 6 — 第二趟出卡

每个角色一份，同样能并发就并发。

每份任务拿到：
- `{baseDir}/references/profile-pass.md` 和 `{baseDir}/references/schema.md`（读它们，照着做）
- 该角色归并后的 `name` / `aliases` / `notes` / `quotes`
- **同批其他角色的名字**（避免长相声线撞车）

角色卡 JSON 写到 `<workdir>/card-<slug>.json`。

**同时写一段故事摘要**：中文 3–5 句，交代时空背景、核心情境、这几个人聚在一起的由头。短篇直接从原文写；长篇从各块的 roster note 归纳。不剧透结局，不写成推荐语。

合成 `<输出目录>/<书名>-cast.json`：

```json
{ "source": "书名", "summary": "……", "characters": [ ... ] }
```

### Step 7 — 校验 ⛔ 不能跳

```bash
node {baseDir}/scripts/novel-characters.mjs validate <cast.json> <book.txt>
```

检查：结构、`importance` 枚举、**引文逐字**、**出图提示词不含人名**、**语言分工（voice 该中文、image 该英文）**。

**有违规就按报错逐条修，改完重跑，直到通过。** 这四类错模型真的会犯——这套检查就是被真实输出打出来的。

### Step 8 — 三视图（可选，只给 protagonist 和 major）

读 `{baseDir}/references/turnaround.md`，照它的调用契约做。要点：

- **没有 codex 就整步跳过**，只交提示词，后面照常走
- 跑在 codex 里就直接用 `$imagegen`；跑在别处就 shell 调 codex，先按那里的脚本探测版本最高的 binary（旧版会直接报错）
- **一个角色一次调用，绝不批量**
- 必须写明 copy 到 `./images/<slug>-turnaround.png`
- 单个角色失败就跳过，不阻断；最后汇总说明

`supporting` / `minor` 只给提示词不出图。用户明确要求全出就全出。

### Step 9 — 输出

```bash
cd <输出目录>
node {baseDir}/scripts/novel-characters.mjs render <cast.json> --md   > <书名>-cast.md
node {baseDir}/scripts/novel-characters.mjs render <cast.json> --html > report.html
```

`render` 会自动去 `images/<slug>-turnaround.png` 找图，找到就嵌进 report.html。所以**先出图再 render**。

report.html 的样式约定见 `{baseDir}/references/report-style.md`——要改样式先读它，别把它改回通用卡片墙。

最终落地：

```
<输出目录>/
├── <书名>-cast.json
├── <书名>-cast.md
├── report.html          ← 双击就能开
└── images/*.png         ← 有 codex 才有
```

### Step 10 — 汇报

一句话说清：角色数、出图数、报告路径。校验一次没过的话，说明修了什么。有角色出图失败、被截断、或因为没有 codex 而没出图，明确说清楚。

---

## 边界

- 单次上限 24 块（约 33 万字符），超了会明确报 `truncated`，不静默截断
- **输出是中文优先**：`persona` 和 `voice` 的描述字段强制中文，校验器会拦英文。分析英文原著也照样出中文角色卡
- 出图只走 codex built-in `$imagegen`。**不用它的 CLI fallback**（要 `OPENAI_API_KEY`）
- 想要能实时编辑、边跑边看的交互界面，那是另一个东西，不在这个 skill 里

## 自测

```bash
node {baseDir}/scripts/selftest.mjs
```

不调模型、不花额度，覆盖分块 / 归并 / 校验 / 渲染的全部确定性逻辑。改完脚本先跑这个。

## 自带样例

`{baseDir}/examples/渡口.txt` 是一篇短故事，4 个角色，其中货郎全程只有绰号、船夫只被叫过「老伯」——专门用来验别名归并。对应产出 `渡口-cast.json` / `渡口-cast.md` 可以当质量基准，也是校验的自检夹具。
