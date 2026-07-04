# Quickstart: gNMI Streaming Telemetry MCP Server

**Feature**: 003-gnmi-mcp-server | **Date**: 2026-03-26

## Prerequisites

- Python 3.10+
- gNMI-enabled network device(s) with TLS configured
- TLS CA certificate (and optionally client cert/key for mTLS)
- Network connectivity to device gNMI port

## 1. Install Dependencies

```bash
cd mcp-servers/gnmi-mcp/
pip install -r requirements.txt
```

Or use the project install script:

```bash
bash scripts/install.sh
```

## 2. Configure Environment Variables

Copy the example and fill in your values:

```bash
# In the repo root .env file, add:

# gNMI Target Devices (JSON array format)
GNMI_TARGETS='[{"name":"router1","host":"10.0.0.1","port":57400,"username":"admin","password":"secret","vendor":"cisco-iosxr"},{"name":"switch1","host":"10.0.0.2","port":6030,"username":"admin","password":"secret","vendor":"arista"}]'

# TLS Configuration
GNMI_TLS_CA_CERT=/path/to/ca-bundle.pem
# Optional: for mutual TLS
GNMI_TLS_CLIENT_CERT=/path/to/client.crt
GNMI_TLS_CLIENT_KEY=/path/to/client.key
# Lab mode only: skip TLS verification (still uses TLS encryption)
# GNMI_TLS_SKIP_VERIFY=false

# Response size threshold (bytes, default 1048576 = 1MB)
# GNMI_MAX_RESPONSE_SIZE=1048576

# Max concurrent subscriptions (default 50)
# GNMI_MAX_SUBSCRIPTIONS=50
```

## 3. Register in OpenClaw

The MCP server is registered in `config/openclaw.json`:

```json
{
  "mcpServers": {
    "gnmi-mcp": {
      "command": "python",
      "args": ["mcp-servers/gnmi-mcp/gnmi_mcp_server.py"],
      "env": {}
    }
  }
}
```

## 4. Verify Connection

Test that the server can reach your devices:

```
> Use gnmi_list_targets to show all configured devices and their status
```

Expected: List of devices with reachable/unreachable status.

## 5. Basic Operations

### Query device state (gNMI Get)

```
> Get interface state from router1 using gNMI
```

### Subscribe to telemetry

```
> Subscribe to interface counters on router1 every 10 seconds
```

### Browse YANG models

```
> Show YANG capabilities on router1
```

### Apply configuration (requires ServiceNow CR)

```
> Set interface Loopback0 description to 'Management' on router1 via gNMI with CR CHG0012345
```

## 6. Verify GAIT Logging

After any operation, verify the GAIT audit trail recorded the action:

```
> Show the latest GAIT session log entries
```
