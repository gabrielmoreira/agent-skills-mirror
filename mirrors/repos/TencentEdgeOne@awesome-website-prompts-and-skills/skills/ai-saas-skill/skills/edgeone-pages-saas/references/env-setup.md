# Environment Setup

本文档描述 **Step 4** —— 根据 Spec 生成 `.env.local` 并引导用户获取必要的密钥。

> 模板的 `.env.example` 里一共 **14 个变量**，但用户真正需要填的数量取决于 `Spec.features` 的开关。**不要让用户把 14 个全填满** —— 对大多数用户来说那是巨大的心理负担。

---

## ⛔ 安全红线

1. **`.env.local` 绝不能提交到 git**。`saas-starter` 的 `.gitignore` 已经覆盖了，别去改它。
2. **不要把密钥回显在日志 / README / 代码注释里**。用户粘贴后直接写入 `.env.local`，再用 `***` 掩码确认。
3. **`SUPABASE_SERVICE_ROLE_KEY` 权限极高**（能绕过 RLS），只能用在服务端代码里，强调给用户。
4. **Stripe secret key 泄露 = 直接损失**。填入前明确告知用户这是服务端密钥。
5. 部署到 EdgeOne Pages 时，环境变量应该在控制台配置，而不是把 `.env.local` 打进构建产物。这一步由 `edgeone-pages-deploy` skill 处理，本 skill 只负责本地开发用的 `.env.local`。

---

## 总流程

1. `cp .env.example .env.local`
2. 按 Spec.features **过滤出必要的 key 列表**（见下表）
3. 对每个必要 key，决定"立刻填"还是"先占位，稍后填"
4. 用 IDE 的问答工具批量收集用户提供的值
5. 写入 `.env.local`，输出掩码确认
6. 验证 `.gitignore` 仍然覆盖 `.env.local`

---

## 变量清单（按模块分组）

### 模块 A：App 基础（始终必填）

| 变量 | 用途 | 开发期取值 |
|------|------|------|
| `NEXT_PUBLIC_APP_URL` | 站点 URL，用于生成 OG / 邮件回链 | `http://localhost:3000` |

### 模块 B：Supabase（`features.auth` 或 `features.credits` 为 true 时必填）

| 变量 | 用途 | 获取方式 |
|------|------|------|
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase 项目 API URL | 见下方 "Supabase 获取流程" |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | 客户端匿名 key（公开 OK） | 同上 |
| `SUPABASE_SERVICE_ROLE_KEY` | 服务端 service role key（⚠️ 高权限） | 同上，务必保密 |

### 模块 C：Stripe（`features.credits` 为 true 时必填）

> 本模板中 **credits 与 Stripe 是强绑定的**：积分通过 Stripe 付费购买。只要 `features.credits=true`，以下 Stripe 变量就是必填。如果用户只想要"用户注册登录但不要付费"，应在 intake 阶段把 `features.credits` 设为 `false`（保留 `features.auth=true` 即可）。

| 变量 | 用途 | 获取方式 |
|------|------|------|
| `STRIPE_SECRET_KEY` | Stripe 服务端 key（`sk_test_...` 开发 / `sk_live_...` 生产） | Stripe Dashboard → Developers → API keys |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook 签名校验 | Dashboard → Webhooks → 新建 endpoint 后获取 |
| `STRIPE_CALLBACK_URL` | 支付成功/取消的回调 URL | 通常 = `NEXT_PUBLIC_APP_URL` |

### 模块 D：AI Provider（`features.aiImage` 为 true 时，至少填一个）

| 变量 | 用途 | 获取方式 |
|------|------|------|
| `FAL_API_KEY` | fal.ai API key | https://fal.ai/dashboard/keys |
| `FIREWORKS_API_KEY` | Fireworks AI key | https://fireworks.ai/account/api-keys |
| `AI_IMAGE_CREDIT_COST` | 每张 AI 图消耗的积分数 | 数字即可，例如 `10` |

> `.env.example` 只列了 FAL 和 Fireworks，但 `package.json` 里还引入了 OpenAI / Google / xAI / Replicate / DeepInfra / Luma / Together 等 SDK。如果用户想用其他 provider，需要额外配置对应的 API key（官方文档 `[PROVIDER]_API_KEY` 命名规范，例如 `OPENAI_API_KEY`、`GOOGLE_GENERATIVE_AI_API_KEY` 等，具体以 `src/lib/ai/*` 的代码为准）。**不确定时去读代码，不要编造变量名**。

### 模块 E：Admin（`features.admin` 为 true 时必填）

| 变量 | 用途 | 获取方式 |
|------|------|------|
| `ADMIN_EMAILS` | 管理员邮箱列表（逗号分隔） | 直接从 Spec.adminEmails 拼接 |

### 模块 F：Contentful CMS（`features.cms` 为 true 时必填）

| 变量 | 用途 | 获取方式 |
|------|------|------|
| `CONTENTFUL_SPACE_ID` | Contentful Space ID | https://app.contentful.com → Settings → API keys |
| `CONTENTFUL_ACCESS_TOKEN` | Delivery API token | 同上 |
| `CONTENTFUL_ENVIRONMENT` | Contentful 环境名 | 通常填 `master` |

---

## 根据 Spec 生成的必填列表（例子）

**例 1：默认规格（全开，但 `cms=false`）**
必填 8 个：
```
NEXT_PUBLIC_APP_URL
NEXT_PUBLIC_SUPABASE_URL
NEXT_PUBLIC_SUPABASE_ANON_KEY
SUPABASE_SERVICE_ROLE_KEY
STRIPE_SECRET_KEY
STRIPE_WEBHOOK_SECRET
STRIPE_CALLBACK_URL
FAL_API_KEY（或 FIREWORKS_API_KEY）
AI_IMAGE_CREDIT_COST
ADMIN_EMAILS
```

**例 2：极简免费工具（auth on，其他全关）**
必填 4 个：
```
NEXT_PUBLIC_APP_URL
NEXT_PUBLIC_SUPABASE_URL
NEXT_PUBLIC_SUPABASE_ANON_KEY
SUPABASE_SERVICE_ROLE_KEY
```

**例 3：纯展示站（auth 也关，类似官网）**
必填 1 个：
```
NEXT_PUBLIC_APP_URL
```

---

## Supabase 获取流程（高频）

如果 Spec.features.auth 或 credits 为 true，走这个 mini-guide：

1. 访问 https://supabase.com，注册 / 登录
2. 点 **New Project**，填名字和数据库密码（记下密码，后续可能用到）
3. 等待 1~2 分钟项目创建完成
4. 左侧菜单 **Project Settings → API**：
   - 复制 `Project URL` → 填入 `NEXT_PUBLIC_SUPABASE_URL`
   - 复制 `anon public` key → 填入 `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - 复制 `service_role` key（⚠️ secret） → 填入 `SUPABASE_SERVICE_ROLE_KEY`
5. 左侧菜单 **SQL Editor → New query**，粘贴 `database_init.sql` 的内容，Run
6. （启用 OAuth 时）**Authentication → Providers** 启用 Google / GitHub，填入对应 Client ID / Secret

---

## Stripe 获取流程（高频）

如果 Spec.features.credits 为 true 且用户确认要付费：

1. 访问 https://dashboard.stripe.com，注册 / 登录
2. 顶部确认是 **Test mode**（开发期一律测试模式）
3. **Developers → API keys**：
   - 复制 Secret key（`sk_test_...`）→ `STRIPE_SECRET_KEY`
4. **Developers → Webhooks → Add endpoint**：
   - Endpoint URL 本地开发可先填 `http://localhost:3000/api/webhook/stripe`（生产再换）
   - 或用 `stripe listen --forward-to localhost:3000/api/webhook/stripe` 本地代理
   - 选择要监听的事件（通常 `checkout.session.completed`、`invoice.paid` 等，以代码为准）
   - 创建后 **Signing secret** (`whsec_...`) → `STRIPE_WEBHOOK_SECRET`
5. `STRIPE_CALLBACK_URL` = `NEXT_PUBLIC_APP_URL`

---

## 写入 .env.local 的操作

采集完用户输入后：

```bash
# 示例内容（替换占位后写入）
cat > .env.local <<'EOF'
NEXT_PUBLIC_APP_URL=http://localhost:3000

NEXT_PUBLIC_SUPABASE_URL=<paste>
NEXT_PUBLIC_SUPABASE_ANON_KEY=<paste>
SUPABASE_SERVICE_ROLE_KEY=<paste>

# ...（仅写入必填的那些）
EOF
```

写完后：

```bash
# 掩码展示（确认不泄露全值）
awk -F= '{key=$1; val=$2; mask=substr(val,1,4) "***" substr(val,length(val)-3); print key "=" mask}' .env.local
```

最后确认 `.gitignore`：

```bash
grep -q "^\.env\.local$\|^\.env\*\.local$\|\.env" .gitignore && echo "✅ .env.local 已被 .gitignore 覆盖" || echo "⚠️ 需要手动添加"
```

---

## 常见问题

| 问题 | 排查 |
|------|------|
| `npm run dev` 启动后报 `Invalid URL` | 大概率 `NEXT_PUBLIC_SUPABASE_URL` 没填或拼错 |
| 登录成功但积分不显示 | `database_init.sql` 没执行，或 `SUPABASE_SERVICE_ROLE_KEY` 用错 |
| `/admin` 空白/重定向 | `ADMIN_EMAILS` 没填或邮箱大小写不匹配 |
| Stripe 支付回调失败 | 本地需要 `stripe listen` 代理，或 `STRIPE_WEBHOOK_SECRET` 跟实际 webhook 对不上 |
| AI 生图 401 | Provider key 错，或账户没充值 / 超出免费额度 |
| 部署到 EdgeOne Pages 后环境变量丢失 | `.env.local` 不会随构建上传；要在 EdgeOne Pages 控制台的 Environment Variables 单独配置 |

---

## 完成后

环境变量填齐后，回到 `SKILL.md` 的 **Step 5** 继续本地验证。
