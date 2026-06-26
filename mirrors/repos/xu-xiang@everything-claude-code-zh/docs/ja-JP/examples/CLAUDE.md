# 项目级 CLAUDE.md 示例

这是项目级 CLAUDE.md 文件的示例。请将其放置在项目根目录中。

## 项目概览

[项目简要说明 - 核心功能、技术栈]

## 重要规则

### 1. 代码构成

- 倾向于使用大量小文件，而非少数大文件
- 高内聚、低耦合
- 通常 200-400 行，单个文件最大 800 行
- 按功能/领域组织代码，而非按类型组织

### 2. 代码风格

- 代码、注释和文档中不使用表情符号（Emoji）
- 始终保持不可变性（Immutability）——不修改对象或数组
- 不在生产环境代码中使用 `console.log`
- 使用 `try/catch` 进行妥善的错误处理
- 使用 Zod 等进行输入验证

### 3. 测试

- 测试驱动开发（TDD）：先写测试
- 最低 80% 的代码覆盖率
- 工具函数（Utility）的单元测试
- API 集成测试
- 关键流程的端到端（E2E）测试

### 4. 安全

- 不使用硬编码的敏感信息
- 敏感数据使用环境变量
- 验证所有用户输入
- 仅使用参数化查询
- 启用 CSRF 保护

## 文件结构

```
src/
|-- app/              # Next.js app router（应用路由）
|-- components/       # 可复用的 UI 组件
|-- hooks/            # 自定义 React Hook
|-- lib/              # 工具函数库
|-- types/            # TypeScript 类型定义
```

## 主要模式

### API 响应格式

```typescript
interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
}
```

### 错误处理

```typescript
try {
  const result = await operation()
  return { success: true, data: result }
} catch (error) {
  console.error('Operation failed:', error)
  return { success: false, error: 'User-friendly message' }
}
```

## 环境变量

```bash
# 必须
DATABASE_URL=
API_KEY=

# 可选
DEBUG=false
```

## 可用命令

- `/tdd` - 测试驱动开发（TDD）工作流
- `/plan` - 创建实现计划
- `/code-review` - 审查代码质量
- `/build-fix` - 修复构建错误

## Git 工作流

- Conventional Commits: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`
- 不直接提交到 `main` 分支
- PR 需要经过审查
- 合并前必须通过所有测试
