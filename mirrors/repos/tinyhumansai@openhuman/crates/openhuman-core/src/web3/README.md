# web3

The crypto family: a local multi-chain wallet, token swaps and cross-chain
bridges through deBridge, generic EVM dapp calls, and the x402 machine-payment
protocol. Almost all of the logic (the wallet engine, the per-chain signing
flows, the quote store, the agent tools) lives in the vendored
[`tinywallet`](../../../../vendor/tinywallet) crates. This folder is the host
adapter: it plugs OpenHuman's keyring, consent, config, backend client, and
chat scope into those crates through seams, and owns the RPC controllers.

Callers are the controller registry (`core/all.rs`), the tool registry
(`tools/ops.rs`), and the generic `http_request` tool, which falls back to an
x402 payment on an HTTP 402.

## How it works

### The process-wide engine and service

[`seams.rs`](./seams.rs) holds one `WalletEngine` and one `Web3Service` for the whole
process, built lazily on first use behind a `OnceLock` (`seams::engine()`,
`seams::service()`). Both come from `tinywallet-web3` and hold no
configuration of their own. Everything host-specific reaches them through
seams, each resolving its configuration per call:

| Seam (from `tinywallet-web3`) | Host implementation |
| --- | --- |
| `Transport` | `OpenHumanTransport` ([`wallet/transport.rs`](./wallet/transport.rs)) over the wallet RPC layer |
| `RpcEndpoints` | `HostEndpoints` ([`wallet/endpoints.rs`](./wallet/endpoints.rs)), the `OPENHUMAN_WALLET_RPC_*` environment |
| `WalletSigner` | `HostSigner` (`seams.rs`): keyring secret, decrypt, then the loaded wallet module |
| `WalletAccounts` | `HostAccounts` (`seams.rs`): the wallet's stored set-up state |
| `QuoteScope` | `TaskLocalScope` (`seams.rs`): the chat turn's `APPROVAL_CHAT_CONTEXT` |
| `Web3Backend` | `HostBackend` (`seams.rs`): `CryptoClient` over the integrations client |

```text
   core/all.rs                tools/ops.rs
   (wallet_*, web3_*,         (wallet_*, web3_*, x402_request)
    x402_* controllers)             |
          |                         |
          v                         v
   +----------------------------------------------+
   | web3/  (host adapter)                        |
   |   seams::engine() / seams::service()         |
   +----------------------------------------------+
          |  WalletEngine / Web3Service  (tinywallet-web3)
          |
          +-- WalletSigner --> HostSigner
          |       wallet::secret_material + decrypt_secret
          |       -> modules::wallet (loaded tinywallet module)
          |          derives key, signs, returns signed bytes
          +-- Transport/RpcEndpoints --> chain RPC (reqwest)
          +-- Web3Backend --> CryptoClient
          |       -> /agent-integrations/crypto/{routes,swap,bridge}
          +-- QuoteScope --> APPROVAL_CHAT_CONTEXT (thread, client)
```

No private key is ever assembled in this process, and the recovery phrase
never enters `tinywallet-web3`. `HostSigner` decrypts the phrase for one call
and sends it, as a `tinywallet_bus::wire::SecretMaterial`, over a confidential
call to the loaded wallet module, which must have proved it is an artifact
this build pinned (`modules::wallet`).

### Swap, bridge, and dapp: confirm then execute

All three use the same two-step flow, implemented in
`tinywallet_web3::crypto::service`:

```text
 web3_swap_quote / web3_bridge_quote / web3_dapp_call
   resolve the wallet's own address for the chain family (if not given)
   swap/bridge: HostBackend -> backend deBridge proxy -> quote + unsigned tx
   dapp: validate caller-supplied contract + calldata (no backend call)
   store quote { id, owner = QuoteScope::current_owner(), TTL 5 min }
   return { quoteId, kind, expiresAtMs, quote }
                     |
                     v
 web3_*_execute { quoteId, confirmed: true }
   take_for(owner)       -> "not found" if owner differs or expired
   sign via WalletSigner -> broadcast via Transport
   failure: restore the quote with a refreshed TTL
   return { quoteId, kind, transactionHash, explorerUrl?, feeRaw }
```

Quotes are bound to the chat thread and client that prepared them, so a
leaked `quoteId` cannot be executed from another session. Non-chat callers
(CLI, direct JSON-RPC, cron, sub-agents) have no owner and can execute their
own quotes. Cross-chain requests to `web3_swap` and same-chain requests to
`web3_bridge` are rejected, mirroring deBridge's split between single-chain
swaps and cross-chain DLN orders.

deBridge uses real EVM chain ids (1 Ethereum, 10 Optimism, 56 BNB, 137
Polygon, 8453 Base, 42161 Arbitrum) and a synthetic Solana id, `7565164`.
`chain_family` (in `tinywallet-web3`) maps a deBridge id to the local signer
family, and ids the wallet cannot sign for are rejected at quote time.

### Wallet and x402

The wallet ([`wallet/`](./wallet/)) owns onboarding, consent, the encrypted recovery
phrase, balances, and native and token transfers across EVM, Bitcoin, Solana,
and Tron, using the same prepare, confirm, execute pattern. x402 ([`x402/`](./x402/))
intercepts an HTTP 402 challenge, checks the spending ledger, has the wallet
sign a payment, and retries. Each has its own README.

## Layout

| Path | What it does |
| --- | --- |
| [`mod.rs`](./mod.rs) | Facade. Declares the family, re-exports `tinywallet_web3::crypto::service` as `web3::types`, aggregates the swap, bridge, and dapp controllers (`all_web3_controller_schemas`, `all_web3_registered_controllers`) and agent tools (`all_web3_agent_tools`), and holds shared schema helpers (`req_json`, `opt_str`, `json_result`, `execute_inputs`). |
| [`seams.rs`](./seams.rs) | The process-wide engine and service, and the host seam implementations listed above. |
| [`client.rs`](./client.rs) | `CryptoClient`, a thin wrapper over the shared `IntegrationClient` for `/agent-integrations/crypto/*`. Responses are passed through as `serde_json::Value`. |
| [`stub.rs`](./stub.rs) | Compiled when `web3` is off: the three aggregators return empty collections. |
| [`swap/`](swap/README.md) | `web3_swap` controllers: `quote`, `execute`, `routes`. |
| [`bridge/`](./bridge/) | `web3_bridge` controllers: `quote`, `execute`. |
| [`dapp/`](dapp/README.md) | `web3_dapp` controllers: `call`, `execute`. |
| [`wallet/`](wallet/README.md) | Wallet controllers, onboarding and secret state (`ops/`), the engine wrapped in `Outcome` (`execution.rs`), endpoint resolution, and the chain transport. Has its own `stub.rs`. |
| [`x402/`](x402/README.md) | x402 controllers, wallet and proxy seams for `tinywallet-x402`, ledger budget from the environment, payment records. Has its own `stub.rs`. |

## Key types and entry points

- `seams::engine()` and `seams::service()` return the shared `WalletEngine`
  and `Web3Service`. The wallet tools in `tools/ops.rs` are built over
  `engine()`; the swap, bridge, and dapp tools over `service()`.
- `HostSigner`, `HostAccounts`, `TaskLocalScope`, and `HostBackend`
  (`seams.rs`) are the seam implementations a contributor changes when host
  behavior has to change.
- `CryptoClient::from_config` ([`client.rs`](./client.rs)) errors when no backend credential
  is available, the same gate the Composio tools use.
- `all_web3_agent_tools()` ([`mod.rs`](./mod.rs)) builds the seven swap, bridge, and dapp
  tools from `tinywallet_web3::tools::web3`.
- `x402::request_tool()` and `x402::handle_402_and_pay` are the x402 entry
  points for the tool registry and the `http_request` 402 retry.

## RPC / CLI surface

All are registered under `DomainGroup::Web3` in `core/all.rs`. Method names
are `openhuman.<namespace>_<function>`.

| Namespace | Functions |
| --- | --- |
| `web3_swap` | `quote`, `execute`, `routes` |
| `web3_bridge` | `quote`, `execute` |
| `web3_dapp` | `call`, `execute` |
| [`wallet`](./wallet) | `setup`, `status`, `reveal_recovery_phrase`, `balances`, `chain_status`, `network_defaults`, `supported_assets`, `encode_erc20_transfer`, `prepare_transfer`, `execute_prepared`, `tx_status`, `tx_receipt`, `lookup_tx` |
| [`x402`](./x402) | `get_summary`, `list_payments`, `update_budget` |

Each `*_execute` takes `quoteId` and `confirmed`, and `confirmed` must be
true. That flag is the explicit boundary between preparing and spending.

## Agent tools

- Swap, bridge, dapp (from `tinywallet_web3::tools::web3`):
  `web3_swap_quote`, `web3_swap_execute`, `web3_swap_routes`,
  `web3_bridge_quote`, `web3_bridge_execute`, `web3_dapp_call`,
  `web3_dapp_execute`. They register unconditionally and error at call time
  when the user is not signed in.
- Wallet tools (status, chain status, prepare transfer, tx status, receipt,
  lookup) are re-exported through [`wallet/tools.rs`](./wallet/tools.rs) and `tools/mod.rs`, and
  built in `tools/ops.rs`.
- `x402_request`, from `tinywallet-x402`, wired through [`x402/seams.rs`](./x402/seams.rs).

## Boundaries

- Wallet engine, transfer flows, per-chain transaction building, swap,
  bridge, and dapp quote preparation, the quote store, and the agent tools
  belong to `tinywallet-web3`. The x402 wire format, payment builders,
  spending ledger, and `x402_request` tool belong to `tinywallet-x402`. Chain
  primitives and wire types belong to `tinywallet-bus` and
  `tinywallet-crypto`. Key derivation and signing belong to the loadable
  `tinywallet` module. All of these are in `vendor/tinywallet`, upstream
  `tinyhumansai/tinywallet`.
- Loading and attesting the wallet module belongs to `modules/wallet.rs`.
- Quote routes, deBridge integration, and the affiliate fee (default 1%,
  collected on-chain by deBridge on the source chain) belong to the backend.
  This module passes quotes through unchanged.
- The approval chat context (`APPROVAL_CHAT_CONTEXT`) belongs to
  `security::approval`.

## Gotchas

- The `web3` Cargo feature is not in the core's `default` set, despite older
  comments (including in `Cargo.toml` and the `mod.rs` docs) calling it
  default-on. It is in `scripts/ci/product-features.txt`, so the shipped app
  has it. It enables `tinywallet-bus`, `tinywallet-x402`, `tinywallet-web3`,
  and `modules`. At runtime `DomainSet::web3` gates the same surface.
- `pub mod web3`, `wallet`, and `x402` are always compiled. Each is a facade
  with its own [`stub.rs`](./stub.rs) for the disabled build, so always-on callers
  (`core/all.rs`, `tools/ops.rs`, `tools/impl/network/host.rs` for x402) need
  no `#[cfg]`. Stub signatures must match the real ones, and only
  `cargo check --no-default-features` catches drift.
- `TaskLocalScope` reads a `tokio::task_local!`, which propagates across
  `.await` but not across `tokio::spawn`. If the chat path ever runs the tool
  loop on a freshly spawned task without re-installing the scope, the owner
  gate silently becomes a no-op. [`seams_tests.rs`](./seams_tests.rs) pins that it reads the
  task-local.
- `CryptoClient` logs only chain ids. Request bodies carry wallet addresses,
  which must not be logged in full.

## Tests

[`seams_tests.rs`](./seams_tests.rs) composes the real wallet state and pins the task-local scope.
[`stub_tests.rs`](./stub_tests.rs) runs only in the disabled build. `wallet/` and `x402/` keep
their own tests.

```bash
cargo test -p openhuman --features web3 web3::
cargo check -p openhuman --no-default-features   # stub drift
```

## Further reading

- [Wallet](../../../../gitbooks/features/wallet.md)
- [tinywallet submodule](../../../../vendor/tinywallet/README.md)
- [Loadable modules](../../../../gitbooks/developing/loadable-modules.md)
