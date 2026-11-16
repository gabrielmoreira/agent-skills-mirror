# Motion Package tools

Create a portable creative package containing a design document, a motion document, materials and optional Agent instructions. The [specification](../../docs/motion-package-spec.md) defines the contract; [Product Story](examples/product-story/README.md) is a complete recipe package to copy and extend.

This private local module uses Node built-ins, with no dependency installation, workspace linking or npm publication. It does not start Studio. From the repository root:

```sh
node packages/motion-package/cli.mjs check packages/motion-package/examples/product-story
node packages/motion-package/cli.mjs pack packages/motion-package/examples/product-story /tmp/product-story
node packages/motion-package/cli.mjs check /tmp/product-story
```

The destination's parent must exist; the destination itself must not. `pack` copies only the declared, hash-verified files and manifest, preserving the checked bytes. It refuses an existing destination or a destination inside the source package. No source code, lifecycle hooks or network calls run during checking/packing. The resulting folder can be shared directly or archived with ordinary tools.

After intentionally editing files, keep the inventory explicit and refresh its hashes:

```sh
node packages/motion-package/cli.mjs lock /tmp/product-story
node packages/motion-package/cli.mjs check /tmp/product-story
```

New file entries need a 64-character lowercase hexadecimal `sha256` field; an all-zero value can be used before the first `lock`. Do not use `lock` to accept unexplained changes in a downloaded package. It writes only the manifest, does not discover new files, and is not a transaction with external editors. Finish editing before locking or packing. The implementation holds the listed bytes in memory; use it for modest authoring packages, not unbounded media archives.

The JSON CLI result distinguishes success from failure; failures exit with status 1. `check` covers manifest fields, required entry roles, dependency declarations, portable paths, file types and hashes. It does not lint creative documents, follow Markdown references, validate input schemas, verify a Skill host, resolve dependencies or prove rendered quality. See the [verification boundary](../../docs/motion-package-spec.md#5-manifest).

The module exports `inspectPackage(directory)`, `lockPackage(directory)` and `packPackage(directory, destination)`. The bundled schema drives shape checks; the internal evaluator supports only the keywords used by this schema and is not a general-purpose JSON Schema library. The toolkit and sample are source authoring resources, not new core production Skills or auto-discovered templates.

Run the focused tests at the repository root:

```sh
node --test tests/motion-package.test.ts
```

## Acknowledgements

Document interoperability follows [DESIGN.md](https://github.com/google-labs-code/design.md) and [Agent Skills](https://github.com/agentskills/agentskills); the [reference review](../../docs/motion-package-spec.md#references-and-acknowledgements) also records the community design collection. The toolkit's original code follows the repository's [Apache-2.0 license](../../LICENSE).
