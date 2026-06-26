---
name: security-review
description: 在添加身份验证、处理用户输入、操作机密信息（Secrets）、创建 API 端点以及实现支付/敏感功能时使用此技能。提供全面的安全检查清单和模式。
---

# 安全审查技能 (Security Review Skill)

此技能旨在确保所有代码遵循安全最佳实践，并识别潜在漏洞。

## 激活时机

- 实现身份验证 (Authentication) 或授权 (Authorization) 时
- 处理用户输入或文件上传时
- 创建新的 API 端点时
- 操作机密信息 (Secrets) 或凭据时
- 实现支付功能时
- 存储或传输敏感数据时
- 集成第三方 API 时

## 安全检查清单

### 1. 机密信息管理 (Secret Management)

#### ❌ 严禁行为
```typescript
const apiKey = "sk-proj-xxxxx"  // 硬编码的机密信息
const dbPassword = "password123" // 存在于源码中
```

#### ✅ 始终遵循
```typescript
const apiKey = process.env.OPENAI_API_KEY
const dbUrl = process.env.DATABASE_URL

// 确保机密信息存在
if (!apiKey) {
  throw new Error('OPENAI_API_KEY not configured')
}
```

#### 验证步骤
- [ ] 无硬编码的 API 密钥、令牌或密码
- [ ] 所有机密信息均通过环境变量管理
- [ ] 将 `.env.local` 添加到 .gitignore
- [ ] Git 历史记录中不包含机密信息
- [ ] 生产环境机密信息存储在托管平台（如 Vercel、Railway）

### 2. 输入验证 (Input Validation)

#### 始终验证用户输入
```typescript
import { z } from 'zod'

// 定义验证 Schema
const CreateUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(100),
  age: z.number().int().min(0).max(150)
})

// 处理前验证
export async function createUser(input: unknown) {
  try {
    const validated = CreateUserSchema.parse(input)
    return await db.users.create(validated)
  } catch (error) {
    if (error instanceof z.ZodError) {
      return { success: false, errors: error.errors }
    }
    throw error
  }
}
```

#### 文件上传验证
```typescript
function validateFileUpload(file: File) {
  // 检查大小（最大 5MB）
  const maxSize = 5 * 1024 * 1024
  if (file.size > maxSize) {
    throw new Error('File too large (max 5MB)')
  }

  // 检查类型
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif']
  if (!allowedTypes.includes(file.type)) {
    throw new Error('Invalid file type')
  }

  // 检查扩展名
  const allowedExtensions = ['.jpg', '.jpeg', '.png', '.gif']
  const extension = file.name.toLowerCase().match(/\.[^.]+$/)?.[0]
  if (!extension || !allowedExtensions.includes(extension)) {
    throw new Error('Invalid file extension')
  }

  return true
}
```

#### 验证步骤
- [ ] 使用 Schema 验证所有用户输入
- [ ] 限制文件上传（大小、类型、扩展名）
- [ ] 不在查询中直接使用用户输入
- [ ] 使用白名单验证（而非黑名单）
- [ ] 错误消息不泄露敏感信息

### 3. 防止 SQL 注入 (SQL Injection Prevention)

#### ❌ 严禁拼接 SQL
```typescript
// 危险 - 存在 SQL 注入漏洞
const query = `SELECT * FROM users WHERE email = '${userEmail}'`
await db.query(query)
```

#### ✅ 始终使用参数化查询
```typescript
// 安全 - 使用参数化查询
const { data } = await supabase
  .from('users')
  .select('*')
  .eq('email', userEmail)

// 或在原生 SQL 中使用
await db.query(
  'SELECT * FROM users WHERE email = $1',
  [userEmail]
)
```

#### 验证步骤
- [ ] 所有数据库查询均使用参数化查询
- [ ] SQL 中无字符串拼接
- [ ] 正确使用 ORM / 查询构建器 (Query Builder)
- [ ] Supabase 查询已正确净化 (Sanitized)

### 4. 身份验证与授权 (Authentication and Authorization)

#### JWT 令牌处理
```typescript
// ❌ 错误：localStorage（容易受到 XSS 攻击）
localStorage.setItem('token', token)

// ✅ 正确：httpOnly Cookie
res.setHeader('Set-Cookie',
  `token=${token}; HttpOnly; Secure; SameSite=Strict; Max-Age=3600`)
```

#### 授权检查
```typescript
export async function deleteUser(userId: string, requesterId: string) {
  // 始终先确认授权
  const requester = await db.users.findUnique({
    where: { id: requesterId }
  })

  if (requester.role !== 'admin') {
    return NextResponse.json(
      { error: 'Unauthorized' },
      { status: 403 }
    )
  }

  // 继续执行删除
  await db.users.delete({ where: { id: userId } })
}
```

#### 行级安全 (Row Level Security - Supabase)
```sql
-- 在所有表上启用 RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- 用户只能查看自己的数据
CREATE POLICY "Users view own data"
  ON users FOR SELECT
  USING (auth.uid() = id);

-- 用户只能更新自己的数据
CREATE POLICY "Users update own data"
  ON users FOR UPDATE
  USING (auth.uid() = id);
```

#### 验证步骤
- [ ] 令牌存储在 httpOnly Cookie 中（而非 localStorage）
- [ ] 在敏感操作前进行授权检查
- [ ] 在 Supabase 中启用行级安全 (Row Level Security)
- [ ] 实现基于角色的访问控制 (RBAC)
- [ ] 确保会话管理安全

### 5. 防止 XSS (XSS Prevention)

#### 净化 HTML
```typescript
import DOMPurify from 'isomorphic-dompurify'

// 始终对用户提供的 HTML 进行净化
function renderUserContent(html: string) {
  const clean = DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'p'],
    ALLOWED_ATTR: []
  })
  return <div dangerouslySetInnerHTML={{ __html: clean }} />
}
```

#### 内容安全策略 (Content Security Policy)
```typescript
// next.config.js
const securityHeaders = [
  {
    key: 'Content-Security-Policy',
    value: `
      default-src 'self';
      script-src 'self' 'unsafe-eval' 'unsafe-inline';
      style-src 'self' 'unsafe-inline';
      img-src 'self' data: https:;
      font-src 'self';
      connect-src 'self' https://api.example.com;
    `.replace(/\s{2,}/g, ' ').trim()
  }
]
```

#### 验证步骤
- [ ] 净化用户提供的 HTML
- [ ] 配置 CSP 响应头
- [ ] 不渲染未经验证的动态内容
- [ ] 利用 React 内置的 XSS 防护机制

### 6. CSRF 防护

#### CSRF 令牌 (Tokens)
```typescript
import { csrf } from '@/lib/csrf'

export async function POST(request: Request) {
  const token = request.headers.get('X-CSRF-Token')

  if (!csrf.verify(token)) {
    return NextResponse.json(
      { error: 'Invalid CSRF token' },
      { status: 403 }
    )
  }

  // 处理请求
}
```

#### SameSite Cookie
```typescript
res.setHeader('Set-Cookie',
  `session=${sessionId}; HttpOnly; Secure; SameSite=Strict`)
```

#### 验证步骤
- [ ] 在状态变更操作中使用 CSRF 令牌
- [ ] 在所有 Cookie 中设置 SameSite=Strict
- [ ] 实现双重提交 Cookie 模式 (Double Submit Cookie Pattern)

### 7. 速率限制 (Rate Limiting)

#### API 速率限制
```typescript
import rateLimit from 'express-rate-limit'

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 分钟
  max: 100, // 每个窗口期最多 100 个请求
  message: 'Too many requests'
})

// 应用于路由
app.use('/api/', limiter)
```

#### 高成本操作
```typescript
// 对搜索操作进行更严格的速率限制
const searchLimiter = rateLimit({
  windowMs: 60 * 1000, // 1 分钟
  max: 10, // 每分钟最多 10 个请求
  message: 'Too many search requests'
})

app.use('/api/search', searchLimiter)
```

#### 验证步骤
- [ ] 为所有 API 端点设置速率限制
- [ ] 对高成本操作实施更严格的限制
- [ ] 基于 IP 的速率限制
- [ ] 基于用户（已验证）的速率限制

### 8. 敏感数据泄露

#### 日志记录 (Logging)
```typescript
// ❌ 错误：在日志中记录敏感数据
console.log('User login:', { email, password })
console.log('Payment:', { cardNumber, cvv })

// ✅ 正确：脱敏处理
console.log('User login:', { email, userId })
console.log('Payment:', { last4: card.last4, userId })
```

#### 错误消息
```typescript
// ❌ 错误：泄露内部细节
catch (error) {
  return NextResponse.json(
    { error: error.message, stack: error.stack },
    { status: 500 }
  )
}

// ✅ 正确：通用的错误消息
catch (error) {
  console.error('Internal error:', error)
  return NextResponse.json(
    { error: 'An error occurred. Please try again.' },
    { status: 500 }
  )
}
```

#### 验证步骤
- [ ] 日志中不包含密码、令牌或机密信息
- [ ] 面向用户使用通用的错误消息
- [ ] 详细错误仅存在于服务器日志中
- [ ] 不向用户暴露堆栈轨迹 (Stack Traces)

### 9. 区块链安全 (Solana)

#### 钱包验证
```typescript
import { verify } from '@solana/web3.js'

async function verifyWalletOwnership(
  publicKey: string,
  signature: string,
  message: string
) {
  try {
    const isValid = verify(
      Buffer.from(message),
      Buffer.from(signature, 'base64'),
      Buffer.from(publicKey, 'base64')
    )
    return isValid
  } catch (error) {
    return false
  }
}
```

#### 交易验证
```typescript
async function verifyTransaction(transaction: Transaction) {
  // 验证接收者
  if (transaction.to !== expectedRecipient) {
    throw new Error('Invalid recipient')
  }

  // 验证金额
  if (transaction.amount > maxAmount) {
    throw new Error('Amount exceeds limit')
  }

  // 确保用户余额充足
  const balance = await getBalance(transaction.from)
  if (balance < transaction.amount) {
    throw new Error('Insufficient balance')
  }

  return true
}
```

#### 验证步骤
- [ ] 验证钱包签名
- [ ] 验证交易详情
- [ ] 交易前检查余额
- [ ] 禁止盲签交易 (Blind Transaction Signing)

### 10. 依赖项安全

#### 定期更新
```bash
# 检查漏洞
npm audit

# 修复可自动修复的问题
npm audit fix

# 更新依赖项
npm update

# 检查过时的包
npm outdated
```

#### 锁定文件 (Lockfiles)
```bash
# 始终提交锁定文件
git add package-lock.json

# 在 CI/CD 中使用以实现可重现的构建
npm ci  # 替代 npm install
```

#### 验证步骤
- [ ] 依赖项保持最新
- [ ] 无已知漏洞（npm audit 通过）
- [ ] 已提交锁定文件
- [ ] 在 GitHub 上启用 Dependabot
- [ ] 定期进行安全更新

## 安全测试

### 自动化安全测试
```typescript
// 测试身份验证
test('requires authentication', async () => {
  const response = await fetch('/api/protected')
  expect(response.status).toBe(401)
})

// 测试授权
test('requires admin role', async () => {
  const response = await fetch('/api/admin', {
    headers: { Authorization: `Bearer ${userToken}` }
  })
  expect(response.status).toBe(403)
})

// 测试输入验证
test('rejects invalid input', async () => {
  const response = await fetch('/api/users', {
    method: 'POST',
    body: JSON.stringify({ email: 'not-an-email' })
  })
  expect(response.status).toBe(400)
})

// 测试速率限制
test('enforces rate limits', async () => {
  const requests = Array(101).fill(null).map(() =>
    fetch('/api/endpoint')
  )

  const responses = await Promise.all(requests)
  const tooManyRequests = responses.filter(r => r.status === 429)

  expect(tooManyRequests.length).toBeGreaterThan(0)
})
```

## 部署前安全检查清单

在每次生产环境部署前：

- [ ] **机密信息**：无硬编码的机密信息，全部通过环境变量管理
- [ ] **输入验证**：验证所有用户输入
- [ ] **SQL 注入**：所有查询均已参数化
- [ ] **XSS**：净化所有用户内容
- [ ] **CSRF**：已启用防护
- [ ] **身份验证**：正确的令牌处理
- [ ] **授权**：已部署角色检查
- [ ] **速率限制**：在所有端点上启用
- [ ] **HTTPS**：生产环境强制开启
- [ ] **安全响应头**：配置 CSP、X-Frame-Options
- [ ] **错误处理**：错误消息中不包含敏感数据
- [ ] **日志记录**：日志中不包含敏感数据
- [ ] **依赖项**：保持最新且无漏洞
- [ ] **行级安全 (RLS)**：在 Supabase 中启用
- [ ] **CORS**：已正确配置
- [ ] **文件上传**：已验证（大小、类型）
- [ ] **钱包签名**：已验证（针对区块链应用）

## 资源

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Next.js 安全指南](https://nextjs.org/docs/security)
- [Supabase 安全指南](https://supabase.com/docs/guides/auth)
- [Web Security Academy](https://portswigger.net/web-security)

---

**请记住**：安全不是可选项。单个漏洞就可能危及整个平台。如有疑问，请采取最谨慎的做法。
