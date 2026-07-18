---
name: cut-talking-head
description: 剪辑中文口播原素材：逐词转录、识别口误与重复、生成删词候选、在 Studio 审核后执行可靠物理剪切，并重建剪后字幕。用户说剪口播、处理口误、生成口播基础素材、继续剪口播，或确认卡回传 action=continue_cut / return_cut_review 时使用。不要用于单独安装、单独打开工作台、普通视频编辑或口播分镜成片。
---

# 剪口播

这是 `chengfeng-videocut` 的第一个业务入口。目标产物只有：

```text
source_cut.mp4 + subtitles.srt
```

Skill 做语义判断与编排；产品 Runtime 是项目、Cuts、媒体剪切和 Studio 状态的唯一写入者。

## 0. 每次先做 Runtime 预检

把 `SKILL_DIR` 设为当前 `SKILL.md` 所在目录的绝对路径，不要假定插件安装位置：

```bash
PLUGIN_ROOT="$(cd "$SKILL_DIR/../.." && pwd)"
ENSURE="$PLUGIN_ROOT/scripts/ensure-runtime.cjs"
VC="$PLUGIN_ROOT/scripts/videocut-cli.cjs"

node "$ENSURE" --install-if-missing --json
```

必须把它作为当前任务的内联步骤：

- `ready`：继续本 Skill。
- `missing`：脚本只提示一次“正在从 GitHub Release 安装”，校验完成后自动续跑。
- `runtime_unhealthy`、安装失败或安装后 doctor 失败：报告结构化诊断并停止。
- 预检阶段禁止启动服务、打开 Studio 或创建项目。

详细协议见 [Runtime 与产品契约](../../references/runtime-and-product-contract.md)。

## 1. 接受真实输入

只接受用户给出的真实口播视频或现有真实项目。没有真实媒体就停止；禁止用示例、占位视频或浏览器里的其他项目顶替。

```text
[真实视频]
    |
    v
[逐词转录 + 稳定 wordIds]
    |
    v
[Product project prepare]
```

若 Runtime 尚未提供原视频转录命令，可使用当前环境已经获准的 ASR 能力生成任务目录内的逐词候选；若没有可用 ASR，就明确报告 `missing_transcription_adapter`，不要打开 Studio，也不要伪造 transcript。

准备项目：

```bash
node "$VC" project prepare "$jobDir" \
  --video "$taskLocalVideo" \
  --transcript "$taskLocalTranscript" \
  --json
```

`--video` 与 `--transcript` 必须是任务目录内的真实文件。已有规范项目时先 `workflow get`，不要重复创建 `projectId`。

## 2. 生成并提交删词候选

先读 [语义删除规则](references/semantic-deletion.md)。候选只引用稳定 `wordIds`：

```json
{
  "schemaVersion": 1,
  "cutWordIds": ["word-12", "word-13"],
  "reasons": [
    { "wordIds": ["word-12", "word-13"], "kind": "repeat", "risk": "low" }
  ]
}
```

固定原则：

- 删除只有“删除 / 未删除”两态；AI 原因不形成“建议删除”第三态。
- 口误、重复和残句默认删前保后；长句、整句和分叉重说必须高风险复核。
- 普通停顿不由 Skill 计算。相邻静音合并与 `natural-pause-v2` 由 Product 确定性执行。
- 不直接写 `cut-selection.json`、`project.json` 或事件日志。

启动产品服务时只允许无头启动，不加 `--open`：

```bash
node "$VC" start --host 127.0.0.1 --port 5190 --json
```

用环境提供的后台进程能力运行它。然后先读最新 revision，再提交候选：

```bash
node "$VC" workflow get "$jobDir" --json
node "$VC" cuts set "$jobDir" \
  --file "$proposalFile" \
  --expected-revision "$latestRevision" \
  --json
```

## 3. 到人工审核时才打开 Studio

只有 transcript 与 Cuts 已落盘、工作流已经进入 `cut_review_ready`，才打开同一个 canonical Studio：

```bash
node "$VC" open "$jobDir" --json
```

使用 Codex 内置浏览器打开返回的 URL，并进入 `?view=koubo`。此时停止自动推进，等待用户划词、恢复和保存。

不要：

- 把“打开工作台”当任务第一步；
- 访问旧 `review.html`、8898 或 8899；
- 控制 Studio DOM、直接改媒体元素；
- 创建独立音频轨或占位字幕轨。

## 4. 确认卡与物理剪切

用户表示审核完成后：

1. 重新 `workflow get`，取得当前 `projectId`、项目 revision 与 Cuts revision。
2. 调用本插件 MCP App 的 `show_workflow_confirmation`，传入：

```text
projectId
stage=cut_review_ready
expectedProjectRevision
expectedCutsRevision
selectedCount（可选）
removedDuration（可选）
```

3. 卡片只回传 action，不直接剪切。
4. 收到 `action=continue_cut` 后再次读取最新 revision；若与卡片 revision 不同，停止并让用户核对新编辑。
5. revision 一致时才执行：

```bash
node "$VC" cuts apply "$jobDir" \
  --expected-revision "$latestRevision" \
  --confirmed \
  --json
```

`return_cut_review` 返回同一 Studio；`pause_workflow` 保存状态后停止。

## 5. 重建剪后字幕

物理剪切成功后，必须基于 `source_cut.mp4` 重新转录。先读 [剪后字幕校对](references/subtitle-correction.md)。禁止把原始字幕按删除区间机械拼成最终字幕。

字幕候选通过产品发布：

```bash
node "$VC" workflow get "$jobDir" --json
node "$VC" artifact put "$jobDir" \
  --type subtitles \
  --file "$subtitleProposal" \
  --expected-project-revision "$latestProjectRevision" \
  --expected-artifact-revision "$latestSubtitleRevisionOrNone" \
  --json
```

只有媒体可解码、有音频流、剪后字幕已发布且时间轴有效，才能报告基础素材包完成。

## 恢复与失败

- `revision_conflict`：重新读取状态，说明用户刚才的编辑，不自动覆盖。
- `media_has_no_audio`：保留原素材和上一份有效产物，停止交付。
- `runtime_unhealthy`：不要循环重装。
- 页面关闭但服务仍在：读取 workflow 后从当前状态续做，不新建项目。
- 任何失败都不得把“能预览”说成“已经剪好”。
