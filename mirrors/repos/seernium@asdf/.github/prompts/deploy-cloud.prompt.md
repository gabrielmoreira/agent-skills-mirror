---
description: Set up cloud deployment and CI/CD for a specified provider
agent: cloud-deployment-engineer
---

Set up cloud deployment to ${input:provider:Vercel, AWS, GCP, or another platform}. Use the `deployment-scaffolder` skill's cloud-deployment templates, wire CI to run typecheck/lint/test/build before any deploy step, route secrets through the provider's native secret manager, and confirm a rollback path exists.
