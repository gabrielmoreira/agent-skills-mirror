# Pack signing keys

One `.pub` per published pack: the ed25519 **verifying** key a consumer
passes to `xerj corpus add <pack> --verify-sig <file>`. A key here is the
out-of-band half of the pack's signature — it must travel by a different
channel than the pack itself (this repository), never inside the pack.

The matching seed (`.key`) **never** lives in this repository. It exists
only as the `PACK_SIGNING_SEED` secret in CI; `xerj corpus build` never
signs, and the publish workflow verifies its own output against the `.pub`
committed here before publishing — so a seed that does not match the
committed `.pub` fails the build instead of shipping an unverifiable pack.

Rotating a key (the procedure, before we need it):

```sh
xerj corpus keygen --out tools/packs/keys/<name>   # new pair
# set the new PACK_SIGNING_SEED secret from the .key, commit the new .pub
# IN THE SAME CHANGE, delete the local .key
```

Consumers re-fetch the `.pub` when they choose to trust the new one; the
next scheduled publish ships under it.

See `docs/CORPUS_PACKS.md` for the full trust model, and
`tools/packs/rust-vulns/README.md` for the pack these rules were written
for.
