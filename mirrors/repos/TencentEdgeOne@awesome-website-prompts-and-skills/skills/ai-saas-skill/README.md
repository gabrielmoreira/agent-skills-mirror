# EdgeOne Pages SaaS Skill

一份引导 AI Agent 基于 [`TencentEdgeOne/saas-starter`](https://github.com/TencentEdgeOne/saas-starter) 模板快速搭建 SaaS 网站，并最终部署到 EdgeOne Pages 的 Skill。

> 本 Skill 是官方 [`edgeone-pages-skills`](https://github.com/TencentEdgeOne/edgeone-pages-skills) 的补充，职责聚焦于 **「从 0 起步搭一个 SaaS 站点」**，部署阶段会交由官方 `edgeone-pages-deploy` Skill 完成。

---

## 这个 Skill 做什么

用户只要说一句 **"帮我搭一个 AI SaaS 网站部署到 EdgeOne Pages"** 之类的话，AI Agent 会：

1. **先询问用户有没有自己的 Prompt**
   - 有 → 按用户 Prompt 解析产品定位、功能模块、配色、文案
   - 没有 → 走内置问答流程，依次问清产品方向 / 配色 / 是否启用支付 / 是否启用 AI 图像生成 / 多语言需求
2. **使用 `npx degit TencentEdgeOne/saas-starter <project>` 拉取模板**（不带 git 历史）
3. **按用户意图对模板做定制**：品牌文案、配色（CSS 变量）、多语言词典、功能模块裁剪（Stripe / AI / Contentful / Admin 等可开关）
4. **生成 `.env.local`** 并交互式引导用户填入必要的 Supabase / Stripe / AI Provider 密钥
5. **指引本地启动** `next dev`（模板默认）或 `edgeone pages dev`（如需边缘函数/KV 联调）
6. **衔接部署**：提示用户调用 `edgeone-pages-deploy` Skill 完成上线

---

## 目录结构

```
ai-saas-skill/
├── README.md                              # 你正在看的文件
└── skills/
    └── edgeone-pages-saas/
        ├── SKILL.md                       # Skill 入口（frontmatter + 主决策流程）
        └── references/                    # 按需加载的详细文档
            ├── user-prompt-intake.md      # 有/无 Prompt 的双分支问答流程
            ├── template-setup.md          # degit 脚手架 + 依赖 + 目录映射
            ├── customization.md           # 品牌/配色/文案/模块裁剪的文件定位
            └── env-setup.md               # 环境变量清单 + 各服务申请指引
```

遵循 Anthropic `skill-creator` 规范：`SKILL.md` 保持轻量（入口 + 决策树），细节文档放 `references/` 按需加载。

---

## 安装方式

### 方式一：自然语言安装（推荐）

在支持 Skills 的 AI 编程工具（Claude Code / CodeBuddy / Cursor 等）中：

> 帮我安装这个 skill：`<this-repo-url>/ai-saas-skill`

AI Agent 会自动拉取并放到对应位置。

### 方式二：手动安装

把 `skills/edgeone-pages-saas/` 整个目录复制到你的工具对应 skills 目录即可，例如：

- **Claude Code**：`~/.claude/skills/`
- **CodeBuddy**：`~/.codebuddy/skills/`
- **Cursor**：项目 `.cursor/rules/` 或全局 skills 目录

---

## 触发方式

在 AI 对话中使用自然语言，示例：

- "帮我用 saas-starter 搭一个 AI 图片生成的 SaaS 网站部署到 EdgeOne Pages"
- "基于 saas-starter 做一个卖课 SaaS"
- "I have a prompt for my SaaS, help me build it on EdgeOne Pages"
- "初始化一个 SaaS 项目到 EdgeOne Pages"

AI Agent 识别到意图后，**第一件事就是询问你有没有自己的 Prompt**。

---

## 与其他 EdgeOne Pages Skill 的关系

| Skill | 职责 | 来源 |
|-------|------|------|
| **edgeone-pages-saas**（本 Skill） | 脚手架 + 模板定制（从 0 到可运行） | 本仓库 |
| `edgeone-pages-dev` | 在已有 Pages 项目里写 Edge/Cloud Functions、中间件、KV | 官方 |
| `edgeone-pages-deploy` | 把项目部署上线到 EdgeOne Pages | 官方 |

三者可以串联使用：**saas → dev（可选，加自定义函数） → deploy**。

### 是否需要先装官方两个 skill？

**不强依赖**。本 Skill 自成一体，单独装就能完成「脚手架 + 定制 + 本地跑通」。

但强烈建议 **至少和 `edgeone-pages-deploy` 一起装**，这样最后一步能让 AI 自动接管部署（装 CLI、登录、上传、返回 URL）。否则用户最后要自己敲部署命令。

| 你想做的事 | 需要装的 Skill |
|-----------|---------------|
| 只想生成一个本地能跑的 SaaS 项目 | 仅 `edgeone-pages-saas` |
| 生成 + 自动部署上线（**推荐**） | `edgeone-pages-saas` + `edgeone-pages-deploy` |
| 生成 + 后续可能要加自定义函数/KV + 自动部署 | 三个全装 |

官方两个 Skill 的安装方式参见：<https://github.com/TencentEdgeOne/edgeone-pages-skills>

---

## 前置依赖

- Node.js ≥ 18
- npm / pnpm / yarn 任一
- （部署阶段需要）EdgeOne Pages 账号

---

## License

MIT
