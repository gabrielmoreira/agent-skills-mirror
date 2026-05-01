---
applyTo: "src/api/**,src/controllers/**,src/resolvers/**,src/services/**,src/wrappers/**,src/transformers/**,src/middleware/**"
---
# API Architecture Standards

## The Request Lifecycle

Every API request in this project follows this exact path:

```
Client Request
      ↓
Controller / Resolver          ← Entry point. Auth + Authorization here ONLY.
      ↓
Service                        ← Business logic. Orchestrates the flow.
      ↓
API Wrapper                    ← One wrapper per external API. Handles HTTP.
      ↓
External API (3rd party)       ← Dynamics, Stripe, SendGrid, etc.
      ↓
API Wrapper (receives response)
      ↓
Transformer                    ← Maps external shape → internal shape.
      ↓
Service (receives clean data)
      ↓
Controller / Resolver          ← Sends final response to client.
```

---

## Layer Responsibilities — What Goes Where

### Controller / Resolver (`src/controllers/` or `src/resolvers/`)
**Only these things:**
- Parse and validate the incoming request (use zod/class-validator)
- Check authentication (`req.user` must exist if protected)
- Check authorization (role/permission check)
- Call the service with clean, typed input
- Return the service result to the client

**Never in a controller:**
- Business logic
- Direct external API calls
- Database queries
- Data transformation

```typescript
// ✅ Correct controller
async createOrder(req: Request, res: Response) {
  const payload = createOrderSchema.parse(req.body)   // validate
  requireRole(req.user, 'manager')                    // authorize
  const result = await this.orderService.createOrder(payload)
  return res.json(result)
}
```

---

### Service (`src/services/`)
**Only these things:**
- Analyze the incoming payload to decide what to do
- Orchestrate calls to API wrappers or repositories
- Apply business rules (conditionals, calculations, validations)
- Combine data from multiple sources
- Return the final result to the controller

**Never in a service:**
- HTTP calls (use the wrapper)
- Response formatting for HTTP (that's the controller)
- Raw SQL (use repositories)

```typescript
// ✅ Correct service
async createOrder(payload: CreateOrderInput) {
  const customer = await this.dynamicsWrapper.getCustomer(payload.customerId)
  if (!customer.isActive) throw new Error('Inactive customer')
  const order = await this.dynamicsWrapper.createOrder({
    ...payload,
    accountId: customer.accountId    // business rule: use accountId not customerId
  })
  return order   // already transformed by the wrapper
}
```

---

### API Wrapper (`src/wrappers/`)
**Only these things:**
- Hold the base URL, auth token/credentials for ONE external API
- Make the actual HTTP calls (axios, fetch)
- Handle external API authentication (refresh tokens, re-auth)
- Handle retry logic and transport errors
- Call the appropriate transformer on the response
- Return clean, typed internal objects to the service

**Never in a wrapper:**
- Business logic
- Decisions about WHAT to call (that's the service's job)

```typescript
// ✅ Correct wrapper
async getCustomer(customerId: string): Promise<Customer> {
  const token = await this.getAuthToken()   // handles token refresh
  const response = await axios.get(
    `${this.baseUrl}/accounts(${customerId})`,
    { headers: { Authorization: `Bearer ${token}` } }
  )
  return customerTransformer.fromDynamics(response.data)  // always transform
}
```

---

### Transformer (`src/transformers/`)
**Only these things:**
- Map external API field names → internal field names
- Convert external data types → internal types (dates, enums, etc.)
- Strip fields the service doesn't need
- Never add business logic — pure data mapping

```typescript
// ✅ Correct transformer
export const customerTransformer = {
  fromDynamics: (raw: DynamicsAccount): Customer => ({
    id: raw.accountid,               // external: accountid → internal: id
    name: raw.name,
    email: raw.emailaddress1,        // external: emailaddress1 → internal: email
    isActive: raw.statecode === 0,   // enum conversion
    createdAt: new Date(raw.createdon)  // string → Date
  })
}
```

---

## External API Documentation

Every external API this project integrates with has a doc in `docs/external-apis/`:

```
docs/external-apis/
├── dynamics/
│   ├── README.md              ← Auth, base URL, rate limits, common patterns
│   ├── accounts.api.md        ← Account entity: fields, queries, operations
│   ├── contacts.api.md        ← Contact entity: fields, queries, operations
│   └── orders.api.md          ← Order entity: fields, queries, operations
├── [other-external-api]/
│   └── README.md
└── README.md                  ← Index of all external APIs
```

**When adding new external API calls → ALWAYS check this folder first.**
If the doc doesn't exist, create it using `docs/templates/external-api-doc-template.md`.

---

## API Wrapper Documentation

Every wrapper class has its own doc in `docs/apis/wrappers/`:

```
docs/apis/wrappers/
├── dynamics-wrapper.md        ← All methods, what they call, what they return
├── [other-wrapper].md
└── README.md
```

---

## Adding a New External API Call — The Checklist

When adding a new call to an external API:

1. **Check** `docs/external-apis/[api-name]/` — does the entity/endpoint doc exist?
   - If not → create it using the external API doc template
2. **Add the method** to the existing wrapper class
3. **Create a transformer** mapping for the response shape
4. **Add a service method** with the business logic
5. **Add the controller/resolver endpoint** with auth
6. **Write tests** for each layer (unit-test each layer independently)
7. **Update** `docs/apis/wrappers/[wrapper].md` with the new method
8. **Update** the corresponding `docs/apis/[domain]/[endpoint].api.md`

Use the `/add-new-api` prompt to get Copilot to walk through this automatically.
