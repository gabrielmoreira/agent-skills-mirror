# 完整工作流：四个概念如何串联

> 用好 AI

前面几篇分别讲了 [Prompt](../prompt/)、[Rules](../rules/) + [Skills](../skills/)、[Projects](../projects/)、[MCP](../mcp/)。它们各自解决一个问题，但真正发挥威力是在组合使用时。

---

## 一条完整的链路

```
Prompt   →  告诉 AI「做什么」
Skills   →  告诉 AI「按什么流程做」
Rules    →  约束 AI「过程中遵守什么」
Projects →  提供「项目背景和持久上下文」
MCP      →  连接「外部系统，真正执行操作」
```

对应到 iOS 开发者熟悉的概念：

| AI 概念 | iOS 类比 |
|---------|---------|
| Prompt | 函数调用 |
| Skills | Framework 能力 |
| Rules | 编码规范 |
| Projects | Xcode Project |
| MCP | REST API 调用 |

---

## 一个完整的例子

假设你在开发一个 iOS 翻译 App，要实现「图片 OCR + 翻译」功能。看看五个概念如何协作：

### 第一步：Prompt — 发起任务

你对 AI 说：

> 「用 Swift 实现图片 OCR + 翻译流程，支持中英互译，使用 Vision 框架做 OCR。」

这是整条链路的起点。Prompt 定义了「做什么」。

### 第二步：Skills — 按流程执行

AI 匹配到已有的 Skills：

- **iOS 功能开发 Skill**：按「需求分析 → 接口设计 → 代码实现 → 测试」的标准流程推进
- **Code Review Skill**：代码写完后自动做一轮自审

Skills 定义了「按什么流程做」，保证执行质量稳定。

### 第三步：Rules — 遵守规范

整个过程中，AI 自动遵守项目的 Rules：

- UI 用 SnapKit 布局，不用 Storyboard
- 网络请求通过 Service 层，ViewController 不直接调用
- 错误处理要用 Logger，不用 print
- 新代码要有单元测试

Rules 约束了「过程中遵守什么」，不需要每次提醒。

### 第四步：Projects — 利用项目上下文

AI 在你的项目空间中工作，可以：

- 读取现有的 Service 层代码，了解网络请求的封装方式
- 查看 Models/ 目录，复用已有的数据模型
- 参考 CLAUDE.md 中的技术栈信息和目录约定
- 基于之前的对话记录，了解架构决策的背景

Projects 提供了「项目背景和持久上下文」，AI 不需要从零了解你的项目。

### 第五步：MCP — 连接真实系统

AI 通过 MCP 调用外部工具完成实际操作：

- 读写项目文件（filesystem Server）
- 查看 Git 历史和创建分支（github Server）
- 查询 OCR API 和翻译 API 的文档（browser Server）
- 运行测试并获取结果

MCP 让 AI 从「给你建议」变成「直接动手做」。

---

## 串联起来

```
你说「实现图片 OCR + 翻译」               ← Prompt
    ↓
AI 按功能开发 Skill 的标准流程推进          ← Skills
    ↓
过程中自动遵守 SnapKit、Service 层等规范    ← Rules
    ↓
读取项目代码和文档，基于现有架构实现         ← Projects
    ↓
读写文件、查 API 文档、运行测试             ← MCP
    ↓
输出：完整的 OCR + 翻译模块代码
```

**五个概念各管一层，缺一不可：**

- 没有 Prompt → AI 不知道做什么
- 没有 Skills → AI 没有标准流程，输出质量不稳定
- 没有 Rules → AI 不遵守团队规范，代码风格混乱
- 没有 Projects → AI 不了解项目背景，每次从零开始
- 没有 MCP → AI 不能操作真实系统，只能纸上谈兵

这就是 AI 工作体系的完整图景。每个概念解决一个层面的问题，组合在一起，AI 才能从「聊天工具」变成「真正的协作伙伴」。
