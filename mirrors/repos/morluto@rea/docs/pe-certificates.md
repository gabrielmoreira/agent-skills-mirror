# PE Authenticode certificate tables

`inspect_pe_certificates` / `inspect-pe-certificates` answers whether one
selected local PE32/PE32+ image declares an `IMAGE_DIRECTORY_ENTRY_SECURITY`
table, which `WIN_CERTIFICATE` entries that table stores, and which PKCS#7
signer and X.509 fields those entries carry. It reads the file without
executing it and does not require a Windows SDK, catalog file, or disassembler.

```bash
rea inspect-pe-certificates /absolute/path/to/application.exe --json
```

The CLI resolves relative paths against the caller's working directory. MCP
and the advertised input schema require an absolute filesystem path and
preserve that exact selection:

```json
{
  "name": "inspect_pe_certificates",
  "arguments": { "path": "/artifacts/application.exe" }
}
```

## Observations

The inline Evidence result contains the artifact path, SHA-256, and byte length.
`table` is the file-offset security directory, or `null` when the directory is
absent or zero. Each `entries[]` item reports `WIN_CERTIFICATE` length,
revision, type, and the payload SHA-256.

For `WIN_CERTIFICATE` type 2 (PKCS#7 signedData) `pkcs7` contains digest
algorithm OIDs, embedded X.509 serial/issuer/subject/validity fields, and
signer identifier facts. A signer identified by subject key identifier reports
that value as `subject_key_identifier_hex`. Other certificate types keep
`pkcs7` null.

A missing table is observed absence of that directory. It is not proof the
image is unsigned in every catalog or overlay sense.

## Limits and failures

The selected file is limited to 64 MiB by default (512 MiB maximum). At most
eight `WIN_CERTIFICATE` entries are examined by default. Malformed PE headers,
truncated certificate entries, and PKCS#7 that is not structurally signedData
fail without partial success. A security directory that ends in fewer than
eight header bytes, including zeros, is a truncated `WIN_CERTIFICATE` and
fails the same way. SignedData must contain at least one `SignerInfo`, and
each `SignerInfo` must carry a non-empty signature value. Each embedded X.509
certificate must include `subjectPublicKeyInfo` and `signatureValue`. Decoded
certificate name text, serials, validity spellings, and subject key identifiers
share a 64 KiB budget per PKCS#7 payload. Unsupported certificate name
encodings, including TeletexString (T.61) and GeneralString, fail explicitly
rather than returning names decoded with an assumed character set.

This workflow does not verify signatures, certificate chains, timestamps, or
Authenticode digest coverage of image bytes.
