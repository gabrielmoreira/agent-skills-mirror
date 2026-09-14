# wallet

Core-owned local multi-chain crypto wallet, deliberately **basic**: key/account management plus the primitive on-chain operations. Owns onboarding metadata (consent + derived per-chain account addresses), secret material at rest (an encrypted recovery phrase stored in the OS keychain or workspace JSON), and the agent-facing surface: address + balance reads, network/asset catalogs, chain readiness, a prepare-then-confirm-then-execute flow for **native sends and token transfers** (ERC20 / SPL / TRC20 / BEP20), transaction broadcast, and read-only transaction inspection (status, receipt, lookup) across EVM (Ethereum + Base/Arbitrum/Optimism/Polygon/BNB Chain), Bitcoin (P2WPKH), Solana (native + SPL), and Tron (native + TRC20). This process decrypts the recovery phrase and hands it, as a `tinywallet_bus::wire::SecretMaterial`, to the loaded `tinywallet` native module (`crate::modules::wallet`), which derives the key, signs, and returns the raw signed bytes; the core then broadcasts. The binary never assembles a private key outside `cfg(test)`.

Higher-level DeFi affordances (swaps, bridges, generic dapp/contract calls) live in the separate [`web3`](../README.md) module, which builds on the wallet's **crate-internal** `sign_and_broadcast_evm` / `sign_and_broadcast_solana` primitives. They are not part of the wallet's agent / RPC surface.

## Compile-time gate (`web3` feature)

`pub mod wallet;` in `web3/mod.rs` is ALWAYS compiled — it is a facade. The real
implementation (`ops`, `execution`, `defaults`, `abi`, `chains`, `schemas`,
`tools`, `transport`) is gated behind the default-ON `web3` Cargo feature
(shared with `web3` and `web3::x402`). When the feature is off, `stub` takes
its place and mirrors the subset of the public surface that always-on / other-
gated callers depend on — `WALLET_NOT_CONFIGURED_MESSAGE`, `status`,
`secret_material`, `WalletChain`, `prepare_transfer`, `execute_prepared`, the
prepare/execute param + result types, `solana_cluster` / `SolanaCluster`,
`prepared_quotes_for_test`, and the controller-registration entry points
(`all_wallet_registered_controllers`, `all_wallet_controller_schemas`) —
with no-op / disabled-error bodies. Signatures must match the real ones
exactly; `cargo check --no-default-features` is the only thing that catches
drift.

## Responsibilities

- Persist wallet onboarding state (consent flag, mnemonic word count, setup source, exactly one derived account per supported chain) and the encrypted recovery phrase.
- Prefer the OS keychain for the encrypted mnemonic; transparently migrate the secret out of `wallet-state.json` into the keychain on load/save, and back to JSON when the keychain is unavailable (headless).
- Expose read-only wallet info: status, per-account native balances (EVM live, others provider-gated), supported-asset catalog, per-network defaults (RPC/explorer/capability flags), and per-chain readiness.
- Build prepared-transaction quotes (validated, fee-estimated, TTL'd) that must be explicitly confirmed before execution.
- Sign and broadcast confirmed quotes per chain; restore (and TTL-refresh) the quote on failure so it stays retryable.
- Bind each quote to the chat thread that prepared it so a leaked `quote_id` in a shared channel can't be hijacked from another agent session.
- Expose six agent tools (`wallet_status`, `wallet_chain_status`, `wallet_prepare_transfer`, `wallet_tx_status`, `wallet_tx_receipt`, `wallet_lookup_tx`) and thirteen `wallet.*` RPC controllers.
- Provide crate-internal `sign_and_broadcast_evm` / `sign_and_broadcast_solana` primitives for the `web3` layer (sign+broadcast an externally-built unsigned transaction). Not exposed to the agent / RPC surface.

## Key files

| File | Role |
| --- | --- |
| `crates/openhuman-core/src/web3/wallet/mod.rs` | Export-focused module root; module docstring, `mod`/`pub use` re-exports. |
| `crates/openhuman-core/src/web3/wallet/ops.rs` | Onboarding metadata + secret persistence: `WalletChain`/`WalletAccount`/`WalletStatus` types, `setup`/`status`/`reveal_recovery_phrase`, atomic `wallet-state.json` writes (temp-file + fsync), corrupt-state quarantine, keychain load/save/migrate, `validate_setup`, and `secret_material` (crate-internal) used by chain signers. |
| `crates/openhuman-core/src/web3/wallet/execution.rs` | Execution surface: balances/network_defaults/supported_assets/chain_status reads, `prepare_transfer`/`execute_prepared` (native + token transfers only), `tx_status`/`tx_receipt`/`lookup_tx` readers, the crate-internal `sign_and_broadcast_evm`/`sign_and_broadcast_solana` wrappers over `chains::`, the in-memory quote store (TTL'd, capped at 64), `QuoteOwner` chat-thread binding, amount/address/calldata validation, fee estimation, hex/u256 helpers. |
| `crates/openhuman-core/src/web3/wallet/defaults.rs` | `EvmNetwork` enum (chain id, default RPC, explorer base, env var), default RPC/REST URLs for BTC/Solana/Tron, env-override resolution, and per-chain/per-network asset catalogs. |
| `crates/openhuman-core/src/web3/wallet/abi.rs` | `encode_erc20_transfer` — delegates the `transfer(address,uint256)` calldata encoding to `tinywallet_bus::abi`, mapping its typed errors (`InvalidRecipient`/`InvalidAmount`) to the plain-`String` shape the RPC/tool surface uses. |
| `crates/openhuman-core/src/web3/wallet/schemas.rs` | RPC controller schemas + `handle_*` dispatchers delegating to `ops`/`execution`; `all_wallet_controller_schemas` / `all_wallet_registered_controllers`. |
| `crates/openhuman-core/src/web3/wallet/rpc.rs` | **Network transport** (not RPC controllers): shared `reqwest::Client`, JSON-RPC POST (`rpc_call`, `evm_rpc_call`, `rpc_call_to`), REST GET/POST helpers, URL redaction for logs. |
| `crates/openhuman-core/src/web3/wallet/transport.rs` | OpenHuman's implementation of the `tinywallet_bus::rpc::Transport` seam: resolves a `tinywallet_bus::rpc::NetworkId` to an endpoint (including `OPENHUMAN_WALLET_RPC_<CHAIN>` overrides), redacts URLs for logs, and reuses `rpc.rs`'s shared `reqwest` client. Classifies errors conservatively — anything it cannot prove is a transport failure is reported as `TransportError::Rpc` (authoritative) rather than `Unreachable` (retryable), so an unclassifiable error stops a failover loop instead of risking a double broadcast. |
| `crates/openhuman-core/src/web3/wallet/tools.rs` | Re-exports the six agent tool structs from `tools/`. |
| `crates/openhuman-core/src/web3/wallet/tools/status.rs` | `WalletStatusTool` (`wallet_status`). |
| `crates/openhuman-core/src/web3/wallet/tools/chain_status.rs` | `WalletChainStatusTool` (`wallet_chain_status`). |
| `crates/openhuman-core/src/web3/wallet/tools/prepare_transfer.rs` | `WalletPrepareTransferTool` (`wallet_prepare_transfer`). |
| `crates/openhuman-core/src/web3/wallet/tools/tx_query.rs` | `WalletTxStatusTool` (`wallet_tx_status`), `WalletTxReceiptTool` (`wallet_tx_receipt`), `WalletLookupTxTool` (`wallet_lookup_tx`) — share a `{chain, hash, evmNetwork?}` input and delegate to the matching `wallet::*` dispatcher. |
| `crates/openhuman-core/src/web3/wallet/chains/mod.rs` | Per-chain executor namespace; docstring of the small per-chain surface (`execute_*_quote`, `native_balance`, `validate_*_address`). |
| `crates/openhuman-core/src/web3/wallet/chains/evm.rs` | EVM path: validates addresses with `tinywallet_bus::address::evm::validate`, gathers `eth_chainId`/nonce/`eth_gasPrice`/`eth_estimateGas` over JSON-RPC, builds a legacy gas-price `tinywallet_bus::wire::TransactionSpec::Evm`, signs it in the module via `modules::wallet::sign_transaction_in_module`, and broadcasts with `eth_sendRawTransaction`. One derivation path shared across all EVM networks. Also hosts the crate-internal `sign_and_broadcast_evm`. |
| `crates/openhuman-core/src/web3/wallet/chains/btc.rs` | Bitcoin P2WPKH (BIP84) path: Esplora REST UTXO discovery, largest-first coin selection and fee policy stay here; the `TransactionSpec::Btc` (selected UTXOs, amount, fee) is encoded and signed in the module via `sign_transaction_in_module`, then broadcast over Esplora. Address checks via `tinywallet_bus::address::btc::{validate, validate_sender}`. |
| `crates/openhuman-core/src/web3/wallet/chains/solana.rs` | Solana native + SPL transfers: hand-rolled message/transaction wire format (`sha2`, `bs58`, `curve25519_dalek` for the off-curve ATA check) so `solana-sdk` is not pulled in; the message is signed in the module via `modules::wallet::sign_message` (`Scheme::Ed25519`), broadcast over JSON-RPC. The `ed25519_dalek` local signer is `cfg(test)` only. Also hosts `sign_and_broadcast_versioned` behind the crate-internal `sign_and_broadcast_solana`. |
| `crates/openhuman-core/src/web3/wallet/chains/tron.rs` | Tron native + TRC20 transfers over TronGrid REST: the node builds the raw transaction, `tinywallet_bus::tx::tron::{recompute_txid, verify_contract}` checks it matches what was requested, then it is signed in the module as `TransactionSpec::Tron`. Address checks via `tinywallet_bus::address::tron`. |
| `crates/openhuman-core/src/web3/wallet/stub.rs` | Disabled-wallet facade compiled when `web3` is off; mirrors the subset of the real surface that always-on / other-gated callers need, with no-op / disabled-error bodies. See the Compile-time gate section. |
| `crates/openhuman-core/src/web3/wallet/test_support.rs` | `#[cfg(test)]` shared plumbing: `TEST_LOCK`, `setup_wallet_in` (deterministic "abandon … about" mnemonic), per-chain sample addresses. |

## Public surface

From `mod.rs` re-exports:
- **Onboarding (`ops`)**: `setup`, `status`, `reveal_recovery_phrase`, `RevealRecoveryPhraseResult`, `WalletAccount`, `WalletChain`, `WalletSetupParams`, `WalletSetupSource`, `WalletStatus`, `WALLET_NOT_CONFIGURED_MESSAGE`; `pub(crate) secret_material`.
- **Execution (`execution`)**: `balances`, `chain_status`, `execute_prepared`, `wallet_network_defaults`, `prepare_transfer`, `tx_status`, `tx_receipt`, `lookup_tx`, `supported_assets`, `prepared_quotes_for_test`; types `BalanceInfo`, `ChainStatus`, `ExecutePreparedParams`, `ExecutionResult`, `PrepareTransferParams`, `PreparedKind` (NativeTransfer / TokenTransfer), `PreparedStatus`, `PreparedTransaction`, `ProviderStatus`, `SupportedAsset`, `TxState`, `TxStatusInfo`, `TxReceiptInfo`, `TxLookupInfo`. Crate-internal: `sign_and_broadcast_evm`, `sign_and_broadcast_solana`, `RawBroadcastResult`.
- **Defaults (`defaults`)**: `asset_catalog`, `default_rpc_url`, `env_var_for_chain`, `evm_asset_catalog`, `explorer_tx_url`, `find_asset`, `find_asset_for_network`, `network_defaults`, `rpc_source_for_chain`, `rpc_url_for_chain`, `rpc_url_for_evm_network`, `solana_cluster`, `EvmNetwork`, `RpcSource`, `SolanaCluster`, `WalletAssetDefinition`, `WalletNetworkDefaults`.
- **ABI**: `encode_erc20_transfer`.
- **Schemas**: `all_controller_schemas`, `all_registered_controllers`, `all_wallet_controller_schemas`, `all_wallet_registered_controllers`, `schemas`, `wallet_schemas`.

## RPC / controllers

Namespace `wallet` (method form `openhuman.wallet_<function>`), 13 controllers registered via `all_wallet_registered_controllers`:

| Function | Purpose |
| --- | --- |
| `status` | Onboarding status + safe account metadata (addresses). |
| `setup` | Persist consent + derived accounts + encrypted mnemonic (all inputs required); refuses to overwrite a configured wallet unless `force: true`. |
| `balances` | Native-asset balances per account (EVM live; others provider-gated). |
| `network_defaults` | RPC/explorer/capability flags + asset catalogs per chain. |
| `supported_assets` | Built-in asset catalog incl. default EVM ERC-20s / BEP20s. |
| `encode_erc20_transfer` | Encode `transfer(address,uint256)` calldata (EVM only). |
| `chain_status` | Per-chain readiness + active RPC URL. |
| `prepare_transfer` | Quote a native/token transfer (all four chains). |
| `execute_prepared` | Confirm (`confirmed: true`) + execute a quote by `quoteId` (tx send). |
| `tx_status` | Check a transaction's lifecycle state (pending/confirmed/failed/not_found) by hash. |
| `tx_receipt` | Fetch a transaction receipt (success, fee, block) by hash. |
| `lookup_tx` | Look up the raw transaction payload by hash. |
| `reveal_recovery_phrase` | Decrypt and return the stored BIP-39 phrase (`{phrase, wordCount}`); read-only, for transient display in the UI. |

Wired into the registry in `crates/openhuman-core/src/core/all.rs` (controllers + schemas + capability description).

## Agent tools

Owned in `tools/`, re-exported via `tools.rs`:
- `WalletStatusTool` — `wallet_status`
- `WalletChainStatusTool` — `wallet_chain_status`
- `WalletPrepareTransferTool` — `wallet_prepare_transfer`
- `WalletTxStatusTool` — `wallet_tx_status`
- `WalletTxReceiptTool` — `wallet_tx_receipt`
- `WalletLookupTxTool` — `wallet_lookup_tx`

All implement `crate::tools::traits::Tool` and delegate to the matching `wallet::*` functions. (There is no agent tool for `execute_prepared` here; execution is reached via RPC.)

## Events

None. The module publishes/subscribes no `DomainEvent`s and has no `bus.rs`. Chat-context coupling is via the task-local `approval::APPROVAL_CHAT_CONTEXT`, not the event bus.

## Persistence

- **`{workspace_dir}/state/wallet-state.json`** — `StoredWalletState`: consent flag, source, mnemonic word count, accounts, `updated_at_ms`, and (only as fallback) the encrypted mnemonic. Written atomically (temp file + `sync_all` + dir fsync + `persist`), guarded by a process-wide `WALLET_STATE_FILE_LOCK`. Corrupt/unreadable/invalid files are quarantined to `…json.corrupted.<ts>`.
- **OS keychain** — preferred home for the encrypted mnemonic under key `wallet.mnemonic`, scoped by a workspace-derived user id (`crate::security::keyring`), used only when `keyring_consent::policy::check_secret_access()` returns `Proceed` and the keyring is available. When available, the secret is stripped from JSON; load promotes any JSON-resident secret into the keychain.
- **In-memory quote store** (`execution.rs`) — `PreparedTransaction`s, 5-minute TTL, cap 64, pruned on access. Not persisted across restarts.

## Dependencies

- `crate::config` (`Config`, `config::rpc::load_config_with_timeout`) — resolves workspace dir and config for state paths, keychain user id, and decryption.
- `crate::security::keyring` (`is_available`/`get`/`set`) — OS keychain storage for the encrypted mnemonic.
- `crate::security::encryption::rpc` (`encrypt_secret`/`decrypt_secret`) — chain executors decrypt the recovery phrase before handing it to the wallet module.
- `crate::modules::wallet` (`derive_account`, `sign_transaction_in_module`, `sign_message`) — the loaded `tinywallet` native module does every derivation and signature; the phrase is only sent after the module passes the attestation check (`modules::wallet::attested_proxy`).
- `crate::security::approval::APPROVAL_CHAT_CONTEXT` — task-local chat owner (`thread_id`/`client_id`) used to bind quotes to their originating thread.
- `crate::tools::traits` — `Tool`/`ToolResult`/`ToolCallOptions` for the agent tools.
- `crate::core::all` (`ControllerFuture`, `RegisteredController`) and `crate::core` (`ControllerSchema`, `FieldSchema`, `TypeSchema`) — RPC controller registry wiring.
- `crate::rpc::RpcOutcome` — standard RPC return shape.
- `tinywallet-bus` (`vendor/tinywallet/crates/tinywallet-bus`, optional, gated by the `web3` feature; features `btc`, `evm`, `solana`, `tron`, `keccak`, `net`, `wire`, `eip712`, `abi`, `tx-codec`) — the contract crate. It owns address formats (parsing/validation/conversion) and the wire types crossing the `Transport` seam (`SecretMaterial`, `TransactionSpec`, `NetworkId`), the ERC-20/EIP-712 encoders, and the Tron verifier. Per Cargo.toml's own rationale: taken as the contract crate and NOT the root `tinywallet` crate — key derivation, transaction building, signing and the chain clients (including the `bitcoin` crate and its native secp256k1 build) live inside that loaded module now, so this binary links none of it. The root `tinywallet` crate is still a dev-dependency, used only so test fixtures can derive a known account from a BIP-39 vector phrase.
- Other external crates: `curve25519-dalek` (optional, pulled in by the `web3` feature; Solana off-curve ATA check), `bs58` (Solana base58 program ids/addresses), `sha2` (Solana ATA/PDA derivation), `hex`, `reqwest`, `serde`/`serde_json`, `tempfile`, `parking_lot`, `once_cell`. `k256`, `coins-bip39`, `ed25519-dalek` and the root `tinywallet` crate are test-only here (the `web3` feature does not enable `k256`/`coins-bip39`): they back the `cfg(test)` local signers in `chains/solana.rs`, `execution.rs` and the test fixtures, so unit tests can run without a loaded module.

## Used by

- `crates/openhuman-core/src/tools/mod.rs` — re-exports `wallet::tools::*`; `crates/openhuman-core/src/tools/ops.rs` — registers the six wallet agent tools (gated on the `web3` feature) and reserves the `wallet_`/`web3_`/`x402_` name prefixes as Web3-exclusive.
- `crates/openhuman-core/src/core/all.rs` — wires controllers/schemas/capability description.
- `crates/openhuman-core/src/test_support/introspect.rs` — `wallet_prepared_quotes` introspection helper used in tests, backed by `wallet::prepared_quotes_for_test`.

## Notes / gotchas

- **`rpc.rs` here is network transport, not RPC controllers.** RPC controllers live in `schemas.rs`. This is an exception to the canonical "`rpc.rs` = domain API" convention.
- **Quote-owner binding** (`execution.rs`): `execute_prepared` only runs when the caller's `current_owner()` equals the prepare-time owner. On mismatch it returns the byte-identical `quote '…' not found` error as a true miss — no enumeration oracle. Non-chat callers (CLI / direct RPC / background/cron) have `owner == None` and can only execute quotes they also prepared with no chat context. `current_owner()` relies on the inline `.await` chain in `web_chat::run_chat_task`; detaching the tool loop onto a fresh `tokio::spawn` without re-scoping `APPROVAL_CHAT_CONTEXT` would silently disable the gate.
- **Quotes are consumed atomically**: `take_quote_for` removes the quote before broadcast so concurrent confirmations can't double-submit; on failure the quote is restored with a refreshed TTL.
- **Setup requires exactly one account per chain** (EVM, BTC, Solana, Tron) and a non-empty encrypted mnemonic; valid mnemonic word counts are 12/15/18/21/24.
- **EVM is one `WalletChain::Evm` variant across 6 networks** (Ethereum, Base, Arbitrum, Optimism, Polygon, BNB Chain) selected by `EvmNetwork` (defaults to `ethereum_mainnet`); other chains ignore `evmNetwork`. BTC rejects token transfers. Swaps / bridges / contract calls are not in the wallet — they live in the [`web3`](../README.md) module.
- **RPC endpoints are overridable** per chain/network via `OPENHUMAN_WALLET_RPC_*` env vars (used by tests pointing at an axum mock). Log lines redact URLs to scheme+host.
- **`balances`**: only EVM reads live (Ethereum mainnet); BTC/Solana/Tron call their providers but fall back to zero with `ProviderStatus::Missing` on error.
