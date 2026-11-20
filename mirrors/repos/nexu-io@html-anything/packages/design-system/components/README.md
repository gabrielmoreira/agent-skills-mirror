# Open Design UI

This directory owns the shared React controls.

## Preview while designing

From the repository root, install dependencies with `npm ci` once, then start the component site:

```sh
npm run components:dev
```

Open the local URL printed in the terminal. Find the control in the component index, open its detail page, and use the Preview and Code tabs to test and copy an example. Use the toolbar to switch themes. The site also includes a local Contribution guide. Keep the development server running while editing. Saving a component or its example updates the browser. The component site uses the same source as Studio and runs without the Studio backend.

For a new component, add a registry entry and a preview, examples and API notes in [site/examples.tsx](site/examples.tsx). `npm run components:build` generates a static build in `packages/design-system/components/dist`.

To build the installable package candidate, run `npm run build:open-design-ui`. It writes `open-design-ui@0.0.1` to `dist/open-design-ui` without publishing it. Run `npm pack --dry-run` or `npm stage publish --dry-run` from that directory before any separately authorized registry write.

Component details use paths such as `/components/slider`. Vite handles direct links during development and preview. For static hosting, serve the build at the origin root and fall back to `index.html` for catalogue page routes.

## Use from an Agent

Ask the Agent to use the repository-local [ODUI apply Skill](../../../.agents/skills/odui-apply/SKILL.md) and give it the Studio page or control to change. For example, `Use $odui-apply to replace the retry button in workspace search. Keep its behavior and verify the existing test.`

The component detail page offers **Copy to Agent** for a new use case and **Copy migration prompt** for replacing an existing control. Add the target Studio page or feature to the copied prompt before using it.

Read [registry.json](registry.json) to discover each control's source path, import alias, named export, example and product consumer. The site also serves the same file at `/registry.json`. Use the listed alias in Studio and in the component site:

```tsx
import { Button } from 'open-design-ui/button';
import { IconButton } from 'open-design-ui/icon-button';
import { Slider } from 'open-design-ui/slider';
```

Studio already loads the two shared styles in the registry. Keep the app's Tailwind source scan pointed at the shared controls. The alias resolves to source in this checkout through TypeScript and Vite. Agents can use it with their normal repo tools.

- `Button` supports native button props, `primary`, `secondary`, `ghost` and `danger` variants, three sizes, an optional icon and a loading state. Set the native `type` deliberately. Both button components accept `variant="plain"` for controls with their own layout and surface. It keeps the keyboard focus style and leaves sizing to the caller.
- `IconButton` requires an icon and an accessible name (`aria-label`). It defaults to a medium, square ghost button and accepts the same variants and native button props.
- `Slider` takes a named, bounded numeric value. Use `onPreview` for temporary feedback and `onCommit` to store a change. Keep provider defaults and validation in the feature.

In Studio application code, use these shared controls for new actions and ranges. `npm run design:check` rejects native JSX `<button>` (including `om-button`) and `<input type="range">` that exceed the [per-file legacy baseline](../../../scripts/studio-native-controls.json). When migrating a legacy control, lower its count and remove zero-count entries. CI runs the same rule through `npm run check`.

## Contribute a control

1. In the design or brief, show the actual use, states, keyboard behavior and token choices. Use the [shared design system](../README.md) for color, typography, spacing and motion.
2. Set `data-odui-component` on the component root to its registry name for the Studio UI inspector. Add the shared source, the registry entry and an interactive example in [site/examples.tsx](site/examples.tsx). Connect one real Studio use case in the same PR. Set `consumer` to the production JSX file that renders the registered export through its alias. Preserve that call site's events, labels, focus and layout.
3. Start with `"adoption": { "mode": "opt-in", "review": "..." }`. In `review`, name a representative remaining use case or the behavior that must be verified before enforcing reuse. If the control should stay optional, write the reason. Include the verified Studio use case and this decision in the PR.
4. Run `npm run design:check`, `npm run typecheck:studio`, `npm run components:build` and relevant Studio tests. Check the example and the real consumer with a keyboard and in both themes.

### Enforce reuse

When the review condition is met, document the common Studio uses and any specialized controls that need separate behavior. When reuse should be mandatory, add the native control rule in [the checker](../../../scripts/check-component-imports.ts) and record existing uses in [the baseline](../../../scripts/studio-native-controls.json). Update the registry to `"adoption": { "mode": "enforced" }` in the same PR. Show that the shared control works in the chosen use cases and verify that lint rejects a new native instance. The baseline lets existing uses migrate incrementally.

`npm run design:check` verifies that each registry entry points to a Studio file that renders its registered export. It checks that the declared adoption mode matches the implemented rule and that opt-in entries record a review condition or reason.

### First migration

[GenerationParameters](../../../studio/src/motion/GenerationParameters.tsx) now imports the shared Slider directly. The provider still owns the label, range, step, default and committed value. Existing React Button and Slider callers use the aliases directly. Component implementations depend on their own directory and shared UI dependencies. The preview can also load design system assets. `npm run design:check` checks these import boundaries.

## Project Skills

The repository-local Skills are split by intent:

| Skill | Use it for |
| --- | --- |
| [`odui-dev`](../../../.agents/skills/odui-dev/SKILL.md) | Start the catalogue, inspect states and review live changes. |
| [`odui-build`](../../../.agents/skills/odui-build/SKILL.md) | Create or evolve a component, example, registry item and real consumer. |
| [`odui-apply`](../../../.agents/skills/odui-apply/SKILL.md) | Replace a business control with an existing shared component. |
| [`odui-check`](../../../.agents/skills/odui-check/SKILL.md) | Audit tokens, boundaries, adoption status and browser evidence before review. |

Use the Skill that matches the work. A catalogue preview does not replace verification of the real Studio consumer.

In an Agent prompt, name the Skill directly. For example, use `$odui-dev` to open the local catalogue, `$odui-build` to add a new control, `$odui-apply` to replace an existing Studio control, or `$odui-check` before review. These Skills are repository-local and are available after the Agent reads `AGENTS.md`.
