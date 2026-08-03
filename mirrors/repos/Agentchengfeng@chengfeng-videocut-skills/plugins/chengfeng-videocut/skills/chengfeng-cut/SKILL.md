---
name: chengfeng-cut
description: 剪辑中文口播原素材：逐词转录、按词典修正听错的专名、识别口误与重复、生成删词候选、打开 Studio 让用户复核。只产出一份已复核的删词账本，不切媒体、不做字幕、不做分镜动画。用户说剪口播、处理口误、生成口播基础素材、继续剪口播，或确认卡回传 action=return_cut_review 时使用。不要用于执行物理剪切、导出剪后视频、单独安装、单独打开工作台或口播分镜成片。
user-invocable: true
---

# 剪口播

从一条视频到**一份人工复核过的删词账本（Cuts + EDL）**，不碰媒体文件。全程五步：

```text
0  预检     Runtime 装好、健康（没装自动装，装不上就停）
1  建档     真实视频 → 云端逐词转录 → 产品建项目 → 起服务 → 读回状态
2  修字     词典把听错的专名换回来（在判断删什么之前）
3  删词     取播放顺序 → 判断口误/重复 → 候选提交产品（CAS）
4  审核     校验通过后打开 Studio，用户亲自划词复核
5  交棒     报告结果，停在账本 —— 出成片归导出 skill
```

**不切媒体**：账本改一次是几十毫秒，切一次是一个不可撤销的文件。到本 Skill 结束，
磁盘上没有任何新视频。Skill 做语义判断与编排；产品 Runtime 是项目、Cuts 和
Studio 状态的唯一写入者。

先读取并执行 [业务 Skill 的阶段合同](../../references/business-workflow-contract.md)。
本文步骤与合同阶段的对应：1=preflight+Product state readback，3=proposal+Product CAS，
4=project-level review binding。合同后三个阶段（确认、执行、验收）属于导出 Skill。

各条规矩的事故来历在 [事故簿](references/lessons.md)——规矩在正文，故事在那边。

## 0. Runtime 预检

先读取并执行 [Runtime 预检](../../references/runtime-preflight.md)——它是预检的唯一真本：
定义 `$PLUGIN_ROOT` / `$ENSURE` / `$RUNNING` / `$STUDIO` / `$VC` 工具变量，安装缺失的
Runtime，并规定每种失败结果的处置（含「禁止自制替代界面」禁令）。任何非 `ready`
结果都按它的规定停止。

## 1. 建档：真实输入 → 转录 → 产品建项目

**干什么**：把用户的本地真实视频和云端逐词稿交给产品，原子建档，起服务，读回状态。

```bash
# 云端逐词转录（生成任务目录内的 transcript 候选）之后：
node "$VC" project create "$jobDir" \
  --video "$taskLocalVideo" \
  --transcript "$taskLocalTranscript" \
  --aspect-ratio "$aspectRatio" \
  --json

node "$RUNNING" --json          # 产品声明式确保常驻服务（5190）

node "$VC" workflow get "$jobDir" --json    # Product state readback
node "$VC" cuts get "$jobDir" --json
```

规矩：

- 只接受用户给出的真实口播视频或现有真实项目；没有真实媒体就停止，禁止用示例、
  占位视频顶替
- 转录只用当前环境已获准的**云端 ASR**；禁止回退本地 ASR；没有可用云端 ASR 时报告
  `missing_cloud_transcription_adapter`，不开 Studio、不伪造 transcript
- `--video` / `--transcript` 必须是任务目录内的真实文件；`aspectRatio` 只能是
  `3:4 / 4:3 / 16:9`，默认 `4:3`
- 已有规范项目先 `inspect` 确认并复用，不重复创建 `projectId`；只有恢复
  `cut_prepare_running` 或明确刷新时才用 `project prepare`
- `project create` 是唯一入口：不经过素材库、上传会话或额外 Skill；Skill 不得先写
  `project.json`
- 服务必须由脚本确认 `healthy=true`、`runtimeMode=launchd`、版本兼容、URL 为
  canonical 5190 后才继续；失败透传结构化错误并停止，禁止回退 foreground、换端口、
  杀未知进程
- 两份 readback 必须指向同一个 `projectId`，保存 workflow stage 与
  Project / Cuts / EditList 三个 revision；缺失或不一致即停止

## 2. 修字：把听错的专名换回来

**干什么**：在判断删什么**之前**，用词典修正转录听错的专名——听错的字不是多余的话，
删掉 `Clock` 那句话就缺一个词，删词修不掉它。

```bash
node "$VC" transcript dictionary "$jobDir" \
  --dictionary "$PLUGIN_ROOT/references/ai-term-dictionary.md" --json
```

它直接改，并列出改了哪几处。**改完必须看那份清单**——词典不看上下文也会改错
（把真说的「Skills」normalize 成「Skill」之类）；看到不对就改词典，不在别处打补丁。

只有词典解决不了、且作者手上有稿子时，才追加一次上下文对齐：

```bash
node "$VC" transcript align "$jobDir" --script "$scriptPath" --json   # 只报不改
node "$VC" transcript correct "$jobDir" --file "$correctionFile" --json
```

规矩：

- **只改文字，不改时间、词数、wordId**——产品逐词比对时间戳，动了直接拒绝
- **只换写法，不换意思**——真说错又重说的属于残句改口，归下一步删词管
- 词典没有、稿子也确认不了的，**不许猜**：报告出来留给人补词典。塞一个编的名字
  比留一个听错的名字更坏
- 中文口语按原文保留：说「叉」「大模型」就是他说的话
- 词典是**每次转录都要过的一道闸**（同一段音频转两遍结果都不一样，见事故簿）

**文稿按标点分段**：转录里每个词带标点，文稿一个逗号一段、一句一行；字幕吃同一份
标点，两边断句一致。2026-07-28 之前的老项目没有标点，跑
`node "$VC" transcript regroup "$jobDir" --json` 重切段落即可（逐词校验 id/时间/文字
不变，对剪过的项目安全）；真要标点得重转——标点在旧转录里根本不存在。

## 3. 删词：判断并提交候选

**干什么**：读 [语义删除规则](references/semantic-deletion.md)，在产品的播放顺序视图上
判断口误与重复，提交完整候选。

```bash
node "$VC" transcript playback "$jobDir" --json   # 判断的唯一输入

node "$VC" cuts get "$jobDir" --json              # 取 Cuts 自己的 revision
node "$VC" cuts set "$jobDir" \
  --file "$proposalFile" \
  --expected-revision "$latestCutsRevision" \
  --json
```

候选只引用稳定 `wordIds`：

```json
{
  "schemaVersion": 1,
  "cutWordIds": ["word-12", "word-13"],
  "reasons": [
    { "wordIds": ["word-12", "word-13"], "kind": "repeat", "risk": "low" }
  ]
}
```

规矩：

- **判断只用 `transcript playback` 的播放顺序，不许自己从 `transcript.json` 拼**——
  「说了两遍」靠播出来相邻，自己拼会把跳号读成缺内容而误否（见事故簿）
- 删除只有「删除 / 未删除」两态；AI 原因不形成「建议删除」第三态
- 口误、重复、残句默认删前保后；长句、整句、分叉重说必须高风险复核
- 普通停顿不由 Skill 计算：相邻静音合并与 `natural-pause-v2` 由产品确定性执行
- 候选是**本轮判断的完整结论，不是增量**——`cuts set` 是替换语义，交增量会把上一轮
  语义删词静默丢掉（见事故簿）；也禁止读取或手工合并
  `initialization.baselineCutWordIds`
- `reasons` 落盘，如实写；产品会裁掉提到未删词的部分
- 不直接写 `cut-selection.json`、`project.json` 或事件日志
- `cuts get.data.revision` 是 Cuts 的 revision，`workflow get.data.revision` 是项目的，
  **禁止混用**
- 提交成功后必看 `noLongerCut`（本次不再删的词数）：不为零且非有意撤回 = 交了增量，
  回去补全量重交；读到 `"unknown"` 也要看见
- 随后立即再次 `workflow get` + `cuts get`，确认 `cut_review_ready` 与三个 revision；
  不一致即停，绝不直接写 JSON 或自动覆盖

## 4. 审核：到人工审核时才打开 Studio

**干什么**：transcript 与 Cuts 落盘、工作流进入 `cut_review_ready` 后，打开产品审核页
让用户亲自复核。

```bash
node "$RUNNING" --json                    # 打开前再次幂等 ensure
node "$VC" open "$jobDir" --json          # 取产品返回的项目 URL

node "$STUDIO" \
  --url "$productUrl" \
  --view koubo \
  --json                                  # 能力门禁：确认 5190 注册了 koubo 视图
```

规矩：

- 只有门禁返回 `ok=true` 才用 Codex 内置浏览器打开 `studio.url`，然后停止自动推进，
  等用户划词、恢复、保存
- 打开前把 `productUrl` 的 `#project/<projectId>` 与 readback 的 `projectId` 严格比对，
  并绑定 `stage=cut_review_ready` 与三个 revision——门禁 `ok=true` 只证明产品面能力，
  不能替代项目级绑定；任何不一致重新 readback
- `studio_capability_missing`：停止并说明版本不兼容，可建议 `$chengfeng-report-bug`；
  禁止因 URL 带 `?view=koubo` 就认为新界面存在，禁止回退旧任务面板
- 不要把「打开工作台」当任务第一步；不访问旧 `review.html`、8898/8899；
  不控制 Studio DOM、不直接改媒体元素；不创建独立音频轨或占位字幕轨

## 5. 交棒：到账本为止

用户复核完成后本 Skill 结束。**不弹确认卡，不执行剪切**——物理剪切的确认卡属于
导出 Skill，那张卡冻结的必须是用户按下确认那一刻的 revision。

```bash
node "$VC" workflow get "$jobDir" --json   # 结束前读回一次
node "$VC" cuts get "$jobDir" --json
```

报告三件事，然后告诉用户下一步跑导出：删了多少词、少了多少秒；当前 stage
（应为 `cut_review_ready`）；项目 / Cuts / EDL 三个 revision。

`return_cut_review`：先再次 `node "$RUNNING" --json`，再返回同一 Studio 继续复核。

报告分级：Product 结构化 revision 为 **API/readback PASS**；真实浏览器帧审核才是
**visual frame PASS**；没人实际听音一律 **human listening UNVERIFIED**，不得用播放、
DOM、截图或媒体探测替代。

## 恢复与失败

- `revision_conflict`：重新读取状态，说明用户刚才的编辑，不自动覆盖
- `runtime_unhealthy`：不循环重装
- `service_identity_mismatch` / `service_port_conflict`：停止，不回退 foreground、
  不换端口、不杀未知进程
- 页面关闭但服务仍在：读取 workflow 后从当前状态续做，不新建项目
- 任何失败都不得把「账本已写」说成「已经剪好」——到这一段为止没有任何媒体文件产生

附注：本 Skill 接受**本地真实视频**与**云端逐词稿**直接进入产品，这是合同 preflight
的要求；两者都真实存在是一切判断的前提。
