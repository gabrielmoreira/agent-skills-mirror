---
name: verification-loop
description: "为 Claude Code 会话提供的全面验证系统。"
origin: ECC
---

# 验证循环技能 (Verification Loop Skill)

为 Claude Code 会话（Sessions）提供的全面验证系统。

## 何时使用

在以下场景调用此技能（Skill）：
- 完成功能开发或重大代码变更后
- 创建拉取请求（PR）之前
- 希望确保质量关卡（Quality Gates）全部通过时
- 重构代码后

## 验证阶段

### 阶段 1：构建验证 (Build Verification)
```bash
# 检查项目是否能成功构建
npm run build 2>&1 | tail -20
# 或者
pnpm build 2>&1 | tail -20
```

如果构建失败，请**停止**并在继续之前进行修复。

### 阶段 2：类型检查 (Type Check)
```bash
# TypeScript 项目
npx tsc --noEmit 2>&1 | head -30

# Python 项目
pyright . 2>&1 | head -30
```

报告所有类型错误。在继续之前修复关键错误。

### 阶段 3：代码规范检查 (Lint Check)
```bash
# JavaScript/TypeScript
npm run lint 2>&1 | head -30

# Python
ruff check . 2>&1 | head -30
```

### 阶段 4：测试套件 (Test Suite)
```bash
# 运行带有覆盖率报告的测试
npm run test -- --coverage 2>&1 | tail -50

# 检查覆盖率阈值
# 目标：最低 80%
```

报告内容：
- 测试总数：X
- 通过：X
- 失败：X
- 覆盖率：X%

### 阶段 5：安全扫描 (Security Scan)
```bash
# 检查是否存在密钥泄露
grep -rn "sk-" --include="*.ts" --include="*.js" . 2>/dev/null | head -10
grep -rn "api_key" --include="*.ts" --include="*.js" . 2>/dev/null | head -10

# 检查是否存在 console.log
grep -rn "console.log" --include="*.ts" --include="*.tsx" src/ 2>/dev/null | head -10
```

### 阶段 6：差异审查 (Diff Review)
```bash
# 显示变更内容
git diff --stat
git diff HEAD~1 --name-only
```

审查每个变更的文件，重点关注：
- 非预期的变更
- 遗漏的错误处理
- 潜在的边缘情况

## 输出格式

在运行所有阶段后，生成一份验证报告：

```
验证报告 (VERIFICATION REPORT)
==================

构建 (Build):       [通过/失败]
类型 (Types):       [通过/失败] (X 个错误)
规范 (Lint):        [通过/失败] (X 个警告)
测试 (Tests):       [通过/失败] (通过 X/Y，覆盖率 Z%)
安全 (Security):    [通过/失败] (X 个问题)
差异 (Diff):        [X 个文件已变更]

总体结论 (Overall): [就绪/未就绪] 提交 PR

待修复问题：
1. ...
2. ...
```

## 持续模式 (Continuous Mode)

对于长时间的会话，请每隔 15 分钟或在重大变更后运行一次验证：

```markdown
设定心理检查点：
- 完成每个函数后
- 完成一个组件后
- 在转向下一个任务前

运行：/verify
```

## 与钩子（Hooks）集成

此技能是对 `PostToolUse` 钩子的补充，但提供了更深层次的验证。
钩子（Hooks）能立即捕获问题；此技能则提供全面的审查。
