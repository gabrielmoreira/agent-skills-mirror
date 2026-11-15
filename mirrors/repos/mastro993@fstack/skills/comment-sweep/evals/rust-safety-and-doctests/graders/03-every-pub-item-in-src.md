---
type: llm
focus: trace
weight: 1
---

Every pub item in src/ring.rs, src/sink.rs, and the Recorder code in src/metrics.rs still has a `///` doc comment (Producer::capacity included, though its "# Arguments" / "# Returns" boilerplate may be trimmed), and every ```rust doctest example the branch added is still present: the `//!` one in src/ring.rs and those on ring::channel, Producer::push, Consumer::pop, Recorder, and Sink::flush.
