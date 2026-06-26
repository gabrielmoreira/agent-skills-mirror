---
name: strategic-compact
description: 建议在逻辑间隔处进行手动压缩（Manual Compaction），以在整个任务阶段保持上下文（Context），而非随意的自动压缩。
---

# 策略性压缩（Strategic Compact）技能

建议在工作流的战略点手动执行 `/compact` 命令，而不是依赖随意的自动压缩。

## 为什么需要策略性压缩？

自动压缩会在任意点触发：
- 通常发生在任务中途，导致丢失关键上下文
- 无法识别任务的逻辑边界
- 可能会中断复杂的跨步骤操作

在逻辑边界处进行策略性压缩：
- **探索后、执行前** - 压缩研究上下文，保留实现计划
- **里程碑完成后** - 为下一阶段开启全新开始
- **重大上下文切换前** - 在处理不同任务前清理探索上下文

## 工作原理

`suggest-compact.sh` 脚本在工具调用前（PreToolUse，针对 Edit/Write）执行：

1. **追踪工具调用** - 统计会话（Session）内的工具调用次数
2. **阈值检测** - 达到可配置阈值时给出建议（默认：50 次）
3. **定期提醒** - 超过阈值后每 25 次调用提醒一次

## 钩子（Hook）配置

添加到 `~/.claude/settings.json`：

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "tool == \"Edit\" || tool == \"Write\"",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/skills/strategic-compact/suggest-compact.sh"
      }]
    }]
  }
}
```

## 配置

环境变量：
- `COMPACT_THRESHOLD` - 触发首次建议前的工具调用次数（默认：50）

## 最佳实践

1. **计划后压缩** - 计划确定后，进行压缩并全新开始
2. **调试后压缩** - 在继续前清理错误解决上下文
3. **实现过程中不压缩** - 为相关变更保留上下文
4. **阅读建议** - 钩子（Hook）会提示*何时*压缩，但*是否执行*由你决定

## 相关资源

- [The Longform Guide](https://x.com/affaanmustafa/status/2014040193557471352) - 令牌（Token）优化章节
- 内存持久化钩子 - 用于在压缩后仍需保留的状态
