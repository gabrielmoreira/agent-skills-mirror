---
name: continuous-learning
description: 自动从 Claude Code 会话（Session）中提取可重用的模式（Pattern），并将其作为已学习的技能（Skill）保存以备将来使用。
---

# 持续学习技能（Continuous Learning Skill）

Claude Code 会话结束时自动进行评估，提取可作为已学习技能保存的可重用模式（Pattern）。

## 工作原理（How it Works）

此技能在每个会话结束时作为 **Stop 钩子（Hook）** 执行：

1. **会话评估**：检查会话是否有足够的消息（默认：10 条以上）
2. **模式检测**：识别可从会话中提取的模式
3. **技能提取**：将有用的模式保存到 `~/.claude/skills/learned/`

## 配置（Configuration）

通过编辑 `config.json` 进行自定义：

```json
{
  "min_session_length": 10,
  "extraction_threshold": "medium",
  "auto_approve": false,
  "learned_skills_path": "~/.claude/skills/learned/",
  "patterns_to_detect": [
    "error_resolution",
    "user_corrections",
    "workarounds",
    "debugging_techniques",
    "project_specific"
  ],
  "ignore_patterns": [
    "simple_typos",
    "one_time_fixes",
    "external_api_issues"
  ]
}
```

## 模式类型（Pattern Types）

| 模式 | 描述 |
|---------|-------------|
| `error_resolution` | 特定错误的解决方法 |
| `user_corrections` | 来自用户修正的模式 |
| `workarounds` | 针对框架/库特性的解决方案 |
| `debugging_techniques` | 有效的调试方法（Debugging Approaches） |
| `project_specific` | 项目特定的约定 |

## 钩子配置（Hook Configuration）

添加到 `~/.claude/settings.json`：

```json
{
  "hooks": {
    "Stop": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/skills/continuous-learning/evaluate-session.sh"
      }]
    }]
  }
}
```

## 为什么使用 Stop 钩子

- **轻量**：仅在会话（Session）结束时执行一次
- **非阻塞**：不会给每条消息增加延迟（Latency）
- **完整上下文**：可以访问整个会话的转录内容

## 相关项目

- [The Longform Guide](https://x.com/affaanmustafa/status/2014040193557471352) - 关于持续学习的部分
- `/learn` 命令 - 会话中的手动模式提取

---

## 对比笔记（调查：2025年1月）

### vs Homunculus

Homunculus v2 采用了更精细的方法：

| 功能 | 当前方法 | Homunculus v2 |
|---------|--------------|---------------|
| 观察 | Stop 钩子 (会话结束时) | PreToolUse/PostToolUse 钩子 (100% 可靠性) |
| 分析 | 主上下文 (Main Context) | 后台智能体 (Background Agent, Haiku) |
| 粒度 | 完整的技能 | 原子级的“本能 (Instinct)” |
| 置信度 | 无 | 0.3-0.9 的权重分配 |
| 演进 | 直接转换为技能 | 本能 → 集群 → 技能/命令/智能体 |
| 共享 | 无 | 本能的导出/导入 |

**homunculus 的重要洞察：**
> "v1 依赖技能进行观察。技能是概率性的，触发率约为 50-80%。v2 使用钩子（100% 可靠性）进行观察，并使用本能作为学习行为的原子单位。"

### v2 的潜在改进

1. **基于本能的学习** - 具有置信度评分的更小、原子级的行为
2. **后台观察者** - 并行分析的 Haiku 智能体
3. **置信度衰减** - 在发生冲突时降低本能的置信度
4. **领域标签** - 代码风格、测试、git、调试等
5. **演进路径** - 将相关的本能聚类为技能/命令/智能体

详细信息：请参阅 `/Users/affoon/Documents/tasks/12-continuous-learning-v2.md`。
