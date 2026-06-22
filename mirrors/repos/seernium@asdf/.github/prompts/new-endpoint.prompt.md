---
description: Scaffold a new API route or Server Action with validation and error handling
agent: backend-api
---

Create a new ${input:endpointType:API route or Server Action} for ${input:purpose}. Use the `node-api-builder` skill: define the `zod` schema first, then the handler, with auth check → validation → business logic → structured error response, in that order. Include a test covering the happy path and one failure case.
