---
name: coding-standards
description: TypeScript、JavaScript、React、Node.js 开发的通用编码标准、最佳实践和模式。
---

# 编码标准与最佳实践

适用于所有项目的通用编码标准。

## 代码质量原则

### 1. 可读性优先 (Readability First)

* 代码被阅读的次数远多于编写的次数
* 明确的变量名和函数名
* 优先考虑自描述代码而非注释
* 保持格式一致

### 2. KISS (Keep It Simple, Stupid)

* 采用能运行的最简单方案
* 避免过度设计
* 避免过早优化
* 易于理解 > 巧妙的代码

### 3. DRY (Don't Repeat Yourself)

* 将通用逻辑提取到函数中
* 创建可复用组件
* 在模块间共享工具函数 (Utility functions)
* 避免复制粘贴式编程

### 4. YAGNI (You Aren't Gonna Need It)

* 不要预先构建不需要的功能
* 避免臆测性的泛化
* 仅在必要时增加复杂度
* 从简单开始，按需进行重构 (Refactoring)

## TypeScript/JavaScript 标准

### 变量命名

```typescript
// ✅ 推荐：描述性名称
const marketSearchQuery = 'election'
const isUserAuthenticated = true
const totalRevenue = 1000

// ❌ 错误：不明确的名称
const q = 'election'
const flag = true
const x = 1000
```

### 函数命名

```typescript
// ✅ 推荐：动词-名词模式
async function fetchMarketData(marketId: string) { }
function calculateSimilarity(a: number[], b: number[]) { }
function isValidEmail(email: string): boolean { }

// ❌ 错误：不明确或仅使用名词
async function market(id: string) { }
function similarity(a, b) { }
function email(e) { }
```

### 不变性模式 (Immutability Patterns)（重要）

```typescript
// ✅ 始终使用展开运算符 (Spread operator)
const updatedUser = {
  ...user,
  name: 'New Name'
}

const updatedArray = [...items, newItem]

// ❌ 绝不直接修改（Mutate）
user.name = 'New Name'  // 错误
items.push(newItem)     // 错误
```

### 错误处理 (Error Handling)

```typescript
// ✅ 推荐：全面的错误处理
async function fetchData(url: string) {
  try {
    const response = await fetch(url)

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    return await response.json()
  } catch (error) {
    console.error('Fetch failed:', error)
    throw new Error('Failed to fetch data')
  }
}

// ❌ 错误：缺乏错误处理
async function fetchData(url) {
  const response = await fetch(url)
  return response.json()
}
```

### Async/Await 最佳实践

```typescript
// ✅ 推荐：尽可能并行执行
const [users, markets, stats] = await Promise.all([
  fetchUsers(),
  fetchMarkets(),
  fetchStats()
])

// ❌ 错误：非必要的串行执行
const users = await fetchUsers()
const markets = await fetchMarkets()
const stats = await fetchStats()
```

### 类型安全 (Type Safety)

```typescript
// ✅ 推荐：正确的类型
interface Market {
  id: string
  name: string
  status: 'active' | 'resolved' | 'closed'
  created_at: Date
}

function getMarket(id: string): Promise<Market> {
  // 实现
}

// ❌ 错误：使用 'any'
function getMarket(id: any): Promise<any> {
  // 实现
}
```

## React 最佳实践

### 组件结构

```typescript
// ✅ 推荐：带类型的函数式组件
interface ButtonProps {
  children: React.ReactNode
  onClick: () => void
  disabled?: boolean
  variant?: 'primary' | 'secondary'
}

export function Button({
  children,
  onClick,
  disabled = false,
  variant = 'primary'
}: ButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`btn btn-${variant}`}
    >
      {children}
    </button>
  )
}

// ❌ 错误：无类型、结构不清晰
export function Button(props) {
  return <button onClick={props.onClick}>{props.children}</button>
}
```

### 自定义钩子 (Custom Hooks)

```typescript
// ✅ 推荐：可复用的自定义钩子
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    return () => clearTimeout(handler)
  }, [value, delay])

  return debouncedValue
}

// 用法
const debouncedQuery = useDebounce(searchQuery, 500)
```

### 状态管理 (State Management)

```typescript
// ✅ 推荐：正确的状态更新
const [count, setCount] = useState(0)

// 基于先前状态的函数式更新
setCount(prev => prev + 1)

// ❌ 错误：直接引用状态
setCount(count + 1)  // 在异步场景中可能会过期
```

### 条件渲染 (Conditional Rendering)

```typescript
// ✅ 推荐：清晰的条件渲染
{isLoading && <Spinner />}
{error && <ErrorMessage error={error} />}
{data && <DataDisplay data={data} />}

// ❌ 错误：三元运算符地狱
{isLoading ? <Spinner /> : error ? <ErrorMessage error={error} /> : data ? <DataDisplay data={data} /> : null}
```

## API 设计标准

### REST API 规范

```
GET    /api/markets              # 列出所有市场
GET    /api/markets/:id          # 获取特定市场
POST   /api/markets              # 创建新市场
PUT    /api/markets/:id          # 更新市场（完整更新）
PATCH  /api/markets/:id          # 更新市场（部分更新）
DELETE /api/markets/:id          # 删除市场

# 用于过滤的查询参数
GET /api/markets?status=active&limit=10&offset=0
```

### 响应格式

```typescript
// ✅ 推荐：一致的响应结构
interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
  meta?: {
    total: number
    page: number
    limit: number
  }
}

// 成功响应
return NextResponse.json({
  success: true,
  data: markets,
  meta: { total: 100, page: 1, limit: 10 }
})

// 错误响应
return NextResponse.json({
  success: false,
  error: 'Invalid request'
}, { status: 400 })
```

### 输入验证 (Input Validation)

```typescript
import { z } from 'zod'

// ✅ 推荐：架构验证 (Schema validation)
const CreateMarketSchema = z.object({
  name: z.string().min(1).max(200),
  description: z.string().min(1).max(2000),
  endDate: z.string().datetime(),
  categories: z.array(z.string()).min(1)
})

export async function POST(request: Request) {
  const body = await request.json()

  try {
    const validated = CreateMarketSchema.parse(body)
    // 使用验证后的数据继续
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json({
        success: false,
        error: 'Validation failed',
        details: error.errors
      }, { status: 400 })
    }
  }
}
```

## 文件结构

### 项目结构

```
src/
├── app/                    # Next.js App 路由
│   ├── api/               # API 路由
│   ├── markets/           # 市场页面
│   └── (auth)/           # 认证页面（路由组）
├── components/            # React 组件
│   ├── ui/               # 通用 UI 组件
│   ├── forms/            # 表单组件
│   └── layouts/          # 布局组件
├── hooks/                # 自定义 React 钩子
├── lib/                  # 工具类与配置
│   ├── api/             # API 客户端
│   ├── utils/           # 辅助函数
│   └── constants/       # 常量
├── types/                # TypeScript 类型
└── styles/              # 全局样式
```

### 文件命名

```
components/Button.tsx          # 组件使用 PascalCase
hooks/useAuth.ts              # 使用 'use' 前缀的 camelCase
lib/formatDate.ts             # 工具类使用 camelCase
types/market.types.ts         # 带有 .types 后缀的 camelCase
```

## 注释与文档

### 何时添加注释

```typescript
// ✅ 推荐：解释“为什么”，而不是“是什么”
// 使用指数退避算法，避免在服务中断期间过载 API
const delay = Math.min(1000 * Math.pow(2, retryCount), 30000)

// 为了在大数组下的性能，此处特意使用直接修改（Mutation）
items.push(newItem)

// ❌ 错误：陈述显而易见的事实
// 计数器加 1
count++

// 将 name 设置为用户名
name = user.name
```

### 公共 API 的 JSDoc

````typescript
/**
 * 使用语义相似度搜索市场。
 *
 * @param query - 自然语言搜索查询
 * @param limit - 最大结果数（默认值：10）
 * @returns 按相似度分数排序的市场数组
 * @throws {Error} 如果 OpenAI API 失败或 Redis 不可用
 *
 * @example
 * ```typescript
 * const results = await searchMarkets('election', 5)
 * console.log(results[0].name) // "Trump vs Biden"
 * ```
 */
export async function searchMarkets(
  query: string,
  limit: number = 10
): Promise<Market[]> {
  // 实现
}
````

## 性能最佳实践

### 记忆化 (Memoization)

```typescript
import { useMemo, useCallback } from 'react'

// ✅ 推荐：记忆化高开销计算
const sortedMarkets = useMemo(() => {
  return markets.sort((a, b) => b.volume - a.volume)
}, [markets])

// ✅ 推荐：记忆化回调函数
const handleSearch = useCallback((query: string) => {
  setSearchQuery(query)
}, [])
```

### 延迟加载 (Lazy Loading)

```typescript
import { lazy, Suspense } from 'react'

// ✅ 推荐：延迟加载重型组件
const HeavyChart = lazy(() => import('./HeavyChart'))

export function Dashboard() {
  return (
    <Suspense fallback={<Spinner />}>
      <HeavyChart />
    </Suspense>
  )
}
```

### 数据库查询

```typescript
// ✅ 推荐：仅选择需要的列
const { data } = await supabase
  .from('markets')
  .select('id, name, status')
  .limit(10)

// ❌ 错误：选择所有列
const { data } = await supabase
  .from('markets')
  .select('*')
```

## 测试标准

### 测试结构（AAA 模式）

```typescript
test('calculates similarity correctly', () => {
  // 安排 (Arrange)
  const vector1 = [1, 0, 0]
  const vector2 = [0, 1, 0]

  // 执行 (Act)
  const similarity = calculateCosineSimilarity(vector1, vector2)

  // 断言 (Assert)
  expect(similarity).toBe(0)
})
```

### 测试命名

```typescript
// ✅ 推荐：描述性测试名称
test('returns empty array when no markets match query', () => { })
test('throws error when OpenAI API key is missing', () => { })
test('falls back to substring search when Redis unavailable', () => { })

// ❌ 错误：模糊的测试名称
test('works', () => { })
test('test search', () => { })
```

## 代码异味 (Code Smells) 检测

请注意以下反模式 (Anti-patterns)。

### 1. 过长函数

```typescript
// ❌ 错误：函数超过 50 行
function processMarketData() {
  // 100 行代码
}

// ✅ 推荐：拆分为更小的函数
function processMarketData() {
  const validated = validateData()
  const transformed = transformData(validated)
  return saveData(transformed)
}
```

### 2. 过深嵌套

```typescript
// ❌ 错误：5 层以上的嵌套
if (user) {
  if (user.isAdmin) {
    if (market) {
      if (market.isActive) {
        if (hasPermission) {
          // 执行操作
        }
      }
    }
  }
}

// ✅ 推荐：提前返回 (Early returns)
if (!user) return
if (!user.isAdmin) return
if (!market) return
if (!market.isActive) return
if (!hasPermission) return

// 执行操作
```

### 3. 魔术字 (Magic Numbers)

```typescript
// ❌ 错误：未经解释的数字
if (retryCount > 3) { }
setTimeout(callback, 500)

// ✅ 推荐：具名常量
const MAX_RETRIES = 3
const DEBOUNCE_DELAY_MS = 500

if (retryCount > MAX_RETRIES) { }
setTimeout(callback, DEBOUNCE_DELAY_MS)
```

**请记住**：代码质量不容妥协。清晰且可维护的代码将实现快速开发和从容重构。
