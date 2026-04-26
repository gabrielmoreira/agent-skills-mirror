# Customization

本文档描述 **Step 3** —— 根据 Spec 对模板做定制。

> **原则：targeted edits only。** 只改必要的文件，不要大范围重写。每一条定制都先说清要改哪个文件、为什么改，再动手。

---

## 操作顺序

按这个顺序做，依赖关系最自然：

1. 品牌信息（站名、slogan、metadata）
2. 配色（CSS 变量）
3. 多语言词典（文案）
4. 功能模块裁剪（按 Spec.features 删除目录 / 依赖）
5. `package.json` 元信息更新（name、description）

每步做完 **口头汇报一次**（"已更新 Header 站名、已同步到 zh-CN / en-US 词典"），方便用户打断纠正。

---

## 1. 品牌信息

### 1.1 `src/app/layout.tsx` — 站点 metadata

找到形如下面的 `metadata` 导出：

```ts
export const metadata: Metadata = {
  title: '...',
  description: '...',
  // ...
}
```

把 `title` 改成 `${Spec.productName} — ${Spec.tagline}`，`description` 改成 Spec.tagline（或更完整的一段）。OpenGraph / Twitter 字段同步更新。

### 1.2 `src/components/layout/Header.tsx` — 导航栏品牌名

搜索原 logo 文案（通常是 `"SaaS Starter"` 或 `"Starter"`），替换为 `Spec.productName`。如果模板里是引用 i18n key（例如 `{dict.brand.name}`），直接改词典即可，不动代码。

### 1.3 `public/favicon.ico` / `public/logo.*`

提示用户替换，但 **不要帮用户生成图标**（没有图形能力）。留给用户手动：

> 记得替换 `public/favicon.ico` 和 `public/logo.svg`（或 `.png`），尺寸建议 512×512。暂时不换也不影响开发。

---

## 2. 配色

### 2.1 改 `src/app/globals.css`

定位到 `:root { ... }` 块，修改：

```css
:root {
  --primary: <Spec.primaryColorHSL>;              /* 例如: 221 83% 53% */
  --primary-dark: <Spec.primaryColorHSL 的深色变体>;
  --accent: <Spec.accentColorHSL>;
  --accent-dark: <Spec.accentColorHSL>;
  /* 其他变量保持不变 */
}
```

**`-dark` 变体的生成规则**（如果 Spec 没给）：

- `*-dark` = 把亮度 L 调整 ±12（浅色主调取更亮，深色主调取更暗）
- 饱和度 S 可以保持不变，或者 ±10

举例（紫色，模板默认）：
```css
--primary: 260 51% 48%;
--primary-dark: 257 59% 60%;
--accent: 257 100% 65%;
--accent-dark: 257 100% 65%;
```

举例（蓝色）：
```css
--primary: 221 83% 53%;
--primary-dark: 221 83% 65%;
--accent: 217 91% 60%;
--accent-dark: 217 91% 72%;
```

### 2.2 不要改 `tailwind.config.js`

模板把颜色通过 `hsl(var(--primary) / <alpha-value>)` 绑定到了 CSS 变量，改 `globals.css` 就够。**不要**去改 Tailwind 的 `theme.extend.colors` —— 那会让两边不同步。

### 2.3 验证配色是否生效

`npm run dev` 后观察：
- Header CTA 按钮颜色
- Hero section 的渐变
- Features / Pricing 的高亮边框

如果看起来没变，检查是不是浏览器缓存（Ctrl+Shift+R 强刷）。

---

## 3. 多语言词典

### 3.1 定位词典文件

```
dictionaries/
├── en-US.json
├── zh-CN.json
└── ...（其他语言）
```

### 3.2 按 Spec.locales 裁剪

删除 `Spec.locales` 不包含的文件。**同时**：

- 检查 `middleware.ts` 和 `next.config.js` 里是否有 locale 白名单常量，同步裁剪
- 检查 `src/lib/` 下是否有 `getDictionary.ts` 一类的加载器，同步裁剪

### 3.3 批量替换品牌词

在保留下来的每个 json 文件中，把所有出现的原始品牌名（如 `"SaaS Starter"`）替换成 `Spec.productName`。Hero 的 slogan key（通常是 `hero.title` / `hero.subtitle`）替换为 `Spec.tagline`。

改动后用 `jq` 或者 Node 校验 JSON 合法：

```bash
node -e "JSON.parse(require('fs').readFileSync('dictionaries/en-US.json','utf8'))"
```

### 3.4 产品方向文案微调

根据 `Spec.industry`，可以给用户建议改掉几处关键文案：

| industry | 建议改的 key（示例，以实际词典为准） |
|----------|--------|
| `ai-image` | `hero.*`, `features.*`（保持原样基本够用） |
| `ai-text` | 把"图片生成"改为"文本生成" |
| `ai-video` | 改成"视频生成 + 模型/时长"相关表述 |
| `course` | `features` 改为"课程目录 / 学习进度 / 证书"等 |
| `membership` | `pricing` 改为"月度/年度会员"表述 |

**不要替用户写大量营销文案。** 改关键词即可，让用户自己再打磨。

---

## 4. 功能模块裁剪

**每删一个模块前，都先告诉用户要删哪些文件 + 改哪些依赖，等用户确认再动。**

> ⚠️ **通用守则：先 `ls` 再 `rm`。** 下面列的路径是 `saas-starter` 当前版本的预期位置，但上游可能改结构（比如把 `src/app/ai` 换成路由组 `src/app/(ai)`）。**每条 `rm -rf` 执行前先 `ls` 确认目录真实存在**；不存在就跳过并汇报，不要编造路径也不要强行删除。

### 4.1 `features.aiImage = false`

删除：
```bash
ls -d src/app/ai && rm -rf src/app/ai
ls -d src/app/api/ai 2>/dev/null && rm -rf src/app/api/ai   # 可能不存在
```

`package.json` 中移除 AI SDK 依赖：

- 打开 `package.json`，**删除 `dependencies` 里所有以 `@ai-sdk/` 开头的条目**（上游可能新增/删减，不要用死名单）
- 同时删除顶层的 `"ai"` 包（Vercel AI SDK 主包）
- 如果 `devDependencies` 里也有，一并清掉

> 参考：当前模板版本常见的 `@ai-sdk/*` 包括 deepinfra / fal / fireworks / google / luma / openai / replicate / togetherai / xai 等，但**以实际 `package.json` 为准**。

环境变量移除：`FAL_API_KEY`、`FIREWORKS_API_KEY`、`AI_IMAGE_CREDIT_COST`

可能需要改：`src/components/layout/Header.tsx` 导航中 "AI" 链接；`src/app/page.tsx` 首页 CTA；pricing 页的积分套餐文案。

### 4.2 `features.credits = false`

先警告用户：

> 关掉积分意味着 AI 图生图、付费套餐都会没有计费逻辑。如果你仍然要 Stripe 付费，需要你自己改成"订阅到期"模型。是否继续？

确认后：
- 删除 `src/components/` 中积分相关组件（查找 "credit"、"Credits" 关键字）
- `database_init.sql` 中保留用户表，移除积分表（`credits`、`credit_transactions` 等）
- 移除 pricing 页的积分相关展示

### 4.3 `features.blog = false`

```bash
ls -d src/app/blog && rm -rf src/app/blog
ls -d content/blog && rm -rf content/blog
```

`package.json` 移除：`gray-matter`、`remark`、`remark-html`、`react-syntax-highlighter`、`@types/react-syntax-highlighter`、`date-fns`（如果没其他地方用）

`src/components/layout/Footer.tsx` / `Header.tsx` 里的 Blog 链接同步去掉。

### 4.4 `features.admin = false`

```bash
ls -d src/app/admin && rm -rf src/app/admin
ls -d src/app/api/admin 2>/dev/null && rm -rf src/app/api/admin   # 可能不存在
```

环境变量移除：`ADMIN_EMAILS`

`middleware.ts` 中如果有 `/admin` 路径守卫逻辑，同步删掉。

### 4.5 `features.cms = false`

```bash
ls -d cms/contentful && rm -rf cms/contentful
```

`package.json` 移除：
- `dependencies`: `contentful`、`@contentful/rich-text-html-renderer`、`@contentful/rich-text-types`、`turndown`
- `scripts.contentful:export` 整条删掉

环境变量移除：`CONTENTFUL_SPACE_ID`、`CONTENTFUL_ACCESS_TOKEN`、`CONTENTFUL_ENVIRONMENT`

`public/images/contentful/` 如果存在，也一并删除。

### 4.6 `features.i18n = false`（只保留一种语言时）

本质上是把 `dictionaries/` 裁剪到只剩一个文件。**注意 `middleware.ts` 很可能在做 locale 重定向**，读一下并相应简化（或者保留 middleware 不动，只留一个 locale 也能跑）。

---

## 5. `package.json` 元信息

```json
{
  "name": "<Spec.productNameKebab>",
  "version": "0.1.0",
  "description": "<Spec.tagline>",
  "private": true
}
```

保留 `"private": true`，避免手滑 `npm publish` 泄露。

---

## 6. 清理 AI 规则文件（可选）

模板自带：
- `.cursorrules`
- `.cursor/rules/`
- `.windsurfrules`

如果用户不用对应工具，可以删掉；用的话保留。**不会影响运行。**

---

## 定制完成后的自检

跑一遍：

```bash
npm run lint      # 应该无错
npm run build     # 关键 —— 确保所有删除没留下悬空 import
```

如果 `build` 失败：
- "Cannot find module" → 某个文件 import 了被删掉的模块，顺藤摸瓜删掉 import 或整个文件
- "Type error" → TS 类型引用丢失，同上
- 环境变量缺失 → Step 4 `.env.local` 要填齐

build 通过后，进入 **Step 4 — 环境变量**（见 `env-setup.md`）。
