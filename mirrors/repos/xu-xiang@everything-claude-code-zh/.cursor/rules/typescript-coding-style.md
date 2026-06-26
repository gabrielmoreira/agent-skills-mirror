---
description: "TypeScript 编码风格，扩展了通用规则"
globs: ["**/*.ts", "**/*.tsx", "**/*.js", "**/*.jsx"]
alwaysApply: false
---
# TypeScript/JavaScript 编码风格（Coding Style）

> 本文件在通用编码风格规则的基础上，扩展了针对 TypeScript/JavaScript 的特定内容。

## 不可变性（Immutability）

使用扩展运算符（spread operator）进行不可变更新：

```typescript
// 错误：直接修改（Mutation）
function updateUser(user, name) {
  user.name = name  // 修改了原对象！
  return user
}

// 正确：不可变性（Immutability）
function updateUser(user, name) {
  return {
    ...user,
    name
  }
}
```

## 错误处理（Error Handling）

使用 `async/await` 配合 `try-catch`：

```typescript
try {
  const result = await riskyOperation()
  return result
} catch (error) {
  console.error('Operation failed:', error)
  throw new Error('Detailed user-friendly message')
}
```

## 输入验证（Input Validation）

使用 Zod 进行基于模式（schema）的验证：

```typescript
import { z } from 'zod'

const schema = z.object({
  email: z.string().email(),
  age: z.number().int().min(0).max(150)
})

const validated = schema.parse(input)
```

## 控制台日志（Console.log）

- 生产代码中严禁出现 `console.log` 语句。
- 请改用专业的日志库（logging libraries）。
- 详见钩子（Hooks）以了解自动检测机制。
