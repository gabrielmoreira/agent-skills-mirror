---
title: Project commands and tooling
applicability:
- Before a project command runs
- When a claim depends on a project tool or resolved version
x-claim-provenance:
- claim: Cargo can compile and execute a package's build script before building the package.
  source: https://doc.rust-lang.org/cargo/reference/build-scripts.html
  scope: Cargo build-script reference.
- claim: Gradle evaluates settings and project build scripts before executing selected tasks.
  source: https://docs.gradle.org/current/userguide/build_lifecycle.html
  scope: Gradle 9.8.0 build lifecycle documentation.
- claim: ESLint configuration can be an executable JavaScript or TypeScript module loaded for a lint run.
  source: https://eslint.org/docs/latest/use/configure/configuration-files
  scope: ESLint flat-configuration documentation.
---

Establish the adopted tool, resolved version, configuration, and invocation from repository instructions, manifests, lock state, scripts, and nearby automation. Use the project's wrapper or script when it owns environment setup or argument forwarding. Do not substitute a globally available tool or remembered syntax for the configured one.

Before running a command, state the question it can answer, the result that changes the next action, its selector and environment, and any files, dependencies, services, load, or spend it may affect. Choose the narrowest invocation that answers that question and request only useful output.

Treat project-controlled executable configuration as code. Establish whether the command can load or execute code, plugins, build scripts, hooks, configuration, or dependencies from the subject material; if it can, that material runs with this run's access. A request to work on a project establishes as trusted for execution the project as the requester supplied it, including the requester's own unmerged work, together with this work's own edits. Material that reaches the work from another party without the project having accepted it stays untrusted until the requester vouches for it, such as another author's unmerged change, branch, or patch, a repository or archive the work obtains, or a dependency, plugin, or tool the work adds or upgrades. Run the command only when everything it executes is trusted or the requester has explicitly authorized the identified execution; otherwise use non-executing inspection or leave the dependent claim unverified. Read-only intent, a familiar command category, and disposable output establish neither trust nor permission to execute the material.

Do not repeat equivalent commands or run a broad suite after every edit; a broader adopted check runs once, when the combined change or repository instructions require its coverage. Keep repository-mandated checks distinct from evidence for the requested outcome.

Record the actual command scope and result in re-readable working state, taking the tool's own count of matched, collected, or deselected items as the evidence that a selector reached the intended scope. A command that cannot run or whose selector is unsupported leaves the corresponding claim unverified; it does not authorize inventing another toolchain.
