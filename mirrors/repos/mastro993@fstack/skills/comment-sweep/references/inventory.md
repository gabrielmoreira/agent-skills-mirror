# Inventory brief

The brief for whoever takes the inventory: you on a small sweep, a scout on a big one. For a scout, fill in the `<...>` fields and send the block as its whole prompt. Taking the inventory is reading and nothing else, so any subagent can do it, even one without a shell.

```
You list code comments exactly as they are. Listing is the whole job: the judging and the editing
happen elsewhere.

Repo: <repo root>
Files: <path of the batch's batch-N.files>
Diff: <path of the batch's batch-N.diff, or "none">

With a diff, the lines in scope are its `+` lines. With no diff, every line of every listed file
is in scope. Open the files themselves to read each comment whole, including the parts outside
the lines in scope.

A file can hold several comment syntaxes: HTML <!-- --> and the code in its <script> and <style>
tags, template comments ({# #}, {{!-- --}}, <%# %>), MDX {/* */}, the code cells of a Jupyter
notebook. List them all.

Print one line for every comment that touches a line in scope, in file order:

  path:line: kind: text

- line: the line the comment starts on. For a block comment, or consecutive line comments that
  read as one comment, give the range, as in `src/a.ts:12-15`. Neighbouring comments that say
  separate things get a line each.
- text: the comment's own words, exactly as written, without its markers, on one line. Past 120
  characters, cut it there and end with `…`.
- kind:
  directive  a tool reads it: lint or type suppressions (eslint-disable, @ts-expect-error,
             noqa, type: ignore, nolint, NOLINT, rubocop:, ktlint-disable, swiftlint:,
             prettier-ignore, ...), build tags and compiler pragmas (//go:build, //go:generate,
             #pragma, -*- coding -*-, a #! line, swift-tools-version), SAFETY: comments,
             coverage markers, licence, copyright and SPDX headers, @generated or DO NOT EDIT,
             Deprecated: or @deprecated, doctests (>>>), Rust doc examples, JSDoc types in
             JavaScript files (@type, @param {T}, @typedef), triple-slash references,
             sourceMappingURL. When unsure, say directive.
  doc        a docstring or doc comment on a declaration: a Python docstring, /** */, ///, //!,
             a Go comment directly above an exported name.
  comment    any other comment.

Text inside a string, template literal, or regex is code. A Python docstring is a comment, even
though it is a string.

End with one line: `files: <n read>, comments: <n>`.
```
