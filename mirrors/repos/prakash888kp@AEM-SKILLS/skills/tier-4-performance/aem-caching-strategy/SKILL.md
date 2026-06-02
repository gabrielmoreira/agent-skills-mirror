# AEM Caching Strategy

## Purpose
Design and implement multi-layer caching architectures spanning CDN, dispatcher, AEM in-memory caches, and application-level caches for optimal content delivery performance.

## When to Use (Triggers)
- User mentions "caching," "cache invalidation," "cache strategy," or "TTL"
- References to dispatcher cache, CDN cache, Sling caching, or in-memory cache
- Questions about cache hit ratio, stale content, or cache warming
- Requests involving personalized content caching or edge-side includes
- Discussion of cache coherency, invalidation patterns, or cache hierarchy

## Core Capabilities
- Design multi-tier caching architecture (CDN → Dispatcher → AEM → JCR)
- Configure TTL-based and event-based cache invalidation strategies
- Implement application-level caching for expensive computations
- Handle personalized content caching using Edge Side Includes (ESI) or client-side
- Optimize cache hit ratios across all caching layers

## Domain Knowledge Required
### Technical Foundation
- HTTP caching semantics (Cache-Control directives, Vary header, ETag, conditional requests)
- CDN architecture (edge caching, origin shield, cache keys, purge APIs)
- Cache invalidation patterns (TTL, event-based, tag-based, surrogate keys)
- Cache consistency models (eventual, strong, read-after-write)

### AEM-Specific Context
- Dispatcher cache (file-based, stat file invalidation, auto-invalidation)
- AEM in-memory caches (Sling ResourceResolver cache, component output cache)
- Stat file level and its impact on invalidation scope
- Grace period configuration for serving stale content during refresh
- Client library fingerprinting for long-term asset caching

## Implementation Approach
### Step 1: Cache Architecture Design
Plan the caching layers and their responsibilities.
- Map content types to appropriate caching tiers
- Define TTL strategy per content type (static: days, pages: hours, API: minutes)
- Identify uncacheable content and alternatives (ESI, client-side, SDI)
- Plan cache key strategy (URL, headers, cookies that vary)

### Step 2: CDN Configuration
Set up edge caching for global performance.
- Configure CDN caching rules per content type
- Set up surrogate keys or cache tags for targeted purge
- Implement origin shield to reduce load on dispatcher
- Configure WAF rules that don't break caching

### Step 3: Dispatcher Cache Optimization
Maximize dispatcher cache effectiveness.
- Configure stat file level for granular invalidation
- Implement permission-sensitive caching where needed
- Set up cache warming after deployment or invalidation
- Configure grace period and serveStaleOnError

### Step 4: Application-Level Caching
Implement in-AEM caching for expensive operations.
- Cache Sling Model computation results with TTL
- Implement query result caching for repeated queries
- Use Guava/Caffeine cache for service-level data caching
- Configure cache sizing based on available heap

### Step 5: Invalidation Strategy
Implement coherent cache invalidation across all layers.
- Configure flush agents for dispatcher invalidation on publish
- Set up CDN purge triggers on content activation
- Implement tag-based invalidation for related content groups
- Design cache warming jobs post-invalidation

## Quality Checklist
- [ ] CDN cache hit ratio > 95% for static assets
- [ ] Dispatcher cache hit ratio > 85% for page content
- [ ] No stale content visible beyond defined TTL
- [ ] Cache invalidation triggers within 30 seconds of publish
- [ ] Personalized content doesn't pollute shared cache
- [ ] Cache warming covers critical user paths after deploy
- [ ] Application-level caches bounded and don't cause OOM
- [ ] Monitoring in place for cache hit ratios across all layers

## Related Skills
- aem-dispatcher-configuration (dispatcher cache details)
- aem-performance-tuning-profiling (performance measurement)
- aem-content-api-headless (API response caching)

## Example Use Cases
1. **E-commerce Product Pages:** Implement multi-layer caching for 50,000 product pages with personalized pricing (client-side fetch), shared product details (dispatcher cache, 1h TTL), and static assets (CDN, 1y TTL with fingerprinting).
2. **News Site with Breaking Content:** Design caching strategy balancing freshness (5-minute TTL for homepage) with performance (long TTL for article pages), using Sling Dynamic Include for personalized sidebar content.
3. **Global CDN with Regional Content:** Configure CDN caching with Vary header on geo-location for region-specific content, surrogate key purging for content updates, and edge-side includes for user-specific navigation.

## Notes
- Dispatcher cache is file-based — every cached response is a file on disk; monitor disk space
- Stat file invalidation invalidates entire subtrees — set stat file level carefully
- Never cache responses with Set-Cookie headers — this caches session identifiers
- AEM Cloud Service includes built-in CDN — configure via dispatcher rules, not separate CDN config
