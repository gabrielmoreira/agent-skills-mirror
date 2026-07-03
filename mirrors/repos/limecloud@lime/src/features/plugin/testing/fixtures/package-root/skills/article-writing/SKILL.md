---
name: article-writing
description: 内容工厂正文写作技能，根据检索、大纲和标题候选生成可审核中文文章草稿。
---

# Article Writing

## 何时使用

- 已有 `researchRounds`、`titleCandidates` 和 `outline`。
- 需要生成 `articleDraft.source.processMarkdown` 和 `articleDraft.source.documentText`，并在右侧 Article Workspace 展示正式正文。

## 输入

- `contentBrief`
- `researchRounds`
- `titleCandidates`
- `outline`
- `citations`
- `imageSlots`

## 执行步骤

1. 选择最稳妥的标题作为正文标题。
2. 按大纲生成正文，小节之间保持自然过渡。
3. 把检索过程、标题候选、大纲和编排步骤写入 `processMarkdown`。
4. 把可编辑正式正文写入 `documentText` / `finalMarkdown`，不混入过程稿。
5. 不在聊天区铺正文，只返回 Article Workspace Patch。

## 输出

- `articleDraft.source.processMarkdown`
- `articleDraft.source.documentText`
- `articleDraft.source.finalMarkdown`
- `articleDraft.source.excerpt`
- `articleDraft.source.outline`
- `articleDraft.source.citations`

## 失败回退

如果无法完成完整正文，输出结构化半成品，状态标为 `needs_review`，并保留已完成小节。
