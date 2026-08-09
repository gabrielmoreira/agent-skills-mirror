# Security Policy

Thank you for helping keep Tutti safe.

## Supported Versions

Tutti is in early development. Security fixes are made on the active `main`
branch and included in the next available release.

## Reporting a Vulnerability

Do not open a public issue for security vulnerabilities.

Email `tutti@nexight.io` with:

- A clear description of the issue and impact.
- Steps to reproduce, proof-of-concept code, logs, or screenshots when available.
- The affected version, commit, operating system, and relevant configuration.
- Whether the issue affects Tutti Local, Tutti · VM, or both.

We aim to acknowledge reports within 3 business days. After triage, we will keep
you informed about severity, expected fix timing, and disclosure coordination
when applicable.

## Scope

In scope:

- Vulnerabilities in the desktop app, local daemon, CLI, or published packages in
  this repository.
- Issues that expose local files, credentials, agent session data, workspace
  state, or app outputs without user intent.
- Privilege escalation, command execution, sandbox escape, or unsafe update paths.

Out of scope:

- Social engineering, physical attacks, or issues requiring compromised user
  devices.
- Vulnerabilities in third-party model providers, plugins, apps, or services that
  are not maintained by this repository.
- Denial-of-service reports without a practical security impact.
- Automated scanner output without a working exploit path.

## Safe Harbor

We will not pursue legal action for good-faith security research that:

- Avoids privacy violations, data destruction, and service disruption.
- Uses only the access needed to demonstrate the issue.
- Reports the issue privately and gives us a reasonable time to fix it.
