# EVA typography comparison

A fixed-scene study of text roles and repeated technical typography, authored on 2026-11-13. The final treatment preserves every original phrase, the machine illustration, camera, animation and decoded audio. See the [evaluation report](../../docs/reports/typography-evaluation.md) for method, positive observations and limits.

![Original left, final right at 12 seconds](comparison-12s.png)

- [Synchronized 24-second comparison](synchronized-comparison.mp4): original left, final synthesis right. The labels in the historical media read “original” and “final” in Chinese.
- [Original composition](before.html) and [final composition](after.html): exact historical native composition source, supplied for source inspection. They are Hyperframes template fragments, not standalone HTML pages or complete playable projects; project-local font references require the original assets.
- [Typography-only source delta](typography.patch): the body and original timeline are unchanged. All changes are within the style block.
- [Evidence identities](evidence.json): source/media hashes, export checks, audio equality and evaluation conditions. No account data, workstation paths, runtime credentials or private logs are included.

## Review or download

Inspect the same phrase at the same time in the two halves. Compare event vs instrument roles, the repeated use of condensed uppercase labels, numeric grouping, retained explanations and remaining overlaps. More faces, larger type and less copy are not quality criteria by themselves.

The MP4 uses the repository's existing optional-media LFS policy. After cloning with LFS downloads skipped, fetch only this case:

```sh
git lfs pull --include="examples/typography-eva/synchronized-comparison.mp4" --exclude=""
```

Verify the file against `evidence.json`. The source and preview are historical experiment evidence, not a new model run on the PR's latest runtime or the 40-family expansion. These example files and media are excluded from application/Skill distribution.

## Brief and result boundary

The newly authored brief asks for a 24-second landscape motion graphic about EVA Unit 01 awakening: black, purple and fluorescent green; synchronization and restraints; head raise and lit eyes; release; A.T. Field climax; UNIT 01 ending; original layered vector artwork and mechanical/low-frequency audio; editable source and MP4. The unavailable original screenshot project was not replayed.

The frozen original, old/new complaint pair, family-only and treatment/copy controls, old/new ordinary completion pair and final synthesis make eight conditions. Two independent blinded model reviewers agreed on a limited local improvement for the final synthesis, with all original information retained. They did not establish stable new-Skill superiority or human audiovisual acceptance. The final treatment was Agent-curated after review.

## Acknowledgements

EVA / Evangelion and Unit 01 identify the fan-study subject; this is an unofficial vector interpretation, not official artwork or an endorsed production. The case does not distribute proprietary brand fonts. Its selected open fonts are Barlow Condensed, Noto Sans SC, Noto Serif SC and IBM Plex Sans, with upstream identities/licenses maintained in the [catalog](../../skills/openmotion-production/fonts/catalog.json). The historical media contains the rendered artwork and text; complete font binaries, audio source files and project runtime state are not included here.
