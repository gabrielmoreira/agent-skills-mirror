# Quickstart: GNS3 MCP Server

**Feature**: 012-gns3-mcp-server
**Date**: 2026-04-02

## Prerequisites

1. **GNS3 Server** running with REST API v3 enabled (GNS3 2.2.0+)
2. **Python 3.10+** installed
3. **Valid GNS3 credentials** with appropriate privileges
4. **Network connectivity** to GNS3 server (default port: 3080)

## Installation

```bash
# Navigate to the server directory
cd mcp-servers/gns3-mcp-server

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your GNS3 server details
nano .env
```

## Configuration

Edit `.env` with your GNS3 server details:

```bash
# Required
GNS3_URL=http://localhost:3080
GNS3_USER=admin
GNS3_PASSWORD=your_password_here

# Optional
GNS3_VERIFY_SSL=true
GNS3_TOKEN_TTL=3000
```

## Verify Installation

```bash
# Test connectivity (from mcp-servers/gns3-mcp-server/)
python -c "
import os
from dotenv import load_dotenv
import httpx

load_dotenv()
url = os.getenv('GNS3_URL')
response = httpx.get(f'{url}/v3/version')
print(f'GNS3 Server: {response.json()}')
"
```

## Register in OpenClaw

Add to `config/openclaw.json`:

```json
{
  "mcpServers": {
    "gns3": {
      "command": "python3",
      "args": ["-u", "mcp-servers/gns3-mcp-server/gns3_mcp_server.py"],
      "env": {
        "GNS3_URL": "${GNS3_URL}",
        "GNS3_USER": "${GNS3_USER}",
        "GNS3_PASSWORD": "${GNS3_PASSWORD}"
      }
    }
  }
}
```

## Basic Usage Examples

### List Projects
```
"List all my GNS3 labs"
```

### Create a Lab
```
"Create a new GNS3 lab called routing-test"
```

### Add Devices
```
"Add a Cisco IOSv router to routing-test"
"Add an Arista vEOS switch to routing-test"
```

### Connect Devices
```
"Connect router1 eth0 to switch1 eth0 in routing-test"
```

### Start the Lab
```
"Start all nodes in routing-test"
```

### Capture Traffic
```
"Start capturing traffic on the link between router1 and router2"
```

### Create Snapshot
```
"Create a snapshot called baseline for routing-test"
```

### Console Access
```
"Show console info for router1 in routing-test"
```

## Troubleshooting

### Connection Refused
- Verify GNS3 server is running: `curl http://localhost:3080/v3/version`
- Check firewall allows port 3080
- Verify GNS3_URL is correct

### Authentication Failed
- Verify username and password in .env
- Test credentials in GNS3 Web UI
- Check user has required privileges

### Template Not Found
- List available templates: "List GNS3 templates"
- Verify template is installed on GNS3 server
- Check template name spelling

### Node Start Failed
- Check compute server resources (CPU, memory)
- Verify node's disk image exists
- Review GNS3 server logs

## Skills Reference

| Skill | Purpose |
|-------|---------|
| gns3-project-lifecycle | Create, open, close, delete, clone labs |
| gns3-node-operations | Add, start, stop, reload devices |
| gns3-link-management | Connect and disconnect interfaces |
| gns3-packet-capture | Capture and analyze traffic |
| gns3-snapshot-ops | Save and restore lab states |

## Next Steps

1. Create your first lab: "Create a GNS3 lab called my-first-lab"
2. Add some devices from templates
3. Connect them with links
4. Start the lab and access consoles
5. Create a snapshot before making changes
