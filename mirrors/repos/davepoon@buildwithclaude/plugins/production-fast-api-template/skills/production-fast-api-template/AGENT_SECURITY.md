# LLM and Agent Security Standards

These standards cover the security of the LLM, RAG and agent parts of the unified FastAPI + RAG +
Agentic AI backend: the threat catalog, the OWASP mappings, how tools are registered, authorized
and audited, the production control baseline, adversarial testing and the release gate.

In generated projects, this file lives at `docs/standards/AGENT_SECURITY.md`. It extends
`API_SECURITY.md` §9 (RAG) and §10 (agents), which hold the mandatory API-level controls, and it
works together with `GUARDRAILS.md` (content-safety checks), `PYDANTIC_STANDARDS.md` §8 (plan and
tool-argument validation), `API_CONVENTIONS.md` §2 (authorization dependencies),
`ASYNC_EXECUTION.md` (budgets, timeouts, workers) and `AI_EVALUATION.md` (adversarial datasets).

**Status labels:**

- 🟢 **Convention.** A proposed standard. Follow it by default.
- 🟡 **Needs approval.** An open team decision. Present the options and don't pick one silently.
- ⚪ **Illustrative.** Example code, records or policies showing a pattern. It is not an implemented module and doesn't choose a vendor, framework or limit.

**Taxonomies used together:**

- **OWASP Top 10 for LLM Applications 2025** (`LLM01`–`LLM10`): model and application risks such as prompt injection, data leakage, unsafe output handling, vector weaknesses and unbounded consumption.
- **OWASP Top 10 for Agentic Applications 2026** (`ASI01`–`ASI10`): risks that appear when agents plan, use tools, keep memory, talk to other agents and act autonomously.
- **OWASP API Security Top 10 2023** (`API1`–`API10`): used in `API_SECURITY.md` for the HTTP surface that wraps the agents.

> **The core rule.** The LLM may *propose* an action. Deterministic application code must
> authenticate, authorize, validate, approve, execute and audit it.

---

## 0. Quick rules for code generation

| # | Rule | Status |
|---|---|---|
| 1 | Treat **all model-consumed content as potentially hostile**: user prompts, retrieved chunks, web pages, emails, files, OCR text, tool results, MCP responses, memory and messages from other agents. | 🟢 |
| 2 | Content may supply **facts**, never **authority**. Nothing the model reads can grant permissions, change the task, add tools or approve an action. | 🟢 |
| 3 | Authorization is decided in code (`auth/`, `rag/security/`, `agents/security/`, `execution/`), never in a prompt. "Never reveal X" in a system prompt is not access control. | 🟢 |
| 4 | Retrieval applies the caller's access scope as a store filter **before** any content reaches the model (`API_SECURITY.md` §9). | 🟢 |
| 5 | Tools are **allowlisted** in `agents/tools/tool_registry.py` with an owner, risk rating, data classification and side-effect type. The model can't register, rename or redescribe a tool at runtime. | 🟢 |
| 6 | Effective tool permission = the **user's** permissions ∩ the **agent's** declared permissions ∩ the **tool's** policy. It's evaluated immediately before every call, even if an earlier plan was approved. | 🟢 |
| 7 | Every tool argument is validated in code: schema, ownership, tenant, limits, destinations, paths. Validation isn't authorization, and both are required. | 🟢 |
| 8 | Tool and MCP results are **untrusted input**: parsed into typed models, restricted to expected fields, labeled with provenance and checked at G5. They can't trigger follow-up calls on their own. | 🟢 |
| 9 | Irreversible, external or high-impact actions need **human approval bound to the exact arguments**. A change after approval invalidates the approval. | 🟢 (the action list 🟡) |
| 10 | Every agent run has hard budgets: steps, tool calls, tokens, cost, wall-clock time and concurrency. Exceeding a budget stops the run with a typed error. | 🟢 (values 🟡) |
| 11 | Model output is never passed to an interpreter (SQL, shell, template, HTML, URL fetch, file path, deserializer) without a dedicated control: parameterization, allowlists, escaping or a sandbox. | 🟢 |
| 12 | No secrets in prompts, context, memory, tool descriptions or logs. Agents use their own short-lived, scoped workload identity, never a user's broad token or a shared service account. | 🟢 |
| 13 | Memory writes follow a policy: provenance, timestamp, user/session isolation, expiry, and revalidation on read. Retrieved or tool content never writes durable memory directly. | 🟢 |
| 14 | Messages between agents are schema-validated, authenticated and treated as untrusted. One agent can't grant another agent privileges through natural language. | 🟢 |
| 15 | Every externally visible effect can be reconstructed from audit events (§6). | 🟢 |
| 16 | Security tests assert that **the backend prevented the effect**, not only that the model refused (§8). | 🟢 |

### Where the code goes

| Control | Location |
|---|---|
| Tool registry (allowlist, owner, risk rating, schemas, side effects, enforcement point) | `src/agents/tools/tool_registry.py` |
| Effective tool permission (user ∩ agent ∩ tool policy) | `src/agents/security/tool_permissions.py` |
| Budgets, egress, filesystem and sandbox policy per agent | `src/agents/security/execution_policy.py` |
| Which actions need approval; approval binding and expiry | `src/agents/security/approval_policy.py` |
| Enforcing all of the above just before each call | `src/execution/executor.py` (it calls the policies; it doesn't redefine them) |
| Plan, tool-call and final-response models | `src/agents/structured_output.py` (PYDANTIC_STANDARDS §8) |
| Principal and permitted tools in the execution context | `src/agents/dependencies.py` |
| RAG access scope, document validation, post-retrieval policy | `src/rag/security/` (`API_SECURITY.md` §9) |
| Content-safety checks (injection, PII, harmful content) | `src/guardrails/` at checkpoints G0–G6 (GUARDRAILS §3) |
| Memory write and read policy | `src/cognition/memory/memory_manager.py` |
| Audit event schema | `src/common/security/audit_schemas.py` |
| Deterministic security tests | `tests/security/{rag,agents}/` |
| Adversarial and benign prompt datasets | `evaluation/datasets/guardrails/` (synthetic only) |

---

## 1. Threat catalog

### 1.1 Prompt injection

| Attack | How it works | Typical impact |
|---|---|---|
| **Direct injection** | The user tells the model to ignore instructions, reveal secrets, bypass policy or change role. | System-prompt leakage, unsafe answers, policy bypass |
| **Indirect injection** | Instructions are hidden in a web page, PDF, email, ticket, repository, RAG document, image or tool result that the agent later reads. | Data exfiltration or actions taken while processing trusted-looking content |
| **Instruction smuggling** | Instructions are hidden with HTML, Markdown, comments, zero-width or bidirectional Unicode, whitespace, Base64 or other encodings. | Bypassing simplistic filters |
| **Long-context hijacking** | The attacker floods the context with distracting or conflicting text so that important instructions are diluted or pushed out. | Lost policy adherence, wrong decisions |
| **Role confusion** | Content pretends to be a system or developer message, an administrator, a tool result or another agent. | Privilege escalation, instruction-priority manipulation |
| **Thought/observation injection** | Text imitates the agent's own reasoning or observation format so that the loop treats it as its own conclusion. | Hijacked plan or tool choice |
| **Memory poisoning** | False facts or instructions are stored in long-term memory, summaries, profiles or preferences. | Persistent compromise across sessions |
| **RAG poisoning** | Malicious or misleading content is inserted into the indexed corpus. | Attacker-controlled answers or embedded instructions |
| **Tool-output injection** | A tool response contains "send this file to…" or "run this command…", and the model treats it as an instruction. | Unauthorized follow-up tool calls |

### 1.2 Tool and agent attacks

- **Tool parameter manipulation.** The attacker steers arguments: the recipient of an email, the account or tenant queried, the file path, a SQL filter, a payment amount, a URL to fetch. A tool call isn't safe because the model generated it.
- **Excessive agency.** The agent holds more tools, permissions or autonomy than its task needs, so a successful injection has a larger blast radius.
- **Tool chaining.** Harmless calls compose into a harmful one: read a malicious document → extract an instruction → search internal data → send the results out. Review the tool set as a **graph of reachable action chains**, not as isolated permissions.
- **Cross-agent injection.** One agent passes malicious or misleading content to another. Protocols such as MCP and A2A add untrusted tool metadata, server impersonation and unsafe capability discovery.
- **Approval bypass.** Arguments change after approval, an approved action is replayed, or a write path is reached through a read-only workflow.

### 1.3 Data and privacy attacks

- **Sensitive information disclosure:** system prompts, credentials, personal data, confidential documents, hidden reasoning or traces, other users' conversations, retrieval results the caller can't see.
- **Cross-tenant leakage:** manipulated identifiers, filters, conversation IDs or retrieval queries. Enforce tenant isolation in the database and service layer, never only in the prompt.
- **Membership and training-data inference** against custom or fine-tuned models trained on sensitive data.
- **Leakage through logs and traces:** prompts, chunks, tool arguments and outputs copied into logs, traces or evaluation reports.

### 1.4 Traditional injection through LLM-generated content

LLM output becomes dangerous when an interpreter consumes it:

| Sink | Risk | Required control 🟢 |
|---|---|---|
| Database | SQL injection | No model-written SQL. Tools expose narrow, parameterized queries (`get_order_status(order_id)`, not `run_sql(query)`). |
| Shell / OS | Command injection | No shell tools by default. If one is approved 🟡: fixed argv, allowlisted commands, sandbox (§5). |
| Code | Code execution | Isolated sandbox only (ASI05, §5). Never `exec`/`eval` in the app process. |
| Browser / admin UI | XSS, HTML and Markdown injection | Encode for the output context. Render Markdown with raw HTML disabled. Links are allowlisted or shown as plain text. |
| Templates | Server-side template injection | Model text is data passed into templates, never template source. |
| Outbound HTTP | SSRF | The destination policy from `API_SECURITY.md` §5.7. |
| Filesystem | Path traversal | Generated names are never paths. Map to IDs under a fixed root and resolve and verify the prefix. |
| Parsers | Unsafe deserialization | JSON only, validated by Pydantic. No `pickle`, `yaml.load`, `eval` or XML without a hardened parser. |

### 1.5 Retrieval and document risks

Untrusted documents with instructions, hidden text in HTML or OCR, poisoned or stale entries,
wrong-tenant results, citation spoofing, ranking manipulation, oversized documents crowding policy
out of the context. The controls are in `API_SECURITY.md` §9.

### 1.6 Model and output risks

- **Jailbreaks** through role-play, hypotheticals, translation, encoding, multi-turn pressure or conflicting instructions. Resistance is defense in depth, never a guarantee.
- **Fabricated authority:** invented facts, citations, permissions, tool results or completed actions. Consequential claims are verified against the source system (§4.3).
- **Harmful output:** phishing, malware, fraud, unsafe advice, abuse. Handled by guardrails (GUARDRAILS §3) plus downstream validation.
- **Denial of service and cost attacks:** huge prompts, expensive retrieval, loops, recursive agents, long conversations. Handled by budgets (§4.4) and `API_SECURITY.md` §8.

---

## 2. OWASP Top 10 for LLM Applications 2025: audit mapping

| Risk | Attack scenario | Audit questions | Required mitigations | Our components |
|---|---|---|---|---|
| **LLM01 Prompt Injection** | A user, email, web page, PDF, ticket or RAG document tells the agent to ignore policy and send confidential data. | Can untrusted content reach the model? Can retrieved text influence tools? Are direct and indirect injections tested? | Separate instructions from data; label external content untrusted; least-privilege tools; validate actions in code; approval for sensitive operations; adversarial testing. | `llm/prompts/`, G1/G2/G5, `agents/security/`, `execution/executor.py` |
| **LLM02 Sensitive Information Disclosure** | The agent returns another customer's records, prompt secrets, internal documents, tokens or confidential tool output. | Is authorization enforced before retrieval and tool execution? Are logs and traces redacted? | Tenant/resource authorization outside the model; redact secrets and PII; DLP checks; minimal context; isolated sessions and memory. | `rag/security/access_control.py`, G3/G6, `common/logging.py` |
| **LLM03 Supply Chain** | A poisoned model, prompt template, embedding model, plugin, MCP server, package or dataset enters production. | Are dependencies pinned and reviewed? Are models and tools verified? | SBOM; pinned versions and hashes; dependency scanning; reviewed tool and MCP connectors; signed artifacts; staged rollout and rollback. | `API_SECURITY.md` §13, `providers/mcp/` |
| **LLM04 Data and Model Poisoning** | Malicious RAG content or corrupted fine-tuning data biases answers or hides instructions. | Who can write to the corpus? Are documents versioned and approved? | Protected ingestion; provenance; quarantine of new sources; embedded-instruction scanning (G0); document ACLs; rollback and integrity checks. | `rag/ingestion.py`, `rag/security/document_validation.py`, G0 |
| **LLM05 Improper Output Handling** | Model-generated SQL, shell, HTML, URLs, paths or code are executed or rendered unvalidated. | Is output passed to an interpreter? Is it schema-validated? | Typed structured outputs; parameterized queries; escaping; command and URL allowlists; sandboxing; reject unexpected fields. | PYDANTIC_STANDARDS §5–§8; this file §1.4 |
| **LLM06 Excessive Agency** | The agent can delete records, send mail, move money, change permissions or call arbitrary APIs without confirmation. | Which tools exist? Read or write? Are there limits and approvals? | Least privilege; split read/write tools; per-resource scope; transaction limits; human approval for irreversible actions; loop and call caps. | `tool_registry.py`, `agents/security/*` |
| **LLM07 System Prompt Leakage** | The model reveals prompts, hidden policies, tool descriptions, credentials or security logic. | Does the prompt contain secrets? Is prompt secrecy treated as a boundary? | No secrets in prompts; authorization in code; don't rely on prompt secrecy; output filtering; safe errors. | `llm/prompts/`, G3 |
| **LLM08 Vector and Embedding Weaknesses** | Retrieval returns another tenant's content, attacker documents or manipulated rankings. | Are vector records ACL-filtered before retrieval? Can users influence ranking or metadata? | Authorization before search; tenant namespaces; validated metadata; protected embedding and ingestion; retrieval-quality and provenance monitoring. | `rag/security/`, `providers/vector_store/` |
| **LLM09 Misinformation** | The agent fabricates a policy, status, citation, transaction or completed action. | Are important claims and tool results verified? | Grounding in authoritative sources; citations; action status read back from the source system; exposed uncertainty; fallbacks. | `rag/generation/validation.py`, `AI_EVALUATION.md` |
| **LLM10 Unbounded Consumption** | Huge prompts, repeated tool calls, recursive agents, expensive retrieval or long conversations exhaust quota or money. | Are there token, time, cost, iteration and concurrency limits? | Rate limits; quotas; context and document size caps; per-tenant budgets; timeouts; circuit breakers; loop detection; cancellation; backpressure. | `API_SECURITY.md` §8, `execution_policy.py`, ASYNC_EXECUTION §10 |

---

## 3. OWASP Top 10 for Agentic Applications 2026: audit mapping

| Risk | What to audit | Production controls | Our components |
|---|---|---|---|
| **ASI01 Agent Goal Hijack** | Can user input, retrieved data, tool output or memory change the agent's objective? | Immutable task envelope; explicit trust boundaries; untrusted-content markers; goal and policy checks before each action; injection tests. | `agents/schemas.py` (`AgentTask`), `execution/executor.py` |
| **ASI02 Tool Misuse and Exploitation** | Can a legitimate tool be used unsafely (bulk delete instead of lookup)? | Tool-specific authorization; strict schemas; argument validation; resource and quantity limits; dry-run; action preview; human approval. | `tool_permissions.py`, `approval_policy.py`, tool argument models |
| **ASI03 Identity and Privilege Abuse** | Does the agent inherit a broad user token, a shared service account, cached credentials or another agent's permissions? | Dedicated workload identity; short-lived scoped tokens; per-user and per-tenant authorization; no credentials in prompts; privilege separation; rotation. | `auth/tokens.py`, ECS task roles (`API_SECURITY.md` §11) |
| **ASI04 Agentic Supply Chain** | Are third-party agents, tools, plugins, prompts, registries and protocol servers trusted without review? | Inventory and SBOM; pinned/signed components; sandboxed connectors; allowlisted tools; code review; monitoring; kill switch. | `tool_registry.py`, `providers/mcp/`, CI (`API_SECURITY.md` §13) |
| **ASI05 Unexpected Code Execution** | Can generated code, shell commands, notebooks, plugins or files run outside a secure boundary? | Prefer non-code APIs; isolated sandbox; non-root; restricted filesystem and network; CPU/memory/time limits; no host credentials; egress filtering. | `execution_policy.py`, §5 |
| **ASI06 Memory and Context Poisoning** | Can an attacker write persistent instructions or false facts into memory, summaries, profiles or shared context? | Write policy; source and timestamp metadata; user/session isolation; approval for durable memory; integrity checks; expiry and deletion; revalidation on use. | `cognition/memory/memory_manager.py` |
| **ASI07 Insecure Inter-Agent Communication** | Can agents spoof, replay, alter or forge messages or tool results? | Mutual authentication; signed messages; schema validation; nonces/sequence numbers; per-message authorization; confidentiality; bounded trust. | `agents/team_orchestrator.py`, `agents/schemas.py` |
| **ASI08 Cascading Failures** | Can one failing agent trigger repeated actions across the workflow? | Timeouts; circuit breakers; retry budgets; idempotency keys; compensation/rollback; dependency isolation; blast-radius limits; emergency stop. | `execution/error_handler.py`, ASYNC_EXECUTION §6 and §10 |
| **ASI09 Human-Agent Trust Exploitation** | Does the UI make output look authoritative or hide uncertainty and side effects? | Show sources and limits; preview exact actions; distinguish proposed from completed; meaningful approval; operator training against automation bias. | Approval payloads (§4.2), response schemas |
| **ASI10 Rogue Agents** | Could an agent drift, be compromised or act outside its role? | Behavioral monitoring; policy outside the model; periodic permission review; canary tests; quarantine; fast disable and credential revocation. | Audit events (§6), kill switch (§4.5) |

---

## 4. Tool security

Tool manipulation turns a prompt problem into a real-world incident, so every tool gets its own
review.

### 4.1 Tool registry 🟢

Every entry in `agents/tools/tool_registry.py` declares:

- An owner, business purpose, **risk rating** and data classification.
- Its **side-effect type**: `read`, `write`, `external_send`, `financial`, `destructive`, `code_execution` or `permission_change`.
- A pinned argument model and result model (versioned; a change is reviewed like an API change).
- Its guardrail **enforcement point** (in-app or gateway, GUARDRAILS §2).
- Whether it requires approval, and its per-call and per-run limits.

Also:

- Tools are **allowlisted**. The executor looks names up in the registry and never accepts a tool definition from model output.
- Tool descriptions shown to the model are static, reviewed text. They never change at runtime and never contain secrets or internal hostnames.
- External connectors and MCP servers are inventoried and approved before use (ASI04). The tools an MCP server advertises are filtered against the registry. New server-side tools don't appear automatically.
- Unused and deprecated tools are removed.

### 4.2 Tool authorization card

Document every tool with a card like this one, stored with the tool's module:

```text
⚪ Illustrative
Tool:               send_email
Actor:              customer-support-agent
Side effect:        external_send
Allowed operation:  send a reply to the authenticated customer on the current ticket
Allowed data:       the current ticket only
Forbidden:          external recipients, attachments, bulk send
Approval:           required before sending; approval binds recipient, subject and body hash
Limits:             1 recipient, 1 message per approval, no fields classified confidential
Audit event:        agent.tool.executed (required)
```

- **Don't use one broad token for all agents.** Each agent, environment and operation gets a narrowly scoped identity. On-behalf-of calls carry the **user's** delegated scope, never more (API_SECURITY §4.6).
- The effective permission is recomputed **just before execution**. A plan approved at step 1 doesn't authorize step 5, and permissions revoked mid-run take effect at the next call.

```python
# ⚪ Illustrative content for src/agents/security/tool_permissions.py
from src.agents.exceptions import ToolNotPermitted
from src.agents.schemas import AgentExecutionContext
from src.agents.tools.tool_registry import ToolSpec


def authorize_tool_call(spec: ToolSpec, ctx: AgentExecutionContext) -> None:
    """Default deny. The model's plan is never an input to this decision."""
    if spec.name not in ctx.agent_allowed_tools:
        raise ToolNotPermitted(spec.name, reason="not_in_agent_profile")
    if not spec.required_permissions <= ctx.principal_permissions:
        raise ToolNotPermitted(spec.name, reason="principal_lacks_permission")
    if spec.side_effect not in ctx.allowed_side_effects:
        raise ToolNotPermitted(spec.name, reason="side_effect_not_allowed")
```

### 4.3 Tool arguments and results

Argument checks, run in code after Pydantic validation and before G4 (PYDANTIC_STANDARDS §8):

- Type and schema, required and optional fields, allowed values.
- **Resource ownership and tenant boundaries**, using the same `valid_*` logic as the API (API_CONVENTIONS §1–§2).
- Quantity, monetary and recipient limits; destination allowlists; path restrictions; URL schemes and hosts.
- Whether the action is reversible, which decides whether approval is needed.

An agent may propose:

```json
{"tool": "refund_order", "order_id": "ORD-123", "amount": 2500, "currency": "INR"}
```

The backend independently confirms that the authenticated user owns the order, the amount is
refundable, the currency matches, the agent may refund, and the amount is within its limit.

**Results are untrusted.** A compromised API, parser, plugin or MCP server can return text that
tries to steer the next step. So:

- Parse results into the tool's result model (`extra="forbid"` for our tools, `extra="ignore"` for third-party payloads).
- Keep only the fields the next step needs, and preserve provenance (`tool`, `call_id`, source).
- Run G5 on any free text before it re-enters the context, and wrap it as data, never as instructions.
- A result can never add tools, raise limits or mark an approval as given.
- **Verify completion from the source system.** "Refund issued" means the refund API returned a success status that the executor read back, not that the model said so (LLM09, ASI09).

```json
{"status": "success", "order_id": "ORD-123", "refundable_amount": 2500, "currency": "INR"}
```

### 4.4 Budgets 🟢 (values 🟡)

`agents/security/execution_policy.py` defines, per agent profile: maximum steps, tool calls per
run and per tool, input and output tokens, cost, wall-clock time, parallel tool calls, and
identical-call repetition (loop detection). The executor checks them before each step, and a
breach raises a typed `AgentBudgetExceeded`, recorded in the audit trail. Long runs go to the
worker path (ASYNC_EXECUTION §6) with the same budgets.

### 4.5 Human approval and the kill switch

- **Actions that require approval** by default (the final list is 🟡): external communications, deleting or modifying records, financial transactions, publishing, permission changes, sharing sensitive data, running code, changing infrastructure.
- The approval request shows the **exact** tool, target, arguments, data to be shared and expected side effect, not "Continue?". Mark proposed actions and completed actions differently.
- An approval is a server-side record bound to the principal, run, tool, **argument hash** and expiry. It is single-use. The executor re-checks it and the permissions at execution time; changed arguments or an expired approval mean a new approval.
- A **kill switch** per agent and per tool (settings or feature flag 🟡) disables execution, revokes the agent's credentials and stops queued runs. Test it.

---

## 5. Runtime isolation for code and side effects (ASI05)

- Prefer narrow APIs over code execution. A code-execution tool needs approval 🟡.
- If one is approved: a separate, isolated sandbox (never the API or worker process, and never a container that holds the task role), running as non-root with a read-only root filesystem except a scratch directory, no host credentials, no metadata endpoint access, denied or allowlisted egress, and CPU, memory, time and output-size limits.
- File tools work under a fixed root per tenant and run. Resolve the path and check that it stays under the root. Symlinks outside the root are rejected.
- Network tools go through the outbound destination policy (API_SECURITY §5.7).
- Production and test credentials are separate. Agents in test environments never hold production credentials.

---

## 6. Observability and audit

Log these as structured audit events (schema: `API_SECURITY.md` §12), with redaction:

- User, tenant and agent identity; correlation and run IDs.
- Model, prompt and policy versions.
- Retrieved document IDs and the authorization decision for each (never the chunk text).
- Tool selected, argument **hash** plus non-sensitive argument fields, policy checks and outcomes.
- Approval requested, granted, denied or expired.
- Tool result status and the final externally visible effect.
- Latency, tokens, cost, retries, step count and budget breaches.

Store audit events in tamper-resistant storage 🟡. Alert on unusual destinations, repeated
denials, privilege changes, high-volume retrieval, abnormal tool sequences, budget breaches and
sudden shifts in guardrail block rates.

---

## 7. Production control baseline

Before launch, a production agent has:

**Identity and access.** SSO for users and operators; per-agent workload identity; short-lived,
scoped credentials; tenant and resource authorization in backend services; separate read and
write permissions; secrets from Secrets Manager or SSM; no credentials in prompts, context, memory,
logs or tool descriptions.

**Runtime isolation.** Sandboxed code execution; restricted egress; no unrestricted shell,
filesystem, browser or HTTP tool; separate production and test credentials; quotas and timeouts;
per-tenant rate and cost limits; a kill switch that revokes tools and credentials.

**Human control.** Approval for the actions in §4.5, showing exact targets, arguments, data and
effects.

**Observability.** The events in §6, in tamper-resistant storage, with alerts.

---

## 8. Security testing plan

Test the complete workflow, not just the chat prompt. Every test records **whether the backend
prevented the unauthorized effect**, not only whether the model resisted.

| Area | Cases | Kind |
|---|---|---|
| Prompt and content | Direct "ignore previous instructions"; indirect injection in HTML, PDF, email, ticket and repository fixtures; hidden Unicode, Markdown, comments, encodings, multilingual and image text; long-context distraction; role and observation spoofing | Effectiveness in `evaluation/datasets/guardrails/`; enforcement paths deterministic in `tests/security/agents/` with a scripted fake LLM |
| RAG | Wrong-tenant retrieval, unauthorized document IDs in citations, poisoned chunk with instructions, deleted document still retrievable | Deterministic, `tests/security/rag/` with an in-memory fake store |
| Memory | Poisoning, cross-session and cross-user contamination, expired memory reused | Deterministic, `tests/cognition/` + `tests/security/agents/` |
| Tools and authorization | Arguments changed after approval; another tenant's resource ID; raised amount, quantity or recipients; write tool through a read-only workflow; chaining harmless tools into a sensitive action; replayed approval; skipped approval; expired or over-privileged credentials; recursive or parallel calls | Deterministic, `tests/security/agents/` |
| Tool results | Malicious instructions in tool output; malformed and oversized payloads; hallucinated success | Deterministic with fake tools |
| Resilience | Oversized prompts and documents; tool timeouts; external API compromise; loops and retry storms; refusals; partial failure; kill switch; rollback | Deterministic where possible, integration environment otherwise |

The deterministic tests use a **scripted fake LLM** that emits the malicious plan or tool call
directly. This tests our enforcement code independently of whether a real model would comply.
Model-in-the-loop red-teaming runs only in an approved environment, on synthetic data, and never
against external systems without authorization.

---

## 9. Minimum release gate

Don't release an agent to production unless all of these are true:

- [ ] No high-risk tool is reachable without backend authorization.
- [ ] Tenant isolation is tested and enforced outside the prompt.
- [ ] All model outputs consumed by code are schema-validated.
- [ ] Shell, code, SQL, HTML, URL and file operations have dedicated controls.
- [ ] Sensitive actions have approval, or an approved compensating control.
- [ ] Loops, spending, tokens and tool calls are bounded.
- [ ] Memory writes are controlled and auditable.
- [ ] Credentials are scoped, short-lived and absent from model context.
- [ ] Audit logs can reconstruct every external side effect.
- [ ] Incident response can disable the agent, revoke credentials, quarantine memory and roll back data.
- [ ] Red-team testing covers LLM01–LLM10 and ASI01–ASI10.

---

## 10. Threat checklist for a new agent or tool

Answer these in the pull request that introduces the agent or tool:

1. What untrusted content can reach the model?
2. Can that content influence a tool call?
3. Which tools can read sensitive data?
4. Which tools cause irreversible side effects?
5. Is authorization enforced in backend code?
6. Can a user reach another tenant's data?
7. Can the model generate SQL, shell commands, URLs, HTML or code?
8. Are those outputs sandboxed or parameterized?
9. Can retrieved content write to memory or change instructions?
10. Are tool results parsed and validated?
11. Are high-risk actions confirmed by a user?
12. Are tokens, cost, time, tool calls and loops limited?
13. Can the audit log reconstruct what happened?
14. What is the fallback when the model is uncertain or a control fails?
15. Were indirect injections tested in documents, emails, web pages, images and tool responses?

---

## 11. Decisions still requiring team approval 🟡

1. The list of actions that require human approval, and the approval UI and storage.
2. Budget values per agent profile (steps, tokens, cost, time, parallelism).
3. Whether any code-execution, shell or browser tool is allowed, and the sandbox technology.
4. The inter-agent message authentication mechanism (signed envelopes, mTLS, gateway identity).
5. The workload identity model for agents and the on-behalf-of token exchange.
6. The approved MCP servers and third-party connectors, and their review process.
7. Tamper-resistant audit storage and retention.
8. The kill-switch mechanism (settings reload, feature flag service, gateway policy).
9. Durable-memory policy: what may be stored, approval, expiry, deletion.
10. The environment and scope for model-in-the-loop red-teaming.
