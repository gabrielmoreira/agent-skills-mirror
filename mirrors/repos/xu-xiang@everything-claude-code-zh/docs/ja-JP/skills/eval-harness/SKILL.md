---
name: eval-harness
description: Claude Code 会话的正式评测框架，实现了评测驱动开发（EDD）原则
tools: Read, Write, Edit, Bash, Grep, Glob
---

# 评测工具集（Eval Harness）技能

Claude Code 会话的正式评测框架，实现了评测驱动开发（Evaluation-Driven Development, EDD）原则。

## 哲学

评测驱动开发将评测视为“AI 开发的单元测试”：
- 在实现前定义预期行为
- 开发过程中持续运行评测
- 追踪每次变更的回归情况
- 使用 pass@k 指标衡量可靠性

## 评测类型

### 能力评测（Capability Eval）
测试 Claude 是否能够完成以前无法完成的任务：
```markdown
[CAPABILITY EVAL: feature-name]
任务：Claude 应达成目标的描述
成功标准：
  - [ ] 标准 1
  - [ ] 标准 2
  - [ ] 标准 3
预期输出：预期结果的描述
```

### 回归评测（Regression Eval）
确保变更未破坏现有功能：
```markdown
[REGRESSION EVAL: feature-name]
基线（Baseline）：SHA 或检查点名称
测试：
  - existing-test-1: PASS/FAIL
  - existing-test-2: PASS/FAIL
  - existing-test-3: PASS/FAIL
结果：X/Y 通过（之前为 Y/Y）
```

## 评测者类型

### 1. 代码库评测者（Codebase Graders）
使用代码进行确定性检查：
```bash
# 检查文件中是否包含预期模式
grep -q "export function handleAuth" src/auth.ts && echo "PASS" || echo "FAIL"

# 检查测试是否成功
npm test -- --testPathPattern="auth" && echo "PASS" || echo "FAIL"

# 检查构建是否成功
npm run build && echo "PASS" || echo "FAIL"
```

### 2. 基于模型的评测者（Model-Based Graders）
使用 Claude 评测自由格式的输出：
```markdown
[MODEL GRADER PROMPT]
请评估以下代码变更：
1. 是否解决了所述问题？
2. 结构是否合理？
3. 是否处理了边界情况？
4. 错误处理是否得当？

Score: 1-5 (1=差, 5=优秀)
Reasoning: [说明]
```

### 3. 人工评测者（Human Graders）
标记需要手动复审：
```markdown
[HUMAN REVIEW REQUIRED]
变更：变更内容的说明
原因：需要人工复审的原因
风险等级：LOW/MEDIUM/HIGH
```

## 指标

### pass@k
“k 次尝试中至少成功 1 次”
- pass@1: 首次尝试的成功率
- pass@3: 3 次以内的成功率
- 常见目标：pass@3 > 90%

### pass^k
“k 次尝试全部成功”
- 更高可靠性的标准
- pass^3: 连续 3 次成功
- 用于关键路径（Critical Path）

## 评测工作流

### 1. 定义（编码前）
```markdown
## 评测定义：feature-xyz (EVAL DEFINITION: feature-xyz)

### 能力评测
1. 能够创建新用户账号
2. 能够验证邮箱格式
3. 能够安全地哈希化密码

### 回归评测
1. 现有登录功能依然可用
2. 会话管理未发生变更
3. 退出流程得以维持

### 成功指标
- 能力评测 pass@3 > 90%
- 回归评测 pass^3 = 100%
```

### 2. 实现
编写符合已定义评测要求的代码。

### 3. 评测
```bash
# 运行能力评测
[运行各能力评测并记录 PASS/FAIL]

# 运行回归评测
npm test -- --testPathPattern="existing"

# 生成报告
```

### 4. 报告
```markdown
评测报告：feature-xyz (EVAL REPORT: feature-xyz)
========================

能力评测：
  create-user:     通过 (PASS) (pass@1)
  validate-email:  通过 (PASS) (pass@2)
  hash-password:   通过 (PASS) (pass@1)
  总体：           3/3 通过

回归评测：
  login-flow:      通过 (PASS)
  session-mgmt:    通过 (PASS)
  logout-flow:     通过 (PASS)
  总体：           3/3 通过

指标：
  pass@1: 67% (2/3)
  pass@3: 100% (3/3)

状态：可供评审 (READY FOR REVIEW)
```

## 集成模式

### 实现前
```
/eval define feature-name
```
在 `.claude/evals/feature-name.md` 中创建评测定义文件。

### 实现中
```
/eval check feature-name
```
执行当前评测并报告状态。

### 实现后
```
/eval report feature-name
```
生成完整的评测报告。

## 评测存储

在项目中存储评测：
```
.claude/
  evals/
    feature-xyz.md      # 评测定义
    feature-xyz.log     # 评测执行历史
    baseline.json       # 回归基线
```

## 最佳实践

1. **编码前定义评测** —— 强制明确思考成功标准。
2. **频繁运行评测** —— 及早发现回归问题。
3. **追踪 pass@k 随时间的变化** —— 监控可靠性趋势。
4. **尽可能使用代码评测者** —— 确定性 > 概率性。
5. **安全问题由人工复审** —— 不要完全自动执行安全检查。
6. **保持评测高效** —— 缓慢的评测将不会被执行。
7. **评测与代码版本管理同步** —— 评测是一等公民产物。

## 示例：添加身份验证

```markdown
## 评测：添加身份验证 (EVAL: add-authentication)

### 第一阶段：定义 (10 分钟)
能力评测：
- [ ] 用户可以通过邮箱/密码注册
- [ ] 用户可以使用有效的凭据登录
- [ ] 无效凭据会被拒绝并返回适当错误
- [ ] 页面刷新后会话依然持久
- [ ] 退出登录会清除会话

回归评测：
- [ ] 公开路由依然可以访问
- [ ] API 响应未发生变更
- [ ] 数据库模式保持兼容

### 第二阶段：实现 (时长不定)
[编写代码]

### 第三阶段：评测
运行：/eval check add-authentication

### 第四阶段：报告
评测报告：添加身份验证 (EVAL REPORT: add-authentication)
==============================
能力：5/5 通过 (pass@3: 100%)
回归：3/3 通过 (pass^3: 100%)
状态：可以上线 (SHIP IT)
```
