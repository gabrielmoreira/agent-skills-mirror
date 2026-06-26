---
name: eval-harness
description: 适用于 Claude Code 会话的正规评测框架（Evaluation Framework），实现了评测驱动开发（Eval-Driven Development, EDD）原则
origin: ECC
tools: Read, Write, Edit, Bash, Grep, Glob
---

# 评测框架（Eval Harness）技能（Skill）

一个用于 Claude Code 会话的正规评测框架（Evaluation Framework），旨在落实评测驱动开发（Eval-Driven Development, EDD）原则。

## 何时激活

- 为 AI 辅助工作流设置评测驱动开发（EDD）
- 为 Claude Code 任务的完成情况定义通过/失败标准
- 使用 pass@k 指标衡量智能体（Agent）的可靠性
- 为提示词（Prompt）或智能体（Agent）的变更创建回归测试套件
- 跨模型版本对智能体（Agent）性能进行基准测试

## 核心理念

评测驱动开发（Eval-Driven Development）将评测（Eval）视为“AI 开发中的单元测试”：
- 在实现**之前**定义预期行为
- 在开发过程中持续运行评测（Evals）
- 跟踪每次变更带来的回归（Regressions）
- 使用 pass@k 指标进行可靠性度量

## 评测类型

### 能力评测（Capability Evals）
测试 Claude 是否能够完成其之前无法完成的任务：
```markdown
[CAPABILITY EVAL: feature-name]
Task: 描述 Claude 应该完成的任务
Success Criteria:
  - [ ] 准则 1
  - [ ] 准则 2
  - [ ] 准则 3
Expected Output: 预期结果的描述
```

### 回归评测（Regression Evals）
确保变更不会破坏现有功能：
```markdown
[REGRESSION EVAL: feature-name]
Baseline: SHA 或检查点（checkpoint）名称
Tests:
  - existing-test-1: PASS/FAIL
  - existing-test-2: PASS/FAIL
  - existing-test-3: PASS/FAIL
Result: X/Y 通过 (之前为 Y/Y)
```

## 评分器（Grader）类型

### 1. 基于代码的评分器（Code-Based Grader）
使用代码进行确定性检查：
```bash
# 检查文件是否包含预期模式
grep -q "export function handleAuth" src/auth.ts && echo "PASS" || echo "FAIL"

# 检查测试是否通过
npm test -- --testPathPattern="auth" && echo "PASS" || echo "FAIL"

# 检查构建是否成功
npm run build && echo "PASS" || echo "FAIL"
```

### 2. 基于模型的评分器（Model-Based Grader）
使用 Claude 对开放式输出进行评估：
```markdown
[MODEL GRADER PROMPT]
评估以下代码变更：
1. 它是否解决了所述问题？
2. 结构是否良好？
3. 是否处理了边缘情况？
4. 错误处理是否恰当？

Score: 1-5 (1=差, 5=优秀)
Reasoning: [解释]
```

### 3. 人工评分器（Human Grader）
标记以供人工复核：
```markdown
[HUMAN REVIEW REQUIRED]
Change: 变更内容描述
Reason: 为何需要人工复核
Risk Level: LOW/MEDIUM/HIGH
```

## 指标（Metrics）

### pass@k
“在 k 次尝试中至少成功一次”
- pass@1: 首次尝试成功率
- pass@3: 3 次尝试内的成功率
- 典型目标：pass@3 > 90%

### pass^k
“所有 k 次试验均成功”
- 更高的可靠性门槛
- pass^3: 连续 3 次成功
- 用于关键路径（Critical Paths）

## 评测工作流（Eval Workflow）

### 1. 定义（编码前）
```markdown
## EVAL DEFINITION: feature-xyz

### 能力评测（Capability Evals）
1. 能够创建新用户账号
2. 能够验证邮箱格式
3. 能够安全地哈希密码

### 回归评测（Regression Evals）
1. 现有登录功能仍然正常
2. 会话管理未改变
3. 注销流程完好无损

### 成功指标
- 能力评测的 pass@3 > 90%
- 回归评测的 pass^3 = 100%
```

### 2. 实现
编写代码以通过定义的评测（Evals）。

### 3. 评测
```bash
# 运行能力评测
[运行每个能力评测，记录 PASS/FAIL]

# 运行回归评测
npm test -- --testPathPattern="existing"

# 生成报告
```

### 4. 报告
```markdown
EVAL REPORT: feature-xyz
========================

Capability Evals:
  create-user:     PASS (pass@1)
  validate-email:  PASS (pass@2)
  hash-password:   PASS (pass@1)
  Overall:         3/3 passed

Regression Evals:
  login-flow:      PASS
  session-mgmt:    PASS
  logout-flow:     PASS
  Overall:         3/3 passed

Metrics:
  pass@1: 67% (2/3)
  pass@3: 100% (3/3)

Status: READY FOR REVIEW
```

## 集成模式（Integration Patterns）

### 实现前
```
/eval define feature-name
```
在 `.claude/evals/feature-name.md` 创建评测定义文件

### 实现中
```
/eval check feature-name
```
运行当前评测并报告状态

### 实现后
```
/eval report feature-name
```
生成完整的评测报告

## 评测存储（Eval Storage）

在项目中存储评测（Evals）：
```
.claude/
  evals/
    feature-xyz.md      # 评测定义
    feature-xyz.log     # 评测运行历史
    baseline.json       # 回归基准
```

## 最佳实践

1. **在编码之前定义评测** - 强制对成功标准进行清晰思考
2. **频繁运行评测** - 尽早发现回归问题
3. **长期跟踪 pass@k** - 监控可靠性趋势
4. **尽可能使用代码评分器** - 确定性 > 概率性
5. **安全相关的由人工复核** - 绝不要完全自动化安全检查
6. **保持评测速度快** - 慢的评测不会被经常运行
7. **评测与代码版本同步** - 评测是一等公民（First-class Artifacts）

## 示例：添加身份验证（Authentication）

```markdown
## EVAL: add-authentication

### 阶段 1：定义 (10 分钟)
能力评测：
- [ ] 用户可以使用邮箱/密码注册
- [ ] 用户可以使用有效凭据登录
- [ ] 无效凭据被拒绝并返回正确错误
- [ ] 会话在页面重新加载后保持
- [ ] 注销会清除会话

回归评测：
- [ ] 公共路由仍然可以访问
- [ ] API 响应未改变
- [ ] 数据库架构兼容

### 阶段 2：实现 (时间视情况而定)
[编写代码]

### 阶段 3：评测
运行：/eval check add-authentication

### 阶段 4：报告
EVAL REPORT: add-authentication
==============================
Capability: 5/5 passed (pass@3: 100%)
Regression: 3/3 passed (pass^3: 100%)
Status: SHIP IT (可以发布)
```