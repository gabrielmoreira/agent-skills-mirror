---
name: chengfeng-export-talking-head
description: 把已审核的口播删词账本落成剪后视频：展示确认卡、执行物理剪切、验收剪后媒体。只在删词已经人工复核之后使用。用户说导出口播、执行剪切、把剪好的视频导出来、继续导出，或确认卡回传 action=continue_cut 时使用。不要用于生成删词候选、字幕、分镜动画或成片渲染。
user-invocable: true
---

# 导出

流程的第三段。上游是剪口播（产出一份已复核的删词账本），下游是字幕。

```text
剪口播 ──账本──▶ 【导出】──source_cut.mp4──▶ 字幕 ──subtitles.srt──▶ 分镜动画
```

**这是整条链子上第一个产生媒体文件的地方。** 在此之前全是非破坏的：账本记着播哪些段，预览把它们拼起来给人听，原片一动不动。物理剪切之后才有一个真的文件。

所以这一段的全部风险都在一件事上：**剪的必须是用户确认过的那一版，不是他确认之后又改出来的那一版。** 下面每一条约束都是为这件事服务的。

Skill 做编排与确认；产品 Runtime 是项目、Cuts、EDL 和媒体剪切的唯一写入者。

先读取并执行 [业务 Skill 的阶段合同](../../references/business-workflow-contract.md)。

## 0. 每次先做 Runtime 预检

从 Codex 已启用 Plugin 列表精确取得 `chengfeng-videocut` 的 `source.path`。`SKILL_DIR` 不是 Codex 保证注入的变量；禁止依赖它、硬编码开发机路径或用 `find` 猜测安装目录：

```bash
PLUGIN_ROOT="$(codex plugin list --json | node -e 'let s=""; process.stdin.on("data", c => s += c); process.stdin.on("end", () => { const rows = JSON.parse(s).installed || []; const hit = rows.filter(x => x.enabled && x.name === "chengfeng-videocut" && x.source && x.source.path); if (hit.length !== 1) process.exit(1); process.stdout.write(hit[0].source.path); });')"
test -n "$PLUGIN_ROOT" && test -f "$PLUGIN_ROOT/.codex-plugin/plugin.json" || { echo "chengfeng-videocut enabled plugin root unavailable" >&2; exit 1; }
ENSURE="$PLUGIN_ROOT/scripts/ensure-runtime.cjs"
RUNNING="$PLUGIN_ROOT/scripts/ensure-running.cjs"
STUDIO="$PLUGIN_ROOT/scripts/ensure-studio.cjs"
VC="$PLUGIN_ROOT/scripts/videocut-cli.cjs"

node "$ENSURE" --install-if-missing --json
```

- `ready`：继续本 Skill。
- `missing`：脚本只提示一次「正在从 GitHub Release 安装」，校验完成后自动续跑。
- `runtime_unhealthy`、安装失败或安装后 doctor 失败：报告结构化诊断并停止。
- `runtime_capability_missing`：停止并要求升级，禁止回退旧剪辑链。
- 预检阶段禁止启动服务、打开 Studio 或创建项目。

详细协议见 [Runtime 与产品契约](../../references/runtime-and-product-contract.md)。

## 1. 入口断言：确认上游真的走完了

```bash
node "$RUNNING" --json
node "$VC" workflow get "$jobDir" --json
node "$VC" cuts get "$jobDir" --json
```

必须同时成立，缺一条都停止：

| 断言 | 不成立时 |
| --- | --- |
| `workflow get.data.stage` 为 `cut_review_ready` | 上游没走完 —— 切换到 `$chengfeng-videocut:chengfeng-cut-talking-head` |
| Cuts 存在且 `cutWordCount > 0` | 没有任何删词，没有可剪的东西 —— 停止并说明 |
| `workflow get.data.editListRevision` 有确定值 | EDL 不存在时该值必须明确为 `none`，**禁止省略**，也禁止自己编一个 |

**不要因为「用户说剪好了」就跳过这一步。** 用户说的是他在界面上改完了，不是产品状态已经就绪。

## 2. user confirmation：确认卡

物理剪切不可撤销，所以它前面必须有一张卡，而且卡上冻结的是**当下这一刻**的三个 revision。

```text
projectId
stage=cut_review_ready
expectedProjectRevision
expectedCutsRevision
expectedEditListRevision
selectedCount（可选）
removedDuration（可选）
```

调用本插件 MCP App 的 `show_workflow_confirmation`，传入上面这些。

- **卡片只回传 action，不直接剪切。**
- `continue_cut`：进入第 3 步。
- `return_cut_review`：先再次 `node "$RUNNING" --json`，再返回同一 Studio 让用户继续改；改完回到本 Skill 第 1 步重来。
- `pause_workflow`：保存状态后停止。

本次不实现一次性 confirmation receipt；卡片动作仍由 Agent 与 Product revision 比对约束，不把它描述为 Product 强制 receipt。

## 3. Product execution：物理剪切

收到 `continue_cut` 之后：

1. 再次执行 `node "$RUNNING" --json`。
2. 再次执行 `workflow get` 与 `cuts get`。
3. 项目、Cuts、EDL 任一 revision 与卡片不一致，**停止**，让用户核对他在确认之后又做的编辑。

三个都一致时才执行，并且**仍然用卡片回传的那份 revision**：

```bash
node "$VC" cuts apply "$jobDir" \
  --expected-revision "$confirmedProjectRevision" \
  --expected-edit-list-revision "$confirmedEditListRevision" \
  --confirmed \
  --json
```

**禁止把刚读到的「当前最新 revision」替换成确认 revision。** 这两个值在正常情况下相等，正因为相等，替换掉不会有任何症状——直到某次用户在确认之后又改了一刀，而剪刀落在他没看过的那一版上。相等时替换毫无收益，不等时替换正是灾难本身。

## 4. outcome verification：验收剪后媒体

```bash
node "$VC" workflow get "$jobDir" --json
```

三条都满足才能报告剪辑完成：

- 媒体可解码
- **有音频流**
- 时长与确认时的时间线一致

**到这里本 Skill 结束。** 不重新转录、不产出字幕、不发布字幕 artifact——那是字幕 Skill 的事，它自己从 `source_cut.mp4` 重新转写。不要为了「让下游能跑」在这里补一份占位字幕。

报告必须分开写：Product 结构化 revision / artifact / verification 为 **API/readback PASS**；真实同项目浏览器帧审核才是 **visual frame PASS**；没有人实际听音时一律为 **human listening UNVERIFIED**，不得用播放、DOM、截图或媒体探测替代。

## 恢复与失败

- `revision_conflict`：重新读取状态，说明用户刚才的编辑，不自动覆盖；若 `reason=edit_list_changed_after_confirmation`，**必须重新展示确认卡**，不能沿用旧确认。
- `revision_required`：旧入口没有携带 `expectedEditListRevision`，按未确认处理并停止；禁止自动补成当前 EDL revision。
- `media_has_no_audio`：保留原素材和上一份有效产物，停止交付。
- `invalid_state`：多半是 stage 不对（上游没走完，或已经剪过了）。读回 workflow 说明当前处在哪一步，不要重试。
- `runtime_unhealthy`：不要循环重装。
- `service_identity_mismatch` 或 `service_port_conflict`：停止，不回退 foreground、不换端口、不杀未知进程。
- 页面关闭但服务仍在：读取 workflow 后从当前状态续做，不新建项目。
- 任何失败都不得把「能预览」说成「已经剪好」。**预览是拼出来的，不落盘；剪好是一个真的文件。** 这两件事在这一段之前一直不同，正是本 Skill 让它们第一次相同。
