---
type: skill
lifecycle: stable
inheritance: inheritable
name: microsoft-standards
description: Practical guidance for applying Microsoft's security (SDL), privacy, responsible AI, accessibility, and compliance standards during code generation, review, and planning. Use when writing code, reviewing changes, creating plans, or handling data.
tier: standard
applyTo: '**/*deployment*,**/*microsoft*,**/*standards*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Microsoft Standards Compliance

This skill provides **actionable patterns** for applying Microsoft's standards during everyday development work. It transforms principles into concrete checks that agents can apply during code generation, review, and planning.

## When This Skill Applies

- Writing or reviewing code that handles user data, credentials, or external input
- Creating plans or designs for new features
- Generating tests, configs, or infrastructure code
- Working with AI-generated content that will be user-facing
- Reviewing PRs or analyzing code quality

## 1. Security (SDL)

### During Code Generation

**Credential handling:**
- NEVER hardcode secrets, connection strings, passwords, or tokens
- Use placeholders: `<YOUR_CONNECTION_STRING>`, `${SECRET_NAME}`, or key vault references
- Pattern: `var secret = configuration["KeyVault:SecretName"];` not `var secret = "abc123";`
- Flag any existing hardcoded secrets found during analysis

**Azure resource identifiers in documentation:**
- NEVER commit real subscription IDs, tenant IDs, client/app IDs, MI names, Key Vault FQDNs, or resource group names in documentation — these aid reconnaissance even though they are not secrets
- Use placeholders: `<subscription-id>`, `<tenant-id>`, `<client-id>`, `<mi-name>`, `<resource-group>`
- If a doc needs real values for operational reference, move them to an access-controlled location and link to it
- This applies to markdown docs, feature plans, onboarding guides, and any checked-in text — not just code

**Input validation:**
- Validate and sanitize all external inputs (HTTP parameters, file contents, user input)
- Use parameterized queries — never concatenate SQL strings
- Pattern: `command.Parameters.AddWithValue("@id", userId);` not `$"SELECT * FROM users WHERE id = '{userId}'"`
- Validate file paths to prevent directory traversal: reject `..` in path components

**Dependency trust:**
- When suggesting NuGet/npm packages, prefer well-known Microsoft or community-verified packages
- Flag unfamiliar or low-download-count packages for human review
- Check that suggested package versions don't have known CVEs when possible

**Attack surface:**
- When adding new endpoints, consider: authentication required? authorization checked? rate limiting?
- When adding file operations, consider: path traversal? symlink attacks? race conditions?
- When generating logging code: ensure secrets, tokens, and PII are NOT logged

### During Code Review

Ask these questions about the change:
1. Does this introduce a new externally-reachable endpoint?
2. Are there new credential references? How are they stored?
3. Is user input flowing to database queries, file paths, or command execution?
4. Are error messages revealing internal implementation details?
5. Are new dependencies from trusted sources?
6. Does documentation contain real Azure resource identifiers (subscription IDs, client IDs, Key Vault FQDNs) that should be placeholders?

### During Documentation Generation

**Self-review checklist for AI-generated docs:**
- **Sensitive data** — Scan for GUIDs, subscription IDs, tenant IDs, client IDs, Key Vault FQDNs, and MI names. Replace with `<placeholder>` format
- **Markdown rendering** — Ensure blank lines before headings (especially after tables), proper fence closing, and consistent list formatting
- **Internal consistency** — If the same concept is described in multiple places within a doc, verify all descriptions match (e.g., issuer URLs, subject formats, token audiences)
- **Reference accuracy** — Verify tool/repo/service names match their actual names (e.g., don't write `mcp_docs-repo-mai` when the name is `docs-repo-main`)
- **Code sample correctness** — Ensure code examples implement the pattern described in the surrounding prose, not a conflicting pattern

## 2. Privacy

### During Code Generation

**Data minimization:**
- Collect only the data needed for the specific operation
- Don't add fields "just in case" — every data point has a privacy cost
- Pattern: Log operation results, not the full request payload with user data

**PII in logs and telemetry:**
- NEVER log: email addresses, IP addresses, usernames, auth tokens, request bodies with personal data
- DO log: operation names, status codes, durations, anonymized identifiers
- Pattern: `logger.LogInformation("User action completed. Duration: {Duration}ms", elapsed);`
- NOT: `logger.LogInformation("User {Email} performed {Action} from {IP}", email, action, ip);`

**Data handling patterns:**
```csharp
// GOOD: Anonymize before logging
var anonymizedId = HashUtility.ComputeHash(userId);
logger.LogInformation("Operation completed for user {AnonymizedId}", anonymizedId);

// BAD: Raw PII in logs
logger.LogInformation("Operation completed for user {UserId} ({Email})", userId, email);
```

**Consent and retention:**
- When generating code that stores user data, add comments noting retention policy requirements
- Flag any new data collection for privacy review: `// TODO: Privacy review — new user data collection`

### During Code Review

Ask these questions:
1. Does this change collect, store, or process personal data?
2. Is PII appearing in logs, telemetry, or error messages?
3. Are data retention policies considered?
4. Is there a consent mechanism if new data is being collected?

## 3. Responsible AI

### During Code Generation

**Human review of AI outputs:**
- AI-generated content meant for users must go through human review
- Add review gates: `// AI-generated — requires human review before publishing`
- Don't auto-publish AI-generated recommendations, diagnoses, or decisions

**Transparency:**
- When generating AI-facing code, make the AI's role clear to end users
- Pattern: Include disclaimers like "This suggestion was generated by AI and should be reviewed"
- Don't present AI outputs as definitive human-authored conclusions

**Bias and fairness:**
- When generating prompts or AI instructions, avoid assumptions about users
- Use inclusive language and examples
- Don't hardcode cultural, demographic, or geographic assumptions
- **NEVER use exclusionary terms** — "whitelist/blacklist", "master/slave", "sanity check", "grandfathered", "man-hours" — in any generated content (code, comments, docs, commit messages, variable names). Use inclusive alternatives: allowlist/blocklist, primary/replica, smoke test, legacy, person-hours. When editing existing files that contain these terms, replace them in the same edit. See Inclusive Language Guide for the full banned-terms table.
- **NEVER use competitive or adversarial framing** — "first-mover advantage", "competitive positioning", "out-innovate", "beat [team X]", "protect our work" — in any generated content. Use collaborative alternatives: "early adoption", "iteration speed", "share broadly", "lift the org". When extracting content from meetings where speakers used competitive language, reframe to collaborative alternatives while preserving intent. See Inclusive Language Guide — Collaborative Framing.

**Content safety:**
- When generating AI prompts, include safety boundaries
- Pattern: Include content filtering or guardrails for user-facing AI features
- Flag any AI feature that could generate harmful content without moderation

### During Code Review

Ask these questions:
1. Does this AI feature have human oversight before impacting users?
2. Is the AI's role transparent?
3. Could the AI output be harmful, biased, or misleading?
4. Are there content safety guardrails?

## 4. Accessibility

### During Code Generation

**Documentation and markdown:**
- Use proper heading hierarchy (H1 → H2 → H3, no skipping levels)
- Include alt text for images: `![Description of what the image shows](image.png)`
- Don't rely solely on color to convey information — add text labels
- Use descriptive link text, not "click here"

**UI code (when applicable):**
- Include ARIA labels on interactive elements
- Ensure keyboard navigation works
- Maintain sufficient color contrast (4.5:1 minimum for text)
- Pattern: `<button aria-label="Close dialog">X</button>`

**Tables and structured data:**
- Include header rows in markdown tables
- Use clear, descriptive column headers
- Don't use tables for layout — only for tabular data

### During Code Review

Ask these questions:
1. Do documents have proper heading hierarchy?
2. Do images have alt text?
3. Is information conveyed by means other than color alone?
4. Are interactive elements keyboard-accessible?

## 5. Compliance & Regulatory

### During Code Generation

**Regulated data awareness:**
- When working with healthcare, financial, or government data, flag for compliance review
- Add comments: `// Compliance: This handles [HIPAA/GDPR/FedRAMP]-regulated data`
- Don't make assumptions about compliance requirements — ask the user

**Audit trail:**
- For sensitive operations, ensure audit logging exists
- Pattern: Log who did what, when, and from where (without PII overexposure)
- Immutable audit logs preferred for compliance-critical operations

**Data residency:**
- When generating infrastructure code, note data residency requirements
- Flag cross-region data transfers for review

### During Code Review

Ask these questions:
1. Does this work touch regulated data (health, financial, government)?
2. Is there an audit trail for sensitive operations?
3. Are data residency requirements met?
4. Should this change go through a compliance review?

## Quick Reference: Code Generation Checklist

Before generating or suggesting code, mentally run through:

| Standard | Quick Check |
|----------|-------------|
| **Security** | No hardcoded secrets? Inputs validated? Dependencies trusted? |
| **Privacy** | No PII in logs? Data minimized? Consent considered? |
| **RAI** | Human review for AI outputs? Transparent? Unbiased? |
| **Accessibility** | Proper headings? Alt text? Not color-dependent? |
| **Compliance** | Regulated data flagged? Audit trail exists? |

## Escalation

When you identify a potential standards concern:
1. **Flag it immediately** — don't defer to later
2. **Be specific** — name the standard and the concern
3. **Suggest mitigation** — propose a fix or safer alternative
4. **Defer to human judgment** — for ambiguous cases, ask the user

Pattern:
> ⚠️ **Security concern:** This code concatenates user input into a SQL query, which is vulnerable to SQL injection. Recommend using parameterized queries instead. See [SDL guidance](https://www.microsoft.com/en-us/securityengineering/sdl).

## Related Resources

- Planning Guidelines — Microsoft Standards Compliance
- Security Considerations
- [Microsoft SDL](https://www.microsoft.com/en-us/securityengineering/sdl)
- [Microsoft Responsible AI](https://www.microsoft.com/en-us/ai/responsible-ai)
- [WCAG Guidelines](https://www.w3.org/WAI/standards-guidelines/wcag/)
