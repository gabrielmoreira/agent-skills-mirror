# Install the published OpenMotion application (optional)

Repository installation defaults to the [source guide](../install.md). Use this route only when the user explicitly selects the published npm application. It includes a prebuilt Studio, MCP and production Skills and uses the package's configured online template catalog; it does not clone or build the source repository.

## Choose a published channel

- **Stable / prod templates:** read the [published stable installation guide](https://releases.open-design.ai/open-motion/install.md).
- **Test / DEV templates:** use the [published test installation guide](https://releases.open-design.ai/open-motion/dev/install.md) only when explicitly requested. Use separate host configuration/profile, application home, data and Skills paths. DEV still requires its service network and authorization.

Follow the selected published guide and its recorded package/version, platform and host options. Do not guess a package version, execute unresolved `{{...}}` placeholders or apply newer source-only flags to an older package. Use the immutable version guide and exact package version for reproducible installation and troubleshooting. If the guide cannot be read, report the failure; do not silently switch to source or another channel.

The published guide selects the current host's `openmotion setup --host` command. Codex, Claude Code, DeepSeek Harness and WorkBuddy have registration adapters; any other local Agent passes its own name, installs the same application and Skills, and registers the returned MCP entry itself ([other local Agents](npm-installation.md#other-local-agents)). Configure only that host and preserve existing projects, credentials and unrelated settings. [Platform recipes and recovery](npm-installation.md)

For **Codex only**, the repository bootstrap also accepts an explicit pinned package:

```sh
bash install.sh --package EXACT_PACKAGE_SPEC
```

Replace `EXACT_PACKAGE_SPEC` with the exact `@openmotion/app@VERSION` from the selected release record. A reviewed HTTPS candidate or absolute local `.tgz` additionally requires `OPENMOTION_INSTALLER_SHA256` from its matching manifest. Setup options follow the package specification. With no arguments, `install.sh` still installs from source. Other hosts use the published guide's direct npm command.

<a id="installation-success-reply"></a>

## Installation and onboarding

Follow the installed version's instructions and the [shared onboarding contract](install-onboarding.md#installation-success-reply). Source, npm and plugin setup share the maintained contract; published packages retain the behavior embedded in their own version. Verify actual MCP access to the selected workspace and open its template library without creating a project. Registration, a prepared URL or generated cards alone do not establish visible onboarding.

Installation does not authorize project creation, export or paid model calls. Repository changes do not update existing published packages or hosted guides; a new package requires a separately authorized [manual release](release-workflows.md).
