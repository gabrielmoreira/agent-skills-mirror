# Template Setup

本文档描述 **Step 2** —— 如何把 `saas-starter` 模板拉到本地并完成依赖安装。

---

## 前置检查

在动手之前快速确认环境：

```bash
node -v      # 需要 >= 18
npm -v       # 任意版本
which npx    # 确认 npx 可用
```

如果 Node.js 版本低于 18，引导用户升级（`nvm install 20` 或 `nvm use 20`），然后再继续。

---

## 拉取模板

**首选方式：`degit`** —— 只下载代码快照，不带 `.git` 历史，最干净：

```bash
npx degit TencentEdgeOne/saas-starter <productNameKebab>
```

- `<productNameKebab>`：从 Spec 中取，例如 `pixora`、`my-ai-saas`
- 如果目标目录已存在且非空，degit 会失败 —— 询问用户是换名还是 `--force`
- 网络失败时，回退到：

  ```bash
  git clone --depth=1 https://github.com/TencentEdgeOne/saas-starter.git <productNameKebab>
  cd <productNameKebab> && rm -rf .git
  ```

拉完后：

```bash
cd <productNameKebab>
```

---

## 安装依赖

按用户环境偏好选一个（默认 `npm`）：

```bash
npm install
# 或
pnpm install
# 或
yarn
```

> 模板 `package.json` 锁定 Next.js 14.0.4 + React 18，不要让用户盲目升级 Next.js 15，可能有 App Router 兼容问题。

常见安装警告可以忽略：
- peer dep 警告（Radix UI / React 18）— 不影响运行
- deprecated 包提示 — 这是上游依赖的问题，不用管

安装失败的排查：

| 错误 | 原因 | 解决 |
|------|------|------|
| `ERESOLVE` 冲突 | 依赖版本冲突 | `npm install --legacy-peer-deps` |
| `EACCES` 权限 | npm 全局目录权限 | 用 nvm 管理 Node，不用 sudo |
| 网络超时 | npm 源慢 | `npm config set registry https://registry.npmmirror.com` |
| `gyp`/`node-gyp` 报错 | 本地没 Python/build-essential | 基本可以忽略（模板无原生模块），除非真的报错退出 |

---

## 预期目录结构

拉完依赖后，目录应该长这样（只列会被定制用到的文件/夹）：

```
<productNameKebab>/
├── .cursor/
│   └── rules/                    # Cursor AI 规则（可保留，可删）
├── .cursorrules                  # Cursor AI 规则（旧格式）
├── .env.example                  # ← Step 4 会用来生成 .env.local
├── .gitignore                    # 已覆盖 .env.local，别改
├── .windsurfrules                # Windsurf AI 规则
├── LICENSE
├── README.md
├── README_zh-CN.md
├── cms/
│   └── contentful/               # ← features.cms=false 时整个删
├── content/
│   ├── blog/                     # Markdown 博客源
│   └── cases/                    # 案例页源
├── database_init.sql             # ← Supabase 初始化脚本
├── dictionaries/
│   ├── en-US.json                # ← Step 3 改文案
│   ├── zh-CN.json                # ← Step 3 改文案
│   └── ...（其他 locale 可删）
├── middleware.ts                 # Next.js 中间件（i18n 路由）
├── next.config.js
├── package.json                  # ← Step 3 可能要删 AI/CMS/Stripe 依赖
├── postcss.config.js
├── public/                       # 静态资源（logo、OG 图）
├── scripts/                      # SEO 生成等工具脚本
├── src/
│   ├── app/
│   │   ├── admin/                # ← features.admin=false 时删
│   │   ├── ai/                   # ← features.aiImage=false 时删
│   │   ├── blog/                 # ← features.blog=false 时删
│   │   ├── cases/                # ← features.blog=false 时可删（同属内容页）
│   │   ├── globals.css           # ← Step 3 改配色
│   │   ├── layout.tsx            # ← Step 3 改站点 metadata
│   │   └── page.tsx              # 首页
│   ├── components/
│   │   ├── layout/               # Header / Footer
│   │   ├── sections/             # Hero / Features / Pricing
│   │   └── ui/                   # 基础组件（Button/Card 等，别动）
│   └── lib/                      # 工具函数（Supabase/Stripe/AI 客户端）
├── tailwind.config.js
└── tsconfig.json
```

### 目录实际结构验证

如果用户在运行 `ls` 后发现上面列出的某个目录不存在（说明上游模板更新了结构），**不要编造**，停下来读实际的 `src/app/` 和 `src/components/`，再决定怎么改。

---

## 确认检查点

完成本步后，把这份 checklist 发给用户确认：

- [ ] 已 `cd` 进入项目目录
- [ ] `node_modules/` 已生成
- [ ] `ls -la` 能看到 `.env.example`、`src/`、`package.json`
- [ ] 没有 `.git/` 目录（degit 不会带，git clone 路径要自行删除）

确认通过后进入 **Step 3 — 定制**（见 `customization.md`）。

---

## 可选：跳过本地的一键部署

如果用户表达"我不想本地开发，就想先看看线上效果"，可以直接引导他们用云端一键模板部署：

> 浏览器打开：https://edgeone.ai/pages/new?template=saas-starter
>
> 登录 EdgeOne 账号后会自动 fork 到 GitHub 并部署，拿到线上 URL 后再回来走本 skill 做定制。

但这条路不适合需要做深度定制的场景 —— 云端模板部署没办法定制化代码，最终还是得拉回本地改。主流程默认走 degit。
