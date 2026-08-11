# `@elizaos/ui/spatial`

Shared spatial authoring primitives for plugin views.

The public modality contracts still include `gui`, `xr`, and `tui`, but this
package currently ships only the DOM authoring/runtime path. The `tui` subpath is
a compatibility seam that throws if called, and the concrete WebXR/headset and
terminal renderers have been removed.

## Authoring

```tsx
import { Button, Card, HStack, SpatialSurface, Text, useSpatialState } from "@elizaos/ui/spatial";

export function Counter({ start = 0 }) {
  const [n, setN] = useSpatialState(start);
  return (
    <SpatialSurface modality="gui">
      <Card title="Counter" gap={1}>
        <Text style="heading">{`Count: ${n}`}</Text>
        <HStack gap={1}>
          <Button onPress={() => setN((v) => v + 1)}>+1</Button>
          <Button variant="outline" onPress={() => setN(0)}>Reset</Button>
        </HStack>
      </Card>
    </SpatialSurface>
  );
}
```

## Vocabulary

| Primitive | IR node | Purpose |
| --- | --- | --- |
| `Stack` / `HStack` / `VStack` | `box` | flex container |
| `Card` | `box` | bordered, padded surface |
| `List` | `box` | vertical list |
| `Text` | `text` | typed text |
| `Button` | `button` | action |
| `Field` | `field` | labelled input |
| `Divider` | `divider` | rule, optionally captioned |
| `Spacer` | `spacer` | fixed or flexible space |
| `Image` | `image` | image metadata |

## State

Use `useSpatialState`, `useSpatialMemo`, and `useSpatialRef` for state that needs
to survive React-to-IR evaluation. DOM views can also use ordinary React hooks
where the logic is DOM-only.

## Verification

- `__tests__/evaluate.test.tsx` covers React-to-IR evaluation and the retained
  terminal compatibility seam.
- `dom.modality-owner.test.tsx` covers DOM modality detection and ownership.

Do not reintroduce concrete XR or terminal rendering by adding ad hoc files under
this package. Add them behind the existing modality contracts with focused tests
when those surfaces are intentionally restored.
