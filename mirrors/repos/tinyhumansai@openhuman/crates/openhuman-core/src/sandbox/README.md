# Sandbox host adapter

OpenHuman owns command-execution orchestration and the existing `sandbox.*`
RPC surface. TinySecurity owns sandbox planning, admission and single-use plan
consumption. TinyBox owns native jail facts and process execution.

The host builds a plan request from trusted command, environment, runtime and
caller facts, asks TinySecurity for a plan, then passes the admitted artifact to
the selected TinyBox executor. A missing module, refused plan or failed
consumption denies execution. OpenHuman maps the module results to the existing
`None`, `Local` or `Docker` routing and status contracts; it does not duplicate
the protected-path or credential-root policy.

The host keeps the `SANDBOX_ENV_PASSTHROUGH` allowlist, configuration switches,
status RPC, and executor lifecycle. The sandbox cannot be disabled for SaaS.
Local grants for stdio MCP servers use the same TinySecurity floor and TinyBox
admission path.

See [Privacy and security](../../../../docs/gitbooks/en/features/privacy-and-security.md)
for the product boundary. Policy behavior belongs in TinySecurity and native
execution behavior belongs in TinyBox; OpenHuman tests only its mapping,
routing, callbacks and module seams.
