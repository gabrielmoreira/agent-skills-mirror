---
title: TypeScript
category: Language
guides:
- javascript-typescript-documentation
x-claim-provenance:
- claim: Node.js type stripping, unflagged as experimental in Node.js 23.6, supports only erasable TypeScript syntax, not enum declarations, namespaces or modules with runtime code, parameter properties, or import = and export = assignments; TypeScript 5.8's --erasableSyntaxOnly flag errors on such constructs.
  source: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-8.html
- claim: useDefineForClassFields emits class fields with ECMAScript define semantics instead of assignment, and defaults to true when the target is ES2022 or higher, including ESNext.
  source: https://www.typescriptlang.org/tsconfig/useDefineForClassFields.html
- claim: Without exactOptionalPropertyTypes an optional property can be assigned undefined; with it, a property marked optional cannot be assigned undefined unless undefined is part of its declared type.
  source: https://www.typescriptlang.org/tsconfig/exactOptionalPropertyTypes.html
---

The effective compiler configuration, TypeScript version, strictness flags, module and resolution modes, target libraries, declaration settings, project references, and actual emit or type-stripping path define the project configuration, and syntax, type-system facilities, decorators, and module behavior exist only where the configured compiler and runtime or transformation path support them. The emit path decides what some source means. Node's type stripping runs only erasable syntax, so enums, namespaces with runtime code, parameter properties, and `import =` assignments need a compiler, and `useDefineForClassFields`, on by default from target ES2022, emits class fields with definition rather than assignment semantics, which changes what a field declaration does at run time.

Optional versus missing versus null, structural compatibility, variance, narrowing, promise and event ordering, runtime validation, serialization, cancellation, and declaration or emitted compatibility are behavioral contracts, and types do not validate untrusted runtime values. Even the difference between a missing property and one set to `undefined` depends on configuration, because an optional property accepts `undefined` unless `exactOptionalPropertyTypes` is on. Emitted behavior sits behind enums, class fields, decorators, imports, async lowering, assertions, generics, private fields, and erased types, and type-only declarations differ from value-bearing ones.

Code is also referenced indirectly, through:

- ambient declarations, module augmentation, and declaration merging
- runtime property names, dynamic imports, path aliases, and conditional exports
- generated declarations, schemas, serializers, and framework metadata
- unsafe casts

Declaration output, public overloads, type-only versus value exports, module-format interoperation, default exports, package resolution, and consumers that compile under different compatible settings are observable state.

Static checks and runtime tests are separate evidence, each run through the configured compiler, transformer, loader, resolver, and host; type-check success is not runtime proof, and a loader the project does not use does not represent the shipped path. Behavioral evidence covers parsed or deserialized boundaries, optional and nullable values, exhaustive unions, rejected promises, event ordering, cancellation, serialization, and each assertion that suppresses compiler evidence. Published-compatibility evidence includes emitted JavaScript and declarations and representative consumer compilation, and type-check or build cost is a separate measurement from emitted runtime or bundle cost.
