---
applyTo: "**"
---
# Shimmy Vision Deployment Guide

## 🔐 CRITICAL: Access & Credentials (READ FIRST)

### Required Environment Variables
All credentials are stored in `.env` file (gitignored). Source with: `source .env`

**Keygen API:**
- `KEYGEN_ACCOUNT_ID=6270bf9c-23ad-4483-9296-3a6d9178514a`
- `KEYGEN_ADMIN_TOKEN=admin-8087987cc615a82c0e67583b2163860df66cbcb5770b73026857c45d2f47d6b9v3`
- `KEYGEN_PRODUCT_TOKEN=prod-e1c02ef59daf4772577df65970f7c07a3058c7037648eba932c48f97a5488ab7v3`

**Stripe API:**
- `STRIPE_KEY=sk_test_51RwqRv1g5xy1QMw5LPiGeHt0qcVIkpsqi9fBbxgB4vgIzKBwyTgSfv1WmuaesbTSig0hMTaWft2o7Y4NZ5gxLINw00d5HNnuze`
- `STRIPE_PUBLISHABLE_KEY_TEST=pk_test_51RwqRv1g5xy1QMw5drOBCVy7G8isU0C07QL4wNYHzy9MTLTBiGDhrFVHmO03dbuPiq3PXDrK9aVMGKIMTne48AQV00n9v9cCIw`
- `STRIPE_PUBLISHABLE_KEY_LIVE=pk_live_51RwqRv1g5xy1QMw5P01z0dVCQWSnSqc2VQEfmscQyrfy2LAe1Un2gqE3b3kmxxxFlP8XyosxJVu2K1p81ShmgyDw009RQ8xU6Q`

**Cloudflare Workers:**
- `CLOUDFLARE_WORKERS_TOKEN` (set in Windows environment)
- Use: `export CLOUDFLARE_API_TOKEN=$CLOUDFLARE_WORKERS_TOKEN`

**GitHub API:**
- `GITHUB_TOKEN` (set in Windows environment)

### API Testing Commands
**Keygen:**
```bash
source .env
curl -H "Authorization: Bearer $KEYGEN_ADMIN_TOKEN" \
  "https://api.keygen.sh/v1/accounts/$KEYGEN_ACCOUNT_ID/licenses"
```

**Stripe:**
```bash
source .env
curl -u "$STRIPE_KEY:" https://api.stripe.com/v1/customers
```

**Wrangler:**
```bash
export CLOUDFLARE_API_TOKEN=$CLOUDFLARE_WORKERS_TOKEN
wrangler whoami
```

**GitHub:**
```bash
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user
```

## Complete Deployment Overview

This guide covers deploying all components of the Shimmy Vision ecosystem to production.

## Prerequisites

### **Required Accounts**
- **GitHub**: Source control, Pages hosting, Actions CI/CD
- **Cloudflare**: Workers, DNS, CDN  
- **Stripe**: Payment processing (test + live)
- **Keygen**: License management and validation

### **Required Tools**
- **Wrangler CLI**: Cloudflare Workers deployment
- **Git**: Source control operations
- **Node.js**: Frontend build process
- **Rust**: Backend compilation

### **Required Secrets/Keys**
- Stripe API keys (test + live)
- Keygen account credentials  
- Cloudflare API tokens
- GitHub personal access tokens

## 1. Frontend Deployment (React → GitHub Pages)

### **Repository Setup**
```bash
# Repository: shimmy-vision (public)
cd /c/Users/micha/repos/shimmy-vision

# Verify package.json homepage
cat package.json | grep homepage
# Should show: "https://michael-a-kuykendall.github.io/shimmy-vision"
```

### **Environment Configuration**
```bash
# Set Stripe publishable key for live environment
cat > .env.local << EOF
VITE_STRIPE_PUBLISHABLE_KEY=pk_live_51RwqRv1g5xy1QMw5P01z0dVCQWSnSqc2VQEfmscQyrfy2LAe1Un2gqE3b3kmxxxFlP8XyosxJVu2K1p81Shmg
yDw009RQ8xU6Q
EOF
```

### **Build & Deploy**
```bash
# Build for production
npm run build

# Deploy to GitHub Pages
npm run deploy
# OR manually:
# npx gh-pages -d dist
```

### **GitHub Pages Configuration**
1. Go to repository Settings → Pages
2. Source: "Deploy from a branch"  
3. Branch: `gh-pages` / `/ (root)`
4. Custom domain: (optional) `vision.shimmy.dev`

### **Verification**
- **URL**: https://michael-a-kuykendall.github.io/shimmy-vision
- **Test**: Click through pricing tiers
- **Expected**: Stripe checkout loads correctly

## 2. Cloudflare Worker Deployment (Payment Processing)

### **Authentication Setup**
```bash
# Set Cloudflare API token (use CLOUDFLARE_WORKERS_TOKEN for Workers)
export CLOUDFLARE_API_TOKEN=$CLOUDFLARE_WORKERS_TOKEN

# Verify authentication
wrangler auth status
```

### **Environment Configuration**
```bash
cd /c/Users/micha/repos/shimmy-workspace/cloudflare-worker

# Deploy to test environment first
wrangler publish --env test

# Deploy to production environment  
wrangler publish --env production
```

### **Required Secrets (Test Environment)**
```bash
# Keygen Configuration
wrangler secret put KEYGEN_ACCOUNT_ID --env test
# Enter: 6270bf9c-23ad-4483-9296-3a6d9178514a

wrangler secret put KEYGEN_PRODUCT_TOKEN --env test  
# Enter: prod-e1c02ef59daf4772577df65970f7c07a3058c7037648eba932c48f97a5488ab7v3

# Stripe Configuration (TEST)
wrangler secret put STRIPE_SECRET_KEY --env test
# Enter: sk_test_... (from Stripe dashboard)

wrangler secret put STRIPE_WEBHOOK_SECRET --env test  
# Enter: whsec_test_... (from Stripe webhook configuration)

# Stripe Price IDs (TEST)
wrangler secret put STRIPE_PRICE_DEVELOPER --env test
wrangler secret put STRIPE_PRICE_PROFESSIONAL --env test
wrangler secret put STRIPE_PRICE_STARTUP --env test  
wrangler secret put STRIPE_PRICE_ENTERPRISE --env test
wrangler secret put STRIPE_PRICE_LIFETIME --env test
```

### **Required Secrets (Production Environment)**
```bash
# Same as test, but use production values:
wrangler secret put KEYGEN_ACCOUNT_ID --env production
wrangler secret put KEYGEN_PRODUCT_TOKEN --env production

# Stripe LIVE keys
wrangler secret put STRIPE_SECRET_KEY --env production
# Enter: sk_live_... (from Stripe dashboard)

wrangler secret put STRIPE_WEBHOOK_SECRET --env production  
# Enter: whsec_live_... (from Stripe live webhook)

# Stripe LIVE Price IDs
wrangler secret put STRIPE_PRICE_DEVELOPER --env production
# ... (repeat for all tiers)
```

### **Deployment Commands**
```bash
# Test deployment
wrangler publish --env test
# Deployed to: shimmy-license-webhook-test.michaelallenkuykendall.workers.dev

# Production deployment
wrangler publish --env production  
# Deployed to: shimmy-license-webhook.michaelallenkuykendall.workers.dev
```

### **Verification**
```bash
# Test health endpoint
curl https://shimmy-license-webhook-test.michaelallenkuykendall.workers.dev/health

# Expected response:
# {"status": "ok", "timestamp": "2025-01-08T..."}
```

## 3. Stripe Configuration

### **Test Environment Setup**
1. **Go to Stripe Dashboard** → Switch to "Test mode"
2. **Create Products** for each tier:
   - Developer: $12/month subscription
   - Professional: $29/month subscription  
   - Startup: $79/month subscription
   - Enterprise: $299/month subscription
   - Lifetime: $499 one-time payment

3. **Configure Product Metadata**:
   ```
   keygen_policy_id: [policy-id-from-keygen]
   tier: developer|professional|startup|enterprise|lifetime
   ```

4. **Create Webhook**:
   - URL: `https://shimmy-license-webhook-test.workers.dev/stripe-webhook`
   - Events: `checkout.session.completed`
   - Copy signing secret for STRIPE_WEBHOOK_SECRET

### **Production Environment Setup**
1. **Switch to Live mode** in Stripe Dashboard
2. **Create Live Products** (same as test, but live prices)
3. **Configure Live Webhook**:
   - URL: `https://shimmy-license-webhook.workers.dev/stripe-webhook`
   - Events: `checkout.session.completed`
4. **Update Payment Links** with live product IDs

## 4. Keygen Configuration

### **Account Setup**
- **Account ID**: `6270bf9c-23ad-4483-9296-3a6d9178514a` (already configured)
- **Product Token**: Already configured in .env

### **Policy Configuration**
Create policies for each tier with appropriate limits:

```bash
# Developer Policy
{
  "maxUses": 2500,
  "duration": 2592000000,  # 30 days in milliseconds
  "scheme": "LICENSED"
}

# Professional Policy  
{
  "maxUses": 10000,
  "duration": 2592000000,
  "scheme": "LICENSED"
}

# Startup Policy
{
  "maxUses": 50000, 
  "duration": 2592000000,
  "scheme": "LICENSED"
}

# Enterprise Policy
{
  "maxUses": null,  # unlimited
  "duration": 2592000000,
  "scheme": "LICENSED"
}

# Lifetime Policy
{
  "maxUses": null,  # unlimited
  "duration": null, # never expires  
  "scheme": "LICENSED"
}
```

### **Entitlements Configuration**
Each policy should include:
- `VISION_ANALYSIS`: Core vision processing
- `API_ACCESS`: HTTP API access
- `CLI_ACCESS`: Command-line interface access

## 5. Backend Deployment (Rust Application)

### **Local Build**
```bash
cd /c/Users/micha/repos/shimmy-workspace

# Build with vision features
cargo build --release --features llama,vision

# Build with GPU support  
cargo build --release --features llama,vision,llama-cuda
```

### **Distribution Methods**

#### **GitHub Releases**
```bash
# Create release binaries
cargo build --release --features llama,vision --target x86_64-pc-windows-msvc
cargo build --release --features llama,vision --target x86_64-unknown-linux-gnu
cargo build --release --features llama,vision --target x86_64-apple-darwin

# Upload to GitHub Releases with version tags
```

#### **Docker Deployment**  
```bash
# Build Docker image
docker build -f deploy/Dockerfile -t shimmy:latest .

# Push to registry
docker tag shimmy:latest ghcr.io/michael-a-kuykendall/shimmy:latest
docker push ghcr.io/michael-a-kuykendall/shimmy:latest
```

#### **Cloud Deployment (Fly.io)**
```bash
# Deploy to Fly.io
fly deploy --config deploy/fly.toml

# Configure environment variables
fly secrets set SHIMMY_LICENSE_KEY=your-license-key
```

## 6. DNS & SSL Configuration

### **Cloudflare DNS Setup**
```
Type    Name                Value                                           TTL
CNAME   vision              michael-a-kuykendall.github.io                  Auto
CNAME   api                 shimmy-license-webhook.workers.dev             Auto  
CNAME   api-test           shimmy-license-webhook-test.workers.dev         Auto
```

### **SSL Configuration**
- **GitHub Pages**: Automatic SSL with custom domain
- **Cloudflare Workers**: SSL included by default
- **Custom Domain**: Configure through Cloudflare SSL settings

## 7. Monitoring & Alerting

### **Cloudflare Workers Monitoring**
```bash
# Real-time logs
wrangler tail --env production

# Metrics dashboard
# Visit Cloudflare Dashboard → Workers & Pages → shimmy-license-webhook
```

### **Stripe Monitoring**
- **Dashboard**: Monitor payments, failed charges, disputes
- **Webhooks**: Check delivery status and retry logic
- **Events**: Monitor checkout.session.completed events

### **Keygen Monitoring**  
- **Dashboard**: License creation, validation requests
- **Usage**: Track monthly usage per license
- **API**: Monitor validation response times

### **Application Monitoring**
```bash
# Enable detailed logging
export RUST_LOG=shimmy=debug,shimmy_vision=trace

# Monitor license validation
export SHIMMY_VISION_TRACE=1
```

## 8. Testing & Validation

### **End-to-End Testing**
```bash
# 1. Test checkout flow
curl "https://shimmy-license-webhook-test.workers.dev/buy?tier=developer&email=test@example.com"

# 2. Complete Stripe payment with test card: 4242424242424242

# 3. Verify license creation
curl -H "Authorization: Bearer ${KEYGEN_ADMIN_TOKEN}" \
  "https://api.keygen.sh/v1/accounts/${KEYGEN_ACCOUNT_ID}/licenses"

# 4. Test license validation
export SHIMMY_LICENSE_KEY=[new-license-key]
cargo run --features llama,vision -- generate --prompt "test" --image test.jpg
```

### **Production Readiness Checklist**
- [ ] Frontend builds and deploys successfully
- [ ] All Worker secrets configured correctly  
- [ ] Stripe webhooks delivering to live Worker
- [ ] Keygen policies configured with correct limits
- [ ] License validation working in shimmy application
- [ ] DNS records pointing to production endpoints
- [ ] Monitoring dashboards configured
- [ ] Backup procedures documented

## 9. Emergency Procedures

### **Rollback Process**
```bash
# 1. Revert frontend to previous version
git revert HEAD
npm run deploy

# 2. Rollback Worker deployment
wrangler publish --env production [previous-version]

# 3. Disable live Stripe webhooks (if needed)
# Go to Stripe Dashboard → Webhooks → Disable endpoint
```

### **Issue Resolution**
- **Payment Failures**: Check Stripe webhook delivery logs
- **License Issues**: Verify Keygen API connectivity  
- **Worker Errors**: Use `wrangler tail` for real-time debugging
- **Frontend Issues**: Check GitHub Pages build logs

This deployment guide ensures a complete, production-ready deployment of the entire Shimmy Vision ecosystem.---
applyTo: "**"
---
