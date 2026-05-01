# Komponent Örnekleri — Referans

Bu dosya `SKILL.md` tarafından referans olarak okunuyor. Ajan "komponent kararı" gerektiğinde buraya bakıyor.

## Kural: önce mevcut kütüphane

Yeni bir komponent yazmadan önce `shadcn/ui` içinde var mı kontrol et. 90% zaman vardır.

## Temel komponentler

### Button
- Varyantlar: `primary | secondary | ghost | destructive`
- Durumlar: `default | hover | active | disabled | loading`
- Keyboard: Enter + Space tetikler
- A11y: `aria-busy="true"` loading sırasında
- Kaynak: `shadcn/ui` button

### Card
- Yapı: `CardHeader > CardTitle + CardDescription`, `CardContent`, `CardFooter`
- Varyant: `elevated` (shadow) | `outline` (border) | `ghost` (bg yok)
- Kaynak: `shadcn/ui` card

### Input / Form Field
- Her input: `Label + Input + HelperText + ErrorText`
- A11y: label `htmlFor` → input `id` eşleşmeli
- Error state'i `aria-invalid="true"` + `aria-describedby`
- Kaynak: `shadcn/ui` form (react-hook-form + zod)

### Modal / Dialog
- Focus trap zorunlu
- Esc ile kapanmalı
- Background scroll kilitle
- A11y: `role="dialog"`, `aria-labelledby`, `aria-modal="true"`
- Kaynak: `shadcn/ui` dialog (radix-ui altta)

### Navbar
- Sticky mi, fixed mi, static mi — projeye göre
- Mobil: hamburger + drawer
- A11y: `role="navigation"`, aktif link `aria-current="page"`

## Kalıp komponentler

### Pricing Card (3 plan)
```
Card
├─ Badge ("Most popular" · opsiyonel)
├─ CardTitle (Plan adı)
├─ Price (büyük) + Period (/month)
├─ FeatureList (Check icon + text)
└─ CTA Button
```
- Varyant vurgu: ortadaki kart ölçek (scale-105) ve border vurgulu
- Toggle: monthly/yearly → animated price

### Dashboard Layout
```
Sidebar (w-64) | Main Content
                ├─ TopBar (h-14)
                └─ ContentArea (p-6)
```
- Responsive: sidebar mobilde drawer olur
- Sidebar açıldığında `aria-expanded` değişmeli

### Data Table
- `shadcn/ui` data-table — tanstack-table altta
- Sıralama, filtreleme, pagination zorunlu
- Boş durum (empty state) tasarla — kullanıcı "veri yok mu, yükleniyor mu?" diye tahmin etmemeli

## State'ler (her komponent için kontrol listesi)

- [ ] **Default** — boş/başlangıç
- [ ] **Loading** — spinner / skeleton
- [ ] **Empty** — veri yok
- [ ] **Error** — bir şey patladı
- [ ] **Success** — işlem başarılı

Bu 5 state kontrol edilmezse tasarım eksiktir.

## Responsive breakpointler (Tailwind)

| Breakpoint | Genişlik | Kullanım |
|---|---|---|
| sm | 640px | küçük tablet |
| md | 768px | tablet |
| lg | 1024px | laptop |
| xl | 1280px | büyük ekran |
| 2xl | 1536px | geniş monitör |

Mobile-first: önce mobil yaz, breakpoint prefix'leriyle büyüt.

---

(gerçek skill'de 100+ komponent örneği olurdu — bu kısaltılmış demo örneği)
