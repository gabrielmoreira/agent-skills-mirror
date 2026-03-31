# Tailwind v4 Rules

## No Arbitrary Values

The project uses Tailwind v4 with a continuous numeric scale. Never use bracket arbitrary values.

### Wrong

```tsx
<div className="h-[380px] w-[280px] max-w-[85%] min-w-[80px]">
<div className="gap-[14px] p-[18px] text-[10px] text-[11px]">
<div className="[@media(min-width:640px)]:grid-cols-2">
```

### Correct

```tsx
<div className="h-96 w-72 max-w-sm">          // h-96=384px, w-72=288px
<div className="gap-3.5 p-4 text-xs">          // gap-3.5=14px, p-4=16px
<div className="sm:grid-cols-2">
```

## Numeric Scale Reference

### Height / Width
```
h-4  = 16px    h-5  = 20px    h-6  = 24px    h-7  = 28px
h-8  = 32px    h-9  = 36px    h-10 = 40px    h-11 = 44px
h-12 = 48px    h-14 = 56px    h-16 = 64px    h-20 = 80px
h-24 = 96px    h-32 = 128px   h-40 = 160px   h-48 = 192px
h-56 = 224px   h-64 = 256px   h-72 = 288px   h-80 = 320px
h-96 = 384px
```

### Spacing (gap / padding / margin)
```
0.5=2px  1=4px  1.5=6px  2=8px  2.5=10px  3=12px  3.5=14px
4=16px   5=20px  6=24px   7=28px  8=32px   9=36px  10=40px
12=48px  14=56px  16=64px
```

### Max Width Semantic Utilities
```
max-w-xs  = 320px     max-w-sm  = 384px
max-w-md  = 448px     max-w-lg  = 512px
max-w-xl  = 576px     max-w-2xl = 672px
max-w-3xl = 768px     max-w-4xl = 896px
max-w-5xl = 1024px    max-w-6xl = 1152px
max-w-7xl = 1280px
```

## Typography Scale

```
text-xs   = 12px   (avatar initials, badge pills, mono timestamps, tiny buttons)
text-sm   = 14px   (body text, table cells, descriptions — DEFAULT)
text-base = 16px   (larger body, card titles)
text-lg   = 18px   (section headings)
text-xl   = 20px   (page headings)
text-2xl  = 24px   (stat values, hero text)
```

**Rule:** `text-sm` is the minimum for readable content. Use `text-xs` only for tiny decorative elements.

## Responsive Breakpoints

Use only standard Tailwind breakpoints:
```
sm: 640px    md: 768px    lg: 1024px    xl: 1280px    2xl: 1536px
```

Never use custom media query syntax.
