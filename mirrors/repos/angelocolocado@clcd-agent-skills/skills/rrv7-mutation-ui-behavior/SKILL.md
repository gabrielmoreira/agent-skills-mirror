---
name: rrv7-mutation-ui-behavior
description: Use this skill whenever wiring React Router v7 (RRv7) UI components, forms, modals, or action buttons to `clientAction` mutations—strictly governing pending/disabled button states, shadcn/ui `<Spinner />` usage, and response-driven UI updates (excluding visual design or styling).
---

# RRv7 Mutation UI Behavior & State Rendering

Follow these strict rules whenever connecting a view or component to an RRv7 `clientAction` mutation. This skill governs **functional UI behavior only**—do not redesign layouts, colors, or unrelated styling.

## Strict Implementation Rules

1. **Mutation Wiring (`useFetcher` / `Form`):**
   - Connect forms or trigger buttons using RRv7's `useFetcher()` (preferred for modals, inline actions, and multi-action pages) or `<Form>` with `useNavigation()`.
   - Always include the matching `intent` field so `clientAction` routes the request to the correct handler.

2. **Disable Buttons During Pending State:**
   - Track the in-flight state (`fetcher.state !== "idle"` or `navigation.state === "submitting"`).
   - Strictly set `disabled={isSubmitting}` on the primary submit button (and any secondary/cancel buttons that could conflict with the request) to prevent duplicate submissions.

3. **Loading Indicator (`<Spinner />` from shadcn/ui):**
   - Locate and import the project's shadcn/ui `<Spinner />` component (typically in `~/components/ui/spinner` or `@/components/ui/spinner`).
   - Conditionally render `<Spinner />` inside the active submit button while the mutation is pending (alongside descriptive loading text or replacing the button's static icon).

4. **Response Detection & Conditional UI Updates:**
   - Inspect the returned action payload (`fetcher.data` or `useActionData()`) and explicitly handle the `{ success, code, data }` contract from `rrv7-api-mutation-handler`:
   - **On `success === true`:** Trigger the appropriate post-success UI state—such as resetting form fields, closing open dialogs/drawers/sheets, clearing temporary selection states, or displaying the updated state.
   - **On `success === false`:** Keep the form or dialog open and preserve the user's current inputs. If `code === 422` and `data?.errors` is present, display field-level validation error messages beneath the corresponding form inputs.

5. **Scope Boundary (Behavior Only, No Design Changes):**
   - Only add or modify state hooks, `disabled` attributes, `<Spinner />` rendering, and conditional UI logic.
   - Preserve the component's existing layout, Tailwind classes, and visual design unless explicitly instructed otherwise.