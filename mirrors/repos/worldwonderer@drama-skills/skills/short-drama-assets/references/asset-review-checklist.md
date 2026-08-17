# 资产拆解审查清单

## Binding gate (`AST-05`)

资产接受前，每个下游 binding 都要解析到已接受的 identity，且 variant
必须在引用的剧情范围内有效。未解决的 occurrence 继续保持 unresolved；不得
为了让提示词或分镜继续工作，猜一个看似合理的 ID。

按“机械事实 → 语义判断 → 创作者接受”顺序检查。Owner 可按 finding 修订；修订动作本身
不等于审查 verdict。需要 verdict 时另起一次审查动作，自检也可以如实记录有证据支持的结论。

## A. 机械检查（`structural_invariant`）

- [ ] 每个 production-relevant screenplay block 有 occurrence 或明确
  `no_asset_change` disposition。
- [ ] 每个文件首行的 `sources` 声明了它用到的全部上游快照，记录里的 `src` 都能解析到
  其中一条。
- [ ] occurrence 的 `source_ref` 指向 accepted screenplay/index 快照，并给出 field、
  block、scene。
- [ ] source pointer、derived visible facts、asset reconciliation、continuity pointer 的
  数据角色没有混写。
- [ ] 每个 occurrence 的 decision 恰为 `reuse` / `new_variant` / `new_asset` /
  `unresolved`。
- [ ] `new_variant` 有 base、differences、cause、valid_from、valid_until/open-ended。
- [ ] ID 唯一；所有已接受 binding 精确解析到 Character+Look、Location+View 或
  Prop+State。
- [ ] unresolved 没有伪造 accepted binding，不能流入 prompt/storyboard 编译。
- [ ] 每条 delta 有 before、after、cause/source、effective range、affected bindings。
- [ ] linked outgoing/incoming 状态一致，或有明确待处理 reconciliation。
- [ ] 可读文字政策完整；`exact_readable` 不与 `no_readable_text` 冲突。

机械失败指出具体 record/field、owner 和修复方向，不回显整段创作文本。

## B. 语义审查（`reviewed_invariant`）

逐条引用剧本/设定集 证据回答：

- [ ] 含混代词、匿名人、同款多件物没有被猜成某个已有 ID。
- [ ] Character 身份锚点与服装、伤势、湿污、姿势等临时状态分离。
- [ ] Location 地理/固定锚点没有因角度、时段、天气、灯光被复制成新地点。
- [ ] Prop 形制/功能身份没有因 owner、开合、破损、内容或文字状态被复制。
- [ ] 每个新 asset 有不能复用的持久证据；每个 variant 说明 base 什么保持不变。
- [ ] 提取没有凭空补脸、品牌、门窗、内容物、伤势、灯光或可读文字。
- [ ] transfer、伤势、换装、停电、天气/光态和知识变化都有足以支持的剧情原因。
- [ ] occurrence 的 production disposition 合理：提及不被误当出镜，关键操作物不被
  降成普通布景。

Reviewer finding 应含被引用记录（`src` 与 `record_id`）、evidence、impact、required fix、
owner、severity、status；不能只说“资产不够细”或“看起来 AI”。

## C. Craft 默认（可覆盖，不单独阻断）

- [ ] 身份未变时优先复用或 variant，没有追求“一场一资产”。
- [ ] 瞬时 pose/camera/framing 留给 storyboard，没有制造 Look/View/State 爆炸。
- [ ] 设定集 只保留识别、复用、prompt、镜头和连续性所需事实。
- [ ] Location 先有地理/入口/固定锚点，再有氛围；Prop 有尺度/形制/材料/功能；
  Character 有可观察的区分锚点。
- [ ] outgoing 精简但足以让下一场/集无脑内补全地继续。

Creator 可用制作原因覆盖，例如需要逐件审批背景陈设；记录 override，而非改成硬规则。

## D. Taste 选项（只确认选择）

- [ ] 群演按 group 还是个体管理已选择。
- [ ] 同建筑空间拆分颗粒度能支持当前制作。
- [ ] 蒙太奇/梦境/主观断裂已声明边界。
- [ ] 临时可见状态用 delta 还是升为 variant 符合本项目复用策略。

不得仅因 reviewer 偏好另一个选项而判失败。

## E. Creator acceptance（独立 checkpoint）

给创作者看的摘要必须列出：

1. 复用项及匹配证据；
2. 新 variant 及 base/difference/cause/validity；
3. 新 asset 及持久区分证据；
4. unresolved 的原文证据、候选和不同选择的下游影响；
5. continuity deltas 与跨集 outgoing；
6. 接受后会 stale 的下游文件。

逐项保存 `proposed/accepted/rejected/superseded` 与 creator decision ref。Creator acceptance
不自动代表结构检查、审查 verdict 或 delivery-ready；只在对应动作真实发生时分别记录。

## 当前范围完成判据

本次范围内结构检查通过、每个 occurrence 已决定、无 unresolved binding、continuity 可交接，
且 creator 接受了新增/复用/变体/delta，即完成当前资产批次。审查与交付是后续独立动作，
不作为图片提示词或 storyboard 这两个并列分支的隐式前置门槛。
