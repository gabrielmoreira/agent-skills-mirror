---
name: chengfeng-finish-talking-head
description: 把口播基础素材制作成完整成片：生成并审核分镜、动画和总时间线，随后导出与验收 final.mp4。用户说口播成片、口播分镜、口播动画、导出口播视频、继续口播成片，或确认卡回传 action=continue_finish_storyboard / continue_finish_animation / continue_finish_timeline / return_finish_storyboard / return_finish_animation / return_finish_timeline 时使用。不要用于原始删词、单独安装、单独打开工作台或普通 HyperFrames 视频。
user-invocable: true
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

先读取并执行 [两个业务 Skill 的阶段合同](../../references/business-workflow-contract.md)。本 Skill 只在已有 Product `projectId` 上续跑，不创建项目、不导入素材、不建立上传会话或素材库；任何一次续跑都保持固定阶段：`preflight -> Product state readback -> proposal -> Product CAS -> project-level review binding -> user confirmation -> Product execution -> outcome verification`。

## 0. preflight：每次先做 Runtime 预检

```bash
PLUGIN_ROOT="$(codex plugin list --json | node -e 'let s=""; process.stdin.on("data", c => s += c); process.stdin.on("end", () => { const rows = JSON.parse(s).installed || []; const hit = rows.filter(x => x.enabled && x.name === "chengfeng-videocut" && x.source && x.source.path); if (hit.length !== 1) process.exit(1); process.stdout.write(hit[0].source.path); });')"
test -n "$PLUGIN_ROOT" && test -f "$PLUGIN_ROOT/.codex-plugin/plugin.json" || { echo "chengfeng-videocut enabled plugin root unavailable" >&2; exit 1; }
ENSURE="$PLUGIN_ROOT/scripts/ensure-runtime.cjs"
RUNNING="$PLUGIN_ROOT/scripts/ensure-running.cjs"
STUDIO="$PLUGIN_ROOT/scripts/ensure-studio.cjs"
VC="$PLUGIN_ROOT/scripts/videocut-cli.cjs"

node "$ENSURE" --install-if-missing --json
```

`PLUGIN_ROOT` 只来自上面已启用 Plugin 行的 `source.path`。不要依赖未保证存在的 `SKILL_DIR`、硬编码开发机路径或用目录搜索猜测安装位置。

预检是本 Skill 内部步骤，不是第三个 Skill。缺失时提示一句并安装；`runtime_unhealthy`、`runtime_capability_missing` 或安装失败时停止，不覆盖现有安装，也不回退旧剪辑链。预检和无头生成阶段都不得打开 Studio。详细协议见 [Runtime 与产品契约](../../references/runtime-and-product-contract.md)。

Runtime 预检成功后、第一次 `workflow get` 前，立即让 Product 声明式确保常驻服务：

```bash
node "$RUNNING" --json
```

只有脚本确认服务 `healthy=true`、`runtimeMode=launchd`、版本兼容、PID 有效且 URL 为 canonical 5190 入口后，才继续。失败时透传 Product 的结构化错误并停止；禁止回退 foreground、换端口或杀未知进程。

## 1. Product state readback：检查基础素材包

```bash
node "$VC" workflow get "$jobDir" --json
```

必须同时存在并通过产品检查：

- `source_cut.mp4`：真实剪后视频，含音频流；
- `subtitles.srt`：基于剪后视频重建的规范字幕；
- `workflow get.data.artifact.state=current`；
- `workflow get.data.artifact.editListRevision` 与当前 `editListRevision` 完全相同；
- 同一个 `projectId` 与当前 project revision。

只有文件路径、但 Runtime 没有返回上述 artifact 状态时，以 `artifact_state_unavailable` fail-closed。不得仅因 `source_cut.mp4` 存在就假设它对应当前时间线，也不得让旧成片进入分镜链。

若缺失，切换到 `$chengfeng-videocut:chengfeng-cut-talking-head` 完成前置剪辑，再以同一个 `projectId` 恢复本 Skill。不要新增业务状态机或第二个项目。

## 2. 读取项目配置并准备 proposal

比例、动画风格与额外要求必须来自当前项目状态；不要读取所有项目共享的可变全局默认值。用户尚未选择时，只询问会实质改变成片的必要信息。

```json
{
  "aspectRatio": "4:3",
  "animationStyle": "xiaohei",
  "requirements": "保留真实产品操作画面"
}
```

用户确认配置后，用最新 revision 执行 `start-final`。每一步都重新读取 revision，不能连续复用旧值。

## 3. proposal → Product CAS：分镜候选

先读 [分镜规则](references/storyboard-rules.md)。按字幕语义分段，候选段落绑定稳定 `wordIds`，再通过产品校验发布：

```bash
node "$VC" artifact put "$jobDir" \
  --type visual-plan \
  --file "$visualPlanProposal" \
  --expected-project-revision "$latestProjectRevision" \
  --expected-artifact-revision "$latestArtifactRevisionOrNone" \
  --json
```

首次进入 storyboard，以及下文首次进入 animation / timeline 审核视图，都必须在打开前重复同一顺序，不能依赖流程开头那次 ensure：

```bash
node "$RUNNING" --json
node "$VC" open "$jobDir" --json
node "$STUDIO" --url "$productUrl" --view "$reviewView" --json
```

## 3.1 project-level review binding：分镜审核

只有对应状态进入 `*_review_ready`、能力门禁返回 `ok=true`，才打开 `studio.url`。打开前必须把 Product URL 的 `#project/<projectId>` 与 workflow readback `projectId` 严格比对，并把当前 workflow stage、Project / EditList revision 和本阶段 artifact revision 绑定到审核；能力门禁 PASS 只证明产品面存在，不能替代项目级绑定。storyboard 使用 `reviewView=storyboard`，animation 与 timeline 使用 `reviewView=preview`。用户保存审核结果后，先再次执行 `node "$RUNNING" --json`，再调用 `show_workflow_confirmation`。卡片回传 `action=continue_finish_storyboard` 或 `action=return_finish_storyboard` 时都先执行：

```bash
node "$RUNNING" --json
```

`continue_finish_storyboard` 重新 Product readback 并逐项校验绑定 revision 后执行 `confirm-storyboard`；`return_finish_storyboard` 回到同一项目的 storyboard 审核页，不推进状态。

## 4. proposal → Product CAS → project-level review binding：动画候选与审核

先读 [动画规则](references/animation-rules.md)；需要 HTML 模块时再读 [动画模块契约](references/animation-module-contract.md)。

动效风格从 [风格注册表](animation-styles/styles.json) 选取，再读该风格自己的 `SKILL.md` 与 references。当前只有 `xiaohei`（小黑漫画感 SVG 动效）。注册表里没有的风格不得凭空发明；用户未指定时说明可选项并让用户选。

- 动画必须绑定具体口播句与 cue。
- 真实产品操作、截图、结果页优先使用真实素材。
- 无动画时提交空 modules 和明确原因，不能造占位模块。
- HTML 必须支持任意时间 seek 后恢复确定状态。

发布 `animation-manifest` 后，等待 `animation_review_ready`，通过同一能力门禁进入 `preview` 视图审核。用户保存后先 ensure-running；卡片回传 `action=continue_finish_animation` 或 `action=return_finish_animation` 时都先执行：

```bash
node "$RUNNING" --json
```

`continue_finish_animation` 重新 Product readback 并校验 URL/hash projectId、stage、Project / EditList / artifact revisions 后执行 `confirm-animation`；`return_finish_animation` 回到同一项目的动画审核页，不推进状态。

## 5. proposal → Product CAS → project-level review binding：时间线候选与审核

先读 [时间线与导出](references/timeline-and-export.md)。最终时间线只消费剪后时间、真实字幕与已审核模块：

```bash
node "$VC" artifact put "$jobDir" \
  --type timeline \
  --file "$timelineProposal" \
  --expected-project-revision "$latestProjectRevision" \
  --expected-artifact-revision "$latestArtifactRevisionOrNone" \
  --json
```

状态进入 `timeline_review_ready` 后，通过同一能力门禁进入 `preview` 视图审核。用户保存后先 ensure-running；卡片回传 `action=continue_finish_timeline` 或 `action=return_finish_timeline` 时都先执行：

```bash
node "$RUNNING" --json
```

`continue_finish_timeline` 重新 Product readback 并校验 URL/hash projectId、stage、Project / EditList / artifact revisions 后执行 `confirm-timeline`；`return_finish_timeline` 回到同一项目的时间线审核页，不推进状态。

## 6. user confirmation → Product execution → outcome verification：产品导出与验收

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

报告必须明确证据等级：Product 的 stage / revision / `verification.json` 相符是 **API/readback PASS**；只有在 Codex 内置浏览器打开同一 `#project/<projectId>` 和绑定 revision 观察真实画面，才是 **visual frame PASS**；没有人实际比较听感时固定写 **human listening UNVERIFIED**。自动播放、静音、截图、DOM 或流解码不能替代人工听音。

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
- `studio_capability_missing` 时禁止打开任何没有 capability manifest 的旧 Studio，也不静默回退；可建议 `$chengfeng-report-videocut-bug` 生成脱敏 Issue 草稿。
- `service_identity_mismatch` 或 `service_port_conflict` 时停止；禁止 foreground 启动、换端口或杀未知进程。
- `return_finish_*` 必须先执行 `node "$RUNNING" --json`，再返回对应审核视图；`pause_workflow` 保存后停止。
- `revision_conflict` 必须重新读状态，不能静默覆盖。
- “能播放预览”不等于“成片已导出”。
- 本次不实现一次性 confirmation receipt；确认仍绑定明确 action 与 Product revisions。
