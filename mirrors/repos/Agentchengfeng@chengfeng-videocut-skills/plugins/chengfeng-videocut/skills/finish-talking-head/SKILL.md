---
name: finish-talking-head
description: 把口播基础素材制作成完整成片：生成并审核分镜、动画和总时间线，随后导出与验收 final.mp4。用户说口播成片、口播分镜、口播动画、导出口播视频、继续口播成片，或确认卡回传 action=continue_finish_storyboard / continue_finish_animation / continue_finish_timeline 时使用。不要用于原始删词、单独安装、单独打开工作台或普通 HyperFrames 视频。
---

# 口播成片

这是 `chengfeng-videocut` 的第二个业务入口。它消费已审核的基础素材包，产出：

```text
source_cut.mp4 + subtitles.srt
               |
               v
      storyboard / animation / timeline
               |
               v
        final.mp4 + verification.json
```

## 0. 每次先做 Runtime 预检

```bash
PLUGIN_ROOT="$(cd "$SKILL_DIR/../.." && pwd)"
ENSURE="$PLUGIN_ROOT/scripts/ensure-runtime.cjs"
VC="$PLUGIN_ROOT/scripts/videocut-cli.cjs"

node "$ENSURE" --install-if-missing --json
```

预检是本 Skill 内部步骤，不是第三个 Skill。缺失时提示一句并安装；失败时停止。预检和无头生成阶段都不得打开 Studio。详细协议见 [Runtime 与产品契约](../../references/runtime-and-product-contract.md)。

## 1. 检查基础素材包

```bash
node "$VC" workflow get "$jobDir" --json
```

必须同时存在并通过产品检查：

- `source_cut.mp4`：真实剪后视频，含音频流；
- `subtitles.srt`：基于剪后视频重建的规范字幕；
- 同一个 `projectId` 与当前 revision。

若缺失，切换到 `$cut-talking-head` 完成前置剪辑，再以同一个 `projectId` 恢复本 Skill。不要新增“口播工作台”总控入口，也不要创建第二个项目。

## 2. 读取项目配置

比例、动画风格与额外要求必须来自当前项目状态；不要读取所有项目共享的可变全局默认值。用户尚未选择时，只询问会实质改变成片的必要信息。

```json
{
  "aspectRatio": "4:3",
  "animationStyle": "xiaohei",
  "requirements": "保留真实产品操作画面"
}
```

用户确认配置后，用最新 revision 执行 `start-final`。每一步都重新读取 revision，不能连续复用旧值。

## 3. 分镜候选 → 审核

先读 [分镜规则](references/storyboard-rules.md)。按字幕语义分段，候选段落绑定稳定 `wordIds`，再通过产品校验发布：

```bash
node "$VC" artifact put "$jobDir" \
  --type visual-plan \
  --file "$visualPlanProposal" \
  --expected-project-revision "$latestProjectRevision" \
  --expected-artifact-revision "$latestArtifactRevisionOrNone" \
  --json
```

只有状态进入 `storyboard_review_ready`，才启动或复用产品服务并打开 Studio。用户保存审核结果后，调用 `show_workflow_confirmation`；卡片回传 `continue_finish_storyboard` 时重新校验 revision，再执行 `confirm-storyboard`。

## 4. 动画候选 → 审核

先读 [动画规则](references/animation-rules.md)；需要 HTML 模块时再读 [动画模块契约](references/animation-module-contract.md)。

- 动画必须绑定具体口播句与 cue。
- 真实产品操作、截图、结果页优先使用真实素材。
- 无动画时提交空 modules 和明确原因，不能造占位模块。
- HTML 必须支持任意时间 seek 后恢复确定状态。

发布 `animation-manifest` 后，等待 `animation_review_ready`，在同一个 Studio 审核。卡片回传 `continue_finish_animation` 后才执行 `confirm-animation`。

## 5. 时间线候选 → 审核

先读 [时间线与导出](references/timeline-and-export.md)。最终时间线只消费剪后时间、真实字幕与已审核模块：

```bash
node "$VC" artifact put "$jobDir" \
  --type timeline \
  --file "$timelineProposal" \
  --expected-project-revision "$latestProjectRevision" \
  --expected-artifact-revision "$latestArtifactRevisionOrNone" \
  --json
```

状态进入 `timeline_review_ready` 后，在同一个 Studio 审核。卡片回传 `continue_finish_timeline` 且 revision 仍一致，才执行 `confirm-timeline`。

## 6. 产品导出与验收

最终导出必须由 Runtime 自己完成；Skill 不携带 renderer，也不传旧 Skill 脚本路径：

```bash
node "$VC" workflow get "$jobDir" --json
node "$VC" render run "$jobDir" \
  --expected-revision "$latestRevision" \
  --confirmed \
  --json
```

若当前 Runtime 返回 `missing_renderer`，明确报告这是 Runtime 版本缺口并停止。禁止把旧 `export_final_video.cjs`、独立预览服务或直接 FFmpeg 导出偷偷塞回 Skill。

只有同时满足以下条件才报告完成：

- `renders/final.mp4` 存在，视频流与音频流均可解码；
- 分辨率与项目比例一致；
- 时长与时间线在容差内；
- 关键帧无黑边、遮挡、错误素材或幽灵字幕；
- `renders/verification.json` 的 `passed=true`。

## 确认与恢复规则

```text
candidate saved
      |
      v
*_review_ready ----> 打开同一个 Studio ----> 用户保存
      |                                      |
      |                         MCP App 回传 action + revision
      |                                      |
      +<-------- revision mismatch ----------+
      |             停止并核对
      v
confirmed transition
```

- 卡片不直接执行任何 destructive action。
- `return_finish_*` 返回对应审核视图；`pause_workflow` 保存后停止。
- `revision_conflict` 必须重新读状态，不能静默覆盖。
- “能播放预览”不等于“成片已导出”。
