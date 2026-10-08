# 运行与项目格式

## 依赖

Python 3.9+；FFmpeg（含 libx264、sendcmd、drawbox）；探测原片需要 ffprobe。macOS 使用 Swift/AppKit 和系统 PingFang 字体渲染。其他平台使用 Pillow，并在样式中提供 `font_title_path`、`font_question_path`，可选 TTC 的 `font_title_index`、`font_question_index`。字体需覆盖字幕实际字符并分别提供粗体和中等字重，不接受缺字方框；交付前必须看实际图。字体不随 Skill 分发。

FFmpeg 从 `--ffmpeg`、`FFMPEG` 环境变量、PATH、可用的 imageio_ffmpeg 依次寻找。ffprobe 通过 `--ffprobe`、`FFPROBE`、PATH 寻找。脚本不自动联网安装。缺工具时优先查宿主运行时；安装依赖遵循当前环境授权。探测不可用时可用用户明确提供的最终参数，不能伪造探测结果。

## 命令

以下命令从 Skill 目录运行；其他目录使用脚本绝对路径。路径始终正确引用。

```bash
python3 scripts/navigation.py doctor
python3 scripts/navigation.py preset-show
python3 scripts/navigation.py probe input.mp4
python3 scripts/navigation.py prepare input.srt prepared.json
python3 scripts/navigation.py validate project.json
python3 scripts/navigation.py render project.json output-v1
python3 scripts/navigation.py preset-save my-blue style.json --default
```

`prepare` 和 `preset-save` 拒绝覆盖目标；`render` 要求不存在的新输出目录。默认预设已存在时更改默认需 Agent 将旧 `config.json` 另存版本后更新，不能用 `preset-save --default` 覆盖它。只保存样式而不设默认可省略 `--default`。

## project.json

示例的 SHA 值需从 `prepare` 的 `source.sha256` 复制。秒值以原片绝对时间为准，结束为不含端点。项目中的字幕路径支持相对于项目文件或绝对路径；导出的快照记录绝对路径便于恢复。

```json
{
  "schema_version": 1,
  "source": {"subtitles": "input.srt", "sha256": "从 prepare 输出取得的真实 SHA256"},
  "target": {"width": 1920, "height": 2560, "nav_height": 280, "fps": "30000/1001"},
  "duration": 60,
  "coverage": [5, 60],
  "subtitle_warnings_reviewed": false,
  "segments": [
    {"chapter": "opening", "title": "开始之前：理清问题", "question": "哪些问题需要先解决？", "start": 5, "end": 20},
    {"chapter": "platform", "title": "第一部分：选择平台", "question": "如何选择适合自己的平台？", "start": 20, "end": 60}
  ]
}
```

- `style` 可直接放完整样式快照；否则读取可选 `preset` 名称，再否则读取用户默认或内置样式。项目快照固定完整 style，不随用户默认变化。
- `source` 允许额外记录原视频路径、大小、mtime、SHA、探测结果和最终设置来源，Agent 继续旧项目时必须核对已记录的原片版本。渲染只消耗字幕，脚本强制验证字幕 SHA。大视频哈希有成本，可先比文件大小/mtime，有改变就重新核对时间。
- `target.height` 是最终画布高度，`nav_height` 是叠加素材高度；都使用正偶数以兼容 H.264/yuv420p。奇数画布需说明编码约束，明确裁切/补边策略，不能悄悄改变用户输出尺寸。
- 帧率用精确分数字符串，29.97 素材先确认是否为 `30000/1001`，不要把数字小数自动等同该分数。
- `coverage` 必须连续，segments 完整覆盖；大章节 id 连续出现，复习独立成章时给独立 id。
- 一条字幕按开始时刻归属板块，时间表写「第一条/最后一条字幕」，不声称是完整句子。边界跨字幕时 Agent 查看上下文确认，可另附完整句意，不能修改原文。
- 源字幕错序会按时间排序；重叠只报警，不改变原时间。人工/Agent 核对后才设置 `subtitle_warnings_reviewed: true`，不要为了运行自动跳过。
- 最终帧边界采用绝对秒 × fps 四舍五入，误差最多半帧；素材放置点也对齐到同一帧网格，使用输出说明的精确时刻。不要逐段累加取整。

## 产物与检查

`navigation-full.mp4`、`project.json`、`timeline.json`、`时间轴.md`、`使用说明.md`、编号文字 PNG、`validation.json`。其余 render-spec、filters、progress、encode.log 为可复现过程记录。

编码先生成静态章节文字，再按真实帧时间驱动进度宽度；章节间隙按大章节时长占比放置。进度区间为 coverage，最后一帧填满。默认黑底蓝色，文本不随进度闪动。

脚本完整解码检查帧数。Agent 另外用 ffprobe 核对尺寸、帧率、音轨（应无音轨），或者查看实际解码日志；抽帧时按帧号选择，核对最长文字、每个章节边界前后及首尾进度。`validation.json` 的 `visual_review_required` 表示还需人工/Agent 视觉检查，编码成功不能替代该步骤。

预览只在用户需要时额外生成并明确标为预览；交付主链接始终是正常速度完整版。适配画面需把条带放到最终画布中检查，而非仅孤立看导航图。

## 自主适配补充

`question` 是兼容字段名，可存当前问题、话题或步骤；空字符串表示只有第一行。每个板块的标题仍必须非空。字幕不足以定位的板块需 `visual_evidence: [{"time": 12.5, "note": "实际看到的操作或场景"}]`，时刻必须位于该板块。整片无对白时 `source: {}` 可用于纯画面分章；应额外记录原视频路径、大小与 mtime，首尾字幕字段为 null，时间表明确显示无对白。不得为通过校验而伪造画面依据。

`source.video` 配合 `video_size`、`video_mtime_ns` 可验证原片版本；变化后先重核，再更新快照。

使用 `doctor` 检查宿主能力。macOS 需要可调用的 Swift/AppKit；其他环境或没有 Swift 时，需要 Pillow 和两种字重的字体文件。在 style 中明确字体路径及 TTC index，字体不随 Skill 分发。字体覆盖范围与许可由使用者核对；实际查看输出才能确认无缺字。

渲染通过 `-vf` 直接传递滤镜，兼容取消旧 filter_script 参数的 FFmpeg。编码要求 libx264、sendcmd 和 drawbox；音频提取需要 aresample。脚本不会自动下载依赖。

音频提取与分段合并命令见 [转写与时间映射](transcription.md)。使用外部转写时记录服务或模型、语言、时间基准和上传授权；这些记录不包含凭证。
