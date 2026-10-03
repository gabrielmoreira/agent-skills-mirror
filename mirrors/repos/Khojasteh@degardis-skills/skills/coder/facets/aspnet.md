---
title: ASP.NET
category: Framework and library
description: Classic .NET Framework ASP.NET, including System.Web, Web Forms, MVC, and Web API, rather than ASP.NET Core.
x-claim-provenance:
- claim: Access to ASP.NET session state is exclusive per session; concurrent requests for the same session run one after another, and read-only session requests take no exclusive lock but can wait for a read-write lock.
  source: https://learn.microsoft.com/en-us/previous-versions/ms178581(v=vs.140)
  scope: ASP.NET on .NET Framework; archived documentation dated 2014-12-04.
- claim: Modifying Global.asax or Web.config restarts the application and loses values in application state and session state, and session modes other than InProc require primitive or serializable session values.
  source: https://learn.microsoft.com/en-us/previous-versions/ms178581(v=vs.140)
  scope: ASP.NET on .NET Framework; archived documentation dated 2014-12-04.
- claim: ASP.NET merges Machine.config, the root Web.config, and site, application, and subdirectory Web.config files, computes settings per requested virtual path, and restarts the application on a configuration change unless the section sets restartOnExternalChanges to false or uses configSource.
  source: https://learn.microsoft.com/en-us/previous-versions/aspnet/ms178685(v=vs.100)
  scope: ASP.NET 4 documentation; archived, dated 2014-10-22.
- claim: The behavior of async and await in ASP.NET is undefined unless httpRuntime targetFramework 4.5 enables the await-friendly asynchronous pipeline.
  source: https://devblogs.microsoft.com/dotnet/all-about-httpruntime-targetframework/
  scope: .NET blog post by Levi Broderick, 2012-11-19; .NET Framework 4.5.
---

Classic ASP.NET behavior is assembled from more than the application's own code. Configuration merges from Machine.config and the root Web.config on the server, through site and application Web.config files, down to subdirectory files, and is computed for each request from the requested URL's virtual path, so a setting can come from outside the repository or change with how virtual directories are mapped. IIS hosting, the target framework, the application model (Web Forms, MVC, or Web API), the authentication provider, and the session and cache stores decide which APIs and migration paths exist.

Much of a request's state is ambient rather than passed in: request context, application and server state, view and control state, and the synchronization context. Code that looks self-contained can depend on it, and its behavior, like the request pipeline's, is observable only in the configured IIS or equivalent host. The behavior of `async` and `await` is undefined unless the application opts into the await-friendly pipeline that `<httpRuntime targetFramework="4.5" />` enables.

Session state serializes work: requests that share a session and need read-write access run one at a time, and a read-only request can still wait behind a read-write one. The default in-process session and application state live in the worker process and are lost when the application restarts, which a change to Web.config or Global.asax triggers. Session modes other than in-process require every session value to be a primitive or serializable type, so moving to an out-of-process store can break values that worked before.

A move to ASP.NET Core is settled item by item: authentication tickets, machine-key-protected values, session state, membership hashes, URLs, and any Web Forms lifecycle behavior each survive or are deliberately withdrawn. While both applications run, a reverse proxy or route split, a shared session store, and shared authentication tickets are the usual bridges between them.

Behavior is also reached through configuration and hosting rather than code:

- HTTP modules and handlers, handler mappings, and MIME settings
- System.Web ambient access and server path mapping
- application state and uploaded files
- rewrite rules and configuration transforms
- machine-level configuration and host authentication outside the application tree

Evidence for routing, model binding, authentication and authorization, antiforgery, session, cache, view state, serialization, async completion, and cleanup holds only for the framework and host settings it ran under, so each supported combination is its own evidence. Performance evidence comes from a release build of a warmed application; view-state size, session serialization and locking, synchronous use of request threads, per-request allocation, and application recycling are the usual costs.
