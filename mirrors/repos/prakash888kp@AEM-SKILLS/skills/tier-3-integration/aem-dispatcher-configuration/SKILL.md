# AEM Dispatcher Configuration

## Purpose
Configure, optimize, and troubleshoot the AEM Dispatcher module for Apache/IIS including caching rules, filter definitions, load balancing, and security hardening.

## When to Use (Triggers)
- User mentions "dispatcher," "cache rules," "filter rules," or "Apache configuration"
- References to `.any` files, `dispatcher.conf`, or vanity URL handling
- Questions about cache invalidation, TTL, stat files, or auto-invalidation
- Requests involving URL rewriting, redirect management, or request filtering
- Discussion of CDN integration, load balancing, or dispatcher farm configuration

## Core Capabilities
- Configure dispatcher farms with cache rules, filters, and render definitions
- Implement fine-grained cache invalidation strategies (stat file level, explicit flush)
- Design URL rewriting and redirect management with dispatcher rules
- Set up security filters blocking sensitive paths and parameters
- Optimize cache hit ratio through strategic caching configuration

## Domain Knowledge Required
### Technical Foundation
- Apache HTTP Server module architecture and configuration
- HTTP caching semantics (Cache-Control, Expires, ETag, Last-Modified)
- URL rewriting with mod_rewrite rules and conditions
- Load balancing algorithms and health check patterns

### AEM-Specific Context
- Dispatcher module architecture (.any configuration hierarchy)
- Cache invalidation via stat files and auto-invalidation
- Flush agents and their interaction with dispatcher cache
- Dispatcher filter syntax (allow/deny, glob patterns, URL structure)
- Stat file level and its impact on invalidation granularity
- Grace period and serveStaleOnError behavior

## Implementation Approach
### Step 1: Farm Architecture
Design the dispatcher farm topology.
- Define farms per site/domain (author farm, publish farm(s))
- Configure renders (publish instance connections)
- Set up load balancing with health checks (stickyConnections, healthcheck URL)
- Define virtual hosts and domain routing

### Step 2: Cache Configuration
Set up caching rules for optimal hit ratio.
- Define cache root directory and cache headers
- Configure cacheable paths and document types (/cache rules)
- Set stat file level for appropriate invalidation granularity
- Configure grace period for stale content serving during invalidation
- Implement TTL-based caching for API responses

### Step 3: Filter Rules
Implement security and access filtering.
- Block access to system paths (/crx, /system, /libs)
- Filter query parameters that shouldn't reach AEM
- Block extension-based attacks (.json, .xml on sensitive paths)
- Allow only required HTTP methods per path
- Implement dispatcher-level CSRF validation

### Step 4: URL Management
Configure rewrites and redirects.
- Implement vanity URL resolution
- Configure resource mapping (Sling mapping) integration
- Set up redirect rules for SEO and legacy URL handling
- Handle extension-less URLs and content path mapping

### Step 5: Performance Tuning
Optimize dispatcher for high traffic.
- Tune cache hit ratio (target >95% for static, >80% for pages)
- Configure concurrent connections and timeouts
- Implement cache warming strategies
- Set up dispatcher clustering for high availability

## Quality Checklist
- [ ] Cache hit ratio exceeds 90% for page content
- [ ] Security filters block all sensitive AEM paths
- [ ] Flush agents correctly invalidate changed content
- [ ] Load balancing distributes traffic evenly with failover
- [ ] URL rewrites handle all required patterns without loops
- [ ] Configuration validated with dispatcher validator tool
- [ ] Grace period configured for availability during cache misses
- [ ] No query string parameters leak to cache file paths incorrectly

## Related Skills
- aem-caching-strategy (overall caching architecture)
- aem-security-access-control (dispatcher security layer)
- aem-replication-publishing (flush agent configuration)

## Example Use Cases
1. **Multi-Site Dispatcher:** Configure a single dispatcher serving 5 domains with site-specific cache rules, shared static asset caching, and per-site filter policies with different security requirements.
2. **API Gateway Pattern:** Set up dispatcher as API gateway for headless content delivery with TTL-based caching, CORS header injection, and authentication token validation at the edge.
3. **Zero-Downtime Deployment:** Implement dispatcher-level blue/green deployment support with health-check-based render switching, cache warming of new instances, and automatic failback on health check failure.

## Notes
- AEM Cloud Service manages dispatcher config via Cloud Manager — use the SDK dispatcher tools for local validation
- Always validate configuration with `dispatcher-sdk-validator` before deployment
- Stat file level is the single most impactful cache efficiency setting — set it thoughtfully
- Dispatcher does NOT cache responses with Set-Cookie headers — ensure AEM doesn't set cookies on cacheable responses
