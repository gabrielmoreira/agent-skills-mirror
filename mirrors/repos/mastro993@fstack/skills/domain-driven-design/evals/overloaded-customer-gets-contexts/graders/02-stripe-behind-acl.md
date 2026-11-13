---
type: llm
focus: trace
weight: 1
---

The reply flags Stripe types (Stripe.PaymentIntent, Stripe.Invoice) inside the Order model in src/models/Order.ts and proposes keeping them in an adapter or anticorruption layer so the domain model does not import stripe.
