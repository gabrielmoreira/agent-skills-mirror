#!/usr/bin/env python3
"""Mechanically validate a migrated Lightning Out 2.0 host page.

The six non-negotiable LO 2.0 rules (Workflow B, Step B4) plus the core
library/component checklist items are all *deterministic code-structure*
checks. This script runs them against a migrated HTML host page so the
workflow gates on a repeatable pass/fail instead of prose interpretation.

Usage:
  python3 scripts/validate-lo20-page.py <path-to-migrated.html>

Prints one PASS/FAIL line per rule. Exits 0 only when every rule passes;
exits 1 if any rule fails, 2 on a usage/IO error.
"""
import re
import sys


def check(src: str):
    """Return a list of (ok: bool, label: str, detail: str)."""
    results = []

    def add(ok, label, detail=""):
        results.append((ok, label, detail))

    # --- Library / Beta removal -------------------------------------------
    # Locate the versioned library path, then scan back to the opening
    # <script to check for `async`. We do NOT isolate the tag with [^>]*
    # because placeholder URLs like https://<DOMAIN>.my.salesforce.com
    # legitimately contain a '>' inside the attribute value.
    lib_path = "lightning.out.latest/index.iife.prod.js"
    idx = src.find(lib_path)
    has_lo2_lib = idx != -1
    lib_async = False
    if has_lo2_lib:
        start = src.rfind("<script", 0, idx)
        if start != -1:
            lib_async = bool(re.search(r"\basync\b", src[start:idx]))
    add(has_lo2_lib and lib_async, "LO 2.0 library script tag",
        "must load .../lightning.out.latest/index.iife.prod.js with `async`")

    beta_lib = bool(re.search(r"lightning\.force\.com/[^\"']*lightning\.out\.js", src))
    beta_calls = bool(re.search(r"\$Lightning\.(use|createComponent)", src))
    add(not beta_lib and not beta_calls, "No Lightning Out Beta remnants",
        "no lightning.out.js / $Lightning.use / $Lightning.createComponent")

    # --- Rule 1: customElements.whenDefined must use a literal string ------
    wd = re.findall(r"customElements\.whenDefined\(\s*([^)]*?)\s*\)", src)
    if not wd:
        add(False, "Rule 1: whenDefined literal string",
            "no customElements.whenDefined(...) call found")
    else:
        # Require the ENTIRE trimmed argument to be a single quoted string
        # literal. A prefix-only check (starts with a quote) would let
        # expressions like `'c-' + componentTag` slip through.
        all_literal = all(
            re.fullmatch(r"""(['"]).*?\1""", arg.strip()) for arg in wd)
        add(all_literal, "Rule 1: whenDefined literal string",
            "argument must be a quoted string, not the `components` variable")

    # --- Rule 2: mountLo20 declared with two parameters -------------------
    decl = re.search(r"function\s+mountLo20\s*\(([^)]*)\)", src)
    if not decl:
        add(False, "Rule 2: mountLo20(frontdoorUrl, orgUrl)",
            "no `function mountLo20(...)` declaration found")
    else:
        params = [p for p in decl.group(1).split(",") if p.strip()]
        add(len(params) == 2, "Rule 2: mountLo20(frontdoorUrl, orgUrl)",
            f"declaration has {len(params)} parameter(s), expected 2")

    # --- Rule 3: clearCachedResult present (called before mounting) -------
    add(bool(re.search(r"clearCachedResult\s*\(", src)),
        "Rule 3: clearCachedResult() before mount",
        "clearCachedResult() must run before every mountLo20() call")

    # --- Rule 4: every mountLo20 call passes two arguments ----------------
    calls = re.findall(r"(?<!function\s)\bmountLo20\s*\(([^)]*)\)", src)
    # Count args for EVERY call site (the declaration is excluded by the
    # lookbehind). Do NOT skip empty argument lists: a zero-arg
    # `mountLo20()` has an arg count of 0, which is != 2 and must fail.
    bad_calls = [c for c in calls
                 if len([a for a in c.split(",") if a.strip()]) != 2]
    add(len(bad_calls) == 0, "Rule 4: mountLo20 calls pass two args",
        f"{len(bad_calls)} call(s) do not pass exactly two arguments")

    # --- Rule 5: boot() wrapper defined and invoked -----------------------
    boot_def = bool(re.search(r"function\s+boot\s*\(", src))
    boot_call = bool(re.search(r"(?<!function\s)\bboot\s*\(\s*\)", src))
    add(boot_def and boot_call, "Rule 5: boot() wrapper",
        "define function boot() and call boot() once at the end")

    # --- Rule 6: component tag has no inline display style ----------------
    comp_tags = re.findall(r"<c-[a-z0-9-]+[^>]*>", src)
    add(len(comp_tags) > 0, "Component tag present",
        "expected a <c-...> custom element in the HTML")
    inline_hidden = any(re.search(r"style\s*=\s*['\"][^'\"]*display\s*:\s*none",
                                  t) for t in comp_tags)
    add(not inline_hidden, "Rule 6: no inline display:none on component tag",
        "control visibility via the loading indicator, not the component tag")

    return results


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if len(argv) != 1:
        print("usage: validate-lo20-page.py <path-to-migrated.html>",
              file=sys.stderr)
        return 2
    try:
        with open(argv[0], "r", encoding="utf-8") as fh:
            src = fh.read()
    except OSError as e:
        print(f"error: cannot read {argv[0]}: {e}", file=sys.stderr)
        return 2

    results = check(src)
    failed = 0
    for ok, label, detail in results:
        mark = "PASS" if ok else "FAIL"
        line = f"[{mark}] {label}"
        if not ok and detail:
            line += f" -- {detail}"
        print(line)
        if not ok:
            failed += 1

    print(f"\n{len(results) - failed}/{len(results)} checks passed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
