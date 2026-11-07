# OAuth 第三方登录配置指南

本文档介绍如何配置 Google 和 GitHub 第三方登录，以及 Cloudflare Turnstile 人机验证。

## 目录

- [Google OAuth 配置](#google-oauth-配置)
- [GitHub OAuth 配置](#github-oauth-配置)
- [Cloudflare Turnstile 配置](#cloudflare-turnstile-配置)
- [部署配置说明](#部署配置说明)
- [常见问题](#常见问题)

---

## Google OAuth 配置

### 步骤 1：创建 Google Cloud 项目

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 点击顶部的项目选择器，然后点击「新建项目」
3. 输入项目名称（如 `QuantDinger`），点击「创建」

### 步骤 2：配置 OAuth 同意屏幕

1. 在左侧菜单中，选择「API 和服务」→「OAuth 同意屏幕」
2. 选择用户类型：
   - **外部**：允许任何 Google 账户登录（推荐）
   - **内部**：仅限组织内用户（需要 Google Workspace）
3. 填写应用信息：
   - 应用名称：`QuantDinger`
   - 用户支持电子邮件：您的邮箱
   - 开发者联系信息：您的邮箱
4. 点击「保存并继续」，跳过「范围」和「测试用户」，完成配置

### 步骤 3：创建 OAuth 2.0 客户端 ID

1. 在左侧菜单中，选择「API 和服务」→「凭据」
2. 点击「+ 创建凭据」→「OAuth 客户端 ID」
3. 选择应用类型：**Web 应用**
4. 填写名称：`QuantDinger Web Client`
5. 添加「已授权的重定向 URI」：
   ```
   http://localhost:5000/api/auth/oauth/google/callback
   ```
   > 部署到服务器后，需要添加生产环境的 URI（见下文）
6. 点击「创建」
7. 复制生成的 **客户端 ID** 和 **客户端密钥**

### 步骤 4：配置 .env 文件

```bash
# Google OAuth
GOOGLE_CLIENT_ID=你的客户端ID.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=你的客户端密钥
GOOGLE_REDIRECT_URI=http://localhost:5000/api/auth/oauth/google/callback
```

---

## GitHub OAuth 配置

### 步骤 1：创建 GitHub OAuth App

1. 访问 [GitHub Developer Settings](https://github.com/settings/developers)
2. 点击「OAuth Apps」→「New OAuth App」
3. 填写应用信息：
   - **Application name**：`QuantDinger`
   - **Homepage URL**：`http://localhost:8080`（或您的域名）
   - **Authorization callback URL**：
     ```
     http://localhost:5000/api/auth/oauth/github/callback
     ```
4. 点击「Register application」

### 步骤 2：获取凭据

1. 在应用详情页面，复制 **Client ID**
2. 点击「Generate a new client secret」生成密钥
3. 立即复制 **Client Secret**（只显示一次）

### 步骤 3：配置 .env 文件

```bash
# GitHub OAuth
GITHUB_CLIENT_ID=你的Client_ID
GITHUB_CLIENT_SECRET=你的Client_Secret
GITHUB_REDIRECT_URI=http://localhost:5000/api/auth/oauth/github/callback
```

---

## Cloudflare Turnstile 配置

Turnstile 是 Cloudflare 提供的免费、隐私友好的人机验证服务，用于防止机器人攻击。

### 步骤 1：创建 Turnstile Widget

1. 访问 [Cloudflare Turnstile](https://dash.cloudflare.com/?to=/:account/turnstile)
2. 点击「Add site」
3. 填写信息：
   - **Site name**：`QuantDinger`
   - **Domain**：添加您的域名（本地开发可添加 `localhost`）
   - **Widget Mode**：选择 `Managed`（推荐）或 `Invisible`
4. 点击「Create」

### 步骤 2：获取密钥

创建成功后，您将看到：
- **Site Key**：前端使用，可公开
- **Secret Key**：后端使用，需保密

### 步骤 3：配置 .env 文件

```bash
# Cloudflare Turnstile
TURNSTILE_SITE_KEY=你的Site_Key
TURNSTILE_SECRET_KEY=你的Secret_Key
```

---

## 部署配置说明

当您将应用部署到服务器并绑定域名时，需要更新配置。

### 场景 1：前后端同域（推荐）

假设您的域名是 `yourdomain.com`，前后端通过 nginx 反向代理部署在同一域名下：
- 前端：`https://yourdomain.com`
- 后端 API：`https://yourdomain.com/api`

**.env 配置：**
```bash
# 前端地址（OAuth 成功后跳转）
FRONTEND_URL=https://yourdomain.com

# Google OAuth
GOOGLE_REDIRECT_URI=https://yourdomain.com/api/auth/oauth/google/callback

# GitHub OAuth
GITHUB_REDIRECT_URI=https://yourdomain.com/api/auth/oauth/github/callback
```

### 场景 2：前后端分离域名

假设：
- 前端：`https://yourdomain.com`
- 后端 API：`https://api.yourdomain.com`

**.env 配置：**
```bash
FRONTEND_URL=https://yourdomain.com

GOOGLE_REDIRECT_URI=https://api.yourdomain.com/api/auth/oauth/google/callback

GITHUB_REDIRECT_URI=https://api.yourdomain.com/api/auth/oauth/github/callback
```

### 更新 OAuth 提供商配置

部署后，您还需要在 OAuth 提供商后台更新回调地址：

**Google Cloud Console：**
1. 访问「凭据」页面
2. 编辑您的 OAuth 客户端
3. 在「已授权的重定向 URI」中添加生产环境地址：
   ```
   https://yourdomain.com/api/auth/oauth/google/callback
   ```

**GitHub Developer Settings：**
1. 编辑您的 OAuth App
2. 更新「Authorization callback URL」为生产环境地址

### Turnstile 域名配置

在 Cloudflare Turnstile 控制台中，确保添加了您的生产域名：
- `yourdomain.com`
- `www.yourdomain.com`（如果使用）

---

## 常见问题

### Q: OAuth 登录跳转后显示错误「redirect_uri_mismatch」

**A:** 回调地址不匹配。请检查：
1. `.env` 中的 `GOOGLE_REDIRECT_URI` 或 `GITHUB_REDIRECT_URI`
2. OAuth 提供商后台配置的回调地址
3. 两者必须完全一致（包括 http/https、端口、路径）

### Q: Turnstile 验证一直失败

**A:** 请检查：
1. `TURNSTILE_SITE_KEY` 和 `TURNSTILE_SECRET_KEY` 是否正确
2. 当前域名是否已添加到 Turnstile 的域名列表
3. 本地开发时，确保添加了 `localhost`

### Q: 如何禁用第三方登录？

**A:** 在 `.env` 中留空相关配置即可：
```bash
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
```
系统会自动隐藏第三方登录按钮。

### Q: 如何禁用用户注册？

**A:** 在 `.env` 中设置：
```bash
ENABLE_REGISTRATION=false
```

### Q: OAuth 登录成功但无法跳转回前端

**A:** 请检查 `FRONTEND_URL` 配置是否正确，确保是前端页面的完整地址（包含协议）。

---

## 相关链接

- [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
- [GitHub Developer Settings](https://github.com/settings/developers)
- [Cloudflare Turnstile](https://dash.cloudflare.com/?to=/:account/turnstile)
