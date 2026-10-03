---
title: WordPress
category: Runtime and platform
x-claim-provenance:
- claim: WordPress nonces should never be relied on for authentication, authorization, or access control, functions are protected with current_user_can(), and a nonce is not single-use but remains valid for a window of time.
  source: https://developer.wordpress.org/apis/security/nonces/
- claim: WP-Cron checks the list of scheduled tasks on page loads and does not run constantly like system cron, so a task scheduled for a time runs only when a later page load occurs.
  source: https://developer.wordpress.org/plugins/cron/
- claim: Output is best escaped as late as possible, ideally as the data is output, with context-specific functions such as esc_html(), esc_attr(), esc_url(), esc_js(), and wp_kses().
  source: https://developer.wordpress.org/apis/security/escaping/
---

The configured WordPress and PHP versions, active theme and plugins, multisite mode, database prefix, caching layers, filesystem ownership, scheduler, REST use, and hosting decide which APIs apply. Hook and priority, capability and identity, nonce use, validation and output escaping, query ownership, REST permission, content representation, cache invalidation, schema evolution, activation, deactivation, uninstall, and recovery are behavioral contracts.

A nonce establishes intent, not permission: a WordPress nonce stays valid for a window the resolved version defines, can be reused within it, and is never an authorization check, which is what `current_user_can()` is for. Output escaping belongs at the point of output and depends on context, because `esc_html`, `esc_attr`, `esc_url`, `esc_js`, and `wp_kses` each make a value safe for one kind of place only. WP-Cron is triggered by page loads rather than by a clock, so a scheduled event runs only when traffic arrives after its due time, and on a quiet site it runs late.

In a move, content and public URLs are contracts: posts, blocks and shortcodes, media, metadata and options, users and hashes, taxonomies, menus, feeds, sitemaps, redirects, and client endpoints.

Behavior runs through actions and filters, global state, capability checks, nonce verification, sanitization and context-specific escaping, prepared queries, REST routes, multisite boundaries, option autoloading, cron, object and page caches, and activation and uninstall hooks. Behavior is also referenced indirectly, through:

- hook registration and priority, plugin load order, and theme hierarchy
- shortcodes and blocks embedded in content
- custom types and taxonomies, metadata keys, and rewrite rules
- scheduled events and generated image sizes

Characteristic failure modes are state-changing endpoints without both capability and intent checks, SQL or markup crossing unstructured boundaries, per-request global mutation, stale caches, repeated cron effects, and cleanup that could touch another site.

Evidence comes from an isolated WordPress installation and database, because tests run against a real site change its content, users, and options, and hooks, globals, users, content, options, caches, cron, and schema changes are reset between cases. Behavioral evidence covers priorities, capabilities, nonces, sanitization and escaping, prepared queries, REST permissions, multisite isolation, content compatibility, activation, deactivation, and uninstall, cache freshness, and scheduled work. Performance evidence depends on the production plugin, theme, and cache set, with query and hook counts, autoloaded options, outbound calls, scheduled work, and public URL behavior as the relevant cost surfaces.
