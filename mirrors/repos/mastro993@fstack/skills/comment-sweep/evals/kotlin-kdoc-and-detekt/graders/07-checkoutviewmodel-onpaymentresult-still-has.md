---
type: llm
focus: trace
weight: 1
---

CheckoutViewModel.onPaymentResult still has its "Must be called on the main thread" note, and the final reply proposes annotating it with @MainThread (or @UiThread) so the comment can go.
