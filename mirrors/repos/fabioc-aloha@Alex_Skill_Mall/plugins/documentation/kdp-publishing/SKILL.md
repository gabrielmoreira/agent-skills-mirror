---
type: skill
inheritance: inheritable
lifecycle: stable
name: kdp-publishing
description: "Amazon KDP self-publishing specs — cover requirements, interior formatting, spine formulas, ink options, and pricing tiers"
applyTo: "**/*kdp*,**/*publish*,**/*book*"
tier: extended
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Domain Knowledge: Amazon KDP Self-Publishing

**Source**: Validated from publishing *Alex in Wonderland* (Amazon KDP, February 21, 2026)
**Applies to**: Any book published via Amazon Kindle Direct Publishing
**Last verified**: February 21, 2026

## Live Reference: *Alex in Wonderland* (Published February 21, 2026)

| Field           | Value                                                                         |
| --------------- | ----------------------------------------------------------------------------- |
| Title           | Alex in Wonderland: A Detective Mystery Adventure                             |
| Series          | Alex Finch Detective Series, Book 1                                           |
| Author          | *(your name)*                                                                 |
| ISBN            | 979-8-24895072-0 (KDP free ISBN, 979-8 prefix)                                |
| Kindle ASIN     | B0GPCV6V6R — [amazon.com/dp/B0GPCV6V6R](https://www.amazon.com/dp/B0GPCV6V6R) |
| Paperback ASIN  | B0GPJ4HP27 — [amazon.com/dp/B0GPJ4HP27](https://www.amazon.com/dp/B0GPJ4HP27) |
| eBook price     | $5.00 (qualifies for 70% royalty tier)                                        |
| Paperback price | $28.00                                                                        |
| KDP Select      | Enrolled (eBook)                                                              |
| Status          | Both formats: Live                                                            |
| Submitted       | February 21, 2026                                                             |

---

## Platform Overview

Amazon KDP offers free print-on-demand publishing of eBooks, paperbacks, and hardcovers at kdp.amazon.com. No upfront costs. Royalties paid ~60 days after month-end threshold (~$100).

---

## Supported Formats

| Format          | Pages  | Notes                                  |
| --------------- | ------ | -------------------------------------- |
| Kindle eBook    | —      | Reflowable; no ISBN required           |
| Paperback (POD) | 24–828 | Matte or glossy cover                  |
| Hardcover (POD) | 75–550 | Not eligible for Expanded Distribution |

---

## Interior Specifications (6×9 Paperback)

| Element          | Requirement                      |
| ---------------- | -------------------------------- |
| Margins          | Min 0.375" inside, 0.25" outside |
| Bleed            | 0.125" if images extend to edge  |
| Image resolution | **300 DPI minimum** (critical)   |
| Image color mode | CMYK for print; RGB for eBook    |
| Max file size    | 650 MB                           |

### Ink Options

| Option         | Use case                    | Cost/page (US) |
| -------------- | --------------------------- | -------------- |
| Black Ink      | B&W illustrations only      | $0.012         |
| Standard Color | Budget color (72–600 pages) | $0.0255        |
| Premium Color  | Best quality                | $0.065         |

**Recommendation for illustrated books**: Standard Color for cost-effective full-color chapter banners.

---

## Cover Specifications

| Element      | Requirement                                         |
| ------------ | --------------------------------------------------- |
| File type    | Single PDF (front + spine + back wrap)              |
| Resolution   | 300 DPI minimum                                     |
| Color mode   | CMYK                                                |
| Bleed        | 0.125" on all outside edges                         |
| Cover finish | Glossy recommended for children's/illustrated books |
| eBook cover  | 2560 × 1600 px ideal; JPEG or TIFF; RGB             |

### Spine Width Formula (6×9)

```
Black ink/white paper:   page_count × 0.002252"
Premium color/white:     page_count × 0.002347"
```

Example (280 pages, standard color): ~0.63–0.66"

**Tool**: Use KDP Cover Calculator at kdp.amazon.com/cover-calculator for exact template.

---

## ISBN Strategy

| Option            | Cost                      | Imprint                   | Portable |
| ----------------- | ------------------------- | ------------------------- | -------- |
| Free KDP ISBN     | $0                        | "Independently published" | KDP only |
| Own ISBN (Bowker) | $125 single / $295 for 10 | Your imprint name         | Yes      |

**Rule**: Each format (eBook, paperback, hardcover) requires a unique ISBN.
**Recommendation**: Own ISBN if planning wide distribution beyond Amazon; free ISBN if Amazon-exclusive.

---

## Pricing & Royalties

### eBook

| Rate    | Price range     | Notes                       |
| ------- | --------------- | --------------------------- |
| 35%     | $0.99–$200      | Any price                   |
| **70%** | **$2.99–$9.99** | Minus $0.15/MB delivery fee |

**Recommended eBook price**: $4.99–$6.99 (qualifies for 70%)

### Paperback (6×9, Standard Color, ~280 pages)

```
Printing cost = $1.00 + (pages × $0.0255)
280 pages → $1.00 + $7.14 = $8.14 printing cost

At $14.99: (0.60 × $14.99) − $8.14 = $0.85 royalty
At $17.99: (0.60 × $17.99) − $8.14 = $2.65 royalty
```

**Recommended paperback price**: $15.99–$17.99

### Expanded Distribution (Paperback only)

- 40% royalty (vs. 60% direct)
- Access to Ingram, bookstores, libraries
- Allow 8 weeks to appear in channels

---

## Categories & Keywords

**Reading age settings**:
- Ages 9–12 → Children's Books categories
- Ages 13–17 → Teen & Young Adult categories

**Category selections** (up to 3 for middle-grade mystery):
1. Children's Books > Mysteries & Detectives
2. Children's Books > Science Fiction & Fantasy > Fantasy & Magic
3. Children's Books > Growing Up & Facts of Life > Friendship

**Keywords** (up to 7): Use specific, searchable terms. Update monthly based on search trends.

---

## Publication Timeline

| Action                | Timeline                             |
| --------------------- | ------------------------------------ |
| eBook review          | 24–72 hours                          |
| Paperback review      | Up to 72 hours (US) / 5 days (other) |
| "Look Inside" feature | 7–10 business days                   |
| Editions linked       | 48 hours to 1 week                   |
| Expanded Distribution | Up to 8 weeks                        |

---

## Marketing Tools

| Tool               | What it does                                                                                    |
| ------------------ | ----------------------------------------------------------------------------------------------- |
| Author Central     | Author page, bio, BookScan data, editorial reviews                                              |
| A+ Content         | Enhanced detail page with images (8 business days review)                                       |
| KDP Select         | Kindle Unlimited enrollment; Free promotions (5 days/90-day period); requires eBook exclusivity |
| Sponsored Products | Search result ads; $0.10–$0.50/click typical                                                    |

---

## Common Pitfalls

1. **Low-res images**: 300 DPI must be at final print size — upscaling won't fix quality
2. **Wrong color mode**: Convert to CMYK before embedding in print manuscript
3. **Bleed mistakes**: Set up manuscript with 0.125" bleed if banners extend to page edges
4. **Spine variance**: Allow ±0.125" variance — don't place critical elements near fold lines
5. **Age/category mismatch**: Wrong reading age prevents appearance in children's categories
6. **ISBN mismatch**: ISBN printed in interior must match what's entered in KDP for each format

---

## Pre-Publishing Checklist

- [ ] Create KDP account and complete W-9 (Tax Questionnaire)
- [ ] Add bank account for direct deposit
- [ ] Finalize manuscript as PDF with 300 DPI images
- [ ] Calculate spine width and generate cover wrap
- [ ] Decide ISBN strategy (free vs. own)
- [ ] Order physical proof copy before publishing (~$10–15)
- [ ] Upload eBook first (fastest to go live)
- [ ] Set reading age (9–12 or 13–17)
- [ ] Select 3 categories and 7 keywords
- [ ] Set prices (eBook $4.99–6.99; paperback $15.99–17.99)
- [ ] Enable Expanded Distribution (paperback)

## Post-Publishing Checklist

- [ ] Claim Author Central page
- [ ] Set up A+ Content
- [ ] Link all editions (eBook + paperback + hardcover)
- [ ] Run $0.99 launch promotion (KDP Select Free Days or Countdown Deal)
- [ ] Set up Amazon Advertising campaign

---

## Cost Estimate (Minimum)

| Item                      | Cost        |
| ------------------------- | ----------- |
| KDP Publishing            | Free        |
| Proof copy                | ~$10–15     |
| Author copies (10)        | ~$100–150   |
| Own ISBN (optional)       | $125–295    |
| Advertising (optional)    | $100–500/mo |
| **Minimum out-of-pocket** | **~$10–15** |

---

## Distribution Comparison

| Platform             | Market share          | Royalty | Exclusivity           |
| -------------------- | --------------------- | ------- | --------------------- |
| Amazon KDP           | ~80%                  | 35–70%  | Optional (KDP Select) |
| IngramSpark          | Bookstores, libraries | 55%     | No                    |
| Draft2Digital        | Multiple retailers    | 60%     | No                    |
| Barnes & Noble Press | B&N stores            | 65%     | No                    |

**Wide strategy**: All platforms — maximum reach
**Exclusive strategy**: KDP only — KDP Select perks, Kindle Unlimited per-page royalties
