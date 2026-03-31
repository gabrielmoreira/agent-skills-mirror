# Brand & Design Identity Rules

## Primary Accent — Orange

Creative Tim's brand color is **orange**. Always use orange for primary accents, interactive elements, CTAs, and logo marks.

### Correct

```tsx
// Logo / app icon
<div className="flex h-8 w-8 items-center justify-center rounded-lg bg-orange-600">
  <Bot className="h-4 w-4 text-white" />
</div>

// Avatar fallback
<AvatarFallback className="bg-orange-100 text-orange-700">JD</AvatarFallback>

// Type badge
<Badge className="bg-orange-50 text-orange-700 border-orange-200">OpenClaw</Badge>

// Active nav item accent
<span className="h-1 w-5 rounded-full bg-orange-500" />
```

### Wrong

```tsx
// DO NOT use violet or purple — signals AI-generated defaults
<div className="bg-violet-600">
<Badge className="text-purple-700">
<span className="text-indigo-500">
```

**Why:** Purple/violet is the default accent in many AI coding tools. Blocks using these colors look auto-generated and break visual consistency with the Creative Tim brand.

## Status Color System

| State | Tailwind Color |
|-------|---------------|
| Active / Success | `emerald` |
| Warning / In-Review / Paused | `amber` |
| Error / Stopped / Critical | `red` |
| Info / In-Progress | `blue` |
| Neutral / Backlog | `slate` |

## Surface & Border Conventions

- **Sidebar / subtle backgrounds:** `bg-muted/30`
- **Card backgrounds:** default `bg-background` (Card component handles this)
- **Borders:** use `border` theme token — never `border-gray-200` or hardcoded colors
- **Text:** `text-foreground` (primary), `text-muted-foreground` (secondary/captions)

## Do Not Use Inline Styles

```tsx
// WRONG
<div style={{ color: '#ff6b35' }}>

// CORRECT
<div className="text-orange-500">
```
