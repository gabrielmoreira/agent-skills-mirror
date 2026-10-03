---
title: Flask
category: Framework and library
x-claim-provenance:
- claim: Flask's session is implemented on top of cookies signed cryptographically, so the user can look at the contents of the cookie but not modify it without the secret key used for signing.
  source: https://flask.palletsprojects.com/en/stable/quickstart/
  scope: Flask 3.1.x documentation.
- claim: Unless customized, Flask enables Jinja autoescaping for templates ending in .html, .htm, .xml, .xhtml, and .svg rendered with render_template() and for all strings rendered with render_template_string(), and a template can opt in or out with the autoescape tag.
  source: https://flask.palletsprojects.com/en/stable/templating/
  scope: Flask 3.1.x documentation.
- claim: The request is not active while a streamed response's generator runs, because the view has already returned, so accessing it raises RuntimeError unless the generator is wrapped with stream_with_context(); headers cannot change after streaming starts, so the session must not be modified in the generator.
  source: https://flask.palletsprojects.com/en/stable/patterns/streaming/
- claim: Werkzeug's ProxyFix middleware should be used only when the application is actually behind a proxy and configured with the number of proxies that set each header, because incoming headers can be faked and a wrong configuration can be a security issue.
  source: https://flask.palletsprojects.com/en/stable/deploying/proxy_fix/
---

The configured Flask, Werkzeug, template engine, extension, and server versions, application factory, blueprint layout, configuration sources, session mechanism, and deployment host define the Flask environment. Extension initialization order, secret and signing configuration, proxy trust, CLI commands, and host behavior are project configuration rather than framework defaults, and the defaults that do exist are narrower than they look. The default session is a signed cookie that the user can read but not modify without the secret key, so its contents are not confidential. Werkzeug's `ProxyFix` trusts forwarded headers only for the number of proxies it is configured with, and applied where no proxy exists, or with the wrong count, it lets a client forge the values those headers carry.

Application and request context ownership, route and blueprint registration, validation, authentication and authorization, session and cookie behavior, template escaping, database transaction scope, and error handling are behavioral contracts. Context is the easiest to lose: a streamed response's generator runs after the view has returned, so `request` is no longer active there and raises `RuntimeError` unless the generator is wrapped in `stream_with_context`, and because the headers are already sent, the generator cannot change the session. Autoescaping covers only templates ending in `.html`, `.htm`, `.xml`, `.xhtml`, or `.svg` and strings passed to `render_template_string`, so a template with any other extension renders values unescaped unless it opts in.

Control flow, lifecycle, and ownership run through context push and teardown, local proxies, before/after request handlers, error handlers, streaming responses, sessions, templates, database sessions, signals, background work, and extension cleanup. Behavior is also referenced indirectly, through:

- blueprint names and prefixes and endpoint strings
- application-factory registration and configuration keys
- template references, CLI commands, and extension state
- proxy headers and WSGI server settings

Characteristic failure modes are global state that crosses application instances or tests, work that outlives request context, unsafe template or redirect inputs, and database work committed outside the intended owner.

The application factory with isolated configuration and context is the base evidence boundary, and a request client or hosted boundary is needed where routing, sessions, middleware, templates, or server behavior matters. Behavioral evidence covers blueprint registration, context teardown, validation, allowed and denied authorization, cookies and sessions, templates, error handlers, streaming, transactions, CLI commands, and extension state. Performance evidence comes from the production WSGI configuration and a warmed application, and an optimization must preserve context ownership, worker model, session behavior, and cleanup.
