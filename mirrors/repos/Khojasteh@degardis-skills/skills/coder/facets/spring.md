---
title: Spring
category: Framework and library
x-claim-provenance:
- claim: In proxy mode, which is the default, only external method calls coming in through the proxy are intercepted, so self-invocation of a @Transactional method within the target object does not lead to an actual transaction at run time; AspectJ mode weaves the target class to cover any kind of method call.
  source: https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html
- claim: By default Spring marks a transaction for rollback only for RuntimeException and Error, and checked exceptions thrown from a transactional method do not cause a rollback unless rollback rules such as rollbackFor name them.
  source: https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/rolling-back.html
- claim: If Spring Security is on the classpath, Spring Boot auto-configures security for the entire web application, actuator endpoints included, until the application configures security itself.
  source: https://docs.spring.io/spring-boot/reference/web/spring-security.html
---

The configured Spring, Boot, Java, build, web stack, security, data, messaging, cache, and deployment versions decide which annotations and starters apply. Auto-configuration, conditional beans, generated metadata, actuator endpoints, native-image or ahead-of-time settings, and platform configuration are part of the effective application; adding Spring Security to the classpath, for example, changes what every web endpoint, actuator endpoints included, requires until the application configures security itself, and that auto-configured default is established for the resolved Boot version rather than assumed. Spring upgrade compatibility spans Java, servlet and enterprise APIs, managed libraries, and the test stack; release property-migration diagnostics expose renamed or relocated configuration, while temporary migration aids remain transition state until that configuration is reconciled.

Bean ownership and scope, configuration precedence, proxy boundary, validation, authentication and authorization, transaction propagation, lazy loading, serialization, retries, async work, events, and application lifecycle are behavioral contracts. The proxy boundary decides whether annotations take effect at all: in the default proxy mode only calls that arrive through the proxy are intercepted, so a `@Transactional` method invoked from another method of the same bean runs without a transaction. Rollback has a default of its own, since only unchecked exceptions and errors roll a transaction back, and a checked exception lets it commit unless a rollback rule names that exception. Behavior runs through component scanning, bean creation and scope, proxy interception, self-invocation, configuration binding, filter and security chains, validation, transactions, ORM sessions, events, scheduling, messaging, retry, cache, and shutdown.

Code is also referenced indirectly, through:

- annotations, bean names, and qualifiers
- expression strings, configuration property keys, and profiles
- repository queries and ORM mappings
- generated sources, reflection hints, and starter-provided registrations

Characteristic failure modes are scoped state captured by singletons, transaction annotations bypassed at the actual call boundary, lazy access outside a session, N+1 queries, lost security context, retrying side effects, and default security behavior.

Evidence scope can be a unit, slice, or application context depending on which real container, proxy, web, transaction, messaging, or persistence boundary must remain present. Behavioral evidence covers bean scope and conditions, configuration precedence, validation, allowed and denied security paths, transaction propagation, query shape, serialization, retry and acknowledgment, async context, and lifecycle cleanup. Direct-call, proxy, request, transaction-commit, listener, scheduled, and asynchronous boundaries are distinct failure surfaces, and success at one does not establish another. Performance evidence comes from a warmed production profile, and an optimization must preserve proxy semantics, transaction ownership, shared-bean thread safety, pool limits, and startup behavior.
