---
type: llm
focus: trace
weight: 1
---

Every public class, interface, named object, and function in src/main/kotlin that had a KDoc before the run still has a KDoc directly above it (trimming is fine), including CheckoutRepository.getCart, whose KDoc may lose its "@param id the id" and "@return the cart" lines but must not be removed. (detekt exempts unnamed companion objects, so their KDoc may go.)
