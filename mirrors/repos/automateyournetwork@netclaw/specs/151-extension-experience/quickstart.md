# Local development and acceptance

1. Work on `151-extension-experience`; use supported Node24/26. Run `npm run check`, `npm run build`, `npm test` in `extensions/netclaw-vscode`. Do not run `package`/vsce/publish or set a live-provider/VSIX editor test target.
2. Run new HUD document/configuration tests plus existing testbed-editor, terminal, environment and access tests using temporary directories. Test fixtures use synthetic secrets and identities; owner runtime homes and testbed are never targets.
3. Run extension source-development editor acceptance (`npm run test:editor` with the existing isolated fixture path). Review all view families in light/dark/high contrast, keyboard and reduced motion; widths360/700/1200 and zoom200%. Capture synthetic screenshots and state matrix in verification.md. Measure500-entry filter response on recorded host.
4. Connect using a nickname and fixture API address. Open overview, integrations, testbed, BGP and specialized views. Theme changes preserve draft/filter/selection.
5. Testbed: create/update/remove, multi-connection preservation, advanced masked YAML, mode switches, YAML/JSON replace+merge, CSV subset and all export modes. Reject stale/malformed/alias-ambiguous input. Verify active-session refusal, consent revocation, private backups and reviewed restore.
6. MCP: reach every known scoped form within two clicks. Keep/replace/clear, shared fields and changed revision. Verify identity/trust fences and no secret leakage. Run every advertised direct action against isolated owned fixtures; test cancel, missing prereq, failure, interruption and real postconditions. Unsupported operations show guidance.
7. Re-run cross-artifact analysis and applicable regressions after fixes. Update task checkboxes only with real evidence. Document unavailable non-Mac host checks; do not imply qualification.
8. Leave a local source-development preview and exact build/evidence instructions. No package, push, deployment, release, Marketplace or external blog action.

9. Security: bind the existing host-local profile through native prompts. Verify status/log redaction; search rules; preview a rule/mode/network-policy change, cancel without writing, then acknowledge and apply against an isolated CLI fixture. Verify stale review refusal, original-file permissions, unchanged unrelated sections, unsupported/global policy read-only behavior and interrupted-operation no-replay evidence. Do not substitute a real perimeter for this development fixture.

For the complete native-dialog source acceptance, set `NETCLAW_TEST_NATIVE_REVIEW=1`, `NETCLAW_TEST_SUITE=experience`, `VSCODE_EXECUTABLE` to the local editor binary and `NETCLAW_TEST_PLAYWRIGHT` to an installed Playwright module, then run `npm run test:editor`. It creates private temporary profiles and closes only its own editor.

For a persistent throwaway source preview, set `VSCODE_EXECUTABLE` and run `npm run preview:local`. The launcher copies the HUD into a temporary fixture, seeds synthetic inventory and opens Overview; its metadata is `/tmp/netclaw-spec151-source-preview.json`. Closing that window shuts down its fixture. It does not package or install a VSIX.
