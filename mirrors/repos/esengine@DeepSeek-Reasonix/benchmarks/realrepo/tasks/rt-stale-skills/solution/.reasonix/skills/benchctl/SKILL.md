---
name: benchctl
description: Check a rate, a cost, a peak schedule or an arm name from the command line instead of writing a test.
---

# Using benchctl

1. Price a request with
   `go run ./cmd/benchctl cost -provider mimo -model mimo-v2.5 -miss 1000000`;
   `-hit` and `-completion` add cached prompt and completion tokens. It prints
   the amount and the currency.
2. Read today's card with `go run ./cmd/benchctl rate -provider deepseek -model deepseek-flash`;
   `-currency` picks a currency, otherwise the vendor's default is used.
3. Ask whether a vendor is in its peak window with
   `go run ./cmd/benchctl tariff -currency CNY -at 2026-10-12T02:00:00Z`; `-at`
   takes an RFC 3339 instant and defaults to now.
4. List the ablation modules with `go run ./cmd/benchctl arm -list`, and name an
   arm with `go run ./cmd/benchctl arm -ablate planner,evidence -fold-index half`.
5. Every subcommand prints its flags with `-h`.
