---
applyTo: "**"
---
# Live Stripe Setup Instructions

## Overview
Instructions for configuring Stripe for live/production mode.

## Dashboard Access
- Login to Stripe dashboard
- Toggle to "Live mode" (top-left switch)

## Product Setup
Ensure live products exist with correct metadata:
- Shimmy Vision Developer
- Professional
- Startup
- Enterprise
- Lifetime

### Required Metadata
- `keygen_policy_id`: Corresponding Keygen policy ID
- `tier`: developer/professional/startup/enterprise/lifetime

## Price Configuration
- Lifetime tier: Enable Alipay and WeChat Pay
- All prices: Set to active and correct amounts

## Webhook Setup
- Create webhook endpoint: `https://shimmy-license-webhook.michaelallenkuykendall.workers.dev/stripe-webhook`
- Events: `checkout.session.completed`
- Copy signing secret for worker secret

## API Keys
- Publishable key: pk_live_...
- Secret key: sk_live_...

## Verification
- Test products visible in live dashboard
- Webhook configured and receiving events
- Payment methods enabled for international customers

## Previous Usage
- Test products created and functional
- Live products may need creation or metadata updates
- Webhook needs live endpoint configuration