# C5 cleanup CLI usage and host boundary

The installed `scripts/cleanup_cli.py` is a dispatcher over the real POSIX quarantine/restore core. An ordinary invocation has **no host adapter**: capabilities and private scope-document structural validation work; selected-root plan/quarantine/reconcile/restore return `HOST_ADAPTER_UNAVAILABLE`. Flags, saved JSON and digests cannot supply ownership verification or operation permission.

## Commands

From the installed Skill, use an absolute script path when running from elsewhere:

```sh
python -I -S -B /trusted/claude-guardian/scripts/cleanup_cli.py capabilities
python -I -S -B /trusted/claude-guardian/scripts/cleanup_cli.py validate-scope --scope /private/operator-scope.json
```

The remaining exact argument forms are intended for a reviewed in-process Agent host bridge. Running them through the ordinary script entry remains blocked:

```text
plan --scope /private/operator-scope.json --plan-output /private/new-plan.json
quarantine --plan-file /private/new-plan.json --expected-plan-digest PLAN_DOCUMENT_DIGEST
reconcile --plan-file /private/new-plan.json --expected-plan-digest PLAN_DOCUMENT_DIGEST --receipt-output /private/new-receipt.json
restore --receipt-file /private/new-receipt.json --expected-receipt-digest RECEIPT_DOCUMENT_DIGEST
```

Use the returned **document_digest** for the wrapper command, not the underlying core's action_digest. A digest verifies selected bytes; it is not authorization. Existing outputs are never overwritten. Private records require appropriate same-user/group 0600 files and 0700 directories; outputs cannot be inside selected, protected or quarantine trees. Review the precise core path/metadata limits before selecting real objects.

## Trusted Agent bridge

The integration point for new plan/quarantine work is `cleanup_cli.main(argument_list, host=reviewed_live_host, entry_request=current_entry)`. Import from a trusted installed scripts directory or use isolated file-path loading; exact sibling dependencies are supported without modifying sys.path. There is no plugin-path, `--entry-file` or “yes/verified” cleanup flag on `cleanup_cli.py` itself (the macOS wrapper below accepts a private entry declaration that grants nothing): the reviewed host supplies the current dict explicitly.

Choose the current local/VM/VPS route before inspecting the selected target. Existing assets, a default recommendation or an old interview are not a current selection, and there is no automatic old-interview-to-entry adapter. The following complete sanitized declaration is a fictional local example with unknown network resources; it permits only entry to the original offline precheck gate:

```json
{
  "schema_version": "guardian-environment-entry-input/0.1",
  "route": {"choice": "local", "state": "selected"},
  "targets": [{"role": "local", "target_ref": "device-1"}],
  "network": {
    "possession": "unknown", "selection": "unknown",
    "configuration": "unknown", "path": "unknown"
  },
  "local_entry": {"kind": "unknown"},
  "final_egress": {"kind": "unknown", "protocol": "unknown"},
  "client": "claude_code"
}
```

Use only documented enums and non-identifying aliases, never real hostnames, IPs, subscription URLs, UUIDs, credentials, configuration text or approval fields. This declaration neither proves a host binding nor authorizes a read, save, move or restore. Unknown/absent resources do not require a purchase before separately authorized offline work; this example does not qualify for configuration or active probes. Keep the actual operator scope's target_ref equal to the chosen declared alias.

After independent host admission and operation-specific approval, the call shapes are:

```python
# current_entry is the complete current dict above, not an imported permission.
# reviewed_live_host must supply the real checks described below.
code = cleanup_cli.main(
    ["plan", "--scope", "/private/guardian-task/operator-scope.json",
     "--plan-output", "/private/guardian-task/new-plan.json"],
    host=reviewed_live_host, entry_request=current_entry,
)
# Only after reviewing the retained plan and its returned document_digest:
code = cleanup_cli.main(
    ["quarantine", "--plan-file", "/private/guardian-task/new-plan.json",
     "--expected-plan-digest", reviewed_plan_digest],
    host=reviewed_live_host, entry_request=current_entry,
)
```

These are placeholder paths and host variables, not a runnable grant or a suggestion to synthesize successful callbacks. The host must check each return code and private state before continuing. plan/quarantine require `offline_precheck` for the same target; unknown resources alone do not waive any cleanup check. Missing, withdrawn, stale, conflicting or mismatched entry blocks new work with fixed errors; changing the dict during a call stops dependent steps. Do not replace it with an implicit local route or reuse previous approval to pass.

Retained plans bind the complete entry used when they were created, including across separate calls or processes. A changed route, target, selected resource or configuration declaration requires a newly generated and reviewed plan; supplying a new eligible entry cannot make an old plan usable for quarantine. Do not edit the stored binding digest to bypass this check. Historical cleanup plans without that entry binding remain usable only for exact reconciliation/recovery of existing work, never for a new quarantine. The same replan requirement applies to retained repair plans; none of these digests conveys permission.

VM declarations require both distinct `vm_host` and `vm_guest` aliases and independent real bindings. Entry eligibility does not provide a VM adapter or let a host result certify a guest. VPS remains basic and non-intrusive: quarantine is rejected with `VPS_QUARANTINE_OUTSIDE_BASIC_CHECK_SCOPE`; no VPS deployment or configuration capability is added. Keep the original exact cleanup host, filesystem and operation boundaries even when an entry is eligible. Other native/diagnostic/repair entry-file forms and the inventory /2 envelope are documented in the installed [environment-entry instructions](host-libraries.md#environment-entry).

The host must implement:

- `verify(target_ref, core_scope_digest, bindings)`: freshly and permissibly verify actual device/user/namespace, exact Claude-owned scope, inactive applications/databases, protected/shared exclusions and an independently verified backup. Return the core's fixed success value only after those checks
- `approve(operation, digest, target_ref, private_review)`: show exact private scope, consequences and recovery; check current operation-specific consent bound to the full wrapper/save review. Repeated calls revalidate that same live consent. Quarantine approval never approves restore
- `exclusive(target_ref, core_scope_digest, bindings)`: hold actual writer exclusion throughout mutation and verification. This is a real host obligation, not a boolean supplied by the model
- `cancelled()`: reflect cancellation; revoked consent or changed context must stop further steps

`bindings` contains backup_ref and host_context_ref. These are live lookup references, not serialized evidence or privileges. Read/hash scope, private persistence, mutation and restore permissions remain distinct. The host privately displays details; ordinary stdout intentionally contains only fixed states, counts, digests and generated recovery identifiers. The implementation itself provides no native Claude discovery or inactivity verifier.

## Operator document and recovery

The bounded operator JSON has exactly schema_version=`guardian-cleanup-operator-scope/0.1`, target_ref, mode=`C5-full-local-data`, ordered roots, protected_paths, quarantine_directory, backup_ref and host_context_ref. Each root has root_ref, canonical absolute path and data_kind (`cli_app_data` or `desktop_app_data`). Declaration is not ownership proof. An independent content-verified backup is required from the host; quarantine is a recoverable move, not a backup copy.

Retain the private plan, its reviewed document digest and the core's quarantine batch. After an interruption, re-establish host identity/ownership/inactivity/backup checks, reconcile against the retained plan and current batch, then obtain separate approval for the new receipt before restore. Exceptions may follow real moves. Use recovery_id, moved_count and stage; never infer “nothing happened” from failure. Interrupted record persistence can report private_record_may_exist=true. Preserve these records and inspect through the authorized recovery path; do not retry with overwrite or delete journals to force success.

Recovery of that existing retained work does not require a new environment entry. Call `cleanup_cli.main(reconcile_arguments, host=reviewed_live_host)` and, after reviewing the fresh receipt and separately approving restoration, `cleanup_cli.main(restore_arguments, host=reviewed_live_host)`. Route withdrawal must not strand the original recovery obligation. This exception preserves all receipt/digest, current target, ownership/inactivity, backup, exclusion and restore-consent checks; it grants no new quarantine, broader cleanup or configuration action. The separate exact-file `recovery_cli.py` paths likewise retain their original recovery checks without requiring `--entry-file`.

Successful quarantine removes **all selected verified roots from their active locations**. Private quarantine data, recovery journals and independent backups remain. Report exact selected/excluded categories and partial completion. This does not certify discovery of every Claude object, permanent secure erasure, credential/browser cleanup, uninstall, account reset or removal of remote restrictions. Permanent purge is unsupported and would require a separate implementation and per-action approval.

## Installed-package evidence

`tests/test_cleanup_cli_package.py` builds and extracts the real release ZIP, checks that the test-only fixture helper is absent, and runs ordinary script commands from an unrelated directory under `-I -S -B`. Without a host all root operations are blocked before reading the supplied missing paths.

A separate test parent creates and captures the exact private fixture identities, backup bytes and a synthetic explicit entry for that fixture target. One child interpreter plans and quarantines with that declaration; after it exits, a different interpreter independently rechecks those live bindings, reloads the retained plan using the parent-held digest, reconciles and restores without a new entry under new stage-specific synthetic consent. The fixture's cooperating writer lock and known absence of an application apply only to this disposable test. No saved approval is reused. Original/protected/backup content and retained records are checked afterward.

This is an observed two-process synthetic recovery exercise, not a native ownership adapter or proof about real Claude processes, arbitrary external writers, macOS application behavior or Windows cleanup. Native acceptance remains `not_run`.

## macOS built-in host (`native_cleanup_mac.py`)

`scripts/native_cleanup_mac.py` is the reviewed host for macOS only; other platforms get `UNSUPPORTED_PLATFORM`. It wraps `cleanup_cli.main` and supplies the four host methods itself:

- `verify`: the host context matches (`context` prints the opaque `host_context_ref` to put in the scope); every root is on a fixed list of Claude-owned locations, split into `regenerable` caches/logs (`~/.claude/cache`, `telemetry`, `usage-data`, `stats-cache.json`, `shell-snapshots`, `debug` ..., `~/Library/Caches/claude-cli-nodejs`, `~/Library/Logs/Claude`, crash/diagnostic reports), `persistent` Desktop data (`Application Support/Claude`, `Claude-3p`, `claude-code-desktop`, `com.anthropic.claudefordesktop`, HTTPStorages, WebKit, Saved Application State, Preferences) and `conversation` records (`~/.claude/projects`, `~/.claude/history.jsonl`; only when the user said yes to moving them — the Agent asks and recommends it, because transcripts keep old command output such as a real public IP; the terminal prompt labels them and says old sessions cannot be resumed) — `allowed` prints it; the whole of `~/.claude` can never be a root, and neither can anything at or under its protected entries (`settings*.json`, `skills`, `plugins`, `commands`, `agents`, `.credentials.json` ...), refused as `shared_scope`; no Claude process is running, and the host itself must not have been started from Claude Code or the Claude app (`RUNNING_UNDER_CLAUDE`); a content-verified backup made by this module matches each root at its active or quarantined location. Anything else is refused. `~/.claude.json` and any root containing `.credentials.json` are refused as `credential_scope` (illegal jailbreak or reverse-proxy tools inside these protected places are removed item by item by the Agent per `illegal-tools-cleanup.md`, not by this host); the CLI binary, `~/.local/share/claude`, `/Applications/Claude.app`, the keychain and browser site data are out of scope.
- `approve`: consent is typed in a real terminal (stdin and stdout must be TTYs). The prompt shows the operation, target, roots, protected paths, quarantine, backup and consequence, and asks for `CONFIRM <operation> <first 8 hex of the review digest>`. Any other input cancels. There is no flag, file or non-interactive mode. A whole cycle asks only four times: `create_backup`, `plan` (one prompt covers reading the scope and saving the plan), `quarantine`, and `restore_cleanup` when needed. `read_reconcile` and `save_receipt` only read what was already approved and write a private record, so they do not ask again; one consent covers its operation group for the process.
- `exclusive`: Claude must not be running on entry or exit. macOS has no mandatory lock, so this detects and fails; processes are matched by executable name, so a Node-launched Claude Code session is not seen and the user is told to quit every session first.
- `cancelled`.

Commands (run by the user, or by an Agent in a terminal the user is watching):

```text
python native_cleanup_mac.py context
python native_cleanup_mac.py allowed
python native_cleanup_mac.py backup --scope /private/scope.json
python native_cleanup_mac.py plan --scope /private/scope.json --plan-output /private/plan.json [--entry-file /private/entry.json]
python native_cleanup_mac.py quarantine --plan-file ... --expected-plan-digest ... --host-scope /private/scope.json [--entry-file ...]
python native_cleanup_mac.py reconcile --plan-file ... --expected-plan-digest ... --receipt-output ... --host-scope /private/scope.json
python native_cleanup_mac.py restore --receipt-file ... --expected-receipt-digest ... --host-scope /private/scope.json
```

`backup` copies the roots to `~/.claude-guardian/backups/<backup_ref>/` (0700, files 0600, hashes in `manifest.json`); that directory must appear in `protected_paths`. The backup holds the same sensitive files as the roots, including login state: keep it private and delete it yourself when no longer needed. `--entry-file` is a private 0600 declaration of the selected route; it grants nothing. On a refusal the reason (`host_refusal`) is printed to stderr. Evidence is synthetic and CI only; native acceptance is `not_run`.

`scripts/native_claude_state_mac.py` holds three further macOS actions, each with its own `CONFIRM <action> <digest8>` terminal consent, Claude not running, and the same refusal when started from Claude: `keychain [--service=credentials|safe-storage]` (find without printing secrets, then delete; sign-in is lost and cannot be recovered), `simple on|off` (structured edit of `CLAUDE_CODE_SIMPLE` in `~/.claude/settings.json` after a backup; the official variable equals `--bare`, so OAuth and keychain credentials are not read and subscription sign-in does not work while it is on), and `timezone <IANA name>` (`sudo systemsetup -settimezone`, password typed only in sudo's own hidden prompt; the previous zone is printed). There is no device-identifier rotation. Windows has no host: see `windows-cleanup.md`.

Usage notes from the 2026-10-22 Mac acceptance run: the `-I -S -B` form above applies only to `cleanup_cli.py` (it loads its siblings by file path); `native_cleanup_mac.py`, `native_claude_state_mac.py` and `repair_cli.py` import their sibling modules normally, so run them as `python /trusted/claude-guardian/scripts/<script>.py ...` (or with the scripts directory on `PYTHONPATH`) — `-I` makes `repair_cli.py` fail with `ModuleNotFoundError: config_edit_plan`. `quarantine`, `reconcile` and `restore` each need `--host-scope`; `plan` and `quarantine` take `--entry-file`. The `document_digest` needed for the next command is printed in the command's stdout JSON, not stored in the saved envelope file. On macOS 15 the kernel adds `com.apple.provenance` to every file a local process writes and it cannot be removed; the metadata gates tolerate that single attribute (ADR-031) and still refuse any other extended attribute, so a root that holds files with other attributes (for example `com.apple.quarantine` on downloaded files) is refused with `UNSUPPORTED_METADATA`: pick a narrower root.
