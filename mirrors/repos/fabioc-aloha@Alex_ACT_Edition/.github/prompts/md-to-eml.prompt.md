---
description: "Convert a Markdown document to a RFC 5322-compliant .eml file — newsletter, governance announcement, release email"
mode: agent
lastReviewed: 2026-05-01
---

# Markdown → Email (.eml)

Convert markdown to a sendable .eml file with proper email headers, inline CSS, and table-based layout. Designed for newsletters, governance communication, and release announcements.

Skill: [md-to-eml](../skills/md-to-eml/SKILL.md). Instruction: [md-to-eml.instructions.md](../instructions/md-to-eml.instructions.md). Muscle: `.github/muscles/md-to-eml.cjs`.

## When to Use

- Drafting a release announcement to ship as an email
- Converting a markdown changelog into a customer-facing newsletter
- Producing governance / compliance communication that must be email-archivable
- Any time the output needs to render correctly across Outlook, Gmail, Apple Mail, and webmail clients

## Required frontmatter

The source markdown must have YAML frontmatter that maps to RFC 5322 headers:

```yaml
---
to: recipient@example.com
from: sender@example.com
subject: "Release announcement — Edition v0.9.2"
cc: optional@example.com
date: 2026-05-01
---

# Body starts here
```

The muscle reads `to`, `from`, `subject`, `cc`, `bcc`, `reply-to`, and `date`. Missing `subject` will fail.

## Steps

1. **Confirm source and target.** Source `.md` path, output `.eml` path. If output omitted, default to source basename with `.eml`.
2. **Verify frontmatter** has at least `to`, `from`, `subject`. The muscle will reject the file otherwise.
3. **Optional flags**:
   - `--no-replace-em-dashes` — keep `—` in prose (default: replaced with `, `)
   - `--no-strip-decorative-rules` — keep decorative `---` thematic breaks (default: stripped)
   - `--inline-styles` — bake CSS into every tag (default: ON for email; turning off may break older clients)
4. **Run**:

   ```sh
   node .github/muscles/md-to-eml.cjs announce.md --output dist/announce.eml
   ```

5. **Verify** by opening the `.eml` in your mail client (Outlook: drag into preview pane; Apple Mail: open file). Check:
   - Subject renders correctly
   - Tables align in narrow viewports
   - Hyperlinks are clickable, not raw text
   - Mermaid diagrams (if any) appear as inline PNG, not broken SVG references
   - Em-dashes have been replaced (or preserved if `--no-replace-em-dashes` was used)

6. **Send** by attaching to a draft, dragging into a Send queue, or using your mail client's "Open .eml file" workflow.

## Boundaries

- **Email clients vary.** RFC 5322 + table-based layout is the lowest common denominator; if a specific client misrenders, the fix may be in your CSS not the muscle.
- **Mermaid → PNG is mandatory for email.** SVG references break in most mail clients. The muscle handles this automatically; don't try to inline SVG.
- **No `[toc]` support.** Email is a flat read; tables of contents don't add value and break in narrow viewports.
- **Image attachments not handled.** The muscle inlines images via base64 data URIs (works in most clients, may inflate size). For very large images, host externally and use absolute URLs.
- **Don't ship unencrypted PII.** The muscle doesn't add S/MIME or PGP. If the email needs encryption, run a separate signing pass.
