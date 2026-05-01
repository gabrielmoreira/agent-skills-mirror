---
name: ui-ux-pro-max
description: UI/UX design intelligence. Use when user asks for UI/UX design, component architecture, layout, color system, or visual hierarchy decisions. Includes 50+ styles, 161 palettes, 57 font pairings.
---

# UI/UX Pro Max

## Ne zaman tetiklenir
- Kullanıcı UI/UX tasarımı istediğinde
- "component", "layout", "design system", "color palette" geçtiğinde
- Landing page, dashboard, admin panel, e-commerce UI tasarımı

## Referans dosyaları

Bu skill klasöründe ek referanslar var:
- `styles.md` — 50+ stil (glassmorphism, neumorphism, brutalism, bento grid, ...)
- `palettes.md` — 161 renk paleti
- `fonts.md` — 57 font eşleşmesi
- `components.md` — komponent örnekleri

## Yaklaşım

### 1. İhtiyacı anla
Kullanıcı ne istiyor? Website? Dashboard? Landing?

### 2. Stili seç
`styles.md`'den projeye uygun stili çek. Gerekçesiyle sun.

### 3. Renk paleti seç
`palettes.md`'den uygun paleti al. Marka kimliğine dikkat et.

### 4. Tipografi
`fonts.md`'den 2 font eşleşmesi seç (heading + body).

### 5. Komponentleri planla
`components.md`'den örneklere bak, projeye uyarla.

## Çıktı formatı

```
## Tasarım Özeti
- **Stil:** <seçilen stil, neden>
- **Palet:** <renkler + hex kodlar>
- **Fontlar:** <heading + body>
- **Anahtar componentler:** <liste>
- **Responsive yaklaşımı:** <breakpointlar>
- **Accessibility notları:** <aria, keyboard nav, contrast>
```

## Kurallar

- Stack: Tailwind v4 + shadcn/ui (varsayılan)
- Ant Design kullanma
- Dark mode + responsive her zaman
- Accessibility zorunlu — her component aria + keyboard nav alır
