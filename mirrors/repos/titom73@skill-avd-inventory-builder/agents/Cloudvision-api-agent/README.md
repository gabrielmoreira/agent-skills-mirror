# CloudVision API Specialist Agent

## Description

**CloudVision API specialist** agent that helps write, debug, and review Python scripts for interacting with Arista CloudVision Portal (on-prem) and CloudVision as-a-Service (CVaaS) using gRPC Resource APIs, CloudVision Connector, or REST endpoints.

## Features

- CloudVision Resource APIs (gRPC, Protobuf-modeled)
- CloudVision Python library (`cloudvision` package)
- CloudVision Connector (low-level gRPC client)
- REST API support (`/api/resources/`)
- Service account token authentication
- On-prem and CVaaS connectivity
- Error handling and retry patterns
- Production best practices

## Supported Workflows

### 1. Device Inventory Management

- Query all devices
- Filter devices by model, status, or tags
- Get device hardware information
- Monitor streaming status

### 2. Event and Alert Monitoring

- Query events by severity
- Filter events by time range
- Create event annotations
- Configure alert rules

### 3. Change Control Lifecycle

- Create change controls
- Approve and start change controls
- Monitor change control execution
- Automated change control workflows

### 4. Configlet Management

- Create static and generated configlets
- Update configlet content
- Assign configlets to devices
- Delete configlets

### 5. Workspace Operations

- Create workspaces for staged changes
- Submit workspaces (create change controls)
- Abandon workspaces (discard changes)

### 6. Tag Management

- Create device and interface tags
- Query devices by tags
- Delete tags

## Installation

### Claude Code

```bash
# From repository root
./scripts/install.sh claude agent Cloudvision-api-agent /path/to/your/project

# Or remote installation (no clone required)
curl -fsSL https://git.as73.inetsix.net/ai/arista-skills-agents/raw/branch/main/scripts/install-remote.sh | bash -s -- claude agent Cloudvision-api-agent
```

The agent will be copied to your clipboard. Paste it into Claude Code.

### GitHub Copilot

```bash
# From repository root
./scripts/install.sh copilot agent Cloudvision-api-agent /path/to/your/repo

# Or remote installation
curl -fsSL https://git.as73.inetsix.net/ai/arista-skills-agents/raw/branch/main/scripts/install-remote.sh | bash -s -- copilot agent Cloudvision-api-agent /path/to/your/repo
```

This creates:
- `.github/agents/Cloudvision-api-agent.md` — agent definition
- `AGENTS.md` (root) — active agent file for GitHub Copilot

## Files

| File | Description | Target Platform | Size |
|------|-------------|-----------------|------|
| `core.md` | Source of truth — core CloudVision API concepts | Reference | ~140 lines |
| `claude.md` | Full version with workflows, examples, troubleshooting | Claude Code | ~995 lines |
| `copilot.md` | Condensed version with essential patterns | GitHub Copilot | ~190 lines |

## Architecture

```
core.md (source of truth)
├── claude.md   (core + workflows + examples + troubleshooting)
└── copilot.md  (condensed for ~8k token budget)
```

### Content Split

**core.md** contains:
- CloudVision architecture (on-prem vs CVaaS)
- Authentication fundamentals
- Resource APIs structure (config vs state, RPC verbs)
- Key API domains
- CloudVision Connector basics
- REST API basics
- Core constraints and code quality standards

**claude.md** adds:
- CVaaS regional URLs
- Advanced authentication patterns (3 patterns)
- Complete workflows with runnable examples:
  * Device inventory query
  * Event monitoring with filters
  * Change control lifecycle (create, approve, execute)
  * Configlet management (create, get, delete)
  * Workspace operations
  * Tag management
- Error handling patterns (basic + retry with backoff)
- Troubleshooting guide (authentication, permissions, network, certificates)
- REST API examples
- Production best practices (connection management, streaming, security, performance)
- Complete API domain reference with use cases

**copilot.md** provides:
- Quick setup patterns (on-prem, CVaaS, async)
- CVaaS regional URLs (condensed)
- Resource APIs quick reference
- Common code patterns (get devices, query events, create configlet)
- REST API example
- Error handling (brief)
- Constraints checklist

## Usage Examples

### Example 1: Get Device Inventory

**User request**:
> Get all devices from CloudVision and filter by model "DCS-7050SX3-48YC8".

**Agent output**: Complete Python script with:
- Environment variable setup
- gRPC channel creation
- DeviceService stub
- `GetAll` streaming
- Model filtering
- Type hints and error handling

### Example 2: Query Critical Events

**User request**:
> Query all critical events from the last 24 hours.

**Agent output**: Python script with:
- EventService stub
- Event filtering by severity
- Time-based filtering
- Event details output (timestamp, device, component, description)

### Example 3: Create and Assign Configlet

**User request**:
> Create a configlet named "NTP-SERVERS" with NTP configuration.

**Agent output**: Python script with:
- ConfigletService stub
- Configlet creation with warning comment
- Example commented out for safety
- Instructions to uncomment to execute

## Dependencies

```toml
[project]
dependencies = [
    "cloudvision>=1.26.1",
    "grpcio>=1.60.0",
    "protobuf>=4.25.0",
]
```

Optional for REST API:
```toml
[project.optional-dependencies]
rest = [
    "requests>=2.31.0",
]
```

## API Domains Reference

| Domain | Description |
|--------|-------------|
| `inventory.v1` | Device inventory, hardware info, streaming status |
| `event.v1` | Events, alerts, event annotations |
| `changecontrol.v1` | Change control lifecycle management |
| `configlet.v1` | Static and generated configlets |
| `configstatus.v1` | Configuration compliance and sync status |
| `workspace.v1` | Workspace management for staged changes |
| `tag.v2` | Device and interface tagging |
| `studio.v1` | Studios configuration and inputs |
| `connectivitymonitor.v1` | Connectivity health monitoring |
| `dashboard.v1` | Custom dashboard definitions |
| `lifecycle.v1` | EOS lifecycle and EOL information |
| `alert.v1` | Alert rules and configurations |
| `serviceaccount.v1` | Service account management |

See `core.md` for complete domain list.

## Resources

- [CloudVision API Documentation](https://aristanetworks.github.io/cloudvision-apis)
- [CloudVision Python Library Docs](https://aristanetworks.github.io/cloudvision-python/)
- [CloudVision Examples Repository](https://github.com/arista-netdevops-community/CloudVisionPortal-Examples)
- [Python Client Source](https://github.com/aristanetworks/cloudvision-python)
- [Go Client Source](https://github.com/aristanetworks/cloudvision-go)
- [gRPC Python Documentation](https://grpc.io/docs/languages/python/)

## Version

- **Current Version**: 1.0
- **Last Updated**: 2026-04-10
- **Compatibility**: CloudVision 2020.1.x+, cloudvision Python package 1.26.1+
