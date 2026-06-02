# AEM Commerce & Content System Integration

## Purpose
Integrate AEM with commerce platforms (Adobe Commerce/Magento, Salesforce Commerce, SAP Commerce) using the Commerce Integration Framework (CIF) for unified content-commerce experiences.

## When to Use (Triggers)
- User mentions "commerce," "CIF," "product catalog," or "shopping experience"
- References to Adobe Commerce, Magento, commerce connectors, or product data
- Questions about product detail pages, cart integration, or checkout flows
- Requests involving commerce data in AEM components or commerce APIs
- Discussion of CIF Core Components, GraphQL commerce, or commerce authoring

## Core Capabilities
- Configure Commerce Integration Framework (CIF) with commerce backends
- Implement CIF Core Components for product display and commerce functionality
- Design content-commerce page patterns (PDP, PLP, cart, checkout)
- Build custom commerce components using CIF React components
- Integrate product data with AEM content authoring workflows

## Domain Knowledge Required
### Technical Foundation
- Commerce platform architecture (catalog, cart, checkout, order management)
- GraphQL API patterns for commerce data (products, categories, cart mutations)
- Micro-frontend patterns for commerce widgets
- Commerce data modeling (SKU, variants, pricing, availability)

### AEM-Specific Context
- Commerce Integration Framework (CIF) architecture and components
- CIF Core Components (product teaser, product list, search bar, cart)
- Commerce product picker for authoring (product/category selection)
- CIF URL pattern handling (product URLs, category URLs)
- CIF GraphQL client and caching layer
- Commerce Cloud Service configuration

## Implementation Approach
### Step 1: Commerce Backend Connection
Configure the connection to the commerce platform.
- Install CIF add-on and connector for target commerce platform
- Configure Commerce Cloud Service with endpoint and credentials
- Set up GraphQL endpoint connectivity and authentication
- Validate product catalog data accessibility from AEM

### Step 2: Catalog & Navigation
Implement product browsing and discovery.
- Configure category page template with CIF navigation component
- Set up product list page (PLP) with filtering and pagination
- Implement product detail page (PDP) template with variants
- Configure URL generation for SEO-friendly commerce pages

### Step 3: Commerce Components
Build and customize commerce UI components.
- Deploy CIF Core Components as foundation
- Customize product teaser for brand-specific display
- Implement add-to-cart with variant selection
- Build wishlist and comparison functionality
- Configure product recommendations component

### Step 4: Content-Commerce Fusion
Combine editorial content with commerce data.
- Create editorial content areas on PDP (brand story, usage guides)
- Implement commerce-aware Experience Fragments (upsell, cross-sell)
- Build content-driven product showcases (lookbooks, collections)
- Configure personalization using commerce context (cart contents, browse history)

### Step 5: Cart & Checkout
Implement shopping flow components.
- Configure mini-cart and full cart page components
- Integrate checkout flow with commerce platform
- Handle payment and shipping service connections
- Implement order confirmation and account pages

## Quality Checklist
- [ ] Product data loads within 2 seconds on PDP
- [ ] Cart operations (add, update, remove) function correctly
- [ ] Commerce URLs resolve to correct products/categories
- [ ] Cached product data refreshes on catalog updates
- [ ] Authoring experience allows product selection via picker
- [ ] Commerce components render correctly in AEM preview
- [ ] Pricing and availability data reflects real-time backend state
- [ ] Commerce functionality works on all supported breakpoints

## Related Skills
- aem-content-api-headless (headless commerce delivery)
- aem-personalization-ecommerce (commerce personalization)
- aem-caching-strategy (commerce data caching)

## Example Use Cases
1. **Fashion Retail Platform:** Integrate AEM with Adobe Commerce for 50,000 SKUs with visual merchandising, lookbook content, size/color variant selection, and personalized recommendations.
2. **B2B Commerce Portal:** Build a B2B purchasing experience with custom pricing tiers, bulk ordering, approval workflows for purchases, and account-specific product catalogs.
3. **Multi-Brand Marketplace:** Implement a marketplace experience where multiple brands share a commerce backend with brand-specific content experiences, shared cart, and unified checkout.

## Notes
- CIF uses GraphQL for real-time commerce data — cache aggressively for catalog data, minimally for pricing
- Product URLs are virtual in AEM — they don't correspond to JCR pages but resolve via CIF URL provider
- CIF Core Components are React-based micro-frontends embedded in AEM pages
- Adobe Commerce (Magento) is the primary supported backend but CIF supports custom connectors
