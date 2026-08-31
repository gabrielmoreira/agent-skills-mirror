# LLM App Build Rails

Load this reference when preparing the build handoff. The always-loaded skill body states the rules; this is the per-rail decision, what it costs to defer, and the failure mode that shows up when the rail is missing.

Everything here is a prepared handoff contract. OMH makes no provider call, runs no eval, and observes no token count. A rail decision recorded here is a design, not evidence that any code exists.

The rails, in the order a late decision gets expensive: `provider boundary`, `structured output`, `prompt artifacts`, `retrieval grounding`, `evaluation`.

## 1. Provider Boundary

One module owns the provider client. It holds the model ID, the credential lookup, the timeout, the retry policy, and the rate-limit backoff, and every feature calls through it.

- **Model ID is exact.** `claude-opus-4-1-20250805`, not `claude-opus-latest`. A floating alias silently re-points under a benchmark, and the run that "regressed" was measuring a different model. Keep the ID in one named constant or config value, and record it beside any result meant to be compared with another result.
- **Credentials come from the environment or a secret store.** Never a literal in source, a prompt file, a test fixture, or an example. A key committed once is a key rotated forever.
- **Failures are classified, not swallowed.** Timeout, rate limit, transient 5xx, invalid request, and content refusal are five different outcomes, and only the first three are safe to retry. A single broad `except` around the call turns a schema bug into an infinite retry loop and a quota exhaustion into a silent empty answer.
- **Retries are bounded and idempotent.** Cap the attempts, back off exponentially with jitter, honor the provider's retry-after header when it sends one, and never retry a request the caller cannot afford to have executed twice.
- **Timeouts are explicit at both levels.** A per-request timeout and a total budget for the operation; a streaming call that stalls mid-response is not covered by a connect timeout alone.

Deferring this rail means every later call site invents its own model pin, timeout, and retry policy, and they diverge without anyone deciding that they should.

## 2. Structured Output

Decide the output contract before the prompt. The caller consumes a shape, so declare the shape.

- **Schema first.** A JSON schema, a typed model, or the provider's structured-output/tool-call mode. The schema is the contract; the prompt is the attempt to satisfy it.
- **Validate every response.** Parse and validate before the value reaches any caller. An unvalidated response is an unvalidated input from an external system that happens to be fluent.
- **Repair once, then fail loudly.** On a validation error, re-ask once with the specific error text included, then fail. An unbounded repair loop is a token bill with no exit condition, and a silent fallback to a default value is the false-green that makes a broken extractor look healthy for a month.
- **Never regex-scrape prose.** Pulling a field out of a paragraph with a regular expression works until the model rephrases, and then it fails without an error. If the output is worth parsing, it is worth declaring.

Deferring this rail means the parsing lives at the call sites, and every prompt edit becomes a parser edit nobody remembers to make.

## 3. Prompt Artifacts

A prompt is source code with a review history, not a string literal.

- **Files, not inline strings.** A prompt in a file shows up in a diff; a prompt inside a function body does not, and neither does the change that broke it.
- **Version identifier.** Give each prompt a version the call site records with its output, so a bad response can be traced to the prompt that produced it.
- **Separate the channels.** System rules (what the model always is), task instruction (what this call must do), and injected context (retrieved documents, user input, tool results) are three regions with three trust levels. Concatenating them into one blob is how a document becomes an instruction.
- **Injection-aware handling of untrusted content.** Retrieved documents, uploads, tool output, and web pages are data. Fence them, label them as untrusted, and state in the system region that content inside the fence never changes the task. Then assume the fence can still fail: the real defense is that the model's output is schema-validated and its tools are least-privilege, so a successful injection cannot do anything the caller did not already authorize.

Deferring this rail means nobody can answer which prompt produced last week's bad output.

## 4. Retrieval Grounding

Only build this rail if the feature retrieves. If it does, it is the rail most likely to be blamed for a generation problem it did not cause.

- **Chunking is a decision, not a default.** Chunk size, overlap, and boundary (paragraph, section, semantic) change what can be retrieved at all. Record the choice; a retrieval failure caused by a mid-sentence split cannot be prompted away.
- **Citations are grounding, not decoration.** Every claim the model makes from retrieved context carries the chunk it came from, so an unsupported claim is visible rather than plausible.
- **Evaluate retrieval before generation.** Measure whether the right chunk was in the context window at all, with a retrieval metric on a labeled set. A generation score sitting on top of unmeasured retrieval cannot separate a bad answer from a bad document set, and the team spends a week rewriting a prompt that was never the problem.

Deferring this rail means every quality complaint gets answered with a prompt edit.

## 5. Evaluation

Named here for ordering; the shape of the deliverables and the comparison record are in `references/eval-harness.md`.

The rule that belongs on this rail: the eval suite is part of the feature, not a follow-up ticket. A feature that ships without a golden set has no way to answer whether the next prompt edit helped, and the answer defaults to whoever tried it and liked the output.

## Evidence Boundary

A rail decision, a schema, a prompt layout, or an eval design is prepared work. It is not implementation, an observed eval run, review, CI, or merge evidence. Token counts, latency, and cost belong to runs; a figure no run reported stays null and is never estimated from a pricing table.
