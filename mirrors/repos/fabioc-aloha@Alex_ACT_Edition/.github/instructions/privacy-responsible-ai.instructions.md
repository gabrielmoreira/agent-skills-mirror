---
type: instruction
lifecycle: stable
inheritance: inheritable
description: "Privacy by design, data protection, and responsible AI principles"
application: "When handling PII, designing AI systems, or ensuring ethical AI use"
applyTo: "**/*privacy*,**/*pii*,**/*responsible*ai*,**/*ethic*"
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Privacy & Responsible AI

## Privacy by Design

1. **Minimize**: Collect only what's needed
2. **Purpose limit**: Use data only for stated purpose
3. **Anonymize**: Remove identifiers when possible
4. **Encrypt**: Protect at rest and in transit
5. **Expire**: Delete when no longer needed

## PII Handling

| Data Type | Classification | Handling |
|-----------|----------------|----------|
| Name + contact | Personal | Standard protection |
| SSN, health | Sensitive | Encryption, access control |
| Anonymized | Not PII | Verify truly anonymous |

## Responsible AI

- **Fairness**: Check for bias in training data and outputs
- **Transparency**: Explain AI decisions when impactful
- **Human oversight**: Escalation path for AI errors
- **Safety**: Content filtering, rate limits

## Anti-Patterns

- Collecting "just in case"
- Logging PII in plaintext
- No data retention policy
- AI decisions without appeal
