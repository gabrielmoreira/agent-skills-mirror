# x402

HTTP 402 machine-payment protocol (x402.org / coinbase/x402 v2). Intercepts an
HTTP 402 response carrying a `PAYMENT-REQUIRED` header, builds a payment (a
Solana SPL/USDC transfer, or an EVM EIP-3009 `transferWithAuthorization`),
signs it with the wallet's key, and retries the request with the proof in a
`PAYMENT-SIGNATURE` header. A facilitator co-signs as fee payer and broadcasts,
so the client never needs native gas currency (SOL/ETH) to pay.

Sibling of the [`wallet`](../wallet/README.md) module in the
[`web3`](../README.md) family. Payments are reached either through the
dedicated `x402_request` agent tool or as a 402 fallback inside the generic
`http_request` tool.

The implementation lives in the **`tinywallet-x402`** crate
(`vendor/tinywallet/crates/tinywallet-x402`, features `wire`, `pay`, `ledger`,
`tools`): the 402 client, the EVM and Solana payment builders, the spending
ledger and the `x402_request` agent tool. This directory is the host side and
nothing else: the seams the crate is handed, the RPC controllers, the spending
limits, and the disabled-build stub. A behavior change to the protocol, the
payment construction, the ledger or the tool belongs in `tinywallet`, not here.

## Compile-time gate (`web3` feature)

`pub mod x402;` (declared in `web3/mod.rs`) is always compiled: it is a
facade. The real payment surface (`seams`, `schemas`, `budget` and the
`tinywallet_x402` re-exports) is gated behind the default-ON `web3` Cargo feature (shared with
`web3` and `web3::wallet`). When the feature is off, `stub.rs` takes its
place and exposes only the three entry points with always-on callers:
`init_ledger` (a no-op; the boot call site in `core/runtime/bootstrap.rs` is itself
runtime-gated on `DomainGroup::Web3`), `all_x402_registered_controllers`, and
`all_x402_controller_schemas` (both empty). The `x402_request` tool's registration
and the `http_request` 402-retry path are `#[cfg(feature = "web3")]` at their
own call sites, so the rest of the payment surface (`PaymentRecord`, `store`,
`SettlementResponse`, and so on) is never referenced when the feature is off
and does not need a stub. Signatures must match the real ones exactly;
`cargo check --no-default-features` is the only thing that catches drift.

## Key files

| File | Role |
| --- | --- |
| `mod.rs` | Facade root: feature gate; re-exports from `tinywallet_x402` (`X402Client`, `X402Error`, `X402PaymentResult`, `handle_402`, the ledger and wire types); `init_ledger`, `handle_402_and_pay`, `try_paid_request` and `request_tool`, which supply the seams; the `store` accessors used by `http_request`. |
| `seams.rs` | `WalletPaymentSigner` (the crate's `PaymentSigner`: keyring secret, decrypt, `modules::wallet::{derive_account, sign_message}`), `RuntimeProxyPolicy` (`ProxyPolicy` over `config::apply_runtime_proxy_to_builder`), and the `payments()` / `request_tool()` constructors that pair them with the wallet's `OpenHumanTransport`. |
| `budget.rs` | The spending limits: the crate's defaults plus the `OPENHUMAN_X402_*` overrides. |
| `records.rs` | `pending_record`: the `Pending` ledger record for the `http_request` fallback (ledger session + chat thread). |
| `schemas.rs` | RPC controller schemas and handlers for the `x402` namespace: `get_summary`, `list_payments`, `update_budget`. |
| `stub.rs` | Disabled facade compiled when `web3` is off. See Compile-time gate above. |
| `seams_tests.rs`, `budget_tests.rs`, `stub_tests.rs` | Behavior tests. `stub_tests.rs` runs only in the disabled build. The protocol, builder, ledger and tool tests live in the crate. |

## The seams

| Trait (in `tinywallet-x402`) | Host implementation | Notes |
| --- | --- | --- |
| `PaymentSigner` (`account`, `sign`) | `WalletPaymentSigner` | The mnemonic is decrypted here for one confidential module call and never enters the crate; it sees an address and finished signatures. Errors keep their historical prefixes (`wallet secret:`, `load config:`, `decrypt mnemonic:`, `derive account:`). |
| `rpc::Transport` (from `tinywallet-crypto`) | `wallet::transport::OpenHumanTransport` | Reads the Solana blockhash through the wallet's failover-aware RPC layer. |
| `ProxyPolicy` (`apply`) | `RuntimeProxyPolicy` | Applies the runtime proxy configuration to the tool's HTTP client. |

## RPC / controllers

Namespace `x402` (method form `openhuman.x402_<function>`), registered via
`all_x402_registered_controllers`:

| Function | Purpose |
| --- | --- |
| `get_summary` | Spending totals for session/day/month plus the current budget limits. |
| `list_payments` | Recent payment records, newest first (`limit`, default 50, max 500). |
| `update_budget` | Update `per_request_max` / `daily_max` / `monthly_max` (atomic USDC units; 1 USDC = 1,000,000). |

## Agent tool

`x402_request` is `tinywallet_x402::tools::X402RequestTool`, built by
`request_tool()` and registered in `tools/ops.rs`. See the crate for its
behavior: it sends the initial request, requires a `PAYMENT-REQUIRED` /
`X-PAYMENT-REQUIRED` header on a 402, pays via `handle_402_and_pay`, records a
`Pending` ledger entry, retries with `PAYMENT-SIGNATURE`, and settles the entry
from the retry's outcome and the `PAYMENT-RESPONSE` header. It differs from the
generic `http_request` tool (`tinytools_std::network::HttpRequestTool`, with its payment hook in `tools/impl/network/host.rs`), which
handles a 402 only as a silent fallback.

The tool is built with `TaskLocalThread` (`seams.rs`), the host's
`tinywallet_x402::thread::ThreadScope`: it reads the chat thread id from the
`APPROVAL_CHAT_CONTEXT` task-local and the crate records it as
`PaymentRecord.thread_id` (absent outside a chat turn). `session_id` is always
the ledger's own `x402-<uuid>` boot id. The `http_request` 402 fallback builds
its record with `pending_record` (`records.rs`), which applies the same rule.

## Persistence

- `{workspace_dir}/x402/payments.jsonl`: one JSON `PaymentRecord` per line,
  appended on every pending/settled/failed payment (`tinywallet_x402::ledger`).
  Loaded into memory by `init_ledger` and held in the crate's process-wide
  ledger.
- Budget enforcement (defaults: 1 USDC per request, 10 USDC per day, 100 USDC
  per month, in atomic units) checks and reserves the amount atomically against
  the in-memory ledger before a payment is signed, so concurrent payments cannot
  exceed a cap. Daily and monthly totals sum the `Settled` records for the
  current UTC day / calendar month plus the amounts held by in-flight payments.
  The session total reported by `get_summary` counts records whose `session_id`
  equals the ledger's `x402-<uuid>` boot id, which every payment of this process
  carries (both writers), so it is the process's total; it is not a cap. The chat
  thread is recorded separately in `thread_id`. `init_ledger` seeds the limits from
  `OPENHUMAN_X402_PER_REQUEST_MAX` / `OPENHUMAN_X402_DAILY_MAX` /
  `OPENHUMAN_X402_MONTHLY_MAX` when set (`budget.rs`); `update_budget` changes
  them for the running process only and does not rewrite historical records.

## Dependencies

- `tinywallet-x402` (features `wire`, `pay`, `ledger`, `tools`): everything above.
- `crate::web3::wallet::secret_material`: the encrypted mnemonic and derivation
  path for the chain being paid on.
- `crate::security::encryption::rpc::decrypt_secret`: decrypts the mnemonic in
  this process just long enough to hand it to the module.
- `crate::modules::wallet::{derive_account, sign_message}`: derivation and
  signing happen inside the loaded `tinywallet` native module over a
  confidential bus call; this binary never derives a private key.
- `crate::config::rpc::load_config_with_timeout` and
  `config::apply_runtime_proxy_to_builder`.

## Used by

- `crates/openhuman-core/src/tools/impl/network/host.rs`:
  `X402PaymentHook`, gated `#[cfg(feature = "web3")]` and installed on
  `http_request` as its `PaymentHook`, is the 402 fallback path any HTTP tool
  call can hit. It calls `x402::handle_402_and_pay` and records to the same
  ledger via `x402::store::with_ledger_mut`.
- `crates/openhuman-core/src/tools/ops.rs`: registers `x402::request_tool()` as
  an agent tool.
- `crates/openhuman-core/src/core/all.rs`: wires `all_x402_registered_controllers`
  into the controller registry under `DomainGroup::Web3`.
- `crates/openhuman-core/src/core/runtime/bootstrap.rs`: calls
  `init_ledger(&workspace_dir, &x402_session)` at boot, itself runtime-gated on
  `DomainGroup::Web3`.

## Notes / gotchas

- The paying account never needs SOL (or ETH/native gas) for the payment
  transaction itself; the facilitator is the fee payer and on-chain submitter.
  The wallet does still need the payment asset (typically USDC) on the target
  chain.
- Budget limits live in the process (defaults or env at boot, then
  `update_budget`); spend totals are recomputed from the on-disk ledger on
  every boot, so restarting does not reset what was spent today or this
  month. None of this substitutes for on-chain spending limits.
- Two distinct paths reach a payment: the purpose-built `x402_request` agent
  tool (always expects a 402) and the generic `http_request` tool's
  opportunistic 402 fallback. Both funnel through `handle_402_and_pay` and the
  same ledger, so spending is tracked consistently regardless of entry point.
