---
applyTo: "**"
---
---
applyTo: "**"
---
# Shimmy Vision Complete Ecosystem Documentation

## � CRITICAL: Access & Credentials (READ FIRST)

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

## �📋 Overview

This documentation provides complete context for the Shimmy Vision product ecosystem - a locally-run vision AI product with paid licensing. This guide ensures any AI assistant can understand and work with the system without requiring extensive discovery.

## 🏗️ System Architecture

**Shimmy Vision** is a complete production SaaS product consisting of:

### **Core Repositories**
- **shimmy-workspace** (`c:\Users\micha\repos\shimmy-workspace`) - Main Rust application with vision features
- **shimmy-vision** (`c:\Users\micha\repos\shimmy-vision`) - React frontend for marketing + checkout  
- **shimmy-vision-private** (`c:\Users\micha\repos\shimmy-vision-private`) - Proprietary vision processing code

### **Production Infrastructure**
- **Frontend**: GitHub Pages at `michael-a-kuykendall.github.io/shimmy-vision`
- **Payment**: Cloudflare Workers handling Stripe webhooks → Keygen license generation
- **Backend**: Local Rust application with licensed vision features
- **Licensing**: Keygen.sh with Ed25519 cryptographic verification

## 📚 Documentation Structure

### **[Architecture Overview](shimmy-vision-architecture.md)**
Complete technical architecture including:
- Component relationships and data flow
- Technology stack (Rust, React, Cloudflare, Stripe, Keygen)
- Security architecture with Ed25519 verification
- Environment configuration (test vs production)
- Integration points and monitoring

### **[Business Model](shimmy-vision-business-model.md)**  
Complete product and business context:
- **5 Pricing Tiers**: Developer ($12/mo), Professional ($29/mo), Startup ($79/mo), Enterprise ($299/mo), Lifetime ($499)
- **Target Markets**: AI/ML developers, automation engineers, small teams, enterprises
- **Customer Journey**: Discovery → Evaluation → Purchase → Usage → Retention
- **Revenue Model**: Subscription + usage limits + lifetime options
- **Growth Strategy**: Developer adoption → team expansion → enterprise sales

### **[Deployment Guide](shimmy-vision-deployment-guide.md)**
Production deployment procedures:
- **Frontend Deployment**: React → GitHub Pages via GitHub Actions
- **Worker Deployment**: Cloudflare Workers with environment-specific secrets
- **Stripe Configuration**: Products, webhooks, test vs live modes  
- **Keygen Setup**: Policies, entitlements, usage limits
- **DNS/SSL**: Cloudflare configuration
- **Monitoring**: Real-time logs, metrics, alerting

### **[API Reference](shimmy-vision-api-reference.md)**
Complete API documentation:
- **CLI Interface**: Image processing with prompts and options
- **HTTP API**: `/api/vision` endpoint with streaming support
- **WebSocket API**: Real-time token streaming  
- **License API**: Validation, usage tracking, entitlements
- **Error Codes**: Authentication, processing, rate limiting
- **Integration Examples**: Python, Node.js, cURL
- **Configuration**: Environment variables, security settings

### **[Troubleshooting Guide](shimmy-vision-troubleshooting.md)**
Common issues and solutions:
- **License Issues**: Authentication, validation, usage limits
- **Installation Problems**: Build issues, model downloads, GPU setup
- **Image Processing**: Format support, size limits, URL processing
- **Performance**: Optimization, memory management, GPU acceleration
- **API Integration**: HTTP server, CORS, client libraries
- **Payment Issues**: Stripe checkout, webhook delivery, license generation

## 💰 Business Context

### **What We Sell**
- **Local Vision AI Processing**: OCR, layout analysis, web page extraction
- **Privacy-First**: No cloud dependencies, all processing local
- **Developer-Focused**: CLI + HTTP API for automation
- **Production-Ready**: Structured JSON output, robust error handling

### **Pricing Strategy**  
- **Tiered Subscriptions**: $12-$299/month based on usage limits
- **Page-Based Limits**: 2.5K to unlimited pages per month
- **Machine Licensing**: 1-unlimited licenses per tier
- **Lifetime Option**: $499 one-time for power users
- **International Payment**: WeChat Pay, Alipay for global reach

### **Customer Segments**
- **Primary**: Individual developers ($12-29/mo tiers)
- **Growth**: Small teams and agencies ($79/mo tier)  
- **Enterprise**: Large organizations ($299/mo + custom)
- **Lifetime**: Power users and indie hackers ($499 one-time)

## 🔧 Technical Details

### **Authentication & Security**
- **License Keys**: Format `XXXXXX-XXXXXX-XXXXXX-XXXXXX-XXXXXX-V3`
- **Validation**: Keygen API with Ed25519 signature verification
- **Usage Tracking**: Monthly limits enforced per license
- **Offline Grace**: 24-hour cached license validation

### **Vision Processing**
- **Model**: MiniCPM-V (hard-locked for quality)
- **Input**: JPEG, PNG, PDF, URLs, base64 encoded
- **Output**: Structured JSON with analysis results
- **Limits**: 25MB max image size, configurable dimensions

### **API Endpoints**
- **Vision**: `POST /api/vision` (license-gated)
- **Health**: `GET /health` (public)
- **License**: `POST /api/license/validate` (validation)
- **Usage**: `GET /api/license/usage` (tracking)

## 🚀 Deployment Status

### **Production Plan (Official)**
**Goal**: Backend lifecycle validation only. No product testing. Compare test/live parity, ensure endpoint consistency, then safe production deployment.

#### **Phase 1: Backend Lifecycle Validation (Test Mode Only)**
- [x] **Purchase Flow**: Stripe checkout → license creation
- [x] **Portal Access**: Customer portal sessions + license retrieval  
- [ ] **Test vs Live Parity**: Compare configurations and API responses
- [ ] **Endpoint Parity**: Verify frontend calls match backend endpoints

#### **Phase 2: Safe Production Deployment**
- [ ] **Frontend Switch**: Update to live worker URLs
- [ ] **Stripe Live Mode**: Toggle dashboard + verify products
- [ ] **First Production Purchase**: Manual credit card test

#### **Phase 3: Product Demo (Post-Production)**
- [ ] **GPU Mode Testing**: Build with CUDA for performance
- [ ] **Demo GIF Creation**: Record fast vision processing
- [ ] **Product Page Update**: Add demo to existing site

### **Production Environment**
- **Frontend**: Live at `michael-a-kuykendall.github.io/shimmy-vision`
- **Payment Worker**: `shimmy-license-webhook.workers.dev`  
- **Stripe**: Live mode with real payment processing
- **Keygen**: Production license generation

### **Test Environment**  
- **Payment Worker**: `shimmy-license-webhook-test.workers.dev`
- **Stripe**: Test mode with test cards (4242424242424242)
- **Keygen**: Test licenses for development

## 🔄 Workflow Integration

### **Customer Purchase Flow**
```
User visits shimmy-vision site → 
Selects pricing tier → 
Stripe embedded checkout → 
Payment completion → 
Webhook to Cloudflare Worker → 
Keygen API creates license → 
Email + success page with license key
```

### **Developer Usage Flow**
```
Download shimmy binary → 
Set SHIMMY_LICENSE_KEY env var → 
Run with --features vision → 
License validated via Keygen → 
Vision processing available via CLI/HTTP
```

## 📊 Key Configuration

### **Environment Variables**
- `SHIMMY_LICENSE_KEY` - User license key (required)
- `SHIMMY_VISION_MODEL_PATH` - Custom model location
- `SHIMMY_VISION_MAX_LONG_EDGE` - Image size limits
- `RUST_LOG` - Logging configuration

### **Keygen Configuration**
- **Account ID**: `6270bf9c-23ad-4483-9296-3a6d9178514a`
- **Public Key**: `42f313585a72a41513208800f730944f1a3b74a8acfff539f96ce244d029fa5d`
- **Policies**: Separate for each pricing tier with usage limits

### **Stripe Configuration**
- **Products**: 5 tiers with metadata including `keygen_policy_id`
- **Webhooks**: `checkout.session.completed` → Worker endpoint
- **Payment Methods**: Card, Link, WeChat Pay, Alipay (lifetime)

## 🛡️ Security & Compliance

### **License Verification**
- **Hard-coded Account ID**: Prevents key-swapping attacks
- **Ed25519 Signatures**: Cryptographic response verification  
- **Custom User-Agent**: Enables Keygen crack detection
- **Usage Metering**: Monthly caps enforced server-side

### **Payment Security**
- **Webhook Verification**: Stripe signature validation
- **Environment Isolation**: Separate test/live configurations
- **Secret Management**: Cloudflare Workers secrets, never in code

## 📈 Success Metrics

### **Business Metrics**
- **Monthly Recurring Revenue (MRR)**: Primary growth indicator
- **Customer Acquisition Cost (CAC)**: Marketing efficiency  
- **Lifetime Value (LTV)**: Long-term customer value
- **Tier Distribution**: Revenue mix across pricing tiers

### **Technical Metrics**
- **License Validations**: Monthly active users
- **Pages Processed**: Total platform usage
- **API Response Times**: Performance monitoring
- **Error Rates**: System reliability

## 🆘 Emergency Procedures

### **Critical Issues**
- **Payment Processing Down**: Check Stripe webhook delivery
- **License Validation Failing**: Verify Keygen API connectivity
- **Frontend Issues**: Check GitHub Pages deployment status
- **Security Incidents**: Follow responsible disclosure process

### **Rollback Process**
1. Revert frontend deployment via GitHub
2. Rollback Worker via `wrangler publish [previous-version]`
3. Disable Stripe webhooks if needed
4. Communicate status to customers

## 📞 Support & Contact

- **Technical Support**: michaelallenkuykendall@gmail.com
- **Business Inquiries**: Same email with "BUSINESS" in subject
- **Security Issues**: Same email with "SECURITY" - private disclosure
- **Documentation**: This `.github/instructions/` directory

## 🔄 Maintenance

This documentation is designed to be:
- **Self-Contained**: Complete context without external dependencies
- **AI-Friendly**: Structured for easy AI assistant consumption
- **Production-Ready**: Covers all aspects needed for system operation
- **Maintainable**: Clear structure for updates and additions

**Last Updated**: January 8, 2025  
**Version**: 1.0 (Production Ready)

For any questions or clarifications about the Shimmy Vision ecosystem, start with this documentation set and escalate to the support channels as needed.---
applyTo: "**"
---
