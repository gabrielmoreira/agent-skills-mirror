---
title: Express
category: Framework and library
x-claim-provenance:
- claim: Starting with Express 5, route handlers and middleware that return a Promise call next(value) automatically when they reject or throw, while in Express 4 errors from asynchronous code must be passed to next explicitly; error-handling middleware takes four arguments, and calling next with an error after the response has started makes the default error handler close the connection and fail the request.
  source: https://expressjs.com/en/guide/error-handling.html
- claim: Express 5 requires Node.js 18 or later, requires a wildcard to be named (/*splat), replaces the optional ? with braces, does not support regexp characters in path strings, requires reserved characters to be escaped, and leaves req.body undefined when the body has not been parsed where Express 4 returned {}.
  source: https://expressjs.com/en/guide/migrating-5.html
- claim: With trust proxy disabled the client address comes from the socket; when enabled, req.hostname comes from X-Forwarded-Host, req.protocol from X-Forwarded-Proto, and req.ip from X-Forwarded-For starting at the first untrusted address, and with trust proxy set to true the last trusted reverse proxy must remove or overwrite those headers or a client can supply any value.
  source: https://expressjs.com/en/guide/behind-proxies.html
---

The configured Express and Node versions, module mode, router structure, middleware stack, body parsing, proxy trust, session store, error handler, and deployment topology decide which APIs apply, and the major version changes semantics that look identical in source. Express 5 requires Node.js 18 or later, requires a wildcard to be named, as in `/*splat`, replaces the optional `?` with braces, rejects regular-expression characters in path strings, and leaves `req.body` `undefined` rather than `{}` when no parser ran. Trust-proxy settings, cookie and session options, path matching, and major-version routing or error semantics are configured behavior rather than universal defaults.

Asynchronous error propagation splits most sharply by version. In Express 5 a handler or middleware that returns a rejected promise, including an `async` function that throws, reaches the error handler automatically, while in Express 4 Express never sees that error unless the code passes it to `next`. Error-handling middleware is recognized by its four parameters, and an error raised after the response has started writing can only be handed to the default handler, which closes the connection. Middleware order, mount paths, parameter and query validation, authentication and authorization, request-scoped state, asynchronous error propagation, response ownership, streaming, and cleanup are compatibility-sensitive, because handlers and security rely on them staying fixed.

Proxy trust decides who the client is: with `trust proxy` disabled, `req.ip` is the socket's peer, and once it is enabled `req.ip`, `req.protocol`, and `req.hostname` come from `X-Forwarded-For`, `X-Forwarded-Proto`, and `X-Forwarded-Host`, so the effective setting, including the resolved version's default, is established before any of them is relied on, and a blanket `true` lets a client supply any of them unless the last trusted proxy overwrites those headers.

A request's behavior runs through every matching middleware and router layer via `next` and error `next`, response completion, thrown or rejected work, aborted requests, streams, and cleanup. Behavior is also wired indirectly through:

- application and router mounts, dynamic route registration, and global middleware
- template engines and static serving
- session and cookie configuration and proxy headers
- WebSocket or upgrade handlers and background work escaping the request

Characteristic failure modes are double sends, missing returns after a response, errors lost across async boundaries, unbounded body or stream handling, unsafe redirects, and authentication state trusted before validation.

A direct handler call is evidence only when middleware and host behavior are irrelevant; otherwise the evidence boundary is an in-process or HTTP request through the configured stack. Behavioral evidence covers middleware order, route precedence, validation, allowed and denied authorization, proxy-derived identity, cookies and sessions, async failures, aborted requests, streaming backpressure, response completion, and cleanup. Performance evidence comes from the deployed configuration and real middleware stack, and an optimization must preserve event-loop responsiveness, connection behavior, request limits, and error semantics.
