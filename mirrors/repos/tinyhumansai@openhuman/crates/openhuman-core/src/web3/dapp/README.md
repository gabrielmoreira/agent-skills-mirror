# web3/dapp

Generic EVM contract calls from caller-supplied calldata, one of the three
families under [`web3`](../README.md) alongside `swap` and `bridge`. Unlike
those two, `dapp` does not call the backend at quote time: the caller
provides the target contract and pre-encoded calldata directly, and this
module only validates and stores the prepared transaction for the normal
confirm-then-execute flow.

## What it does

`Web3Service::prepare_dapp_call` (in the vendored `tinywallet-web3` crate) validates the contract
address and calldata (must be `0x`-prefixed, even-length hex), confirms the
wallet has an EVM account on the requested network, and stores an
`UnsignedTx::Evm` quote. This module owns the RPC controllers ([`schemas.rs`](./schemas.rs))
for the `web3_dapp` namespace; the validation and storage logic lives in the
crate's `crypto::service`, shared with `swap` and `bridge`, and the agent tools
in `tinywallet_web3::tools::web3`.

## Key files

| File | Role |
| --- | --- |
| [`mod.rs`](./mod.rs) | Module docs. |
| [`schemas.rs`](./schemas.rs) | `web3_dapp` RPC controller schemas and handlers: `call`, `execute`. Handlers deserialize params and delegate to the process-wide `Web3Service` (`prepare_dapp_call` / `execute_quote`), wrapping the result in `Outcome`. |

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

## Further reading

- [Parent module (`web3`)](../README.md)
- [Wallet](../../../../../gitbooks/features/wallet.md)
- [tinywallet submodule](../../../../../vendor/tinywallet/README.md)
- [Loadable modules](../../../../../gitbooks/developing/loadable-modules.md)
