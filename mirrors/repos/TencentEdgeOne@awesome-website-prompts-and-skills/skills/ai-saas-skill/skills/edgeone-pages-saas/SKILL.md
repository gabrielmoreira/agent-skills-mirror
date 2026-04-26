---
name: edgeone-pages-saas
description: >-
  This skill scaffolds and customizes a production-ready SaaS website on top of the
  TencentEdgeOne/saas-starter template (Next.js 14 + TypeScript + Tailwind + Supabase + Stripe + AI),
  and prepares it for deployment to EdgeOne Pages. It should be used when the user wants to
  start a new SaaS project, AI SaaS, or AI tool site from scratch — e.g.
  "build a SaaS site on EdgeOne Pages", "scaffold an AI SaaS with saas-starter",
  "帮我用 saas-starter 搭一个 SaaS", "初始化一个 AI 图片生成 SaaS 部署到 EdgeOne Pages",
  "create a new AI SaaS project".
  The skill first asks whether the user has their own product Prompt. If yes, it parses the
  Prompt to derive brand, features, color palette, and copy; if no, it runs a short built-in
  questionnaire (product direction / color / payments on-off / AI on-off / i18n).
  It then uses `npx degit TencentEdgeOne/saas-starter` to bootstrap, applies customizations,
  generates `.env.local`, and guides local run.
  Do NOT trigger when the user already has a running project and only wants to add a single
  function/API (use edgeone-pages-dev).
  Do NOT trigger for pure deployment of an existing project (use edgeone-pages-deploy).
  Do NOT trigger for non-SaaS static sites, blogs, or portfolios.
metadata:
  author: edgeone-pages-saas
  version: "1.0.0"
---

# EdgeOne Pages SaaS Scaffolding Skill

Scaffold and customize a SaaS website from the [`TencentEdgeOne/saas-starter`](https://github.com/TencentEdgeOne/saas-starter) template, then hand it off to the deploy skill.

## When to use this skill

- User wants to **start a new SaaS site** (AI SaaS, AI tool, membership site, etc.) on EdgeOne Pages
- User mentions the `saas-starter` template explicitly
- User wants a Next.js + Supabase + Stripe SaaS foundation with credits / auth / payments / AI

**Do NOT use for:**
- Adding a single API/function to an existing project → use `edgeone-pages-dev`
- Deploying an already-built project → use `edgeone-pages-deploy`
- Plain static sites, blogs, landing pages without SaaS features

## How to use this skill (for the coding agent)

Follow the **main flow** below top-to-bottom. Load `references/*.md` only when the flow tells you to — do NOT preload everything.

---

## ⛔ Critical Rules (never skip)

1. **ALWAYS ask the user about their own Prompt FIRST**, before doing anything else. This is the entry gate of the skill.
2. **Never fabricate the user's product** — if information is missing and the user has no Prompt, run the built-in questionnaire in `references/user-prompt-intake.md`.
3. **Never rewrite the template's source tree wholesale.** Apply targeted edits only — see `references/customization.md` for the exact files to touch.
4. **Use `npx degit TencentEdgeOne/saas-starter <project>`** to bootstrap (no `.git` history). Do not run `git clone` unless degit is unavailable.
5. **Never commit `.env.local` or any real API keys** to git. Make sure `.gitignore` covers it (the template already does).
6. **DO NOT deploy inside this skill.** Deployment belongs to `edgeone-pages-deploy`. In Step 6, BEFORE telling the user "you can deploy now", **MUST verify that `edgeone-pages-deploy` skill is installed locally** (check whether `~/.codebuddy/skills/edgeone-pages-deploy/` — or its Windows equivalent `%USERPROFILE%\.codebuddy\skills\edgeone-pages-deploy\` — exists). If not installed, follow the guided-install branch in Step 6.3 instead of just leaving a text hint.
7. **The template's `package.json` uses `next dev`** (NOT `edgeone pages dev`). Only suggest `edgeone pages dev` when the user actually needs to develop/debug Edge Functions, Cloud Functions, or KV locally — and then guide via `edgeone-pages-dev` skill.
8. **Confirm destructive operations before running** (removing unused modules, deleting locale files, rewriting config). Show the plan, then proceed after user says go.

---

## Main Flow

### Step 1 — Gate question: does the user have a Prompt?

**This is mandatory and happens FIRST.** Use the IDE's question UI (e.g. `ask_followup_question`) to ask:

> 开始之前先问一下：你有没有自己准备好的 Prompt / 产品描述？
>
> - **有** — 贴进来，我会据此定位品牌 / 功能 / 配色 / 文案
> - **没有** — 我会用内置问答引导你，问几个关键问题
> - **完全默认** — 直接按模板默认（AI 图片生成 SaaS，紫色主题，中英双语）落地，后续再改

Branch:
- User provides a Prompt → **read `references/user-prompt-intake.md` § "Prompt 解析"** and extract a structured spec
- User chooses the questionnaire → **read `references/user-prompt-intake.md` § "内置问答"** and run through the questions
- User chooses default → skip intake, use default spec in `references/user-prompt-intake.md` § "默认规格"

Output of this step: a **Spec object** with at least the following fields:
```
{
  productName, tagline, industry,
  primaryColorHSL, accentColorHSL,
  features: { auth, credits, aiImage, blog, admin, cms, i18n },
  locales: [...],
  adminEmails: [...]
}
```

Show the Spec back to the user and ask for confirmation before moving on.

---

### Step 2 — Scaffold the project

Read **`references/template-setup.md`** and follow it to:
1. Pick a project directory name (from Spec.productName, kebab-case)
2. Run `npx degit TencentEdgeOne/saas-starter <dir>`
3. `cd <dir>` and install dependencies (`npm install` / `pnpm install` / `yarn`)
4. Verify the directory tree matches the expected layout

Do **not** run any build yet.

---

### Step 3 — Apply customizations

Read **`references/customization.md`** and apply edits based on the Spec:

| Spec field | Target file(s) |
|------------|----------------|
| productName, tagline | `src/app/layout.tsx` (metadata), `src/components/layout/Header.tsx`, `dictionaries/en-US.json`, `dictionaries/zh-CN.json` |
| primaryColorHSL, accentColorHSL | `src/app/globals.css` (`:root` block — `--primary`, `--primary-dark`, `--accent`, `--accent-dark`) |
| features.auth = false | (rare) remove `/auth` routes, strip Supabase; **warn the user this breaks credits/admin** |
| features.credits = false | remove credits UI, simplify DB schema from `database_init.sql` |
| features.aiImage = false | remove `src/app/ai/`, remove `@ai-sdk/*` deps from `package.json`, remove `FAL_API_KEY` / `FIREWORKS_API_KEY` from env |
| features.blog = false | remove `src/app/blog/`, `content/blog/` |
| features.admin = false | remove `src/app/admin/`, remove `ADMIN_EMAILS` env |
| features.cms = false | remove `cms/contentful/`, Contentful deps, `contentful:export` script, CMS env vars |
| features.i18n (locales) | prune `dictionaries/` to requested locales |

**Apply edits one module at a time and report progress.** If a destructive change has downstream impact (e.g. removing auth kills credits), call it out and ask for confirmation.

---

### Step 4 — Environment variables

Read **`references/env-setup.md`** and:
1. Copy `.env.example` → `.env.local`
2. Based on the enabled features, produce a **filtered env list** (only keys the user actually needs)
3. For each required key, either:
   - Ask the user to paste the value, or
   - Guide them to the provider's dashboard and wait
4. Write the collected values into `.env.local`
5. Remind: **never commit `.env.local`**

Optional Supabase schema step: if `features.auth` or `features.credits` is on, point the user to `database_init.sql` and the Supabase SQL Editor (one-paragraph summary is enough — this skill doesn't manage DB execution).

---

### Step 5 — Local verification

Run (or tell the user to run):

```bash
npm run dev     # starts Next.js on http://localhost:3000
```

> The template's default dev command is `next dev` (port 3000). If the user wants to debug Edge Functions / Cloud Functions / KV Storage on EdgeOne Pages locally, they should switch to `edgeone pages dev` (port 8088) — and load the `edgeone-pages-dev` skill for guidance.

Ask the user to open the URL and confirm:
- Homepage renders
- Language switcher works (if i18n enabled)
- Auth signup works (if Supabase env filled)

If something breaks, diagnose common causes:
- Missing env var → check `.env.local` matches the filtered list from Step 4
- Supabase schema not initialized → run `database_init.sql`
- Port conflict → change port via `next dev -p <port>`

---

### Step 6 — Hand off to deployment

**6.1 前置检查 — 确认 `edgeone-pages-deploy` skill 是否已安装**

在向用户发出"可以部署了"的提示之前，**先检查 deploy skill 是否存在**。skills 安装后会落到以下两个位置之一（本地已安装 = 对应目录存在）：

| 平台 | 安装目录 |
|------|---------|
| macOS / Linux | `~/.codebuddy/skills/edgeone-pages-deploy/` |
| Windows | `%USERPROFILE%\.codebuddy\skills\edgeone-pages-deploy\` |

使用 `list_dir`（或等价的目录列举能力）检查该目录是否存在且非空。**不要**用 `cat`/`read_file` 之类的方式，因为 skill 内部文件结构可能变化，目录存在即说明安装成功。

**检查结果分支：**

- **存在** → 进入 **6.2 正常交接**
- **不存在** → 进入 **6.3 引导安装**

---

**6.2 正常交接（deploy skill 已安装）**

对用户说：

> ✅ 项目已就绪，本地跑通后随时可以部署。
>
> 直接告诉我 **"部署到 EdgeOne Pages"**（或 "deploy to EdgeOne Pages"），我会加载 `edgeone-pages-deploy` skill 接管上线流程（CLI 版本检查、登录、首次部署建项目、URL 解析等全套）。

**不要**在本 skill 内执行 `edgeone pages deploy`——那是 deploy skill 的职责，避免重复实现和流程漂移。

---

**6.3 引导安装（deploy skill 未安装）**

使用 IDE 的选择 UI（如 `ask_followup_question`）让用户选择后续路径：

> ⚠️ 检测到你还没安装 **edgeone-pages-deploy** skill，这个 skill 负责把项目一键部署到 EdgeOne Pages（处理 CLI 版本、登录、首次建项目、URL 解析等全套流程）。
>
> 你希望怎么处理？
>
> - **安装 deploy skill（推荐）** — 我会引导你 2 步装完，然后回来继续部署
> - **手动裸部署** — 用 `edgeone` CLI 直接操作，我给你最小命令集
> - **暂不部署** — 项目已本地就绪，后续你可以自己选时机上线

**分支 A — 用户选择"安装 deploy skill"：**

给用户以下指引（不要自己去 clone/download —— skill 安装路径和认证方式可能随 CodeBuddy 版本变化）：

> 安装步骤：
>
> 1. 打开 CodeBuddy 的 **Skills 管理页面**（IDE 侧边栏 → Skills，或命令面板搜索 "Install Skill"）
> 2. 搜索 `edgeone-pages-deploy`（或从 <https://github.com/TencentEdgeOne/edgeone-pages-skills> 添加）
> 3. 安装完成后回到对话框，对我说一句 **"装好了，部署"** 即可

等待用户回复"装好了"之后，**再次执行 6.1 的前置检查**验证目录已出现，然后进入 6.2 正常交接。

如果用户反馈安装失败或找不到 Skills 管理入口，降级引导到分支 B（手动裸部署），不要让用户卡在这一步。

**分支 B — 用户选择"手动裸部署"：**

给出最小命令集（**仅最小集**——不要在这里复刻 deploy skill 的完整能力，如 site 选择、token 管理、URL 解析等；那是 deploy skill 的职责，重复实现只会让两边漂移）：

```bash
# 1. 安装 CLI（首次）
npm install -g edgeone@latest

# 2. 登录（首次，会开浏览器授权）
edgeone login

# 3. 在项目根目录部署
cd <your-project>
edgeone pages deploy -n <project-name>
```

关键提示（仅说这两条，其他交给用户自行查 CLI 文档）：

- 首次 deploy 会自动在 EdgeOne Pages 控制台创建项目并生成 `edgeone.json`，后续 deploy 不用再带 `-n`
- deploy 成功后的访问 URL 形如 `https://<project>-xxx.edgeone.cool?eo_token=...&eo_time=...`——**`eo_token` / `eo_time` 查询参数必须保留**，去掉会 401

**分支 C — 用户选择"暂不部署"：**

简短收尾：

> 项目已本地就绪。随时想上线，对我说 **"部署到 EdgeOne Pages"** 或自行运行 `edgeone pages deploy` 都行。

---

**不管走哪个分支，都不要在本 skill 内自行实现 deploy 的完整流程**（CLI 版本检查、China/Global site 选择、token 保存管理、URL 鉴权参数解析等）。

---

## Routing

| Step | Read |
|------|------|
| Gate question + Prompt parsing / questionnaire / default spec | [references/user-prompt-intake.md](references/user-prompt-intake.md) |
| degit bootstrap, dependency install, directory map | [references/template-setup.md](references/template-setup.md) |
| Brand / color / copy / feature-module file locations | [references/customization.md](references/customization.md) |
| Full env variable list + how to obtain each key | [references/env-setup.md](references/env-setup.md) |

---

## Quick Reference

**Template repo:** https://github.com/TencentEdgeOne/saas-starter
**One-click deploy (alternative to this skill):** https://edgeone.ai/pages/new?template=saas-starter
**Bootstrap command:** `npx degit TencentEdgeOne/saas-starter my-saas`
**Default dev:** `npm run dev` (port 3000, runs `next dev`)
**Hand-off to deploy skill:** user says "deploy to EdgeOne Pages" / "部署到 EdgeOne Pages"
