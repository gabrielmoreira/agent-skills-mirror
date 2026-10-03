---
title: NestJS
category: Framework and library
x-claim-provenance:
- claim: NestJS creates request-scoped provider instances for each request, propagates request scope through dependent injection trees, and documents a resulting performance cost.
  source: https://docs.nestjs.com/fundamentals/injection-scopes
- claim: A NestJS request passes through middleware, guards, interceptors before the handler, pipes, the handler, interceptors after the handler, and exception filters; middleware, guards, interceptors, and pipes run global first, then controller-level, then route-level, while filters resolve route-level first and global last.
  source: https://docs.nestjs.com/faq/request-lifecycle
- claim: Shutdown hook listeners are disabled by default; after enableShutdownHooks(), onModuleDestroy, beforeApplicationShutdown, and onApplicationShutdown respond to app.close() or termination signals such as SIGTERM, and SIGTERM never works on Windows.
  source: https://docs.nestjs.com/fundamentals/lifecycle-events
- claim: In a hybrid application, useGlobalPipes() does not set up pipes for connected microservices by default; TypeScript interfaces disappear during transpilation, so a parameter typed as an interface has the metatype Object and validation relies on class-based DTOs.
  source: https://docs.nestjs.com/pipes
---

The configured NestJS, TypeScript, reflection, validation, transport, ORM, and platform-adapter versions decide which decorators and lifecycle APIs apply. Module ownership, provider scope, injection token, request pipeline order, validation and transformation, authentication and authorization, exception mapping, serialization, transaction scope, and background or message handling are behavioral contracts.

The request pipeline has a fixed order: middleware, guards, interceptors before the handler, pipes, the handler, interceptors after it, and exception filters. Within each stage, global components run before controller-level and route-level ones, except filters, which resolve route-level first and global last. Validation depends on runtime metadata: TypeScript interfaces disappear during compilation, so a parameter typed with an interface reaches a pipe as plain `Object`, and only a class-based DTO gives validation something to check. Provider scope has a cost of its own, because a request-scoped provider is created for every request and makes every provider that depends on it request-scoped as well.

HTTP, microservice, WebSocket, queue, and scheduled transports are distinct: each has different context, acknowledgment, retry, and lifecycle behavior, and global setup does not automatically reach all of them. In a hybrid application, `useGlobalPipes()` does not cover connected microservices by default, which is one way validation ends up applied at only one transport. Shutdown is opt-in as well: `onModuleDestroy`, `beforeApplicationShutdown`, and `onApplicationShutdown` respond to termination signals only after `enableShutdownHooks()`, and `SIGTERM` never reaches them on Windows.

Behavior runs through module imports and exports, dynamic modules, provider resolution and scope, middleware, guards, interceptors, pipes, filters, decorators, reflection metadata, lifecycle hooks, and application shutdown. Code is also referenced indirectly, through:

- injection tokens and string or symbol registrations
- route metadata, validation DTOs, and global providers
- platform adapters and ORM entities
- message patterns, queue names, and generated API schemas

Characteristic failure modes are request-scoped providers captured by wider scopes, transformation mistaken for validation, authorization applied only at one transport, retrying effects, and background work without shutdown ownership.

Evidence scope ranges from a module to an application, HTTP boundary, or transport boundary depending on where the real DI and pipeline behavior occurs. Behavioral evidence covers provider scope, pipeline order, validation and transformation, allowed and denied authorization, exception shape, serialization, transactions, retries and acknowledgments, lifecycle startup and shutdown, and adapter-specific behavior. Runtime evidence depends on the configured compiler metadata and platform adapter, and a change must preserve reflection, emitted decorators, transport contracts, and resource cleanup unless altering them is part of its requested outcome. Startup and warm request handling are separate performance measurements under the configured adapter. Request-scope propagation and provider construction, validation or serialization pipes, guards and interceptors, database calls, and blocking handler work are the characteristic cost sites, and an optimization must preserve request isolation, pipeline contracts, and shutdown ownership.
