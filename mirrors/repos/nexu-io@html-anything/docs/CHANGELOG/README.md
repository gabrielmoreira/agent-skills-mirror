# Stable release descriptions

[Changelog index](../../CHANGELOG.md) · [Release workflow](../release-workflows.md)

## One maintained description

Prepare stable release copy here; the candidate workflow reads it from the **exact frozen application source SHA**, not from the latest branch or the workflow's control checkout. It seals the description in `release-notes.md`, records its hash in `candidate.json` and shows it in the Actions summary. Publication reuses those sealed bytes, adding installation links and release identity. The publisher never rereads these source files.

Test candidates continue to generate automatic commit-based notes. They do not read stable or Unreleased descriptions. Release copy does not imply successful installation, live templates, Agent creation or human audiovisual acceptance.

## Prepare a stable version

1. Update [the English draft](unreleased/en.md) and [the Chinese draft](unreleased/zh-CN.md) with user-visible highlights, additions, changes, fixes, upgrade notes, known issues and acceptance focus. Link relevant public PRs; keep private test results outside the repository.
2. Select the next stable version. Copy the reviewed drafts into `docs/CHANGELOG/v{version}/en.md` and `zh-CN.md`, change their first lines to `# OpenMotion {version}`, and replace the draft notice with the reviewed version scope. Use absolute public HTTPS links so the same Markdown works in GitHub Releases. For example, a selected `0.0.2` uses `v0.0.2/` and `# OpenMotion 0.0.2`; this is an example, not a reserved or published version.
3. Submit those files through a PR to `main`. Build that exact stable version from a source SHA containing the descriptions. Review the sealed Notes in the candidate Summary alongside the package identity.
4. After the separately authorized publication succeeds, add the confirmed version/date and source/Release links to the root index through a PR. Begin the next Unreleased draft. Never label a draft or candidate as published.

Versioned copy uses plain UTF-8 Markdown, without YAML front matter. Each file must have the exact version heading, a nonempty body and a maximum size of 512 KiB; the final bilingual candidate Notes must fit within 1 MiB. `en.md` is the default; `zh-CN.md` is recommended. No base-version, other-version or Unreleased fallback is allowed.

- Neither file exists: warn and keep the automatic draft, including an explicit missing-copy notice. This does not add a manual build gate.
- Only English exists: warn and use it, with a visible missing-Chinese notice.
- Only Chinese exists, or supplied content has an invalid type, encoding, size or version heading: fail before sealing; fix the supplied source instead of silently ignoring it.
- GitHub access or transport fails: report the actual error; an access failure is not proof that copy is absent.

Missing editorial copy does not block packaging by itself. Maintainers still review the public wording before publication. A list of commits is working material, not evidence of completed acceptance or an exhaustive list of known issues.

## Frozen candidates and corrections

Editing the repository does not update an existing candidate, its R2 snapshot or its published Release. When source or sealed Notes change, create a new candidate/version; do not rebuild a second artifact with an already retained version. Existing candidates, including those prepared before this authoring flow, retain their original Notes.

Published GitHub Release prose may be corrected by an authorized maintainer. Publication retries preserve that prose and never overwrite it from the repository. Such an edit does not change the immutable candidate or package; record the correction in the repository when appropriate.

## Distribution boundary

`CHANGELOG.md` and this directory are repository/publication sources. They are deliberately excluded from application, npm installer and plugin ZIP distribution. The candidate's sealed `release-notes.md` remains an Actions/R2 companion file; it is not inserted into the npm tgz. Notes preparation never modifies the already-built tgz. Existing distribution allowlists, runtime behavior, version numbering and manual publication permissions are unchanged.
