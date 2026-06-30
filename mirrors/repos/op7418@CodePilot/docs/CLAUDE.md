# Docs 目录

- `design.md` — UI 设计规范（基于 Settings > Providers / Models 沉淀的卡片 / 分割线 / 徽章 / preview 流程等模式；新加 Settings 页面前先读这份）
- `guardrails/` — 模块级开发契约（不变量 / 关键文件 / 常见坑 / 测试）；改 chat / runtime / provider / 模型选择相关代码前必读对应文档
- `rules/` — 流程规则（汇报协议 / 完成状态词典 / 发版细则）；顶层 CLAUDE.md / AGENTS.md 的长流程拆到这里
- `handover/` — 交接文档（架构、数据流、设计决策）
- `research/` — 调研文档（技术方案、可行性分析）
- `exec-plans/` — 执行计划（`active/` 进行中、`completed/` 已完成）+ 技术债务追踪

**规则：**
- 检索子目录前先读对应 README.md；增删文件后更新 README.md 索引
- 纯调研放 `research/`；有明确分阶段步骤的放 `exec-plans/active/`
- 执行计划完成后移至 `exec-plans/completed/`
- 设计规范变更后同步更新 `design.md` 的 anchor implementations 表
