# YouTube Research MCP for GitHub Copilot

This optional GitHub Copilot plugin installs the canonical `youtube-mcp-tools`
MCP server for evidence-first YouTube research, transcript analysis, and
source-grounded collateral generation.

Install it through Alex ACT Plugin Mall:

```bash
copilot plugin marketplace add fabioc-aloha/Alex_Skill_Mall
copilot plugin install youtube-research@alex-mall
```

The plugin launches `youtube-mcp-tools@2.0.0` with `npx`. Public transcript
tools require no credential. Set `YOUTUBE_API_KEY` in the host environment to
enable YouTube search, metadata, analysis, flashcards, and live topic research.
Direct collateral generation is opt-in and additionally uses the documented
`YOUTUBE_MCP_DIRECT_*` environment variables.

For non-Copilot hosts, use the installation guidance in the
[canonical repository](https://github.com/fabioc-aloha/youtube-mcp-tools).
