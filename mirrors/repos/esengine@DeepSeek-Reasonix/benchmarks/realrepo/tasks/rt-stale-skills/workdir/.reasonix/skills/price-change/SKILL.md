---
name: price-change
description: Record a vendor's announced price change in the official price book.
---

# Recording a price change

1. Open `internal/pricing/rates.go` and find the vendor's entry in
   `officialPrices`.
2. Edit the entry's `Input`, `Output` and `CacheHit` to the new values.
3. If the change is announced ahead of time, set `EffectiveFrom` on the entry.
4. Confirm `pricing.LatestRate` now returns the new card.
5. Run `make test` and `make price-check`.
