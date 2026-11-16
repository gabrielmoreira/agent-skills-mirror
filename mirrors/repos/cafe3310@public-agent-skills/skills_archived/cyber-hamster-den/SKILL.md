---
name: cyber-hamster-den
description: 电子仓鼠窝：整合 X (Twitter) 导出 JSON、Discord 频道导出 JSON 与 Obsidian Inbox 日志/剪藏，通过 01-ingest / 02-db / 03-result 三阶段流水线实现跨平台去重、正文提取与多媒体资源本地化归档
license: Apache-2.0
author: github/cafe3310
depends_on_skill:
  - github/cafe3310/public-agent-skills -> markdown-new
depends_on_binary:
  - yt-dlp
  - gallery-dl
  - pandoc
  - ffmpeg
  - python3
---

# 电子仓鼠窝 (Cyber Hamster Den)

将散落在 X (Twitter) Likes 导出文件、Discord「电子仓鼠」频道导出文件以及 Obsidian Inbox 每日剪藏日志中的收藏条目汇总到统一目录，通过增量指纹数据库避免重复下载，并将每条收藏转化为包含本地多媒体文件与还原原文的自包含 Post 目录。

## 目录结构约定

默认在独立数据仓库 `~/workspace/hamster-den/` 下维护三层目录（可通过 `--den-root` 或环境变量 `HAMSTER_DEN_ROOT` 覆盖）：

- `01-ingest/`：原始输入池。直接将导出的 X JSON、Discord JSON 或 Obsidian `📮Inbox` 下的 `.md` 日志文件放入此目录（支持任意子目录或平铺）。
- `02-db/`：状态追踪与去重数据库。
  - `processed_files.json`：记录 `01-ingest/` 中已扫描文件的相对路径、SHA256 哈希与扫描时间。文件未发生变化时自动跳过；文件追加或更新后自动重扫。
  - `url_registry.json`：以归一化后的 `canonical_url`（及推文 Status ID）为键，记录已完成的条目、对应的 `03-result/` 目录名称及出现过的平台来源。
  - `pending_queue.yaml`：增量扫描生成的待处理任务队列，支持预览确认与断点续传（状态含 `pending`、`completed`、`partial`、`failed`）。
  - `progress.jsonl`：运行期追加写入的单行进度日志（Append-only Journal），避免每条任务重写数 MB 的 `pending_queue.yaml`，并在重启时自动回放恢复中断进度。
- `03-result/`：最终产出的仓鼠项目目录。每个条目生成一个名为 `[YYYY-MM-DD-HH] {分类} {标识}` 的独立子目录，内含下载好的视频、原图、`metadata.info.json` 以及还原原文并内嵌本地媒体的同名 `.md` 文档。

---

## 核心工作流

### 阶段 0：初始化与历史数据迁移（首次运行或合并旧目录时执行）

首次建立仓鼠窝，或需要将历史已下载目录合并入库时，运行 `init-and-migrate`（默认使用 `~/workspace/hamster-den`）：

```bash
python3 <path_to_skill>/scripts/hamster_pipeline.py init-and-migrate \
  --den-root ~/workspace/hamster-den \
  --migrate-from "<vault_path>/cafe3310/📮Inbox/📮下载内容"
```

- 脚本会将历史下载目录移动至 `03-result/`，解析每个目录内的 `.md` 与 `metadata.info.json`，将所有历史 URL 与推文 ID 登记到 `02-db/url_registry.json` 中（状态记为 `completed`）。

### 阶段 1：增量扫描 `01-ingest/` 并生成去重队列

当向 `01-ingest/` 放入新的导出文件或日志后，运行 `scan`：

```bash
python3 <path_to_skill>/scripts/hamster_pipeline.py scan \
  --den-root ~/workspace/hamster-den
```

三种输入格式的自动识别与解析规则：
1. **X (Twitter) 导出 JSON**：识别顶层数组结构，提取 `id`、`full_text`、作者信息以及 `media[].original` 高清直链；自动检测同一批次中作者本人的连续自回复（如在回复中补充 Prompt）并合并正文。
2. **Discord 频道导出 JSON**：识别 `messages` 数组：
   - 若单条消息内包含多个外部链接，拆分为多个独立条目，共享该条消息中的个人评语（`user_note`）。
   - 若某条含链接消息之后 5 分钟内紧跟一条无链接、无附件的纯文字消息，自动将该文字消息合并为前一条链接的 `user_note`。
   - 提取 `embeds` 中的 OpenGraph 预览图与 `attachments` 附件直链。
3. **Obsidian Inbox Log / Web Clipper Markdown**：
   - 若 Frontmatter 含 `source` / `url`，按单篇剪藏文章解析，提取正文与外链图片。
   - 若为每日 Inbox 日志，按顶级条目边界切分（保留提示词内嵌 `---`），**仅识别**包含 `* Note` / `* time:` / `* source:` 且带有有效外部链接的结构化条目，提取链接、分类后缀、附带正文与 `![[...]]` 本地图片引用；跳过无链接的纯文字/纯图片随笔以及未补全格式的非结构化条目。

扫描完成后，脚本会过滤掉已在 `02-db/url_registry.json` 中完成的 URL，合并本次跨平台重复收藏的条目，并将待处理清单写入 `02-db/pending_queue.yaml`。

### 阶段 2：执行内容抓取与多媒体本地化（输出至 `03-result/`）

消费 `02-db/pending_queue.yaml`，按条目类型拉取内容并落地到 `03-result/`。注意：抓取 X (Twitter) 或海外站点前，需确保已配置环境中的代理设置：

```bash
python3 <path_to_skill>/scripts/hamster_pipeline.py process \
  --den-root ~/workspace/hamster-den \
  --workers 4
```

如本次队列包含 Obsidian Inbox 本地附件图片（`![[...]]`），可额外传入可选参数 `--vault-root "<vault_path>"` 以便从原库 `_attachments` 拷贝对应图片。

支持的参数与断点续传特性：
- `--workers <N>`：并发下载线程数（默认 `4`；对 `yt-dlp` / `gallery-dl` CLI 抓取自动加锁串行限流防 429）。
- `--retry-failed`：重跑队列中状态为 `partial`（部分媒体因网络瞬断未下完）与 `failed` 的条目。
- `--limit <N>`：单次最多处理的条目数。
- `--checkpoint-every <N>`：每完成多少条全量刷盘一次 `pending_queue.yaml`（默认 `25`），单条完成时实时追加 `02-db/progress.jsonl`，收到 `SIGINT`/`SIGTERM` 或退出时自动合并刷盘。
- 文件级与字节级续传：已下载成功的非空图片/视频在重跑时直接跳过；大体积视频下载至 `.part` 临时文件并支持 `HTTP Range` 断点续传，遇到 `429` 或 `5xx` 按 `2s -> 4s -> 8s -> 16s` 退避重试。

不同目标类型的本地化行为：
- **X (Twitter) 导出条目**：直接通过 HTTP 下载 `media[].original` 中的原图与最高画质 `.mp4`，展开正文中剩余的 `t.co` 外链，无需重复调用 `yt-dlp` 请求 X 网页。
- **来自 Discord / Inbox 的 X 或视频链接**：调用 `yt-dlp`（带 `--write-info-json`）抓取最高画质视频，配合 `gallery-dl` 下载多图推文原图与文本元数据。
- **GitHub 仓库链接 (`github.com/<owner>/<repo>`)**：拉取仓库元数据（描述、Stars、Language、Topics）与默认分支 `README.md` 原文，将 README 中的相对/远程配图下载至当前目录并重写为 `![[readme_01.png]]` 本地嵌入。
- **arXiv 论文链接 (`arxiv.org/abs/<id>`)**：通过 arXiv API / Meta 标签提取论文标题、作者列表与完整 Abstract 正文。
- **个人网站 / 技术文章 / Showcase**：下载 OpenGraph 封面图（`og_cover`），调用 `markdown-new` 或 `pandoc` 将网页正文转换为 Markdown，同时下载正文中引用的远程图片并重写为本地 `![[web_img_01.jpg]]` 嵌入。

### 阶段 3：清理 Obsidian `📮Inbox` 中已入库内容

当确认条目已在 `02-db/url_registry.json` 登记为 `completed` 后，可用 `prune-inbox` 清理 Obsidian `cafe3310/📮Inbox` 中已迁移的内容。该命令**默认执行 dry-run 预览**，先列出待移除文件、需按 `---` 块级裁剪的每日日志、可选的旧下载清单及未被引用的附件，经用户确认后再传 `--apply` 执行：

```bash
# 1. Dry-run 预览待移除列表
python3 <path_to_skill>/scripts/hamster_pipeline.py prune-inbox \
  --den-root ~/workspace/hamster-den \
  --vault-root "<vault_path>" \
  --include-manifests

# 2. 确认无误后实际移除
python3 <path_to_skill>/scripts/hamster_pipeline.py prune-inbox \
  --den-root ~/workspace/hamster-den \
  --vault-root "<vault_path>" \
  --include-manifests \
  --apply
```

说明：
- 单篇剪藏笔记（frontmatter 含 `source`/`url`）若对应 URL 已入库，整篇列入待删除；每日日志按 `---` 分块判断，若全块已入库则整篇列入待删除，若仅部分块已入库则保留未入库块与纯文字随笔，仅剔除已入库块。
- 仅当某个 `_attachments` 图片不再被任何保留中的 Inbox 条目及 vault 其他笔记引用时，才会被列入待删除附件列表。
