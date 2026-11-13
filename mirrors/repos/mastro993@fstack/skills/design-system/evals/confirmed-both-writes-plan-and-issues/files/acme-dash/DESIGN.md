---
version: alpha
name: Acme Dash
description: Calm, dense operations dashboard.
colors:
  primary: "#2F5BEA"
  primary-hover: "#2549C4"
  on-primary: "#FFFFFF"
  surface: "#FFFFFF"
  on-surface: "#16181D"
  muted: "#6B7280"
  border: "#E3E5EA"
  danger: "#C8372D"
typography:
  title-lg:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: 700
    lineHeight: 1.25
  title-md:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: 600
    lineHeight: 1.3
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.45
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: 500
    lineHeight: 1.3
  caption:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: 500
    lineHeight: 1.3
rounded:
  sm: 4px
  md: 8px
  lg: 12px
  full: 9999px
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.label-md}"
    rounded: "{rounded.md}"
    padding: 8px 16px
  button-primary-hover:
    backgroundColor: "{colors.primary-hover}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.md}"
    padding: 8px 16px
  button-danger:
    backgroundColor: "{colors.danger}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.md}"
    padding: 8px 16px
  card:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.lg}"
    padding: 16px
---

## Overview
An internal operations dashboard for project leads and finance staff. Calm and dense: data first, one clear primary action per screen.

## Colors
- **Primary (#2F5BEA):** the main action on a screen, links, focus rings.
- **Surface / On-surface:** cards and text.
- **Muted (#6B7280):** secondary text and metadata.
- **Border (#E3E5EA):** card and input outlines.
- **Danger (#C8372D):** destructive actions and overdue amounts only.

Dark mode values live in `src/styles/theme.css` and are not yet recorded here.

## Typography
Inter throughout. Titles at 24px and 18px, body and labels at 14px, captions at 12px.

## Layout
A 4px rhythm: 4, 8, 16, 24, 32. Pages are centered at max 1024px with 32px padding.

## Elevation & Depth
Mostly flat. Cards use a 1px border and at most a small shadow; dialogs use a large shadow over a 40% black overlay.

## Shapes
4px for small controls, 8px for buttons and inputs, 12px for cards and dialogs, full for avatars.

## Components
Buttons come in primary, secondary, and danger. One primary button per view.

## Do's and Don'ts
- Do use tokens; don't write hex values in components.
- Don't use danger for anything that isn't destructive or overdue.
