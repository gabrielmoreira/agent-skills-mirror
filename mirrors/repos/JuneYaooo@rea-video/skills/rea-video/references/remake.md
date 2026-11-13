# 复刻

复刻可以用的工具和方式单独列在 `remake-tools.md`，告诉用户有哪些可选时看那个文件。

## 用哪个模型

- 用户指定了视频模型：拆解时加 `--engine <id>`（`rea-video models` 列出可选的 id）；已经拆完的用 `rea-video models <id> --plan out/ref` 改按它重出方案。
- 用户没指定：不用问，直接用默认的那个。
- 把提示词交给用户之前，按 `rea-video models <id>` 打印的写法改写每个生成单元的提示词：时间和镜头怎么分、参考素材怎么指代、台词和不想要的内容怎么写；首帧 / 首尾帧模式下只留运动和运镜。要重画首帧时，图像提示词按所用图像模型的写法改（同一个命令）。
- 选帧、擦字、首尾帧怎么配：`rea-video models keyframes`。

## 各类镜头怎么复刻

- **AI 类镜头**：用原镜头首尾帧加 VLM 提示词，通过 [capsule-cinema](https://github.com/JuneYaooo/capsule-cinema) 生成（会计费，先 `--dry-run`，并征得用户同意）。
- **静态图推拉、静帧**：本地按测得的运动参数重建。
- **代码渲染**：用 Remotion 重建，或在 ChatCut 里生成动效图形。用 Remotion 时，把报告「代码合成」一节（每镜做法、逐镜动效时间轴、色值）连同 `shots/` 里的元素截图、关键帧条和 `packaging/overlays.ass` 一起交给写代码的人或 LLM；按时间轴的时间和位置写动画，按截图重画图形，图标 / Logo / 插画这类画不出来的直接抠图用。
- **真实素材**：列清单让用户提供；拿到后用 `rea-video assemble` 拼回原时间线，或放进 ChatCut 按原片节奏剪。
- **声音**：TTS、BGM（按 BPM / 调性 / 情绪）、音效（按时间点）三条轨分别准备。
- **剪辑包装（字幕、花字、贴纸）**：不进生成。生成模型只出干净的人和画面，包装层最后按「剪辑包装层」的时间轴叠上去，这样字不会被模型画糊，换文案时也只改包装层。
  - 首尾帧上带着原片字幕的，`remake-plan` 的任务里有 `overlays_in_frames` 和警告：先擦掉字再当参考图，否则生成画面会照抄原字幕。
  - 换文案时，花字和贴纸按报告里的「按台词定位」放到新文案的对应句子上，不沿用原秒数；「常驻图层」整段叠一次。

**用户自己拍的素材、或在网页上手动生成的视频，拼回原时间线**（不需要 capsule-cinema）：

1. 按分镜表（`report.md` 的镜头号和时长）把素材对应到镜头。一条长素材覆盖多个镜头时，先用 ffmpeg 按动作切开；拿不准对应关系时给用户看截图确认。
2. 写一个 `results.json`：`{"results": {"<镜头号>": {"video": "<素材绝对路径>"}, ...}}`。手动生成的「生成单元」视频覆盖多个镜头时，同样先按单元提示词里的「镜头i（a–b s）」时间切开再填。
3. `rea-video assemble out/ref/breakdown.json <results.json 路径>`：每段生成素材整段变速塞进原镜头时长（最多快 3 倍、慢 1.25 倍，超出部分再裁），切点和原片对齐，没填的镜头暂时用原片占位，声音沿用原片；输出 `remake.mp4` 和左右对比的 `compare.mp4`。告诉用户哪些镜头还是原片占位、声音还要换。
   - 加 `--overlays`：把测得的字幕 / 花字 / 标题按原样式叠到换掉的镜头上（原片占位的镜头本来就有字，不重复叠）。字体是通用无衬线体，颜色和底框是测量值，可能和原片有出入；贴纸只在 `assemble_log.json` 的 `stickers_to_add` 里列出来，要自己找素材贴。

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
