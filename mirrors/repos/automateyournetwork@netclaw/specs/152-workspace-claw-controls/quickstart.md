# Local Preview and Verification

1. Work on `152-workspace-claw-controls`; package/push is authorized for the WSL handoff; keep live deployment/publication held.
2. Build/check the extension with its existing npm scripts. Run focused management, process, file and controller tests, then extension/HUD regression tests affected by the change.
3. Run the dedicated workspace preview launcher using the cached native VS Code executable. It must create new temporary user-data, extensions and runtime directories, two synthetic runtime connections and no real provider/device credentials.
4. In the upper Connections area open Workspace Files. Read/edit/upload each allowlisted file, review Save, reopen and verify. Try an externally changed baseline and confirm conflict without overwrite. No Delete control exists.
5. Exercise Save alone, Save and Restart, Stop then Start, and Restart for each runtime. Observe actual fixture process replacement and connection recovery; another fixture installation must remain running.
6. Exercise dirty drafts, native cancellation, Unicode typing/undo, LF/CRLF preservation, three themes, 360px layouts and 200% zoom. Inspect screenshots and fix defects before handoff.
7. Keep the final temporary VS Code window open for owner review. Record exact source/build hashes, fixture attribution, preview metadata and evidence in verification.md. Do not publish or change live runtime services. For the subsequent owner-authorized package/push and real-workspace inspection, follow WSL-HANDOFF.md.
