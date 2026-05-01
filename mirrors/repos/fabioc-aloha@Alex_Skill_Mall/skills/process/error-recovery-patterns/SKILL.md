---
type: skill
lifecycle: stable
inheritance: inheritable
name: error-recovery-patterns
description: What to do when things break.
tier: standard
applyTo: '**/*error*,**/*recovery*,**/*patterns*'
currency: 2026-04-20
lastReviewed: 2026-04-30
---

# Error Recovery Patterns Skill


> What to do when things break.

## Recovery Hierarchy

Prevent → Detect → Contain → Recover → Learn

## Retry Rules

| Retry | Don't Retry |
| ----- | ----------- |
| Network timeouts | Validation errors (400) |
| Rate limits (429) | Auth failures (401, 403) |
| Server errors (5xx) | Not found (404) |
| Connection refused | Business logic errors |

## Retry with Backoff

```typescript
const delay = baseDelay * Math.pow(2, attempt - 1);
const jitter = Math.random() * 0.3 * delay;
await sleep(delay + jitter);
```

## Circuit Breaker States

CLOSED → (failures > threshold) → OPEN → (timeout) → HALF-OPEN → (success) → CLOSED

## Fallback Patterns

| Pattern | Use Case |
| ------- | -------- |
| Default value | Config loading |
| Cached value | Data fetch failure |
| Degraded service | Non-critical features |

```typescript
const result = await primary().catch(() => fallback());
```

## Rollback Patterns

| Pattern | Use Case |
| ------- | -------- |
| DB transaction | Atomic operations |
| Saga (compensate) | Distributed transactions |
| Feature flag | Instant rollback |

### Saga Pattern Implementation

```typescript
// Compensating transactions for distributed operations
interface SagaStep<T> {
  execute: () => Promise<T>;
  compensate: () => Promise<void>;
}

async function executeSaga<T>(steps: SagaStep<T>[]): Promise<T[]> {
  const completed: SagaStep<T>[] = [];
  const results: T[] = [];
  
  try {
    for (const step of steps) {
      results.push(await step.execute());
      completed.push(step);
    }
    return results;
  } catch (error) {
    // Compensate in reverse order
    for (const step of completed.reverse()) {
      try {
        await step.compensate();
      } catch (compensateError) {
        console.error('Compensation failed:', compensateError);
        // Log but continue compensating other steps
      }
    }
    throw error;
  }
}

// Usage: Order processing saga
const orderSaga: SagaStep<void>[] = [
  {
    execute: () => reserveInventory(orderId),
    compensate: () => releaseInventory(orderId)
  },
  {
    execute: () => chargePayment(orderId),
    compensate: () => refundPayment(orderId)
  },
  {
    execute: () => scheduleShipment(orderId),
    compensate: () => cancelShipment(orderId)
  }
];
```

## Error Boundaries

Contain failures to prevent cascade. Catch at component boundaries, log, show fallback UI.

```typescript
// React error boundary pattern
class ErrorBoundary extends React.Component<Props, State> {
  state = { hasError: false, error: null };
  
  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }
  
  componentDidCatch(error: Error, info: React.ErrorInfo) {
    // Log to monitoring service
    logErrorToService(error, info.componentStack);
  }
  
  render() {
    if (this.state.hasError) {
      return <FallbackUI error={this.state.error} onRetry={() => this.setState({ hasError: false })} />;
    }
    return this.props.children;
  }
}
```

## Timeout and Cancellation

```typescript
// AbortController for cancellable operations
async function fetchWithTimeout<T>(
  url: string, 
  options: RequestInit = {}, 
  timeoutMs: number = 30000
): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
  
  try {
    const response = await fetch(url, { 
      ...options, 
      signal: controller.signal 
    });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return response.json();
  } finally {
    clearTimeout(timeoutId);
  }
}
```

## Strategy Pivot (For AI Assistants)

When your approach fails repeatedly, don't keep retrying — pivot.

| Failure Pattern | Pivot Strategy |
| --------------- | -------------- |
| Same edit fails twice | Re-read file, verify context is current |
| Same command fails twice | Try alternative tool or manual approach |
| Same build error | Check if your prior changes caused it |
| User says "upstream problem" | Back up, analyze earlier changes |
| Pattern doesn't work | Ask user what they know |

**Rule of Three**: Two failures of the same approach = third attempt MUST be fundamentally different.

**Surface the problem**: "I've tried X twice and it's failing. I think the issue is [analysis]. Here's an alternative approach..."

## Error Classification

| Error Type | Retry? | Strategy |
| ---------- | ------ | -------- |
| Transient (network, timeout) | Yes | Exponential backoff with jitter |
| Rate limit (429) | Yes | Respect Retry-After header |
| Client error (4xx) | No | Fix request, don't retry blindly |
| Server error (5xx) | Sometimes | Retry with backoff, then escalate |
| Validation error | No | Fix input data |
| Auth error (401, 403) | No | Re-authenticate or check permissions |

## Graceful Degradation

```typescript
// Feature flags for instant rollback
interface FeatureFlags {
  useNewCheckout: boolean;
  enableAISearch: boolean;
  showBetaFeatures: boolean;
}

async function getFeatureFlags(userId: string): Promise<FeatureFlags> {
  try {
    return await flagService.getFlags(userId);
  } catch {
    // On failure, return safe defaults (old behavior)
    return {
      useNewCheckout: false,
      enableAISearch: false,
      showBetaFeatures: false
    };
  }
}
```
