---
name: article-editing
description: 内容工厂审稿校对技能，检查事实、结构、语气、发布风险和修改建议。
---

# Article Editing

## 何时使用

- 已生成 `articleDraft`。
- 需要发布前复核、交付检查或继续改稿。

## 输入

- 文章 Markdown
- 引用、风险、配图占位
- 渠道和目标读者

## 执行步骤

1. 检查结构是否完整。
2. 检查事实和引用是否匹配。
3. 检查语气是否符合渠道。
4. 生成交付检查清单和修改建议。

## 输出

- `deliveryChecklist`
- `reviewNotes`
- `riskFlags`

## 失败回退

如果正文缺失，只输出缺口清单，不生成发布结论。
