# Tactical building blocks

The patterns that shape code inside one full-depth bounded context. Each exists to make the model explicit and its rules hard to break. Use a pattern only when it expresses something real: a factory or specification with no rule inside is ceremony.

## Contents

- [Value objects](#value-objects)
- [Entities](#entities)
- [Aggregates](#aggregates)
- [Domain events](#domain-events)
- [Domain services and application services](#domain-services-and-application-services)
- [Repositories](#repositories)
- [Factories](#factories)
- [Specifications](#specifications)
- [Supple design](#supple-design)

## Value objects

Defined only by their attributes: money, a date range, an address, a document type. Immutable, compared by value, validated at construction, and carrying behavior. Use far more of them than feels natural, and model *whole values*: a `FullName`, not two strings. If you are about to pass a primitive that has rules (an amount, an ID, a percentage, an email), make it a value object, and invalid states can't exist anywhere.

```ts
export class ValidityPeriod {
  private constructor(readonly from: Date, readonly until: Date) {}

  static of(from: Date, until: Date): ValidityPeriod {
    if (until <= from) throw new DomainError("Validity must end after it starts");
    return new ValidityPeriod(from, until);
  }

  contains(instant: Date): boolean {
    return instant >= this.from && instant < this.until;
  }

  extendBy(days: number): ValidityPeriod { // returns a new value
    return ValidityPeriod.of(this.from, new Date(this.until.getTime() + days * 86_400_000));
  }

  equals(other: ValidityPeriod): boolean {
    return this.from.getTime() === other.from.getTime()
      && this.until.getTime() === other.until.getTime();
  }
}
```

## Entities

An identity that persists while attributes change: a customer, an order, a credential. Equality by identity. Keep entities about behavior and invariants; push descriptive data into value objects.

Identity can come from the user, the application (a UUID), the database, or another context. Generate it early, in the application before saving, because events raised at creation need the ID.

## Aggregates

A cluster of entities and values changed as one unit, with a single **root** as the only entry point. Its sole purpose is to protect invariants. Outside code holds references only to the root, and only roots load from a repository.

Evans's example: a purchase order whose lines must never exceed an approved total. Two people editing different lines at once each make a valid change that together breaks the limit, so the order and its lines are one aggregate, changed and locked as a whole.

**Vernon's four rules**

| # | Rule | Why |
| --- | --- | --- |
| 1 | Model true invariants in consistency boundaries | Only rules that must hold *immediately* justify clustering objects |
| 2 | Design small aggregates | Big clusters load slowly and collide under concurrency; default to a root plus a few value objects |
| 3 | Reference other aggregates by identity | Hold `productId`, not `product`; keeps boundaries honest and storage flexible |
| 4 | Use eventual consistency outside the boundary | Change one aggregate per transaction; update the others by reacting to its events |

Rule 2 in practice: Vernon's team first modeled a `Product` containing all its backlog items, releases, and sprints. Two people editing unrelated backlog items failed each other's optimistic-concurrency checks. Splitting backlog items, releases, and sprints into separate aggregates that reference the product by ID removed the conflicts.

When someone says "these must be consistent", ask the domain expert what happens if they are out of sync for a few seconds. Usually nothing bad, so they can be separate aggregates.

**Bending the rules** is legitimate when the UI genuinely creates several aggregates in one gesture, there is no messaging yet, the organization mandates global transactions, or query performance needs a direct reference. Break a rule deliberately and record why in an ADR.

```ts
type CredentialStatus = "valid" | "suspended" | "revoked";

export class Credential {
  private pending: DomainEvent[] = [];

  private constructor(
    readonly id: CredentialId,
    readonly holderId: HolderId,        // another aggregate, by identity
    readonly docType: DocType,          // value object
    private status: CredentialStatus,
    private validity: ValidityPeriod,   // value object
  ) {}

  static issue(id: CredentialId, holder: HolderId, docType: DocType,
               validity: ValidityPeriod, at: Date): Credential {
    const c = new Credential(id, holder, docType, "valid", validity);
    c.record({ type: "CredentialIssued", credentialId: id, docType, occurredOn: at });
    return c;
  }

  revoke(reason: RevocationReason, at: Date): void {
    if (this.status === "revoked") return; // idempotent
    this.status = "revoked";
    this.record({ type: "CredentialRevoked", credentialId: this.id, reason, occurredOn: at });
  }

  isPresentable(now: Date): boolean {
    return this.status === "valid" && this.validity.contains(now);
  }

  pullEvents(): DomainEvent[] { const e = this.pending; this.pending = []; return e; }
  private record(e: DomainEvent) { this.pending.push(e); }
}
```

Note what is *not* an aggregate here: a `Wallet` holding every credential. Credentials share no invariant, so one big root would only add contention and slow loads; the wallet is a read model over many small aggregates.

## Domain events

Something that happened that domain experts care about, named in the past tense in the language (`BacklogItemCommitted`, `CredentialRevoked`). Immutable, carrying the aggregate's identity, a timestamp, and just enough data for subscribers to act. Listen for "when…", "if that happens…", "notify…", and "after…": each usually hides one. Event Storming is a workshop built on exactly this.

**Publishing.** The aggregate records events while handling a command; the application service publishes them after saving. To avoid saving the aggregate and losing the event, or the reverse, store events in the same transaction as the aggregate and forward them to the broker afterwards (a *transactional outbox*).

```ts
export class RevokeCredential {
  constructor(private repo: CredentialRepository,
              private events: EventPublisher,
              private clock: Clock) {}

  async execute(cmd: { credentialId: string; reason: RevocationReason }) {
    const credential = await this.repo.byId(CredentialId.from(cmd.credentialId));
    if (!credential) throw new NotFound("credential", cmd.credentialId);

    credential.revoke(cmd.reason, this.clock.now());    // the domain decides
    await this.repo.save(credential);                   // one aggregate per transaction
    await this.events.publish(credential.pullEvents()); // others react later
  }
}
```

**Receivers** are:

- *idempotent*: the same event processed twice has the effect of once, since messages are redelivered;
- *order-tolerant*: they carry versions or timestamps when order matters;
- *translated at the border*: an event from another context passes through the ACL before touching the model;
- *explicit about in-flight states*: while waiting on another context, the model says so (requested, ready, failed).

**Long-running processes.** When a workflow spans contexts, model its progress. In Vernon's example, creating a product requests a discussion from Collaboration; the product holds the discussion's availability as a status and moves it forward when the matching event arrives. Failures and timeouts become visible states, not exceptions lost in a log.

**Offline is a domain concept.** On a device, eventual consistency is a fact. A credential's status carries *when it was last confirmed*, and a presentation policy decides what is acceptable ("status confirmed within 24 hours"): a specification experts can read and argue about, instead of a timeout buried in a network client.

## Domain services and application services

| | Domain service | Application service |
| --- | --- | --- |
| Lives in | Domain model | Application layer |
| Holds | A business operation spanning several objects, or an external policy | Coordination: load, call, save, publish |
| Example | `TransferPolicy.canTransfer(a, b, amount)` | `TransferFunds.execute(cmd)` |
| Knows | Domain types only | Repositories, transactions, security, events |

Both are stateless and named in the language. The *anemic domain model* is the failure: entities as bags of getters and setters while services hold all the logic. Move behavior onto the objects that own the data.

## Repositories

The illusion of an in-memory collection of aggregate roots: one per aggregate type, never one per table or child entity. The interface (a port) lives in the domain; the implementation (an adapter) lives outside.

| Flavor | Behaves like | Fits |
| --- | --- | --- |
| Collection-oriented | A set: add once, changes tracked automatically | ORMs with a unit of work |
| Persistence-oriented | Explicit `save()` after each change | Document and key-value stores, mobile storage, most TypeScript |

```ts
export interface CredentialRepository {
  nextId(): CredentialId;
  byId(id: CredentialId): Promise<Credential | undefined>;
  matching(spec: Specification<Credential>): Promise<Credential[]>;
  save(credential: Credential): Promise<void>;
}
```

## Factories

Creation of a complex object or aggregate so that it is born valid. Often a method on another aggregate root, which reads like the language and enforces the rule:

```ts
class Forum {
  startDiscussion(id: DiscussionId, author: Author, subject: string): Discussion {
    if (this.closed) throw new DomainError("Cannot start a discussion in a closed forum");
    return Discussion.start(this.tenant, this.id, id, author, subject);
  }
}
```

## Specifications

A business rule as a named predicate object, used to validate an object, select objects from a collection, or describe what to build. The standard way to make an implicit rule explicit.

```ts
interface Specification<T> { isSatisfiedBy(candidate: T): boolean; }

class CanAnswerRequest implements Specification<Credential> {
  constructor(private request: PresentationRequest, private now: Date) {}

  isSatisfiedBy(c: Credential): boolean {
    return c.docType.equals(this.request.docType)
      && c.isPresentable(this.now)
      && c.hasAttributes(this.request.requestedAttributes);
  }
}
```

## Supple design

Good models are discovered over many conversations, not designed up front. Evans's loan-syndication team fought special cases in lenders' shares until they saw that shares were a value with their own arithmetic (a "share pie" that adds, scales, and prorates); modeled that way, the special cases disappeared.

| Practice | In code |
| --- | --- |
| Intention-revealing interfaces | Names state effect and purpose, so callers never read the implementation |
| Side-effect-free functions | As much logic as possible in functions that return results, usually on value objects |
| Assertions | Pre- and post-conditions and invariants stated in code and tests |
| Conceptual contours | Code split along the domain's natural seams, so changes stay local |
| Standalone classes | Few dependencies; a class understandable alone |
| Closure of operations | Operations returning their inputs' type (value + value = value) compose cleanly |
| Declarative style | Specifications and values combined to describe rules, not step-by-step procedures |

**Distillation** keeps effort on the core: a one-page *domain vision statement*, core modules marked as core, complex algorithms pulled out as *cohesive mechanisms* so the core stays expressive, and core concepts *segregated* from supporting code.
