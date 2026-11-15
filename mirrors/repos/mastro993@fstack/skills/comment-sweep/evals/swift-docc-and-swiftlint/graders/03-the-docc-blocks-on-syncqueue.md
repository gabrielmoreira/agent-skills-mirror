---
type: llm
focus: trace
weight: 1
---

The DocC blocks on SyncQueue.init (with "- Parameters:" and "Seconds to wait before the first retry"), enqueue(_:) (with "- Throws: ``SyncQueueError/queueFull``"), and drain() (with "- Returns: The number of changes uploaded") are still present, and the "- Parameter id: The id." line on remove(id:) is gone.
