---
applyTo: "**"
---
# Shimmy Vision Architecture Overview

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

## System Architecture

Shimmy Vision is a complete, production-ready vision AI product ecosystem consisting of:

### 1. **Core Components**

#### **Main Backend (shimmy-workspace)**
- **Location**: `c:\Users\micha\repos\shimmy-workspace`
- **Type**: Rust application with vision feature flag
- **Purpose**: Local inference server with paid vision capabilities
- **License**: Open Source (MIT/Apache) + Proprietary vision module

#### **Frontend (shimmy-vision)** 
- **Location**: `c:\Users\micha\repos\shimmy-vision`
- **Type**: React + TypeScript + Vite application
- **Deployment**: GitHub Pages at `https://michael-a-kuykendall.github.io/shimmy-vision`
- **Purpose**: Marketing site + Stripe checkout integration
- **Repository**: Public GitHub repository

#### **Private Vision Module (shimmy-vision-private)**
- **Location**: `c:\Users\micha\repos\shimmy-vision-private` 
- **Type**: Rust crate with proprietary vision processing
- **Purpose**: Core vision functionality behind licensing
- **Repository**: Private GitHub repository
- **License**: Proprietary

#### **Payment Processing (Cloudflare Worker)**
- **Location**: `c:\Users\micha\repos\shimmy-workspace\cloudflare-worker`
- **Type**: Cloudflare Workers JavaScript
- **Purpose**: Stripe webhook → Keygen license generation
- **Deployment**: 
  - Test: `https://shimmy-license-webhook-test.michaelallenkuykendall.workers.dev`
  - Live: `https://shimmy-license-webhook.michaelallenkuykendall.workers.dev`

### 2. **Technology Stack**

#### **Backend Stack**
- **Language**: Rust 2021 edition
- **Features**: `llama`, `vision`, `llama-cuda` (optional)
- **Vision Model**: MiniCPM-V (hard-locked)
- **HTTP Framework**: Axum
- **Authentication**: Keygen license validation
- **Encryption**: Ed25519 signature verification

#### **Frontend Stack**
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **UI Library**: Radix UI + shadcn/ui
- **Styling**: Tailwind CSS
- **Payment**: Stripe.js embedded checkout
- **Deployment**: GitHub Pages with GitHub Actions

#### **Infrastructure Stack**
- **Payment**: Stripe (test + live modes)
- **Licensing**: Keygen.sh with Ed25519 verification
- **CDN/Functions**: Cloudflare Workers
- **DNS**: Cloudflare
- **Deployment**: GitHub Pages + Actions

### 3. **Data Flow**

#### **Purchase Flow**
```
User visits shimmy-vision site → 
Clicks "Buy Now" → 
Stripe Embedded Checkout → 
Payment completed → 
Stripe webhook → Cloudflare Worker → 
Keygen API creates license → 
User receives license key
```

#### **Usage Flow**
```
User downloads shimmy → 
Sets SHIMMY_LICENSE_KEY env var → 
Runs shimmy with --features vision → 
License validated against Keygen → 
Vision processing enabled → 
HTTP/CLI API available
```

### 4. **Security Architecture**

#### **License Verification**
- **Hard-coded Account ID**: `6270bf9c-23ad-4483-9296-3a6d9178514a`
- **Ed25519 Public Key**: `42f313585a72a41513208800f730944f1a3b74a8acfff539f96ce244d029fa5d`
- **Signature Verification**: All API responses cryptographically verified
- **Usage Metering**: Monthly caps enforced per license tier

#### **Payment Security**
- **Webhook Verification**: Stripe signature validation
- **Environment Isolation**: Separate test/live configurations
- **Secret Management**: Cloudflare Workers secrets, never in code

#### **Vision Model Security**
- **License Check**: Every vision request validates license
- **No Bypass**: No dev mode in production builds
- **Private Code**: Core vision logic in separate private repository

### 5. **Environment Configuration**

#### **Test Environment**
- **Stripe**: Test mode with test cards
- **Worker**: `shimmy-license-webhook-test.workers.dev`
- **Keygen**: Test licenses for development
- **Purpose**: Development and integration testing

#### **Production Environment**  
- **Stripe**: Live mode with real payments
- **Worker**: `shimmy-license-webhook.workers.dev`
- **Keygen**: Production licenses for customers
- **Purpose**: Live customer transactions

### 6. **Monitoring & Observability**

#### **Payment Monitoring**
- **Cloudflare Workers**: Real-time logs via `wrangler tail`
- **Stripe Dashboard**: Payment status, webhooks, customers
- **Keygen Dashboard**: License creation, validation, usage

#### **Application Monitoring**
- **Rust Logging**: Configurable via `RUST_LOG` environment
- **HTTP Metrics**: Request/response times, error rates
- **Usage Tracking**: License validation frequency, feature usage

### 7. **Deployment Architecture**

#### **Frontend Deployment**
```
Local development → 
GitHub push to main → 
GitHub Actions builds → 
Deploys to GitHub Pages → 
Available at michael-a-kuykendall.github.io/shimmy-vision
```

#### **Worker Deployment**
```
Local development →
wrangler publish --env test/live →
Deployed to Cloudflare Workers →
Webhook endpoints available
```

#### **Backend Distribution**
```
Local builds →
GitHub Releases →
Cargo publish (open features only) →
Private vision module linked at build time
```

### 8. **Integration Points**

#### **External Services**
- **Stripe**: Payment processing, subscription management
- **Keygen**: License generation, validation, usage tracking
- **Cloudflare**: DNS, CDN, serverless functions
- **GitHub**: Source control, CI/CD, static hosting

#### **API Endpoints**
- **Vision API**: `POST /api/vision` (license-gated)
- **Health**: `GET /health`
- **License Check**: Internal validation
- **Webhook**: `POST /stripe-webhook`
- **Checkout**: `GET /buy?tier=X`

### 9. **Development Workflow**

#### **Feature Development**
1. Work on open features in main repository
2. Work on vision features in private repository  
3. Link private crate during builds
4. Test with development licenses
5. Deploy through standard CI/CD

#### **Release Process**
1. Update version in all components
2. Test payment flow end-to-end
3. Deploy worker updates
4. Deploy frontend updates
5. Create GitHub release with binaries

This architecture provides a complete separation of concerns while maintaining integration, security, and scalability for a production SaaS vision product.---
applyTo: "**"
---
