---
title: Javadoc contracts
applicability:
- When Javadoc comments are among what the work produces or assesses
x-claim-provenance:
- claim: The first sentence of the main description is a summary sentence, @param documents type parameters written in angle brackets, {@linkplain} differs from {@link} only in showing its label in plain text, {@code} is equivalent to {@literal} in code font, @since names the release since which the feature has existed, and @deprecated is used together with the @Deprecated annotation.
  source: https://docs.oracle.com/en/java/javase/21/docs/specs/javadoc/doc-comment-spec.html
  scope: JDK 21 documentation comment specification.
---

Configured Javadoc indexes consume the opening summary sentence as the compact description of an element. `@param` covers value and type parameters, `@return` covers non-void results, and separate `@throws` entries preserve distinct documented failure conditions; the prose attached to those tags adds behavior that declared types alone do not communicate. For futures and stages, an immediate throw and exceptional completion are observably different failure timings.

`{@link}` and `{@linkplain}` address program elements, `{@code}` carries inline literals, and `{@literal}` protects escape-sensitive text. Package and module context has dedicated homes in `package-info.java` and `module-info.java`. Where the project uses them, `@apiNote`, `@implSpec`, and `@implNote` separate caller-facing specification from API and implementation notes.

An established `@Deprecated` declaration and `@deprecated` prose are complementary signals, and the annotation belongs to the compiled declaration rather than to its documentation. `@since` denotes the version in which an element actually shipped rather than the version in which documentation was edited. When the owning task requires generated-documentation verification, the project's Javadoc task and configured doclint policy are the relevant evidence surfaces.
