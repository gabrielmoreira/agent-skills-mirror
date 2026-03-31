---
applyTo: "**"
---
# Shimmy Vision Business Model & Products

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

## Product Overview

**Shimmy Vision** is a locally-run vision AI product that transforms images, documents, and web pages into structured JSON data. Built as a paid feature for the open-source Shimmy inference server.

### **Value Proposition**
- **Privacy-First**: Runs entirely locally, no data sent to cloud
- **Developer-Focused**: CLI + HTTP API for automation and integration  
- **Production-Ready**: Structured JSON output, robust error handling
- **Easy Integration**: Drops into existing AI workflows and tools

## Product Tiers & Pricing

### **1. Developer - $12/month**
**Target**: Individual developers, small projects
- **Pages**: 2,500/month
- **Machines**: 1 license
- **Features**: OCR + Layout + Web extraction
- **Use Case**: Personal projects, prototyping, learning

### **2. Professional - $29/month**  
**Target**: Freelancers, consultants, small agencies
- **Pages**: 10,000/month
- **Machines**: 1 license  
- **Features**: Client-ready results, CLI + HTTP API
- **Use Case**: Client work, automation, production apps

### **3. Startup - $79/month**
**Target**: Small teams, growing companies
- **Pages**: 50,000/month  
- **Machines**: Up to 5 licenses
- **Features**: Team deployment, pipeline integration
- **Use Case**: Product features, team workflows, scaling

### **4. Enterprise - $299/month**
**Target**: Large organizations, enterprise teams  
- **Pages**: Unlimited
- **Machines**: Unlimited licenses
- **Features**: Dedicated support, enterprise deployment
- **Use Case**: Large-scale processing, enterprise integration

### **5. Lifetime - $499 one-time**
**Target**: Power users, indie hackers, lifetime value seekers
- **Pages**: Unlimited  
- **Machines**: 1 license
- **Features**: All future updates, no recurring cost
- **Payment**: WeChat Pay, Alipay, Card, Link (optimized for international)

## Revenue Model

### **Subscription Revenue (Monthly)**
- **Monthly Recurring Revenue (MRR)**: Primary revenue stream
- **Annual Plans**: 2-month discount for annual payment  
- **Usage-Based**: Monthly page processing limits
- **Overages**: Additional pages at tiered rates

### **One-Time Revenue**
- **Lifetime Licenses**: High-value one-time purchases
- **Enterprise Setup**: Custom deployment and configuration
- **Training/Support**: Premium support packages

## Customer Journey

### **Discovery Phase**
1. **SEO Traffic**: "local vision AI", "privacy OCR", "document processing"
2. **GitHub**: Open source shimmy users discover vision features
3. **Developer Communities**: Reddit, HackerNews, Dev.to
4. **Content Marketing**: Technical blogs, tutorials, demos

### **Evaluation Phase**  
1. **Free Trial**: Download shimmy, try without license (limited)
2. **Documentation**: Comprehensive API docs, examples, tutorials
3. **Demo Videos**: Screen recordings of real-world usage
4. **Community**: Discord/GitHub discussions, support

### **Purchase Phase**
1. **Pricing Page**: Clear tier comparison on shimmy-vision site
2. **Stripe Checkout**: Embedded, mobile-optimized payment flow
3. **License Delivery**: Immediate email + success page with key
4. **Onboarding**: Quick-start guide, example scripts

### **Usage Phase**
1. **License Setup**: Set SHIMMY_LICENSE_KEY environment variable  
2. **API Integration**: HTTP endpoints for automation
3. **CLI Usage**: Direct command-line processing  
4. **Monitoring**: Usage dashboards, limit notifications

### **Retention Phase**
1. **Usage Monitoring**: Track monthly limits, send warnings
2. **Feature Updates**: New vision models, capabilities
3. **Support**: Email support, community forums
4. **Upselling**: Move users to higher tiers as usage grows

## Competitive Positioning

### **vs. Cloud Vision APIs (Google, AWS, Azure)**
- **Privacy**: No data leaves user's machine
- **Cost**: Predictable monthly pricing vs. per-API-call
- **Latency**: No network roundtrips
- **Reliability**: Works offline, no API limits

### **vs. Open Source Solutions**  
- **Quality**: Professional OCR + layout analysis
- **Support**: Dedicated support and documentation
- **Integration**: Purpose-built for developer workflows
- **Reliability**: Production-tested, battle-hardened

### **vs. Desktop OCR Software**
- **Automation**: HTTP API + CLI for scripting
- **Modern Output**: JSON schema, not just text
- **Developer Experience**: Built for technical users
- **Integration**: Drops into existing AI/ML pipelines

## Market Segments

### **Primary Segments**

#### **1. AI/ML Developers**
- **Size**: ~50K developers globally
- **Need**: Document processing for RAG, training data
- **Budget**: $30-100/month for tools
- **Acquisition**: Technical content, GitHub, conferences

#### **2. Automation Engineers**  
- **Size**: ~100K professionals globally
- **Need**: Document workflow automation
- **Budget**: $50-300/month for business tools
- **Acquisition**: RPA communities, business automation blogs

#### **3. Independent Developers**
- **Size**: ~500K globally  
- **Need**: Client work, SaaS features, side projects
- **Budget**: $10-50/month for development tools
- **Acquisition**: Developer communities, social media

### **Secondary Segments**

#### **4. Small Agencies**
- **Size**: ~10K agencies globally
- **Need**: Client deliverables, competitive advantage
- **Budget**: $100-500/month for tools and software
- **Acquisition**: Agency networks, case studies

#### **5. Enterprise Teams**
- **Size**: ~1K large companies globally  
- **Need**: On-premise solutions, privacy compliance
- **Budget**: $1K-10K/month for enterprise tools
- **Acquisition**: Direct sales, enterprise partnerships

## Growth Strategy

### **Phase 1: Developer Adoption (0-100 customers)**
- **Focus**: Individual developer adoption
- **Channels**: GitHub, Reddit, HackerNews
- **Pricing**: Emphasize Developer and Professional tiers
- **Content**: Technical tutorials, API documentation

### **Phase 2: Team Expansion (100-500 customers)**
- **Focus**: Small teams and agencies
- **Channels**: Startup communities, agency networks  
- **Pricing**: Push Startup tier, introduce annual plans
- **Content**: Case studies, team workflow guides

### **Phase 3: Enterprise Growth (500+ customers)**
- **Focus**: Large organizations, enterprise deals
- **Channels**: Direct sales, partner referrals
- **Pricing**: Enterprise tier, custom pricing
- **Content**: Compliance guides, security documentation

## Production Deployment Plan

**Goal**: Backend lifecycle validation only. No product testing. Compare test/live parity, ensure endpoint consistency, then safe production deployment.

### **Phase 1: Backend Lifecycle Validation (Test Mode Only)**
- [x] **Purchase Flow**: Stripe checkout → license creation
- [x] **Portal Access**: Customer portal sessions + license retrieval  
- [ ] **Test vs Live Parity**: Compare configurations and API responses
- [ ] **Endpoint Parity**: Verify frontend calls match backend endpoints

### **Phase 2: Safe Production Deployment**
- [ ] **Frontend Switch**: Update to live worker URLs
- [ ] **Stripe Live Mode**: Toggle dashboard + verify products
- [ ] **First Production Purchase**: Manual credit card test

### **Phase 3: Product Demo (Post-Production)**
- [ ] **GPU Mode Testing**: Build with CUDA for performance
- [ ] **Demo GIF Creation**: Record fast vision processing
- [ ] **Product Page Update**: Add demo to existing site

## Key Metrics

### **Acquisition Metrics**
- **Monthly Signups**: New trial users per month
- **Conversion Rate**: Trial to paid conversion
- **Customer Acquisition Cost (CAC)**: Marketing spend per customer
- **Organic Traffic**: SEO and content-driven visitors

### **Revenue Metrics**  
- **Monthly Recurring Revenue (MRR)**: Primary business metric
- **Average Revenue Per User (ARPU)**: Revenue efficiency
- **Lifetime Value (LTV)**: Long-term customer value
- **LTV/CAC Ratio**: Unit economics health

### **Usage Metrics**
- **Monthly Active Users**: License validations per month
- **Pages Processed**: Total usage across all customers  
- **Feature Adoption**: API vs CLI usage patterns
- **Tier Distribution**: Revenue mix across pricing tiers

### **Retention Metrics**
- **Churn Rate**: Monthly customer loss percentage
- **Tier Migration**: Customer movement between plans
- **Usage Growth**: Customer expansion within tiers
- **Support Tickets**: Customer satisfaction indicator

This business model provides multiple revenue streams, clear customer segmentation, and a growth path from individual developers to enterprise teams.