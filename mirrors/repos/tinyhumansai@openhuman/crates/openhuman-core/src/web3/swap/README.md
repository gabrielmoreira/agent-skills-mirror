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
extraction) lives in `Web3Service::quote_swap` in the vendored `tinywallet-web3`
crate; this module only owns the RPC controllers (`schemas.rs`) for the
`web3_swap` namespace. The agent tools are in
`tinywallet_web3::tools::web3`.

## Key files

| File | Role |
| --- | --- |
| `mod.rs` | Module docs. |
| `schemas.rs` | `web3_swap` RPC controller schemas and handlers: `quote`, `execute`, `routes`. Handlers deserialize params and delegate to the process-wide `Web3Service` (`web3::seams::service()`): `quote_swap` / `execute_quote` / `routes`, wrapping the result in `Outcome`. |

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
