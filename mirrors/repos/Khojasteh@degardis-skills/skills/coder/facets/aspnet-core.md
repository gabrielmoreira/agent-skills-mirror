---
title: ASP.NET Core
category: Framework and library
x-claim-provenance:
- claim: The order middleware appears in Program defines invocation order for requests and the reverse for responses, and that order can be critical for security, performance, and functionality.
  source: https://learn.microsoft.com/en-us/aspnet/core/fundamentals/middleware/
- claim: A scoped service created in the root container is effectively promoted to singleton; in the Development environment the default service provider checks that scoped services are not resolved from the root provider or injected into singletons; hosted services resolve scoped services through a scope they create.
  source: https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection/overview
- claim: Injecting a scoped service into conventional middleware through its constructor throws at run time because it forces the scoped service to behave like a singleton.
  source: https://learn.microsoft.com/en-us/aspnet/core/fundamentals/dependency-injection
- claim: Forwarded headers are processed only when the request's original remote IP matches KnownProxies or KnownNetworks, and ASPNETCORE_FORWARDEDHEADERS_ENABLED does not restrict accepted proxies.
  source: https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/proxy-load-balancer
- claim: Sharing authentication cookies requires a shared data protection key store, a common application name, cookie name, and scheme; ASP.NET 4.x apps share them through Microsoft.Owin.Security.Interop; .NET 6 WebApplicationBuilder normalizes the content root path so apps migrating from HostBuilder or WebHostBuilder get a different application name.
  source: https://learn.microsoft.com/en-us/aspnet/core/security/cookie-sharing
---

Middleware runs in the order `Program` adds it on the way in and in reverse on the way out, and that order is critical for security, performance, and functionality: a check placed after the component that answers the request, or a short-circuiting component placed before a check, changes what every request is allowed to do. Service lifetime is the other structural contract. A scoped service resolved from the root provider or captured by a singleton is effectively promoted to a singleton; the default service provider checks for both only in the Development environment, and a scoped service injected into conventional middleware's constructor throws at run time. Hosted and background services reach scoped dependencies through a scope they create.

Forwarded headers are honored only from the proxies and networks the forwarded-headers options name, so the effective lists, including the resolved version's default, decide whose client address and scheme the application sees: behind a real proxy those lists have to name it, and lists wider than the actual proxies let callers spoof the values. Enabling forwarding through `ASPNETCORE_FORWARDEDHEADERS_ENABLED` does not restrict which proxies are accepted.

Apps can read each other's authentication cookies only when they share the data protection key ring, the application name set with `SetApplicationName`, the cookie name, and the authentication scheme. The default application name derives from the content root path, which .NET 6's `WebApplicationBuilder` normalizes differently from `HostBuilder` or `WebHostBuilder`, so changing the hosting model without setting the name explicitly can make existing cookies and protected data unreadable. The same sharing, through `Microsoft.Owin.Security.Interop` on the classic side, is how an incremental migration from ASP.NET keeps one sign-in across both applications, alongside endpoint splits, a proxy or gateway, shared state, and an explicit condition for retiring the old host.

The configured framework and hosting versions, endpoint model, configuration providers, authentication schemes, serializer, persistence layer, and deployment host decide which APIs apply. Request handling runs through routing and model binding, validation, the separate authentication and authorization steps, DI scope capture, response completion, hosted services, and application shutdown. Request cancellation, transaction boundaries, error responses, authorization policy, background-work ownership, and server and client streaming semantics are further compatibility-sensitive contracts, and characteristic failures are work escaping request scope, missing antiforgery, tenant-boundary loss, synchronous waits, and undisposed streams or responses.

Behavior is also wired indirectly through:

- routes, attributes, and views
- options binding and configuration keys
- reflection, source generation, and EF mappings
- service registrations and background scopes
- reverse-proxy settings and data-protection stores

Evidence boundaries range from a direct service call and an in-process host to HTTP integration or a deployed host, and hosting-level evidence is necessary when middleware, routing, authentication, data protection, or transport behavior decides the result. DI scopes, configuration, identities, database state, clocks, background services, cancellation, and application lifetime need isolation between cases, and authorization evidence needs both allowed and denied paths. Performance evidence comes from a published production configuration after warmup, and an optimization must preserve scope lifetime, authorization, cancellation, serialization, connection-pool behavior, and query count.
