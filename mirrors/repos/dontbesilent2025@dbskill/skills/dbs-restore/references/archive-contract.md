<!-- 本文件由 dbskill 统一生成，多个 Skill 共用同一内容，请勿单独修改 -->

# 存档契约

`dbs-save` 写入存档，`dbs-restore` 恢复存档，`dbs-report` 合并存档生成报告。三者共用本文件定义的位置、命名和格式。三个 Skill 的正文只写各自的流程，存档规则以本文件为准。

三个 Skill 各自带一份内容相同的副本（`references/archive-contract.md`），任一 Skill 单独安装也能读取。

## 1. 用户面向的措辞

跟用户对话时不暴露内部术语：

- 「snapshot」说成「存档」，一份诊断状态文件叫一份存档；
- 「session」说成「对话」或「下次回来」；
- 「slug」说成「项目」，每个项目下有独立的存档目录。

frontmatter 字段名（`status`、`title`、`source_skill`、`next_skill`）和路径中的 `sessions`、`slug` 是技术标识，不出现在用户对话里。

## 2. 项目名（slug）

每份存档属于一个项目，用来分隔不同生意的诊断。

- **默认项目名**：取自 `basename $(pwd)`。保留中文、英文字母和数字，英文字母转小写；空格、标点和其他符号替换成 `-`，连续的 `-` 合并为一个，去掉首尾的 `-`。处理后为空时用 `default`。例如「命名讨论」保持为 `命名讨论`，`My Shop (2026)` 变成 `my-shop-2026`。
- **用户显式指定**：使用 `--slug <项目名>`。
- 当前目录是用户家目录或没有明确项目时，项目名为 `default`。

## 3. 存档根目录

先解析存档根目录，后续路径都基于这个结果拼接。

配置文件固定为当前工作目录下的 `.dbs/config.json`：

```json
{
  "version": 1,
  "mode": "default"
}
```

| mode | 存档根目录 |
|---|---|
| `default` | `~/.dbs/` |
| `project` | 当前工作目录下的 `.dbs/` |
| `custom` | `root` 字段指定的目录 |

自定义示例：

```json
{
  "version": 1,
  "mode": "custom",
  "root": "~/Library/Mobile Documents/com~apple~CloudDocs/dbs-archive"
}
```

解析规则：

1. 读取当前工作目录下的 `.dbs/config.json`。
2. 文件不存在，或 `mode` 是 `default` 时，存档根目录为 `~/.dbs/`。
3. `mode` 是 `project` 时，存档根目录为当前工作目录下的 `.dbs/`。
4. `mode` 是 `custom` 时，读取 `root`。展开开头的 `~`；相对路径按当前工作目录解析。
5. 配置无法解析、`mode` 不受支持、`root` 为空，或路径指向 `/`、用户家目录、当前项目根目录时，停止当前操作并说明配置问题。不要到其他位置猜测，也不要静默退回默认位置。

只有 `dbs-save` 的 `location` 命令可以写入配置文件；`dbs-restore` 与 `dbs-report` 只读取配置。

## 4. 目录与文件名

```text
{存档根目录}/sessions/{项目名}/{YYYYMMDD-HHMMSS}-{标题}.md
{存档根目录}/reports/{项目名}/{YYYYMMDD-HHMMSS}-{项目名}.md
```

- `YYYYMMDD-HHMMSS` 使用本地时间。
- 文件名中的标题把空格和标点替换成 `-`，保留中英文字符。
- 同一秒已有同名文件时，追加 4 位随机后缀，例如 `-a7k2`。
- 排序和「最新」一律按文件名前缀的时间判断，不依赖文件修改时间；云同步可能改写修改时间。
- 存档和报告每次新建，不覆盖已有文件。

## 5. 存档文件格式

YAML frontmatter 加 Markdown 正文。

```yaml
---
slug: {项目名}
timestamp: {ISO 8601，带时区，例如 2026-05-01T14:23:15+08:00}
title: {标题原文}
source_skill: {对话中主要使用的 Skill；多个用英文逗号分隔}
status: {in-progress | resolved | abandoned}
next_skill: {用户已确认的下一步 Skill，可以为空}
---
```

`timestamp` 不能写成 `20260501T14:23:15+0800`。生成时优先使用：

```bash
python3 -c "from datetime import datetime; print(datetime.now().astimezone().isoformat(timespec='seconds'))"
```

`status` 的取值与对用户展示的中文：

| 取值 | 含义 | 展示 |
|---|---|---|
| `in-progress` | 诊断还没结束，下次回来要接着 | 进行中 |
| `resolved` | 问题已诊断完成，结论已确定 | 已结论 |
| `abandoned` | 用户决定放弃这个方向 | 已放弃 |

不确定时默认 `in-progress`。

正文固定 6 段，顺序如下：

1. `## 用户主诉`：用户最初的问题，1～2 句，保留原话语气。
2. `## 已得出的结论`：每条一句话。
3. `## 用户已否决的方向`：每条写明否决理由；没有时写「（暂无）」。
4. `## 待验证假设`：没有时写「（暂无）」。
5. `## 已确认的下一步`：用户已经确认时，写做什么、为什么、对应哪个 Skill；尚未确认时写「待定，交回 /dbs 判断」。
6. `## 备注`：任何对以后回访有用的信息。

旧版存档中名为「推荐下一步」的段落，按「已确认的下一步」读取。读取时遇到缺失的字段或段落，使用现有内容继续，不中断。

## 6. next_skill 的含义

- 只有用户已经明确选择下一个 Skill，或明确确认按某个 Skill 继续时，才填写 `next_skill`。
- 上一个 Skill 只给出候选方向、用户尚未确认时，留空，恢复后交回 `/dbs` 判断。
- 恢复存档时，只有用户明确说按上次确认的下一步继续，才进入 `next_skill` 指向的 Skill，并把存档内容作为上下文。
