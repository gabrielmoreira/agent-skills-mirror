# Failure Pattern Reference

Use this when a bug has repeated, a first fix did not hold, or the symptom smells like runtime state rather than local code syntax.

## Stale Verifier Or Tool Cache

Signals: verifier output points at deleted temp worktrees, old generated files, or paths outside the current repo; rerunning after a clean checkout changes the file path but not the current code.

Checks:
- Confirm the reported path exists.
- Clear the tool cache only after proving the path is stale.
- Re-run the same verifier from the current repo root.

## Worker Queue Or DB Boundary

Signals: UI says work is running but no worker processes it; logs show scheduler activity but no queued row; retry fixes one item but not the pipeline.

Checks:
- Trace request -> enqueue -> worker pickup -> persistence -> UI refresh.
- Inspect queue rows or job state directly.
- Add a regression test around the enqueue boundary, not only the worker body.

## Generated Rebuild Boundary

Signals: source changed but generated output, app bundle, CLI artifact, archive, checksum, or release package still contains old behavior.

Checks:
- Identify the source-to-artifact rule.
- Verify the build system watches the source path.
- Inspect the generated artifact contents, not just the source diff.

## Guard Lifetime Race

Signals: permission, auth, or state guard looks correct locally but a delayed callback, app relaunch, or alternate entry point bypasses it.

Checks:
- Trace guard creation, retention, invalidation, and every alternate entry point.
- Verify cold launch, warm launch, deep link/file open, and retry paths when applicable.
- Prefer explicit durable state over transient flags when the guard must survive relaunch.

## Atomic Temp Filename

Signals: concurrent runs collide, cleanup removes the wrong file, or a partially written output is observed.

Checks:
- Use unique temp directories or atomic rename.
- Keep cleanup scoped to files created by the current run.
- Test two concurrent or back-to-back runs when the tool supports it.

## Path, Cwd, Or Symlink Escape

Signals: an operation intended for one root touches a sibling directory, follows a symlink unexpectedly, or behaves differently from another working directory.

Checks:
- Resolve and compare canonical roots before writing or deleting.
- Reject paths outside the allowed root after symlink resolution.
- Reproduce from a non-default cwd and through any UI entry point that supplies paths.
