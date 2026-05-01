# Human Skill Tree App

## Deployment

- **永远使用 Vercel CLI 手动部署**，不依赖 GitHub webhook 自动部署
- 部署命令：`npx vercel --prod`
- 原因：Vercel 连接 Git 仓库后会强制要求 Git 用户关联，CLI 部署更可靠
- 部署前确保 `npx next build` 本地构建通过

## Git Repository

- `origin` — 私有仓库 `human-skill-tree-app`（完整代码，含付费功能）
- 仓库设为 **private**，代码不公开
- 部署通过 Vercel CLI：`npx vercel --prod`（不依赖 Git webhook）
- 推送前确认：`git remote -v && git branch`

## Tech Stack

- Next.js 16 + TypeScript + Tailwind CSS
- Supabase Auth + PostgreSQL
- OpenRouter API (AI models)
- next-intl (i18n: en, zh, ja)
- Vercel 部署

## Payment System

- 爱发电 (afdian) — 国内支付 (微信/支付宝)
- LemonSqueezy — 海外支付 (信用卡/PayPal)
- 三档计划: Free (10条/天), Basic ¥29.9/月 (100条/天), Pro ¥99.9/月 (无限)
- Admin 用户绕过所有限制
