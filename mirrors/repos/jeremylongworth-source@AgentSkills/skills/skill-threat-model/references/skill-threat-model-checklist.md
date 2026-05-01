# Skill Threat Model Checklist

## Scope

- Source:
- Version or commit:
- Install path:
- Files reviewed:
- Files not reviewed:

## Assets

- Local files
- Repo history
- Environment variables
- Credentials and tokens
- Customer or business data
- External services
- MCP/tool permissions

## Trust Boundaries

- User prompt to skill instructions
- Skill instructions to reference files
- Reference files to scripts
- Scripts to shell, filesystem, network, or package manager
- MCP/tool access to private systems
- Public docs to internal data

## Threat Paths

- Prompt injection or instruction override
- Data exfiltration
- Privilege escalation
- Unsafe script execution
- Secrets exposure
- Supply-chain compromise
- Host-specific install surprise

## Recommendation

Use one:

- approve
- approve with changes
- block
- defer
