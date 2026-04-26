# User Prompt Intake

本文档描述 **Skill 启动的第一步** —— 如何采集用户的产品意图，最终产出一个结构化的 Spec 对象供后续步骤使用。

三条分支：**有 Prompt / 内置问答 / 默认规格**。

---

## Spec 对象（所有分支最终都要产出这个）

```json
{
  "productName": "MyAISaaS",
  "productNameKebab": "my-ai-saas",
  "tagline": "Generate stunning AI images in seconds",
  "industry": "ai-image",
  "primaryColorHSL": "260 51% 48%",
  "accentColorHSL": "257 100% 65%",
  "features": {
    "auth": true,
    "credits": true,
    "aiImage": true,
    "blog": true,
    "admin": true,
    "cms": false,
    "i18n": true
  },
  "locales": ["en-US", "zh-CN"],
  "adminEmails": ["admin@example.com"]
}
```

字段说明：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `productName` | string | ✓ | 产品展示名，会写入 metadata、Header、i18n 字典 |
| `productNameKebab` | string | ✓ | 项目目录名 / degit 目标目录（小写短横线） |
| `tagline` | string | ✓ | 首页 Hero 的一句话 slogan |
| `industry` | string | ✓ | 行业定位，用于选择文案基调；枚举：`ai-image` / `ai-text` / `ai-video` / `saas-tool` / `course` / `membership` / `other` |
| `primaryColorHSL` | string (HSL H S% L%) | ✓ | CSS 变量 `--primary` 的值，空格分隔 3 个数字 |
| `accentColorHSL` | string | ✓ | CSS 变量 `--accent` |
| `features.*` | boolean | ✓ | 功能模块开关，决定是否保留对应目录/依赖/环境变量 |
| `locales` | string[] | ✓ | 支持的语言，从 `["en-US","zh-CN"]` 中选择一个或两个 |
| `adminEmails` | string[] | 条件 | 仅当 `features.admin=true` 时必填 |

**依赖规则（硬约束，必须在确认 Spec 前校验）：**

- `features.credits=true` ⟹ `features.auth=true`（积分依赖用户体系）
- `features.aiImage=true` ⟹ `features.credits=true`（AI 生图要扣积分）
- `features.admin=true` ⟹ `features.auth=true`
- `features.cms=true` ⟹ `features.blog=true`（CMS 用来管博客内容）

如果用户的选择违反了依赖，应当提示并请用户调整。

---

## 分支 A：用户提供了自己的 Prompt

### A.1 收集 Prompt

告诉用户：

> 把你的 Prompt / 产品描述贴进来就行，越具体越好。可以包含：产品名、做什么、目标用户、想要的颜色/风格、是否需要支付/AI/博客/后台、支持哪些语言。
>
> 如果有信息缺失我会追问，不会凭空捏造。

### A.2 解析 Prompt 为 Spec

按下表从 Prompt 文本里抽取字段：

| Spec 字段 | 抽取策略 |
|-----------|----------|
| `productName` | 找引号包裹的专有名词，或 "叫 XX" / "called XX" / "name: XX" 模式 |
| `tagline` | 找 "slogan / tagline / 一句话 / 卖点" 附近的句子，否则根据 `industry` 生成候选 |
| `industry` | 关键词匹配：`图片/image` → `ai-image`；`文本/文案/copywriting` → `ai-text`；`视频/video` → `ai-video`；`课程/course/学习` → `course`；`会员/membership` → `membership`；未命中 → `saas-tool` 或 `other` |
| `primaryColorHSL` | 颜色词（紫/蓝/绿 …）或 HEX 值 → 转成 HSL 三元组，见下表 |
| `accentColorHSL` | 默认取 primary 色相 +5°、饱和度 +20%、亮度 +15%；或者用户显式指定 |
| `features.*` | 关键词匹配：`支付/stripe/付费 → aiImage 相关依赖`；`博客/blog → blog`；`后台/admin → admin`；`Contentful/CMS → cms`；提到"不需要/去掉 XX" → 对应 false |
| `locales` | `中文/英文/bilingual` → `["en-US","zh-CN"]`；`仅中文` → `["zh-CN"]`；`only English` → `["en-US"]`；未提及 → 询问 |
| `adminEmails` | 从 Prompt 中用邮箱正则抓取；未找到且 `features.admin=true` → 追问 |

常见颜色词 → HSL（仅作参考，用户显式 HEX 优先）：

| 颜色 | primaryColorHSL | accentColorHSL |
|------|-----------------|----------------|
| 紫（默认） | `260 51% 48%` | `257 100% 65%` |
| 蓝 | `221 83% 53%` | `217 91% 60%` |
| 绿 | `142 71% 45%` | `142 76% 56%` |
| 橙 | `25 95% 53%` | `32 95% 60%` |
| 红 | `0 84% 55%` | `0 84% 65%` |
| 粉 | `330 81% 60%` | `328 85% 70%` |
| 青 | `180 84% 40%` | `180 100% 55%` |
| 黑灰（极简） | `0 0% 13%` | `0 0% 30%` |

HEX → HSL 可以用浏览器 devtools 或任何在线工具转换；写入 `globals.css` 时只保留 `H S% L%` 三段，前导不带 `hsl(`，因为模板使用 Tailwind 的 `hsl(var(--x) / <alpha>)` 模式。

### A.3 补问缺失字段

把解析结果展示给用户，并逐条追问缺失的必填字段。**不要编造**——如果缺少就问。

### A.4 展示并确认 Spec

把最终 Spec 以 JSON 代码块形式给用户看一遍，明确问：

> 以上是我解析出来的产品规格，有没有要调整的？没问题就可以开始脚手架。

用户确认后进入 Step 2。

---

## 分支 B：用户没有 Prompt —— 内置问答

按顺序问，一次问 1～2 题（用 IDE 的 `ask_followup_question`）。**不要一口气问完所有问题**，节奏要自然。

### B.1 产品定位（必问）

> 你想做哪个方向的 SaaS？
>
> - AI 图片生成（默认，和模板最贴合）
> - AI 文本工具（文案 / 翻译 / 摘要）
> - AI 视频生成
> - 通用 SaaS 工具
> - 课程 / 知识付费
> - 会员订阅制
> - 其他（描述一下）

→ 落到 `industry`

### B.2 产品名 + 一句话卖点（必问）

> 给它起个名字，再加一句话简介。例如：
>
> - 名字：Pixora
> - 一句话：3 秒生成专业级 AI 插画

→ `productName` + `productNameKebab` + `tagline`

### B.3 配色（必问）

> 主色调想要什么感觉？
>
> - 紫（模板默认，科技感）
> - 蓝（经典 SaaS）
> - 绿（效率 / 金融）
> - 橙（活泼 / 创作工具）
> - 黑白极简
> - 自定义（贴 HEX 或 HSL）

→ `primaryColorHSL` + `accentColorHSL`（按 A.2 的颜色表）

### B.4 支付（必问）

> 需要 Stripe 付费 + 积分体系吗？
>
> - 要（推荐，模板默认行为）
> - 不要（做免费工具）

→ `features.credits`（关联 `features.auth` 强制为 true）

### B.5 AI 图像生成（取决于 industry）

仅当 `industry ∈ {ai-image, ai-video}` 或用户在 B.1 选了 AI 方向时问：

> 启用 AI 图片生成功能？（需要 FAL / Fireworks API Key）
>
> - 启用
> - 先不启用，后面再加

→ `features.aiImage`

### B.6 Blog + CMS（选问）

> 需要自带博客 / 案例页吗？
>
> - 需要博客（Markdown）
> - 需要博客 + Contentful CMS
> - 都不需要

→ `features.blog` + `features.cms`

### B.7 管理后台（选问）

> 需要 `/admin` 管理后台？（看用户、订单、发积分）
>
> - 需要（填入管理员邮箱）
> - 不需要

如果选需要，追问：

> 管理员邮箱？可以多个，用逗号分隔。

→ `features.admin` + `adminEmails`

### B.8 多语言（选问）

> 支持哪些语言？
>
> - 英文 + 中文（默认）
> - 仅英文
> - 仅中文

→ `locales`

### B.9 汇总并确认

按 A.4 格式展示 Spec，确认后进入 Step 2。

---

## 分支 C：完全默认规格

当用户选择"完全默认"或明确表达"按模板默认走"时，直接使用：

```json
{
  "productName": "AI SaaS Starter",
  "productNameKebab": "ai-saas-starter",
  "tagline": "Launch your AI SaaS in minutes",
  "industry": "ai-image",
  "primaryColorHSL": "260 51% 48%",
  "accentColorHSL": "257 100% 65%",
  "features": {
    "auth": true,
    "credits": true,
    "aiImage": true,
    "blog": true,
    "admin": true,
    "cms": false,
    "i18n": true
  },
  "locales": ["en-US", "zh-CN"],
  "adminEmails": []
}
```

注意：`adminEmails` 默认空 —— 需要在 Step 4 写环境变量时提醒用户填上，否则 `/admin` 会没有任何人可以登录。

展示给用户，一键确认后直接进入 Step 2。

---

## 异常处理

| 情况 | 处理 |
|------|------|
| 用户 Prompt 完全不包含 SaaS/产品信息（比如贴了一段代码） | 指出这不像产品 Prompt，引导走内置问答 |
| 用户输入违反依赖规则（例如要 credits 但不要 auth） | 解释依赖关系，让用户在"调整 features"或"两者都开"之间选 |
| 用户迟迟不回答必填问题 | 提供一个"先用默认值，后面再改"的选项，继续推进 |
| 用户给的 HEX 颜色格式错误 | 要求再确认，不要强行转换 |
