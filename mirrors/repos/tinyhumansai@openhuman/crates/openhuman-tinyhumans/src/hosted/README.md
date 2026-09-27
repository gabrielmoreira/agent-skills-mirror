# hosted

RPC proxy domains for the hosted TinyHumans backend. Each one is a thin
client of `tinyhumansai/backend`: the truth lives server-side, and this side
only authenticates a request, forwards it, and shapes the result. They live
in this crate rather than the core because a core with no TinyHumans
connection has no use for them.

## Contents

- [`billing/`](billing/README.md): plans, Stripe/Coinbase purchase and
  top-up flows, credit balance and transactions, auto-recharge and saved
  cards, coupon redemption.
- [`team/`](team/README.md): team CRUD, membership, role changes, invites,
  usage, active-team switching.
- [`referral/`](referral/README.md): referral codes and reward claims.
- [`announcements/`](announcements/README.md): the latest active product
  announcement, surfaced on harness init.

Each domain follows the same shape: an `ops.rs` of async handlers that
attach the session credential and call the backend, and a `schemas.rs` that
registers them as controllers (`openhuman.billing_*`, `team_*`, `referral_*`,
`announcements_*`). None of them own local state, domain types, or
authorization; a missing or invalid session surfaces the backend's 401/403
verbatim as an RPC error string.

## Wiring

`extension()` in `mod.rs` collects every domain's registered controllers
into one `ControllerExtension` tagged `DomainGroup::Hosted`, plus the
`NAMESPACES` table `namespace_description` serves for this surface.
`crate::install()` hands this extension to
`core::all::register_controller_extension` so these RPC methods appear in
whichever core's registry called `install()`, without the core knowing these
domains exist. `crates/openhuman-core/src/core/all.rs` is the extension
point; it never grows a `billing` or `team` branch of its own.

## Where to look next

- Each subdirectory's own README for its RPC surface and wire names.
- [`../transport/README.md`](../transport/README.md): the
  `BackendTransport` these domains ultimately call through.
- `AGENTS.md`, "Backend API": why hosted-only proxy domains belong here and
  not in the core.
