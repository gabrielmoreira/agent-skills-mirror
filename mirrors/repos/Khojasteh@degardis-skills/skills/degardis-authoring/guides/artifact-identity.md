---
title: Artifact identity
applicability:
- When the work depends on how an artifact's exact contents are identified
---

An artifact's identity is one digest over the logical content entries the child agent receives. It is independent of where those entries are held, so any party with the exact artifact and this algorithm can recompute and compare the identity whether the artifact is a folder, an archive such as a ZIP, a service-held skill, or another store.

Compute version 1 as follows:

1. Enumerate every content entry under the artifact's top level. A directory marker is not an entry. For each entry, obtain its exact content bytes and its hierarchy of relative name components from the store.
2. Form the canonical name by joining those components with `/` and normalizing the result to Unicode NFC. Encode it as UTF-8 without a byte-order mark. A canonical name must be relative and must contain no empty, `.` or `..` component. If two entries have the same canonical name, the artifact has no identity under this algorithm; do not discard or choose between them.
3. Order the entries by canonical name, comparing Unicode code points rather than using a locale's or a case-insensitive order.
4. Begin one SHA-256 input with the ASCII bytes of `degardis-artifact-identity-v1`, followed by one zero byte.
5. For each entry in order, append an eight-byte unsigned big-endian integer giving the byte length of its canonical UTF-8 name, the name bytes, an eight-byte unsigned big-endian integer giving the length of its content, and the exact content bytes. A length that cannot be represented in eight bytes makes the identity unavailable.
6. The identity is `degardis-artifact-v1:sha256:` followed by the lowercase hexadecimal SHA-256 of that complete input.

The fixed domain, lengths, name rules, and duplicate-name rejection make the entry sequence unambiguous. The same canonical names and bytes therefore give the same identity across stores. Permissions, timestamps, explicit directory records, and other store metadata are left out because not every store has them, so changing only that metadata leaves the identity unchanged. The original non-NFC spelling of a name and the container's own byte representation are likewise outside the identity. Subject to SHA-256's collision resistance, changing any canonical name, content byte, or entry changes the identity, including line endings converted on checkout or an entry added by a store or operating system.

To verify a claimed identity, obtain the artifact, recompute its identity independently, and require the complete identity strings to match. A match establishes that the verified logical entries equal those bound to the claimed digest; it does not establish who created the artifact or digest, whether either was authorized, or whether the artifact is safe. When provenance or authenticity matters, obtain the claimed identity through an authenticated channel or bind it to an authorized signature or attestation, and report that evidence separately.

Report the identity with any handle the host gives the artifact, such as a location or version identifier, and, where the artifact was built from a Degardis source, the source fingerprint, each as provenance rather than as a substitute. Neither a handle nor a fingerprint proves which content the child agent receives.

Where no identity can be established—because the host cannot expose the exact entry names and bytes, an entry is a link to content held elsewhere rather than stable content of its own, the canonical names are invalid or duplicate, the artifact cannot be held stable, or the digest cannot be computed—report it as unavailable and what it would have settled. A judgment about an artifact nobody can name again is a judgment nobody can check.
