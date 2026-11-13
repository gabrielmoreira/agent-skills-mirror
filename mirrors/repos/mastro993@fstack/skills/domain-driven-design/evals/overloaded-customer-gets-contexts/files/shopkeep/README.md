# shopkeep

Backend for our B2B office-supplies shop. One Express app, one Postgres database.

Three teams work in this repo:

- **Sales**: leads, quotes, discounts.
- **Billing**: invoices and payments through Stripe.
- **Fulfillment**: picking, packing, shipping.

Everything shares `src/models` and `src/services`.
