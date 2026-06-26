---
name: security-review
description: 在添加身份验证、处理用户输入、操作机密信息、创建 API 接口或实现支付/敏感功能时使用此技能。提供全面的安全自查清单和模式。
origin: ECC
---

# 安全审查技能（Security Review Skill）

此技能（Skill）旨在确保所有代码遵循安全最佳实践，并识别潜在的漏洞。

## 何时启用

- 实现身份验证（Authentication）或授权（Authorization）时
- 处理用户输入或文件上传时
- 创建新的 API 接口（Endpoints）时
- 操作机密（Secrets）或凭据（Credentials）时
- 实现支付功能时
- 存储或传输敏感数据时
- 集成第三方 API 时

## 安全自查清单

### 1. 机密管理（Secrets Management）

#### ❌ 严禁行为
```typescript
const apiKey = "sk-proj-xxxxx"  // 硬编码机密
const dbPassword = "password123" // 出现在源代码中
```

#### ✅ 推荐做法
```typescript
const apiKey = process.env.OPENAI_API_KEY
const dbUrl = process.env.DATABASE_URL

// 验证机密是否存在
if (!apiKey) {
  throw new Error('未配置 OPENAI_API_KEY')
}
```

#### 验证步骤
- [ ] 无硬编码的 API 密钥、令牌（Tokens）或密码
- [ ] 所有机密均存储在环境变量中
- [ ] `.env.local` 已包含在 .gitignore 中
- [ ] Git 历史记录中不包含机密信息
- [ ] 生产环境机密配置在托管平台（如 Vercel, Railway）

### 2. 输入验证（Input Validation）

#### 始终验证用户输入
```typescript
import { z } from 'zod'

// 定义验证模式（Schema）
const CreateUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(100),
  age: z.number().int().min(0).max(150)
})

// 在处理前进行验证
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
  // 大小检查（最大 5MB）
  const maxSize = 5 * 1024 * 1024
  if (file.size > maxSize) {
    throw new Error('文件过大（最大 5MB）')
  }

  // 类型检查
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif']
  if (!allowedTypes.includes(file.type)) {
    throw new Error('无效的文件类型')
  }

  // 扩展名检查
  const allowedExtensions = ['.jpg', '.jpeg', '.png', '.gif']
  const extension = file.name.toLowerCase().match(/\.[^.]+$/)?.[0]
  if (!extension || !allowedExtensions.includes(extension)) {
    throw new Error('无效的文件扩展名')
  }

  return true
}
```

#### 验证步骤
- [ ] 所有用户输入均通过模式（Schemas）验证
- [ ] 文件上传受到限制（大小、类型、扩展名）
- [ ] 查询中不直接使用用户输入
- [ ] 使用白名单验证（而非黑名单）
- [ ] 错误消息不泄露敏感信息

### 3. SQL 注入防护（SQL Injection Prevention）

#### ❌ 严禁拼接 SQL
```typescript
// 危险 - 存在 SQL 注入漏洞
const query = `SELECT * FROM users WHERE email = '${userEmail}'`
await db.query(query)
```

#### ✅ 始终使用参数化查询
```typescript
// 安全 - 参数化查询
const { data } = await supabase
  .from('users')
  .select('*')
  .eq('email', userEmail)

// 或使用原始 SQL
await db.query(
  'SELECT * FROM users WHERE email = $1',
  [userEmail]
)
```

#### 验证步骤
- [ ] 所有数据库查询均使用参数化查询
- [ ] SQL 中无字符串拼接
- [ ] 正确使用 ORM 或查询构建器（Query Builder）
- [ ] Supabase 查询已正确过滤

### 4. 身份验证与授权（Authentication & Authorization）

#### JWT 令牌处理
```typescript
// ❌ 错误做法：存储在 localStorage 中（易受 XSS 攻击）
localStorage.setItem('token', token)

// ✅ 正确做法：使用 httpOnly cookies
res.setHeader('Set-Cookie',
  `token=${token}; HttpOnly; Secure; SameSite=Strict; Max-Age=3600`)
```

#### 授权检查
```typescript
export async function deleteUser(userId: string, requesterId: string) {
  // 务必先验证授权
  const requester = await db.users.findUnique({
    where: { id: requesterId }
  })

  if (requester.role !== 'admin') {
    return NextResponse.json(
      { error: 'Unauthorized' },
      { status: 403 }
    )
  }

  // 执行删除操作
  await db.users.delete({ where: { id: userId } })
}
```

#### 行级安全性（Supabase Row Level Security）
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
- [ ] 令牌存储在 httpOnly cookies 中（而非 localStorage）
- [ ] 敏感操作前进行授权检查
- [ ] 在 Supabase 中启用了行级安全性（RLS）
- [ ] 实现了基于角色的访问控制（RBAC）
- [ ] 会话管理（Session Management）安全

### 5. XSS 防护（XSS Prevention）

#### 清理 HTML
```typescript
import DOMPurify from 'isomorphic-dompurify'

// 始终清理用户提供的 HTML
function renderUserContent(html: string) {
  const clean = DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'p'],
    ALLOWED_ATTR: []
  })
  return <div dangerouslySetInnerHTML={{ __html: clean }} />
}
```

#### 内容安全策略（Content Security Policy）
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
- [ ] 清理了用户提供的 HTML
- [ ] 配置了 CSP 响应头
- [ ] 无未经验证的动态内容渲染
- [ ] 使用了 React 内置的 XSS 防护机制

### 6. CSRF 防护（CSRF Protection）

#### CSRF 令牌（Tokens）
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

#### SameSite Cookies
```typescript
res.setHeader('Set-Cookie',
  `session=${sessionId}; HttpOnly; Secure; SameSite=Strict`)
```

#### 验证步骤
- [ ] 在状态变更操作中使用 CSRF 令牌
- [ ] 所有 Cookie 均设置 SameSite=Strict
- [ ] 实现了双重提交 Cookie 模式（Double-submit cookie pattern）

### 7. 速率限制（Rate Limiting）

#### API 速率限制
```typescript
import rateLimit from 'express-rate-limit'

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 分钟
  max: 100, // 每个窗口期最大 100 次请求
  message: '请求过于频繁'
})

// 应用于路由
app.use('/api/', limiter)
```

#### 高消耗操作
```typescript
// 为搜索操作设置更严格的速率限制
const searchLimiter = rateLimit({
  windowMs: 60 * 1000, // 1 分钟
  max: 10, // 每分钟最大 10 次请求
  message: '搜索请求过于频繁'
})

app.use('/api/search', searchLimiter)
```

#### 验证步骤
- [ ] 所有 API 接口均设置了速率限制
- [ ] 对高消耗操作设置了更严格的限制
- [ ] 基于 IP 的速率限制
- [ ] 基于用户的速率限制（已认证用户）

### 8. 敏感数据泄露（Sensitive Data Exposure）

#### 日志记录
```typescript
// ❌ 错误做法：记录敏感数据
console.log('User login:', { email, password })
console.log('Payment:', { cardNumber, cvv })

// ✅ 正确做法：屏蔽敏感数据
console.log('User login:', { email, userId })
console.log('Payment:', { last4: card.last4, userId })
```

#### 错误消息
```typescript
// ❌ 错误做法：泄露内部细节
catch (error) {
  return NextResponse.json(
    { error: error.message, stack: error.stack },
    { status: 500 }
  )
}

// ✅ 正确做法：通用的错误消息
catch (error) {
  console.error('Internal error:', error)
  return NextResponse.json(
    { error: '发生错误，请稍后重试。' },
    { status: 500 }
  )
}
```

#### 验证步骤
- [ ] 日志中不包含密码、令牌或机密
- [ ] 向用户展示通用的错误消息
- [ ] 详细错误仅记录在服务器日志中
- [ ] 不向用户暴露堆栈轨迹（Stack traces）

### 9. 区块链安全 (Solana)（Blockchain Security）

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
  // 验证收款人
  if (transaction.to !== expectedRecipient) {
    throw new Error('无效的收款人')
  }

  // 验证金额
  if (transaction.amount > maxAmount) {
    throw new Error('金额超出限制')
  }

  // 验证用户余额充足
  const balance = await getBalance(transaction.from)
  if (balance < transaction.amount) {
    throw new Error('余额不足')
  }

  return true
}
```

#### 验证步骤
- [ ] 已验证钱包签名
- [ ] 已校验交易详情
- [ ] 交易前进行余额检查
- [ ] 不存在盲签（Blind transaction signing）行为

### 10. 依赖项安全（Dependency Security）

#### 定期更新
```bash
# 检查漏洞
npm audit

# 自动修复可修复的问题
npm audit fix

# 更新依赖
npm update

# 检查过期的包
npm outdated
```

#### 锁定文件
```bash
# 务必提交锁定文件
git add package-lock.json

# 在 CI/CD 中使用以确保可重现的构建
npm ci  # 而不是 npm install
```

#### 验证步骤
- [ ] 依赖项保持最新
- [ ] 无已知漏洞（npm audit clean）
- [ ] 已提交锁定文件
- [ ] 在 GitHub 上启用了 Dependabot
- [ ] 定期进行安全更新

## 安全测试（Security Testing）

### 自动化安全测试
```typescript
// 测试身份验证
test('需要身份验证', async () => {
  const response = await fetch('/api/protected')
  expect(response.status).toBe(401)
})

// 测试授权
test('需要管理员角色', async () => {
  const response = await fetch('/api/admin', {
    headers: { Authorization: `Bearer ${userToken}` }
  })
  expect(response.status).toBe(403)
})

// 测试输入验证
test('拒绝无效输入', async () => {
  const response = await fetch('/api/users', {
    method: 'POST',
    body: JSON.stringify({ email: 'not-an-email' })
  })
  expect(response.status).toBe(400)
})

// 测试速率限制
test('执行速率限制', async () => {
  const requests = Array(101).fill(null).map(() =>
    fetch('/api/endpoint')
  )

  const responses = await Promise.all(requests)
  const tooManyRequests = responses.filter(r => r.status === 429)

  expect(tooManyRequests.length).toBeGreaterThan(0)
})
```

## 部署前安全自查清单

在任何生产环境部署之前：

- [ ] **机密 (Secrets)**: 无硬编码机密，全部在环境变量中
- [ ] **输入验证 (Input Validation)**: 所有用户输入均已验证
- [ ] **SQL 注入 (SQL Injection)**: 所有查询均已参数化
- [ ] **XSS**: 用户内容已清理
- [ ] **CSRF**: 已启用防护
- [ ] **身份验证 (Authentication)**: 正确的令牌处理
- [ ] **授权 (Authorization)**: 角色检查已就绪
- [ ] **速率限制 (Rate Limiting)**: 在所有接口上均已启用
- [ ] **HTTPS**: 在生产环境中强制执行
- [ ] **安全响应头 (Security Headers)**: 已配置 CSP, X-Frame-Options
- [ ] **错误处理 (Error Handling)**: 错误中不包含敏感数据
- [ ] **日志记录 (Logging)**: 日志中不包含敏感数据
- [ ] **依赖项 (Dependencies)**: 保持最新，无已知漏洞
- [ ] **行级安全性 (Row Level Security)**: 在 Supabase 中已启用
- [ ] **CORS**: 已正确配置
- [ ] **文件上传 (File Uploads)**: 已验证（大小、类型）
- [ ] **钱包签名 (Wallet Signatures)**: 已验证（如果是区块链项目）

## 资源

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Next.js 安全指南](https://nextjs.org/docs/security)
- [Supabase 安全指南](https://supabase.com/docs/guides/auth)
- [Web Security Academy](https://portswigger.net/web-security)

---

**请记住**：安全不是可选项。一个漏洞就可能破坏整个平台。如有疑虑，请宁可保守。
