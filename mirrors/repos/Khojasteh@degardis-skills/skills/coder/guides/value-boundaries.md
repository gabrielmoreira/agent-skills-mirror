---
title: Value ownership across boundaries
applicability:
- When a value crosses a boundary where its representation can change
- When values from more than one source can collide
---

Name the conceptual owner of the value, the concept each receiver consumes, and every representation it takes at a boundary. When a caller already holds an established cohesive aggregate and the callee consumes several of its members for one boundary responsibility, pass the aggregate. Pass narrower values when the aggregate would expose an unrelated responsibility or create an unwanted dependency; name that concrete reason rather than preserving or expanding a decomposed signature by inertia. Do not pass a broad context object merely to avoid choosing a contract.

Enumerate the actual boundaries the value crosses, such as source-language code, configuration, serialization, templates, commands, protocols, storage, and another runtime. For each transition, establish type, spelling, casing, escaping, parsing, validation, normalization, defaults, null, missing and unknown values, precision or encoding, mutability, and error behavior. Do not infer one boundary's representation from another or let two representations drift merely because each is locally well typed.

When several sources can supply the value, define precedence and collision behavior explicitly, including whether equal, empty, invalid, repeated, or unknown values differ. Preserve source identity when later policy depends on where the value came from.

Carry the source-domain value or cohesive aggregate to the boundary that owns the destination contract; derive destination representations and perform keyed merges there. Trace the value to the final consumer and verify each distinct representation there, not only at the first parser, intermediate object, or assignment. Where independently controlled sources can use the same key, exercise a collision at that final consumer rather than relying on incidental insertion order. A completed boundary change accounts for every reader, writer, schema, example, and compatibility path that depends on the old ownership, representation, or precedence rule.
