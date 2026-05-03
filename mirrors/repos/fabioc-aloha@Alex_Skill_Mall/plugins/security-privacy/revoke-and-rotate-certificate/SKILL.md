---
type: skill
lifecycle: stable
inheritance: inheritable
name: revoke-and-rotate-certificate
description: Skill helps user to revoke and rotate certificate in case of exposed secrets
tier: standard
applyTo: '**/*revoke*,**/*and*,**/*rotate*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

Use `EnD security docs` MCP to find best practices for certificate revocation and rotation. If user is in corp tenant, you can run az cli to rotate certificate. If user is in torus, you can use `torus-docs-mcp` MCP to find the powershell command or script to rotate certificate in torus subscription and guide user through the process of rotating certificate.