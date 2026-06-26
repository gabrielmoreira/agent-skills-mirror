# 验证循环（Verification Loop）技能

针对 Claude Code 会话的全面验证系统。

## 使用场景

在以下情况调用此技能：
- 完成功能或重大代码变更后
- 创建拉取请求（PR）之前
- 需要确认质量门禁（Quality Gates）是否通过时
- 重构代码之后

## 验证阶段

### 阶段 1：构建验证（Build Verification）
```bash
# 确认项目是否可以构建
npm run build 2>&1 | tail -20
# 或者
pnpm build 2>&1 | tail -20
```

如果构建失败，请停止并修正后再继续。

### 阶段 2：类型检查（Type Check）
```bash
# TypeScript 项目
npx tsc --noEmit 2>&1 | head -30

# Python 项目
pyright . 2>&1 | head -30
```

报告所有类型错误。在继续之前修复关键错误。

### 阶段 3：代码规范检查（Lint Check）
```bash
# JavaScript/TypeScript
npm run lint 2>&1 | head -30

# Python
ruff check . 2>&1 | head -30
```

### 阶段 4：测试套件（Test Suite）
```bash
# 运行带有覆盖率报告的测试
npm run test -- --coverage 2>&1 | tail -50

# 确认覆盖率阈值
# 目标：最低 80%
```

报告：
- 总计测试数：X
- 成功：X
- 失败：X
- 覆盖率：X%

### 阶段 5：安全扫描（Security Scan）
```bash
# 检查敏感信息（Secrets）
grep -rn "sk-" --include="*.ts" --include="*.js" . 2>/dev/null | head -10
grep -rn "api_key" --include="*.ts" --include="*.js" . 2>/dev/null | head -10

# 检查 console.log
grep -rn "console.log" --include="*.ts" --include="*.tsx" src/ 2>/dev/null | head -10
```

### 阶段 6：差异审查（Diff Review）
```bash
# 显示变更内容
git diff --stat
git diff HEAD~1 --name-only
```

审查每个变更的文件：
- 意料之外的变更
- 缺失的错误处理
- 潜在的边缘情况（Edge cases）

## 输出格式

运行所有阶段后，生成验证报告：

```
验证报告
==================

构建：     [成功/失败]
类型：     [成功/失败] (X 个错误)
Lint：     [成功/失败] (X 个警告)
测试：     [成功/失败] (X/Y 成功，Z% 覆盖率)
安全：     [成功/失败] (X 个问题)
差异：     [X 个文件变更]

结论：     PR 准备状态 [就绪/未就绪]

待修复问题：
1. ...
2. ...
```

## 持续模式

对于较长的会话，每 15 分钟或在主要变更后运行一次验证：

```markdown
设置心理检查点：
- 完成每个函数后
- 完成每个组件后
- 转移到下一个任务前

执行：/verify
```

## 与钩子（Hooks）集成

此技能是对 `PostToolUse` 钩子的补充，但提供了更深入的验证。
钩子用于即时捕获问题；此技能则提供全面的审查。
