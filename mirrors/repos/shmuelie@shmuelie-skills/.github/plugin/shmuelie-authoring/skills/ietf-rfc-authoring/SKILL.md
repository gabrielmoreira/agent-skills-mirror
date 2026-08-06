---
name: ietf-rfc-authoring
description: "Write documentation in the IETF RFC style/format (for internal specs and protocol documents), using kramdown-rfc (Markdown to RFC XML v3). Use when asked to write a spec in IETF/RFC style, format a document like an RFC, produce an RFC-style protocol or format specification, apply RFC 2119 (BCP 14) keywords, or render Markdown to RFC-looking text/HTML with kramdown-rfc / kdrfc / xml2rfc. This is about producing RFC-STYLE documents, NOT submitting Internet-Drafts to the IETF."
---

# Writing IETF RFC-Style Documents

Produce documents that **look and read like an RFC** — the recognizable structure, keyword
conventions, grammar notation, and text/HTML rendering — for internal or personal
specifications. This is about **style and format**, not IETF submission: there is no
datatracker, no `idnits`, no draft expiry, no working-group process, no RFC Editor queue here.
A document authored this way *looks* like an RFC; it has no standing as one.

Primary toolchain: **kramdown-rfc** (Markdown → RFC XML v3) + **xml2rfc** (XML → txt/html).

## What "RFC style" is

The identifying features you are reproducing:

- **BCP 14 key words** (MUST / SHOULD / MAY …) in UPPER CASE for normative statements.
- Numbered sections with a conventional order (Abstract, Introduction, Conventions,
  body, Security Considerations, References).
- **Normative vs Informative** reference split.
- **ABNF** (RFC 5234) for any formal grammar/syntax.
- Monospaced, ~72-column plain-text rendering (plus an HTML rendering).

You pick your own document title and name. The IETF `draft-<name>-<topic>-NN` filename is
optional flavor — use it if you want the authentic look, but nothing requires it.

## Authoring with kramdown-rfc

A document is a single Markdown file with a **YAML metadata header** followed by sectioned
Markdown (`abstract`, `middle`, `back`, plus `normative`/`informative` reference blocks).
kramdown-rfc defaults to **RFC XML v3** (since 1.6.1).

### Metadata header (enough to render)

```yaml
---
title: My Protocol
abbrev: MyProto
docname: spec-myprotocol-01          # any name you like; -NN is just style
category: std                        # std | info | exp | bcp (affects the header label)
ipr: trust200902                     # set it so xml2rfc doesn't warn (render-only concern)
area: General
workgroup: Internal Engineering      # free text; it's just a label in the header
keyword:
  - example
  - specification
stand_alone: yes
pi: [toc, sortrefs, symrefs]
author:
  - ins: S. Englard
    name: Shmueli Englard
    org: Microsoft
    email: author@example.com
normative:
  RFC2119:
  RFC8174:
informative:
  RFC1925:
--- abstract
One-paragraph summary of what this document specifies.

--- middle

# Introduction

... body sections ...

--- back

# Appendix
```

The `--- abstract`, `--- middle`, `--- back` lines are kramdown-rfc **section separators**
(not YAML). Everything after the header is normal Markdown.

### Body idioms

- **BCP 14 boilerplate** — put this at the top of a "Conventions" / "Requirements Language"
  section to emit the standard RFC 8174 paragraph and enable keyword tagging:

  ```markdown
  # Conventions and Definitions

  {::boilerplate bcp14-tagged}
  ```

  That directive renders the canonical text ("The key words MUST, MUST NOT, … are to be
  interpreted as described in BCP 14 {{RFC2119}} {{RFC8174}} when, and only when, they
  appear in all capitals, as shown here."). If you'd rather not use the directive, paste that
  paragraph literally.

- **References / citations** — cite inline; kramdown-rfc auto-builds the reference entry:
  - Normative: `{{!RFC2119}}`  ·  Informative: `{{?RFC1925}}`
  - After a first tagged cite (or a `normative:`/`informative:` header entry) just use
    `{{RFC2119}}`.
  - Rename an anchor: `{{!TCP=RFC0793}}`, then `{{TCP}}`.
  - Non-RFC sources: spell them out under `informative:` in the header (title/author/date/
    seriesinfo/target) — see the skeleton.
- **Cross-references** to your own sections: give a heading an anchor
  (`# Widgets {#widgets}`) and reference it with `(#widgets)` / `{{widgets}}`.
- **Code / ABNF** — fenced blocks with a language; use `abnf` for grammar:

  ```markdown
  ~~~ abnf
  greeting = "HELLO" SP token CRLF
  token    = 1*ALPHA
  ~~~
  ```

## Section structure (RFC-style)

Order your sections like a real RFC (this is the RFC 7322 house style, minus the
submission-only chrome):

1. **Abstract** — what the document specifies, in one short paragraph (the `abstract` section).
2. **Introduction** — problem, scope, context.
3. **Conventions and Definitions** — the `{::boilerplate bcp14-tagged}` block + terminology.
4. **Body** — the actual protocol / format / behavior, in numbered sections; use MUST/SHOULD
   deliberately; include ABNF and figures/tables as needed.
5. **Security Considerations** — expected in RFC style; always include a real one.
6. **IANA Considerations** — *optional for a style doc.* Only include if your document defines
   registries/code points; otherwise omit (or, if you want the authentic look, add a section
   saying "This document has no IANA actions.").
7. **References** — split **Normative** and **Informative** (kramdown-rfc emits both from your
   citations/headers).
8. **Appendices / Acknowledgements / Authors' Addresses** — the `back` section; Authors'
   Addresses is generated from the `author` metadata.

kramdown-rfc + xml2rfc auto-add the "Status of This Memo" and Copyright chrome. For a
style-only document that text is meaningless boilerplate — it's harmless (and adds to the
authentic look), so just leave it; don't hand-edit it.

## Tooling (render only)

```sh
# Install (Ruby >= 2.3; the gem pulls in kramdown etc.)
gem install kramdown-rfc          # provides `kramdown-rfc` and `kdrfc`
pip install xml2rfc               # the XML -> txt/html renderer

# One-shot: Markdown -> XML -> txt/html
kdrfc spec-myprotocol.md          # writes .xml and .txt
kdrfc -h spec-myprotocol.md       # also emit .html
kdrfc -r spec-myprotocol.md       # use a REMOTE xml2rfc (no local xml2rfc install)

# Two-step (equivalent), handy for inspecting the XML:
kramdown-rfc spec-myprotocol.md > spec-myprotocol.xml
xml2rfc spec-myprotocol.xml --text --html
```

Read the **xml2rfc warnings** to clean up the render (undefined references, empty/unbalanced
sections, missing `category`/`ipr`). That's the only validation in scope — `idnits` and the
datatracker submission checks are for actually submitting to the IETF and are **not** used here.

## Skeleton template

A complete, self-contained kramdown-rfc document that renders with `kdrfc`:

```markdown
---
title: The Example Widget Protocol
abbrev: Widget
docname: spec-widget-00
category: info
ipr: trust200902
area: General
workgroup: Internal Engineering
keyword: [widget, example]
stand_alone: yes
pi: [toc, sortrefs, symrefs]
author:
  - ins: S. Englard
    name: Shmueli Englard
    org: Microsoft
    email: author@example.com
normative:
  RFC2119:
  RFC8174:
  RFC5234:
informative:
  RFC1925:
--- abstract

This document specifies the Example Widget Protocol, a trivial request/response
exchange used to demonstrate IETF RFC-style authoring.

--- middle

# Introduction

The Widget Protocol lets a client request a widget from a server.  This document
defines its message format and behavior.

# Conventions and Definitions

{::boilerplate bcp14-tagged}

Widget:
: The unit of data exchanged by this protocol.

# Message Format

A request MUST be a single line terminated by CRLF, using the following grammar:

~~~ abnf
request = "GET" SP widget-id CRLF
widget-id = 1*DIGIT
~~~

A server MUST respond with the widget, and SHOULD do so within one second.  A
client MAY retry a request that times out.

# Security Considerations

This protocol provides no confidentiality or integrity and MUST NOT be used over
untrusted networks without a secure transport such as TLS.

--- back

# Acknowledgements

Thanks to the reader for reviewing this example.
```

Render it: `kdrfc -h spec-widget-00.md` → `spec-widget-00.txt` + `.html` in RFC style.

## Gotchas

- **Keywords only in UPPER CASE and only where normative.** Lowercase "must" is prose, not a
  requirement (that's the whole point of RFC 8174).
- **Set `category` and `ipr`** or xml2rfc warns — purely so it renders cleanly; neither implies
  any real status for a style-only doc.
- **The auto "Status of This Memo"/Copyright is IETF chrome** — don't hand-edit it; it's
  meaningless for an internal doc but makes the output look authentic.
- **ABNF must be RFC 5234-correct**, otherwise it just renders as an ordinary code block with
  no checking.
- **Split references** into Normative (needed to implement) vs Informative (background). Tag
  cites with `!` vs `?` and kramdown-rfc sorts them into the right section.
- **Looks like ≠ is an RFC.** This produces RFC-*style* documents only; they carry no IETF
  standing, number, or registration.
