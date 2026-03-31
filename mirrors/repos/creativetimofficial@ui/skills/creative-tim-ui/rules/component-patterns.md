# Component Patterns

## Card Structure

Standard grouping pattern: `Card > CardHeader + CardContent`.

```tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

<Card>
  <CardHeader>
    <CardTitle className="text-sm font-medium">Section Title</CardTitle>
  </CardHeader>
  <CardContent>
    {/* content */}
  </CardContent>
</Card>
```

## KPI / Stat Cards — Use py-0

Stat grid cards use `py-0` so vertical rhythm is controlled by the parent grid, not the card itself.

```tsx
// CORRECT
<Card className="relative overflow-hidden">
  <CardContent className="px-4 py-0">
    <div className="absolute top-0 left-0 h-full w-1 bg-emerald-500" />
    <p className="text-muted-foreground text-sm">Active Agents</p>
    <p className="mt-1 text-2xl font-bold text-emerald-700">4</p>
  </CardContent>
</Card>

// WRONG — default py-6 causes excessive padding in stat grids
<Card>
  <CardContent className="p-4">
```

## Sidebar Navigation

Width: `w-64` (256px). Background: `bg-muted/30`. Right border: `border-r`.

```tsx
<aside className="bg-muted/30 flex h-full w-64 flex-col border-r">
  <div className="flex items-center gap-2.5 border-b px-5 py-4">
    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-orange-600">
      <Bot className="h-4 w-4 text-white" />
    </div>
    <span className="text-sm font-semibold">App Name</span>
  </div>
  <nav className="flex-1 space-y-0.5 p-3">
    {NAV_ITEMS.map((item) => (
      <button
        key={item.label}
        className={`flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors ${
          item.active
            ? "bg-background text-foreground shadow-sm"
            : "text-muted-foreground hover:bg-background/60 hover:text-foreground"
        }`}
      >
        <item.icon className="h-4 w-4" />
        {item.label}
      </button>
    ))}
  </nav>
</aside>
```

## ScrollArea for Overflow

Any list that can overflow must use `ScrollArea` (not `overflow-y-auto` directly).

```tsx
import { ScrollArea } from "@/components/ui/scroll-area"

<ScrollArea className="flex-1">
  <div className="space-y-2 p-4">
    {items.map((item) => <Item key={item.id} {...item} />)}
  </div>
</ScrollArea>
```

## Status Badge with Dot

```tsx
<div className="inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-xs font-medium bg-emerald-50 text-emerald-700 border-emerald-200">
  <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
  Active
</div>
```

## Avatar Fallback Colors

Use orange tones for user/agent avatars:
```tsx
<AvatarFallback className="bg-orange-100 text-xs font-semibold text-orange-700">
  JD
</AvatarFallback>
```

## Action Buttons in Tables

Small ghost buttons for row actions:
```tsx
<Button variant="ghost" size="sm" className="h-6 px-2 text-xs">
  <Eye className="mr-1 h-3 w-3" />
  View
</Button>
```
