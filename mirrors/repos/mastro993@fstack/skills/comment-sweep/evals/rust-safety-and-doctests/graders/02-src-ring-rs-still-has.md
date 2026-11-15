---
type: llm
focus: trace
weight: 1
---

src/ring.rs still has all four `// SAFETY:` comments (above `unsafe impl<T: Send> Sync for Inner<T>`, the write in push, the read in pop, and the drop loop in `Drop for Inner`), each still directly above its unsafe code.
