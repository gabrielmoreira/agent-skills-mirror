---
type: skill
lifecycle: stable
inheritance: inheritable
name: sse-streaming
description: POST-based Server-Sent Events streaming for Azure Functions — HTTP streaming, chunked response parsing, reconnection
tier: standard
applyTo: '**/*sse*,**/*streaming*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# SSE Streaming


POST-based Server-Sent Events pattern for Azure Functions. Solves the gap where native EventSource (GET-only) can't send request bodies, and Azure Static Web Apps don't proxy WebSocket to the API layer.

---

## Why POST-Based SSE

| Option | SWA API Support? | POST body? | Limitation |
|--------|-----------------|------------|------------|
| WebSocket | No | N/A | SWA doesn't proxy WebSocket to Functions |
| EventSource | Yes | GET only | Can't send context in request body |
| **POST + ReadableStream** | **Yes** | **Yes** | **Recommended pattern** |

---

## Azure Functions Setup

### Enable HTTP Streaming

```json
// host.json
{
  "version": "2.0",
  "extensions": {
    "http": {
      "enableHttpStream": true
    }
  }
}
```

### Streaming Function Pattern

```typescript
import { app, HttpRequest, HttpResponseInit, InvocationContext } from '@azure/functions';

app.http('stream-response', {
  methods: ['POST'],
  authLevel: 'anonymous', // SWA handles auth via EasyAuth
  route: 'stream',
  handler: async (req: HttpRequest, context: InvocationContext): Promise<HttpResponseInit> => {
    const payload = await req.json();

    const stream = new ReadableStream({
      async start(controller) {
        try {
          // Stream from Azure OpenAI or any async source
          const aiStream = await getAIStream(payload);

          for await (const chunk of aiStream) {
            const sseData = `data: ${JSON.stringify({ text: chunk, done: false })}\n\n`;
            controller.enqueue(new TextEncoder().encode(sseData));
          }

          // Signal completion
          controller.enqueue(
            new TextEncoder().encode(`data: ${JSON.stringify({ done: true })}\n\n`)
          );
        } catch (error) {
          controller.enqueue(
            new TextEncoder().encode(`data: ${JSON.stringify({ error: 'Stream failed', done: true })}\n\n`)
          );
        } finally {
          controller.close();
        }
      },
    });

    return {
      status: 200,
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'X-Accel-Buffering': 'no', // Disable proxy buffering
      },
      body: stream,
    };
  },
});
```

---

## Client Consumption

### POST + ReadableStream Pattern

```typescript
interface SSEMessage {
  text?: string;
  done: boolean;
  error?: string;
}

async function streamResponse(
  payload: unknown,
  onChunk: (text: string) => void,
  onComplete: () => void,
  onError: (error: string) => void,
): Promise<void> {
  const response = await fetch('/api/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    onError(`HTTP ${response.status}: ${response.statusText}`);
    return;
  }

  const reader = response.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    // Parse SSE messages from buffer
    const messages = buffer.split('\n\n');
    buffer = messages.pop() || ''; // Keep incomplete message in buffer

    for (const msg of messages) {
      if (!msg.startsWith('data: ')) continue;
      const json = msg.slice(6); // Remove 'data: ' prefix

      try {
        const parsed: SSEMessage = JSON.parse(json);
        if (parsed.error) { onError(parsed.error); return; }
        if (parsed.text) { onChunk(parsed.text); }
        if (parsed.done) { onComplete(); return; }
      } catch {
        // Ignore malformed messages
      }
    }
  }

  onComplete();
}
```

### React Hook

```typescript
function useStreamedResponse() {
  const [text, setText] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const stream = useCallback(async (payload: unknown) => {
    setText('');
    setIsStreaming(true);
    setError(null);

    await streamResponse(
      payload,
      (chunk) => setText(prev => prev + chunk),
      () => setIsStreaming(false),
      (err) => { setError(err); setIsStreaming(false); },
    );
  }, []);

  return { text, isStreaming, error, stream };
}
```

---

## Cancellation with AbortController

```typescript
async function streamWithAbort(
  payload: unknown,
  signal: AbortSignal,
  onChunk: (text: string) => void,
): Promise<void> {
  const response = await fetch('/api/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
    signal,
  });

  const reader = response.body!.getReader();
  signal.addEventListener('abort', () => reader.cancel());

  // ... same parsing logic
}

// Usage
const controller = new AbortController();
streamWithAbort(payload, controller.signal, onChunk);
controller.abort(); // To cancel
```

---

## SWA Timeout Handling

Azure Static Web Apps has a **45-second API timeout**. For long operations, use multi-phase streaming:

```typescript
// Instead of one long stream, report progress in phases
app.http('long-operation', {
  methods: ['POST'],
  handler: async (req, context) => {
    const stream = new ReadableStream({
      async start(controller) {
        const send = (data: object) =>
          controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify(data)}\n\n`));

        send({ phase: 'step-1', progress: 0.1 });
        const result1 = await doStep1();

        send({ phase: 'step-2', progress: 0.5 });
        const result2 = await doStep2(result1);

        send({ phase: 'complete', progress: 1.0, result: result2 });
        controller.close();
      },
    });

    return { body: stream, headers: { 'Content-Type': 'text/event-stream' } };
  },
});
```

---

## Error Recovery

### Retry Strategy

```typescript
async function streamWithRetry(
  payload: unknown,
  onChunk: (text: string) => void,
  maxRetries: number = 2,
): Promise<void> {
  let lastError: string | undefined;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      await streamResponse(payload, onChunk, () => {}, (err) => { throw new Error(err); });
      return;
    } catch (error) {
      lastError = error instanceof Error ? error.message : 'Unknown error';
      if (attempt < maxRetries) {
        await new Promise(resolve => setTimeout(resolve, 1000 * (attempt + 1)));
      }
    }
  }

  throw new Error(`Stream failed after ${maxRetries + 1} attempts: ${lastError}`);
}
```

---

## Activation Patterns

| Trigger | Response |
|---------|----------|
| "SSE", "streaming", "server-sent events" | Full skill activation |
| "Azure Functions stream", "HTTP streaming" | Azure Functions Setup section |
| "ReadableStream", "chunked response" | Client Consumption section |
| "abort", "cancel stream" | Cancellation section |
| "SWA timeout", "45 second" | SWA Timeout Handling section |
