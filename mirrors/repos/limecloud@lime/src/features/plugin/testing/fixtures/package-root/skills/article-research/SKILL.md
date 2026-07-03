---
name: article-research
description: 内容工厂写文章前的资料检索技能，整理三轮检索、引用、核心判断和风险。
---

# Article Research

## 何时使用

- 用户通过 `@写文章` 或 `@写作` 发起文章任务。
- 需要先整理资料、引用、上下文和风险，再进入正文写作。

## 输入

- 主题、读者、渠道、目标和语气
- 用户提供的 references、截图、上下文或历史素材
- 当前工作流 metadata

## 执行步骤

1. 明确主题、读者问题和文章目标。
2. 做三轮资料整理：主题目标、场景痛点、结构和发布要求。
3. 给每轮资料保留 query、summary、citations 和 status。
4. 汇总 `keyTakeaways`、`citations` 和 `riskFlags`。

## 输出

- `researchRounds`
- `citations`
- `keyTakeaways`
- `riskFlags`

## 失败回退

资料不足时输出 `needs_review`，并写明需要用户补充什么，不编造来源。
