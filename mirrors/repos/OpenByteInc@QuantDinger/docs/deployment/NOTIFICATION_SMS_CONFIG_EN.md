# SMS Notification Configuration Guide

> QuantDinger supports SMS notifications via Twilio, ensuring you receive critical trading signals anywhere.

---

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [About Twilio](#about-twilio)
- [Configuration Steps](#configuration-steps)
  - [Step 1: Create a Twilio Account](#step-1-create-a-twilio-account)
  - [Step 2: Obtain API Credentials](#step-2-obtain-api-credentials)
  - [Step 3: Get a Phone Number](#step-3-get-a-phone-number)
  - [Step 4: Configure Environment Variables](#step-4-configure-environment-variables)
  - [Step 5: Enable SMS Notifications in Strategy](#step-5-enable-sms-notifications-in-strategy)
- [Pricing Information](#pricing-information)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

- A valid phone number to receive SMS messages
- A credit/debit card for Twilio billing (trial accounts include free credits)
- QuantDinger backend service deployed and running

---

## About Twilio

[Twilio](https://www.twilio.com) is a leading cloud communications platform providing reliable SMS services worldwide.

**Why Twilio?**
- ✅ Global coverage in 180+ countries
- ✅ High deliverability and reliability
- ✅ Pay-as-you-go pricing, no monthly fees
- ✅ Free trial credits for new users
- ✅ Comprehensive API documentation and support

---

## Configuration Steps

### Step 1: Create a Twilio Account

1. Visit [Twilio Sign Up](https://www.twilio.com/try-twilio)
2. Click **Sign Up** to create a new account
3. Fill in your email, password, and basic information
4. Verify your email and phone number
5. Complete account activation

> 💡 **Tip**: New users receive $15 USD in free trial credits.

---

### Step 2: Obtain API Credentials

After registration, access the Twilio Console:

1. Log in to [Twilio Console](https://console.twilio.com)
2. Locate the **Account Info** section on the Dashboard
3. Note the following information:
   - **Account SID**: Format `ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - **Auth Token**: Click to reveal and copy (keep this secure)

> ⚠️ **Security Notice**: The Auth Token is essentially your API password. Never share it publicly. If compromised, regenerate it immediately in the console.

---

### Step 3: Get a Phone Number

You need a Twilio phone number as the SMS sender:

1. In Twilio Console, navigate to **Phone Numbers** → **Manage** → **Buy a number**
2. Select a country and check the **SMS** capability
3. Choose and purchase a number (trial accounts get one free number)
4. Note your Twilio phone number (format: `+1xxxxxxxxxx`)

**Number Selection Tips:**
- Choose a number from the same country as recipients to reduce costs
- For international recipients, consider the destination country's regulations
- Some countries require sender ID registration

---

### Step 4: Configure Environment Variables

Add Twilio parameters to your `.env` file:

```bash
# =========================
# Phone / SMS Configuration (Twilio)
# =========================

# Twilio Account SID (required)
# Format: ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Twilio Auth Token (required)
# Obtained from Twilio Console
TWILIO_AUTH_TOKEN=your_auth_token_here

# Twilio Sender Number (required)
# Format: +CountryCodeNumber, e.g., +14155552671
TWILIO_FROM_NUMBER=+14155552671
```

Restart the backend service after configuration to apply changes.

---

### Step 5: Enable SMS Notifications in Strategy

In the strategy configuration page under "Signal Notifications":

1. Enable the **Phone** notification channel
2. Enter the recipient phone number in the designated field

**Number Format Requirements:**
- Must include country code
- Format: `+CountryCodeNumber`
- Examples:
  - United States: `+14155552671`
  - United Kingdom: `+447911123456`
  - Germany: `+4915112345678`
  - Australia: `+61412345678`

> 💡 **Tip**: You can enter multiple numbers (comma-separated) for multi-recipient notifications.

---

## Pricing Information

Twilio uses pay-as-you-go pricing. SMS costs vary by destination:

| Destination | Approx. Cost (USD/message) |
|-------------|---------------------------|
| United States | $0.0079 |
| Canada | $0.0075 |
| United Kingdom | $0.04 |
| Germany | $0.07 |
| Australia | $0.05 |
| Japan | $0.08 |
| India | $0.04 |

> 💰 **Note**: For current pricing, visit [Twilio SMS Pricing](https://www.twilio.com/sms/pricing). Prices may change.

**Trial Account Limitations:**
- $15 USD free credits
- Can only send to verified phone numbers
- Messages include "Sent from your Twilio trial account" prefix

Upgrade to a paid account to remove these limitations.

---

## Troubleshooting

### Q: Can trial accounts send to any number?

No. Trial accounts can only send to verified phone numbers. Add and verify recipient numbers in Twilio Console under **Verified Caller IDs**. Upgrade to a paid account for unrestricted sending.

### Q: Send failed with invalid number error?

1. Ensure correct format with country code (e.g., `+14155552671`)
2. Remove spaces, dashes, or special characters from the number
3. Verify the recipient can receive international SMS

### Q: Messages not delivered to certain countries?

1. Some carriers may block international SMS
2. Check country-specific regulations (some require sender ID registration)
3. Verify the destination country is supported by Twilio
4. Contact Twilio support for country-specific issues

### Q: How to check delivery status?

Log in to Twilio Console → **Monitor** → **Logs** → **Messaging** to view all SMS records, delivery status, and error details.

### Q: Auth Token was compromised?

Immediately log in to Twilio Console → **Account** → **API Credentials** → Click **Regenerate Auth Token**.

### Q: Are there alternatives to Twilio?

QuantDinger currently only supports Twilio as the SMS provider. For other services, use the Webhook channel to integrate:
- Nexmo (Vonage)
- AWS SNS
- MessageBird
- Plivo

---

## Complete Environment Variable Reference

```bash
# Twilio SMS Configuration
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  # Account SID
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx     # Auth Token
TWILIO_FROM_NUMBER=+14155552671                        # Sender number
```

---

## Related Documentation

- [Telegram Notification Configuration](./NOTIFICATION_TELEGRAM_CONFIG_EN.md)
- [Email SMTP Notification Configuration](./NOTIFICATION_EMAIL_CONFIG_EN.md)
- [Strategy Development Guide](../trading/STRATEGY_DEV_GUIDE.md)
- [Twilio Official Documentation](https://www.twilio.com/docs/sms)
