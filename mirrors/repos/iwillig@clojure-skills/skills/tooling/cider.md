---
name: cider_nrepl_middleware
description: Middleware for nREPL providing enhanced editor integration.
---

# CIDER nREPL

Middleware for nREPL that provides enhanced development features for Emacs and other editors.

## Overview

CIDER (Clojure Interactive Development Environment for Emacs Refined) provides nREPL middleware that adds advanced features like debugging, refactoring, and enhanced introspection.

## Core Concepts

**Middleware**: Extends nREPL capabilities.

```clojure
; In deps.edn :nrepl alias:
; :nrepl
; {:extra-deps {nrepl/nrepl {:mvn/version "1.3.0"}
;               cider/cider-nrepl {:mvn/version "0.56.0"}}
;  :main-opts ["-m" "nrepl.cmdline"
;              "--middleware" "[cider.nrepl/cider-middleware]"
;              "--port" "7889"]}
```

**Editor Integration**: Use from editor.

```clojure
; Emacs CIDER features enabled:
; - Jump to definition (M-.)
; - Find usages (M-?)
; - Code completion
; - Inline evaluation
; - Debugging (breakpoints)
; - Documentation
```

## Key Features

- Code navigation (jump to definition)
- Finding references
- Auto-completion
- Inline documentation
- Debugging with breakpoints
- Refactoring tools
- Test integration
- Error handling

## When to Use

- Emacs-based development
- Advanced editor features
- Debugging complex code
- Interactive development

## When NOT to Use

- Non-Emacs editors (use alternatives)

## Common Patterns

```clojure
; With CIDER running in Emacs:

; 1. Jump to definition: M-.
; (my.app/some-function)  ; Place cursor, press M-.

; 2. Find usages: M-?
; (defn my-func [x] ...)  ; M-? shows all calls to my-func

; 3. Code completion: M-TAB
; (str  ; Type str, M-TAB shows completions

; 4. Inline evaluation: C-x C-e
; (+ 1 2 3)  ; C-x C-e shows => 6

; 5. Debugging:
; #dbg
; (defn buggy-fn [x]
;   (+ x 1))  ; Can set breakpoints

; 6. Documentation: C-c C-d C-d
; (str)  ; Shows docstring for str
```

## Related Libraries

- nrepl/nrepl - nREPL server
- clojure-lsp/clojure-lsp - Language server protocol

## Resources

- CIDER Documentation: https://docs.cider.mx/
- Official Repository: https://github.com/clojure-emacs/cider-nrepl
- API Documentation: https://cljdoc.org/d/cider/cider-nrepl

## Notes

This project supports CIDER for Emacs-based development through nREPL.
