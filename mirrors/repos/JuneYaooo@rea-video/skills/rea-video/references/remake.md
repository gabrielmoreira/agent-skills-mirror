# 复刻

## 各类镜头怎么复刻

- **AI 类镜头**：用原镜头首尾帧加 VLM 提示词，通过 capsule-cinema 生成（会计费，先 `--dry-run`，并征得用户同意）。
- **静态图推拉、静帧**：本地按测得的运动参数重建。
- **代码渲染**：用 Remotion 重建。把报告「代码合成」一节（每镜做法、逐镜动效时间轴、色值）连同 `shots/` 里的元素截图、关键帧条和 `packaging/overlays.ass` 一起交给写代码的人或 LLM；按时间轴的时间和位置写动画，按截图重画图形，图标 / Logo / 插画这类画不出来的直接抠图用。
- **真实素材**：列清单让用户提供。
- **声音**：TTS、BGM（按 BPM / 调性 / 情绪）、音效（按时间点）三条轨分别准备。

**用户自己拍的素材、或在网页上手动生成的视频，拼回原时间线**（不需要 capsule-cinema）：

1. 按分镜表（`report.md` 的镜头号和时长）把素材对应到镜头。一条长素材覆盖多个镜头时，先用 ffmpeg 按动作切开；拿不准对应关系时给用户看截图确认。
2. 写一个 `results.json`：`{"results": {"<镜头号>": {"video": "<素材绝对路径>"}, ...}}`。手动生成的「生成单元」视频覆盖多个镜头时，同样先按单元提示词里的「镜头i（a–b s）」时间切开再填。
3. `rea-video assemble out/ref/breakdown.json <results.json 路径>`：每段素材裁到原镜头时长，没填的镜头暂时用原片占位，声音沿用原片；输出 `remake.mp4` 和左右对比的 `compare.mp4`。告诉用户哪些镜头还是原片占位、声音还要换。

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
