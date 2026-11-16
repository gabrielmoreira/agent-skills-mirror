---
name: obs-archive
description: 将本地文档、视频、图片、演示文稿或外部链接（X/Twitter、视频、互联网文章）下载本地化并归档至 Obsidian 仓库附件目录，同时撰写包含内容解析与内嵌附件/原文的说明笔记
license: Apache-2.0
author: github/cafe3310
depends_on_skill:
  - github/cafe3310/public-agent-skills -> markdown-new
  - github/cafe3310/public-agent-skills -> agent-browser
depends_on_binary:
  - gallery-dl
  - yt-dlp
  - pandoc
  - ffmpeg
  - python3
---

# obs-archive

将用户提供的本地文件（文档、视频、图片、演示文稿）或外部链接（X/Twitter 推文、视频链接、互联网文章）下载并本地化到 Obsidian 仓库的附件目录中，同时阅读解析其内容，在仓库中生成一篇结构清晰、内嵌附件或原文的 Obsidian 归档说明笔记。

## 仓库、归档目录与附件目录约定

1. 默认仓库定位顺序
   - 若用户显式指定了仓库路径，或当前工作目录本身位于某个 Obsidian 仓库内（存在 `.obsidian` 目录），直接使用该仓库。
   - 否则优先查找名为 `obsidian-agi` 的仓库（通过读取系统 Obsidian 注册表 `~/Library/Application Support/obsidian/obsidian.json` 或常见路径如 `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/obsidian-agi`、`~/workspace/obsidian-agi`）。
   - 若仓库根目录下存在 `AGENTS.md`，在写入笔记前先读取并遵守其中的仓库约定。
2. 归档笔记存放目录（`./cafe3310/archives`）
   - 所有通过本技能生成的解析与说明文档，默认统一存放在目标 Obsidian 仓库的 `./cafe3310/archives` 目录下（该目录由本技能维护，内含 `README.md` 说明目录职责与归档规则；若在新仓库首次运行且该目录尚无 `README.md`，应一并创建）。
3. 附件目录解析
   - 严禁硬编码附件目录名称，统一读取目标仓库 `.obsidian/app.json` 中的 `attachmentFolderPath` 配置项确定附件存放路径。
4. 本地文件移动与复制策略
   - 若用户提供的本地文件位于桌面（`~/Desktop`）或下载目录（`~/Downloads`），归档时直接将该文件移动到 Obsidian 附件目录。
   - 若本地文件位于其他目录（如代码仓库、文稿目录），归档时将其复制到 Obsidian 附件目录，保留原路径文件不动。
   - 外部链接抓取产生的临时文件在归档入库时直接移动并清理临时目录。

## 工作流程

### 第一步：探测 Obsidian 仓库与附件配置

运行内置脚本的 `inspect-vault` 子命令，确认目标仓库路径、附件目录路径以及是否存在仓库级 `AGENTS.md`：

```bash
python3 <path_to_skill>/scripts/archive_helper.py inspect-vault [--vault <custom_vault_path>]
```

若返回的 `agents_md_path` 不为空，先读取该文件了解仓库特定规则。

### 第二步：获取与本地化输入源

根据用户提供的输入（本地路径或 URL），创建临时工作目录并运行 `fetch` 子命令：

```bash
python3 <path_to_skill>/scripts/archive_helper.py fetch \
  --input "<url_or_local_path>" \
  --work-dir "/tmp/obsidian_archiver_task"
```

不同类型输入的处理行为：
- 本地文件：校验文件存在性，识别媒体类型，并判断是否处于桌面或下载目录。
- X/Twitter 链接：调用 `gallery-dl --write-metadata` 下载推文原图与文本元数据，同时调用 `yt-dlp` 抓取可能包含的推文视频与 `.info.json`。若遇到需要登录权限的推文，可附加 `--cookies-from-browser chrome` 重试。
- 视频站点链接（YouTube、Bilibili 等）：调用 `yt-dlp` 下载最高画质视频、`.info.json` 描述以及中英文字幕（`.vtt` / `.srt`）。
- 互联网文章链接：优先调用 `markdown-new`（带 `--retain-images`）或 `pandoc` 将网页转换为 Markdown，同时提取正文中引用的所有远程图片并下载至临时目录 `article_images/`。若目标网页存在动态渲染或反爬拦截导致正文为空，改用 `agent-browser` 打开页面提取正文与配图。

### 第三步：阅读资产并提炼简述标题

1. 读取第二步生成的 `fetch_manifest.json` 以及对应的正文、字幕、文档或图片内容：
   - 对文档、PDF、图片：使用文件读取工具直接查看内容。
   - 对演示文稿（`.pptx` / `.key`）或长视频：若无法直接读取二进制，可通过 `ffmpeg` 抽帧、读取字幕文件或转换工具提取关键信息后再做分析。
2. 结合材料内容与用户提问时的补充说明，确定一个简明准确的中文简述标题 `{简述}`（不含特殊路径字符）。

### 第四步：附件重命名入库与文章图片链接重写

运行 `stage-assets` 子命令，将下载的媒体、文章配图或本地文件按规范命名为 `YYYY-MM-DD-HH-{简述}-{序号}.{后缀}`，移入或复制到 Obsidian 附件目录：

```bash
python3 <path_to_skill>/scripts/archive_helper.py stage-assets \
  --vault "<vault_path>" \
  --slug "<简述>" \
  --work-dir "/tmp/obsidian_archiver_task"
```

- 脚本会返回每个附件对应的 Obsidian 内嵌语法 `![[文件名]]`。
- 若输入为互联网文章，脚本会自动将文章 Markdown 中的远程图片链接 `![alt](http...)` 替换为本地附件语法 `![[YYYY-MM-DD-HH-{简述}-img-{序号}.{后缀}]]`，并输出至 `article_localized.md`。

### 第五步：撰写 Obsidian 解析与归档笔记

参考 [references/note-template.md](references/note-template.md)，在 Obsidian 仓库的 `./cafe3310/archives` 目录下（即 `stage-assets` 返回的 `note_suggested_path`）创建名为 `YYYY-MM-DD-HH {站点/来源} - {简述}.md`（例如 `2026-11-08-20 GitHub - pstack Poteto 的提示词编写指南.md`、`2026-11-08-20 X - ...`、`2026-11-08-20 本地文档 - ...`，注意文件名精确到小时，不包含分钟）的笔记。

编写规范：
1. Frontmatter 元数据包含 `title`、`date created`（`YYYY-MM-DD HH:mm`）、`date modified`、`creator`、`background`、`source`（若为外部 URL）与 `references`（填入原始 URL、原始文件路径或关联的 `[[双向引用]]`）。不添加 `#Type-摘录存档` 标签。
2. 正文行文平实克制，直接陈述事实、方法、依据与边界：
   - 少用行内粗体、斜体与反引号，禁止使用「粗体 + 冒号 + 描述」的列表格式，列表统一使用无序列表 `- `。
   - 禁用夸张修辞、企业黑话、「闭环」等空洞名词、「核心是 / 本质在于」等定性断言，以及「三要素 / 四象限」等生造分类词。
3. 章节安排：
   - `## 01. 归档说明与概要`：交代材料来源、作者、发布时间、材料形态以及归档原因。
   - `## 02. 内容解析与说明`：基于对文档、视频、图片、演示文稿或文章的实际阅读，梳理其主要论点、方案设计、关键细节或逻辑脉络。
   - `## 03. 附件与原文存档`：
     - 用 `![[...]]` 内嵌已入库的视频、图片、PDF 或演示文稿附件。
     - 若为互联网文章或长推文，将 `article_localized.md` 中的全文（含已替换为本地 `![[...]]` 的文章配图）完整内嵌在该章节下。
4. 写入完成后，清理 `/tmp/obsidian_archiver_task` 临时目录，并向用户汇报生成的笔记路径、入库附件列表及移动/复制动作。
