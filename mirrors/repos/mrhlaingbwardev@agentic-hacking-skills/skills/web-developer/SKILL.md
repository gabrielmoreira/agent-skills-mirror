---
name: web-developer
description: Use when user says "web လုပ်မယ်", "website ဆောက်", "web app လုပ်", "site လုပ်ပေး", "landing page လုပ်", "build a website", "create web app". Discovery-first web development — ALWAYS interviews the client BEFORE writing code: project type (static vs db-backed), architecture, features, UI/UX inspiration, stack, hosting. Then proposes plan, confirms, and builds.
---

# Web Developer Skill

## TRIGGER RULES

**IMMEDIATELY activate when user mentions building:**
- "web လုပ်မယ်", "website ဆောက်မယ်", "web app လုပ်ချင်တယ်", "site တစ်ခု လုပ်ပေး"
- "landing page", "portfolio site", "e-commerce လုပ်မယ်", "blog ဆောက်"
- "build a website", "make me a web app", "create a site"

**CRITICAL: Do NOT write a single line of code until PHASE 0 discovery is answered.**
Jumping straight to code is the failure mode this skill exists to prevent.

---

## PHASE 0: CLIENT DISCOVERY (MANDATORY — before ANY code)

Ask these as ONE organized numbered list (not one-by-one drip). Wait for answers.
If the user is vague, offer concrete examples for each option to help them decide.

**1. Project Type** — which one?
   - Static website (portfolio, landing, company profile, blog — no database)
   - Dynamic web app (database + auth + user content)
   - E-commerce / booking / dashboard (complex flows)

**2. Core Purpose & Features** — what must it DO? List needed features:
   - e.g. contact form, blog/CMS, login/signup, payments, search, admin panel,
     gallery, booking, multi-language (MM/EN?), newsletter...

**3. Architecture Preference**
   - Simple HTML/CSS/JS (max control, no framework)
   - Modern static (Astro / Next.js static)
   - Full-stack app (Next.js / Remix + DB + API routes)
   - No preference → you recommend based on features

**4. UI/UX Inspiration** — this decides the whole visual direction:
   - Which existing websites does the user LIKE? (paste 1–3 URLs or describe)
   - Mood: minimal/clean · bold/colorful · dark/premium · playful/soft
   - Light mode, dark mode, or both?
   - Any logo / brand colors already?

**5. Data & Auth Needs** (if dynamic)
   - Database: Postgres/Supabase? SQLite? none?
   - Auth: email+password? Google/GitHub OAuth? none?

**6. Pages / Sitemap** — rough page list (Home, About, Blog, Contact...)?

**7. Hosting & Domain**
   - Vercel / Cloudflare Pages / VPS / not decided yet
   - Domain ready? Name?

**8. Content Assets**
   - Texts/copy ready? Images/logo ready? Or should placeholders be used first?

---

## PHASE 1: PROPOSE THE PLAN (after answers)

Present for confirmation before scaffolding:

```
PROJECT PLAN
═══════════════════════
Type:        <static | web app>
Stack:       <framework + styling + db + auth>
Pages:       <sitemap>
Data model:  <tables/entities if any>
UI direction: <inspiration summary → design tokens: colors, fonts, mood>
Hosting:     <target>
Est. flow:   scaffold → core pages → features → polish → deploy
═══════════════════════
Shall I start?
```

### ARCHITECTURE REVIEW (mandatory when stack choice matters)

For anything beyond a static page, include in the plan and confirm:

- **Why this stack** — one line of reasoning vs the alternative you rejected.
  ("Next.js SSR because blog + future auth; rejected Astro since payments need server routes")
- **Scale sanity check** — "at 100 users? at 10,000?" State what breaks first
  (db connections? image bandwidth? rate limits?) and that the current design survives it.
- **Data model sketch** — tables/entities, key relations, who owns each row (`userId` on
  every user-owned table from day one — retrofitting ownership later causes IDOR).
- **Trust boundaries drawn early** — public pages vs authenticated routes vs admin,
  decided BEFORE coding so guards aren't bolted on afterwards.
- Get explicit ✅ on the plan before scaffolding. No silent architecture decisions.

**Stack defaults when user has no preference:**

| Need | Default |
|---|---|
| Static portfolio/landing | Astro or plain HTML + Tailwind |
| Blog/content site | Astro (markdown collections) |
| Web app with db + auth | Next.js + Tailwind + shadcn/ui + Supabase(Postgres) |
| E-commerce | Next.js + Stripe + Postgres |
| Dashboard/tool | Next.js + shadcn/ui |

---

## PHASE 2: BUILD

- Scaffold → implement page by page / feature by feature. Show progress per step.
- **Mobile responsive from the first line** — never desktop-only.
- Semantic HTML, accessible components (labels, alt, contrast).
- Loading/error states for every fetch. Empty states designed, not blank.
- Env/secrets in `.env` only; `.env.example` created; `.gitignore` covers `.env*`.

### SECURITY GATE (applies WHILE building, not after)

Load `web-security` skill for full patterns. Minimum bar per feature — a route is
NOT done until its row passes:

| Feature shipped | Must include before moving on |
|---|---|
| Login/signup | bcrypt/argon hash · zod validation · rate limit on auth routes · generic error messages (no user enumeration) |
| Session/cookies | httpOnly · Secure in prod · SameSite · server-side session check on EVERY protected route |
| Any API route | session-derived userId (never body/query) · input schema validated · ownership checked in query (`where: { id, userId }`) |
| DB queries | parameterized / ORM only — zero string-concatenated SQL anywhere |
| File upload | MIME + extension + size checks · randomized filename · path-traversal guard |
| Payments | server-side prices only · webhook signature verified · idempotency |
| User content render | sanitized (DOMPurify or framework auto-escaping, never raw innerHTML) |
| Password reset | hashed token with expiry · identical response whether email exists or not |
| Admin anything | role check server-side + layout guard — client-side hiding is NOT security |

### PRE-SHIP SECURITY SWEEP (before Phase 3)

```
[ ] grep codebase: queryRawUnsafe / execute( + concat / dangerouslySetInnerHTML
[ ] every protected route has server-side auth check (spot-check 100%)
[ ] security headers middleware present (CSP, X-Frame-Options, nosniff, HSTS)
[ ] .env not tracked by git; no secrets in NEXT_PUBLIC_*
[ ] npm/pnpm audit run; critical vulns fixed or acknowledged
[ ] rate limits on: login, register, password reset, public forms
```

## PHASE 3: POLISH & HANDOFF

Before declaring done:
- [ ] SEO: title/meta description per page, OG tags, sitemap.xml, robots.txt
- [ ] Favicon, 404 page
- [ ] Performance pass: image optimization (`next/image` or width/height attrs), font preloading
- [ ] Lighthouse-style self-check: console errors? broken links? dead assets?
- [ ] Deploy steps for chosen host (or run deploy if credentials configured)
- [ ] Handoff note: how to update content, where env vars live

## ANTI-PATTERNS (never do)

- ❌ Coding before Phase 0 questions are answered
- ❌ Asking questions one at a time across many turns
- ❌ Choosing a heavy stack for a simple need (Next.js+DB for a landing page)
- ❌ Silent architecture decisions — stack/tradeoffs/scale must be confirmed
- ❌ Ignoring stated inspiration and applying generic template style
- ❌ Marking an auth/api/db route "done" without its SECURITY GATE row passing
- ❌ Shipping without mobile check, error states, or the pre-ship security sweep
