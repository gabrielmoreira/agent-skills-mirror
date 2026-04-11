---
name: agent-stream-nesting-logic
description: 万悟平台 SSE 子会话递归嵌套与三明治序列渲染架构指南。涵盖 parentId 领养、order 绝对排序、动静 Chunk 分层及 Vue 2 响应式引用协议。
---

# 子会话递归嵌套渲染架构协议 (Nesting Architecture Protocol)

本指南针对万悟平台中「主消息 -> 子会话 (Skill/Tool/Knowledge) -> 孙级会话」的递归序列化渲染标准，定义了 AI 助手及后续维护者必须遵守的底层逻辑。

## 1. 核心模型：三明治序列 (The Sandwich Sequence)
为了支持正文与多个子会话（工具调用、知识库）的任意插空排列，我们不再按类型分块渲染，而是通过 `messageSequence` 数组实现**“三明治”交错结构**。

- **`type: 'main'`**: 文本片段。直接由 `StreamProcessor` 驱动打字机渲染。
- **`type: 'sub'`**: 子会话卡片。触发 `SubConversion.vue` 组件递归渲染。

### 核心映射逻辑：
- **顶级子会话**: `parentId` 为空的包，进入主消息的 `messageSequence`。
- **嵌套子会话**: 具有 `parentId` 的包，必须由对应的父组件 ID “领养”，存入其自身的 `messageSequence` 中。

## 2. 时序法则：Order 绝对排序
- **局部闭包排序**: 在每一个 `messageSequence` 内部，必须以 `order` 字段为唯一权重进行升序排列。
- **同 Order 追加协定**: 若同一个 ID 下出现多个 Order 相同的数据包，前端视为“内容的物理追加”而非“组件的新增”。

## 3. 动力学：动静 Chunk 分层
在渲染 `main` 片段时，必须区分两种状态以防止打字时界面闪烁：
- **`stableChunks`**: 已完成 Markdown 语法闭环解析并生成的 HTML 块集合。
- **`activeResponse`**: 正在缓冲区排队、尚未完成闭环解析的输入文本（打字动画部分）。

## 4. 引用溯源：Data Attributes 协议
所有生成的子会话 DOM 必须携带以下身份锚点，以支持「引文角标点击」的事件冒泡定位：
- **`data-sub-id`**: 该段文字所属的原子消息 ID（若是吸收片段，则为分片 ID）。
- **`data-parent-id`**: 视觉所属的容器组件 ID（父卡片 ID）。

## 5. 响应式红线 (CRITICAL) - Vue 2 专供
> [!IMPORTANT]
> **绝对禁止使用浅拷贝或快照！**
> 
> 在将子会话（尤其是 `agentSkillText` 正文分段）注册进父组件序列时，**必须直接传递原始响应式对象的引用**（即 `parentSub.messageSequence.push(subConversion)`）。
> 
> - **原因**: 只有保持引用一致，外部 `StreamProcessor` 对 `activeResponse` 的实时增长才能无缝穿透进多层嵌套的子组件 UI 中。若使用 `{...subConversion}` 浅拷贝，会导致打字效果丢失或不连续。

## 6. 生命周期管理
- **状态单向锁**: 状态 `status: 3/4`（结束/失败）一旦更新，不再受后续包干扰回退。
- **ID 纠错逻辑**: 若后端返回 `id === parentId`（自引用死循环），必须在 `sseMethod.js` 拦截层将其重刷 ID 为 `content_` 前缀的分片包。
