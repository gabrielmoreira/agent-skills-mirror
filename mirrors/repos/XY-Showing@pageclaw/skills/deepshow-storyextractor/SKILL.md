---
name: deepshow-storyextractor
description: Extract a complete, independently readable pagestory.md from one source document, especially a PDF, while preserving its meaning, structure, relationships, and useful assets. Use when a document should be faithfully restored before DeepShow creation rather than editorially selected or developed.
---

# DeepShow StoryExtractor

Turn one source document into an independently readable, editable `pagestory.md`. This is a faithful restoration entry point: use the document as the sole content source, preserve its complete semantic content and intended uses, and do not perform StoryCreator-style selection or development.

Read the document as both rendered pages and extractable content. Use available document-reading, rendering, OCR, and asset-extraction tools as needed to recover material that text extraction misses, including diagrams, formulas, superscripts, footnotes, questions, answer options, tables, image text, and link destinations. Reconnect content split by columns, page breaks, or line breaks.

Write one coherent Markdown document in the source language unless the user requests translation. Let its headings and organization follow the source naturally. Use complete sentences and connected paragraphs where they carry the meaning; retain lists, tables, formulas, quotations, images, links, exercises, examples, and templates in forms that preserve their roles. Make relationships conveyed by placement, grouping, arrows, type treatment, or visual hierarchy explicit in prose, tables, or nearby image descriptions. Resolve references and omitted context only when the source makes them clear; state an important ambiguity rather than inventing an answer.

Preserve content because of what it does, not only because of its length. Keep facts, viewpoints, arguments, cases, explanatory and promotional copy, exercises, review material, resources, and useful detail. Repeated words may serve distinct purposes; keep them when the source uses them differently. Keep variables in reusable templates, the question/example/template identity of instructional material, and embedded link names, purposes, and destinations. Treat external link targets as referenced resources, not additional source material to expand.

Remove only extraction or layout noise: repeated running headers or footers, ordinary page numbers, empty pages, decorative rules, broken line wraps, and similar artifacts without semantic content. Do not condense the document for a presumed later page, discard material merely because it is secondary, or add facts not supported by the source.

Create `pagestory.md` at the user-specified output location and an adjacent `assets/` directory only for images, charts, or other source assets needed to retain meaning. Keep the source name and context identifiable in the result. Finish when a reader can understand every part's information, relationships, and use from the Markdown and its cited assets without relying on the source's visual layout.

For a correction, use the existing PageStory and its assets as the baseline. Apply accepted extraction findings while preserving unaffected content, structure, wording, and assets. The result can proceed directly to another DeepShow stage. In chat, provide the output path and only extraction limitations that affect interpretation; do not create a separate extraction report.
