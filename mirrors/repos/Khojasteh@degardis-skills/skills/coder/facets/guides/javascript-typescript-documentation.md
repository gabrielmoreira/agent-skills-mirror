---
title: JavaScript and TypeScript API comments
applicability:
- When JSDoc or TSDoc comments are among what the work produces or assesses
x-claim-provenance:
- claim: JSDoc annotations supply types to JavaScript files checked with checkJs or a // @ts-check comment, JSDoc @param takes a type in braces before the name, and @typedef and @callback define object and function types.
  source: https://www.typescriptlang.org/docs/handbook/jsdoc-supported-types.html
- claim: The TSDoc @param tag is followed by a parameter name, a hyphen, and a description, without a type expression, because the TypeScript declaration supplies the type.
  source: https://tsdoc.org/pages/tags/param/
- claim: TSDoc's discretionary @beta release tag lets tooling trim a declaration from a public release, and API Extractor provides the reference implementation of that trimming.
  source: https://tsdoc.org/pages/tags/beta/
---

Project configuration determines whether comments are parsed as JSDoc or TSDoc, whether JavaScript comments participate in type checking, and whether documentation or declarations are published from them. Their syntaxes are not interchangeable: JavaScript JSDoc can own type expressions such as `@param {string} name - description`, while TypeScript declarations own the type and TSDoc represents the parameter as `@param name - description` without a type expression.

For JavaScript, configured `@typedef` and `@callback` forms can define reusable object and callback contracts, and the project's checked JSDoc syntax determines how optionality and nullability are represented. With `checkJs` or `// @ts-check`, comment types participate in program checking rather than serving as prose only. The configured generator also determines which visibility tags keep internal helpers out of published reference material.

For TypeScript, the exported declaration surface is the natural documentation boundary, and overloads can require distinct documentation when their consumer contracts differ. Release tags such as `@public`, `@beta`, `@alpha`, or `@internal` affect the published surface only when the configured tool assigns them that role. `{@link}` and `{@inheritDoc}` likewise depend on configured resolution and on the inherited contract remaining applicable unchanged.

For promise-returning APIs, `@returns` describes the resolved value, while synchronous throws and promise rejection are separate observable failure paths. `@deprecated` is meaningful when it identifies a replacement. When the owning task requires generated-documentation or API-surface verification, the project's JSDoc, TypeDoc, or API-report command is the relevant evidence surface.
