# Provider discovery and setup

Read for a new generation plan, provider setup or the MCP handbook handoff. Apply the entry's provider preference and spend authorization before submission.

## Media handbook handoff

The MCP handbook media-generation example is an explicit request for multimodal guidance. Start with read-only `inspect` even when the user has yet to supply a concrete asset brief. When a provider is usable under the entitlement guidance below, continue the existing request or ask what they want to generate or which reference they want to recreate. Preserve any reference, brief and project context already supplied.

Follow the setup below and the [job procedure](jobs.md) when generation is needed. Read-only onboarding can proceed without creating a project or starting generation.

## Inspect providers and resolve setup

Call `openmotion_media_use` with `action: "inspect"`. A provider is usable when `available: true`, except for an OpenDesign account with `mediaEntitlement: "not-included"`. If setup is needed, call the tool and arguments from `settingsHandoff` (`openmotion_open_preview` with `target: "providers"`) and follow its page handoff. Verify the page is visible before saying it opened, then give the user one clear next action. Fold it into the workflow's upfront question if there is one.

- **Sign-in needed** (`agent_media_signed_out`): click **Sign in with OpenDesign** directly on the opened **Settings → Model providers → OpenDesign** page (**设置 → 模型供应商 → OpenDesign → 使用 OpenDesign 登录**). Expired sign-in also needs reauthorization.
- **Free or Go** (`mediaEntitlement: "not-included"`): both plans exclude image, video, speech and music generation. If no other provider is usable or the user prefers OpenDesign, use `entry: "agent_media_upgrade_go"` for Go or `entry: "agent_media_upgrade_free"` for Free and guide them to click **Upgrade to Plus** (**升级到 Plus**) directly on the opened **OpenDesign** page. Plus, Pro and Max include multimodal generation.
- **Rejected key** (`agent_media_key_rejected`): say the saved key was rejected and ask the user to replace it in **Model providers**. The user can also save an OpenDesign Cloud or other supported API key here or supply local media. Cloud keys follow their account's model access and credits. Keep keys in settings.

After setup confirmation, run `inspect` again and resume the original request. A signed-in account (`available: true`) with `mediaEntitlement: "included"` or `"unknown"` can proceed to model discovery, as can other usable providers under the user's preferences and spend consent. The normalized plan and boolean `hasBalance` are advisory when present. Model access and credits are checked when generating.

For each needed kind, call `action: "models", provider, modality, refresh: true`. Audio discovery uses `text-to-speech` for speech and `text-to-audio` for music or sound effects. If a needed kind is unavailable, explain the missing part and offer a suitable alternative in the consent question. Continue independent work and avoid switching paid providers or dropping requested capabilities without consent.
