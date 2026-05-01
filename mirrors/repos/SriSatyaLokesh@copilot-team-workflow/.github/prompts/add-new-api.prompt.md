---
description: 'Add a new external API call — walks through the full Controller→Service→Wrapper→Transformer workflow'
agent: 'ApiBuilder'
---
# Add New API Integration

You are adding a new external API call to the project.

## Step 1: Confirm context

Before starting, read the relevant docs by answering these:

**External API**:
- Which external API? (e.g., Dynamics, Stripe): ${input:external-api:Which external API are you calling?}
- Which entity/resource in that API? (e.g., accounts, contacts): ${input:entity:Which entity or resource?}
- What operation? (e.g., GET by ID, list with filters, create): ${input:operation:What operation (get/list/create/update)?}

**Now read**:
1. `#docs/external-apis/${input:external-api}/README.md` — auth and base URL
2. `#docs/external-apis/${input:external-api}/${input:entity}.api.md` — fields and query patterns

> ⚠️ If these docs don't exist: STOP and notify the developer.
> They must fill in `docs/templates/external-api-doc-template.md` first.
> Copilot cannot correctly implement API calls without knowing the exact field names.

## Step 2: Implement in order

Follow the architecture rules in `#.github/instructions/api-architecture.instructions.md`

Implement in this order:
1. **Transformer** — map external fields → internal fields
2. **Wrapper method** — HTTP call + error handling + call transformer
3. **Service method** — business logic using wrapper
4. **Controller/Resolver endpoint** — auth + validation + service call
5. **Tests** — one test file per layer, TDD style
6. **Update docs** — wrapper doc + API endpoint doc

## Step 3: Verify completeness

After implementing, check:
- [ ] Transformer has tests (pure unit, no mocks)
- [ ] Wrapper method handles 404, 429, 5xx correctly
- [ ] Service has business logic (not just passthrough)
- [ ] Controller validates input with schema
- [ ] Controller checks auth/authorization
- [ ] All tests pass: `npm test`
- [ ] Wrapper doc updated: `docs/apis/wrappers/[name]-wrapper.md`
- [ ] API endpoint doc updated: `docs/apis/[domain]/[endpoint].api.md`
