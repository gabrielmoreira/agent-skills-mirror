---
description: "通用模式：仓库（Repository）、API 响应、骨架项目（Skeleton Projects）"
alwaysApply: true
---
# 通用模式 (Common Patterns)

## 骨架项目 (Skeleton Projects)

在实现新功能时：
1. 搜索经过实战检验的骨架项目 (Skeleton Projects)
2. 使用并行智能体 (Parallel Agents) 评估选项：
   - 安全评估 (Security assessment)
   - 可扩展性分析 (Extensibility analysis)
   - 相关性评分 (Relevance scoring)
   - 实施规划 (Implementation planning)
3. 克隆最佳匹配项作为基础
4. 在成熟的结构内进行迭代

## 设计模式 (Design Patterns)

### 仓库模式 (Repository Pattern)

将数据访问封装在一致的接口背后：
- 定义标准操作：`findAll`、`findById`、`create`、`update`、`delete`
- 具体实现负责处理存储细节（数据库、API、文件等）
- 业务逻辑依赖于抽象接口，而非具体的存储机制
- 支持轻松更换数据源，并简化使用 Mock 的测试过程

### API 响应格式 (API Response Format)

为所有 API 响应使用一致的外壳 (Envelope)：
- 包含成功/状态指示器 (Success/Status indicator)
- 包含数据负载 (Data payload)（发生错误时可为空）
- 包含错误消息字段 (Error message)（成功时可为空）
- 包含分页响应的元数据 (Metadata)（total, page, limit）
