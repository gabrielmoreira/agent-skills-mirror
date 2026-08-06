<!-- SYNTHETIC FIXTURE - no real project or identity data. -->

# Synthetic Session Log - Ordinary Missing Case

**Skill:** `release-helper`

The skill documentation advertises Linux, macOS, and Windows release packaging. During a
Windows request, the skill correctly identified the Windows target and attempted its normal
platform dispatch. The `platform_dispatch` implementation had branches for `linux` and
`darwin` only, so it returned `unsupported platform: windows`.

The skill did not claim broader review coverage, omit an evidence boundary, or generalize
from another platform. The failure is an unimplemented advertised platform case.
