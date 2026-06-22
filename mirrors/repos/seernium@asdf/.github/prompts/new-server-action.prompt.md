---
mode: agent
description: Generate a secure Next.js Server Action with auth check, CSRF safety, and Zod validation.
---

Invoke the `backend-api` agent to create a new Server Action.

Structure MUST follow this order:
1. Auth session check (Server Actions are public HTTP endpoints — auth is not optional)
2. Zod schema validation of the input
3. Business logic (only after auth and validation pass)
4. `revalidatePath` or `redirect` on success

Return a typed `ActionResult<T> = { success: true; data: T } | { success: false; error: string }` union.

The Server Action to create: ${input}
