---
name: saga-orchestration
description: "Coordinates multi-service workflows as orchestration or choreography sagas with compensating transactions, durable saga_id state, and step timeouts. Use when order fulfillment, approvals, or distributed rollback spans separate databases and two-phase commit is not viable. Not for single-service local transactions. Never treat sagas as ACID across services."
version: 1.0.1
risk: unknown
source: community
date_added: "2026-02-27"
---

# Saga Orchestration

Patterns and templates for managing distributed transactions and long-running business processes using orchestration or choreography approaches, with compensating transactions for rollback.

## When to Use

Use this skill when:

- Coordinating multi-service transactions that span separate databases or bounded contexts
- Implementing compensating transactions for distributed rollback
- Managing long-running business workflows (order fulfillment, approval pipelines, booking flows)
- Handling failures in distributed systems where two-phase commit is not viable
- Building order fulfillment processes across inventory, payment, shipping, and notification services
- Implementing approval workflows with multi-step state transitions
- Designing event-driven choreography sagas where no central coordinator is desired

## Do Not Use This Skill When

- The task is unrelated to saga orchestration or distributed transactions
- You need a different domain or tool outside this scope
- A single-service local transaction suffices (use standard database transactions)
- You need ACID guarantees across all services (sagas provide eventual consistency only)

## Prerequisites

- Familiarity with asynchronous messaging / event-driven architecture
- A message broker or event bus (e.g., Kafka, RabbitMQ, AWS SNS/SQS, Azure Service Bus)
- A persistence store for saga state (e.g., PostgreSQL, DynamoDB, Cosmos DB)
- Python 3.8+ if using the provided templates directly (templates are language-agnostic in concept but written in Python)
- On Windows host (PowerShell), ensure Python is on PATH:

```powershell
python --version
```

## Overview

### Saga Types

```
Choreography                    Orchestration
┌─────┐  ┌─────┐  ┌─────┐     ┌─────────────┐
│Svc A│─►│Svc B│─►│Svc C│     │ Orchestrator│
└─────┘  └─────┘  └─────┘     └──────┬──────┘
   │        │        │               │
   ▼        ▼        ▼         ┌─────┼─────┐
 Event    Event    Event       ▼     ▼     ▼
                            ┌────┐┌────┐┌────┐
                            │Svc1││Svc2││Svc3│
                            └────┘└────┘└────┘
```

**Choreography**: Each service reacts to events and emits the next event. No central coordinator. Best for simpler flows with few steps.

**Orchestration**: A central orchestrator issues commands to services and tracks state. Best for complex flows with many steps, conditional logic, or strict ordering.

### Saga Execution States

| State            | Description                              |
| ---------------- | ---------------------------------------- |
| **Started**      | Saga initiated, first step dispatched    |
| **Pending**      | Waiting for current step completion      |
| **Compensating** | Rolling back completed steps due to failure |
| **Completed**    | All steps succeeded                      |
| **Failed**       | Saga failed after compensation completed |

## Procedure

### Step 1: Choose Saga Type

1. **Choreography** — Use when the flow is linear, has ≤ 3–4 steps, and services are loosely coupled. Each service subscribes to events and emits the next event.
2. **Orchestration** — Use when the flow has conditional branching, many steps, or you need a single source of truth for saga state. A central orchestrator manages step execution and compensation.

### Step 2: Define Saga Steps and Compensations

For each step, identify:

- **Action**: The command or event that triggers the step
- **Compensation**: The reverse operation that undoes the step's effects
- **Idempotency key**: Ensure the action can be safely retried

Example for order fulfillment:

| Step                | Action                              | Compensation                          |
| ------------------- | ----------------------------------- | ------------------------------------- |
| Reserve inventory   | `InventoryService.ReserveItems`     | `InventoryService.ReleaseReservation` |
| Process payment     | `PaymentService.ProcessPayment`     | `PaymentService.RefundPayment`        |
| Create shipment     | `ShippingService.CreateShipment`    | `ShippingService.CancelShipment`      |
| Send confirmation   | `NotificationService.SendConfirmation` | `NotificationService.SendCancellation` |

### Step 3: Implement the Orchestrator (Orchestration Pattern)

Use the base orchestrator template below. The orchestrator:

1. Creates a saga with a unique `saga_id`
2. Persists saga state to a durable store
3. Dispatches step actions via event publisher
4. Handles step completion / failure callbacks
5. Compensates in reverse order on failure

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

class SagaState(Enum):
    STARTED = "started"
    PENDING = "pending"
    COMPENSATING = "compensating"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class SagaStep:
    name: str
    action: str
    compensation: str
    status: str = "pending"
    result: Optional[Dict] = None
    error: Optional[str] = None
    executed_at: Optional[datetime] = None
    compensated_at: Optional[datetime] = None


@dataclass
class Saga:
    saga_id: str
    saga_type: str
    state: SagaState
    data: Dict[str, Any]
    steps: List[SagaStep]
    current_step: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


class SagaOrchestrator(ABC):
    """Base class for saga orchestrators."""

    def __init__(self, saga_store, event_publisher):
        self.saga_store = saga_store
        self.event_publisher = event_publisher

    @abstractmethod
    def define_steps(self, data: Dict) -> List[SagaStep]:
        """Define the saga steps."""
        pass

    @property
    @abstractmethod
    def saga_type(self) -> str:
        """Unique saga type identifier."""
        pass

    async def start(self, data: Dict) -> Saga:
        """Start a new saga."""
        saga = Saga(
            saga_id=str(uuid.uuid4()),
            saga_type=self.saga_type,
            state=SagaState.STARTED,
            data=data,
            steps=self.define_steps(data)
        )
        await self.saga_store.save(saga)
        await self._execute_next_step(saga)
        return saga

    async def handle_step_completed(self, saga_id: str, step_name: str, result: Dict):
        """Handle successful step completion."""
        saga = await self.saga_store.get(saga_id)

        for step in saga.steps:
            if step.name == step_name:
                step.status = "completed"
                step.result = result
                step.executed_at = datetime.utcnow()
                break

        saga.current_step += 1
        saga.updated_at = datetime.utcnow()

        if saga.current_step >= len(saga.steps):
            saga.state = SagaState.COMPLETED
            await self.saga_store.save(saga)
            await self._on_saga_completed(saga)
        else:
            saga.state = SagaState.PENDING
            await self.saga_store.save(saga)
            await self._execute_next_step(saga)

    async def handle_step_failed(self, saga_id: str, step_name: str, error: str):
        """Handle step failure - start compensation."""
        saga = await self.saga_store.get(saga_id)

        for step in saga.steps:
            if step.name == step_name:
                step.status = "failed"
                step.error = error
                break

        saga.state = SagaState.COMPENSATING
        saga.updated_at = datetime.utcnow()
        await self.saga_store.save(saga)

        await self._compensate(saga)

    async def _execute_next_step(self, saga: Saga):
        """Execute the next step in the saga."""
        if saga.current_step >= len(saga.steps):
            return

        step = saga.steps[saga.current_step]
        step.status = "executing"
        await self.saga_store.save(saga)

        await self.event_publisher.publish(
            step.action,
            {
                "saga_id": saga.saga_id,
                "step_name": step.name,
                **saga.data
            }
        )

    async def _compensate(self, saga: Saga):
        """Execute compensation for completed steps in reverse order."""
        for i in range(saga.current_step - 1, -1, -1):
            step = saga.steps[i]
            if step.status == "completed":
                step.status = "compensating"
                await self.saga_store.save(saga)

                await self.event_publisher.publish(
                    step.compensation,
                    {
                        "saga_id": saga.saga_id,
                        "step_name": step.name,
                        "original_result": step.result,
                        **saga.data
                    }
                )

    async def handle_compensation_completed(self, saga_id: str, step_name: str):
        """Handle compensation completion."""
        saga = await self.saga_store.get(saga_id)

        for step in saga.steps:
            if step.name == step_name:
                step.status = "compensated"
                step.compensated_at = datetime.utcnow()
                break

        all_compensated = all(
            s.status in ("compensated", "pending", "failed")
            for s in saga.steps
        )

        if all_compensated:
            saga.state = SagaState.FAILED
            await self._on_saga_failed(saga)

        await self.saga_store.save(saga)

    async def _on_saga_completed(self, saga: Saga):
        """Called when saga completes successfully."""
        await self.event_publisher.publish(
            f"{self.saga_type}Completed",
            {"saga_id": saga.saga_id, **saga.data}
        )

    async def _on_saga_failed(self, saga: Saga):
        """Called when saga fails after compensation."""
        await self.event_publisher.publish(
            f"{self.saga_type}Failed",
            {"saga_id": saga.saga_id, "error": "Saga failed", **saga.data}
        )
```

### Step 4: Implement a Concrete Saga

```python
class OrderFulfillmentSaga(SagaOrchestrator):
    """Orchestrates order fulfillment across services."""

    @property
    def saga_type(self) -> str:
        return "OrderFulfillment"

    def define_steps(self, data: Dict) -> List[SagaStep]:
        return [
            SagaStep(
                name="reserve_inventory",
                action="InventoryService.ReserveItems",
                compensation="InventoryService.ReleaseReservation"
            ),
            SagaStep(
                name="process_payment",
                action="PaymentService.ProcessPayment",
                compensation="PaymentService.RefundPayment"
            ),
            SagaStep(
                name="create_shipment",
                action="ShippingService.CreateShipment",
                compensation="ShippingService.CancelShipment"
            ),
            SagaStep(
                name="send_confirmation",
                action="NotificationService.SendOrderConfirmation",
                compensation="NotificationService.SendCancellationNotice"
            )
        ]


async def create_order(order_data: Dict):
    saga = OrderFulfillmentSaga(saga_store, event_publisher)
    return await saga.start({
        "order_id": order_data["order_id"],
        "customer_id": order_data["customer_id"],
        "items": order_data["items"],
        "payment_method": order_data["payment_method"],
        "shipping_address": order_data["shipping_address"]
    })
```

### Step 5: Implement Service-Side Handlers

Each service handles action commands and reports success or failure back to the orchestrator:

```python
class InventoryService:
    async def handle_reserve_items(self, command: Dict):
        try:
            reservation = await self.reserve(
                command["items"],
                command["order_id"]
            )
            await self.event_publisher.publish(
                "SagaStepCompleted",
                {
                    "saga_id": command["saga_id"],
                    "step_name": "reserve_inventory",
                    "result": {"reservation_id": reservation.id}
                }
            )
        except InsufficientInventoryError as e:
            await self.event_publisher.publish(
                "SagaStepFailed",
                {
                    "saga_id": command["saga_id"],
                    "step_name": "reserve_inventory",
                    "error": str(e)
                }
            )

    async def handle_release_reservation(self, command: Dict):
        await self.release_reservation(
            command["original_result"]["reservation_id"]
        )
        await self.event_publisher.publish(
            "SagaCompensationCompleted",
            {
                "saga_id": command["saga_id"],
                "step_name": "reserve_inventory"
            }
        )
```

### Step 6: Implement Choreography-Based Saga (Alternative)

When no central orchestrator is desired, use event chaining:

```python
class OrderChoreographySaga:
    """Choreography-based saga using events."""

    def __init__(self, event_bus):
        self.event_bus = event_bus
        self._register_handlers()

    def _register_handlers(self):
        self.event_bus.subscribe("OrderCreated", self._on_order_created)
        self.event_bus.subscribe("InventoryReserved", self._on_inventory_reserved)
        self.event_bus.subscribe("PaymentProcessed", self._on_payment_processed)
        self.event_bus.subscribe("ShipmentCreated", self._on_shipment_created)

        # Compensation handlers
        self.event_bus.subscribe("PaymentFailed", self._on_payment_failed)
        self.event_bus.subscribe("ShipmentFailed", self._on_shipment_failed)

    async def _on_order_created(self, event: Dict):
        await self.event_bus.publish("ReserveInventory", {
            "saga_id": event["order_id"],
            "order_id": event["order_id"],
            "items": event["items"]
        })

    async def _on_inventory_reserved(self, event: Dict):
        await self.event_bus.publish("ProcessPayment", {
            "saga_id": event["saga_id"],
            "order_id": event["order_id"],
            "amount": event["total_amount"],
            "reservation_id": event["reservation_id"]
        })

    async def _on_payment_processed(self, event: Dict):
        await self.event_bus.publish("CreateShipment", {
            "saga_id": event["saga_id"],
            "order_id": event["order_id"],
            "payment_id": event["payment_id"]
        })

    async def _on_shipment_created(self, event: Dict):
        await self.event_bus.publish("OrderFulfilled", {
            "saga_id": event["saga_id"],
            "order_id": event["order_id"],
            "tracking_number": event["tracking_number"]
        })

    async def _on_payment_failed(self, event: Dict):
        await self.event_bus.publish("ReleaseInventory", {
            "saga_id": event["saga_id"],
            "reservation_id": event["reservation_id"]
        })
        await self.event_bus.publish("OrderFailed", {
            "order_id": event["order_id"],
            "reason": "Payment failed"
        })

    async def _on_shipment_failed(self, event: Dict):
        await self.event_bus.publish("RefundPayment", {
            "saga_id": event["saga_id"],
            "payment_id": event["payment_id"]
        })
        await self.event_bus.publish("ReleaseInventory", {
            "saga_id": event["saga_id"],
            "reservation_id": event["reservation_id"]
        })
```

### Step 7: Add Timeouts

Never let a saga step wait indefinitely. Schedule timeout checks:

```python
from datetime import timedelta

class TimeoutSagaOrchestrator(SagaOrchestrator):
    """Saga orchestrator with step timeouts."""

    def __init__(self, saga_store, event_publisher, scheduler):
        super().__init__(saga_store, event_publisher)
        self.scheduler = scheduler

    async def _execute_next_step(self, saga: Saga):
        if saga.current_step >= len(saga.steps):
            return

        step = saga.steps[saga.current_step]
        step.status = "executing"
        step.timeout_at = datetime.utcnow() + timedelta(minutes=5)
        await self.saga_store.save(saga)

        await self.scheduler.schedule(
            f"saga_timeout_{saga.saga_id}_{step.name}",
            self._check_timeout,
            {"saga_id": saga.saga_id, "step_name": step.name},
            run_at=step.timeout_at
        )

        await self.event_publisher.publish(
            step.action,
            {"saga_id": saga.saga_id, "step_name": step.name, **saga.data}
        )

    async def _check_timeout(self, data: Dict):
        saga = await self.saga_store.get(data["saga_id"])
        step = next(s for s in saga.steps if s.name == data["step_name"])

        if step.status == "executing":
            await self.handle_step_failed(
                data["saga_id"],
                data["step_name"],
                "Step timed out"
            )
```

### Step 8: Consider Durable Execution Frameworks

The templates above build saga infrastructure from scratch — saga stores, event publishers, compensation tracking. **Durable execution frameworks** (like DBOS) eliminate much of this boilerplate: the workflow runtime automatically persists state to a database, retries failed steps, and resumes from the last checkpoint after crashes. Instead of building a `SagaOrchestrator` base class, you write a workflow function with steps — the framework handles persistence, crash recovery, and exactly-once execution semantics.

Consider durable execution when you want saga-like reliability without managing the coordination infrastructure yourself.

### Step 9: Load Detailed Examples

If detailed examples or extended implementation patterns are required, open `resources/implementation-playbook.md` for additional walkthroughs, edge cases, and testing strategies.

## Examples

### Minimal Saga Step Definition

```python
steps = [
    SagaStep(
        name="reserve_inventory",
        action="InventoryService.ReserveItems",
        compensation="InventoryService.ReleaseReservation"
    ),
    SagaStep(
        name="process_payment",
        action="PaymentService.ProcessPayment",
        compensation="PaymentService.RefundPayment"
    ),
]
```

### Compensation Flow

1. Step 3 (`create_shipment`) fails
2. Orchestrator sets state to `COMPENSATING`
3. Compensate step 2: `PaymentService.RefundPayment`
4. Compensate step 1: `InventoryService.ReleaseReservation`
5. All compensations complete → state becomes `FAILED`
6. `OrderFulfillmentFailed` event published

## Pitfalls

- **Do not assume instant completion** — Sagas are long-running by nature. Steps may take seconds to minutes. Always persist state and handle async callbacks.
- **Do not skip compensation testing** — Compensations are the most critical part. A failed compensation leaves the system in an inconsistent state. Test every compensation path explicitly.
- **Do not couple services synchronously** — Use async messaging. Synchronous calls between services in a saga create cascading failures and tight coupling.
- **Do not ignore partial failures** — A step may partially succeed (e.g., payment charged but response lost). Design steps to be idempotent so retries are safe.
- **Do not forget correlation IDs** — Without a `saga_id` propagated through all events, tracing and debugging distributed failures becomes nearly impossible.
- **Do not omit timeouts** — A step that never responds will hang the saga forever. Always schedule timeout checks.
- **Do not use sagas when ACID is required** — Sagas provide eventual consistency. If you need strict ACID across services, reconsider your service boundaries or use a shared database.
- **Do not compensate steps that were never completed** — The `_compensate` method checks `step.status == "completed"` before compensating. Ensure your implementation preserves this guard.
- **Do not lose saga state on crash** — The saga store must be durable. In-memory state is unacceptable for production sagas. Persist after every state transition.

## Verification

### Verify Saga State Machine

Check that all state transitions are valid:

```python
# Valid transitions:
# STARTED → PENDING (first step dispatched)
# PENDING → PENDING (step completed, next dispatched)
# PENDING → COMPLETED (last step completed)
# PENDING → COMPENSATING (step failed)
# COMPENSATING → FAILED (all compensations done)
```

### Verify Idempotency

Each step action and compensation must be safely retriable:

```python
# Test: calling reserve_inventory twice with same order_id
# should not create two reservations.
reservation = await inventory_service.reserve(items, order_id)
reservation_2 = await inventory_service.reserve(items, order_id)
assert reservation.id == reservation_2.id  # Idempotent
```

### Verify Compensation Reverses Action

```python
# Test: reserve then release should restore inventory to original state
original_count = await get_inventory(item_id)
await reserve(item_id, quantity=5)
await release_reservation(reservation_id)
assert await get_inventory(item_id) == original_count
```

### Verify Timeout Handling

```python
# Test: step that never responds should trigger timeout
saga = await timeout_orchestrator.start(test_data)
# Wait longer than timeout period
await asyncio.sleep(timeout_minutes * 60 + 1)
saga = await saga_store.get(saga.saga_id)
assert saga.state == SagaState.FAILED
```

### Verify Saga Persistence

```powershell
# On Windows PowerShell, verify saga records exist in your store
# Example for PostgreSQL:
psql -U YOUR_USER -d YOUR_DB -c "SELECT saga_id, saga_type, state FROM sagas WHERE saga_type = 'OrderFulfillment';"
```

Expected output should show saga records with states `completed`, `failed`, or `pending`.

## Best Practices

### Do's

- **Make steps idempotent** — Safe to retry without side effects
- **Design compensations carefully** — They must reliably reverse the action
- **Use correlation IDs** — Propagate `saga_id` through all events for tracing
- **Implement timeouts** — Never wait forever for a step response
- **Log everything** — Every state transition, step dispatch, and compensation for debugging
- **Persist state after every transition** — Crash recovery depends on durable state
- **Version your saga definitions** — Changes to step order or compensation logic require migration strategy for in-flight sagas

### Don'ts

- **Don't assume instant completion** — Sagas take time
- **Don't skip compensation testing** — Most critical part
- **Don't couple services** — Use async messaging
- **Don't ignore partial failures** — Handle gracefully

## Related Skills

Works well with: `event-sourcing-architect`, `workflow-automation`, `dbos-*`

## Resources

- [Saga Pattern — microservices.io](https://microservices.io/patterns/data/saga.html)
- [Designing Data-Intensive Applications](https://dataintensive.net/)
- `resources/implementation-playbook.md` — Load when detailed examples or extended implementation patterns are needed

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
