---
title: Angular
category: Framework and library
x-claim-provenance:
- claim: Zoneless change detection is the default in Angular v21 and later; Angular relies on notifications from core APIs to decide when to run change detection — ChangeDetectorRef.markForCheck (called automatically by AsyncPipe), ComponentRef.setInput, updating a signal read in a template, bound host or template listener callbacks, and attaching a view marked dirty by one of these — and with zoneless enabled NgZone.onMicrotaskEmpty, onUnstable, and onStable never emit and NgZone.isStable is always true.
  source: https://angular.dev/guide/zoneless
  scope: Angular v21 and later; page read 2026-09 from the v22 documentation.
- claim: An update across multiple major versions is performed one major version at a time, and deprecated APIs are removed only in major releases.
  source: https://angular.dev/reference/releases
- claim: Basic template type-checking mode validates only top-level template expressions and does not check embedded views such as *ngIf and *ngFor; full mode (fullTemplateTypeCheck) checks embedded views and pipe return types; strict mode (strictTemplates) adds input binding assignability, strictNullChecks in templates, generic inference, and $event and DOM reference types.
  source: https://angular.dev/tools/cli/template-typecheck
- claim: Angular treats all values as untrusted by default and sanitizes and escapes them when a template binding or interpolation inserts them into the DOM; DomSanitizer bypassSecurityTrust methods mark a value as trusted, and direct DOM interaction through ElementRef lacks that automatic sanitization.
  source: https://angular.dev/best-practices/security
---

The configured Angular and toolchain versions decide what Angular code means. Standalone or module declarations, signal- or subscription-driven state, zone-based or zoneless change detection, and reactive or template-driven forms are version-dependent choices, and lifecycle and subscription helpers exist only in the versions that provide them. An upgrade across several major versions proceeds one major version at a time, deprecated APIs disappear only at major releases, and the framework, CLI, compiler, reactive dependencies, builder, test tooling, and third-party peer requirements form one compatibility surface for source changes.

Change detection shows how much the version decides. Zoneless change detection is the default from Angular v21, and under it Angular runs change detection when a core API notifies it: `markForCheck`, which `AsyncPipe` calls, `ComponentRef.setInput`, an update to a signal a template reads, or a bound template or host listener. Code that waits for `NgZone.onStable` or checks `NgZone.isStable` stops working there, because those observables never emit and `isStable` is always true, and a state change that no notification reports is not rendered until something else triggers a check. Provider scope, component ownership, routing ownership, and SSR or hydration boundaries are the other main ownership decisions, and each piece of state stays coherent only under one reactive model.

Template bindings and interpolation pass a value through Angular's sanitization on its way into the DOM, while a `DomSanitizer` `bypassSecurityTrust` method, `ElementRef`, or another direct DOM API skips that path, so where a value enters the DOM decides whether it was sanitized and untrusted template content remains a characteristic failure alongside stale emissions, nested or duplicate subscriptions, duplicate requests, direct DOM assumptions, and a router or provider whose ownership is wider than intended.

Control flow, lifecycle, and ownership run through component lifecycle, injection scopes, change detection, signals and observables, forms, guards, resolvers, interceptors, sanitization, server-versus-browser execution, and teardown. Code is also referenced indirectly, so structural changes can break:

- templates, selectors, and metadata
- DI tokens, routes, and lazy imports
- style encapsulation, custom elements, and generated declarations
- hybrid bootstrap or state bridges

The configured Angular compiler and template type checker report template diagnostics that plain TypeScript compilation does not, and only as far as the project's strictness reaches: basic mode checks top-level expressions but not embedded views such as `*ngIf` or `*ngFor`, and only `strictTemplates` checks input assignability and null safety in templates, so a clean template check speaks only for the configured mode. Behavioral evidence distinguishes rendered behavior and user interaction, and depends on controlling change detection, async stabilization, HTTP requests, routing, provider scope, and browser/server boundaries. Performance evidence comes from production builds measured with the project's Angular and browser profiling tools, and an optimization must preserve teardown, reactive semantics, stable list identity, bundle constraints, and hydration behavior.
