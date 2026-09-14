# Providers

Implementations live in `vendor/tinychannels/src/providers/`, not here. Every flat file in this directory except `mod.rs` is a one-line `pub use tinychannels::providers::<name>::*;` (or a narrower named re-export: `signal`, `slack`, `whatsapp`, `whatsapp_web`) that keeps the stable `crate::channels::providers::<name>` path — and, via `channels/mod.rs`, the shorter `crate::channels::<name>` path — resolving after the extraction. Verify with `grep -L 'tinychannels::providers' providers/*.rs`, which should print only `mod.rs`. Provider construction is upstream too: `runtime/startup.rs` calls `tinychannels::build_channels` with a credential-hydrated config and the `channels::host` capability surface.

## Providers

| Provider | Re-exported struct | Feature gate |
| --- | --- | --- |
| `dingtalk` | `DingTalkChannel` | `channels` |
| `discord` | `DiscordChannel` | `channels` |
| `email_channel` | `EmailChannel` | `channels` |
| `imessage` | `IMessageChannel` | `channels` |
| `irc` | `IrcChannel` | `channels` |
| `lark` | `LarkChannel` | `channels` |
| `linq` | `LinqChannel` | `channels` |
| `mattermost` | `MattermostChannel` | `channels` |
| `qq` | `QQChannel` | `channels` |
| `signal` | `SignalChannel` | `channels` |
| `slack` | `SlackChannel` | `channels` |
| `telegram` | `TelegramChannel` (+ host glue, below) | `channels` |
| `whatsapp` | `WhatsAppChannel` | `channels` |
| `whatsapp_web` | `WhatsAppWebChannel` | `whatsapp-web` (forwards to `tinychannels/whatsapp-web`) |
| `yuanbao` | `YuanbaoChannel` | `channels` |

`CliChannel` is not a provider re-export: it lives in the ungated `channels/cli.rs` as a local `impl Channel`.

## Telegram is the exception

`providers/telegram/mod.rs` re-exports the transport (`session_store`, `TelegramChannel`) from `tinychannels::providers::telegram`, but keeps three pieces here because they depend on the OpenHuman event bus and runtime rather than on transport:

- `remote_control` — `/status /sessions /new` command handling (`TelegramRemoteCommand`), using the `ChannelRuntimeContext` and `web_chat::invalidate_thread_sessions`.
- `bus::TelegramRemoteSubscriber` — busy-state handler for `DomainEvent::ChannelMessageReceived` / `ChannelMessageProcessed`, subscribed to the process bus in `channels/runtime/startup/start_channels.rs`.
- `approval_surface::TelegramApprovalSurfaceSubscriber` (+ `TELEGRAM_APPROVAL_CLIENT_ID`) — the approval surface for Telegram, subscribed in the same place. `runtime/dispatch/processor.rs::channel_has_approval_surface` returns `true` only for `TELEGRAM_APPROVAL_CLIENT_ID`, so Telegram is currently the only channel whose yes/no replies reach the `ApprovalGate`.

Ported providers reach host capabilities (voice, approvals, conversation history, shutdown, event sink) through the `tinychannels::host::ProviderContext` built by `channels::host::build_provider_context` instead of calling OpenHuman internals directly; see `channels/host/mod.rs`.

## Adding a provider

Provider transport and registration (`ChannelDefinition` metadata in `tinychannels::controllers`) belong upstream in `vendor/tinychannels`. Once a provider exists there:

1. Add `pub mod <name>;` to `providers/mod.rs` and the one-line `pub use tinychannels::providers::<name>::*;` file here.
2. Add the matching `pub use providers::<name>` / `pub use <name>::<Name>Channel` pair to `channels/mod.rs`.
3. If the provider's secret lives outside `config.toml` (keyring or env), extend `hydrate_channel_credentials` in `runtime/startup/credentials.rs` the way `email` and `yuanbao` do; `tinychannels::build_channels` expects an already-hydrated config.
4. If the provider needs host-coupled glue that must stay in OpenHuman (event bus subscribers, runtime-context command handling), follow the Telegram pattern: keep the glue in a submodule here and re-export the transport from `tinychannels`.

Do not reimplement provider transport logic in this crate; `tinychannels::build_channels` and the shared config schema will not pick it up.
