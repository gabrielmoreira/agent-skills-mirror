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

## Compile-time gate (`web3` feature)

`pub mod x402;` (declared in `web3/mod.rs`) is ALWAYS compiled — it is a
facade. The real payment machinery (`ops`, `schemas`, `store`, `tools`,
`types`) is gated behind the default-ON `web3` Cargo feature (shared with
`web3` and `web3::wallet`). When the feature is off, `stub.rs` takes its
place and exposes only the three entry points with always-on callers:
`init_ledger` (a no-op; the boot call site in `core/jsonrpc.rs` is itself
runtime-gated on `DomainGroup::Web3`), `all_x402_registered_controllers`, and
`all_x402_controller_schemas` (both empty). `X402RequestTool`'s registration
and the `http_request` 402-retry path are `#[cfg(feature = "web3")]` at their
own call sites, so the rest of the payment surface (`PaymentRecord`, `store`,
`SettlementResponse`, …) is never referenced when the feature is off and does
not need a stub. Signatures must match the real ones exactly; `cargo check
--no-default-features` is the only thing that catches drift.

## Key files

| File | Role |
| --- | --- |
| `mod.rs` | Facade root: feature gate, re-exports (`handle_402`, `handle_402_and_pay`, `try_paid_request`, `X402Client`, `X402Error`, `X402PaymentResult`, `init_ledger`, the controller pair, wire types). |
| `ops.rs` | Facade over submodules under `ops/` (`client.rs`, `errors.rs`, `headers.rs`, `evm_payment.rs`, `solana_payment.rs`) of the client logic: parse a 402 challenge, build the Solana (`exact` scheme: ComputeBudget limit/price, SPL `TransferChecked`, optional Memo) or EVM (`exact` scheme: EIP-3009 `transferWithAuthorization`) payment, sign, and retry with the proof. |
| `ops/client.rs` / `ops/errors.rs` | `X402Client`/`try_paid_request`, `X402PaymentResult`, `X402Error`, `handle_402`/`handle_402_and_pay`, `wallet_signer` (Solana signer resolution through the wallet module), calling into `build_solana_payment` (`solana_payment.rs`) and `build_evm_payment` (`evm_payment.rs`). |
| `ops/headers.rs` | `PAYMENT-REQUIRED`/`PAYMENT-RESPONSE` header parsing. |
| `ops/evm_payment.rs` | EVM EIP-712 authorization/payload construction (`evm_payment_authorization`, `evm_payment_payload`), `evm_signer` (EVM signer resolution), `build_evm_payment` (signs via `modules::wallet::sign_message`), and a `cfg(test)`-only local `k256` signer used to check the construction against a fixed vector. |
| `ops/solana_payment.rs` | The Solana instruction builders (ComputeBudget, `TransferChecked`, Memo) and `build_solana_payment`. |
| `store.rs` | Append-only JSONL payment ledger (`PaymentLedger`) with per-request/daily/monthly budget enforcement and session/daily/monthly spend summaries; `PaymentRecord`, `PaymentStatus`, `SpendingSummary`, `SpendingBudget`, `BudgetCheck`, the process-global `GLOBAL_LEDGER`, `init_global` (re-exported as `init_ledger`), and `with_ledger`/`with_ledger_mut` accessors. |
| `schemas.rs` | RPC controller schemas + handlers for the `x402` namespace: `get_summary`, `list_payments`, `update_budget`. |
| `tools.rs` | `X402RequestTool` (`x402_request`) — purpose-built agent tool for x402 endpoints, as opposed to the generic `http_request` tool's opportunistic 402 fallback. |
| `types.rs` | Wire types for the v2 protocol: header names, CAIP-2 network/asset constants (Solana mainnet/devnet, Base/Ethereum, USDC mints/contracts), `PaymentRequired`/`PaymentRequirements`/`PaymentPayload`/`PaymentProof` (Evm/Solana variants), `SettlementResponse`, `ResourceInfo`. |
| `stub.rs` | Disabled facade compiled when `web3` is off. See Compile-time gate above. |
| `x402_tests.rs`, `store_tests.rs`, `stub_tests.rs` | Behavior tests, `#[cfg(all(test, feature = "web3"))]` except `stub_tests.rs` which runs only in the disabled build. |

## RPC / controllers

Namespace `x402` (method form `openhuman.x402_<function>`), registered via
`all_x402_registered_controllers`:

| Function | Purpose |
| --- | --- |
| `get_summary` | Spending totals for session/day/month plus the current budget limits. |
| `list_payments` | Recent payment records, newest first (`limit`, default 50, max 500). |
| `update_budget` | Update `per_request_max` / `daily_max` / `monthly_max` (atomic USDC units; 1 USDC = 1,000,000). |

## Agent tool

`X402RequestTool` (`x402_request`, `PermissionLevel::Write`) makes an HTTP
request to an x402-payable endpoint, always expecting a payment challenge: it
sends the initial request, requires a `PAYMENT-REQUIRED`/`X-PAYMENT-REQUIRED`
header on a 402, builds and signs the payment via `handle_402_and_pay`,
records a `Pending` ledger entry, retries with `PAYMENT-SIGNATURE`, and
updates the ledger to `Settled`/`Failed` based on the retry's outcome and the
decoded `PAYMENT-RESPONSE` settlement header. This differs from the generic
`http_request` tool (`crates/openhuman-core/src/tools/impl/network/http_request.rs`),
which handles a 402 only as a silent fallback for any endpoint.

## Persistence

- **`{workspace_dir}/x402/payments.jsonl`** — one JSON `PaymentRecord` per
  line, appended on every pending/settled/failed payment. Loaded into memory
  at `PaymentLedger::new` (via `init_ledger`) and held in the process-global
  `GLOBAL_LEDGER`, guarded by a `parking_lot::Mutex`.
- **Budget enforcement** (`SpendingBudget`, defaults: 1 USDC per request, 10
  USDC per day, 100 USDC per month, in atomic units) is checked against the
  in-memory ledger before a payment is built. Daily and monthly totals sum
  the `Settled` records for the current UTC day / calendar month. The session
  total reported by `get_summary` counts records whose `session_id` equals the
  ledger's `x402-<uuid>` boot id; it is not a cap, and both writers currently
  store an empty `session_id`, so it reads as zero. `init_ledger` seeds the limits
  from `OPENHUMAN_X402_PER_REQUEST_MAX` / `OPENHUMAN_X402_DAILY_MAX` /
  `OPENHUMAN_X402_MONTHLY_MAX` when set; `update_budget` changes them for the
  running process only and does not rewrite historical records.

## Dependencies

- `crate::web3::wallet::secret_material` — fetches the encrypted mnemonic +
  derivation path for the chain being paid on (`WalletChain::Evm` /
  `WalletChain::Solana`).
- `crate::security::encryption::rpc::decrypt_secret` — decrypts the mnemonic
  in this process just long enough to hand it to the signer.
- `crate::modules::wallet::{derive_account, sign_message}` — the actual
  derivation and signing happen inside the loaded `tinywallet` native module
  over a confidential bus call; this binary never derives a private key or
  holds one. Only the decrypted **mnemonic** passes through this process, in
  the `tinywallet_bus::wire::SecretMaterial` handed to those calls.
- `tinywallet_bus::wire::SecretMaterial`, `tinywallet_bus::Chain` — the wire
  types crossing that seam.
- `crate::config::rpc::load_config_with_timeout` — config needed to reach the
  wallet module and decrypt the mnemonic.

## Used by

- `crates/openhuman-core/src/tools/impl/network/http_request.rs` (~lines
  165-265) — `handle_x402_payment`, gated `#[cfg(feature = "web3")]`, is the
  402 fallback path any HTTP tool call can hit; it calls
  `x402::handle_402_and_pay` and records to the same ledger via
  `x402::store::with_ledger_mut`.
- `crates/openhuman-core/src/tools/ops.rs` — registers `X402RequestTool` as an
  agent tool.
- `crates/openhuman-core/src/core/all.rs` (~line 569) — wires
  `all_x402_registered_controllers` into the controller registry under
  `DomainGroup::Web3`.
- `crates/openhuman-core/src/core/jsonrpc.rs` (~line 2477) — calls
  `init_ledger(&workspace_dir, &x402_session)` at boot, itself runtime-gated on
  `DomainGroup::Web3`.

## Notes / gotchas

- The paying account never needs SOL (or ETH/native gas) for the payment
  transaction itself — the facilitator is the fee payer / on-chain submitter.
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
