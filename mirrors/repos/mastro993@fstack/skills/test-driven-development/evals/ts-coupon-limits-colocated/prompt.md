---
tags: [test-driven-development]
max_turns: 80
timeout_seconds: 1500
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

in shopcart/ add two limits to coupons: an optional maxDiscountCents (the coupon's discount never goes above it) and an optional minSubtotalCents (the coupon only applies when the cart subtotal is at least that much). work test-first please

Input files: shopcart/
