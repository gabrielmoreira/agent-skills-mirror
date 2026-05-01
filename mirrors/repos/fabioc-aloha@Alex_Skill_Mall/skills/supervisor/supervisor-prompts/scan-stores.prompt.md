---
description: "Fetch plugin store updates and generate adoption candidates matched against fleet needs"
mode: agent
lastReviewed: 2026-05-01
---

# Scan Stores

Run the store-adoption workflow: fetch all 4 plugin stores, inventory plugins, match against fleet profile, generate candidates report.

## Steps

1. Run `node scripts/store-sync.cjs` from the Supervisor repo root. This fetches all stores and writes `fleet/STORE-INVENTORY.md` + `fleet/store-inventory.json`.
2. Read `fleet/STORE-INVENTORY.md` (plugin descriptions) and `fleet/fleet-profile.json` (heir needs).
3. For each store (production first), semantically match plugins against heir missions and needs. Skip Microsoft-internal tools that require internal infrastructure. Present the top 10 genuine candidates as a table with rationale.
4. For each candidate the user approves, route to Mall, heir local/, or defer per the store-adoption skill.
5. Update `fleet/fleet-profile.json` if needs changed.
