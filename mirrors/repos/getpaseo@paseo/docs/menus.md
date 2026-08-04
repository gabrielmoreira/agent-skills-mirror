# Menus

One engine, in `packages/app/src/components/ui/menu/`. `dropdown-menu.tsx` and `context-menu.tsx`
are wrappers over it and differ only in what opens them — a press, or a long press / right click.
Import the `DropdownMenu*` or `ContextMenu*` names as before; reach for `@/components/ui/menu`
directly only when you are building a third trigger shape.

Do not add a third menu implementation. The two that existed were byte-identical from
`computePosition` down, and the copies drifted: only one of them ever grew a sheet.

## Two presentations

`MenuRoot` picks one from form factor, never from platform — a tablet in a narrow split view
sheets the same way a phone does.

| Screen                         | Surface                         | Submenus                                           |
| ------------------------------ | ------------------------------- | -------------------------------------------------- |
| Wide                           | Popover anchored to the trigger | Flyout overlapping the row, opened by hover intent |
| Compact, `compactMode="sheet"` | Bottom sheet                    | The page is replaced in place, with a back header  |
| Compact, default               | Popover                         | Same as wide                                       |

`compactMode` defaults to `"popover"`, so adopting the sheet is per-menu. That is deliberate:
flipping every menu in the app to sheets at once is not a change anyone can review. Opt a menu in
when you have actually looked at it on a phone.

`ContextMenu` is the exception: it defaults to `compactMode="sheet"` and enables native long press.
Disable mobile triggering explicitly on draggable rows, where long press belongs to drag instead.

## Pages

A submenu is a page, declared as data on the surface and reached by a `MenuSubTrigger` whose `id`
matches:

```tsx
<MenuSurface pages={pages} sheetTitle="Display">
  <MenuSubTrigger id="grouping" value="Project">
    Grouping
  </MenuSubTrigger>
</MenuSurface>
```

Pages are data rather than nested children because the popover renders them as _siblings_ of the
root surface — a flyout nested inside the root's box would be clipped by its `overflow: hidden`.
Declaring them separately is what lets one model drive both presentations.

`menu-navigation.ts` holds that model, and it is pure: the open flyout chain and the mobile push
stack are the same path, so the popover renders every entry in it and the sheet renders only the
last. Nothing else differs between the two.

Opening a submenu truncates the path to the depth of the trigger that opened it. Without that,
sliding the pointer across a row of triggers would stack up every flyout it passed instead of
swapping between them.

## Hover intent

A flyout **overlaps its parent by 5pt** rather than sitting beside it. With a gap there is a strip
of backdrop between the two that belongs to neither surface, and every pixel of it is a chance to
dismiss the menu you are reaching for. Overlapping deletes the strip; don't reintroduce the gap
and try to cover it with a longer timer.

On top of that, a flyout opens after the pointer rests ~90ms, closes ~260ms after it leaves, and
cancels its own pending close while the pointer is inside it. The grace still matters because the
pointer crosses sibling rows on the way down into the flyout.

Hover lives on a plain `View`, never on a `Pressable` — see [hover.md](hover.md), which owns that
rule. Hover only fires on web, which is exactly where flyouts exist; everywhere else the page
opens on press.

## Item states

`selected` and `active` are different questions and must not be merged.

| Prop       | Means                      | Draws                     |
| ---------- | -------------------------- | ------------------------- |
| `selected` | This is the chosen value   | A check, and nothing else |
| `active`   | This row's submenu is open | The fill, and no check    |

A selected row does **not** get a background. A check and a fill are two separate claims about the
same state, and showing both makes a chosen row compete with the row the pointer is actually on.
`showSelectedCheck` moves the check to a reserved leading column when a group needs to stay
aligned whether ticked or not; otherwise it sits at the trailing edge and the leading slot is free
for the option's icon.

Give options icons; leave the root rows without them. The root is labels and their current values,
and a column of icons there is decoration competing with the values you actually came to read.

## Surface details

- The hover fill is **inset by the same amount on every side and rounded** — a chip inside the
  menu, not a band across it. The inset is taken _out of_ the row, never added to it: horizontally
  padding gives up what margin takes so labels don't move, and vertically the fill is shorter by
  the same amount so the row pitch is unchanged. Insetting by growing the row is how the menu ends
  up taller than it started.
- The fill's height only holds because the label's `lineHeight` is pinned. Leave it to the platform
  and content outgrows `minHeight`, which then does nothing.
- **The item's inset is the menu's only spacing.** Rows sit apart because each holds itself in, and
  a separator gets clearance from its neighbours for free. Don't give the separator a margin of its
  own — that is two numbers controlling one gap, and they will disagree.
- Separators use `borderAccent`, the same colour the surface outlines itself with. `border` sits
  between `surface1` and `surface2`, which put it within a hair of the hover fill and made
  separators disappear against a hovered row.

## When a decision earns a submenu

Put a decision behind a submenu when its options are not the point — the current _value_ is. The
root row then reads as the answer (`Grouping  Project ›`) and costs one line instead of one line
per option. A menu whose every option is on screen at once does not survive its third decision.

Independent toggles stay on their page as a checkmark list. A pick-one group can share that page
below a `MenuSeparator`; make selecting the checked row clear it, so "none" doesn't need a row of
its own.

## Gotchas

- **Released height.** Reanimated's web entering animation leaves an inline height snapshot on
  the surface. `AnchoredSurface` clears it, and a `revision` prop re-clears it when content
  identity changes — a pushed page taller than the one it replaced is clipped without that.
- **Sheets size to content.** `enableDynamicSizing`, not fixed snap points. A pushed page is
  rarely the height of the page before it.
- **The sheet's content is teleported out of the menu's subtree**, so `MenuSheetSurface` rebuilds
  both menu contexts through the sheet's `contextBridge`. Providing them around the modal puts
  them on the wrong side of the portal and every item inside throws. Gotcha 7 in
  [floating-panels.md](floating-panels.md).
- **One overlay per menu.** Submenus render inside their parent's layer and paint no second
  backdrop, so there is exactly one `Modal` on native no matter how deep the menu goes.
- Anchoring, flipping, and edge clamping live in `menu-anchor.ts` and are unit-tested. Fix
  positioning bugs there, not at a call site.
- Everything else about floating surfaces on Android — Portal/Modal escape, lifecycle gates,
  status-bar offset, the open flash — is in [floating-panels.md](floating-panels.md).
