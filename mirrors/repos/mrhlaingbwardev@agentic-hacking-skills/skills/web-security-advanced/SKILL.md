---
name: web-security
description: SECURE BY DEFAULT. When building login, API routes, file uploads, database queries, payments, user content, admin panels, webhooks, forms, password reset, OAuth, or any web feature — auto-detect what the user is building and inject the correct security patterns BEFORE it ships. Prevents env leaks, XSS, SQLi, IDOR, CSRF, SSRF, path traversal, mass assignment. Frameworks: Next.js, React, Express, Remix, SvelteKit.
---

# Web Security Skill

## CORE BEHAVIOR

**You are a security guard, not a reference manual.**

When the user writes code for ANY web feature, you MUST:
1. Scan the code for the feature type (see detection table below)
2. Check for missing security patterns
3. Proactively inject fixes BEFORE the user asks
4. Explain only what you changed and why

**NEVER wait for user to say "secure this."** If you see a form, you check it. If you see a route, you guard it. If you see a query, you parameterize it.

## AUTO-DETECTION TABLE

| What you see in code | Feature | Inject pattern # |
|---|---|---|
| `bcrypt`, `signup`, `signin`, `login`, `nextauth`, `clerk`, `auth()` missing | #AUTH | A |
| `route.ts`, `api/`, `server action`, `trpc`, `endpoint`, `handler` | #API | B |
| `formData`, `multer`, `upload`, `file`, `supabase.storage`, `s3.put` | #UPLOAD | C |
| `$queryRawUnsafe`, `execute(` + template, SQL string concat | #DB | D |
| `stripe`, `checkout`, `payment`, `subscription`, `billing` | #PAYMENT | E |
| `profile`, `settings`, `account`, `edit user`, `update user` | #PROFILE | F |
| `comment`, `review`, `textarea`, `dangerouslySetInnerHTML`, `innerHTML` | #CONTENT | G |
| `search`, `searchbar`, `filter`, `ILIKE`, `LIKE` with input | #SEARCH | H |
| `admin`, `dashboard`, `/admin`, `moderator`, `role` | #ADMIN | I |
| `webhook`, `signature`, `stripe.webhooks`, `constructEvent` | #WEBHOOK | J |
| `contact`, `newsletter`, `subscribe`, form without auth | #FORM | K |
| `forgot password`, `reset password`, `reset token` | #RESET | L |
| `middleware.ts`, `middleware` | #MIDDLEWARE | M |
| `oauth`, `google login`, `github login`, `social`, `PKCE` | #OAUTH | N |
| `.env`, `API_KEY=`, `SECRET=`, `sk-`, `ghp_`, `NEXT_PUBLIC_` + secret | #SECRETS | O |
| `create-next-app`, `create app`, new project init | #BOOTSTRAP | P |

---

## A. AUTH FLOW

```
SCAN: Is password hashed? Is there rate limiting? Is input validated? Cookies secure?
ACT: If any missing → inject immediately.
```

### Password Hashing (mandatory)
```typescript
// lib/auth.ts
import { hash, compare } from "bcryptjs"
const SALT = 12

export async function hashPassword(pw: string) { return hash(pw, SALT) }
export async function verifyPassword(pw: string, hashed: string) { return compare(pw, hashed) }
```

### Login Rate Limiting (mandatory)
```typescript
// lib/rate-limit.ts
import { LRUCache } from "lru-cache"

const attempts = new LRUCache<string, number>({ max: 10000, ttl: 15 * 60 * 1000 })

export function checkLoginLimit(ip: string, max = 5): boolean {
  const count = attempts.get(ip) || 0
  if (count >= max) return false
  attempts.set(ip, count + 1)
  return true
}
```

### Signup/Login Route Template
```typescript
import { z } from "zod"

const authSchema = z.object({
  email: z.string().email().max(255),
  password: z.string().min(8).max(128),
})

export async function POST(req: Request) {
  const ip = req.headers.get("x-forwarded-for") || "unknown"
  if (!checkLoginLimit(ip)) return Response.json({ error: "Too many attempts" }, { status: 429 })

  const parsed = authSchema.safeParse(await req.json())
  if (!parsed.success) return Response.json({ error: "Invalid input" }, { status: 400 })

  // For signup: const hashed = await hashPassword(parsed.data.password)
  // For login:  const valid = await verifyPassword(parsed.data.password, user.password)
}
```

### Session Cookie Config
```typescript
// auth.ts
cookies: {
  sessionToken: {
    options: {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      path: "/",
    }
  }
}
```

---

## B. API ROUTE GUARD

```
SCAN: Is there auth check at top? Input validated? Using session user ID (not body param)?
ACT: If missing → add guard + Zod schema.
```

### Every Authenticated Route Gets This
```typescript
import { auth } from "@/auth"

async function guard(req: Request) {
  const session = await auth()
  if (!session?.user?.id) return Response.json({ error: "Unauthorized" }, { status: 401 })
  return session
}

export async function GET(req: Request) {
  const session = await guard(req)
  if (session instanceof Response) return session

  // ALWAYS: session.user.id for data scoping
  // NEVER:  req.body.userId or req.query.userId (IDOR!)
}
```

### Input Validation on Every Route
```typescript
import { z } from "zod"

const schema = z.object({
  title: z.string().min(1).max(200),
  body: z.string().min(1).max(10000),
})

export async function POST(req: Request) {
  const session = await guard(req)
  if (session instanceof Response) return session

  const parsed = schema.safeParse(await req.json())
  if (!parsed.success) return Response.json({ error: "Invalid input" }, { status: 400 })

  const item = await db.post.create({
    data: { ...parsed.data, authorId: session.user.id }
  })
  return Response.json(item)
}
```

---

## C. FILE UPLOAD

```
SCAN: Is file type validated? Size checked? Path traversal prevented? Safe filename?
ACT: If ANY missing → inject the full upload-safe utility below.
```

```typescript
// lib/upload.ts
import { writeFile } from "fs/promises"
import path from "path"

const ALLOWED = {
  "image/jpeg": [".jpg", ".jpeg"],
  "image/png": [".png"],
  "image/webp": [".webp"],
  "image/gif": [".gif"],
  "application/pdf": [".pdf"],
} as const

const MAX = 10 * 1024 * 1024
const DIR = path.join(process.cwd(), "public/uploads")

export function validateFile(file: File) {
  if (!file || file.size === 0) return { ok: false, error: "No file" }
  if (file.size > MAX) return { ok: false, error: `Max ${MAX / 1024 / 1024}MB` }
  const types = ALLOWED[file.type as keyof typeof ALLOWED]
  if (!types) return { ok: false, error: "Invalid type" }
  const ext = path.extname(file.name).toLowerCase()
  if (!types.includes(ext)) return { ok: false, error: "Extension mismatch" }
  return { ok: true, error: null }
}

export function safeName(original: string) {
  const ext = path.extname(original)
  const base = original.replace(ext, "").replace(/[^a-zA-Z0-9_-]/g, "_").slice(0, 50)
  return `${base}-${crypto.randomUUID().slice(0, 8)}${ext}`
}

export async function saveFile(file: File) {
  const name = safeName(file.name)
  const filepath = path.join(DIR, name)

  if (!path.resolve(filepath).startsWith(path.resolve(DIR))) throw new Error("Path traversal")

  await writeFile(filepath, Buffer.from(await file.arrayBuffer()))
  return { url: `/uploads/${name}` }
}
```

---

## D. DATABASE QUERIES

```
SCAN: Look for $queryRawUnsafe(, string concatenation in SQL, template + variable in raw query.
ACT: If found → REPLACE with parameterized query or ORM. Never leave it.
```

```typescript
// BEFORE (dangerous — FIX THIS)
const users = await db.$queryRawUnsafe(`SELECT * FROM User WHERE email = '${email}'`)

// AFTER (safe — use this)
const users = await db.$queryRaw`SELECT * FROM "User" WHERE email = ${email}`

// BEST (use ORM)
const users = await db.user.findUnique({ where: { email } })
```

---

## E. PAYMENT

```
SCAN: Is price from server (not client)? Is webhook signature verified? Are stripe keys in server env only?
ACT: Fix price source, add webhook verification.
```

```typescript
// NEVER trust client price. ALWAYS server-side prices.
const PRICES: Record<string, number> = {
  "pro_monthly": 2900,
  "pro_yearly": 29000,
}

const schema = z.object({
  productId: z.string().refine(id => id in PRICES, "Invalid product"),
})

export async function POST(req: Request) {
  const session = await auth()
  if (!session?.user?.id) return Response.json({ error: "Unauthorized" }, { status: 401 })

  const parsed = schema.safeParse(await req.json())
  if (!parsed.success) return Response.json({ error: "Invalid request" }, { status: 400 })

  const checkout = await stripe.checkout.sessions.create({
    mode: "subscription",
    customer_email: session.user.email!,
    metadata: { userId: session.user.id },
    line_items: [{ price: parsed.data.productId, quantity: 1 }],
    success_url: `${process.env.NEXT_PUBLIC_URL}/billing?success=true`,
    cancel_url: `${process.env.NEXT_PUBLIC_URL}/billing?canceled=true`,
  })
  return Response.json({ url: checkout.url })
}
```

### Webhook Verification (mandatory for Stripe)
```typescript
export async function POST(req: Request) {
  const body = await req.text()
  const sig = req.headers.get("stripe-signature")!

  let event
  try {
    event = stripe.webhooks.constructEvent(body, sig, process.env.STRIPE_WEBHOOK_SECRET!)
  } catch {
    return Response.json({ error: "Invalid signature" }, { status: 400 })
  }
  // Process verified event...
}
```

---

## F. USER PROFILE

```
SCAN: Is userId from session, not body? Are sensitive fields stripped from response?
ACT: Use session.user.id. Strip password/token from response.
```

```typescript
export async function PUT(req: Request) {
  const session = await guard(req)
  if (session instanceof Response) return session

  const schema = z.object({
    name: z.string().min(1).max(100).regex(/^[\p{L}\s'-]+$/u),
    bio: z.string().max(500).optional(),
  })

  const parsed = schema.safeParse(await req.json())
  if (!parsed.success) return Response.json({ error: "Invalid input" }, { status: 400 })

  // ALWAYS session.user.id — NEVER from body
  const user = await db.user.update({
    where: { id: session.user.id },
    data: parsed.data,
  })

  // Strip sensitive fields
  const { password, ...safe } = user
  return Response.json(safe)
}
```

---

## G. USER CONTENT (Comments, Posts)

```
SCAN: Is dangerouslySetInnerHTML present WITHOUT DOMPurify? Is content validated?
ACT: Add DOMPurify sanitization. Add content validation.
```

### Frontend — Sanitize Before Render
```tsx
import DOMPurify from "isomorphic-dompurify"

function Comment({ content }: { content: string }) {
  return (
    <p dangerouslySetInnerHTML={{
      __html: DOMPurify.sanitize(content, {
        ALLOWED_TAGS: ["b", "i", "em", "strong", "a", "br", "p"],
        ALLOWED_ATTR: ["href", "target", "rel"],
      })
    }} />
  )
}
```

### Backend — Validate Before Store
```typescript
const schema = z.object({
  content: z.string().min(1).max(2000),
})

export async function POST(req: Request) {
  const session = await guard(req)
  if (session instanceof Response) return session

  const parsed = schema.safeParse(await req.json())
  if (!parsed.success) return Response.json({ error: "Invalid input" }, { status: 400 })

  const comment = await db.comment.create({
    data: { content: parsed.data.content, authorId: session.user.id }
  })
  return Response.json(comment)
}
```

---

## H. SEARCH

```typescript
// SAFE: parameterized ILIKE query
export async function GET(req: Request) {
  const { searchParams } = new URL(req.url)
  const q = searchParams.get("q")

  if (!q || q.length > 200) return Response.json({ results: [] })

  const results = await db.$queryRaw`
    SELECT id, title, excerpt FROM posts
    WHERE published = true
    AND (title ILIKE ${`%${q}%`} OR excerpt ILIKE ${`%${q}%`})
    LIMIT 20
  `
  return Response.json({ results })
}
```

---

## I. ADMIN PANEL

```typescript
import { auth } from "@/auth"

export async function requireAdmin() {
  const session = await auth()
  if (!session?.user || session.user.role !== "admin") throw new Error("Forbidden")
  return session
}

// In every admin route:
export async function GET(req: Request) {
  await requireAdmin()
  // Admin logic
}

// In admin layout:
export default async function AdminLayout({ children }: { children: React.ReactNode }) {
  const session = await auth()
  if (!session?.user || session.user.role !== "admin") redirect("/login")
  return <>{children}</>
}
```

---

## J. WEBHOOK ENDPOINT

```typescript
import { createHmac, timingSafeEqual } from "crypto"

function verifySig(body: string, sig: string, secret: string): boolean {
  const a = Buffer.from(createHmac("sha256", secret).update(body).digest("hex"))
  const b = Buffer.from(sig.replace("sha256=", ""))
  if (a.length !== b.length) return false
  return timingSafeEqual(a, b)
}

export async function POST(req: Request) {
  const body = await req.text()
  if (!verifySig(body, req.headers.get("x-signature") || "", process.env.WEBHOOK_SECRET!)) {
    return Response.json({ error: "Invalid signature" }, { status: 400 })
  }

  const event = JSON.parse(body)

  // Idempotency
  const exists = await db.event.findUnique({ where: { eventId: event.id } })
  if (exists) return Response.json({ status: "duplicate" })

  await db.$transaction([
    db.order.update({ where: { id: event.orderId }, data: { ... } }),
    db.event.create({ data: { eventId: event.id } }),
  ])
  return Response.json({ status: "ok" })
}
```

---

## K. PUBLIC FORMS (Contact, Newsletter)

```typescript
const limiter = rateLimit({ interval: 3600000 }) // 1 hour window

export async function POST(req: Request) {
  const ip = req.headers.get("x-forwarded-for") || "unknown"
  if (limiter.check(5, ip).isRateLimited) {
    return Response.json({ error: "Too many requests" }, { status: 429 })
  }

  const schema = z.object({
    name: z.string().min(1).max(100),
    email: z.string().email().max(255),
    message: z.string().min(10).max(5000),
  })

  const parsed = schema.safeParse(await req.json())
  if (!parsed.success) return Response.json({ error: "Invalid input" }, { status: 400 })

  // Process form...
  return Response.json({ ok: true })
}
```

---

## L. PASSWORD RESET

```typescript
import { randomBytes, createHash } from "crypto"

export async function createResetToken(userId: string) {
  const token = randomBytes(32).toString("hex")
  const hashed = createHash("sha256").update(token).digest("hex")
  const expires = new Date(Date.now() + 15 * 60 * 1000) // 15 min

  await db.passwordReset.create({ data: { userId, token: hashed, expires } })
  return token
}

// ALWAYS return same response (prevents email enumeration)
export async function requestReset(email: string) {
  const user = await db.user.findUnique({ where: { email } })
  if (user) {
    const token = await createResetToken(user.id)
    // await sendEmail(email, token)
  }
  return { message: "If that email exists, we sent a reset link." }
}
```

---

## M. MIDDLEWARE (Security Headers)

```typescript
// middleware.ts
import { NextResponse } from "next/server"

const HEADERS: Record<string, string> = {
  "X-Content-Type-Options": "nosniff",
  "X-Frame-Options": "DENY",
  "X-XSS-Protection": "0",
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
  "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
  "Content-Security-Policy": [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline'",
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data: blob: https:",
    "font-src 'self'",
    "connect-src 'self'",
  ].join("; "),
}

export function middleware(req: NextRequest) {
  const res = NextResponse.next()
  Object.entries(HEADERS).forEach(([k, v]) => res.headers.set(k, v))
  return res
}
```

---

## N. OAUTH CONFIG

```typescript
// Verify these are set correctly in auth config:
export const authConfig = {
  providers: [
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
  ],
  callbacks: {
    signIn: async ({ account, profile }) => {
      // Verify email
      if (account?.provider === "google") return !!(profile as any).email_verified
      return true
    },
  },
}
```

---

## O. SECRETS & ENV

```
SCAN: git diff --cached for: sk-, ghp_, API_KEY=, SECRET=, password=, token=
SCAN: .env in git? NEXT_PUBLIC_ with private key?
ACT: Remove from code. Move to .env. Add .gitignore. Create .env.example.
```

```gitignore
# MUST HAVE:
.env
.env*.local
```

```
# .env.example (safe to commit):
DATABASE_URL="postgresql://..."
NEXTAUTH_SECRET="openssl rand -base64 32"
NEXTAUTH_URL="http://localhost:3000"
NEXT_PUBLIC_APP_URL="http://localhost:3000"
```

---

## P. PROJECT BOOTSTRAP

When a new project is created, proactively:

1. Verify `.gitignore` has `.env`
2. Create `.env.example`
3. Generate secure random secrets (never hardcode)
4. Run `npm audit` / `pnpm audit`
5. Add security headers to middleware
6. Set secure session cookie defaults

---

## AUDIT MODE

When user says `secure my app` or `security audit`:

### Step 1 — Scan
```bash
# Read these files silently:
cat package.json       # detect framework
cat middleware.ts      # check headers
ls app/api/            # list routes
grep -r "dangerouslySetInnerHTML" --include="*.tsx"
grep -r "queryRawUnsafe" --include="*.ts"
grep -r "NEXT_PUBLIC_" --include=".env*"
cat .gitignore         # check .env is listed
```

### Step 2 — Report
```
SECURITY AUDIT RESULTS
======================

🔴 CRITICAL (fix now):
  - route.ts:15 — /api/users accepts userId from body (IDOR)
  - page.tsx:42 — dangerouslySetInnerHTML without DOMPurify
  - .env:3 — STRIPE_SECRET has NEXT_PUBLIC_ prefix

🟡 WARNING (fix before deploy):
  - middleware.ts missing security headers
  - No rate limiting on /api/auth/login
  - .env not in .gitignore

🟢 PASS:
  - All DB queries use ORM (Prisma)
  - Auth checks present on protected routes
```

### Step 3 — Fix
Ask "Apply all fixes?" then edit each file directly. Show diff for each change.

