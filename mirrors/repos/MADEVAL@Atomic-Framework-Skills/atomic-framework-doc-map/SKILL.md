---
name: atomic-framework-doc-map
description: "Use when you need a fast cross-reference of all 44 Atomic Framework documentation files to find which doc covers which subsystem, feature, or integration."
argument-hint: "Find docs for any subsystem, feature, or integration by name"
user-invocable: true
---

# Atomic Framework Documentation Map

## When to Use
- Looking for the right doc file before editing a subsystem.
- Finding all docs related to a feature family.
- Cross-referencing a doc to the engine path that implements it.

## Cross-Reference Table

| Category | Doc file | Engine path | Skill |
|---|---|---|---|
| Architecture | `docs/README.md` | all | `atomic-framework-overview` |
| Bootstrap | `docs/applications.md` | `Core/App.php`, `App/*` | `atomic-framework-core` |
| Config | `docs/config.md` | `Core/Config/*` | `atomic-framework-core` |
| Prefly | `docs/prefly.md` | `Core/Prefly.php` | `atomic-framework-core` |
| Request | `docs/request.md` | `Core/Request.php`, `Core/Methods.php` | `atomic-framework-core` |
| Middleware | `docs/middleware.md` | `Core/Middleware/*` | `atomic-framework-core` |
| Logging | `docs/log.md` | `Core/Log.php`, `Core/LogChannel.php` | `atomic-framework-core` |
| Error handling | `docs/errorhandler.md` | `Core/ErrorHandler.php` | `atomic-framework-core` |
| Security | `docs/security.md` | `Core/Crypto.php`, `Core/Guard.php` | `atomic-framework-core` |
| Database | `docs/database.md` | `Core/ConnectionManager.php` | `atomic-framework-core` |
| Migrations | `docs/migrations.md` | `Core/Migrations.php`, `CLI/Migrations.php` | `atomic-framework-core`, `atomic-framework-cli-api` |
| Model | `docs/model.md` | `App/Model.php`, `Validator/*` | `atomic-framework-data` |
| Atomic Core ref | `docs/atomic_core.md` | `Core/` (all) | `atomic-framework-core` |
| Atomic Methods | `docs/atomic_methods.md` | `Core/Methods.php`, `Support/helpers.php` | `atomic-framework-core` |
| PDF export | `docs/atomic_pdf.md` | `Files/PDF.php` | `atomic-framework-data` |
| XLS export | `docs/atomic_xls.md` | `Files/XLS.php` | `atomic-framework-data` |
| CLI | `docs/cli.md` | `CLI/*` | `atomic-framework-cli-api` |
| Events | `docs/event.md` | `Event/Event.php` | `atomic-framework-event-hook-lang-mail` |
| Hooks | `docs/hook.md` | `Hook/Hook.php` | `atomic-framework-event-hook-lang-mail` |
| i18n | `docs/i18n.md` | `Lang/I18n.php` | `atomic-framework-event-hook-lang-mail` |
| Mailer | `docs/mailer.md` | `Mail/Mailer.php` | `atomic-framework-event-hook-lang-mail` |
| Notifier | `docs/notifier.md` | `Mail/Notifier.php` | `atomic-framework-event-hook-lang-mail` |
| Template | `docs/template.md` | F3 Template engine | `atomic-framework-theme` |
| Theme | `docs/theme.md` | `Theme/Theme.php` | `atomic-framework-theme` |
| Head | `docs/head.md` | `Theme/Head.php` | `atomic-framework-theme` |
| Assets | `docs/assets.md` | `Theme/Assets.php` | `atomic-framework-theme` |
| OpenGraph | `docs/opengraph.md` | `Theme/OpenGraph.php`, `Theme/Schema.php` | `atomic-framework-theme` |
| Redactor | `docs/redactor.md` | `Core/Redactor.php`, `Theme/Redactor.php` | `atomic-framework-core`, `atomic-framework-theme` |
| Session | `docs/session.md` | `Auth/Session.php`, `Session/SessionManager.php` | `atomic-framework-mutex-session` |
| Mutex | `docs/mutex.md` | `Mutex/Mutex.php` | `atomic-framework-mutex-session` |
| Nonce | `docs/nonce.md` | `Tools/Nonce.php` | `atomic-framework-mutex-session` |
| Transient | `docs/transient.md` | `Tools/Transient.php`, `Cache/*` | `atomic-framework-mutex-session` |
| Queue | `docs/queue.md` | `Queue/Managers/Manager.php` | `atomic-framework-queue-scheduler-telemetry` |
| Scheduler | `docs/scheduler.md` | `Scheduler/Scheduler.php` | `atomic-framework-queue-scheduler-telemetry` |
| Telemetry | `docs/telemetry.md` | `Telemetry/*` | `atomic-framework-queue-scheduler-telemetry` |
| Plugins | `docs/plugins.md` | `App/Plugin.php`, `App/PluginManager.php` | `atomic-framework-plugins` |
| Monopay | `docs/plugins/monopay.md` | `Plugins/Monopay/*` | `atomic-framework-plugins` |
| WordPress | `docs/plugins/wordpress.md` | `Plugins/WordPress/*` | `atomic-framework-plugins` |
| WooCommerce | `docs/plugins/woocommerce.md` | `Plugins/WooCommerce/*` | `atomic-framework-plugins` |
| RSS Reader | `docs/plugins/rss-reader.md` | `Plugins/RssReader/*` | `atomic-framework-plugins` |
| AI Connector | `docs/ai_connector.md` | `Tools/AIConnector.php` | `atomic-framework-tools-websockets` |
| WebSockets | `docs/websockets.md` | `WebSockets/Server.php` | `atomic-framework-tools-websockets` |
| Telegram | `docs/telegram.md` | `Tools/Telegram.php`, `Auth/TelegramAuth.php` | `atomic-framework-tools-websockets`, `atomic-framework-app-auth` |
| Testing | `docs/testing_guide.md` | `tests/` | all |

## Skills Index

| Skill | Focus |
|---|---|
| `atomic-framework-overview` | Architecture, modules, bootstrap, routing map |
| `atomic-framework-core` | Bootstrap, config, middleware, logging, routing, crypto, migrations |
| `atomic-framework-data` | Models, validation, enums, exceptions, file export, helpers |
| `atomic-framework-app-auth` | Controllers, app models, auth, session, OAuth |
| `atomic-framework-cli-api` | CLI commands, API, scaffolding, console output |
| `atomic-framework-event-hook-lang-mail` | Events, hooks, filters, i18n, mail, notifier |
| `atomic-framework-mutex-session` | Mutex, session, nonce, transient |
| `atomic-framework-queue-scheduler-telemetry` | Queue, scheduler, telemetry panel |
| `atomic-framework-theme` | Theme, head, assets, OpenGraph, schema |
| `atomic-framework-plugins` | Plugin lifecycle, PluginManager, built-in integrations |
| `atomic-framework-tools-websockets` | AI Connector, WebSocket server, Telegram |
| `atomic-framework-doc-map` | This index |

## Guardrails
- If a doc file exists for a subsystem, read it before making assumptions about behavior.
- Docs in `docs/plugins/` cover integration-specific APIs; treat them as supplementary.
- `docs/testing_guide.md` applies to all subsystems when writing tests.
