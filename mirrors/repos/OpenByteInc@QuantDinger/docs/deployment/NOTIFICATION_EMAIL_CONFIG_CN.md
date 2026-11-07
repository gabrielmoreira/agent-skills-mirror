# 邮箱 SMTP 通知配置指南

> QuantDinger 支持通过邮件推送策略信号通知，适合需要详细通知记录的用户。

---

## 📋 目录

- [前置要求](#前置要求)
- [支持的邮件服务商](#支持的邮件服务商)
- [配置步骤](#配置步骤)
  - [第一步：获取 SMTP 服务信息](#第一步获取-smtp-服务信息)
  - [第二步：配置环境变量](#第二步配置环境变量)
  - [第三步：策略中启用邮件通知](#第三步策略中启用邮件通知)
- [常见邮件服务商配置示例](#常见邮件服务商配置示例)
- [常见问题](#常见问题)

---

## 前置要求

- 拥有一个支持 SMTP 发送的邮箱账号
- 邮箱已开启 SMTP 服务（部分服务商需手动开启）
- 获取邮箱的授权码或应用专用密码（非登录密码）
- QuantDinger 后端服务已部署并运行

---

## 支持的邮件服务商

QuantDinger 支持任何标准 SMTP 协议的邮件服务商，包括但不限于：

| 服务商 | SMTP 服务器 | 端口 | 加密方式 |
|--------|------------|------|----------|
| Gmail | smtp.gmail.com | 587 (TLS) / 465 (SSL) | TLS / SSL |
| Outlook/Hotmail | smtp.office365.com | 587 | TLS |
| QQ 邮箱 | smtp.qq.com | 587 (TLS) / 465 (SSL) | TLS / SSL |
| 163 邮箱 | smtp.163.com | 465 (SSL) / 25 | SSL |
| 阿里企业邮箱 | smtp.qiye.aliyun.com | 465 | SSL |
| 腾讯企业邮箱 | smtp.exmail.qq.com | 465 | SSL |
| SendGrid | smtp.sendgrid.net | 587 | TLS |
| Mailgun | smtp.mailgun.org | 587 | TLS |
| Amazon SES | email-smtp.{region}.amazonaws.com | 587 | TLS |

---

## 配置步骤

### 第一步：获取 SMTP 服务信息

以 **QQ 邮箱** 为例：

1. 登录 QQ 邮箱网页版 → 设置 → 账户
2. 找到「POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务」
3. 开启「SMTP 服务」
4. 按提示生成**授权码**（16位字母）

> ⚠️ **重要**：授权码不是 QQ 密码，请妥善保管。

以 **Gmail** 为例：

1. 访问 [Google 账号安全设置](https://myaccount.google.com/security)
2. 开启两步验证
3. 生成「应用专用密码」（App Password）
4. 选择「邮件」和设备类型，获取 16 位密码

---

### 第二步：配置环境变量

在 `.env` 文件中配置 SMTP 参数：

```bash
# =========================
# Email / SMTP 配置
# =========================

# SMTP 服务器地址（必填）
SMTP_HOST=smtp.qq.com

# SMTP 端口（必填）
# 常用端口：587 (TLS) / 465 (SSL) / 25 (不加密，不推荐)
SMTP_PORT=465

# SMTP 登录用户名（必填，通常是邮箱地址）
SMTP_USER=your_email@qq.com

# SMTP 密码或授权码（必填）
SMTP_PASSWORD=your_authorization_code

# 发件人地址（可选，默认使用 SMTP_USER）
SMTP_FROM=your_email@qq.com

# 是否使用 STARTTLS（端口 587 通常设为 true）
SMTP_USE_TLS=false

# 是否使用 SSL（端口 465 通常设为 true）
SMTP_USE_SSL=true
```

配置完成后重启后端服务使配置生效。

---

### 第三步：策略中启用邮件通知

在策略配置页面的「信号通知」设置中：

1. 勾选启用 **Email** 通知渠道
2. 在 **收件邮箱** 字段填入接收通知的邮箱地址

> 💡 **提示**：支持填入多个邮箱地址（逗号分隔），实现多人通知。

---

## 常见邮件服务商配置示例

### QQ 邮箱

```bash
SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_USER=123456789@qq.com
SMTP_PASSWORD=abcdefghijklmnop  # 16位授权码
SMTP_FROM=123456789@qq.com
SMTP_USE_TLS=false
SMTP_USE_SSL=true
```

### 163 邮箱

```bash
SMTP_HOST=smtp.163.com
SMTP_PORT=465
SMTP_USER=your_email@163.com
SMTP_PASSWORD=your_authorization_code  # 授权码
SMTP_FROM=your_email@163.com
SMTP_USE_TLS=false
SMTP_USE_SSL=true
```

### Gmail

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password  # 应用专用密码
SMTP_FROM=your_email@gmail.com
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```

### Outlook / Office 365

```bash
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USER=your_email@outlook.com
SMTP_PASSWORD=your_password
SMTP_FROM=your_email@outlook.com
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```

### SendGrid

```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=SG.xxxxxxxxxxxxxxxxxxxxx  # API Key
SMTP_FROM=verified_sender@yourdomain.com
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```

### Amazon SES

```bash
SMTP_HOST=email-smtp.us-east-1.amazonaws.com  # 替换为您的区域
SMTP_PORT=587
SMTP_USER=AKIAIOSFODNN7EXAMPLE  # SMTP 凭证用户名
SMTP_PASSWORD=your_smtp_password  # SMTP 凭证密码
SMTP_FROM=verified@yourdomain.com
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```

---

## 常见问题

### Q: 发送失败，提示认证错误？

1. 检查用户名和密码（授权码）是否正确
2. 确认已开启邮箱的 SMTP 服务
3. 部分邮箱需要使用授权码而非登录密码

### Q: 连接超时？

1. 检查 SMTP 服务器地址和端口是否正确
2. 确认服务器防火墙是否放行对应端口
3. 如使用代理，确认代理配置正确

### Q: TLS 和 SSL 如何选择？

| 端口 | 加密方式 | 配置 |
|------|---------|------|
| 587 | STARTTLS | `SMTP_USE_TLS=true`, `SMTP_USE_SSL=false` |
| 465 | 隐式 SSL | `SMTP_USE_TLS=false`, `SMTP_USE_SSL=true` |
| 25 | 无加密 | `SMTP_USE_TLS=false`, `SMTP_USE_SSL=false` （不推荐）|

### Q: 邮件被标记为垃圾邮件？

1. 使用与 `SMTP_USER` 一致的 `SMTP_FROM` 地址
2. 考虑使用专业邮件服务（如 SendGrid、Mailgun）
3. 配置域名 SPF、DKIM、DMARC 记录（企业邮箱）

### Q: 可以发送 HTML 格式邮件吗？

是的，QuantDinger 自动发送包含格式化信息的 HTML 邮件，同时附带纯文本备选内容以确保兼容性。

---

## 相关文档

- [Telegram 通知配置](./NOTIFICATION_TELEGRAM_CONFIG_CN.md)
- [手机短信通知配置](./NOTIFICATION_SMS_CONFIG_CN.md)
- [策略开发指南](../trading/STRATEGY_DEV_GUIDE_CN.md)
