---
description: "测试要求：80% 覆盖率、TDD 工作流、测试类型"
alwaysApply: true
---
# 测试要求 (Testing Requirements)

## 最低测试覆盖率：80%

测试类型（全部必选）：
1. **单元测试 (Unit Tests)** - 独立函数、工具类、组件
2. **集成测试 (Integration Tests)** - API 接口、数据库操作
3. **端到端测试 (E2E Tests)** - 关键用户流程（根据语言选择框架）

## 测试驱动开发 (Test-Driven Development)

强制 (MANDATORY) 工作流：
1. 先编写测试（红灯阶段 - RED）
2. 运行测试 - 应当失败 (FAIL)
3. 编写最小化实现（绿灯阶段 - GREEN）
4. 运行测试 - 应当通过 (PASS)
5. 重构（改进阶段 - IMPROVE）
6. 验证覆盖率 (80%+)

## 测试失败排查

1. 使用 **tdd-guide** 智能体 (Agent)
2. 检查测试隔离性 (Test Isolation)
3. 验证 Mock 是否正确
4. 修复实现逻辑，而非测试代码（除非测试用例本身有误）

## 智能体支持 (Agent Support)

- **tdd-guide** - 主动 (PROACTIVELY) 用于新功能开发，强制执行“测试先行 (Write-tests-first)”原则
