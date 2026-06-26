---
description: "性能优化：模型选择、上下文管理、构建故障排除"
alwaysApply: true
---
# 性能优化 (Performance Optimization)

## 模型选择策略 (Model Selection Strategy)

**Haiku 4.5** (具备 Sonnet 90% 的能力，成本降低 3 倍):
- 频繁调用的轻量级智能体 (Agents)
- 结对编程与代码生成
- 多智能体系统中的工作智能体 (Worker agents)

**Sonnet 4.6** (最佳编程模型):
- 主要开发工作
- 编排多智能体工作流 (Orchestrating multi-agent workflows)
- 复杂的编程任务

**Opus 4.5** (最深层的推理能力):
- 复杂的架构决策
- 极高的推理需求
- 研究与分析任务

## 上下文窗口管理 (Context Window Management)

避免在上下文窗口 (Context Window) 最后 20% 的容量内执行以下操作：
- 大规模重构
- 跨越多个文件的功能实现
- 调试复杂的交互行为

对上下文敏感度较低的任务：
- 单个文件编辑
- 独立实用工具的创建
- 文档更新
- 简单的 Bug 修复

## 扩展思考 (Extended Thinking) + 计划模式 (Plan Mode)

扩展思考（Extended Thinking）默认开启，为内部推理预留高达 31,999 个 Token。

通过以下方式控制扩展思考：
- **切换开关**: Option+T (macOS) / Alt+T (Windows/Linux)
- **配置文件**: 在 `~/.claude/settings.json` 中设置 `alwaysThinkingEnabled`
- **预算上限**: `export MAX_THINKING_TOKENS=10000`
- **详细模式**: Ctrl+O 查看思考过程输出

对于需要深层推理的复杂任务：
1. 确保扩展思考已开启（默认开启）
2. 开启 **计划模式 (Plan Mode)** 以使用结构化方法
3. 进行多轮审阅以实现透彻分析
4. 使用分工明确的子智能体 (Sub-agents) 以获得多样化的视角

## 构建故障排除 (Build Troubleshooting)

如果构建失败：
1. 使用 **build-error-resolver** 智能体
2. 分析错误信息
3. 进行增量修复
4. 每次修复后进行验证
