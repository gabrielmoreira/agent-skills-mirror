# AEM Content Strategy & Architecture

## Purpose
Design content architecture including information hierarchy, content models, taxonomy strategies, and governance frameworks that support scalable multi-channel content delivery.

## When to Use (Triggers)
- User mentions "content architecture," "content model," "information architecture," or "content strategy"
- References to content types, taxonomy design, or content governance
- Questions about Content Fragments models, page hierarchy, or content reuse
- Requests involving multi-channel content delivery or content-as-a-service
- Discussion of content migration, restructuring, or scalability planning

## Core Capabilities
- Design content type hierarchies using Content Fragment Models
- Create page hierarchies optimized for authoring, navigation, and SEO
- Define taxonomy and tagging strategies aligned with business objectives
- Plan content reuse patterns (Experience Fragments, Content Fragments, MSM)
- Establish content governance frameworks with roles, workflows, and quality gates

## Domain Knowledge Required
### Technical Foundation
- Content modeling principles (structured vs. unstructured, reference vs. embedded)
- Information architecture patterns (hierarchy, faceted, sequential)
- Content lifecycle: creation, review, publication, archival, deletion
- Headless content delivery via GraphQL and Content Services

### AEM-Specific Context
- Content Fragment Models vs. page components vs. Experience Fragments
- Content Fragment variations and associated content
- Sling resource merger and content inheritance
- Content references (fragmentPath, pagePath) and their resolution
- AEM Sites content hierarchy and navigation generation

## Implementation Approach
### Step 1: Content Audit & Requirements
Analyze existing content and business requirements.
- Inventory existing content types and volumes
- Identify content reuse requirements across channels/sites
- Map content to business goals and user journeys
- Define content lifecycle requirements (freshness, expiration, compliance)

### Step 2: Content Model Design
Create the structural models for content.
- Define Content Fragment Models for structured, headless content
- Design page templates for channel-specific presentation
- Establish Experience Fragment templates for reusable, rendered blocks
- Plan model relationships and reference patterns

### Step 3: Taxonomy & Classification
Build the organizational structure for content discovery.
- Design tag namespaces aligned with business domains
- Define controlled vocabularies for critical metadata
- Plan automated tagging rules and smart tag training
- Create category hierarchies supporting faceted navigation

### Step 4: Governance Framework
Establish rules and processes for content quality.
- Define content ownership and responsibility matrix
- Create editorial calendars and publishing schedules
- Establish review/approval workflows per content type
- Set content quality scoring criteria and validation rules

### Step 5: Scalability Planning
Ensure architecture supports growth.
- Plan for multi-site, multi-language expansion
- Design content APIs for future channel requirements
- Establish content archival and lifecycle automation
- Create migration patterns for content evolution

## Quality Checklist
- [ ] Content models support all identified use cases without customization
- [ ] Taxonomy depth does not exceed 4 levels for any branch
- [ ] Content can be delivered to all required channels (web, mobile, email, kiosk)
- [ ] Governance roles mapped to AEM groups with proper permissions
- [ ] Content reuse strategy reduces duplication by at least 30%
- [ ] URL structure supports SEO and user comprehension
- [ ] Content model supports localization requirements
- [ ] Migration path defined for existing content

## Related Skills
- aem-content-api-headless (content delivery)
- aem-template-page-structure (content presentation)
- aem-content-localization-i18n (multi-language content)

## Example Use Cases
1. **Healthcare Content Platform:** Design content architecture for patient education materials requiring medical accuracy review, regulatory compliance metadata, multi-language support, and personalization by condition type.
2. **News Media Redesign:** Architect content model separating editorial content (articles, galleries, videos) from presentation, enabling simultaneous delivery to web, mobile app, Apple News, and AMP with a single content source.
3. **University Website Consolidation:** Merge 200+ department sites into a unified content architecture with shared navigation, centralized brand governance, and delegated authoring permissions per department.

## Notes
- Content Fragment Models are immutable once content is created against them — design with future extensibility in mind
- Prefer Content Fragments over page components for content that must be channel-agnostic
- Experience Fragments are rendered components — use for content that needs visual consistency across touchpoints
- Content architecture decisions are expensive to change — invest in upfront modeling workshops
