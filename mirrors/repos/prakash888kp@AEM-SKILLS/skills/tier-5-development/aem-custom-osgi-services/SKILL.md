# AEM Custom OSGi Services

## Purpose
Design and implement custom OSGi services, configurations, and components in AEM following best practices for modularity, testability, and lifecycle management.

## When to Use (Triggers)
- User mentions "OSGi service," "OSGi component," "service registration," or "bundle"
- References to @Component, @Reference, @Activate, or SCR annotations
- Questions about service configuration, factory configurations, or service ranking
- Requests involving dependency injection, service interfaces, or bundle architecture
- Discussion of OSGi Declarative Services, configuration admin, or metatype

## Core Capabilities
- Implement OSGi Declarative Services components with proper lifecycle annotations
- Design service interfaces with multiple implementations and service ranking
- Configure OSGi services using Configuration Admin and metatype annotations
- Build factory configurations for multi-instance service deployment
- Manage service dependencies with cardinality and policy options

## Domain Knowledge Required
### Technical Foundation
- OSGi framework fundamentals (bundles, services, lifecycle, class loading)
- Declarative Services (DS) annotations (@Component, @Reference, @Activate, @Deactivate)
- Configuration Admin service and metatype specification
- Service registry (service ranking, targeting, filtering)

### AEM-Specific Context
- AEM's OSGi container (Apache Felix) and its console
- Sling-specific annotations (@SlingServlet, @Model integration with OSGi)
- AEM run modes and configuration resolution (/apps/config.author, config.publish)
- Service User Mapper and ResourceResolverFactory usage
- OSGi configuration deployment via /apps/config/ nodes

## Implementation Approach
### Step 1: Service Design
Plan the service interface and implementation architecture.
- Define service interface with clear contract (methods, exceptions, return types)
- Determine if multiple implementations needed (strategy pattern)
- Plan configuration parameters (what should be externally configurable)
- Identify dependencies (other services, ResourceResolver, external systems)

### Step 2: Implementation
Build the service component with proper annotations.
- Create interface in API package, implementation in impl package
- Annotate implementation with @Component(service = ServiceInterface.class)
- Implement @Activate/@Deactivate for lifecycle management
- Use @Reference for dependency injection with appropriate cardinality
- Handle service unavailability gracefully (dynamic references)

### Step 3: Configuration
Make the service externally configurable.
- Create @ObjectClassDefinition for configuration structure
- Annotate component with @Designate for config binding
- Implement @Activate with ComponentContext/config parameter injection
- Support factory configurations where multiple instances needed
- Deploy default configurations under /apps/config/

### Step 4: Run Mode Configuration
Support environment-specific behavior.
- Create config nodes for each environment (author, publish, dev, stage, prod)
- Use run mode-specific configurations for endpoints, timeouts, feature flags
- Implement configuration merge behavior (most-specific wins)
- Document which configurations vary by environment

### Step 5: Testing & Deployment
Validate service behavior and deploy safely.
- Write unit tests with mocked dependencies (Mockito)
- Test with OSGi mock context for integration scenarios
- Verify service registration in Felix console after deployment
- Validate configuration binding and default values

## Quality Checklist
- [ ] Service interface defined separately from implementation
- [ ] @Component annotation specifies service interface explicitly
- [ ] All dependencies use @Reference with appropriate policy
- [ ] Configuration properly externalized (no hardcoded values)
- [ ] Service handles activation/deactivation cleanly (resource cleanup)
- [ ] Null-safe handling when optional references are unavailable
- [ ] Service registered and visible in Felix console
- [ ] Unit tests cover all public methods and edge cases

## Related Skills
- aem-sling-servlets-event-listeners (Sling-specific services)
- aem-unit-integration-testing (testing OSGi services)
- aem-security-access-control (service user for services)

## Example Use Cases
1. **External API Client Service:** Build a configurable HTTP client service with connection pooling, retry logic, circuit breaker, and factory configuration for multiple API endpoints, injectable into Sling Models and servlets.
2. **Content Validation Service:** Implement a service with multiple validation strategy implementations (SEO, accessibility, brand compliance) selectable via service ranking and configuration, triggered from workflow steps.
3. **Cache Management Service:** Create a multi-level cache service with configurable TTL, size limits, and eviction policies using factory configurations for different cache instances (product data, user profiles, translations).

## Notes
- Use Declarative Services annotations (org.osgi.service.component.annotations), not Felix SCR annotations (deprecated)
- Always close ResourceResolvers obtained from ResourceResolverFactory in services (try-with-resources)
- Service ranking determines which implementation is used when multiple exist — higher number wins
- Factory configurations allow multiple instances of the same service with different configs
