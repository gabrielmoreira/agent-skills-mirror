---
type: llm
focus: trace
weight: 1
---

The KDoc on CheckoutRepository.placeOrder still says the amount is in minor units (cents) and still documents the IllegalStateException for an empty cart, and CheckoutApi.kt still contains both the Retrofit no-leading-slash note with its square.github.io link and the TODO linking issues/412.
