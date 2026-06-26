---
description: "ECC 编码规范：不可变性（Immutability）、文件组织、错误处理、验证"
alwaysApply: true
---
# 编码规范（Coding Style）

## 不可变性（Immutability）（至关重要）

始终（ALWAYS）创建新对象，绝不（NEVER）修改（mutate）现有对象：

```
// 伪代码（Pseudocode）
错误（WRONG）： modify(original, field, value) → 原地修改原对象
正确（CORRECT）：update(original, field, value) → 返回包含变更的新副本
```

原理（Rationale）：不可变数据可防止隐藏的副作用，使调试更容易，并实现安全的并发（Concurrency）。

## 文件组织（File Organization）

多而小的文件 > 少而大的文件：
- 高内聚，低耦合（High cohesion, low coupling）
- 通常 200-400 行，最大 800 行
- 从大型模块中提取工具函数（Utilities）
- 按功能/领域（Feature/Domain）组织，而不是按类型（Type）组织

## 错误处理（Error Handling）

始终（ALWAYS）全面处理错误：
- 在每个层级显式（Explicitly）处理错误
- 在面向 UI 的代码中提供用户友好的错误消息
- 在服务端记录详细的错误上下文（Context）
- 绝不静默吞掉（Swallow）错误

## 输入验证（Input Validation）

始终（ALWAYS）在系统边界进行验证：
- 在处理之前验证所有用户输入
- 尽可能使用基于模式（Schema）的验证
- 快速失败（Fail fast）并提供清晰的错误消息
- 绝不信任外部数据（API 响应、用户输入、文件内容）

## 代码质量自查表（Code Quality Checklist）

在标记工作完成之前：
- [ ] 代码易读且命名良好
- [ ] 函数简短（<50 行）
- [ ] 文件职责集中（<800 行）
- [ ] 无深层嵌套（>4 层）
- [ ] 正确的错误处理
- [ ] 无硬编码值（使用常量或配置）
- [ ] 无修改/变异（使用不可变模式）
