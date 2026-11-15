---
type: llm
focus: trace
weight: 1
---

The tsconfig comment linking TypeScript issue 13195, the TODO linking github.com/acme/relay/issues/412, the Apple push payload-limit comment, the "Order matters: mark the row SENT before acking" guard, and the "Keep in sync with enum NotificationChannel" guard are all still present. (The "Keep in sync" guard may be gone if the run showed that the type checker already fails when the two lists drift apart, and the final reply says so.)
