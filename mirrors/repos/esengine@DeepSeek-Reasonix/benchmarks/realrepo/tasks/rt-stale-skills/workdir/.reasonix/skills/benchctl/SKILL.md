---
name: benchctl
description: Check a rate, a cost, a peak schedule or an arm name from the command line instead of writing a test.
---

# Using benchctl

1. Price a request with `benchctl quote -provider mimo -model mimo-v2.5 -tokens 1000000`;
   it prints the amount and the currency.
2. Read today's card with `benchctl rate -vendor deepseek -model deepseek-flash`.
3. Ask whether a vendor is in its peak window with
   `benchctl peak -currency CNY -at 1791770400` (Unix seconds).
4. List the ablation modules with `benchctl arms`, and name an arm with
   `benchctl arm -ablate planner,evidence -index half`.
5. Every subcommand prints its flags with `-h`.
