#!/usr/bin/env python3
"""Deterministic Lightning Out Beta -> LO 2.0 name/URL transforms.

The Beta -> LO 2.0 migration includes a few *purely mechanical* string
conversions that must be applied identically every time (Workflow B, Step B3):

  * Aura component id ``c:myComponent`` -> LWC custom-element tag ``c-my-component``
  * camelCase attribute names -> kebab-case HTML attribute names
  * the org My Domain -> the versioned LO 2.0 library ``<script>`` URL

This script performs those conversions so the workflow never has to hand-derive
them. It does NOT make any judgement calls (target DOM location, whether an LO
2.0 App id is needed, placeholder values) -- those stay in the skill body.

Usage:
  python3 scripts/convert-lo-names.py \
      --component c:myComponent \
      --attributes recordId,ownerId,showRevenue \
      --my-domain https://acme.my.salesforce.com

Any of the flags may be omitted; only the requested conversions are printed.
Exit code is 0 on success, 2 on a malformed argument.
"""
import argparse
import re
import sys

LO2_LIBRARY_PATH = "/lightning/lightning.out.latest/index.iife.prod.js"


def camel_to_kebab(name: str) -> str:
    """myComponent / MyComponent / my_component -> my-component."""
    name = name.strip().replace("_", "-")
    # split camelCase / PascalCase boundaries
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", name)
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1-\2", name)
    return name.lower()


def component_tag(aura_id: str) -> str:
    """c:myComponent -> c-my-component (namespace preserved)."""
    aura_id = aura_id.strip()
    if ":" in aura_id:
        ns, name = aura_id.split(":", 1)
    else:
        ns, name = "c", aura_id
    return f"{ns.strip().lower()}-{camel_to_kebab(name)}"


def library_url(my_domain: str) -> str:
    """Normalize a My Domain to the versioned LO 2.0 library URL."""
    d = my_domain.strip().rstrip("/")
    if not d.startswith("http"):
        d = "https://" + d
    # Beta hosts on *.lightning.force.com; LO 2.0 must load from *.my.salesforce.com
    d = d.replace(".lightning.force.com", ".my.salesforce.com")
    # strip any path the caller pasted, keep scheme://host
    m = re.match(r"(https?://[^/]+)", d)
    host = m.group(1) if m else d
    return f"{host}{LO2_LIBRARY_PATH}"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--component", help="Beta component id, e.g. c:myComponent")
    p.add_argument("--attributes",
                   help="comma/space separated camelCase attribute names")
    p.add_argument("--my-domain",
                   help="org My Domain or Beta host URL")
    args = p.parse_args(argv)

    if not (args.component or args.attributes or args.my_domain):
        p.print_help()
        return 2

    if args.component:
        print(f"component-tag: <{component_tag(args.component)}>")

    if args.attributes:
        raw = [a for a in re.split(r"[,\s]+", args.attributes) if a]
        pairs = [(a, camel_to_kebab(a)) for a in raw]
        print("attributes:")
        for src, dst in pairs:
            print(f"  {src} -> {dst}")

    if args.my_domain:
        print(f"library-url: {library_url(args.my_domain)}  (add the `async` attribute)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
