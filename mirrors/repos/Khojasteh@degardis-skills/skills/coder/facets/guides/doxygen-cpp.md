---
title: Doxygen contracts for C++
applicability:
- When Doxygen documentation is among what the work produces or assesses
x-claim-provenance:
- claim: Doxygen commands start with a backslash or an at-sign, param takes an optional in, out, or in,out direction attribute, tparam documents template parameters, retval documents a named return value, def documents a define macro, and file documents a source or header file.
  source: https://www.doxygen.nl/manual/commands.html
- claim: JAVADOC_AUTOBRIEF and QT_AUTOBRIEF, both NO by default, make Doxygen treat the first line of a Javadoc-style or Qt-style comment, up to the first dot, question mark, or exclamation mark, as the brief description.
  source: https://www.doxygen.nl/manual/config.html
---

The project's Doxyfile and nearby public headers determine the accepted comment form, `\` or `@` command prefix, brief-description behavior, and enabled Doxygen features. A consumer-facing C++ contract normally belongs with the header a consumer includes, while implementation-only notes may remain in source; when both locations describe the same behavior, they form one semantic agreement rather than two independent contracts.

C++ documentation can carry contract information that the type system does not fully express: pointer, reference, and handle ownership or lifetime; allocation and release responsibility; nullability and validity duration; undefined-behavior preconditions; thread, reentrancy, and signal safety; alignment or buffer requirements; exception-safety guarantees; and the observable promise associated with `noexcept`.

The configured forms of `\param[in]`, `\param[out]`, `\param[in,out]`, `\tparam`, and `\retval` encode parameter direction, template parameters, and meaningful return-code distinctions. Failure state and surviving effects remain part of the prose attached to those entries. `\def` and `\file` provide documentation ownership for macros or free declarations that would otherwise lack a natural generated page. When the owning task requires rendered or structural verification, the project's configured Doxygen build is the relevant evidence surface.
