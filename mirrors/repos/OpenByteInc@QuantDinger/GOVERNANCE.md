# QuantDinger Governance

QuantDinger is an Open Byte Inc. open-source project. This document explains
how project decisions are made and how trusted access is assigned.

## Decision model

The project uses a maintainer-led model:

- Contributors propose changes through issues, discussions, and pull requests.
- Maintainers decide whether a change fits the roadmap, architecture, security
  requirements, and maintenance capacity.
- Material changes to public APIs, execution behavior, authentication,
  authorization, broker integrations, database schemas, or release processes
  require an issue or RFC before implementation.
- Security-sensitive decisions may be discussed privately until coordinated
  disclosure is safe.

Maintainers seek consensus. If consensus is not reached, the Project Lead makes
the final decision and records the rationale in the relevant issue, pull
request, or architecture decision document.

## Roles

### Project Lead

- Sets product and technical direction.
- Appoints and removes maintainers.
- Approves releases and security advisories.
- Holds final responsibility for repository and package access.

### Maintainer

- Reviews and merges pull requests.
- Triages issues and vulnerability reports.
- Maintains CI, dependencies, documentation, and releases.
- Applies least privilege when granting repository or infrastructure access.

### Contributor

- Proposes changes under the Developer Certificate of Origin.
- Follows the contribution, testing, security, and coding requirements.
- Does not receive privileged access solely by submitting a contribution.

Current role assignments and holders of sensitive access are listed in
[MAINTAINERS.md](MAINTAINERS.md).

## Changes to governance

Governance changes are proposed by pull request. The Project Lead approves the
final change after public review, except where publishing details would expose
a current security incident.

