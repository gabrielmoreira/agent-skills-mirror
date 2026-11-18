---
name: rrv7-api-mutation-handler
description: Use this skill whenever creating, updating, deleting (data mutations), or integrating non-GET HTTP API requests (POST, PUT, PATCH, DELETE) between a React Router v7 (RRv7) Framework Mode (NO-SSR) frontend and a Laravel backend.
---

# RRv7 + Laravel Safe HTTP Mutation Pattern

Follow this strict architecture whenever wiring up backend API mutations so unhandled errors never trigger React Router v7's `ErrorBoundary` or expose sensitive stack traces to the user.

## Strict Implementation Rules

1. **Location:** Always define the handler function inside the **parent route file** of the current view/page.
2. **Naming Convention:** Name the async function `handle<TaskName>(data: any)` in camelCase accepting `data: any` (e.g., `handleCreateOrderIntent(data: any)`, `handleArchiveOrder(data: any)`).
3. **Axios Client & Error Guard:**
   - Locate and import the project's pre-configured Axios instance (`api`)—typically found under `~/lib/`, `~/utils/`, or `~/app/util/` (match the project's `tsconfig.json` path alias such as `~/` or `@/`).
   - Never use native `fetch` or raw `axios.post()` / `axios.put()` / `axios.delete()` calls.
   - Import `axios` from `"axios"` **solely** for the `axios.isAxiosError(err)` type guard.
4. **Toaster (`sonner`):**
   - Check if `sonner` / shadcn/ui `Toaster` is installed in the project and import `toast` from `"sonner"`.
   - Use `toast.promise()` for async mutations with clear, context-specific `loading`, `success`, and `error` messages.
5. **Try-Catch & Safe Response Contract:**
   - Wrap the mutation inside a `try-catch` block. **Never re-throw** errors out of the handler.
   - **Inside `try`:** Store the un-awaited Axios call in `const requestPromise = api.<method>(...)`, pass it to `toast.promise()`, and strictly return `{ success: true, data: (await requestPromise).data }`.
   - **Inside `catch`:** Use the type-safe guard `if (axios.isAxiosError(err))` to strictly return `{ success: false, code: err.response?.status, data: err.response?.data }`. For non-Axios errors, strictly return `{ success: false }`.
6. **Wiring Up in `clientAction`:**
   - In RRv7 Framework Mode (NO-SSR), wire the handler inside `export async function clientAction({ request }: Route.ClientActionArgs)`.
   - Extract `formData` via `Object.fromEntries(await request.formData())` and route actions using `switch (data.intent)`.
7. **UI Behavior & State Rendering:** Before modifying or generating the view/component UI that triggers this mutation, load and follow the **`rrv7-mutation-ui-behavior`** skill . This strictly controls functional UI behavior and state-driven rendering (e.g., wiring `useFetcher` or `useActionData`, disabling buttons during pending states, resetting forms/closing dialogs on `success: true`, and rendering Laravel `422` field errors from `data.errors`)—excluding final visual styling or layout design.

## Reference Boilerplate

```typescript
import axios from "axios";
import { toast } from "sonner";
import api from "~/lib/axios"; // Adjust to the project's configured Axios client path
import type { Route } from "./+types/<route-name>"; // Match the current route's generated types

export async function clientAction({ request }: Route.ClientActionArgs) {
  if (!["POST", "PUT", "PATCH", "DELETE"].includes(request.method)) {
    return null;
  }

  const formData = await request.formData();
  const data = Object.fromEntries(formData);

  switch (data.intent) {
    case "process-order":
      return await handleCreateOrderIntent(data);

    default:
      return { success: false };
  }
}

async function handleCreateOrderIntent(data: any) {
  try {
    const requestPromise = api.post("/api/v1/order", data);

    toast.promise(requestPromise, {
      loading: "Processing your order...", // Customize based on task context
      success: data?.name
        ? data.name + " has been successfully processed."
        : "Success!", // Customize based on task context
      error: (err) =>
        (axios.isAxiosError(err) && err.response?.data?.message) ||
        "Something went wrong. Please try again later.", // Customize based on task context
    });

    return {
      success: true,
      data: (await requestPromise).data,
    };
  } catch (err) {
    if (axios.isAxiosError(err)) {
      return {
        success: false,
        code: err.response?.status,
        data: err.response?.data,
      };
    }
    return { success: false };
  }
}
```