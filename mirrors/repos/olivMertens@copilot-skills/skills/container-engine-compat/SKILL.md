---
name: container-engine-compat
description: >
  Adapt local container workflows bidirectionally between Docker and Podman.
  Detect engine availability, preserve build context, and verify differences in
  BuildKit/Buildah features, caches, Compose providers, rootless permissions,
  networking, and API sockets. Optimize image size and build time using live
  official Docker AND Podman documentation via MCP/fetch. Project-agnostic:
  discover paths, images, registries, labels, and platforms from the repository.
  Include Azure ACR/azd remote builds and IaC quality/what-if checks only when relevant.
  USE WHEN: "podman", "docker", "local build", "compose", "rootless",
  "container volume/permission", "image too large", "build cache",
  "switch docker podman", "container perf", "container engine".
---

# Docker and Podman Compatibility and Performance

## Goal
Preserve the intended behavior when switching **Docker to Podman or Podman to Docker**.
Use a shared command only where semantics match; otherwise provide explicit variants
and explain limitations. Do not promise universal parity or assume a Docker daemon.
Read repository instructions and discover paths, image names, labels, resource IDs,
platforms, and approved workflows. Never reuse another project's identifiers.

## Scope (NON-negotiable)
- **Local dev/test** → target dual-engine (Docker OR Podman). This is where we act.
- **Cloud/remote build**: identify where the builder actually runs. ACR Tasks needs
  no local engine; `docker buildx --push` alone does not select a remote builder.
  Preserve an approved remote release path without adding a duplicate local build.
- **CI** → hosted runners typically use Docker + `docker/*-action@*`. Do NOT rewrite the
  CI, the remote build command, or the Dockerfiles to Podman unless explicitly asked.

## Rule 0 - Detect the execution environment
For local work, check CLI presence (`Get-Command` in PowerShell or `command -v` in
POSIX shells), then the selected engine's `version` and `info` commands. An installed
CLI does not prove that its daemon, VM, or remote connection is reachable.
Honor the user's explicit preference. If both engines work and none is specified,
use the repository's convention; ask when switching would affect existing state.
Report connection failures rather than silently changing engines.

Record OS, client/server versions, rootless mode, target architecture, selected
Docker context/Buildx driver or Podman connection, and Compose provider as applicable.
On Windows/macOS, inspect the configured Podman machine and its state before proposing
startup; do not create a replacement machine or change resources without approval.

For shared syntax in PowerShell invoke the selected executable as `& $engine ...`;
in a POSIX shell use `"$engine" ...`. Use argument arrays and check native exit codes.
An alias does not translate engine-specific options.

For Docker-API consumers such as Testcontainers, verify Podman's compatibility with
the particular client and use the platform's documented local socket or named pipe.
Discover the endpoint; a Unix socket inside a VM is not automatically accessible to
a Windows client. Set `DOCKER_HOST` only when needed, scoped to the process/session,
and restore it afterwards. Do not expose an unauthenticated TCP API or mount the
engine socket into arbitrary containers. Native Podman commands do not need this shim.

## Equivalence table (dual-engine)
| Intent | Docker | Podman | Portability note |
|---|---|---|---|
| Build | `docker build` / `docker buildx build` | `podman build` | Common flags overlap; BuildKit and Buildah are different builders |
| Run | `docker run` | `podman run` | Verify networking, mounts, user mapping, and health behavior |
| Compose | `docker compose up` | `podman compose up` | Podman delegates to an external Compose provider |
| Images/PS | `docker images` / `ps` | `podman images` / `ps` | same |
| Registry login | `docker login` | `podman login` | Verify registry auth; use secure input, not secrets in command arguments |
| Multi-arch build | `docker buildx build --platform` | `podman build --platform --manifest` | Check execution support and manifest publication separately |
| Cache mount | `RUN --mount=type=cache` | Supported by recent Buildah versions | Check exact mount options; caches are not shared across engines |

Writing rule: when the syntax is identical, **write the detected engine** but note the
other "(or `docker`/`podman`)"; never hardcode a Docker socket path.

## Translation correctness — build & context (avoid broken builds)
When switching an engine or rewriting a command, these are the parity traps that silently
break a build or change the context. Check each one before emitting.

### Dockerfile / BuildKit features
- **Different implementations**: Docker BuildKit can select a frontend with
  `# syntax=docker/dockerfile:1`; without it, BuildKit uses its bundled frontend.
  Podman uses **Buildah**, not that Docker frontend. Keeping the directive is useful
  for Docker but does not enable features in Buildah. Verify each feature against
  the installed versions, including remote-client restrictions.
- **`RUN --mount=type=cache`**: supported on both, but the cache is engine-local and NOT
  shared between Docker and Podman. Never assume a warm cache after switching engines.
- **Secrets and SSH**: both support secret/SSH build mounts in supported versions;
  verify source types and options. Never replace these with `ARG`/`ENV` or copy
  credentials into the context, layers, logs, or cache.
- **Heredocs and COPY extensions**: verify support for heredocs, `COPY --link`,
  named contexts, and other extensions individually. If unsupported, retain the
  approved builder or propose a tested equivalent; never silently remove semantics.

### Build context & ignore files
- **Ignore file precedence**: Podman uses `.containerignore` instead of `.dockerignore`
  when both exist; they are not merged. Podman also has `--ignorefile`. Docker supports
  `.dockerignore` and Dockerfile-specific ignore files, which take precedence over
  the context-root file. Prefer one shared `.dockerignore` where possible; explicitly
  reconcile exclusions if engine-specific files are needed. Do not rely on Git ignore
  rules for a local container build.
- **Preserve the context explicitly**: keep the working directory, Dockerfile path,
  final context argument, named contexts, target, build arguments, and platform.
  `-f` does not make Docker's context the Dockerfile directory; Podman can default to
  that directory when the context is omitted. Always supply the intended context.
- **Verify included files**: inspect packaging/build logs or a disposable context probe
  for required files and excluded non-sensitive sentinels. Do not copy actual secrets
  into a probe. Upload packers may use different rules from the builder; measure both
  uploaded bytes and effective build context. Keep regenerated dependencies and
  outputs out without excluding lockfiles or required source files.
- **Absolute vs relative COPY**: `COPY ./x /y` is relative to the context root on both.
  Do not translate to host-absolute paths.

### Registry names & tags (a top breakage when switching)
- **Qualify external images** with their registry and namespace to avoid Podman's
  short-name resolution differences. Do not rewrite Dockerfile stage aliases as
  registry references. Discover actual names; use placeholders in generic examples.
- **Pin reproducible inputs** by digest where appropriate. Explicit version tags are
  readable but still mutable; a tag is not an immutable pin. Preserve existing pins.

### Cache export/import & multi-arch (buildx vs buildah differ)
- **Cache flags are not interchangeable**: Buildx supports backends such as registry,
  local, gha, and inline, subject to driver/version restrictions. Inline is an export
  format; import it through the image registry. Podman/Buildah documents repository
  arguments such as `--layers --cache-to registry.example.com/team/build-cache
  --cache-from registry.example.com/team/build-cache`, not Buildx's
  `type=registry,ref=...` syntax. Do not assume cache-format interoperability or a
  warm cache after migration. Explain any replacement of a gha/local/inline backend.
- **Local image availability**: the default Buildx `docker` driver loads automatically.
  Other drivers generally need `--load` for local testing unless configured otherwise;
  `--push` publishes to a registry and does not imply local loading. Podman normally
  stores build output in its selected engine's store, which may be in a VM or remote.
  Preserve the requested output and confirm the image is available to the runtime.
- **Multi-arch**: Buildx can build and push a multi-platform index. Podman supports
  multiple `--platform` values with `--manifest`, followed by manifest publication
  including all platform images (verify `podman manifest push --all` for the version).
  Both need native builders, emulation, or cross-compilation for foreign-architecture
  execution. Verify the published platform list; do not equate multi-arch with `--load`.

### Runtime translation traps
- **Host networking**: Podman's `--network host` uses the engine host's network
  namespace, including in rootless operation. On a VM-backed engine that host is not
  necessarily the desktop OS. Docker Desktop support also depends on configuration.
  Prefer explicit port publication where suitable; test host access and DNS.
- **Bind mounts**: resolve paths in the correct client/engine filesystem and check
  UID/GID mapping. SELinux `:Z`/`:z` relabeling can apply to both engines; it changes
  host labels and is not a harmless no-op. Use it only when required and approved.
- **GPU access**: verify engine version, vendor runtime/CDI setup, host OS, and VM
  passthrough. Podman supports CDI device names and some versions support `--gpus`;
  do not assume a universal flag translation or add privileged mode as a shortcut.

## Podman rootless pitfalls (the real friction)
1. **SELinux**: when enforced, distinguish private `:Z` from shared `:z` labels.
  Never recursively relabel system directories or disable isolation just to pass a test.
2. **UID/GID**: default rootless mapping maps the caller to container root.
  `--userns=keep-id` can help with bind mounts, but may change the process user and
  conflict with the image's expectations. Test the actual runtime user and writes;
  avoid recursive ownership changes to host data as a default fix.
3. **Ports**: low-port restrictions depend on the engine host's
  `net.ipv4.ip_unprivileged_port_start`. Prefer a high host port instead of changing
  host security settings. Bind local-only services to loopback where appropriate.
4. **Compose**: `podman compose` wraps an external provider such as `docker-compose`
  or `podman-compose`; it is not a separate native Compose implementation. Discover
  the selected provider and version; test dependencies, health conditions, volumes,
  and build behavior. Protect resolved configuration because it may contain secrets.
5. **Healthchecks**: verify that the chosen image format preserves health metadata,
  then inspect actual scheduling and health transitions. Podman supports automatic
  intervals, subject to host/version support; `podman auto-update` is not the scheduler.

## Ground on official docs LIVE via MCP (MANDATORY for perf)
Before recommending or applying a performance/build optimization, **verify the official
Docker AND Podman docs live** — never from memory (BuildKit flags,
`--mount=type=cache`, `--cache-to/from`, buildah/`podman build` evolve fast).
Fetch BOTH engines to stay dual-compatible, compare, then apply.

Tool order:
1. `mcp_microsoft_lea_microsoft_docs_search` / `microsoft_docs_fetch` → for any Azure/ACR
   side (e.g. `az acr build`, ACR Tasks, ACR cache), when relevant.
2. `vscode-websearchforcopilot_webSearch` **or** `fetch_webpage` → for Docker and Podman
   (docs outside Microsoft Learn). Always query the canonical URLs below.
3. Only conclude on a perf flag after reading the matching official page;
   if Docker and Podman diverge, surface both and pick the portable one.

Canonical URLs to consult (fetch with a targeted `query`):
- Docker — build best practices: `https://docs.docker.com/build/building/best-practices/`
- Docker — BuildKit cache mounts: `https://docs.docker.com/build/cache/optimize/`
- Docker — cache backends (`--cache-to/from`): `https://docs.docker.com/build/cache/backends/`
- Docker — multi-stage: `https://docs.docker.com/build/building/multi-stage/`
- Docker — `.dockerignore`: `https://docs.docker.com/build/concepts/context/#dockerignore-files`
- Podman — `podman build`: `https://docs.podman.io/en/latest/markdown/podman-build.1.html`
- Podman — rootless: `https://docs.podman.io/en/latest/markdown/podman.1.html` + `https://github.com/containers/podman/blob/main/docs/tutorials/rootless_tutorial.md`
- Podman runtime: `https://docs.podman.io/en/latest/markdown/podman-run.1.html`
- Podman Compose: `https://docs.podman.io/en/latest/markdown/podman-compose.1.html`
- Docker frontend: `https://docs.docker.com/reference/dockerfile/`
- Docker drivers: `https://docs.docker.com/build/builders/drivers/`
- Azure remote builds: `https://learn.microsoft.com/azure/developer/azure-developer-cli/remote-builds`
- ACR CLI: `https://learn.microsoft.com/cli/azure/acr#az-acr-build`
- Azure (when targeting Azure, via `microsoft_docs_*`): search "az acr build", "ACR Tasks cache",
  "azd package", "azd provision preview", "az deployment group what-if", "bicep build lint".

Rule: cite consulted URLs and match the guidance to installed versions. Tool-generated
commands are suggestions, not evidence; check official references and CLI help.
If either engine's relevant documentation is unavailable, disclose that specific gap
and mark the affected recommendation `[to verify]`; do not claim dual-engine validation.

## Image / container perf (engine-agnostic)
These rules apply to any local build AND to a remote/registry build. Do not change a
project's Dockerfiles without an explicit request. **Confirm each flag via the live docs
above before applying it**:
- **Layer order**: stable deps BEFORE application code (COPY the dependency manifest/
  lockfile then install, COPY the source afterward) to maximize the cache.
- **Build cache mount**: `RUN --mount=type=cache,target=<pkg-cache-dir> <install cmd>`
  only with verified builder/version support. This is independent of reproducibility:
  keep lockfiles and hashes where supported whether or not caching is enabled.
- **Strict multi-stage**: disposable builder stage; copy into the runtime only the
  artifacts actually needed (built venv/binaries), never the toolchain.
- **Minimal supported base**: select for runtime compatibility, not size alone; pin
  by digest for immutability and keep a deliberate security-update policy.
- **Lean ignore file**: exclude `.venv`, `node_modules`, build outputs, `.git`, temp dirs
  in `.dockerignore` (and `.containerignore` if you target Podman only).
- **Reduce RUN layers**: chain package-manager steps and clean caches in a single RUN
  (e.g. `apt-get update && … && rm -rf /var/lib/apt/lists/*`).
- **Reproducibility**: pinned versions, no unbounded upgrades.
- **Measure before claiming gains**: compare context/upload bytes, cold and warm build
  times, cache hits, final image size, and startup under the same platform/resources.
  Tune stage concurrency and VM CPU/RAM only against measured bottlenecks. Avoid broad
  cache pruning or deleting user images/volumes; clean only artifacts created for testing.

For a migration, run a focused build and runtime smoke test on each available target
engine, checking context inclusion, image metadata, startup, health, and relevant mounts
or ports. Record any engine unavailable locally and the remaining CI validation needed.

## Azure remote build & IaC verification (ONLY when the project targets Azure)
Applies only when Azure is requested or confirmed by the project configuration;
Terraform alone does not imply Azure. Skip otherwise. Verify flags using live Microsoft
Learn docs and installed CLI help. Use available Azure best-practice/CLI tools, but
cross-check generated commands. Follow repository release gates and approved scripts.

### Faster/cleaner remote image build
- **Server-side build (no local engine)**: `az acr build` runs on ACR Tasks. Prefer an
  existing approved remote release workflow when available; do not replace CI implicitly.
  Verify subscription, resource group, registry, RBAC, network access, and target platform
  before submission. Builds/pushes incur cost and change registry state: require authorization.
- **Measure context upload**: the ACR Tasks packer may include files a local
  `.dockerignore` would drop. Verify which ignore rules the packer honors for your setup and
  keep large regenerable folders out of the uploaded context (VCS-ignore them if needed).
- **Cache capabilities**: do not pass Buildx `--cache-from/--cache-to` flags to
  `az acr build`; the current quick-build CLI does not expose them. A BuildKit builder
  using ACR as a registry cache is a separate workflow. Inspect the actual ACR task
  definition/backend before recommending cache changes. Artifact pull-through cache
  is not the same as build-layer cache.
- **azd path**: inspect `azure.yaml`, hooks, host support, and the installed azd version.
  A supported `docker.remoteBuild: true` configuration uses ACR; otherwise packaging
  can require a local engine. Check fallback behavior in logs rather than assuming all
  azd builds are remote. Separate package/build, provisioning, and deployment; review
  hooks before even a preview. Do not add a second build or change these settings implicitly.
- **Verify the artifact**: after an authorized build, check terminal task status, image
  digest and architecture, vulnerability policy, and the intended destination. A queued
  task is not a successful build; do not deploy as part of a documentation or build-only task.

### Infra verification & code quality (run BEFORE apply)
- **Preview the delta — never blind-apply**:
  - Bicep/ARM: use `az deployment group what-if` or the matching subscription/other
    scope, with the actual template, parameters, subscription, and location as required.
  - azd: use `azd provision --preview` only when supported by the installed version and
    IaC provider. Otherwise use that provider's native preview; never substitute apply.
  - Terraform: initialize using the project's provider lockfile, run `terraform plan`
    with `-out` to a protected, ignored temporary path, and review with `terraform show`.
    Treat plans/JSON as sensitive. Apply that saved plan only after separate authorization.
- **Static quality gates**:
  - Bicep: compile and lint the actual template with the installed Bicep CLI and
    `bicepconfig.json`; include parameter validation and the project's PSRule checks.
  - Terraform: `terraform fmt -check`, `terraform validate`, and `tflint`; optionally
    `checkov`/`tfsec` for security posture.
- **Guardrails on the plan**: reject a saved plan if it deletes or replaces resources you did
  not intend to change; diff the what-if output and call out every destroy/replace explicitly
  before proceeding. Do not run `apply` when the preview shows unexpected changes.
- **Review beyond syntax**: check identity/RBAC, secret handling, public access, private
  DNS/network paths, policy, capacity, and costs. Preview can contain unknown values and
  does not prove runtime readiness. Report unavailable checks and verify deployed state
  only after an authorized deployment.
- Preserve CI, Dockerfiles, and the configured remote build path unless their change
  was explicitly requested. A passing quality gate is not deployment authorization.

## Exit checklist
Mark conditional items not applicable with a reason; do not invent tests or infrastructure.

- [ ] Current project paths, image names, labels, IDs, and approved workflows were discovered.
- [ ] For local work: engine reachability, preference, versions, OS, connection, and platform are known.
- [ ] Shared commands preserve semantics; engine-specific variants and unsupported features are explicit.
- [ ] If an API client is used: endpoint compatibility is checked, exposure is restricted, and overrides are scoped.
- [ ] External images are qualified and pins preserved; stage aliases are unchanged.
- [ ] BuildKit versus Buildah capabilities are verified; a Docker syntax directive is not treated as a Buildah upgrade.
- [ ] Context, Dockerfile, target, arguments, platform, named contexts, and ignore precedence are preserved and checked.
- [ ] If caching/multi-arch is used: backend syntax, output/loading, execution support, and published platforms are verified.
- [ ] If runtime is affected: mounts, user mapping, SELinux, ports, host/VM networking, and health behavior are tested as relevant.
- [ ] If Compose/GPU is used: provider or device/runtime support is verified for the selected versions.
- [ ] Every performance recommendation is grounded in live official Docker AND Podman docs with cited URLs; unavailable evidence is marked `[to verify]`.
- [ ] Gains are measured, not assumed; focused build/smoke tests cover available target engines and remaining gaps are disclosed.
- [ ] If Azure applies: actual builder/azd configuration, context upload, auth/network prerequisites, task outcome, and artifact are checked as relevant.
- [ ] If Azure IaC changes: compile/lint/validate and supported what-if or saved-plan review pass; unexpected deletes/replacements block apply.
- [ ] No unrequested Dockerfile/CI/remote-path changes, unauthorized build/push/deployment, leaked secrets, or broad cleanup; test artifacts are cleaned.
