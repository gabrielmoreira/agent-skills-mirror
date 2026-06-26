---
name: tdd-workflow
description: 在创建新功能、修复 Bug 或重构代码时使用此技能。强制执行测试驱动开发（TDD），要求包括单元测试、集成测试和 E2E 测试在内的测试覆盖率达到 80% 以上。
---

# 测试驱动开发（TDD）工作流

此技能（Skill）旨在确保所有代码开发都遵循具有全面测试覆盖率的测试驱动开发（TDD）原则。

## 何时启用

- 创建新功能或特性
- 修复 Bug 或问题
- 重构现有代码
- 添加 API 接口（Endpoints）
- 创建新组件

## 核心原则

### 1. 测试先行
始终先编写测试，然后再实现使测试通过的代码。

### 2. 覆盖率要求
- 最低 80% 的覆盖率（单元测试 + 集成测试 + E2E 测试）
- 覆盖所有边缘情况（Edge Cases）
- 测试异常场景
- 验证边界条件

### 3. 测试类型

#### 单元测试（Unit Testing）
- 单个函数和工具类
- 组件逻辑
- 纯函数
- Helper 和 Utility

#### 集成测试（Integration Testing）
- API 接口
- 数据库操作
- 服务间交互
- 外部 API 调用

#### E2E 测试（E2E Testing） (Playwright)
- 关键用户路径（User Flows）
- 完整的工作流
- 浏览器自动化
- UI 交互

## TDD 工作流步骤

### 第 1 步：编写用户旅程（User Journey）
```
作为[角色]，我想要[行动]，以便于[获益]

示例：
作为用户，我想要语义化搜索市场，
以便于即使没有准确的关键词也能找到相关的市场。
```

### 第 2 步：生成测试用例
为每个用户旅程创建全面的测试用例：

```typescript
describe('Semantic Search', () => {
  it('returns relevant markets for query', async () => {
    // 测试实现
  })

  it('handles empty query gracefully', async () => {
    // 边缘情况测试
  })

  it('falls back to substring search when Redis unavailable', async () => {
    // 降级行为测试
  })

  it('sorts results by similarity score', async () => {
    // 排序逻辑测试
  })
})
```

### 第 3 步：运行测试（预期失败）
```bash
npm test
# 测试应该失败 - 因为尚未实现功能
```

### 第 4 步：实现代码
编写能让测试通过的最少代码：

```typescript
// 由测试引导的实现
export async function searchMarkets(query: string) {
  // 实现在这里
}
```

### 第 5 步：重新运行测试
```bash
npm test
# 这次测试应该成功
```

### 第 6 步：重构（Refactor）
在保持测试通过的同时提高代码质量：
- 消除重复
- 优化命名
- 提升性能
- 提高可读性

### 第 7 步：检查覆盖率
```bash
npm run test:coverage
# 确认已达到 80% 以上的覆盖率
```

## 测试模式

### 单元测试模式 (Jest/Vitest)
```typescript
import { render, screen, fireEvent } from '@testing-library/react'
import { Button } from './Button'

describe('Button Component', () => {
  it('renders with correct text', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })

  it('calls onClick when clicked', () => {
    const handleClick = jest.fn()
    render(<Button onClick={handleClick}>Click</Button>)

    fireEvent.click(screen.getByRole('button'))

    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('is disabled when disabled prop is true', () => {
    render(<Button disabled>Click</Button>)
    expect(screen.getByRole('button')).toBeDisabled()
  })
})
```

### API 集成测试模式
```typescript
import { NextRequest } from 'next/server'
import { GET } from './route'

describe('GET /api/markets', () => {
  it('returns markets successfully', async () => {
    const request = new NextRequest('http://localhost/api/markets')
    const response = await GET(request)
    const data = await response.json()

    expect(response.status).toBe(200)
    expect(data.success).toBe(true)
    expect(Array.isArray(data.data)).toBe(true)
  })

  it('validates query parameters', async () => {
    const request = new NextRequest('http://localhost/api/markets?limit=invalid')
    const response = await GET(request)

    expect(response.status).toBe(400)
  })

  it('handles database errors gracefully', async () => {
    // Mock 数据库故障
    const request = new NextRequest('http://localhost/api/markets')
    // 测试错误处理
  })
})
```

### E2E 测试模式 (Playwright)
```typescript
import { test, expect } from '@playwright/test'

test('user can search and filter markets', async ({ page }) => {
  // 跳转到市场页面
  await page.goto('/')
  await page.click('a[href="/markets"]')

  // 确认页面已加载
  await expect(page.locator('h1')).toContainText('Markets')

  // 搜索市场
  await page.fill('input[placeholder="Search markets"]', 'election')

  // 等待防抖（Debounce）和结果返回
  await page.waitForTimeout(600)

  // 确认搜索结果已显示
  const results = page.locator('[data-testid="market-card"]')
  await expect(results).toHaveCount(5, { timeout: 5000 })

  // 确认结果包含搜索词
  const firstResult = results.first()
  await expect(firstResult).toContainText('election', { ignoreCase: true })

  // 按状态筛选
  await page.click('button:has-text("Active")')

  // 检查筛选后的结果
  await expect(results).toHaveCount(3)
})

test('user can create a new market', async ({ page }) => {
  // 首先登录
  await page.goto('/creator-dashboard')

  // 填写创建市场表单
  await page.fill('input[name="name"]', 'Test Market')
  await page.fill('textarea[name="description"]', 'Test description')
  await page.fill('input[name="endDate"]', '2025-12-31')

  // 提交表单
  await page.click('button[type="submit"]')

  // 检查成功消息
  await expect(page.locator('text=Market created successfully')).toBeVisible()

  // 确认重定向到市场页面
  await expect(page).toHaveURL(/\/markets\/test-market/)
})
```

## 测试文件结构

```
src/
├── components/
│   ├── Button/
│   │   ├── Button.tsx
│   │   ├── Button.test.tsx          # 单元测试
│   │   └── Button.stories.tsx       # Storybook
│   └── MarketCard/
│       ├── MarketCard.tsx
│       └── MarketCard.test.tsx
├── app/
│   └── api/
│       └── markets/
│           ├── route.ts
│           └── route.test.ts         # 集成测试
└── e2e/
    ├── markets.spec.ts               # E2E 测试
    ├── trading.spec.ts
    └── auth.spec.ts
```

## 外部服务 Mock

### Supabase Mock
```typescript
jest.mock('@/lib/supabase', () => ({
  supabase: {
    from: jest.fn(() => ({
      select: jest.fn(() => ({
        eq: jest.fn(() => Promise.resolve({
          data: [{ id: 1, name: 'Test Market' }],
          error: null
        }))
      }))
    }))
  }
}))
```

### Redis Mock
```typescript
jest.mock('@/lib/redis', () => ({
  searchMarketsByVector: jest.fn(() => Promise.resolve([
    { slug: 'test-market', similarity_score: 0.95 }
  ])),
  checkRedisHealth: jest.fn(() => Promise.resolve({ connected: true }))
}))
```

### OpenAI Mock
```typescript
jest.mock('@/lib/openai', () => ({
  generateEmbedding: jest.fn(() => Promise.resolve(
    new Array(1536).fill(0.1) // Mock 1536 维嵌入向量
  ))
}))
```

## 测试覆盖率验证

### 运行覆盖率报告
```bash
npm run test:coverage
```

### 覆盖率阈值
```json
{
  "jest": {
    "coverageThresholds": {
      "global": {
        "branches": 80,
        "functions": 80,
        "lines": 80,
        "statements": 80
      }
    }
  }
}
```

## 应避免的常见测试错误

### ❌ 错误：测试实现细节
```typescript
// 不要测试内部状态
expect(component.state.count).toBe(5)
```

### ✅ 正确：测试用户可见的行为
```typescript
// 测试用户看到的内容
expect(screen.getByText('Count: 5')).toBeInTheDocument()
```

### ❌ 错误：脆弱的选择器
```typescript
// 容易因样式调整而失效
await page.click('.css-class-xyz')
```

### ✅ 正确：语义化选择器
```typescript
// 对变更更具韧性
await page.click('button:has-text("Submit")')
await page.click('[data-testid="submit-button"]')
```

### ❌ 错误：测试未隔离
```typescript
// 测试间相互依赖
test('creates user', () => { /* ... */ })
test('updates same user', () => { /* 依赖前一个测试 */ })
```

### ✅ 正确：独立的测试
```typescript
// 每个测试都设置自己的数据
test('creates user', () => {
  const user = createTestUser()
  // 测试逻辑
})

test('updates user', () => {
  const user = createTestUser()
  // 更新逻辑
})
```

## 持续测试

### 开发中的监听模式（Watch Mode）
```bash
npm test -- --watch
# 文件变更时自动运行测试
```

### Pre-commit 钩子（Hooks）
```bash
# 在每次提交前运行
npm test && npm run lint
```

### CI/CD 集成
```yaml
# GitHub Actions
- name: Run Tests
  run: npm test -- --coverage
- name: Upload Coverage
  uses: codecov/codecov-action@v3
```

## 最佳实践

1. **测试先行** - 始终遵循 TDD。
2. **每个测试只断言（Assert）一件事** - 专注于单一行为。
3. **描述性的测试名称** - 清晰说明测试内容。
4. **Arrange-Act-Assert** - 保持清晰的测试结构。
5. **Mock 外部依赖** - 隔离单元测试。
6. **测试边缘情况** - null、undefined、空值、超大值。
7. **测试错误路径** - 不仅仅是成功路径（Happy Path）。
8. **保持测试快速运行** - 每个单元测试应小于 50ms。
9. **测试后清理** - 避免副作用。
10. **审查覆盖率报告** - 识别覆盖盲点。

## 成功指标

- 达到 80% 以上的代码覆盖率。
- 所有测试均通过（Green）。
- 无跳过或禁用的测试。
- 快速的测试执行（单元测试应在 30 秒内完成）。
- E2E 测试覆盖了关键用户旅程。
- 测试能够在发布前检测到 Bug。

---

**请记住**：测试不是可选的。它是让你能够自信地重构、快速地开发并确保生产环境可靠性的安全网。
