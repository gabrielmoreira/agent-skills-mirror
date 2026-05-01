# Common Sequence Diagram Patterns

This file contains pre-built patterns for common sequence diagram scenarios.

## Table of Contents

1. Authentication and Authorization
2. API Request/Response Patterns
3. Database Transactions
4. Microservices Communication
5. Error Handling
6. Caching Patterns
7. Asynchronous Processing
8. Event-Driven Architecture

## 1. Authentication and Authorization

### Basic Login Flow

```
title User Login Flow

actor User
participant WebApp
control AuthService
database UserDB

User->WebApp: Enter credentials
WebApp->AuthService: POST /login

activate AuthService
AuthService->UserDB: SELECT user WHERE email=?
UserDB-->AuthService: User record

alt Valid credentials
  note over AuthService: Verify password hash
  AuthService->AuthService: Generate JWT token
  AuthService-->WebApp: 200 OK + token
  WebApp-->User: Redirect to dashboard
else Invalid credentials
  AuthService-->WebApp: 401 Unauthorized
  WebApp-->User: Show error message
end

deactivate AuthService
```

### OAuth 2.0 Authorization Code Flow

```
title OAuth 2.0 Authorization Code Flow

actor User
participant ClientApp
participant AuthServer
participant ResourceServer

User->ClientApp: Initiate login
ClientApp->AuthServer: Authorization request
AuthServer->User: Login page
User->AuthServer: Enter credentials

AuthServer-->ClientApp: Authorization code
ClientApp->AuthServer: Exchange code for token
AuthServer-->ClientApp: Access token

ClientApp->ResourceServer: API request + token
ResourceServer->AuthServer: Validate token
AuthServer-->ResourceServer: Token valid
ResourceServer-->ClientApp: Protected resource
ClientApp-->User: Display data
```

## 2. API Request/Response Patterns

### REST API CRUD Operations

```
title REST API CRUD Flow

participant Client
control API
database Database

==Create==
Client->API: POST /users
API->Database: INSERT INTO users
Database-->API: New user ID
API-->Client: 201 Created

==Read==
Client->API: GET /users/123
API->Database: SELECT * FROM users WHERE id=123
Database-->API: User data
API-->Client: 200 OK + user

==Update==
Client->API: PUT /users/123
API->Database: UPDATE users SET ... WHERE id=123
Database-->API: Rows affected
API-->Client: 200 OK

==Delete==
Client->API: DELETE /users/123
API->Database: DELETE FROM users WHERE id=123
Database-->API: Rows deleted
API-->Client: 204 No Content
```

### Pagination and Filtering

```
title API Pagination Flow

participant Client
control API
database Database

Client->API: GET /users?page=1&limit=10&sort=name

note over API: Parse query parameters
API->Database: SELECT * FROM users\nORDER BY name\nLIMIT 10 OFFSET 0

Database-->API: User records + total count

note over API: Build response with metadata
API-->Client: 200 OK\n{\n  data: [...],\n  page: 1,\n  total: 150,\n  hasNext: true\n}
```

## 3. Database Transactions

### Transaction with Rollback

```
title Database Transaction with Error Handling

control Service
database Database

Service->Database: BEGIN TRANSACTION

alt All operations succeed
  Service->Database: INSERT INTO orders
  Service->Database: UPDATE inventory
  Service->Database: INSERT INTO order_items

  note over Service,Database: All operations successful

  Service->Database: COMMIT
  Database-->Service: Transaction complete
else Operation fails
  Service->Database: INSERT INTO orders
  Service-xDatabase: UPDATE inventory (FAILS)

  note over Service,Database: Error detected

  Service->Database: ROLLBACK
  Database-->Service: Transaction rolled back
end
```

### Two-Phase Commit

```
title Distributed Transaction (2PC)

control Coordinator
database DatabaseA
database DatabaseB

Coordinator->DatabaseA: Prepare transaction
Coordinator->DatabaseB: Prepare transaction

par Prepare Phase
  DatabaseA-->Coordinator: Ready
else
  DatabaseB-->Coordinator: Ready
end

alt All participants ready
  Coordinator->DatabaseA: Commit
  Coordinator->DatabaseB: Commit

  par Commit Phase
    DatabaseA-->Coordinator: Committed
  else
    DatabaseB-->Coordinator: Committed
  end
else Any participant fails
  Coordinator->DatabaseA: Abort
  Coordinator->DatabaseB: Abort
end
```

## 4. Microservices Communication

### Service-to-Service Call Chain

```
title Microservices Order Processing

participant APIGateway
control OrderService
control InventoryService
control PaymentService
control NotificationService
database OrderDB

APIGateway->OrderService: POST /orders

OrderService->InventoryService: Check availability
InventoryService-->OrderService: Items available

OrderService->PaymentService: Process payment
PaymentService-->OrderService: Payment confirmed

par Store and Notify
  OrderService->OrderDB: Save order
  OrderDB-->OrderService: Order saved
else
  OrderService->>NotificationService: Send confirmation email
  note right of NotificationService: Async processing
end

OrderService-->APIGateway: Order created
```

### Circuit Breaker Pattern

```
title Circuit Breaker Pattern

control ServiceA
control ServiceB

ServiceA->ServiceB: Request 1
ServiceB-->ServiceA: Success

ServiceA->ServiceB: Request 2
ServiceB-xServiceA: Timeout

ServiceA->ServiceB: Request 3
ServiceB-xServiceA: Error

note over ServiceA: Circuit opens after\nthreshold reached

ServiceA->ServiceA: Request 4 (Circuit OPEN)
ServiceA-->ServiceA: Fail fast

space

note over ServiceA: Wait period expires

ServiceA->ServiceB: Request 5 (Circuit HALF-OPEN)
ServiceB-->ServiceA: Success

note over ServiceA: Circuit closes\nService restored
```

## 5. Error Handling

### Retry with Exponential Backoff

```
title Retry with Exponential Backoff

control Client
control Service

Client->Service: Request (attempt 1)
Service-xClient: 503 Service Unavailable

note over Client: Wait 1 second

Client->Service: Request (attempt 2)
Service-xClient: 503 Service Unavailable

note over Client: Wait 2 seconds

Client->Service: Request (attempt 3)
Service-xClient: 503 Service Unavailable

note over Client: Wait 4 seconds

Client->Service: Request (attempt 4)
Service-->Client: 200 OK

note over Client: Success
```

### Graceful Degradation

```
title Graceful Degradation

participant User
control PrimaryService
control FallbackService
database Cache

User->PrimaryService: Request data

alt Primary service healthy
  PrimaryService-->User: Full response
else Primary service down
  PrimaryService-xUser: Timeout

  note over PrimaryService: Fallback to cache

  opt Cache available
    PrimaryService->Cache: Get cached data
    Cache-->PrimaryService: Stale data
    PrimaryService-->User: Cached response\n(degraded)
  else Cache miss
    PrimaryService->FallbackService: Request minimal data
    FallbackService-->PrimaryService: Basic response
    PrimaryService-->User: Minimal response\n(degraded)
  end
end
```

## 6. Caching Patterns

### Cache-Aside (Lazy Loading)

```
title Cache-Aside Pattern

control Application
database Cache
database Database

Application->Cache: GET user:123

alt Cache hit
  Cache-->Application: User data
  note right of Application: Fast response
else Cache miss
  Cache-->Application: null

  Application->Database: SELECT * FROM users\nWHERE id=123
  Database-->Application: User data

  Application->Cache: SET user:123
  note over Application,Cache: Populate cache for\nnext request
end

Application-->Application: Return user data
```

### Write-Through Cache

```
title Write-Through Cache Pattern

control Application
database Cache
database Database

Application->Cache: SET user:123
Application->Database: UPDATE users\nWHERE id=123

par Write to both
  Cache-->Application: OK
else
  Database-->Application: OK
end

note over Application: Both updated\nsynchronously
```

### Cache Invalidation

```
title Cache Invalidation

control ServiceA
control ServiceB
database Cache
database Database

ServiceA->Database: UPDATE user
Database-->ServiceA: Updated

ServiceA->Cache: DELETE user:123
Cache-->ServiceA: Invalidated

note over ServiceA: Publish invalidation event
ServiceA->>ServiceB: UserUpdated event

ServiceB->Cache: DELETE user:123
note over ServiceB: Other services\ninvalidate their cache
```

## 7. Asynchronous Processing

### Message Queue Pattern

```
title Message Queue Processing

participant Producer
control MessageQueue
participant Consumer
database Database

Producer->>MessageQueue: Publish message
note over Producer: Returns immediately

note over MessageQueue: Message queued

Consumer->MessageQueue: Poll for messages
MessageQueue-->Consumer: Deliver message

activate Consumer
Consumer->Database: Process message
Database-->Consumer: Success
Consumer->MessageQueue: ACK message
deactivate Consumer

note over MessageQueue: Message removed\nfrom queue
```

### Saga Pattern

```
title Saga Pattern (Orchestration)

control Orchestrator
control ServiceA
control ServiceB
control ServiceC

Orchestrator->ServiceA: Step 1: Create order
ServiceA-->Orchestrator: Order created

Orchestrator->ServiceB: Step 2: Reserve inventory
ServiceB-->Orchestrator: Inventory reserved

Orchestrator->ServiceC: Step 3: Process payment
ServiceC-xOrchestrator: Payment failed

note over Orchestrator: Compensate previous steps

Orchestrator->ServiceB: Compensate: Release inventory
ServiceB-->Orchestrator: Inventory released

Orchestrator->ServiceA: Compensate: Cancel order
ServiceA-->Orchestrator: Order cancelled

Orchestrator-->Orchestrator: Saga failed
```

## 8. Event-Driven Architecture

### Event Sourcing

```
title Event Sourcing Pattern

control CommandHandler
database EventStore
control EventProcessor
database ReadModel

CommandHandler->EventStore: Append event:\nOrderCreated

EventStore-->CommandHandler: Event stored

EventStore->>EventProcessor: Publish event

EventProcessor->ReadModel: Update projection
note over EventProcessor,ReadModel: Build current state\nfrom events
```

### CQRS (Command Query Responsibility Segregation)

```
title CQRS Pattern

participant Client
control CommandService
control QueryService
database WriteDB
database ReadDB

==Command (Write)==
Client->CommandService: Create order
CommandService->WriteDB: INSERT order
WriteDB-->CommandService: Success

note over CommandService: Publish event
CommandService->>ReadDB: OrderCreated event
ReadDB->ReadDB: Update denormalized view

CommandService-->Client: Command accepted

space

==Query (Read)==
Client->QueryService: Get order details
QueryService->ReadDB: SELECT from view
ReadDB-->QueryService: Optimized data
QueryService-->Client: Order details
```

## Usage Tips

- Copy and adapt these patterns to your specific use case
- Modify participant names to match your domain
- Adjust error cases based on your requirements
- Combine patterns as needed for complex flows
- Add notes to document business logic specific to your context
