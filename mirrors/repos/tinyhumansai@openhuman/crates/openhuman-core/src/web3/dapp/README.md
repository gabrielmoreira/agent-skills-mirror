# web3/dapp

Generic EVM contract calls from caller-supplied calldata, one of the three
families under [`web3`](../README.md) alongside `swap` and `bridge`. Unlike
those two, `dapp` does not call the backend at quote time: the caller
provides the target contract and pre-encoded calldata directly, and this
module only validates and stores the prepared transaction for the normal
confirm-then-execute flow.

## What it does

`prepare_dapp_call` (in the shared `super::ops`) validates the contract
address and calldata (must be `0x`-prefixed, even-length hex), confirms the
wallet has an EVM account on the requested network, and stores an
`UnsignedTx::Evm` quote. This module owns the RPC controllers (`schemas.rs`)
and agent tools (`tools.rs`) for the `web3_dapp` namespace; the validation and
storage logic lives in `super::ops` and `super::store`, shared with `swap` and
`bridge`.

## Key files

| File | Role |
| --- | --- |
| `mod.rs` | Re-exports `Web3DappCallTool`, `Web3DappExecuteTool` from `tools.rs`. |
| `schemas.rs` | `web3_dapp` RPC controller schemas and handlers: `call`, `execute`. Handlers deserialize params and delegate to `super::super::ops::prepare_dapp_call` / `super::super::store::execute_quote`. |
| `tools.rs` | The two agent tools: `Web3DappCallTool` (`web3_dapp_call`), `Web3DappExecuteTool` (`web3_dapp_execute`). Delegate to the same `ops`/`store` functions as the RPC handlers. |

## RPC / controllers

Namespace `web3_dapp` (method form `openhuman.web3_dapp_<function>`):

| Function | Purpose |
| --- | --- |
| `call` | Prepare a generic EVM contract call. Params: `contractAddress`, `calldata` (0x-prefixed hex), and optional `valueRaw` (default `"0"`), `evmNetwork` (default `ethereum_mainnet`). Returns a prepared quote with a `quoteId`. |
| `execute` | Confirm and execute a prepared quote (`quoteId`, `confirmed: true`). Signs the contract call in-core and broadcasts it. |

## Agent tools

`web3_dapp_call`, `web3_dapp_execute`. The `evmNetwork` argument accepts
`ethereum_mainnet`, `base_mainnet`, `arbitrum_one`, `optimism_mainnet`,
`polygon_mainnet`, `bsc_mainnet`.

## Notes

- No backend call is involved in preparing a dapp call; deBridge is only used by `swap` and `bridge`. Signing and broadcast still go through the wallet's crate-internal `sign_and_broadcast_evm`, same as the other two families.
- The quote id returned by `call` is bound to the chat thread that prepared it, TTL'd at 5 minutes, and restored with a refreshed TTL on a failed broadcast; see the parent [README](../README.md) for the shared quote store.
- BTC and Solana are out of scope here. `dapp` is EVM-only.
