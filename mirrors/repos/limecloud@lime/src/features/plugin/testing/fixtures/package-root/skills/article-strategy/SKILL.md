---
name: article-strategy
description: 内容工厂文章策划技能，生成标题候选、大纲、写作计划和读者收益。
---

# Article Strategy

## 何时使用

- `article-research` 已输出检索轮次和核心判断。
- 需要决定文章角度、标题、结构和每段的写作目的。

## 输入

- `researchRounds`
- `citations`
- 用户主题、读者、渠道和目标

## 执行步骤

1. 提炼文章主张和读者收益。
2. 给出至少 3 个标题候选，每个标题附角度。
3. 生成 5 到 7 段大纲，每段包含目的、要点和证据要求。
4. 生成 `writingPlan`，把检索、策划、正文、审稿、配图串起来。

## 输出

- `titleCandidates`
- `outline`
- `writingPlan`
- `keyTakeaways`

## 失败回退

如果资料不足以支持强结论，标题降级为问题式或经验式标题，并把缺口写入风险区。
