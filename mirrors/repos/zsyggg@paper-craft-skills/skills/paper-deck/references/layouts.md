# Layouts

这些不是固定模板，而是逐页生图时的构图角色。先选页面角色，再写 prompt。

## Slide Roles

| Role | 用途 | 构图 |
|---|---|---|
| `cover` | 封面，一眼说明主题和气质 | 大标题 + 视觉锚点 + 少量元信息 |
| `problem` | 为什么这个问题重要 | 左侧问题/右侧现实场景或证据 |
| `context` | 背景和已有方法 | 时间线 / 方法地图 / 层级图 |
| `method-overview` | 方法总览 | 输入 → 核心模块 → 输出 |
| `mechanism-detail` | 单个核心机制拆解 | 局部放大、编号步骤、短标签 |
| `comparison` | 新旧方法/ablation 对比 | 左右对照、差异高亮 |
| `evidence` | 实验或数据证据 | 大数字 + 小图表 + 解释标签 |
| `paper-figure-remix` | 重画论文 Figure | 保留事实，重新组织视觉层级 |
| `code-link` | 方法与代码对应 | 文件/函数/流程的关系图 |
| `takeaway` | 结论和下一步 | 1 句结论 + 3 个要点 |

## Rhythm

8-12 页推荐节奏：

```text
cover → problem → context → method-overview → mechanism-detail → mechanism-detail → evidence → comparison → limitation → takeaway
```

12-18 页推荐节奏：

```text
cover
problem / context
method-overview
3-5 pages mechanism-detail
2-4 pages evidence / comparison
limitation
takeaway / discussion
```

## Composition Rules

- Cover: 文字少，主视觉强。
- Method overview: 中间主图必须占 65%-80% 画面。
- Mechanism detail: 每页只拆一个机制，避免把整篇论文塞进一页。
- Evidence: 数字要大，解释要短；不要生成密密麻麻的表格。
- Comparison: 左右结构必须对称，差异点要显眼。
- Takeaway: 不要再引入新概念。
- 不要过度留白。留白要服务层级和呼吸感，不能让页面像没做完。
- 如果用户允许使用真实素材，优先给论文图、表格、实验曲线、PDF 截图规划明确落位。

## Text Limits

| 页面类型 | 图片内文字建议 |
|---|---|
| cover | 标题 1 行，副标题 1 行，元信息 1 行 |
| method-overview | 5-9 个短标签 |
| mechanism-detail | 6-12 个短标签 |
| evidence | 1 个大数字 + 2-4 个短解释 |
| takeaway | 1 句主结论 + 3 个短点 |

如果文字超过限制，优先拆页或改成可编辑文字层，不要强行让生图模型写长段落。
