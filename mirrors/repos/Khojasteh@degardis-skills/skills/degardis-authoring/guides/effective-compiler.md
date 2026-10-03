---
title: Effective compiler
applicability:
- When the work depends on the Degardis compiler and this run has not established, from that compiler's own help and manual, its exact invocation and that it accepts each source format the work reads or writes
- When the work depends on changing which compiler is effective
x-claim-provenance:
- claim: "The Degardis compiler is distributed as the degardis package on the Python Package Index, whose project page is the authority on obtaining it, and its command is degardis."
  source: "https://pypi.org/project/degardis/"
  scope: "degardis package"
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

When acquisition from the public package is the authorized fallback, use only the current package's own authoritative installation information to establish runtime requirements, supported installation methods, and prerequisite tooling. Establish that the target environment satisfies the selected method before changing it. If no authoritative compatible method is reachable, stop before source work and report what is missing rather than guessing an install command.

## Format compatibility

- **Effective compiler accepts the source format:** continue in that format. A newer compiler elsewhere does not itself authorize or require migration.
- **Designated compiler rejects the source format:** report the exact incompatibility. Switching compiler and migrating source are different repairs with different authority; take neither merely to make validation pass.
- **A different compiler is authorized and established to accept the source:** select it explicitly as the new effective compiler, then re-establish help, manual, and format acceptance before source work.
- **Migration is authorized and an authoritative contract establishes how to preserve the older source's meaning:** migration belongs to revision and must preserve behavior separately from compiler acceptance.

Compiler releases before 2.0.0 shipped no manual, so an older compiler cannot supply the contract for its own format. For source format 1 that contract is the reference published with release 1.0.1 of the compiler, https://github.com/Khojasteh/degardis/blob/v1.0.1/docs/reference.md, which describes format 1 as entries, workflows, and profiles. Reaching it is a read outside the supplied material and needs the authority such a read requires; while it is unreachable or unauthorized, a format-1 source has no authoritative contract in hand and its incompatibility is reported as it stands.

After any authorized prerequisite action, inspect the resulting exact state and establish the capability it was meant to supply. A failed or unchanged prerequisite is reported once with the next evidence or authority needed; do not repeat an equivalent attempt.
