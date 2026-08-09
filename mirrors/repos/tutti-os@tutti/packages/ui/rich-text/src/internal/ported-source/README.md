# Ported Source Snapshot

These files were moved directly from the old top-level `richText/` directory.

They are intentionally kept out of the package public API for now because they
are only migration references. Treat this folder as a refactor staging area,
not as package source of truth.

Legacy React components that imported desktop-only modules were removed from
this snapshot. Keep any future staging code host-agnostic so shared UI packages
do not accumulate app runtime dependencies.
