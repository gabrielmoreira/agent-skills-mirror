---
name: rrv7-zod-form
description: Use this skill whenever building or wiring forms in React Router v7 (RRv7) Framework Mode (NO-SSR) using Zod, React Hook Form with real-time validation, `useFetcher`, `useEffect` response handling, and shadcn/ui `Field`, `Input`, `Button`, and `Spinner` components.
---

# RRv7 + React Hook Form + Zod Form Pattern

Follow this architecture whenever creating or wiring up validated forms that submit mutations to a parent route's `clientAction` (paired with `rrv7-api-mutation-handler`).

## Strict Implementation Rules

1. **Schema & Real-Time Validation (`zod` + `react-hook-form`):**
   - Define a strict `z.object(...)` schema and infer its TypeScript type via `z.infer<typeof formSchema>`.
   - Initialize `useForm` with `resolver: zodResolver(formSchema)` and **`mode: "onChange"`** so field validation runs in real time as the user types.
2. **Submission via `useFetcher`:**
   - Use RRv7's `useFetcher<typeof clientAction>()` (or typed fetcher) to submit form values directly to the parent route's `clientAction` without a full-page navigation.
   - Always include the matching `intent` key in `fetcher.submit({ ...values, intent: "<intent-name>" }, { method: "POST" })` so `clientAction` routes the request properly.
3. **Response & Status Code Handling (`useEffect`):**
   - Watch `fetcher.state` and `fetcher.data` inside a `useEffect` hook (guarding with `if (fetcher.state !== "idle" || !fetcher.data) return;`).
   - **On `success === true`:** Reset the form via `form.reset()` and trigger any post-success UI callbacks (such as closing a modal/dialog). Rely on RRv7's automatic `clientLoader` revalidation to refresh displayed page data.
   - **On `success === false`:** Preserve user inputs and inspect `code`:
     - If `code === 422` and `data?.errors` exists (Laravel validation errors), loop through `Object.entries(data.errors)` and attach each message to its corresponding field using `form.setError(field, { type: "server", message })`.
     - For other error codes (e.g., `403`, `500`), optionally set a root form error via `form.setError("root", { message })` alongside the toast handled by `clientAction`.
4. **shadcn/ui Components & Pending State:**
   - Use `@/components/ui/field` (`Field`, `FieldLabel`, `FieldDescription`, `FieldError`), `@/components/ui/input` (`Input`), `@/components/ui/button` (`Button`), and `@/components/ui/spinner` (`Spinner`)—adjusting `@/` or `~/` to match `tsconfig.json`.
   - Derive `const isSubmitting = fetcher.state !== "idle";`.
   - Strictly disable the submit `<Button disabled={isSubmitting}>` (and form inputs if appropriate) while submitting, and render `<Spinner />` inside the button during pending states.

## Reference Boilerplate

```tsx
import { useEffect } from "react";
import { useFetcher } from "react-router";
import { Controller, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

import {
  Field,
  FieldDescription,
  FieldError,
  FieldLabel,
} from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";

// 1. Define Zod Schema
const createOrderSchema = z.object({
  name: z.string().min(2, "Order name must be at least 2 characters."),
  quantity: z.coerce.number().min(1, "Quantity must be at least 1."),
});

type CreateOrderValues = z.infer<typeof createOrderSchema>;

interface CreateOrderFormProps {
  onSuccess?: () => void; // e.g., close modal/dialog
}

export function CreateOrderForm({ onSuccess }: CreateOrderFormProps) {
  const fetcher = useFetcher();
  const isSubmitting = fetcher.state !== "idle";

  // 2. Initialize React Hook Form with real-time validation
  const form = useForm<CreateOrderValues>({
    resolver: zodResolver(createOrderSchema),
    mode: "onChange",
    defaultValues: {
      name: "",
      quantity: 1,
    },
  });

  // 3. Submit to parent route's clientAction with intent
  function onSubmit(values: CreateOrderValues) {
    fetcher.submit(
      { ...values, intent: "process-order" },
      { method: "POST" }
    );
  }

  // 4. Detect success or map Laravel error codes via useEffect
  useEffect(() => {
    if (fetcher.state !== "idle" || !fetcher.data) return;

    const result = fetcher.data as {
      success: boolean;
      code?: number;
      data?: { message?: string; errors?: Record<string, string[]> };
    };

    if (result.success) {
      form.reset();
      onSuccess?.();
      return;
    }

    // Handle Laravel 422 field validation errors
    if (result.code === 422 && result.data?.errors) {
      Object.entries(result.data.errors).forEach(([field, messages]) => {
        const message = Array.isArray(messages) ? messages[0] : String(messages);
        form.setError(field as keyof CreateOrderValues, {
          type: "server",
          message,
        });
      });
      return;
    }

    // Handle non-422 errors (e.g., 403, 500) if needed in UI
    if (result.data?.message) {
      form.setError("root", {
        type: "server",
        message: result.data.message,
      });
    }
  }, [fetcher.state, fetcher.data, form, onSuccess]);

  return (
    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
      <Controller control="{form.control}" field, fieldState name="name" render="{({"> (
          <Field data-invalid="{fieldState.invalid}">
            <FieldLabel htmlFor="order-name">Order Name</FieldLabel>
            <Input aria-invalid="{fieldState.invalid}" disabled="{isSubmitting}" id="order-name" placeholder="Enter order name" {...field}/>
            <FieldDescription>
              Provide a descriptive name for this order.
            </FieldDescription>
            {fieldState.invalid && <FieldError errors="{[fieldState.error]}"/>}
          </Field>
        )}
      />

      <Controller control="{form.control}" field, fieldState name="quantity" render="{({"> (
          <Field data-invalid="{fieldState.invalid}">
            <FieldLabel htmlFor="order-quantity">Quantity</FieldLabel>
            <Input aria-invalid="{fieldState.invalid}" disabled="{isSubmitting}" id="order-quantity" type="number" {...field}/>
            {fieldState.invalid && <FieldError errors="{[fieldState.error]}"/>}
          </Field>
        )}
      />

      {form.formState.errors.root && (
        <p className="text-sm font-medium text-destructive">
          {form.formState.errors.root.message}
        </p>
      )}

      <Button disabled="{isSubmitting}" type="submit">
        {isSubmitting && <Spinner/>}
        {isSubmitting ? "Submitting..." : "Submit Order"}
      </Button>
    </form>
  );
}
```