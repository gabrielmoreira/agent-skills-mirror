# web3

High-level web3 surface built on top of the [`wallet`](wallet/README.md)
module. The wallet stays basic (keys, balances, transfers, tx inspection); this
module focuses on EVM/Solana(/BTC) dapp interactions: swaps, bridges, and
generic dapp contract calls.

Quotes and ready-to-sign unsigned transactions come from the openhuman
backend's deBridge proxy (`/agent-integrations/crypto/{routes,swap,bridge}`,
backend PR #852). This module only resolves the caller's wallet address,
forwards the request, and stores a confirm-then-execute quote. On execute it
hands the unsigned transaction to the wallet's crate-internal signing
primitives: `wallet::sign_and_broadcast_evm` for an EVM `to`/`data`/`value`
transaction, or `wallet::sign_and_broadcast_solana` for a hex
`VersionedTransaction`. Private keys never leave the wallet.

## Five family members

Three members (`swap`, `bridge`, `dapp`) are documented here; `wallet` and
`x402` each have their own README:

| Module | Namespace | Purpose |
| --- | --- | --- |
| `swap/` | `web3_swap` | Single-chain swaps via deBridge. Cross-chain requests are rejected with a pointer to `web3_bridge`. |
| `bridge/` | `web3_bridge` | Cross-chain bridges via deBridge DLN. Same-chain requests rejected. Signs and broadcasts on the source chain. |
| `dapp/` | `web3_dapp` | Generic EVM contract calls from caller-supplied calldata (no backend). |
| [`wallet/`](wallet/README.md) | `wallet` | Basic multi-chain key/account management and primitive on-chain operations. |
| [`x402/`](x402/README.md) | `x402` | HTTP-402 payment protocol: intercept, pay, retry, ledger. |

`wallet` and `x402` are declared ungated in `mod.rs`, unlike `swap`/`bridge`/
`dapp`/`ops`/etc., which are `#[cfg(feature = "web3")]`. As `mod.rs` puts it:

> Ungated family members: `wallet` and `x402` are facades in their own right.
> Each keeps its own `stub.rs` and gates its real submodules on the same
> default-ON `web3` feature. Always-compiled callers resolve through those
> stubs (`tools/impl/network/http_request.rs` calls into `x402`), so these
> declarations must NOT carry a `#[cfg]`.

## Compile-time gate (`web3` feature)

`pub mod web3;` (declared in `crates/openhuman-core/src/lib.rs`) is always
compiled: it is a facade. The real swap/bridge/dapp implementation is gated
behind the default-ON `web3` Cargo feature. When the feature is off,
`stub.rs` takes its place and exposes
`all_web3_registered_controllers` / `all_web3_controller_schemas` /
`all_web3_agent_tools` returning empty collections, so `core/all.rs` and
`tools/ops.rs` need no per-call `#[cfg]`. `cargo check --no-default-features`
is the only thing that catches drift between the real and stub signatures.

## Where the logic lives

The swap/bridge/dapp logic is in the vendored `tinywallet-web3` crate
(`vendor/tinywallet/crates/tinywallet-web3`, `crypto::service`), not here: quote
preparation, the confirm-then-execute quote store and the agent tools. This
module is the host adapter. The crate reaches OpenHuman only through seams,
implemented in `seams.rs`.

## Key files

| File | Role |
| --- | --- |
| `mod.rs` | Export-focused root: aggregates `all_web3_controller_schemas` / `all_web3_registered_controllers` / `all_web3_agent_tools` (which builds the crate's tools over the process-wide service), plus shared schema helpers. Re-exports the crate's request/quote types as `web3::types`. |
| `seams.rs` | The host implementations of the crate's seams (`HostSigner`, `HostAccounts`, `TaskLocalScope`, `HostBackend`) and the `OnceLock` holding the process-wide `WalletEngine` and `Web3Service` (`engine()`, `service()`). |
| `client.rs` | `CryptoClient`, a thin wrapper over the shared `IntegrationClient` for `/agent-integrations/crypto/*` (Bearer JWT auth, envelope unwrap). Reached through `HostBackend`. |
| `stub.rs` | Disabled facade compiled when `web3` is off; empty `all_web3_registered_controllers` / `all_web3_controller_schemas` / `all_web3_agent_tools`. See Compile-time gate above. |
| `seams_tests.rs` | Composition tests over the real wallet state, and the regression test that `TaskLocalScope` reads `APPROVAL_CHAT_CONTEXT`. |
| `stub_tests.rs` | Runs only in the disabled build; pins that the three stub entry points return empty collections. |
| `{swap,bridge,dapp}/schemas.rs` | Per-namespace RPC controllers and handlers (namespace strings are wire contracts). |

## RPC / controllers

- `web3_swap`: `quote`, `execute`, `routes` (`openhuman.web3_swap_quote`, and so on).
- `web3_bridge`: `quote`, `execute`.
- `web3_dapp`: `call`, `execute`.

Quote/call methods return a `quoteId`; the matching `*_execute` (with
`confirmed: true`) signs and broadcasts. Quotes are bound to the chat thread
that prepared them, so a leaked `quoteId` cannot be hijacked from another
session. They expire after 5 minutes, and a failed broadcast restores the
quote with a refreshed TTL.

## Agent tools

`web3_swap_quote`, `web3_swap_execute`, `web3_swap_routes`,
`web3_bridge_quote`, `web3_bridge_execute`, `web3_dapp_call`,
`web3_dapp_execute` are defined in `tinywallet_web3::tools::web3` and built over
the process-wide service by `all_web3_agent_tools()` (registered in
`crates/openhuman-core/src/tools/ops.rs`). They call the backend
per-invocation and error gracefully when the user is not signed in.

## Chain-id mapping

deBridge uses real EVM chain ids (1 ETH, 10 Optimism, 56 BNB, 137 Polygon,
8453 Base, 42161 Arbitrum) and a synthetic Solana id (`7565164`). `chain_family`
maps a deBridge id to the local signer family; ids the wallet can't sign for
are rejected at quote time.

## Wiring

- `crates/openhuman-core/src/core/all.rs`: `crate::web3::wallet::all_wallet_registered_controllers()` (around line 884), `crate::web3::all_web3_registered_controllers()` (around line 890), `crate::web3::x402::all_x402_registered_controllers()` (around line 569), each pushed onto the controller registry under `DomainGroup::Web3`.
- `crates/openhuman-core/src/tools/mod.rs` lines 59-60: `#[cfg(feature = "web3")] pub use crate::web3::wallet::tools::*;` re-exports the wallet agent tool structs.
- `crates/openhuman-core/src/tools/ops.rs`: calls `crate::web3::all_web3_agent_tools()` to register the swap/bridge/dapp agent tools, alongside the wallet and x402 tool registrations.

## Dependencies

- `tinywallet-web3` (`vendor/tinywallet/crates/tinywallet-web3`, optional, feature `tools`, enabled by the `web3` feature): the swap/bridge/dapp service, quote store and tools. Its seams are implemented in `seams.rs`.
- [`crate::web3::wallet`]: `status` (through `HostAccounts`) and `secret_material` (through `HostSigner`).
- [`crate::integrations`] (`IntegrationClient`, `build_client`): backend auth and transport, through `HostBackend`.
- `crate::security::approval::APPROVAL_CHAT_CONTEXT`: quote-owner binding, read by `TaskLocalScope`.
- `crate::core::all` / `crate::core`: RPC controller registry wiring.
- `tinywallet-bus` (optional, gated by the `web3` feature): the contract crate. It supplies the `SecretMaterial`/`TransactionSpec` wire types the signer hands to the wallet module and the `Transport` seam types.

## Notes / gotchas

- The backend injects a configurable affiliate fee (default 1%) collected on-chain by deBridge on the source chain; this module passes the quote through unchanged.
- deBridge returns a large nested object; everything not explicitly consumed is passed through as `serde_json::Value`.
- Same-chain `web3_bridge` requests and cross-chain `web3_swap` requests are rejected, mirroring deBridge's split between single-chain swaps and cross-chain DLN orders.
