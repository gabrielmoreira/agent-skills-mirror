---
title: Dependency and artifact integrity
applicability:
- When the work changes, or a claim depends on, what the build consumes or produces beyond hand-maintained source
x-claim-provenance:
- claim: Software construction and configuration management include dependency management, building, release management, and controlled configuration.
  source: https://www.computer.org/education/bodies-of-knowledge/software-engineering/topics
- claim: Secure development includes protecting software components and preserving provenance needed to understand released software.
  source: https://csrc.nist.gov/projects/ssdf
- claim: Reproducibility depends on identified source, build instructions, environment, and inputs for the artifact being compared.
  source: https://reproducible-builds.org/docs/definition/
---

Identify the declaration that owns each direct dependency, the resolver or lock state that selects its transitive graph, and the project policy that constrains source, integrity, license, support, security, platform, or version range. Add a dependency only for a demonstrated capability the project does not already provide more coherently, and compare the operational and maintenance obligations it introduces as part of the design. Popularity, recency, familiarity, or the fact that a package resolves are not evidence that it is acceptable here.

Treat direct and transitive relationships separately. Make the narrowest declaration change that expresses the intended constraint, regenerate resolved state with the adopted tool, and inspect every resulting addition, removal, upgrade, downgrade, source change, integrity change, or platform-specific branch that can affect the project. Do not hand-edit generated lock, catalog, vendor, or resolution output unless the project defines that file as the source of truth. A transitive advisory or conflict is repaired at the declaration that owns the selection, not by pinning the first visible leaf without understanding the graph.

For generated or vendored material, identify the authoritative input and generator before editing. Preserve required notices and project-controlled patches, and make regeneration reproducible enough that a later maintainer can distinguish intended source changes from tool drift. Remove generated or vendored output only after every supported consumer and build path has moved to its replacement or no longer needs it.

Bind a build or release artifact to the source revision, build instructions, configuration, relevant environment, resolved dependencies, generators, and other material inputs that produced it. If the project claims reproducibility, compare independently produced artifacts under the project's defined equivalent inputs; otherwise do not promote a successful rebuild into a reproducibility claim. Where the project records checksums, signatures, attestations, bills of materials, or provenance, verify that they describe the artifact and inputs being accepted rather than merely checking that a record exists.

Keep building, packaging, signing, publishing, installation, and deployment as separate effects. Creating or verifying a local artifact does not authorize uploading it, changing a registry, rotating credentials, or releasing it to users. Report any dependency, resolver, build, or provenance condition that remains unresolved before the affected artifact or completion claim is treated as trusted.
