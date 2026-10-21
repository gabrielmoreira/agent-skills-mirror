---
name: price-change
description: Record a vendor's announced price change in the official price book without losing the rate it replaces.
---

# Recording a price change

1. Find the vendor's rows in `officialRates` in
   `internal/contract/pricing/rates.go`. Each row is one model in one currency.
2. **Append** a `rateGeneration` to the row's `Rates`; never edit an existing
   one. Set `From` to the first billed day (`YYYY-MM-DD`, UTC) when the change
   is announced ahead of time.
3. Leave the earlier generation where it is: `SupersededRates` reads it so a
   stored price that matches it is recognised as ours and refreshed.
4. Update the row's `CheckedOn` constant to the day you confirmed the page.
5. Add a test beside `rates_test.go` that pins `CurrentRate` before and after
   the `From` day by replacing `today`.
6. Run `make check`. `make pricecheck` needs the network and is run by hand.
