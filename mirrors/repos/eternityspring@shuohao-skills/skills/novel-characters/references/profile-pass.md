# 第二趟 · 生成角色卡

你是在为一部动画改编准备制作素材。给你一个角色的名字、归并后的全部观察记录、以及可引用的原文片段，产出一张完整的角色卡。

**只输出 JSON，不要任何解释、不要 markdown 围栏。** 结构见 `schema.md`。

## 硬规则

1. **一切基于观察记录。** 为了让设定可用而不得不补全的部分，要跟原文保持一致，并且**标注出来**——中文字段加「（推断）」，英文字段加 `(inferred)`。**只用一种标记，不要中英都加。**

2. **语言分工。** 除了这四个字段用英文，其余全部中文：`image.prompt`、`image.negativePrompt`、`image.tags`、`image.turnaround`、`voice.prompt`。（`image.style` 可以是英文。）`promptZh` 系列是对应英文的中文版。
   特别注意：`voice.timbre` / `pitch` / `pace` / `accent` / `emotion` / `referenceHint` **是中文，不是英文**。

3. **`persona.evidence` 只能放「可引用原文」区块里的字符串，逐字照抄。** 不许翻译、不许裁剪、不许把两条合并、不许从观察记录里另找。那个区块是空的就返回空数组。

4. **`image.prompt` / `image.promptZh` / `image.turnaround` 里绝对不许出现角色名、别名、作者名、作品名。** 图像模型对这些偏见极重，会画成它记忆里的角色而不是你的角色。描述这个人，不要叫他的名字。

5. `image.prompt` 是**卡通角色设定图**：纯背景、全身或半身、剪影可辨、表情有戏。要写明画风、线条质感、配色、光照、构图、表情。

6. `image.turnaround` 是**三视图设定表**：同一个角色的正视 / 侧视 / 背视三个全身像并排，共用一条地平线，三视的身高比例和服装细节完全一致，中性站姿、双臂自然下垂，**纯白背景**（`plain pure white background`）、均匀漫射光、无投影，方便后期抠图。画风配色跟 `image.prompt` 保持同一个人。

7. `voice.prompt` 是给 TTS 音色设计引擎的：描述**乐器本身**，不是某一句台词的演绎。性别、听感年龄、音色、音高区间、共鸣、气声、语速、节奏、口音、能量、默认情绪。

8. **同一批角色之间要能区分开。** 会给你同批其他角色的名字，别把他们的长相和声线做成一个样。

## 输入格式

```
Character: 老周
Also referred to as: 老伯、摆渡人
Other characters in this cast: 沈知微、陆行远、胡二爷

Observations gathered from the source text:
1. ...
2. ...

Verbatim quotes — the ONLY strings allowed in `persona.evidence`:
- ...
- ...
```
