---
name: container-build-guard
description: Generic guardrail workflow for container image builds. Use when Codex is about to run, debug, review, or advise on docker build, docker compose build/up --build, podman/buildah builds, Dockerfile or Containerfile changes, CI image builds, or any repository where image construction may need network access, mirrors, proxies, long-running commands, controlled logs, or reliable success/failure handoff.
---

# Container Build Guard

Use this skill to keep container image builds from wasting time or flooding context. It has three modules:

1. **Build Preflight**: discover likely external sources and check network readiness before building.
2. **Build Execution**: run long builds in a foreground, log-to-file pattern so Codex regains control as soon as the build exits while only reading a useful log tail.
3. **Post-start Verification**: after `up`/run commands, inspect container state, ports, and logs before declaring success.

## Workflow

1. Identify the intended build command if the user gave one. Otherwise scan the repository for `Dockerfile*`, `Containerfile*`, `docker-compose*.yml`, `compose*.yaml`, CI files, `Makefile`, and package manifests.
2. Before running preflight, run the Docker runtime config check. It inspects and probes, without modifying files:
   - Docker registry mirrors for Docker Hub pulls.
   - Docker daemon proxy settings for registry access.
   - Docker CLI default proxy settings for new containers and build steps.

```bash
python /path/to/container-build-guard/scripts/docker_runtime_config_check.py
```

On Windows PowerShell:

```powershell
python D:\code\skills\skills\container-build-guard\scripts\docker_runtime_config_check.py
```

If this check reports missing or partial config, explain the findings and ask the user for explicit confirmation before changing or overwriting Docker Desktop, daemon, CLI, or BuildKit configuration. Do not silently edit Docker runtime config. If the user declines or wants to continue anyway, proceed with preflight but call out the expected network risk.
Do not treat proxy fields as sufficient by themselves. A proxy can be configured but unreachable, blocked, or ignored by the relevant Docker path. The runtime check must verify the Docker daemon pull path and, when CLI default proxies are present, a new-container network path before reporting them as OK.
For Docker Hub mirrors in China-facing environments, compare the configured `registry-mirrors` against the current fallback set from the Tencent Cloud article at `https://cloud.tencent.com/developer/article/2647943`: `https://docker.xuanyuan.me`, `https://docker.1ms.run`, and `https://docker.m.daocloud.io`. If mirrors are missing, retired, or merely different, ask the user before changing the Docker runtime config instead of silently accepting them.
3. Run the bundled preflight script from the repository root. Prefer `--docker-probe` when Docker is available; it checks image manifests from the Docker daemon's network path without pulling layers. If Docker Hub host probes fail but the daemon may have registry mirrors, add `--docker-pull-probe` with a small limit to verify the actual daemon pull path. If package mirrors are configured, add `--artifact-probe` to test a small generic sample of real package artifact URLs discovered from manifests/lockfiles.
   For first-time or cold builds, also add `--image-prep` to generate a pre-pull/tag plan for discovered container images before running the real build. This is especially important when `docker compose up` would otherwise lazily pull runtime images such as databases after a long build has already completed.

```bash
python /path/to/container-build-guard/scripts/preflight.py . --docker-probe --image-prep
```

On Windows PowerShell:

```powershell
python D:\code\skills\skills\container-build-guard\scripts\preflight.py . --docker-probe --docker-pull-probe --artifact-probe --image-prep
```

4. Read the report before building. Treat `BLOCKER` entries as likely build failures. Treat `WARN` entries as places where static analysis cannot prove success, especially dynamic `curl | sh`, private registries, package managers hidden in shell scripts, or a host/daemon network mismatch.
5. If the user wants JSON for CI or automation, rerun with `--json`.
6. Only proceed to `docker build`, `docker compose build`, `docker compose up --build`, `podman build`, or CI build commands after explaining any blockers and the recommended network, proxy, or mirror configuration.
7. For long builds, use the foreground logging pattern from the Build Execution section rather than fixed sleep polling.

## Build Preflight

Always consider both the host shell and the container builder environment. Host connectivity can differ from Docker Desktop, a remote Docker daemon, BuildKit, WSL, a corporate proxy, or a CI runner.

Check these categories:

- Container registries: Docker Hub, GHCR, Quay, GitLab registry, ECR/GCR/ACR, and private registries from `FROM` or compose `image:`.
- OS packages: `apt`, `apk`, `yum`, `dnf`, `microdnf`, `zypper`, plus repository URLs in Dockerfiles.
- Language packages: npm/yarn/pnpm, pip/uv/poetry, Go modules, Cargo, Maven/Gradle, RubyGems, NuGet.
- Browser and binary installers: Playwright, Puppeteer, Selenium drivers, Chromium, GitHub releases, `curl`, `wget`, and `git clone`.
- Proxy and trust basics: `HTTP_PROXY`, `HTTPS_PROXY`, `NO_PROXY`, Docker daemon reachability, DNS resolution, TCP 443/80, and TLS/HTTPS behavior.

The script performs static discovery and lightweight probes only. It does not run a real image build. With `--docker-probe`, it runs `docker manifest inspect` for discovered images; this is still lightweight, but some Docker clients do not apply registry mirrors to manifest inspection the same way as image pulls. With `--docker-pull-probe`, it pulls a small sample of discovered Docker Hub images through the daemon; use this when host probes to `registry-1.docker.io` or `auth.docker.io` fail but Docker Desktop/daemon mirrors may make builds work. Keep the limit small unless the user explicitly wants stronger coverage.

When using `--docker-probe`, make sure any report-handling code treats manifest probes and pull probes as different result types. Manifest probe results do not carry pull-specific fields such as `local_only_uncertain`; if a report crashes after probing, fix the preflight tool or rerun with `--json` to locate serialization errors before continuing to a real build.

It also checks for common static blockers that often fail late:

- CRLF shebangs in shell scripts referenced by Dockerfiles, which can produce `exec ... no such file or directory` in Linux containers.
- Python package index flags such as `-i`, `--index-url`, and `--default-index`, with warnings that mirrors can return 200 for `/simple` but 403 for wheel artifacts.
- Missing Dockerfile `COPY`/`ADD` sources inside the build context.
- Dynamic downloads (`curl`, `wget`, `git clone`, pipe-to-shell) that can hide extra network dependencies from static discovery.

When `--artifact-probe` is enabled, the script chooses a generic sample of dependency names from `requirements*.txt`, `pyproject.toml`, and `uv.lock`, then checks artifact links from configured non-default Python indexes. Do not hardcode project-specific package names into the skill; let manifests and lockfiles drive the sample.

## Preflight Decision Guidance

- If Docker Hub host probes fail but `--docker-pull-probe` succeeds, treat the host probe as a warning about network asymmetry rather than an automatic build blocker. Report that the daemon mirror/cache path was verified.
- If an unqualified compose `image:` such as `my-service` fails a pull probe, first decide whether it is meant to be a locally built tag before treating it as a registry failure.
- If package index endpoint probes pass but artifact probes fail, fix the package source before building: choose a working mirror, use the official index, configure `pip.conf`/`UV_INDEX_URL`, or pass build args if the Dockerfile supports them.
- Prefer daemon-level registry mirrors for Docker Hub image pulls instead of rewriting `FROM node:...` or `image: postgres:...` to mirror domains. Direct image rewrites can break digests, provenance, auth, or compose semantics.
- When Docker Hub pulls are unreliable, pre-pull via a mirror and tag back to the canonical image name before building, instead of changing Dockerfiles or compose image names. For example, pull `mirror/library/postgres:16-alpine` then `docker tag ... postgres:16-alpine`. The generated `--image-prep` snippets do this generically.
- For apt/apk/pip/npm mirrors, prefer the repository's existing build args or config files when available. Patch Dockerfiles only when the mirror is hardcoded and the user has asked you to fix the build.
- Keep fixes generic and explain the class of problem. Avoid adding project-specific package names, image names, or local paths to this skill.

## Build Execution

Use this pattern when the user asks Codex to actually build an image after preflight:

- Keep the build process in the foreground so Codex regains control immediately when it exits.
- Set the shell command timeout long enough for the build to finish naturally.
- Add plain progress to Docker builds when supported so logs are line-oriented and useful: `docker build --progress=plain ...` or `docker compose --progress plain build ...`.
- Write complete logs to a temp file, but return only the final 80-200 lines to Codex.
- Preserve the original exit code so success and failure are both handled correctly.

PowerShell pattern:

```powershell
$log = Join-Path $env:TEMP "container-build.log"
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
docker build --progress=plain -t my-image . *> $log
$code = $LASTEXITCODE
Get-Content $log -Encoding UTF8 -Tail 160
exit $code
```

On Windows PowerShell, always set `PYTHONUTF8=1` and `PYTHONIOENCODING=utf-8` before running Python-based build/deploy wrappers that may print non-ASCII text. GBK terminals can fail on Unicode output even when the build itself is healthy. Read captured logs with `-Encoding UTF8` so status text and errors are not mangled.

Bash pattern:

```bash
log="${TMPDIR:-/tmp}/container-build.log"
docker build --progress=plain -t my-image . >"$log" 2>&1
code=$?
tail -n 160 "$log"
exit "$code"
```

Avoid backgrounding the build and then using fixed sleeps such as `Start-Sleep -Seconds 240` unless there is a specific reason to continue other independent work while the build runs.

The preflight script can generate wrapper snippets without executing the build:

```powershell
python D:\code\skills\skills\container-build-guard\scripts\preflight.py . --build-command "docker compose build"
```

For compose commands with global options, pass the command exactly as intended:

```powershell
python D:\code\skills\skills\container-build-guard\scripts\preflight.py . --build-command "docker compose -f docker-compose.yml build --parallel"
```

## Post-start Verification

After any successful `docker compose up`, `docker run`, or equivalent Podman command:

- Inspect runtime state with `docker compose ps -a` or `docker ps -a`.
- Treat any `Exited`, restart loop, unhealthy service, or missing expected container as unfinished work.
- Read focused logs with `docker logs --tail 200 <container>` or `docker compose logs --tail 200 <service>`.
- Look first for generic startup failures: `ImportError`, `ModuleNotFoundError`, `exec ... no such file or directory`, `permission denied`, `connection refused`, database migration errors, and missing environment variables.
- Probe declared ports with HTTP when the service is HTTP, otherwise use TCP connectivity.
- Report partial success clearly: images can build while containers still fail to start.

## Reporting Guidance

Keep the final report practical:

- Lead with whether it is reasonable to build now.
- List `BLOCKER` sources first with the exact host or URL that failed.
- Mention warnings where the project probably depends on dynamic downloads or private credentials.
- Give concrete next steps: configure Docker registry mirrors, package mirrors, proxy variables, Docker daemon proxy, `NO_PROXY`, `.npmrc`, `pip.conf`, `UV_INDEX_URL`, `PLAYWRIGHT_DOWNLOAD_HOST`, `GOPROXY`, or offline `docker save/load`.
- If you actually run a build, report the exit code and summarize the final log tail.
- If you start containers, report container state, health status, exposed local URLs/ports, and any failed service logs.
- Avoid claiming a build is guaranteed to pass. Say the preflight only verifies likely network prerequisites.
