# SwiftlyS2 Background Worker Template

Related official docs sections:
- `Thread Safety`
- `Scheduler` (only for responsibility routing against workers; it does not mean a worker is the same thing as a scheduler)

Suitable for: background persistence, batch processing, async computation, and producer / consumer decoupling.

## Usage principles

- Workers should only handle computation / serialization / persistence that is safe to run asynchronously.
- Main-thread-sensitive APIs must not be accessed directly on worker threads.
- Workers must have explicit Start / Stop / Flush / Cancel semantics.
- Before writing back on the main thread, revalidate player / entity / generation state.
- For lightweight periodic tasks, prefer the built-in SwiftlyS2 Scheduler first.

## Example skeleton

```csharp
using System.Collections.Concurrent;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;

namespace MyNamespace;

public sealed class MyBackgroundWorker(ILogger<MyBackgroundWorker> logger)
{
    private readonly ILogger<MyBackgroundWorker> _logger = logger;
    private readonly ConcurrentQueue<MyWorkItem> _queue = new();
    private readonly AutoResetEvent _signal = new(false);
    private CancellationTokenSource? _cts;
    private Task? _workerTask;

    public void Start()
    {
        if (_workerTask is not null)
        {
            return;
        }

        _cts = new CancellationTokenSource();
        _workerTask = Task.Run(() => RunLoop(_cts.Token));
    }

    public void Enqueue(MyWorkItem item)
    {
        _queue.Enqueue(item);
        _signal.Set();
    }

    public async Task StopAsync(bool flushRemaining)
    {
        if (_cts is null || _workerTask is null)
        {
            return;
        }

        _cts.Cancel();
        _signal.Set();

        try
        {
            await _workerTask.ConfigureAwait(false);
        }
        finally
        {
            _workerTask = null;
            _cts.Dispose();
            _cts = null;
        }

        if (flushRemaining)
        {
            FlushRemainingQueue();
        }
    }

    private void RunLoop(CancellationToken cancellationToken)
    {
        while (!cancellationToken.IsCancellationRequested)
        {
            if (!_queue.TryDequeue(out var item))
            {
                _signal.WaitOne(4);
                continue;
            }

            try
            {
                Process(item, cancellationToken);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to process background work item");
            }
        }
    }

    private void Process(MyWorkItem item, CancellationToken cancellationToken)
    {
        // Only do async-safe work here, such as JSON, batch processing, disk IO, or network IO.
    }

    private void FlushRemainingQueue()
    {
        while (_queue.TryDequeue(out var item))
        {
            try
            {
                Process(item, CancellationToken.None);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to flush remaining work items");
            }
        }
    }
}

public sealed record MyWorkItem(ulong SteamId, string Payload);
```

## Checklist

- Is there a Start / Stop / Flush / Cancel lifecycle closure?
- Does it avoid accessing main-thread-sensitive APIs from background threads?
- Does it avoid infinite fire-and-forget patterns?
- Does it revalidate current session / generation before write-back?
- If the task is only a lightweight main-thread periodic task, would Scheduler actually be a better fit?
