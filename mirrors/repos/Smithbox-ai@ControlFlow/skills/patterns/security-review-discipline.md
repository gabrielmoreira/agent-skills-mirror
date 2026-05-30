# Security Review Discipline

This skill codifies the discipline for flagging security issues during code review.
Provenance: adapted from prior art on security-review gating; no local source in this repo.

## Threshold

- **>80% confidence threshold** is REQUIRED for flagging an issue as a vulnerability.

## Explicit Exclusion List

Do NOT flag the following categories (they are excluded from this review mode):

- DOS vulnerabilities
- secrets-on-disk
- rate-limiting
- theoretical issues without an exploitation path
- style issues

## Trigger

The CodeReviewer must load this skill when the delegation payload sets `review_mode: "security"`.
