# Creative Tim Design Philosophy

This is not a style guide. It's the thinking behind every decision — what to build, what to cut, and why.

Over a decade, Creative Tim has shipped 300+ open source UI dashboards, templates, and tools used by 2.8 million developers worldwide. That scale of use across that many products leaves no room for guesswork. Every principle here has been tested against real projects, real teams, and real feedback — not theory.

---

## The 95% Rule — Solve the Common Case Exceptionally Well

Every product Creative Tim ships starts with the same question: what do developers actually need? The answer, across hundreds of products and categories, is consistently the same core set of elements — buttons, tables, cards, sidebars, charts, forms, modals, notifications.

That's the 95%. The remaining 5% is Kanban boards, drag-and-drop, custom file uploaders, timeline components, WYSIWYG editors — powerful, but rare.

**The rule:** build the 95% so well that no one feels the lack of the 5%.

For agents generating code: do not reach for complex solutions to solve simple problems. A developer looking at a block should not find themselves unwrapping three layers of abstraction to change a label. The common case should be obvious, direct, and complete.

```tsx
// WRONG — solves a hypothetical future problem
<DataTable
  columns={columns}
  data={data}
  sortable
  filterable
  paginated
  exportable
  selectable
  onRowClick={handleRowClick}
  onSelectionChange={handleSelection}
  renderCustomCell={(cell) => <CustomCell {...cell} />}
/>

// RIGHT — solves the actual problem in front of you
<Table>
  <TableHeader>...</TableHeader>
  <TableBody>
    {items.map((item) => (
      <TableRow key={item.id}>
        <TableCell>{item.name}</TableCell>
        <TableCell>{item.status}</TableCell>
      </TableRow>
    ))}
  </TableBody>
</Table>
```

---

## The "Light" Principle — A Block Is Done When There Is Nothing Left to Remove

Across Creative Tim's product line, "light" is a recurring word — not because the products lack capability, but because every addition is interrogated. Each plugin, prop, and wrapper adds CSS, JavaScript, and cognitive weight. Most are cut.

This is the hardest design discipline: not building things you know how to build.

**What it means in practice:**

- No feature flags or configuration props for things that can just be changed in code
- No helper components that are only used once
- No animation on elements that don't need to communicate state
- No extra wrapper `div`s that exist only to satisfy a mental model
- No icons that repeat information already conveyed by text
- No empty states, loading states, or error states unless the block actually fetches data

A block should look complete the moment a developer drops it in. Not because it handles every edge case, but because it clearly handles the right ones.

```tsx
// WRONG — wrapping for the sake of wrapping
<SectionWrapper>
  <ContentContainer>
    <InnerContent>
      <Card>...</Card>
    </InnerContent>
  </ContentContainer>
</SectionWrapper>

// RIGHT — as flat as the problem allows
<Card>...</Card>
```

---

## Understand the Problem Before Rendering

The first question is always **what problem does this solve for the person looking at the screen?** Not what looks good in isolation. Not what demonstrates technical capability.

A pricing table exists to reduce friction in a purchase decision. A dashboard exists to surface the one number a person needs to act on. A form exists to collect information with the least possible resistance.

If the purpose of a block is not clear, the block is not clear.

---

## Standing on Foundations — Never Build What Already Exists Well

Creative Tim's history is building *on top of* the best available foundation rather than beside it. Bootstrap → Material Design → shadcn/ui. Each transition kept what worked and added only what was missing.

The same applies to individual blocks. shadcn/ui's `Table`, `Card`, `Button`, `Badge`, `Dialog` are well-designed, accessible, and maintained. Do not rebuild them. Do not wrap them unnecessarily. Do not replicate their functionality in custom components.

The Creative Tim contribution is the **composition** — how these primitives are assembled into something useful for real work. That is where the judgment lives, not in the primitives themselves.

```tsx
// WRONG — reimplementing what shadcn already solved
function CustomButton({ variant, children }) {
  const styles = variant === 'primary' ? 'bg-orange-500 text-white' : 'bg-gray-100'
  return <button className={styles}>{children}</button>
}

// RIGHT — extend the foundation
import { Button } from "@/registry/creative-tim/ui/button"
<Button variant="default">Save changes</Button>
```

---

## Real Use, Not Demo Use

The benchmark for every block is whether a real team would ship it in a production app. Not "does this look impressive in a screenshot?" but "would this hold up under real conditions, used by real people under time pressure?"

**Concretely:** avoid visual complexity that doesn't carry information. A gradient on a card header that doesn't indicate anything is decoration. A status badge that turns red when something is wrong is communication. Only the second one belongs.

```tsx
// WRONG — decoration that doesn't communicate
<CardHeader className="bg-gradient-to-r from-orange-400 to-pink-500 text-white">
  <CardTitle>Users</CardTitle>
</CardHeader>

// RIGHT — surface that lets the content speak
<CardHeader>
  <CardTitle className="text-sm font-medium text-muted-foreground">Users</CardTitle>
</CardHeader>
```

---

## Summary — The Questions to Ask

Before generating or modifying any block, run through these:

1. **Is this in the 95%?** Does this element appear in most real dashboards/UIs, or is it a rare specialization?
2. **What can be removed?** If the block works without it, it probably should.
3. **What is the user trying to do?** Not "what does this block contain" but "what decision does it help someone make?"
4. **Am I building on the foundation or beside it?** Use shadcn/ui primitives. Compose, don't reimplement.
5. **Would this hold up in production?** Not in a demo. In a real app, used by real people under time pressure.
