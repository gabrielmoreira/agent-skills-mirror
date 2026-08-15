---
name: hubspot-integration
description: "Wires HubSpot CRM through Private App tokens or OAuth 2.0: object CRUD, associations v4, batches of at most 100, HMAC-validated webhooks, and Enterprise custom objects. Trigger on hubspot api, contacts, deals, or HubSpot webhooks. Do not use for Salesforce, Stripe billing, or legacy HubSpot API keys."
version: 1.0.1
risk: unknown
source: vibeship-spawner-skills (Apache 2.0)
date_added: 2026-02-27
---

## Overview
Expert patterns for HubSpot CRM integration including OAuth authentication, CRM objects, associations, batch operations, webhooks, and custom objects. Covers Node.js and Python SDKs.

## When to Use
- User mentions or implies: hubspot, hubspot api, hubspot crm, hubspot integration, contacts api.

## Prerequisites
- Node.js or Python environment.
- HubSpot account (Standard or Enterprise for custom objects).
- Environment variables set for authentication (e.g., `HUBSPOT_PRIVATE_APP_TOKEN`, `HUBSPOT_CLIENT_ID`, `HUBSPOT_CLIENT_SECRET`).

## Procedure

### 1. Authentication
Choose between OAuth 2.0 (public apps) or Private App Tokens (internal integrations).

#### Private App Token (Single Account)
```typescript
import { Client } from "@hubspot/api-client";
const hubspotClient = new Client({
  accessToken: process.env.HUBSPOT_PRIVATE_APP_TOKEN,
});
```
Python equivalent:
```python
from hubspot import HubSpot
client = HubSpot(access_token=os.environ["HUBSPOT_PRIVATE_APP_TOKEN"])
```

#### OAuth 2.0 (Multi-Account)
1. Generate authorization URL.
2. Handle OAuth callback to exchange code for tokens.
3. Refresh access token before 30-minute expiry.
4. Create authenticated client.
```typescript
// OAuth 2.0 flow for HubSpot
import { Client } from "@hubspot/api-client";

const CLIENT_ID = process.env.HUBSPOT_CLIENT_ID;
const CLIENT_SECRET = process.env.HUBSPOT_CLIENT_SECRET;
const REDIRECT_URI = process.env.HUBSPOT_REDIRECT_URI;
const SCOPES = "crm.objects.contacts.read crm.objects.contacts.write";

function getAuthUrl(): string {
  const authUrl = new URL("https://app.hubspot.com/oauth/authorize");
  authUrl.searchParams.set("client_id", CLIENT_ID);
  authUrl.searchParams.set("redirect_uri", REDIRECT_URI);
  authUrl.searchParams.set("scope", SCOPES);
  return authUrl.toString();
}

async function handleOAuthCallback(code: string) {
  const response = await fetch("https://api.hubapi.com/oauth/v1/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "authorization_code",
      client_id: CLIENT_ID,
      client_secret: CLIENT_SECRET,
      redirect_uri: REDIRECT_URI,
      code: code,
    }),
  });
  const tokens = await response.json();
  await storeTokens(tokens);
  return tokens;
}

async function refreshAccessToken(refreshToken: string) {
  const response = await fetch("https://api.hubapi.com/oauth/v1/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "refresh_token",
      client_id: CLIENT_ID,
      client_secret: CLIENT_SECRET,
      refresh_token: refreshToken,
    }),
  });
  return response.json();
}

function createClient(accessToken: string): Client {
  return new Client({ accessToken });
}
```

### 2. CRM Object CRUD Operations
```typescript
// CREATE contact
async function createContact(data: { email: string; firstname: string; lastname: string; }) {
  return await hubspotClient.crm.contacts.basicApi.create({
    properties: { email: data.email, firstname: data.firstname, lastname: data.lastname },
  });
}

// READ contact by ID
async function getContact(contactId: string) {
  return await hubspotClient.crm.contacts.basicApi.getById(contactId, ["firstname", "lastname", "email", "phone", "company"]);
}

// UPDATE contact
async function updateContact(contactId: string, properties: object) {
  return await hubspotClient.crm.contacts.basicApi.update(contactId, { properties });
}

// DELETE contact (Archive)
async function deleteContact(contactId: string) {
  await hubspotClient.crm.contacts.basicApi.archive(contactId);
}

// SEARCH contacts
async function searchContacts(query: string) {
  const response = await hubspotClient.crm.contacts.searchApi.doSearch({
    query, limit: 100, properties: ["firstname", "lastname", "email"],
    sorts: [{ propertyName: "createdate", direction: "DESCENDING" }],
  });
  return response.results;
}

// LIST with pagination
async function getAllContacts() {
  const allContacts = [];
  let after = undefined;
  do {
    const response = await hubspotClient.crm.contacts.basicApi.getPage(100, after, ["firstname", "lastname", "email"]);
    allContacts.push(...response.results);
    after = response.paging?.next?.after;
  } while (after);
  return allContacts;
}
```

### 3. Batch Operations
Max 100 items per batch request.
```typescript
// BATCH CREATE contacts
async function batchCreateContacts(contacts: Array<{ email: string; firstname: string; lastname: string; }>) {
  const inputs = contacts.map((contact) => ({ properties: { email: contact.email, firstname: contact.firstname, lastname: contact.lastname } }));
  const response = await hubspotClient.crm.contacts.batchApi.create({ inputs });
  return response.results;
}

// BATCH UPDATE contacts
async function batchUpdateContacts(updates: Array<{ id: string; properties: object }>) {
  const inputs = updates.map(({ id, properties }) => ({ id, properties }));
  const response = await hubspotClient.crm.contacts.batchApi.update({ inputs });
  return response.results;
}

// BATCH READ contacts by ID
async function batchReadContacts(ids: string[], properties: string[] = ["firstname", "lastname", "email"]) {
  const response = await hubspotClient.crm.contacts.batchApi.read({ inputs: ids.map((id) => ({ id })), properties });
  return response.results;
}

// BATCH ARCHIVE contacts
async function batchDeleteContacts(ids: string[]) {
  await hubspotClient.crm.contacts.batchApi.archive({ inputs: ids.map((id) => ({ id })) });
}
```

### 4. Associations v4 API
Requires SDK version 9.0.0+.
```typescript
import { Client, AssociationTypes } from "@hubspot/api-client";

// CREATE association (Contact to Company)
async function associateContactToCompany(contactId: string, companyId: string) {
  await hubspotClient.crm.associations.v4.basicApi.create("contacts", contactId, "companies", companyId, [
    { associationCategory: "HUBSPOT_DEFINED", associationTypeId: AssociationTypes.contactToCompany }
  ]);
}

// BATCH create associations
async function batchAssociateContactsToCompany(contactIds: string[], companyId: string) {
  const inputs = contactIds.map((contactId) => ({
    _from: { id: contactId }, to: { id: companyId },
    types: [{ associationCategory: "HUBSPOT_DEFINED", associationTypeId: AssociationTypes.contactToCompany }],
  }));
  await hubspotClient.crm.associations.v4.batchApi.create("contacts", "companies", { inputs });
}
```
Common association type IDs: Contact to Company: 1, Company to Contact: 2, Deal to Contact: 3, Contact to Deal: 4, Deal to Company: 5, Company to Deal: 6.

### 5. Webhook Handling
Validate signature before processing. Respond within 5 seconds.
```typescript
import crypto from "crypto";

// Webhook signature validation (v3)
function validateWebhookSignature(requestBody: string, signature: string, clientSecret: string): boolean {
  const expectedSignature = crypto.createHmac("sha256", clientSecret).update(requestBody).digest("hex");
  return signature === expectedSignature;
}

// Express webhook handler
app.post("/webhooks/hubspot", async (req, res) => {
  const signature = req.headers["x-hubspot-signature-v3"] as string;
  const timestamp = req.headers["x-hubspot-request-timestamp"] as string;
  const requestBody = JSON.stringify(req.body);

  const isValid = validateWebhookSignature(requestBody, signature, process.env.HUBSPOT_CLIENT_SECRET);
  if (!isValid) return res.status(401).send("Unauthorized");

  const timestampAge = Date.now() - parseInt(timestamp);
  if (timestampAge > 300000) return res.status(401).send("Timestamp expired");

  const events = req.body;
  for (const event of events) {
    await queue.add("hubspot-webhook", event);
  }
  res.status(200).send("OK");
});
```

### 6. Custom Objects
Requires Enterprise tier. Max 10 custom objects per account.
```typescript
// CREATE custom object schema
async function createCustomObjectSchema() {
  const schema = {
    name: "projects",
    labels: { singular: "Project", plural: "Projects" },
    primaryDisplayProperty: "project_name",
    requiredProperties: ["project_name"],
    properties: [
      { name: "project_name", label: "Project Name", type: "string", fieldType: "text" },
      { name: "status", label: "Status", type: "enumeration", fieldType: "select", options: [
        { label: "Active", value: "active" }, { label: "Completed", value: "completed" }, { label: "On Hold", value: "on_hold" }
      ]},
      { name: "budget", label: "Budget", type: "number", fieldType: "number" },
      { name: "start_date", label: "Start Date", type: "date", fieldType: "date" },
    ],
    associatedObjects: ["CONTACT", "COMPANY"],
  };
  return await hubspotClient.crm.schemas.coreApi.create(schema);
}

// CREATE custom object record
async function createProject(data: { project_name: string; status: string; budget: number; }) {
  return await hubspotClient.crm.objects.basicApi.create("projects", { properties: data });
}
```

## Pitfalls
- **Rate Limits Vary by App Type and Hub Tier (HIGH)**: Implement retry logic with backoff for 429 responses. Unthrottled parallel API calls can exceed rate limits.
- **5% Error Rate Threshold for Marketplace Apps (HIGH)**: Exceeding 5% error rate can affect app status.
- **API Keys Deprecated (CRITICAL)**: Never use API keys. Migrate to Private App tokens or OAuth 2.0.
- **OAuth Access Tokens Expire in 30 Minutes (HIGH)**: Store `expiresAt` for refresh logic. Refresh tokens before expiry.
- **Webhook Requests Must Be Validated (CRITICAL)**: Webhook endpoints must validate `X-HubSpot-Signature-v3`. Check timestamp to prevent replay attacks (max 5 minutes).
- **All List Endpoints Require Pagination (MEDIUM)**: Implement cursor-based pagination.
- **Associations v4 API Has Breaking Changes (HIGH)**: Requires SDK version 9.0.0+.
- **Polling Limited to 100,000 Requests Per Day (MEDIUM)**: Avoid excessive polling; use webhooks where possible.
- **Batch Operations**: Max 100 items per batch request. Partial success is possible; check `response.errors`.
- **Custom Objects**: Require Enterprise tier. Max 10 custom objects per account.

## Verification
- **Hardcoded Secrets Check**: Ensure no hardcoded HubSpot API keys, access tokens, or client secrets exist in the codebase. Use environment variables.
- **Webhook Validation Check**: Verify webhook endpoints validate `X-HubSpot-Signature-v3` and check timestamp age.
- **Rate Limit Handling Check**: Verify API calls handle 429 responses with retry logic.
- **Pagination Check**: Verify list API calls implement cursor-based pagination.
- **Batch Operations Check**: Verify loops over multiple items use batch operations instead of individual API calls.

## Related skills
- email-marketing: For email marketing automation beyond HubSpot's built-in tools.
- frontend: For building custom CRM UI or dashboards.
- data-engineer: For ETL pipelines from HubSpot to data warehouses.
- salesforce-development: For HubSpot + Salesforce synchronization.
- stripe-integration: For payment processing beyond HubSpot quotes.
- analytics-specialist: For custom reporting and analytics dashboards.

## Limitations
- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
