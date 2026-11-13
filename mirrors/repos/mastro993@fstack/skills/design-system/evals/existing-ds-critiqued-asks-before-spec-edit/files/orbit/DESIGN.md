---
version: alpha
name: Orbit
colors:
  primary: "#6D28D9"
  on-primary: "#FFFFFF"
  surface: "#FFFFFF"
  on-surface: "#1F1B2E"
  border: "#E4E1EC"
  danger: "#B42318"
typography:
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.5
  label-md:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: 500
    lineHeight: 1.3
rounded:
  sm: 4px
  md: 6px
spacing:
  xs: 4px
  sm: 8px
  md: 12px
  lg: 16px
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.label-md}"
    rounded: "{rounded.md}"
    padding: 8px 12px
---

## Overview
Orbit is a team analytics tool. Calm, compact, and precise.

## Colors
Violet primary for the one main action per screen. Danger only for destructive actions.

## Typography
Inter throughout; 14px body, 13px labels.

## Shapes
Small radii (4px and 6px) keep the UI crisp.
