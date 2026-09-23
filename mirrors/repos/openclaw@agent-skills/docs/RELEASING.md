# Releasing

This repository distributes skills and helper scripts directly from Git.
`package.json` is private development tooling: there is no npm package or
compiled release artifact. GitHub supplies source archives for each release tag.

1. Run the shared checks described in the README and verify the release PR's
   exact head passes Linux, Windows, and native macOS sandbox CI.
2. Move the accumulated `Unreleased` entries into `## X.Y.Z - YYYY-MM-DD`,
   retain contributor credit, and add a one-line **Highlights** lead-in.
   Keep an empty `## Unreleased` section above the release. Use a patch version
   for fixes, or a minor version for features or compatibility changes.
3. Land the release preparation PR and update a clean `main` checkout.
4. Create and push an annotated `vX.Y.Z` tag at that commit. Publish a GitHub
   Release for the existing tag, using the finalized changelog section as its
   body (`gh release create --verify-tag --notes-file <file>`).
5. Verify the published release is not a draft, its tag resolves to the intended
   commit, and its body matches the changelog. No registry publication, signing,
   or downstream snapshot update is implied by this source release.
