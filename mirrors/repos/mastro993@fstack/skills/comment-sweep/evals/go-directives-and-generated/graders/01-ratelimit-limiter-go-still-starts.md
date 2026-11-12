---
type: llm
focus: trace
weight: 1
---

ratelimit/limiter.go still starts with "//go:build !js" and still contains "//go:generate stringer -type=State".
