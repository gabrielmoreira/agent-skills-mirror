---
description: "扩展自通用规则的 TypeScript 安全规约"
globs: ["**/*.ts", "**/*.tsx", "**/*.js", "**/*.jsx"]
alwaysApply: false
---
# TypeScript/JavaScript 安全规约（Security）

> 本文件扩展了通用安全规则，包含针对 TypeScript/JavaScript 的特定内容。

## 密钥管理（Secret Management）

```typescript
// 严禁：硬编码密钥 (Hardcoded secrets)
const apiKey = "sk-proj-xxxxx"

// 务必：使用环境变量 (Environment variables)
const apiKey = process.env.OPENAI_API_KEY

if (!apiKey) {
  throw new Error('OPENAI_API_KEY not configured')
}
```

## 智能体支持（Agent Support）

- 使用 **security-reviewer** 技能（Skill）进行全面的安全审计
