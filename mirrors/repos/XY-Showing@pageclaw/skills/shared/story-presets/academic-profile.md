# Academic Homepage PageStory Preset

Preset: `academic-profile`

This is the canonical authoring scaffold for an academic homepage PageStory. It is a reference template, not a parser schema or completeness checklist. The headings are prompts, not required fields. Sections may be added, renamed, merged, split, reordered, or omitted. Never invent content to complete the template.

## Applies When

Use this preset when the artifact is a researcher's academic homepage or profile. It may show identity, research, academic work, opportunities, and ways to explore or connect for several audiences at once.

## Showing Focus

Help the researcher show, when supported by available material:

- who they are and their current academic status and affiliation;
- their research themes, questions, methods, or agenda;
- representative academic work and other relevant evidence;
- their group, opportunities, or other current academic activity when relevant; and
- useful ways to explore their work or connect with them.

These are showing considerations, not required headings. Missing information should be omitted, marked as uncertain, or asked about; it must not be inferred merely to complete the picture.

## PageStory starter

For a new PageStory, lightweight metadata is recommended when it helps the Agent understand the task:

```markdown
---
title: "{Full Name}"
story_kind: profile
story_preset: academic-profile
audience:
  - "{Intended audiences}"
showing_focus: "{What the owner most wants this homepage to show}"
language: "{Language code}"
---

# Academic Page Story of {Full Name}
```

The metadata is optional. An existing PageStory without front matter remains valid.

## Flexible authoring scaffold

For a new PageStory, use the following order as a starting point and replace literal placeholders only with supported facts. Keep only sections that have useful content. If an open section would materially help the next interview or revision, retain its heading plus one concise HTML comment describing what may belong there; otherwise omit it. Do not use TODO for an ordinary optional section.

1. About
2. Contact and Links
3. Opportunities
4. News
5. Research
6. Publications
7. Preprints
8. Research Projects
9. Software and Datasets
10. Patents
11. Research Group
12. Advising and Mentoring
13. Academic Experience
14. Education
15. Awards and Honors
16. Grants and Fellowships
17. Talks and Presentations
18. Teaching
19. Professional Service
20. Media and Outreach

Do not append visible working sections such as `Sources and Uncertainties` merely to record tool failures or source reconciliation. Keep those notes in conversation or explicit HTML comments unless the information is genuinely intended for page readers. An `Assets` section is appropriate only when it carries assets PageCreator should use.

## Section boundaries

- **About** establishes the researcher's identity, current role, affiliation, background, and concise positioning when supported.
- **Contact and Links** contains contact channels and profile links the owner wants visitors to use.
- **Opportunities** covers current availability, recruiting, collaboration, advising, or job-market status. Do not infer availability from stale material.
- **News** contains dated updates. Preserve date granularity from the source; do not invent a day when only a month is known.
- **Research** covers themes, questions, methods, and long-term agenda.
- **Research Projects** covers concrete initiatives with defined goals, collaborators, or outputs.
- **Research Group** covers the current team.
- **Advising and Mentoring** covers supervision relationships, mentoring activities, and history.
- **Academic Experience** covers research and academic appointments that are not better expressed as Education.
- **Publications** covers formally accepted or published work.
- **Preprints** covers work not yet formally accepted.

For publication reconciliation, user confirmation, a shared stable identifier, an explicit version link, or a source declaration can establish a same-work relationship. Title, topic, or author overlap alone cannot. Publication status separately needs direct user or reliable-source support. Merge or move only when both relationship and status are established; otherwise ask.

## Publication expression

Use a natural Markdown block, for example:

```markdown
### Paper Title

Author One, **Page Owner**, Author Three

*Venue or status, Year.*

**In brief:** Optional plain-language summary supported by the abstract, paper, or equivalent user material.

[PDF](url) · [DOI](url) · [Code](url)
```

Only include facts and links that exist. `In brief` is optional, not a quality requirement for every paper; do not infer it from a title or citation alone. Publication resource links are optional too: prefer representative work and real resources, and never add a TODO merely because a paper lacks them. Keep publication status, authors, venue, and year exact.

## Authoring rules

- Use `<!-- TODO: ... -->` only for a necessary local field in an otherwise evidence-backed entry, and state what would resolve it.
- Use `<!-- CONFIRM: ... -->` for a concrete non-critical conflict and name the conflicting information.
- Use `<!-- Optional: ... -->` for an open editorial suggestion; do not turn it into TODO or CONFIRM.
- Preserve a user's existing structure, omissions, and wording unless the user asks to change them or what needs to be shown clearly requires a rewrite.
- Do not treat this scaffold as a parser schema.
- Do not create empty prose, placeholder facts, fake links, or speculative claims to make the PageStory look complete.
- Do not silently strengthen claims, merge identities, infer relationships, or upgrade publication status.
- Keep names, authorship, venue, year, role, status, and attribution faithful to user statements and available material.
- Use nearby footnotes or source IDs only when they improve clarity or help resolve a meaningful uncertainty; do not turn the PageStory into a provenance database.

## Academic editorial lens

Help the researcher show their identity, current status, research, academic work, and useful ways to explore further. When reliable source entry points support them, keep academic relationships and research outputs explorable when that improves what the page can show for its intended readers.

Mentor or collaborator links and paper or project resources are domain-taste examples, not required fields: do not require links for every person or resources for every work. Consider author emphasis, publication status and ordering, evaluation context, photos, News, and Opportunities without turning them into a retention checklist.

Do not demand a unifying research vision, an `In brief` for every paper, complete resources for every work, or non-empty optional sections.
