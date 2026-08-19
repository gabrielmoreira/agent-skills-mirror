# Scoped Edit 与自然语言修订

## 有界编辑合同 (`IMG-06`)

每次 edit 都声明精确 target/region、要改什么、必须保留什么、以及预期的
continuity impact。如果期望变更会改写 identity 或 accepted 上游事实，路由给
该 owner，不要伪装成局部 prompt revision。

## 目录

1. 两类修改
2. Edit-delta 配方
3. 自然语言 spec → diff → accept → rerender
4. 缓存漂移的 restore/adopt
5. 失败与检查

## 1. 两类修改

- **对画面目标的 edit**：产出 `edit_delta` 提示词，例如改变一件衣服局部状态；不执行图像编辑。
- **对提示词本身的 revision**：创作者用自然语言修改规格；先提案 diff，接受后重渲染 Markdown。

二者都不能改写 assets 拥有的身份/variant 事实。若请求是“把这扇门移到另一面墙”但 Location 地理未变更，应发 assets/storyboard 相关 revision request，而不是悄悄写进 edit。

## 2. Edit-delta 配方

四个问题缺一不可：

```text
Target：哪个精确来源快照（`sources` 键）、记录、entity 和 region？
Change：哪些有边界、可观察的变化？
Preserve：身份、构图、光线、空间以及哪些未影响 entity/region 必须不变？
Continuity impact：预期对应哪个 accepted State/binding，有效到哪里？
```

### Target

- 用元信息绑定目标快照；copyable 正文用自然语言明确主体和区域。
- “改背景”“让她更狼狈”过宽；需要具体新 View/区域与可观察变化。
- 多个不相干 target 默认拆为多个 edit，防止 preserve 集失焦。

### Change

按位置、方向、范围、程度、材质/色彩结果写 delta。例如“右袖肘部以下呈雨水浸湿后的深色，衣料贴合但无撕裂”，比“衣服弄湿”可控。不得补写未接受的伤势或剧情因果。

### Preserve

先列最容易被误改的高价值事实：面部/体态身份、未变 Look 部件、固定地理、道具轮廓与文字、构图/机位、光向、未选区域。不要写“其他全部保持”代替边界思考；允许最后用它概括已经点名的 preserve set。

### Continuity impact

引用 道具状态/Look/View 或提出 owner revision；记录受影响的 prompt/shot/keyframe，而非在 edit 中成为新的连续性权威。若没有影响，也明确 `none` 及理由。

- **`structural_invariant`**：`target_ref`、region、changes、preserve 和 impact 必须存在且没有显式冲突。
- **`reviewed_invariant`**：修改范围是否足够清楚、preserve 是否保护真正身份/地理，需要 reviewer 引用证据判断。
- **`craft_default`**：一次 edit 聚焦少量相互关联的 delta；复杂重构改用新 variant/plate。
- **`taste_option`**：变化的视觉强度由创作者决定，只要状态事实未变。

## 3. 自然语言 spec → diff → accept → rerender

用户不需要知道 JSONL 字段。对“把工作服换成深蓝，但保留脸和袖口油渍”执行：

1. **读取权威源**：当前 accepted spec、asset refs 与 recipe version。
2. **解释请求**：区分 prompt-owned 改动、source-owned 事实、含糊项与可能影响。
3. **生成候选 spec**：不覆盖 accepted spec；不确定值保持 unresolved。
4. **展示语义 diff**：字段路径、before、after、理由、影响、是否需上游 owner。
5. **展示新 prompt 预览**：让创作者看实际文案效果，而非只看字段。
6. **接受/拒绝**：接受才提交；拒绝使原 spec 与 Markdown byte-identical。
7. **重渲染**：从 accepted spec 与 recipe version 导出 Markdown，更新下游 stale 状态。

建议预览：

```markdown
### 提议修改 `IMG-...`
- `variant_delta.uniform.color`: `灰蓝` → `深蓝`
- `preserve`: 新增 `右袖口原有油渍的形状与位置`
- 未改：Character identity、服装剪裁、背景、构图、光向
- 影响：仅当前 Look prompt；若资产 Look 尚未接受深蓝色，先请求 assets 修改
- 未映射：无

**重渲染预览**
> ...
```

对“更有电影感”不能擅自选择一串风格字段。给两三个互斥但可解释的候选（如更明确光比/构图/色彩关系），标为 `taste_option` 让创作者选。

## 4. 缓存漂移的 restore/adopt

`image-prompts.md` 是缓存视图。发现它与 spec 不一致时暂停覆盖：

### Restore

- 展示当前手改文本与将恢复的 canonical preview；
- 创作者接受后从 accepted spec 重渲染；
- 不把手改内容静默写回 spec。

### Adopt

- 将可表示的手改语义解析为候选 spec diff；
- 逐条列出 `mapped`、`unmapped`、`lossy`；
- 有 unmapped/lossy 或改动 source-owned 事实时阻断 adopt，保留原文件与冲突副本；
- 安全且被接受后，先提交 spec，再重渲染成规范 Markdown。最终文本可能排版变化，但语义 diff 必须无损。

选择 `merge` 时也先生成候选 diff；不能以“最后写入者获胜”处理创作权威。

## 5. 失败与检查

### 失败征兆

- 直接改 accepted JSONL 或只改 Markdown；
- diff 只写“优化措辞”，没有字段和语义影响；
- 把身份、Location 地理、道具状态 在 prompt 层擅自改掉；
- edit 只有 Change 没有 Preserve；
- unmapped 手改被自动丢弃；拒绝后文件仍改变。

### 完成检查

- source-owned 请求已路由给正确 owner；
- 候选与 accepted 分离，diff 可读、可拒绝，预览可复制；
- accept 顺序是 spec commit 后 rerender；reject 不变；
- restore/adopt 都有预览，无法对应字段的改动保留为冲突；
- 本提示词修订流程不调用媒体生成或 provider API；实际生产交 `$short-drama-produce`
  并对精确任务预览单独确认。
