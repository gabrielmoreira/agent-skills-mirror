# web3

High-level web3 surface built **on top of** the [`wallet`](wallet/README.md)
module. The wallet stays basic (keys, balances, transfers, tx inspection); this
module focuses on EVM/Solana(/BTC) dapp interactions: **swaps**, **bridges**, and
generic **dapp contract calls**.

Quotes and ready-to-sign **unsigned transactions** come from the openhuman
backend's deBridge proxy (`/agent-integrations/crypto/{routes,swap,bridge}`,
backend PR #852). This module only resolves the caller's wallet address,
forwards the request, and stores a confirm→execute quote. On execute it hands
the unsigned transaction to the wallet's crate-internal signing primitives —
`wallet::sign_and_broadcast_evm` (EVM `to`/`data`/`value`) or
`wallet::sign_and_broadcast_solana` (a hex `VersionedTransaction`) — so private
keys never leave the wallet.

## Five family members

Three members (`swap`, `bridge`, `dapp`) are documented here; `wallet` and
`x402` each have their own README:

| Module | Namespace | Purpose |
| --- | --- | --- |
| `swap/` | `web3_swap` | Single-chain swaps via deBridge. Cross-chain requests are rejected with a pointer to `web3_bridge`. |
| `bridge/` | `web3_bridge` | Cross-chain bridges via deBridge DLN. Same-chain requests rejected. Signs+broadcasts on the **source** chain. |
| `dapp/` | `web3_dapp` | Generic EVM contract calls from caller-supplied calldata (no backend). |
| [`wallet/`](wallet/README.md) | `wallet` | Basic multi-chain key/account management and primitive on-chain operations. |
| [`x402/`](x402/README.md) | `x402` | HTTP-402 payment protocol: intercept, pay, retry, ledger. |

`wallet` and `x402` are declared *ungated* in `mod.rs`, unlike `swap`/`bridge`/
`dapp`/`ops`/etc., which are `#[cfg(feature = "web3")]`. As `mod.rs` puts it:

> Ungated family members: `wallet` and `x402` are facades in their own
> right — each keeps its own `stub.rs` and gates its real submodules on the
> same default-ON `web3` feature. Always-compiled callers resolve through
> those stubs (`tools/impl/network/http_request.rs` -> `x402`), so these
> declarations must NOT carry a `#[cfg]`.

## Compile-time gate (`web3` feature)

`pub mod web3;` (declared in `crates/openhuman-core/src/lib.rs`) is ALWAYS
compiled — it is a facade. The real swap/bridge/dapp implementation is gated
behind the default-ON `web3` Cargo feature. When the feature is off,
`stub.rs` takes its place and exposes
`all_web3_registered_controllers` / `all_web3_controller_schemas` /
`all_web3_agent_tools` returning empty collections, so `core/all.rs` and
`tools/ops.rs` need no per-call `#[cfg]`. `cargo check --no-default-features`
is the only thing that catches drift between the real and stub signatures.

## Key files

| File | Role |
| --- | --- |
| `mod.rs` | Export-focused root: aggregates `all_web3_controller_schemas` / `all_web3_registered_controllers` / `all_web3_agent_tools`, plus shared schema/tool helpers. |
| `types.rs` | deBridge chain-id ↔ local signer mapping (`chain_family`, `DEBRIDGE_SOLANA_CHAIN_ID`), request params, `UnsignedTx`, `Web3QuoteKind`. |
| `client.rs` | `CryptoClient` — thin wrapper over the shared `IntegrationClient` for `/agent-integrations/crypto/*` (Bearer JWT auth, envelope unwrap). |
| `store.rs` | In-memory prepared-quote store (TTL'd, capped, chat-thread owner-bound like the wallet) + the shared confirm→execute path. |
| `ops.rs` | Shared op logic: `routes`, `quote_swap`, `quote_bridge`, `prepare_dapp_call` (address defaulting, backend call, unsigned-tx extraction). |
| `stub.rs` | Disabled facade compiled when `web3` is off; empty `all_web3_registered_controllers` / `all_web3_controller_schemas` / `all_web3_agent_tools`. See Compile-time gate above. |
| `web3_tests.rs` | `#[cfg(all(test, feature = "web3"))]` tests for `chain_family` mapping and the quote store's confirm/execute gate. |
| `ops_tests.rs` | Tests for the shared op logic in `ops.rs` (unsigned-tx extraction, dapp/swap/bridge param rejection). |
| `stub_tests.rs` | Runs only in the disabled build; pins that the three stub entry points return empty collections. |
| `{swap,bridge,dapp}/schemas.rs` | Per-namespace RPC controllers + handlers. |
| `{swap,bridge,dapp}/tools.rs` | Per-namespace agent tools. |

## RPC / controllers

- `web3_swap`: `quote`, `execute`, `routes` (`openhuman.web3_swap_quote`, …).
- `web3_bridge`: `quote`, `execute`.
- `web3_dapp`: `call`, `execute`.

Quote/call methods return a `quoteId`; the matching `*_execute` (with
`confirmed: true`) signs and broadcasts. Quotes are bound to the chat thread
that prepared them (no cross-session hijack of a leaked `quoteId`), TTL'd at
5 minutes, and restored with a refreshed TTL on broadcast failure.

## Agent tools

`web3_swap_quote`, `web3_swap_execute`, `web3_swap_routes`,
`web3_bridge_quote`, `web3_bridge_execute`, `web3_dapp_call`,
`web3_dapp_execute` (registered in `crates/openhuman-core/src/tools/ops.rs`). They call the
backend per-invocation and error gracefully when the user is not signed in.

## Chain-id mapping

deBridge uses real EVM chain ids (1 ETH, 10 Optimism, 56 BNB, 137 Polygon,
8453 Base, 42161 Arbitrum) and a synthetic Solana id (`7565164`). `chain_family`
maps a deBridge id to the local signer family; ids we can't sign for are
rejected at quote time.

## Wiring

- `crates/openhuman-core/src/core/all.rs`: `crate::web3::wallet::all_wallet_registered_controllers()` (~line 884), `crate::web3::all_web3_registered_controllers()` (~line 890), `crate::web3::x402::all_x402_registered_controllers()` (~line 569) — each pushed onto the controller registry under `DomainGroup::Web3`.
- `crates/openhuman-core/src/tools/mod.rs` lines 59-60: `#[cfg(feature = "web3")] pub use crate::web3::wallet::tools::*;` re-exports the wallet agent tool structs.
- `crates/openhuman-core/src/tools/ops.rs`: calls `crate::web3::all_web3_agent_tools()` to register the swap/bridge/dapp agent tools, alongside the wallet and x402 tool registrations.

## Dependencies

- [`crate::web3::wallet`] — `sign_and_broadcast_evm` / `sign_and_broadcast_solana` (crate-internal), `status` for address resolution, `EvmNetwork` / `WalletChain`.
- [`crate::integrations`] (`IntegrationClient`, `build_client`) — backend auth + transport.
- `crate::security::approval::APPROVAL_CHAT_CONTEXT` — quote-owner binding.
- `crate::core::all` / `crate::core` — RPC controller registry wiring.
- `tinywallet-bus` (`crates/openhuman-core/Cargo.toml` ~line 864, optional, gated by the `web3` feature; features `btc`, `evm`, `solana`, `tron`, `keccak`, `net`, `wire`, `eip712`, `abi`, `tx-codec`) — not imported by `web3/*.rs` itself, but the contract crate its `wallet/` and `x402/` members build on: address validation, the `SecretMaterial`/`TransactionSpec` wire types handed to the wallet module, the `Transport` seam, the EIP-712/ERC-20 encoders used by x402, and the Tron verifier.

## Notes / gotchas

- The backend injects a configurable affiliate fee (default 1%) collected on-chain by deBridge on the source chain; this module passes the quote through unchanged.
- deBridge returns a large nested object; everything not explicitly consumed is passed through as `serde_json::Value`.
- Same-chain `web3_bridge` requests and cross-chain `web3_swap` requests are rejected (mirrors deBridge's single-chain swap vs. cross-chain DLN split).
