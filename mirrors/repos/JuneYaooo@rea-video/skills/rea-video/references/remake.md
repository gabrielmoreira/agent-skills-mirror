# 复刻

复刻可以用的工具和方式单独列在 `remake-tools.md`，告诉用户有哪些可选时看那个文件。

## 照着做

报告「自己复刻」开头先判断视频类型（口播、桌拍、AI 短片、卡点混剪等 15 类，按画面类别占比、实拍形式、声音类型和剪辑节奏推出来），再按这类视频的制作顺序列步骤。每一步只写这条原片测出来的数（机位、布光、剪辑节奏、字幕样式、声音来源、生成单元）和本工具的文件和命令，没测到的就不写。用户自己做时先给这部分；类型判错了就说明，按正确类型的顺序给。不要往里加测量之外的经验数字。

## 先跑一条命令

`rea-video remake out/ref`：代码渲染镜头重画（自动跑 `code-remake`），静图按测得的运动重建，`remake/results.json`（`remake-run` 生成的）和 `remake/mine.json`（用户给的或网页上手动生成的，格式 `{"results": {"镜头号": {"video": "绝对路径"}}}`）里的镜头剪进去，其余原片占位，按原时间线拼好，叠回字幕。`remake/status.md` 逐镜写了现在是怎么做的、还要做什么。每拿到一个新镜头就写进 `mine.json` 再跑一次。下面各节是每类镜头的细节。

## 用哪个模型

- 用户指定了视频模型：拆解时加 `--engine <id>`（`rea-video models` 列出可选的 id）；已经拆完的用 `rea-video models <id> --plan out/ref` 改按它重出方案。
- 用户没指定：不用问，直接用默认的那个。
- 把提示词交给用户之前，按 `rea-video models <id>` 打印的写法改写每个生成单元的提示词：时间和镜头怎么分、参考素材怎么指代、台词和不想要的内容怎么写；首帧 / 首尾帧模式下只留运动和运镜。要重画首帧时，图像提示词按所用图像模型的写法改（同一个命令）。
- 选帧、擦字、首尾帧怎么配：`rea-video models keyframes`。

## 各类镜头怎么复刻

- **AI 类镜头**：用原镜头首尾帧加 VLM 提示词，通过 [capsule-cinema](https://github.com/JuneYaooo/capsule-cinema) 生成（会计费，先 `--dry-run`，并征得用户同意）。
- **静态图推拉、静帧**：本地按测得的运动参数重建。
- **代码渲染**：先跑 `rea-video code-remake out/ref`。它按拆片包 `frames/` 里每个场景的采样点或抠图、测得的运动和背景光，写出 `out/ref/code/`（`spec.json` 每个场景一项、`render.py` 渲染器、`overlays.ass` 文字），逐场景把量和亮度对齐原片，渲染出 `code/remake.mp4`，再和原片打分。
  - 往下改都从这一版开始：先改 `spec.json` 里的数（粒子数 `count`、大小 `dot`、亮度 `gain`、运动 `motion`、背景光 `glow`）；要换成新形状，就把 `points` 换成自己的点文件；要做原片没有的效果再改 `render.py`，或照着它改写成 Remotion / Three.js。改完重跑同一条命令，改过的 `spec.json` 会保留，`--reset` 才会从头重建。`python code/render.py --frame 12.5` 可以只出一帧来看。
  - 按输出里 `lowest_scenes` 的 `advice` 改，先改分数最低的场景，对照 `code/compare/compare_worst.jpg` 看。
  - 报告「代码合成」一节的每镜画面描述、`shots/` 里的元素截图和关键帧条，用来补工具测不到的东西：标注怎么入场、图形是什么含义。
- **真实素材**：列清单让用户提供；拿到后写进 `remake/mine.json` 再跑 `rea-video remake`，或放进 ChatCut 按原片节奏剪。
- **表演和情绪**：报告「表演与情绪」一节逐镜写了情绪、表情、动作和语气，生成单元的提示词里已经带上表情和动作。改写提示词时保留看得见的表情和动作，不要换成「开心」「难过」这类词，也不要把幅度写大；有台词的镜头先做有语气的配音，再让画面跟着声音演。
- **声音**：TTS（按脚本表里每句的语气）、BGM（按 BPM / 调性 / 情绪）、音效（按时间点）三条轨分别准备。
- **剪辑包装（字幕、花字、贴纸）**：不进生成。生成模型只出干净的人和画面，包装层最后按「剪辑包装层」的时间轴叠上去，这样字不会被模型画糊，换文案时也只改包装层。
  - 首尾帧上带着原片字幕的，`remake-plan` 的任务里有 `overlays_in_frames` 和警告：先擦掉字再当参考图，否则生成画面会照抄原字幕。
  - 换文案时，花字和贴纸按报告里的「按台词定位」放到新文案的对应句子上，不沿用原秒数；「常驻图层」整段叠一次。

**用户自己拍的素材、或在网页上手动生成的视频，拼回原时间线**（不需要 capsule-cinema）：

1. 按分镜表（`report.md` 的镜头号和时长）把素材对应到镜头。一条长素材覆盖多个镜头时，先用 ffmpeg 按动作切开；拿不准对应关系时给用户看截图确认。
2. 写进 `out/ref/remake/mine.json`：`{"results": {"<镜头号>": {"video": "<素材绝对路径>"}, ...}}`。手动生成的「生成单元」视频覆盖多个镜头时，同样先按单元提示词里的「镜头i（a–b s）」时间切开再填。
3. `rea-video remake out/ref`：每段素材整段变速塞进原镜头时长（最多快 3 倍、慢 1.25 倍，超出部分再裁），切点和原片对齐，没填的镜头暂时用原片占位，声音沿用原片；输出 `remake/remake.mp4`、左右对比的 `remake/compare.mp4` 和 `remake/status.md`。告诉用户哪些镜头还是原片占位、声音还要换。只想拼不想重画代码镜头时用 `rea-video assemble out/ref/breakdown.json <results.json 路径>`。
   - 字幕叠回（`remake` 默认叠，`assemble` 要加 `--overlays`）：把测得的字幕 / 花字 / 标题按原样式叠到换掉的镜头上（原片占位的镜头本来就有字，不重复叠）。字体是通用无衬线体，颜色和底框是测量值，可能和原片有出入；贴纸只在 `assemble_log.json` 的 `stickers_to_add` 里列出来，要自己找素材贴。

**自动生成的限制**：`remake-plan` 和 capsule-cinema 目前还是一个镜头调一次模型；报告里「生成单元」的多镜头提示词要用户手动贴到支持多镜头的模型（如即梦 / Seedance 2.5）上用。向用户说明这一点，并给出两种做法的调用次数。

## 对接 capsule-cinema

生成要用 capsule-cinema 自己的 Python 环境。`rea-video remake-run` / `capsule-draft` 会自动找 `$CAPSULE_CINEMA_PYTHON` 或 `<capsule-root>/.venv/bin/python`，也可以用 `--python` 指定。

```bash
CC=$CAPSULE_CINEMA_ROOT   # capsule-cinema 仓库路径
rea-video remake-plan out/ref/breakdown.json --capsule-root $CC --engine seedance2.0   # 也可以 --mode image_to_video / --labels ai_video
rea-video remake-run out/ref/remake/jobs.json --dry-run      # 先给用户看任务和费用
rea-video remake-run out/ref/remake/jobs.json                # 用户确认后再跑
rea-video assemble out/ref/breakdown.json out/ref/remake/results.json                   # 拼回原时间线 + compare.mp4
rea-video capsule-draft out/ref/breakdown.json --capsule-root $CC --capsule-name xxx [--write-capsule]
```

- jobs.json 里每个任务的 `executor` 取值：
  - `capsule_cinema`：调模型生成
  - `local_ffmpeg`：静态图本地重建
  - `keep_original`：保留原片，比如代码渲染、录屏、真实素材
- `user_assets`：这个镜头需要用户提供的真实素材。生成结果只是近似，要提醒用户。
- `capsule-draft`：通过 capsule-cinema 自带的 `tool_factory` 注入拆解结果，不改 capsule-cinema 代码，生成的配方草稿默认是 `review_required`。
