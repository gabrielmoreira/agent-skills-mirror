# Lookdev 风格帧提示词

`lookdev_frame` 使用 [独立结构模板](../assets/lookdev-frame-spec.jsonl.md)，把项目层已经接受的
视觉方向投影成可比较的通用图片提示词。它不选择画风，
不生成图片，也不从一张参考图推断整部作品的规则。

## 三类测试轴

- `character_expression`：绑定准确 CHAR/LOOK，检查身份锚点、材质/线条和表演可读性；
- `core_location`：绑定准确 LOC/VIEW，检查地理、材质、色彩层级与光源逻辑；
- `high_pressure_scene`：绑定准确场景、人物状态与来源块，检查冲突中的注意中心、遮挡和密度。

不要求三类都固定生成若干张。选择本项目最能暴露方向失效的代表帧，并在规格中写清测试问题。

## 写规格

`purpose` 写 `lookdev_frame`，`lookdev_axis` 选择本次测试轴，`direction_ref` 用文件头 `sources` 中
`short-drama.json` 的快照键，`field` 写
`/creator_authority/visual_direction/choices/look_development`，并用同一个快照键的
`production_profile_ref` 绑定本项目已接受制作配置。高压力场景还要用 `story_context_refs` 绑定
真实 screenplay-index `BLK-…` 场次/动作/信息权限记录，不能从提示词发明剧情状态。再写：稳定项、
允许变化项、要保护的身份/地理/剧情事实，以及删除风格标签后真正改变的材质、光、色、边缘、
景深或空间表达。

风格参考使用 `role: style`：

- `may_control` 只列色彩层级、材质处理、阴影边缘、景深倾向、画面密度等本次准许内容；
- `must_not_control` 保护角色身份、固定场景地理、剧情状态、人数、持物与道具文字；
- 每张参考有稳定 `slot_id` 和显式 `order`，换版或数组重排不改变槽位语义。

角色、地点或压力场景的事实仍来自它们各自 owner。高压力测试帧不得为了“更有冲击力”提前
泄露身份、发明动作结果或改变文字政策。

## 比较与修订

比较人物、地点和压力场景是否共享可辨认语言，同时记录哪一部分允许逐场变化。没有授权生成结果
观察时，只能指出文字层风险。若收到绑定准确 prompt/spec/reference/config 的项目观察，局部修订写
`changes` 与 `preserve`，一次只改诊断所需变量；不把一次结果推广为其他项目或制作配置的规律。
