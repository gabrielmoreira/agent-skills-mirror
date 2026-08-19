# 镜头修订与稳定身份

镜头 ID 表示同一个编辑/导演决定的连续身份，不等于列表位置，也不等于外部制作任务编号。
修订时先判断镜头的叙事职责是否仍是同一个，再决定保留、创建或 retire。

## 身份规则

- **重排**：只改变顺序，镜头目的与边界职责不变时保留原 ID；刷新依赖顺序与相邻边界。
- **插入**：新增一个独立注意或戏剧职责时创建新 ID；不要给后续所有镜头重新编号。
- **内容修订**：同一镜头目的下调整构图、blocking 或边界，保留 ID 并重新发布。
- **拆分**：原镜头被两个或更多独立职责取代时，retire 旧 ID，为每个新镜头创建新 ID；记录
  `revision_lineage`，不把旧 ID 偷给其中一个子镜头。
- **合并**：多个旧镜头被一个新决定取代时，retire 全部旧 ID，创建新 ID，并记录来源集合。
- **恢复**：retire 的 ID 不复用于无关镜头；需要恢复同一职责时用 lineage 显式说明。

普通新镜只需要稳定 `shot_id`；没有 predecessor 或 retired IDs 时省略 `revision_lineage`，
不保存 `mode: new` 和空数组来重复本段规则。
拆分、合并或恢复旧职责时，从
[`revision-lineage.fragment.json`](../assets/revision-lineage.fragment.json) 插入统一结构；同一 shot 文件
内的前身与 retired 关系使用稳定 ID，不伪造指向本文件自身的引用。

## 每次拆分、合并或重排后的对账

重新核对 coverage 的每条 `shot_refs`、场次视觉计划投影、关键帧、motion、容器成员、相邻
start/end boundary、总时长与审查记录。旧 ID 保留在 lineage / retire 记录中用于解释历史，
不能继续被 active coverage 或交付容器引用。

脚本可以检查引用、集合和算术；“是否仍是同一个导演决定”由 agent 根据镜头目的、信息变化、
表演所有权和边界职责判断，不能用文本相似度或数组位置硬判。
