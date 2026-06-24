---
name: ng22-signal-forms
description: Enforces Angular 22 signal-centric form patterns, computed validation mapping, and controlled state mutation.
---

# Angular 22 Signal-Centric Forms

Build forms with explicit reactive state and avoid fallback to legacy patterns. Treat each form as a signal-driven data model with deterministic validation and update flow.

## Core Rules

1. Do not default to `FormBuilder` or template-driven forms for new complex workflows.
2. Keep primary form state in signals and derive view state with `computed()`.
3. Model validation errors as computed maps so error rendering is deterministic and centralized.
4. Use signal inputs to seed initial control values and keep initialization explicit.
5. Keep form arrays trackable with signal-backed collections and immutable updates.

## Signal Input Initialization Pattern

```typescript
import { Component, computed, input, signal } from '@angular/core';

type ProfileForm = {
  name: string;
  aliases: string[];
};

@Component({
  standalone: true,
  selector: 'app-profile-form',
  template: `
    <input [value]="form().name" (input)="setName($any($event.target).value)" />

    @for (alias of form().aliases; track $index; let i = $index) {
      <input [value]="alias" (input)="setAlias(i, $any($event.target).value)" />
    }

    @if (errors().name) {
      <p>{{ errors().name }}</p>
    }
  `,
})
export class ProfileFormComponent {
  initialName = input<string>('');
  initialAliases = input<string[]>([]);

  form = signal<ProfileForm>({
    name: this.initialName(),
    aliases: [...this.initialAliases()],
  });

  errors = computed(() => {
    const value = this.form();

    return {
      name: value.name.trim().length < 2 ? 'Name must be at least 2 characters.' : '',
      aliases: value.aliases.map((alias) =>
        alias.trim().length === 0 ? 'Alias cannot be empty.' : ''
      ),
    };
  });

  setName(name: string): void {
    this.form.update((value) => ({ ...value, name }));
  }

  setAlias(index: number, alias: string): void {
    this.form.update((value) => ({
      ...value,
      aliases: value.aliases.map((current, i) => (i === index ? alias : current)),
    }));
  }
}
```

## Form Array Mutation Discipline

- Add rows with immutable operations such as `aliases: [...aliases, '']`.
- Remove rows with index-filtered copies, never in-place mutation.
- Keep the rendered list keyed with stable tracking (`track item.id`) when available.

## Validation Mapping Pattern

- Derive all validation state in one `computed()` tree.
- Keep field-level and cross-field rules together so templates remain simple.
- Keep error text generation centralized to avoid duplicated string logic in templates.

## Anti-Patterns

- Mixing template-driven directives with signal-first form state.
- Triggering hidden side effects from validators.
- Mutating arrays or nested objects in place and expecting deterministic updates.
- Spreading validation logic across template fragments.

## Review Checklist

- Form state is signal-backed.
- Validation is computed and centralized.
- Arrays are updated immutably and tracked correctly.
- Initialization uses explicit signal inputs.
