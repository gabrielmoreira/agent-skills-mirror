---
name: article-image-plan
description: 内容工厂文章配图技能，根据正文段落规划封面、段落图、信息图和图片生成提示。
---

# Article Image Plan

## 何时使用

- 文章已有标题、大纲或正文。
- 需要把配图占位写入文章对象和图片生成组。

## 输入

- `articleDraft.source.documentText`
- `outline`
- 渠道、读者、语气

## 执行步骤

1. 识别封面图、解释图、流程图和段落插图位置。
2. 每个图片占位绑定 section、purpose 和 prompt。
3. 图片提示必须服务正文，不做纯装饰。
4. 输出给后续图片执行器，不直接调用 Provider。

## 输出

- `imageSlots`
- `imageGenerationSet.source.images`
- `coverPrompt`

## 失败回退

正文不足时只生成封面和大纲级配图建议，并标记 `pending_article_detail`。
