---
name: ng22-forms
description: Recommends typed Angular 22 forms, explicit validation, and predictable submission flows.
---

# Angular 22 Forms & Validation

Use typed reactive forms for complex user input. Keep validation rules explicit and place submission side effects behind a single form service or component method.

## Core Rules

1. Use typed `FormControl` and `FormGroup` structures for non-trivial forms.
2. Keep synchronous validators pure and reusable.
3. Surface validation messages based on control state, not ad hoc template logic.
4. Disable submission while the form is invalid or while a request is in flight.
5. Use custom controls only when a native input cannot express the interaction.
6. Keep server errors separate from field-level validation.

## Example

```typescript
import { Component } from '@angular/core';
import { ReactiveFormsModule, FormControl, FormGroup, Validators } from '@angular/forms';

type ContactFormValue = {
  email: FormControl<string>;
  message: FormControl<string>;
};

@Component({
  standalone: true,
  imports: [ReactiveFormsModule],
  selector: 'app-contact-form',
  template: `
    <form [formGroup]="form" (ngSubmit)="submit()">
      <label>
        Email
        <input formControlName="email" type="email" />
      </label>

      @if (form.controls.email.invalid && form.controls.email.touched) {
        <p>Please enter a valid email address.</p>
      }

      <label>
        Message
        <textarea formControlName="message"></textarea>
      </label>

      <button type="submit" [disabled]="form.invalid || submitting">Send</button>
    </form>
  `,
})
export class ContactFormComponent {
  submitting = false;

  form = new FormGroup<ContactFormValue>({
    email: new FormControl('', { nonNullable: true, validators: [Validators.required, Validators.email] }),
    message: new FormControl('', { nonNullable: true, validators: [Validators.required, Validators.minLength(10)] }),
  });

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.submitting = true;
  }
}
```

## Validation Patterns

- Keep validator functions pure and reusable.
- Use helper functions for repeated error-message logic.
- Show field errors only after touch, dirty, or submit attempts.
- Prefer one submission path per form.
- Reset forms only after a successful submission or explicit user action.

## Zoneless-Friendly Forms

Reactive forms update form state and emit observables, but they do not automatically refresh a zoneless component. If a template depends on reactive-form state, connect it to signals or notify Angular explicitly with change detection.

## Anti-Patterns

- Do not bury validation rules inside template-only logic.
- Do not mix server and field errors into one undifferentiated message source.
- Do not allow submit handlers to perform multiple unrelated jobs.

## Review Checklist

- Form state is typed.
- Validation is reusable and explicit.
- Error display rules are consistent.
- Submission flow is single-path and predictable.
