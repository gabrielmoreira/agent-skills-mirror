# Email SMTP Notification Configuration Guide

> QuantDinger supports strategy signal notifications via email, ideal for users who need detailed notification records.

---

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Supported Email Providers](#supported-email-providers)
- [Configuration Steps](#configuration-steps)
  - [Step 1: Obtain SMTP Service Information](#step-1-obtain-smtp-service-information)
  - [Step 2: Configure Environment Variables](#step-2-configure-environment-variables)
  - [Step 3: Enable Email Notifications in Strategy](#step-3-enable-email-notifications-in-strategy)
- [Provider Configuration Examples](#provider-configuration-examples)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

- An email account with SMTP sending capability
- SMTP service enabled (some providers require manual activation)
- App password or authorization code (not your login password)
- QuantDinger backend service deployed and running

---

## Supported Email Providers

QuantDinger supports any standard SMTP protocol email provider, including:

| Provider | SMTP Server | Port | Encryption |
|----------|-------------|------|------------|
| Gmail | smtp.gmail.com | 587 (TLS) / 465 (SSL) | TLS / SSL |
| Outlook/Hotmail | smtp.office365.com | 587 | TLS |
| Yahoo Mail | smtp.mail.yahoo.com | 587 | TLS |
| SendGrid | smtp.sendgrid.net | 587 | TLS |
| Mailgun | smtp.mailgun.org | 587 | TLS |
| Amazon SES | email-smtp.{region}.amazonaws.com | 587 | TLS |
| Zoho Mail | smtp.zoho.com | 587 | TLS |
| ProtonMail Bridge | 127.0.0.1 | 1025 | STARTTLS |

---

## Configuration Steps

### Step 1: Obtain SMTP Service Information

**For Gmail:**

1. Visit [Google Account Security Settings](https://myaccount.google.com/security)
2. Enable 2-Step Verification
3. Generate an "App Password"
4. Select "Mail" and your device type to get a 16-character password

**For Outlook/Hotmail:**

1. Use your regular email and password
2. Ensure "SMTP AUTH" is enabled in account settings
3. May require app password if 2FA is enabled

> ⚠️ **Important**: App passwords are different from your login password. Keep them secure.

---

### Step 2: Configure Environment Variables

Add SMTP parameters to your `.env` file:

```bash
# =========================
# Email / SMTP Configuration
# =========================

# SMTP server address (required)
SMTP_HOST=smtp.gmail.com

# SMTP port (required)
# Common ports: 587 (TLS) / 465 (SSL) / 25 (unencrypted, not recommended)
SMTP_PORT=587

# SMTP username (required, usually your email address)
SMTP_USER=your_email@gmail.com

# SMTP password or app password (required)
SMTP_PASSWORD=your_app_password

# Sender address (optional, defaults to SMTP_USER)
SMTP_FROM=your_email@gmail.com

# Enable STARTTLS (typically true for port 587)
SMTP_USE_TLS=true

# Enable implicit SSL (typically true for port 465)
SMTP_USE_SSL=false
```

Restart the backend service after configuration to apply changes.

---

### Step 3: Enable Email Notifications in Strategy

In the strategy configuration page under "Signal Notifications":

1. Enable the **Email** notification channel
2. Enter the recipient email address in the designated field

> 💡 **Tip**: You can enter multiple email addresses (comma-separated) for multi-recipient notifications.

---

## Provider Configuration Examples

### Gmail

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password  # 16-character app password
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

### Yahoo Mail

```bash
SMTP_HOST=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USER=your_email@yahoo.com
SMTP_PASSWORD=your_app_password
SMTP_FROM=your_email@yahoo.com
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```

### SendGrid

```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=SG.xxxxxxxxxxxxxxxxxxxxx  # Your API Key
SMTP_FROM=verified_sender@yourdomain.com
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```

### Mailgun

```bash
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USER=postmaster@your-domain.mailgun.org
SMTP_PASSWORD=your_mailgun_smtp_password
SMTP_FROM=noreply@yourdomain.com
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```

### Amazon SES

```bash
SMTP_HOST=email-smtp.us-east-1.amazonaws.com  # Replace with your region
SMTP_PORT=587
SMTP_USER=AKIAIOSFODNN7EXAMPLE  # SMTP credential username
SMTP_PASSWORD=your_smtp_password  # SMTP credential password
SMTP_FROM=verified@yourdomain.com
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```

### Zoho Mail

```bash
SMTP_HOST=smtp.zoho.com
SMTP_PORT=587
SMTP_USER=your_email@zoho.com
SMTP_PASSWORD=your_password
SMTP_FROM=your_email@zoho.com
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```

---

## Troubleshooting

### Q: Authentication error?

1. Verify username and password (app password) are correct
2. Confirm SMTP service is enabled in your email settings
3. Some providers require app passwords instead of login passwords
4. Check if "Less secure app access" needs to be enabled (legacy option)

### Q: Connection timeout?

1. Verify SMTP server address and port are correct
2. Check if server firewall allows the port
3. If using a proxy, ensure proxy configuration is correct
4. Some networks block SMTP ports; try port 587 or 465

### Q: How to choose between TLS and SSL?

| Port | Encryption | Configuration |
|------|------------|---------------|
| 587 | STARTTLS | `SMTP_USE_TLS=true`, `SMTP_USE_SSL=false` |
| 465 | Implicit SSL | `SMTP_USE_TLS=false`, `SMTP_USE_SSL=true` |
| 25 | None | `SMTP_USE_TLS=false`, `SMTP_USE_SSL=false` (not recommended) |

### Q: Emails marked as spam?

1. Use a `SMTP_FROM` address matching your `SMTP_USER`
2. Consider professional email services (SendGrid, Mailgun, Amazon SES)
3. Configure SPF, DKIM, DMARC records for your domain (business email)
4. Avoid spam trigger words in subject/content

### Q: Does it support HTML emails?

Yes, QuantDinger automatically sends formatted HTML emails with a plain text fallback for maximum compatibility.

### Q: Rate limits?

Most providers have sending limits:
- Gmail: ~500/day (personal), 2000/day (Workspace)
- Outlook: ~300/day
- SendGrid: Based on your plan

For high-volume notifications, consider dedicated email services.

---

## Related Documentation

- [Telegram Notification Configuration](./NOTIFICATION_TELEGRAM_CONFIG_EN.md)
- [SMS Notification Configuration](./NOTIFICATION_SMS_CONFIG_EN.md)
- [Strategy Development Guide](../trading/STRATEGY_DEV_GUIDE.md)
