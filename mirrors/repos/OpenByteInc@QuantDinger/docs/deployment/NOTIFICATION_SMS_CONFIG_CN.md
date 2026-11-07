# 手机短信通知配置指南

> QuantDinger 支持通过 Twilio 发送 SMS 短信通知，确保您在任何情况下都能收到重要的交易信号。

---

## 📋 目录

- [前置要求](#前置要求)
- [Twilio 简介](#twilio-简介)
- [配置步骤](#配置步骤)
  - [第一步：注册 Twilio 账号](#第一步注册-twilio-账号)
  - [第二步：获取 API 凭证](#第二步获取-api-凭证)
  - [第三步：获取发送号码](#第三步获取发送号码)
  - [第四步：配置环境变量](#第四步配置环境变量)
  - [第五步：策略中启用短信通知](#第五步策略中启用短信通知)
- [费用说明](#费用说明)
- [常见问题](#常见问题)

---

## 前置要求

- 有效的手机号码用于接收短信
- 可用的信用卡/借记卡用于 Twilio 充值（试用账户有免费额度）
- QuantDinger 后端服务已部署并运行

---

## Twilio 简介

[Twilio](https://www.twilio.com) 是全球领先的云通信平台，提供可靠的 SMS 短信服务。

**为什么选择 Twilio？**
- ✅ 全球覆盖 180+ 国家和地区
- ✅ 高送达率和可靠性
- ✅ 按量计费，无月费
- ✅ 新用户有免费试用额度
- ✅ 完善的 API 文档和技术支持

---

## 配置步骤

### 第一步：注册 Twilio 账号

1. 访问 [Twilio 官网](https://www.twilio.com/try-twilio)
2. 点击 **Sign Up** 注册新账号
3. 填写邮箱、密码等基本信息
4. 验证您的邮箱和手机号码
5. 完成账号激活

> 💡 **提示**：新注册用户可获得 $15 美元的免费试用额度。

---

### 第二步：获取 API 凭证

注册完成后，进入 Twilio 控制台：

1. 登录 [Twilio Console](https://console.twilio.com)
2. 在 Dashboard 页面找到 **Account Info** 区域
3. 记录以下信息：
   - **Account SID**：格式为 `ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - **Auth Token**：点击显示后复制（妥善保管）

![Twilio Console](https://www.twilio.com/docs/static/img/console-account-info.png)

> ⚠️ **安全提示**：Auth Token 相当于 API 密码，请勿泄露。如泄露请立即在控制台重新生成。

---

### 第三步：获取发送号码

您需要一个 Twilio 电话号码作为短信发送方：

1. 在 Twilio Console 左侧菜单选择 **Phone Numbers** → **Manage** → **Buy a number**
2. 选择国家/地区，勾选 **SMS** 功能
3. 选择一个号码并购买（试用账户可免费获取一个号码）
4. 记录您的 Twilio 电话号码（格式：`+1xxxxxxxxxx`）

**号码选择建议：**
- 选择与接收方同一国家的号码可降低费用
- 如需发送到中国大陆，建议使用 Alphanumeric Sender ID 或购买支持中国的号码

---

### 第四步：配置环境变量

在 `.env` 文件中配置 Twilio 参数：

```bash
# =========================
# Phone / SMS 配置 (Twilio)
# =========================

# Twilio Account SID（必填）
# 格式：ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Twilio Auth Token（必填）
# 从 Twilio Console 获取
TWILIO_AUTH_TOKEN=your_auth_token_here

# Twilio 发送号码（必填）
# 格式：+国家代码+号码，如 +14155552671
TWILIO_FROM_NUMBER=+14155552671
```

配置完成后重启后端服务使配置生效。

---

### 第五步：策略中启用短信通知

在策略配置页面的「信号通知」设置中：

1. 勾选启用 **Phone** 通知渠道
2. 在 **手机号码** 字段填入接收短信的号码

**号码格式要求：**
- 必须包含国家代码
- 格式：`+国家代码号码`
- 示例：
  - 美国：`+14155552671`
  - 中国大陆：`+8613812345678`
  - 香港：`+85212345678`

> 💡 **提示**：支持填入多个号码（逗号分隔），实现多人通知。

---

## 费用说明

Twilio 采用按量计费模式，不同国家/地区的短信费用不同：

| 接收地区 | 大约费用（美元/条） |
|---------|-------------------|
| 美国 | $0.0079 |
| 加拿大 | $0.0075 |
| 英国 | $0.04 |
| 德国 | $0.07 |
| 日本 | $0.08 |
| 中国大陆 | $0.06 - $0.10 |
| 香港 | $0.05 |

> 💰 **提示**：实际费用请参考 [Twilio 定价页面](https://www.twilio.com/sms/pricing)，价格可能随时调整。

**试用账户限制：**
- $15 美元免费额度
- 只能发送到已验证的手机号码
- 短信会带有 "Sent from your Twilio trial account" 前缀

升级为正式账户后可解除这些限制。

---

## 常见问题

### Q: 试用账户可以发短信到任意号码吗？

不可以。试用账户只能发送到已验证的手机号码。您需要在 Twilio Console 的 **Verified Caller IDs** 中添加并验证接收号码。升级为正式账户后可发送到任意号码。

### Q: 发送失败，提示号码无效？

1. 确保号码格式正确（含国家代码，如 `+8613812345678`）
2. 去掉号码中的空格、横线等特殊字符
3. 确认接收号码可以接收国际短信

### Q: 中国大陆号码收不到短信？

1. 部分运营商可能拦截国际短信
2. 尝试使用 Alphanumeric Sender ID
3. 确认手机未开启国际短信拦截
4. 联系 Twilio 支持确认中国短信服务状态

### Q: 如何查看发送记录和状态？

登录 Twilio Console → **Monitor** → **Logs** → **Messaging** 可查看所有短信发送记录、状态和错误信息。

### Q: Auth Token 泄露了怎么办？

立即登录 Twilio Console → **Account** → **API Credentials** → 点击 **Regenerate Auth Token** 重新生成。

### Q: 有替代 Twilio 的方案吗？

QuantDinger 目前仅支持 Twilio 作为 SMS 提供商。如需其他服务商支持，可通过 Webhook 通道自行集成：
- 阿里云短信
- 腾讯云短信
- Nexmo (Vonage)
- AWS SNS

---

## 环境变量完整参考

```bash
# Twilio SMS Configuration
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  # Account SID
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx     # Auth Token
TWILIO_FROM_NUMBER=+14155552671                        # 发送号码
```

---

## 相关文档

- [Telegram 通知配置](./NOTIFICATION_TELEGRAM_CONFIG_CN.md)
- [邮箱 SMTP 通知配置](./NOTIFICATION_EMAIL_CONFIG_CN.md)
- [策略开发指南](../trading/STRATEGY_DEV_GUIDE_CN.md)
- [Twilio 官方文档](https://www.twilio.com/docs/sms)
