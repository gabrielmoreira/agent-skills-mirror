# MCP Toolkit

Six skills covering the life of an MCP server: deciding what to build, building
it, proving it works, hardening it, running it, and consuming the ones other
people wrote.

Install it in the projects that build or consume MCP servers. It is deliberately
not part of a general-purpose runtime — most projects never touch MCP, and the
ones that do want depth rather than a summary.

## Install

```bash
copilot plugin install mcp-toolkit@alex-mall
```

Or enable it for one repository by committing `.github/copilot/settings.json`:

```jsonc
{
  "extraKnownMarketplaces": {
    "alex-mall": { "type": "github", "repository": "fabioc-aloha/Alex_Skill_Mall" }
  },
  "enabledPlugins": { "mcp-toolkit@alex-mall": true }
}
```

## The skills

| Skill | Answers |
| --- | --- |
| [mcp-server-design](skills/mcp-server-design/SKILL.md) | Should this be a server at all, and what should it expose? |
| [mcp-server-build](skills/mcp-server-build/SKILL.md) | How do I write it in TypeScript, Python, or C#? |
| [mcp-server-testing](skills/mcp-server-testing/SKILL.md) | Does it work, and can an agent actually use it? |
| [mcp-server-hardening](skills/mcp-server-hardening/SKILL.md) | What breaks when it is reachable over a network? |
| [mcp-server-operations](skills/mcp-server-operations/SKILL.md) | How do I ship, version, and debug it in the wild? |
| [mcp-client-integration](skills/mcp-client-integration/SKILL.md) | How do I safely use a server someone else wrote? |

They are ordered, but each stands alone. Reach for the one matching the question
in front of you.

## Why the client skill is here

Most guidance covers writing servers. Far more people consume them, and that side
carries the risks nobody documents: a server is remote code execution with a
friendly description. `mcp-client-integration` covers evaluating one before you
wire it in.

## Verification

Code samples are verified against the SDK they name, and each skill records what
it was checked against and when. A sample that cannot be verified is removed
rather than carried on trust.

## License

MIT. See [LICENSE](LICENSE).
