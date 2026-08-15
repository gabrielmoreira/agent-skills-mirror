# Apocalypse Mode

Apocalypse Mode is WebBrain's optional offline knowledge layer. It reads
Wikipedia archives in the openZIM format used by Kiwix. It does **not** make the
configured LLM available offline: generating an answer still requires a local
model or a reachable model provider.

## Consent and installation

The feature is disabled by default. Enabling the packaged Wikipedia skill does
not enable Apocalypse Mode, query the Kiwix catalog, or store article text.
Open the **☢ Apocalypse Mode** link beside **Support** in the Settings header to
opt in.

On supported Chromium browsers, enabling Apocalypse Mode also enables the
local LFM2.5-VL vision fallback and immediately starts caching its approximately
770 MB model from Hugging Face in the background. The management page shows
that progress, and the download continues if the page is closed as long as
Chrome remains open. Wikipedia archives still require their own confirmation.
WebBrain checks hardware WebGPU support before selecting the local provider. If
that check or an automatically started download fails, any configured remote
vision provider becomes active again. Disabling local vision in Settings is an
explicit opt-out and is not undone when the service worker restarts.

Archive language is selected independently from WebBrain's interface language.
The management page reads Kiwix's current OPDS catalog and offers an
**All / Starter / Introductions / Text / Full** tier selector. **Starter** shows
curated article subsets, **Introductions** shows compact `mini` editions,
**Text** shows complete `nopic` text editions without images, and **Full** shows
the complete editions that typically include images and other media. **All**
leaves the catalog unfiltered. Before an install, WebBrain resolves the
archive's Metalink and shows its exact byte size,
archive date, catalog publisher/source and license notice, integrity-piece
count, and the browser's reported free extension storage. The archive is
downloaded only after that confirmation. Existing `.zim` files are validated
and their embedded date/language/source/license metadata is shown before import.
When the current catalog or archive omits a license field, WebBrain says that it
was not declared instead of presenting the general Wikipedia notice as an exact
publisher declaration.

Kiwix publishes very different archive sizes. A complete language edition can
require tens or hundreds of GiB, especially when images are included. Catalog
values can change; the confirmation dialog is authoritative for the selected
current entry.

## Storage and lifecycle

- IndexedDB (`webbrain_apocalypse_mode`) contains the opt-in setting, archive
  metadata, byte cursor, generation, retry state, and storage reference.
- Archive bodies are kept in the extension's Origin Private File System (OPFS),
  not as multi-gigabyte IndexedDB values. Chromium browsers exposing the File
  System Access API can instead use a user-selected file target. Removing that
  archive from WebBrain retains the user-owned file; Firefox uses OPFS.
- Downloads use Metalink piece boundaries and verify each piece before writing
  it. The persisted cursor makes background-worker restarts resumable.
- A lease prevents two extension contexts from claiming the same piece.
- Pause and disable increment a generation so stale work cannot commit.
  Deletion removes metadata before bytes, so an in-flight request cannot
  resurrect the archive.
- Transient failures use bounded exponential backoff. Integrity failures never
  write the rejected piece and eventually require a manual retry.
- Catalog downloads continue in the background after the management page is
  closed. Reopen Apocalypse Mode to inspect progress or pause the download.
- The Chromium-only local vision model uses the browser's Transformers cache.
  After the automatic download completes, its GPU allocations are released
  until WebBrain actually needs local screenshot analysis.
- An installed archive that later becomes unreadable because of corruption,
  eviction, or a revoked file grant moves from ready to an actionable error;
  WebBrain reports the read failure instead of misreporting an empty search.
- Update checks can be manual or automatic. The automatic policy performs a
  daily catalog network check, but installing a discovered replacement still
  requires confirmation. A newer archive never silently overwrites an older
  one; delete the older archive after verifying the replacement.

Imported archives are structurally checked and extension free space is reviewed
before they are copied to OPFS. Closing the management page interrupts an active
user-file import because browsers do not provide a durable file grant
consistently. A stale import is marked failed, and its partial bytes are retained
so the failure remains visible and recoverable.
Delete the failed entry to reclaim that storage, then choose the file again to
restart the import. Partial import bytes are removed automatically on explicit
cancellation, quota exhaustion, or another write failure.

## Retrieval and attribution

If a live Wikipedia tool request fails, the exact built-in Wikipedia skill can
search installed archives by canonical title and title prefix through the ZIM
URL index. Retrieval is behind a provider seam; `createKiwixZimProvider()` is
the default, and tests inject another provider without changing lifecycle or
tool-routing code. The ZIM provider follows redirects, decompresses
uncompressed and Zstandard clusters, selects a bounded passage around matching
query terms, and returns the resolved canonical Wikipedia URL plus embedded
archive language/date/source/license metadata. Local archive text uses the same
untrusted-result boundary as live third-party content.

This first implementation intentionally does not embed Kiwix's GPL-licensed
JavaScript/libzim code in WebBrain's MIT extension. It implements the documented
openZIM structures directly and uses the MIT-licensed `fzstd` decoder. It does
not yet read a ZIM's Xapian full-text index, so conceptual queries that do not
contain an article title may need a more specific title.

## Browser limits

- OPFS quota and eviction policy are browser/profile specific. The pre-install
  estimate is informative, not a reservation.
- Chrome Manifest V3 background workers are ephemeral; persisted jobs and alarms
  resume piece downloads after the worker restarts.
- Firefox uses a persistent extension background page, but large storage quotas
  and OPFS behavior can still differ by version and device.
- Private/incognito profiles, profile clearing, extension removal, or browser
  storage eviction can remove archives.
- Very large archives may be impractical on mobile or low-storage devices.

Catalog metadata comes from the [Kiwix OPDS catalog](https://library.kiwix.org/),
the file format is documented by [openZIM](https://wiki.openzim.org/wiki/ZIM_file_format),
and archive content remains subject to the license embedded by its publisher.
