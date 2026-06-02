# AEM Content API & Headless

## Purpose
Implement headless content delivery using AEM's GraphQL API, Content Services, and Content Fragment APIs for decoupled frontend architectures and multi-channel distribution.

## When to Use (Triggers)
- User mentions "headless," "GraphQL," "Content Services," or "content API"
- References to Content Fragment delivery, persisted queries, or API endpoints
- Questions about SPA Editor, remote SPA, or decoupled frontend architecture
- Requests involving JSON delivery, REST endpoints for content, or SDK usage
- Discussion of AEM as a headless CMS or content-as-a-service patterns

## Core Capabilities
- Configure and optimize GraphQL persisted queries for Content Fragment delivery
- Implement Content Services (JSON Exporter) for page-based content APIs
- Set up AEM Headless SDK integration for JavaScript/React/Angular frontends
- Design Content Fragment Model schemas for API-first content delivery
- Configure CORS, authentication, and caching for headless endpoints

## Domain Knowledge Required
### Technical Foundation
- GraphQL schema design (types, queries, fragments, pagination, filtering)
- REST API design principles and JSON:API patterns
- CORS configuration and pre-flight request handling
- CDN caching strategies for API responses (Cache-Control, ETag, Vary)

### AEM-Specific Context
- AEM GraphQL API endpoint structure and persisted queries
- Content Fragment Model to GraphQL schema mapping
- Sling Model Exporter (@Exporter annotation) for JSON serialization
- AEM Headless SDK (JavaScript, Java, iOS, Android)
- Universal Editor and Remote SPA Editor integration

## Implementation Approach
### Step 1: Content Model Design for API
Design Content Fragment Models optimized for API consumption.
- Define models with API consumers in mind (field naming, nesting depth)
- Plan reference resolution strategy (inline vs. linked)
- Configure model field types for optimal serialization (JSON, multi-value)
- Design fragment relationships for query efficiency

### Step 2: GraphQL Configuration
Set up GraphQL endpoints and persisted queries.
- Create GraphQL endpoints for each site/project
- Write and persist common queries for frontend consumption
- Configure query complexity limits and depth restrictions
- Set up filtering, pagination, and sorting capabilities

### Step 3: Authentication & Security
Secure headless API access.
- Configure CORS policies for allowed origins
- Set up token-based authentication (service credentials, IMS tokens)
- Implement API rate limiting and throttling
- Configure CDN-level security (WAF rules, IP allowlisting)

### Step 4: Caching & Performance
Optimize API response performance.
- Configure CDN caching for persisted query responses
- Implement cache invalidation on content publish
- Set up ETags and conditional requests
- Design query patterns that minimize response size

### Step 5: Frontend Integration
Connect frontend applications to AEM headless.
- Integrate AEM Headless SDK in frontend framework
- Implement content preview and editing capabilities
- Configure environment-specific endpoint configuration
- Set up error handling and retry logic for API calls

## Quality Checklist
- [ ] GraphQL persisted queries return expected data structure
- [ ] CORS configured for all required frontend origins
- [ ] API responses cached at CDN with appropriate TTL
- [ ] Cache invalidation triggers on content publish
- [ ] Authentication tokens validated and refreshed correctly
- [ ] API response times under 200ms for common queries (cached)
- [ ] Error responses follow consistent format with actionable messages
- [ ] Content preview works for unpublished content in author mode

## Related Skills
- aem-content-strategy-architecture (content model design)
- aem-caching-strategy (API caching)
- aem-dispatcher-configuration (API routing and caching at dispatcher)

## Example Use Cases
1. **React SPA with AEM Backend:** Build a single-page application consuming Content Fragments via GraphQL persisted queries with real-time preview in AEM author using Universal Editor.
2. **Mobile App Content Feed:** Deliver personalized content to iOS/Android apps using AEM Headless SDK with offline caching, pagination, and push-notification-triggered content refresh.
3. **Multi-Channel Content Hub:** Serve identical content to web, digital signage, chatbot, and email systems through a unified GraphQL API with channel-specific field selection and transformation.

## Notes
- Persisted queries are production-recommended — avoid runtime query execution for performance
- AEM Cloud Service has built-in CDN for GraphQL endpoints — leverage it rather than adding custom CDN
- Content Fragment references resolve up to 10 levels deep by default — design shallow hierarchies
- GraphQL API only serves published content on publish tier — use author endpoint for preview
