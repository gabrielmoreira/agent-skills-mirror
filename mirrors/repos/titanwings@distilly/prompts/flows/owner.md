# Owner Profile

Build a profile of the agent's owner so the agent knows who it works for from the first session. It is **context** the agent reads every session, not a role-play Skill: do not generate a `{character}-{slug}` Skill and never write "you are <user>".

1. Gather information with `{distilly_skill_root}/prompts/owner/intake.md`: first **discover** the sources this agent already has (the tools, connectors and memory in this session, the platform the agent runs on such as Grok's X account, and the user files, connector configs and exports that `tools/owner_sources.py discover` finds on this machine) instead of walking a fixed list; propose which to read, ask the user which to use and whether to add anything else; read only what they pick, read-only; then ask only the questions the sources did not answer. Use only the host's own tools; never ask for API keys or OAuth setup on this path, and do not use the Lark, DingTalk or Slack collectors here.
2. Build the profile with `{distilly_skill_root}/prompts/owner/profile_builder.md`, write it to `/tmp/distilly_owner_profile.md`, show the full text to the user and apply their corrections.
3. After the user approves, save it:
   ```bash
   python3 "{distilly_skill_root}/tools/owner_profile.py" save --profile /tmp/distilly_owner_profile.md
   ```
4. Link it into the current host's always-on user file. Show the `--dry-run` result first and write only after the user agrees:
   ```bash
   python3 "{distilly_skill_root}/tools/owner_profile.py" link --host claude-code --dry-run
   python3 "{distilly_skill_root}/tools/owner_profile.py" link --host claude-code
   ```
   Claude Code uses `~/.claude/CLAUDE.md`; OpenClaw (`--host openclaw`) uses the workspace `USER.md`. Other hosts are not supported yet; tell the user the full profile is at `~/.distilly/owner/profile.md`.
5. Only the text between the Distilly markers changes; everything else in the file is left alone and the previous file is backed up. Delete `/tmp/distilly_owner_profile.md` afterwards.

Updates: when the user corrects something or adds information, edit the full profile, then run `save` and `link` again. To undo: `owner_profile.py unlink --host <host>`.
