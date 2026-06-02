# AEM Personalization & eCommerce

## Purpose
Implement personalized content experiences for eCommerce using AEM's personalization engine, Adobe Target integration, ContextHub, and commerce-context-driven content targeting.

## When to Use (Triggers)
- User mentions "personalization," "targeting," "segments," "A/B testing," or "audiences"
- References to ContextHub, Adobe Target, or content targeting in AEM
- Questions about user segments, personalized experiences, or recommendation engines
- Requests involving behavioral targeting, commerce-driven personalization, or dynamic content
- Discussion of conversion optimization, experience variants, or audience definition

## Core Capabilities
- Configure ContextHub for user context collection and segment evaluation
- Implement content targeting using AEM's built-in personalization engine
- Integrate Adobe Target for A/B testing and AI-powered personalization
- Build commerce-context segments (cart value, purchase history, browse behavior)
- Design personalization strategies with measurement and optimization

## Domain Knowledge Required
### Technical Foundation
- Personalization concepts (segments, audiences, activities, experiences, offers)
- A/B and multivariate testing methodology and statistical significance
- User data collection patterns (first-party, consent-based)
- Machine learning-based recommendation systems

### AEM-Specific Context
- ContextHub architecture (stores, modules, segments)
- AEM targeting mode and experience editing
- Adobe Target integration via A4T (Analytics for Target)
- Experience Fragment offers for Target activities
- AEM Personalization vs. Adobe Target personalization capabilities
- Real-Time Customer Profile integration (via Adobe Experience Platform)

## Implementation Approach
### Step 1: Personalization Strategy
Define targeting goals and segment architecture.
- Identify personalization use cases with business value
- Define user segments based on available data signals
- Plan content variation strategy (how many variants, which content)
- Establish success metrics and measurement approach

### Step 2: ContextHub Configuration
Set up user context collection and segmentation.
- Configure ContextHub stores for data collection (profile, cart, geolocation)
- Define custom ContextHub store implementations for commerce data
- Create segment definitions using segment rules editor
- Implement consent-aware data collection (GDPR/CCPA compliance)

### Step 3: Content Targeting Setup
Configure personalized experiences in AEM.
- Enable targeting mode for applicable templates/pages
- Create targeted experiences for defined segments
- Configure default (fallback) experience for unmatched users
- Set up Experience Fragment offers for reusable personalized blocks

### Step 4: Adobe Target Integration
Connect AEM with Adobe Target for advanced personalization.
- Configure Adobe Target Cloud Service in AEM
- Export Experience Fragments as Target offers
- Set up A/B activities and experience targeting activities
- Configure Analytics integration for measurement (A4T)
- Implement auto-allocation for automated winner selection

### Step 5: Commerce Personalization
Apply personalization using commerce context.
- Build segments based on cart contents and value
- Implement browse history-based product recommendations
- Create purchase history-driven content targeting
- Configure abandonment recovery experiences
- Design loyalty tier-based content personalization

## Quality Checklist
- [ ] Segments evaluate correctly for all defined user contexts
- [ ] Personalized content loads without visible layout shift (CLS < 0.1)
- [ ] Default experience serves for unrecognized users
- [ ] A/B tests configured with proper traffic allocation
- [ ] Consent management integrated with personalization (GDPR)
- [ ] Performance impact of personalization < 200ms additional latency
- [ ] Analytics tracking captures personalization exposure events
- [ ] Personalization degrades gracefully when context unavailable

## Related Skills
- aem-commerce-content-system-integration (commerce data)
- aem-content-api-headless (personalized headless delivery)
- aem-caching-strategy (caching personalized content)

## Example Use Cases
1. **Cart Abandonment Recovery:** Detect users with items in cart returning after 24 hours, display personalized hero banner with their cart items and incentive offer, measure recovery rate vs. standard experience.
2. **Loyalty Tier Experience:** Deliver differentiated site experiences based on loyalty program tier (bronze, silver, gold, platinum) with exclusive content, early access announcements, and tier-specific offers.
3. **AI-Powered Recommendations:** Integrate Adobe Target Recommendations with AEM product pages showing "customers also bought" and "recommended for you" sections with automated algorithm selection.

## Notes
- ContextHub runs client-side — personalization causes a brief delay before targeted content renders
- Adobe Target's edge delivery can reduce personalization latency vs. ContextHub client-side evaluation
- Caching personalized content is complex — use SDI, ESI, or client-side personalization to maintain cache efficiency
- Always provide a meaningful default experience — personalization should enhance, not gate, the experience
