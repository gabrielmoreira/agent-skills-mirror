---
name: short-drama
description: 基于文件系统初始化、继续和交付短剧或漫剧项目，并提供面向创作者的本地 Dashboard；也负责项目级制作形态、视觉方向和 Look Development 路由。用户提出“创建/继续短剧项目”“看进度/下一步”“做 Look Development”“打开 dashboard/短剧创作台”“导出制作资料”，或任务跨多个环节而需要判断负责技能时使用；明确的写作、资产、提示词、分镜或审查请求由对应子 skill 直接处理。
license: MIT
---

# 短剧创作路由

本技能负责找到项目、显示当前状态并把工作交给正确的创作技能，不代写各阶段内容。

## Quick Start

先离线确认本技能被单独复制后仍能初始化、读取和保护项目路径：

```bash
python3 {技能目录}/scripts/selftest.py
python3 {技能目录}/scripts/project_tool.py init ./my-drama --title "示例短剧"
```

创作者可读内容使用 `short-drama.json#/language`；交给图片或视频生成器的提示词正文使用
`#/format/prompt_language`。两者互不推断，详见
[contract-and-ownership.md](references/contract-and-ownership.md#output-language-contract)。

## 每次请求的起点

1. 使用用户给出的路径，或从当前目录向上寻找最近的 `short-drama.json`。
2. 运行 `status`，只读完成当前任务所需的直接输入，不批量加载整个项目。
3. 按用户眼下要完成的工作路由；未安装的阶段技能只影响对应路由，不阻断其他工作。
4. 明确的单阶段任务直接交给独立安装的对应技能，按创作者要的那一步做。

统一预检见 [runtime-preflight.md](references/runtime-preflight.md)，创作入口见
[creator-workflow.md](references/creator-workflow.md)，所有权见
[contract-and-ownership.md](references/contract-and-ownership.md)。

## 意图路由

| 创作者意图 | 路由 |
|---|---|
| 开发点子、系列承诺、改编和分集地图 | `$short-drama-develop` |
| 导入已有多集完整剧本/散稿并生成或补分集地图 | `$short-drama-develop` 按文件实际结构建立索引，每次只读当前集并续跑 |
| 判断长篇是否值得改、建立原文索引 | `$short-drama-novel-analyze` |
| 写或改单集契约、节拍、剧本 | `$short-drama-write` |
| 拆人物、造型、地点、道具和状态 | `$short-drama-assets` |
| 写人物、地点、道具和 Look Development 图片提示词 | `$short-drama-image-prompts` |
| 做覆盖设计、镜头和冻结关键帧 | `$short-drama-storyboard` |
| 写动作、表演、运镜、声音视频提示词 | `$short-drama-video-prompts` |
| 写主题曲/配乐意图或校验时间线音乐规格 | `$short-drama-video-prompts`，歌词必须由创作者提供并接受 |
| 按已确认规格实际生成图片、视频、TTS 或时间线音乐 | `$short-drama-produce` 先展示本次 job，得到明确确认后才执行 |
| 定制作形态、视觉方向或 Look Development 路径 | `$short-drama` |
| 校验、审稿或发修订请求 | `$short-drama-review` |
| 打开创作台、看内容和进度 | `$short-drama dashboard` |

用户的明确意图优先。Look Development 是可选分支；资产图片提示词和分镜在资产确认后可以
并行，不互相等待。需要把已接受的视觉方向变成可比较的代表帧时，读
[look-development.md](references/look-development.md)。

**产物可以直接入场**。 上游的可选环节缺失不构成阻塞：现成剧本可直接进入资产；已接受资产
可直接进入资产图片提示词；已接受剧本加资产可直接进入分镜；已接受镜头与关键帧可直接进入
视频提示词。只补建对应技能拥有的、确实缺少的必要产物，绝不倒补虚构的创作简报或系列大纲。

**请求含糊时不要追问技术细节**。 遇到"帮我把这集做完"这类请求，先展示当前的创作者可读
状态，再给出不超过三个有意义的动作，优先能解开当前交付阻塞的那个；不要拿 schema、事务或
存储格式去问创作者。

## 有界续跑

全链预览或“继续”每轮只授权一个 owner 的一个有界工作单元。写作、资产、图片提示词、分镜和
视频提示词按各自「每轮的工作单元」分批工作；完成当前批次后报告已覆盖范围、剩余范围与
下一步，并把控制权交还创作者。下一阶段、审查和生产各自需要明确的后续请求；生产还要先展示
准确 job 并取得确认。

审查尽量交给没有参与该版本创作的 reviewer，以减少自证偏差；运行环境不支持隔离上下文时，
如实标注为自检即可。CLI 只记录 verdict、reviewer 标签和备注，不收集或伪造上下文证明。
Reviewer 给出证据和修改请求，内容仍由原 owner 修改。

## 初始化

没有项目且用户要初始化时：

1. 确定标题、项目语言、提示词语言、画幅和路径；集数或时长未知就留空。
2. 运行 `init` 建立最小目录和空状态，不覆盖现有文件。
3. 将制作形态与视觉方向保持为 `unset`，告诉创作者下一个最有用的选择。
4. 创作者定下形态、方向、播放面或集长目标后，把这条决定发布并接受为一条创作者决策记录，
   再用 `set-authority` 写回 `short-drama.json`，让下游读到已 `accepted` 的值。

初始化不自动生成故事、剧本或资产设定。

## 本地 Dashboard

Dashboard 是项目内容的轻量展示与有限文本编辑层，核心能力仍在各 skill 中。当用户调用
`$short-drama dashboard` 时：

1. 项目存在时读取 `status`；浏览普通目录时直接使用该目录。
2. 项目内启动时用项目根作为 workspace；否则使用用户给出的容器目录或当前目录。
3. 从本技能安装目录运行：

   ```text
   python3 <short-drama-skill-dir>/scripts/dashboard_server.py --workspace <workspace> --port 0 --open
   ```

4. 回报脚本打印的完整回环地址与停止方式，并保持进程运行。

Dashboard 只读取 workspace 内的文件；密钥、生产 adapter 与工作流编排都在它之外。它按项目
和剧集展示正文、结构化卡片以及已有图片/音频/视频；保存只表示保存文件，不代表创作者确认。
每次启动使用独立本机会话，项目 API 只接受该会话。参数与安全边界见
[lifecycle-commands.md](references/lifecycle-commands.md#dashboard-启动)。

## 项目命令

从本技能安装目录调用 `scripts/project_tool.py`：

| 命令 | 用途 |
|---|---|
| `init` | 初始化最小项目 |
| `status` | 显示项目与产物状态 |
| `publish` | 原子发布一项产物并记录它的直接输入 |
| `accept` | 记录创作者接受或拒绝当前版本 |
| `review` | 记录当前版本的复核结论 |
| `set-authority` | 把已接受的创作者决策写回制作形态、视觉方向、播放面或集长目标 |
| `package` | 打包当前已确认且复核通过的文本/JSON |
| `verify` | 用交付校验和检查打包结果是否被改动 |

完整示例见 [lifecycle-commands.md](references/lifecycle-commands.md)。单文件发布用临时文件与
原子替换完成。

## 状态与修订

对创作者只使用六种状态：

- `draft`：尚未发布；
- `needs_confirmation`：等待创作者决定；
- `accepted`：创作者已接受；
- `revise`：创作者或 reviewer 要求修改；
- `approved`：当前版本已确认且复核通过；
- `update_needed`：输出或某个直接输入已经变化，需要重新发布。

状态在读取时核对当前文件，不把过期传播写回整个项目。修订时只说明负责技能、语义变化、
直接受影响的产物和下一步；重新发布会清除该产物旧的接受与复核结果，不触碰无关产物。
除非诊断需要，不向创作者显示内部 hash 或原始状态文件。

## 交付

先由 `$short-drama-review` 复核，再用 `package` 打包。包内只收录明确选择的、当前状态为
`approved` 的文本和 JSON，并记录有意省略项；二进制媒体、非公开输入、机器状态、绝对路径、
凭据和未批准草稿不进入文本交付包。`verify` 检查清单、校验和及未登记新增文件。

## 边界

- 图片、视频和 TTS 生产只由 `$short-drama-produce` 在展示准确 job 并取得本次明确确认后执行；
  其他技能不直接调用生成服务。
- 运行时不检索外部或非公开生产来源。
- 不把别处案例提升为项目定律。
- 语义冲突不静默修复；不明外部改动由创作者选择保留或重做。
