# Native, managed, and packaged artifacts

## Native targets

After `open_binary`, use focused search, procedure, or function tools directly.
Use `binary_overview` when target metadata or inventory context helps answer the
question. Prefer literal search, names, decompilation, callers, callees, and
cross-references. Addresses and recovered pseudocode are analysis observations,
not original source. Provider unavailability and unsupported metadata remain
unknown rather than false.

Use `binary_session` with its default summary to check the open target, selected
provider, alignment, and recommended remediation. Request the capabilities view
with a family filter and page bounds only when choosing a tool. Request the full
view only for an explicit session-diagnostic need.

## Managed PE/CLI

Start with `inspect_managed_artifact`. REA's canonical managed inspection is
execution-free: do not claim it loaded, reflected, executed, or resolved the
assembly. Keep managed/native boundaries and unavailable reconstruction facts
explicit. A bring-your-own reconstruction oracle is separate from the canonical
parser and must not become an implicit setup dependency.

## Packages and extraction

Use `inspect_artifact` for application bundles, archives, ZIP/APK/IPA/MSIX/AppX,
ASAR, or DMG inputs when the artifact graph and findings help answer the
question. It returns the complete artifact graph inline. Cite graph manifest
IDs when using them.

Use `extract_artifact` when materialized files are needed. It takes no arguments
and materializes all regular files into a fresh temporary directory chosen by
REA. Symlinks and encrypted entries are inventory facts, not extractable files.
The operation still requires the filesystem-write permission grant; callers do
not choose the destination.

Native DMG traversal is macOS-only, read-only, and requires both operator policy
and `native_mount_approved: true`; without both, retain the root-hash-only result.
Approval for inventory never grants extraction authority.
