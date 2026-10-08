---
title: Effective compiler
applicability:
- When the work depends on the Degardis compiler and this run has not established, from that compiler's own help and manual, its exact invocation and that it accepts each source format the work reads or writes
- When the work depends on changing which compiler is effective
x-claim-provenance:
- claim: "The Degardis compiler is distributed as the degardis package on the Python Package Index, whose project page is the authority on obtaining it, and its command is degardis."
  source: "https://pypi.org/project/degardis/"
  scope: "degardis package"
- claim: "Pip installs the latest version satisfying its constraints, prefers stable releases by default, and retains an already satisfied installation unless --upgrade is specified."
  source: "https://pip.pypa.io/en/stable/cli/pip_install/"
  scope: "pip install requirement selection and upgrade behavior; verified 2026-10-06"
---

An authoring run needs one **effective compiler**: the exact compiler invocation whose own help and manual govern this work. Prefer a compiler the requester supplied or explicitly designated; otherwise use an already available installed compiler. Never silently substitute another copy or release because it is easier to invoke.

The invocation, its manual, and explicit acceptance of the declared source format are prerequisites to compiler-dependent source work. A request to report only literal files, fields, or text may proceed from the supplied bytes without treating them as valid Degardis semantics; keep every compiler-dependent conclusion unestablished.

## Establishing the compiler

The compiler is distributed as the `degardis` package on the Python Package Index, whose project page is the authority on obtaining it, and its command is `degardis`; an already installed compiler is found by that command. Establish how to invoke those exact bytes before issuing Degardis commands. For a supplied repository, archive, environment, or executable, inspect only its own packaging metadata, entry points, README, or equivalent local instructions needed to identify a non-destructive invocation. Once an invocation is established, start at its root help from `--help`, establish the source formats that exact compiler accepts, and discover subcommand help and manual topics from it. The compiler's installed files, a source checkout they point to, and that checkout's history stay outside the work however reachable, unless the requester names them. Command names remembered from another installation, neighboring source, and another version's documentation establish nothing: a version remembered from elsewhere reads exactly like a version confirmed.

## Intended compiler

A supplied or designated compiler that cannot be invoked as found is not a reason to install a public release, and version ordering is not compatibility.

If several candidates are available and none was supplied or designated, do not silently choose by version number; use the one the host designates for the workspace, or leave the choice open when no such designation exists.

## Acquiring or changing a compiler

Accessing a package source, installing prerequisites, installing Degardis, upgrading it, or replacing the effective compiler are separate actions. Take one only when that exact reach/effect is authorized and the active task permits it. Authorization for one action authorizes none of the others.

For public-package installation, use the latest stable release unless the requester or standing instructions specify a version or source. Before changing the environment, check its runtime and tooling against the package's current installation instructions; if no compatible method is available, report the blocker rather than install an older release.

With pip, invoke it through the target environment's own interpreter, as `<interpreter> -m pip install degardis`, adding `--upgrade` when upgrading: a bare `pip` or `python` command can resolve to a different environment.

## Format compatibility

- **Effective compiler accepts the source format:** continue in that format. A newer compiler elsewhere does not itself authorize or require migration.
- **Designated compiler rejects the source format:** report the exact incompatibility. Switching compiler and migrating source are different repairs with different authority; take neither merely to make validation pass.
- **A different compiler is authorized and established to accept the source:** select it explicitly as the new effective compiler, then re-establish help, manual, and format acceptance before source work.
- **Migration is authorized and an authoritative contract establishes how to preserve the older source's meaning:** migration belongs to revision and must preserve behavior separately from compiler acceptance.

If the compiler supplies no manual for the source format, obtain an authoritative format reference within the authorized read boundary or leave the format contract unresolved.

After any authorized prerequisite action, verify its result; for installation, record the version and invocation and compare the installed version with the intended release. A failed or unchanged prerequisite is reported once with the next evidence or authority needed; do not repeat an equivalent attempt.
