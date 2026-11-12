# Special files

Some conflicts can't be resolved from their hunks. Handle each kind below, and stage it. Whatever content conflicts remain go back to step 3.

- **Lockfiles and generated files** (`package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `Cargo.lock`, `poetry.lock`, `uv.lock`, codegen output, snapshots) are rebuilt, not merged. First resolve their inputs (`package.json`, the schema, the source), as any other conflict. Then check out the base's version (`git checkout origin/<base> -- <file>`) and regenerate it with the project's tool (`npm install`, `pnpm install`, `cargo update -p <crate>`, `uv lock`, the codegen or snapshot-update command), so the result reflects both sides' inputs. Read a regenerated snapshot's diff: it should change only where an input changed.
- **Binary files** can't be combined. Take the landing side's version. When the other side's change to the file is part of its intent, ask the user which to keep.
- **Modify/delete** (`UD` / `DU` in `git status --short`): find out why the file went, from the deleting commit's PR. If its code moved or was split, carry the other side's change to the new location and `git rm` the old path. If the feature was removed on purpose, the change goes with it, and the report says so.
- **Renames**: git usually follows a rename and applies the other side's change at the new path; the merge output notes each one, so check that the change arrived. When git missed the rename because the file changed too much, the change shows up as a modify/delete: handle it as above.

Done when every special file is resolved and staged.
