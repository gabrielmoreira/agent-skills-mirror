---
version: alpha
name: Product Story
description: An original editorial identity for short evidence-led stories.
colors:
  primary: "#20332E"
  neutral: "#FAF8F0"
  tertiary: "#B14C2E"
typography:
  h1:
    fontFamily: sans-serif
    fontSize: 64px
    fontWeight: 600
    lineHeight: 1.1
  body:
    fontFamily: sans-serif
    fontSize: 28px
    fontWeight: 400
    lineHeight: 1.4
spacing:
  sm: 16px
  md: 32px
  safe: 80px
rounded:
  sm: 8px
components:
  proof-card:
    backgroundColor: "{colors.neutral}"
    textColor: "{colors.primary}"
    typography: "{typography.body}"
    rounded: "{rounded.sm}"
    padding: "{spacing.md}"
---

# Product Story visual identity

## Overview

Warm editorial clarity, a single focal point and visible supporting evidence. This is an original fictional identity for demonstrating package composition, not a real customer's brand guide.

## Colors

Use primary for text, neutral for the canvas and tertiary for the single emphasis mark. Keep actual product imagery faithful to supplied material. Motion rules refer to these semantic names rather than maintaining another palette.

## Typography

Use h1 for one short headline and body for the proof and closing line. The generic family is intentional for this recipe; its appearance varies by machine. A production fork must declare and supply its licensed font before claiming pixel-consistent output.

## Layout

The safe spacing role defines the margin on the sample landscape canvas. Keep one headline and one evidence panel. A portrait adaptation requires a new composition review, not proportional shrinking of every element.

## Elevation & Depth

Use spacing and scale to distinguish the headline from supporting evidence. No shadow or simulated depth is required.

## Shapes

Use the small rounded role for evidence cards. The optional emphasis element is recolorable with currentColor.

## Components

The proof-card role holds supplied evidence. It is an authored video element, not a change to an application's interface controls.

## Do's and Don'ts

- Keep the final action readable without animation.
- Preserve accurate evidence and the owner's approved copy.
- Do not add a second accent merely to decorate empty space.
- Do not treat the illustrative presets as real product or learning claims.
