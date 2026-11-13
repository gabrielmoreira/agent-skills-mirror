# Strategic design

Where most of DDD's value lives: deciding what the models are, where each stops, and how they talk. Tactical patterns inside a context come second; entities and repositories with no boundaries or language behind them are DDD in name only.

## Subdomains: the problem space

Map the business before drawing boundaries in software.

| Kind | What it is | Investment |
| --- | --- | --- |
| Core | What makes the business distinct and worth building in-house | Best people, deepest modeling, full DDD |
| Supporting | Specific to the business, but no differentiator | Build simply; a good-enough model; maybe outsource |
| Generic | A solved problem every business has (identity, billing, email, notifications) | Buy, use open source, or keep it minimal |

In Vernon's case study, Agile Project Management is core, Collaboration is supporting, and Identity & Access is generic. A month spent perfecting the notification model while the core stays muddy is a strategic error.

## Bounded contexts: the solution space

A bounded context is an explicit boundary, usually a module, package, or service owned by one team, inside which one model and one language hold consistently. The same word may mean different things in different contexts, and that is fine: a *Customer* in sales, billing, and shipping are three related but distinct concepts, and one shared class serving all three becomes a mess.

Aim for one bounded context per subdomain. A legacy system that sprawls across many subdomains with one model is a *big ball of mud*: no rewrite needed, but put a boundary around it.

Signals that a boundary is needed:

- The same entity has optional fields only some features use.
- Two teams keep breaking each other's assumptions about a shared model.
- Experts from different departments disagree about what a term means, and both are right.

## Context map

The context map documents every bounded context and the relationship between each pair that talks: who depends on whom, who adapts to whom, how they integrate. It is as much about teams and politics as about code. *Upstream* is the side whose changes flow to the other; *downstream* is the side that depends on it.

| Pattern | Use when | Watch for |
| --- | --- | --- |
| Partnership | Two teams succeed or fail together and coordinate releases | Becoming permanently coupled |
| Shared kernel | A small, stable model genuinely belongs to both | The kernel growing; every change needs both teams |
| Customer / supplier | Downstream's needs can shape upstream's plans | Upstream's priorities silently winning |
| Conformist | Upstream won't change and its model is acceptable | Importing a poor model into your core |
| Anticorruption layer (ACL) | You must integrate with a model you don't want: legacy, vendor, a standard's library | Translation is real work; test it well |
| Open host service | Many consumers need the same capabilities | Designing the protocol for one consumer |
| Published language | A documented exchange format, often paired with an open host service | Leaking internal model details into it |
| Separate ways | Integration costs more than it gives | Duplicated effort later |

Vernon's example: Collaboration calls Identity & Access over REST through an ACL. It never imports `User` or `Role`; it translates them into its own value objects, `Author`, `Moderator`, and `Participant`, because inside a forum that is what a person is.

An ACL is one adapter that knows the foreign shapes and returns domain types:

```ts
// adapters/mdoc/MdocRequestTranslator.ts: the only file that knows the library's shapes
export class MdocRequestTranslator {
  toDomain(raw: ExternalDeviceRequest): PresentationRequest {
    const docs = raw.docRequests.map(d =>
      RequestedDocument.of(
        DocType.of(d.itemsRequest.docType),
        Object.entries(d.itemsRequest.nameSpaces).flatMap(([ns, items]) =>
          Object.entries(items).map(([name, intentToRetain]) =>
            RequestedAttribute.of(ns, name, intentToRetain)))));
    return PresentationRequest.of(docs, Verifier.fromReaderAuth(raw.readerAuth));
  }
}
```

## Integration styles

| Style | Strengths | Costs |
| --- | --- | --- |
| Synchronous API (REST, RPC, in-process call) | Simple to reason about; immediate answer | Temporal coupling: when upstream is down, so are you |
| Messaging with domain events | Autonomy, resilience, a natural audit trail | Eventual consistency; idempotency and ordering to handle |
| Shared database | Fast to start | Hidden coupling; avoid it between contexts |

Default: query synchronously when you need an answer now; publish an event when announcing that something happened. Inside one process, "messaging" can be an in-memory event bus; the boundary is about ownership, not infrastructure.

## Worked example: a digital-identity wallet

| Subdomain | Kind | Why |
| --- | --- | --- |
| Credential lifecycle (issue, store, status, renew) | Core | Where trust, validity, and the experience are decided |
| Presentation (proximity and remote disclosure) | Core | Selective disclosure and consent are the product's value |
| Payments | Supporting | Important, but follows external schemes |
| App user identity, device attestation | Generic-ish | Largely standardized; reuse providers and libraries |
| Notifications, analytics | Generic | Buy or use platform services |

| Upstream → downstream | Relationship | Notes |
| --- | --- | --- |
| Issuer services → Credential lifecycle | Customer/supplier + ACL | Translate issuer formats into `Credential`, `DocType`, `ValidityPeriod` |
| ISO 18013-5 mdoc library → Presentation | Conformist on the wire, ACL inside | The standard is non-negotiable; its CBOR structures stay in the adapter |
| Credential lifecycle → Presentation | Published language (events) | `CredentialIssued` and `CredentialRevoked` keep presentation's read model current |
| Status/revocation service → Credential lifecycle | Open host service | Polled or pushed; offline periods modeled explicitly |
