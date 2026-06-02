# AEM Content Modeling for Retail

## Purpose
Design and implement retail-specific content models including product content structures, campaign hierarchies, store locator data, and omnichannel content architectures for retail brands.

## When to Use (Triggers)
- User mentions "retail content," "product content," "store content," or "retail modeling"
- References to product information beyond catalog (editorial content, guides, reviews)
- Questions about seasonal campaigns, promotional content, or retail calendars
- Requests involving store locator data, regional promotions, or omnichannel content
- Discussion of retail content workflows, merchandising content, or brand content

## Core Capabilities
- Design Content Fragment Models for retail content types (products, stories, recipes)
- Create campaign and promotional content hierarchies with temporal validity
- Implement store/location content models with geographic attributes
- Build omnichannel content structures for web, mobile, in-store, and email
- Configure retail-specific metadata schemas and classification systems

## Domain Knowledge Required
### Technical Foundation
- Content modeling for multi-channel delivery
- Temporal content patterns (valid-from, valid-to, seasonal content)
- Geographic data modeling (locations, regions, store attributes)
- Product information architecture (product → variant → SKU hierarchy)

### AEM-Specific Context
- Content Fragment Models with nested fragments and fragment references
- Structured content for headless delivery to retail channels
- Experience Fragment variations for channel-specific rendering
- Tag-based content classification for merchandising categories
- Content Fragment API for POS/kiosk/digital signage delivery

## Implementation Approach
### Step 1: Retail Content Audit
Analyze retail content types and relationships.
- Inventory content types (product stories, buying guides, lookbooks, store content)
- Map content lifecycle (seasonal, evergreen, promotional, regulatory)
- Identify multi-channel delivery requirements per content type
- Define content relationships (product → story → campaign → store)

### Step 2: Content Fragment Model Design
Build models for each retail content type.
- Design product editorial model (beyond PIM data: brand stories, usage tips)
- Create campaign model (hero, offers, terms, validity dates)
- Build store/location model (address, hours, services, events)
- Implement recipe/guide model (ingredients, steps, related products)

### Step 3: Campaign Hierarchy
Implement temporal promotional content.
- Design campaign folder structure (/content/dam/campaigns/2024/spring/)
- Create campaign content model with date-based validity
- Implement campaign-to-product association patterns
- Configure scheduled activation aligned with campaign dates

### Step 4: Omnichannel Delivery
Enable content for all retail touchpoints.
- Configure GraphQL endpoints for mobile app consumption
- Set up Content Fragment delivery for in-store digital signage
- Design email-compatible content variants
- Build social media content derivation patterns

### Step 5: Merchandising Integration
Connect content with merchandising strategy.
- Implement product-to-content mapping (PIM ID → Content Fragments)
- Create visual merchandising content tools for category pages
- Build promotional banner content with A/B testing variants
- Configure content recommendations engine integration

## Quality Checklist
- [ ] Content models support all identified retail content types
- [ ] Temporal content (campaigns, promos) has clear validity metadata
- [ ] Store content includes all required location attributes
- [ ] Content deliverable to all required channels (web, app, kiosk, email)
- [ ] Product-to-content relationships maintain data integrity
- [ ] Campaign content supports rapid turnaround (< 2 hour publish)
- [ ] Content models extensible for future retail needs
- [ ] Authoring experience efficient for merchandising team

## Related Skills
- aem-content-strategy-architecture (overall content architecture)
- aem-commerce-content-system-integration (commerce data integration)
- aem-personalization-ecommerce (personalized retail experiences)

## Example Use Cases
1. **Seasonal Campaign System:** Model a campaign structure supporting Black Friday, holiday, back-to-school, and clearance campaigns with cascading promotional content from brand level to individual store level.
2. **Recipe & Lifestyle Content:** Design content models for a grocery retailer's recipe platform linking recipes to purchasable products, nutritional information, dietary filters, and seasonal ingredient availability.
3. **Store Experience Content:** Build a store locator content model supporting store-specific events, local promotions, available services (curbside pickup, personal shopping), and real-time inventory messaging.

## Notes
- Retail content has high velocity — design models and workflows for rapid authoring and publishing
- Product editorial content often outlives individual products — plan for product discontinuation
- Campaign content volume peaks seasonally — plan for burst authoring capacity
- Always separate PIM data (prices, SKUs) from editorial content (stories, guides) — they have different lifecycles
