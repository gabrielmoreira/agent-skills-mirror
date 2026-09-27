# web3/swap

Single-chain token swaps via the deBridge proxy, one of the three families
under [`web3`](../README.md) alongside `bridge` and `dapp`. See the parent
README for the shared quote store, chain-id mapping, and signing path; this
file only covers what is specific to swaps.

## What it does

A swap quote asks deBridge for a route to exchange one token for another on
the same chain. Cross-chain requests are rejected here with a pointer to
`web3_bridge`, since deBridge's `/swap` endpoint is single-chain only. The
actual quote logic (address defaulting, the backend call, unsigned-tx
extraction) lives in the shared `super::ops::quote_swap`; this module only
owns the RPC controllers (`schemas.rs`) and the agent tools (`tools.rs`) for
the `web3_swap` namespace.

## Key files

| File | Role |
| --- | --- |
| `mod.rs` | Re-exports `Web3SwapExecuteTool`, `Web3SwapQuoteTool`, `Web3SwapRoutesTool` from `tools.rs`. |
| `schemas.rs` | `web3_swap` RPC controller schemas and handlers: `quote`, `execute`, `routes`. Handlers deserialize params and delegate to `super::super::ops::quote_swap` / `super::super::store::execute_quote` / `super::super::ops::routes`. |
| `tools.rs` | The three agent tools: `Web3SwapQuoteTool` (`web3_swap_quote`), `Web3SwapExecuteTool` (`web3_swap_execute`), `Web3SwapRoutesTool` (`web3_swap_routes`). All delegate to the same `ops`/`store` functions as the RPC handlers, so behavior is identical between the two entry points. |

## RPC / controllers

Namespace `web3_swap` (method form `openhuman.web3_swap_<function>`):

| Function | Purpose |
| --- | --- |
| `quote` | Prepare a single-chain swap. Params: `chainId`, `tokenIn`, `tokenInAmount`, `tokenOut`, and optional `tokenOutRecipient`, `senderAddress`, `slippage` (default `"auto"`). Returns a prepared quote with a `quoteId`. |
| `execute` | Confirm and execute a prepared quote (`quoteId`, `confirmed: true`). Signs and broadcasts. |
| `routes` | List the chains deBridge can swap and bridge between. No params. |

## Agent tools

`web3_swap_quote`, `web3_swap_execute`, `web3_swap_routes`. They call the
backend per invocation and return a tool error, rather than being hidden,
when the caller is not signed in.

## Notes

- Recipient and sender addresses default to the wallet's own derived address for the chain family when omitted.
- The quote id returned by `quote` is bound to the chat thread that prepared it; see the parent [README](../README.md) for the quote store's TTL and ownership rules, which this module shares with `bridge` and `dapp`.
