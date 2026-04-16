# AI Essentials

[![AI Essentials](https://img.shields.io/badge/AI-Essentials-blue?style=flat-square)](https://github.com/iAmMccc/ai-essentials)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)](https://github.com/iAmMccc/ai-essentials/pulls)
[![Update](https://img.shields.io/badge/持续更新中-orange?style=flat-square)](#)
[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey?style=flat-square)](https://creativecommons.org/licenses/by-sa/4.0/)



![](images/cover.png)

AI 核心知识精要 — 帮你建立一套系统的 AI 认知与实践框架。

## 文档

### 理解 AI

- [Token](docs/understanding/token/) — 大模型处理文字的最小单位，理解它才能理解上下文限制和计费逻辑
- [幻觉](docs/understanding/hallucination/) — AI 为什么会一本正经地胡说八道，以及如何应对
- [Agent](docs/understanding/agent/) — 让 AI 从「只会说」变成「能动手」的自主执行系统

### 用好 AI

- [Prompt](docs/using/prompt/) — 提示词：用户与 AI 沟通的语言，决定输出质量的第一关
- [Rules](docs/using/rules/) — 规范：让 AI 始终遵守的行为约束，写一次，持续生效
- [Skills](docs/using/skills/) — 技能：把复杂任务封装成可复用的 AI 能力模块
- [Projects](docs/using/projects/) — 项目空间：让 AI 持续理解你的项目，而不是每次从零开始
- [MCP](docs/using/mcp/) — 连接协议：让 AI 能调用外部工具和数据源，从「给建议」到「真动手」
- [完整工作流](docs/using/workflow/) — 串联：Prompt + Skills + Rules + Projects + MCP 如何协作

### 玩转 AI

> 即将更新

## Skills

开箱即用的 AI Skill，一行命令安装到你的项目中。

> **国内网络无法访问 GitHub？** 可以通过其他方式获取 `skills/` 下对应的文件夹，复制到本地即可使用，后续操作不依赖 GitHub。

### 开发工具

#### 1. 智能提交

自动分析 git diff，生成规范的中文 commit message。安装后在对话中说「帮我提交」即可触发。

[详细说明](skills/git-commit/)

```bash
curl -sL https://raw.githubusercontent.com/iAmMccc/ai-essentials/main/install-skill.sh | bash -s git-commit
```

#### 2. SPM 本地管理

通过终端下载三方库到本地，绕过 Xcode 不走 VPN 的网络限制。安装后需配置 `packages.json` 并执行脚本。

[详细说明](skills/spm-local/)

```bash
curl -sL https://raw.githubusercontent.com/iAmMccc/ai-essentials/main/install-skill.sh | bash -s spm-local
```

#### 3. UI 走查助手

对比 UI 设计稿与 App 截图，自动检查间距、对齐、颜色、字号等视觉差异，替代人工拉线对比。

[使用说明](skills/ui-diff/README.md)

```bash
curl -sL https://raw.githubusercontent.com/iAmMccc/ai-essentials/main/install-skill.sh | bash -s ui-diff
```

### 效率工具

#### 4. 智能笔记生成器

输入链接（抖音视频、微信公众号文章），自动生成结构化学习笔记。

[使用说明](skills/smart-notes/README.md)

```bash
curl -sL https://raw.githubusercontent.com/iAmMccc/ai-essentials/main/install-skill.sh | bash -s smart-notes
```
