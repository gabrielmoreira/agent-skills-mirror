# Self-Hosted Control Plane Pairing

Use this path when a user wants a local runner to claim work from a self-hosted
Control Plane or another explicitly trusted relay.

## Pairing Path

For a new configuration, use setup so platform, executor, project target, and
relay choices are collected together:

```bash
opentag setup --relay https://<trusted-control-plane>
```

For an existing local configuration:

```bash
opentag pair --relay <url>
```

The CLI reads Hosted Control V1 capabilities directly without calling `/healthz`.
Registration sends only the runner ID and an empty capabilities list; it does not bind Project Targets.
Successful registration stores the issued runner credential atomically and
removes the bootstrap pairing token from local config. Do not use `--no-register`
with Hosted Control V1; registration and recovery reject that option.

## Trust And Secrets

- Pair only with an HTTPS origin the user operates or explicitly trusts. The
  relay is a remote control plane for this local runner.
- The relay can access run metadata, command text, and progress, and it controls which queued runs the local runner claims.
- Have the user enter the bootstrap pairing token through the local setup or
  config workflow. Never ask for it in chat, command output, screenshots, or
  committed files.
- Do not reuse bootstrap, recovery, fencing, login-throttle, or provider
  secrets. Follow `docs/control-plane-deployment.md` for deployment authority
  and rotation boundaries.
- Treat the Control Plane console as a bounded operational surface for runners,
  targets, hosted runs, permissions, and audit—not as a general chat cockpit.

## Verify

```bash
opentag config show
opentag status
opentag doctor
```

Confirm the redacted config reports relay mode and a paired Hosted Control V1
runner registration, the expected Project Targets remain in local config, and
no Control Plane alert is failing. If pairing reports recovery-required state,
stop and use the deployment's separately held recovery process; never invent or
reuse a credential.
