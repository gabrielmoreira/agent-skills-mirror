---
name: tdd-workflow
description: 在编写新功能、修复 Bug 或重构代码时使用此技能。强制执行测试驱动开发（TDD），包括单元测试、集成测试和端到端（E2E）测试，覆盖率需达到 80% 以上。
origin: ECC
---

# 测试驱动开发（TDD）工作流

此技能确保所有代码开发都遵循具有全面测试覆盖率的 TDD 原则。

## 何时激活

- 编写新功能或新逻辑
- 修复 Bug 或问题
- 重构现有代码
- 添加 API 端点
- 创建新组件

## 核心原则

### 1. 先测试，后代码（Tests BEFORE Code）
务必先编写测试，然后编写代码使测试通过。

### 2. 覆盖率要求
- 最低 80% 覆盖率（单元测试 + 集成测试 + E2E）
- 覆盖所有边缘情况（edge cases）
- 测试错误场景（error scenarios）
- 验证边界条件（boundary conditions）

### 3. 测试类型

#### 单元测试（Unit Tests）
- 独立函数和工具方法
- 组件逻辑
- 纯函数
- 辅助函数和工具

#### 集成测试（Integration Tests）
- API 端点
- 数据库操作
- 服务间交互
- 外部 API 调用

#### 端到端测试（E2E Tests - Playwright）
- 关键用户流程
- 完整工作流
- 浏览器自动化
- UI 交互

## TDD 工作流步骤

### 第 1 步：编写用户旅程（User Journeys）
```
作为 [角色]，我想 [操作]，以便 [收益]

示例：
作为一名用户，我想进行语义化的市场搜索，
以便即使没有精确的关键词也能找到相关的市场。
```

### 第 2 步：生成测试用例
为每个用户旅程创建全面的测试用例：

```typescript
describe('语义化搜索', () => {
  it('为查询返回相关的市场', async () => {
    // 测试实现
  })

  it('优雅地处理空查询', async () => {
    // 测试边缘情况
  })

  it('当 Redis 不可用时回退到子字符串搜索', async () => {
    // 测试回退行为
  })

  it('按相似度得分对结果进行排序', async () => {
    // 测试排序逻辑
  })
})
```

### 第 3 步：运行测试（预期失败）
```bash
npm test
# 测试应该失败 - 我们还没有实现功能
```

### 第 4 步：实现代码
编写最少量的代码使测试通过：

```typescript
// 由测试引导的实现
export async function searchMarkets(query: string) {
  // 实现代码
}
```

### 第 5 步：再次运行测试
```bash
npm test
# 测试现在应该通过
```

### 第 6 步：重构（Refactor）
在保持测试通过的情况下提高代码质量：
- 消除重复
- 改进命名
- 优化性能
- 增强可读性

### 第 7 步：验证覆盖率
```bash
npm run test:coverage
# 验证是否达到了 80% 以上的覆盖率
```

## 测试模式（Patterns）

### 单元测试模式 (Jest/Vitest)
```typescript
import { render, screen, fireEvent } from '@testing-library/react'
import { Button } from './Button'

describe('Button 组件', () => {
  it('以正确的文本渲染', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })

  it('点击时调用 onClick', () => {
    const handleClick = jest.fn()
    render(<Button onClick={handleClick}>Click</Button>)

    fireEvent.click(screen.getByRole('button'))

    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('当 disabled 属性为 true 时被禁用', () => {
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
  it('成功返回市场数据', async () => {
    const request = new NextRequest('http://localhost/api/markets')
    const response = await GET(request)
    const data = await response.json()

    expect(response.status).toBe(200)
    expect(data.success).toBe(true)
    expect(Array.isArray(data.data)).toBe(true)
  })

  it('验证查询参数', async () => {
    const request = new NextRequest('http://localhost/api/markets?limit=invalid')
    const response = await GET(request)

    expect(response.status).toBe(400)
  })

  it('优雅地处理数据库错误', async () => {
    // 模拟数据库失败
    const request = new NextRequest('http://localhost/api/markets')
    // 测试错误处理
  })
})
```

### E2E 测试模式 (Playwright)
```typescript
import { test, expect } from '@playwright/test'

test('用户可以搜索并过滤市场', async ({ page }) => {
  // 导航到市场页面
  await page.goto('/')
  await page.click('a[href="/markets"]')

  // 验证页面已加载
  await expect(page.locator('h1')).toContainText('Markets')

  // 搜索市场
  await page.fill('input[placeholder="Search markets"]', 'election')

  // 等待防抖和结果
  await page.waitForTimeout(600)

  // 验证显示的搜索结果
  const results = page.locator('[data-testid="market-card"]')
  await expect(results).toHaveCount(5, { timeout: 5000 })

  // 验证结果包含搜索词
  const firstResult = results.first()
  await expect(firstResult).toContainText('election', { ignoreCase: true })

  // 按状态过滤
  await page.click('button:has-text("Active")')

  // 验证过滤后的结果
  await expect(results).toHaveCount(3)
})

test('用户可以创建新市场', async ({ page }) => {
  // 首先登录
  await page.goto('/creator-dashboard')

  // 填写市场创建表单
  await page.fill('input[name="name"]', 'Test Market')
  await page.fill('textarea[name="description"]', 'Test description')
  await page.fill('input[name="endDate"]', '2025-12-31')

  // 提交表单
  await page.click('button[type="submit"]')

  // 验证成功消息
  await expect(page.locator('text=Market created successfully')).toBeVisible()

  // 验证重定向到市场详情页
  await expect(page).toHaveURL(/\/markets\/test-market/)
})
```

## 测试文件组织

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

## 模拟（Mocking）外部服务

### Supabase 模拟
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

### Redis 模拟
```typescript
jest.mock('@/lib/redis', () => ({
  searchMarketsByVector: jest.fn(() => Promise.resolve([
    { slug: 'test-market', similarity_score: 0.95 }
  ])),
  checkRedisHealth: jest.fn(() => Promise.resolve({ connected: true }))
}))
```

### OpenAI 模拟
```typescript
jest.mock('@/lib/openai', () => ({
  generateEmbedding: jest.fn(() => Promise.resolve(
    new Array(1536).fill(0.1) // 模拟 1536 维向量
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
// 对变化具有韧性
await page.click('button:has-text("Submit")')
await page.click('[data-testid="submit-button"]')
```

### ❌ 错误：缺乏测试隔离
```typescript
// 测试之间相互依赖
test('creates user', () => { /* ... */ })
test('updates same user', () => { /* 依赖于前一个测试 */ })
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

### 开发过程中的监听模式 (Watch Mode)
```bash
npm test -- --watch
# 文件更改时自动运行测试
```

### Pre-Commit 钩子
```bash
# 每次提交前运行
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

1. **先写测试** - 始终遵循 TDD
2. **每个测试只做一个断言** - 专注于单一行为
3. **描述性的测试名称** - 说明测试了什么
4. **准备-执行-断言 (Arrange-Act-Assert)** - 清晰的测试结构
5. **模拟外部依赖** - 隔离单元测试
6. **测试边缘情况** - Null, undefined, 空值, 大数据量
7. **测试错误路径** - 不仅仅是成功路径
8. **保持测试快速** - 每个单元测试 < 50ms
9. **测试后清理** - 无副作用
10. **检查覆盖率报告** - 识别缺口

## 成功指标

- 达到 80% 以上的代码覆盖率
- 所有测试通过（绿色）
- 没有跳过或禁用的测试
- 测试执行快速（单元测试 < 30s）
- E2E 测试覆盖关键用户流程
- 测试在上线前发现 Bug

---

**记住**：测试不是可选的。它们是安全网，能够让你自信地进行重构、快速开发并确保生产环境的可靠性。
