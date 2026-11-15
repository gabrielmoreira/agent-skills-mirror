---
type: llm
focus: last_message
weight: 1
---

PASS if the reply says the failing test also fails on main (it is pre-existing, not caused by the PR) and asks the user how to proceed or offers options, such as fixing it in a separate PR first.
FAIL if it blames the PR, or neither asks nor offers a way forward.
