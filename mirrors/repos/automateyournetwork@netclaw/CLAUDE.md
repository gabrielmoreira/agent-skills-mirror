# netclaw Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-04-16

## Active Technologies
- N/A (stateless server; subscription state held in-memory during runtime) (003-gnmi-mcp-server)
- Python 3.10+ + FastMCP (MCP framework), azure-mgmt-network, azure-mgmt-resource, azure-identity (DefaultAzureCredential), gait_mcp (audit logging) (004-azure-network-mcp)
- N/A (stateless; reads from Azure ARM APIs) (004-azure-network-mcp)
- JavaScript (ES2022) / HTML5 / CSS3 for Canvas components; SKILL.md for skill definition + OpenClaw Canvas/A2UI framework (rendering primitives), existing MCP servers (data sources) (005-canvas-a2ui-integration)
- N/A (stateless visualization — all data fetched on demand from MCP servers) (005-canvas-a2ui-integration)
- Python 3.10+ + FastMCP (mcp SDK), httpx (async HTTP client), python-dotenv (001-suzieq-mcp-server)
- N/A (stateless proxy to SuzieQ REST API) (001-suzieq-mcp-server)
- Python 3.10+ + anthropic (SDK with count_tokens), toon-format (TOON serialization), FastMCP (existing MCP framework) (006-token-optimization)
- N/A (in-memory session ledger; no persistent storage) (006-token-optimization)
- N/A (no server code — Jenkins plugin is Java-based and runs inside Jenkins). Skill documentation and configuration files only. + Jenkins 2.533+ with MCP Server plugin (v0.158+), MCP Java SDK 0.17.2 (007-jenkins-mcp-server)
- N/A (stateless — Jenkins maintains all job/build state) (007-jenkins-mcp-server)
- TypeScript/Node.js (community MCP server). No netclaw-authored server code — configuration and skill documentation only. + @zereight/mcp-gitlab (npm package), Node.js 18+ (008-gitlab-mcp-server)
- N/A (stateless proxy to GitLab REST API) (008-gitlab-mcp-server)
- Python 3.10+ (community MCP server). No netclaw-authored server code — configuration and skill documentation only. + mcp-atlassian (pip package), Python 3.10+ (009-atlassian-mcp-server)
- N/A (stateless proxy to Atlassian REST APIs) (009-atlassian-mcp-server)
- Python 3.10+ (consistent with existing NetClaw MCP servers) + FastMCP (MCP framework), asyncio (UDP receivers), pysnmp (SNMP trap decoding), python-syslog-rfc5424 (syslog parsing), xflow (IPFIX/NetFlow decoding) (010-telemetry-receivers)
- In-memory only (data lost on restart, acceptable for demo/testing scope) (010-telemetry-receivers)
- Markdown (documentation reorganization) + N/A (pure markdown files, OpenClaw read tool) (011-soul-optimization)
- Filesystem (`~/.openclaw/workspace/`) (011-soul-optimization)
- Python 3.10+ (consistent with existing NetClaw MCP servers) + FastMCP (MCP framework), httpx (async HTTP client), python-dotenv (environment variables) (012-gns3-mcp-server)
- N/A (stateless proxy to GNS3 REST API) (012-gns3-mcp-server)
- Python 3.10+ (community MCP server uses prisma_sase SDK) + prisma-sdwan-mcp (community), prisma_sase SDK (OAuth2 client) (013-prisma-sdwan-mcp-server)
- N/A (stateless proxy to Prisma SASE REST API) (013-prisma-sdwan-mcp-server)
- N/A (Remote MCP managed service) + Datadog MCP remote endpoint, DD_API_KEY, DD_APP_KEY (016-datadog-mcp-server)
- N/A (stateless proxy to Datadog APIs) (016-datadog-mcp-server)
- Python 3.10+ (consistent with NetClaw MCP servers) + blender-mcp (community, via uvx), Blender 3.0+ (user-installed) (024-blender-3d-viz)
- N/A (stateless - visualization is ephemeral in Blender) (024-blender-3d-viz)
- Python 3.10+ (community MCP server with Aruba CX REST API client) + aruba-cx-mcp-server (community), httpx or requests (REST client) (025-aruba-cx-mcp-server)
- N/A (stateless proxy to Aruba CX REST API) (025-aruba-cx-mcp-server)
- N/A (Remote MCP server - no code required) + N/A (Remote MCP managed service) (026-devnet-content-search-mcp)
- N/A (stateless - all data from remote API) (026-devnet-content-search-mcp)
- Python 3.10+ (MCP servers, policy scripts), Bash (installation) + NVIDIA OpenShell CLI (uv tool), Docker (container runtime), existing FastMCP servers (027-netshell-security)
- Local filesystem for policies and audit logs; no database (027-netshell-security)
- Bash (installation scripts), Python 3.10+ (DefenseClaw requires), Go 1.25+, Node.js 20+ + DefenseClaw (Cisco), Docker (container runtime) (027-netshell-security)
- SQLite (DefenseClaw audit logs), optional SIEM (Splunk HEC, OTLP) (027-netshell-security)

- Python 3.10+ + FastMCP (MCP framework), grpcio + grpcio-tools (gRPC transport), pygnmi (gNMI client library), protobuf, cryptography (TLS handling) (003-gnmi-mcp-server)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.10+: Follow standard conventions

## Recent Changes
- 027-netshell-security: Added Bash (installation scripts), Python 3.10+ (DefenseClaw requires), Go 1.25+, Node.js 20+ + DefenseClaw (Cisco), Docker (container runtime)
- 027-netshell-security: Added Python 3.10+ (MCP servers, policy scripts), Bash (installation) + NVIDIA OpenShell CLI (uv tool), Docker (container runtime), existing FastMCP servers
- 026-devnet-content-search-mcp: Added N/A (Remote MCP server - no code required) + N/A (Remote MCP managed service)


<!-- MANUAL ADDITIONS START -->

## DefenseClaw Security Layer

DefenseClaw from Cisco AI Defense is the recommended enterprise security layer for NetClaw. It provides comprehensive protection including OpenShell sandbox, component scanning, runtime guardrails, and SIEM integration.

### Quick Start

```bash
# During installation
./scripts/install.sh
# Answer "y" to "Enable DefenseClaw (recommended)?"

# Or enable later
./scripts/defenseclaw-enable.sh
```

### Key Features

- **Automatic OpenShell Sandbox** - Kernel-level isolation (Landlock, seccomp, network namespaces)
- **Component Scanning** - Skills, MCPs, and plugins scanned before execution
- **CodeGuard Analysis** - Detects credentials, eval, shell commands, SQL injection
- **Runtime Guardrails** - LLM prompt/completion inspection, tool call inspection
- **Audit Logging** - SQLite database with optional SIEM export (Splunk HEC, OTLP)

### Key Commands

```bash
defenseclaw --version              # Check installation
defenseclaw skill scan <name>      # Scan a skill
defenseclaw tool block <tool>      # Block a tool
defenseclaw tool allow <tool>      # Allow a tool
defenseclaw alerts                 # View security alerts
defenseclaw setup guardrail --mode action  # Enable blocking mode
```

### Configuration

Security mode is stored in `~/.openclaw/config/openclaw.json`:

```json
{
  "security": {
    "mode": "defenseclaw"  // or "hobby" for no security
  }
}
```

### Documentation

- **Full Guide**: [docs/DEFENSECLAW.md](docs/DEFENSECLAW.md)
- **Security Principles**: [docs/SOUL-DEFENSE.md](docs/SOUL-DEFENSE.md)
- **Upgrade Guide**: [docs/UPGRADE-TO-DEFENSECLAW.md](docs/UPGRADE-TO-DEFENSECLAW.md)

<!-- MANUAL ADDITIONS END -->
