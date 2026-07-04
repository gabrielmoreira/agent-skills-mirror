# Quickstart: SuzieQ MCP Server

**Feature**: 001-suzieq-mcp-server
**Date**: 2026-03-26

## Prerequisites

1. A running SuzieQ instance with its REST API enabled (default port 8000)
2. A valid SuzieQ API key
3. Python 3.10+
4. Network connectivity from the MCP server host to the SuzieQ REST API

## Setup

### 1. Install dependencies

```bash
cd mcp-servers/suzieq-mcp/
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
export SUZIEQ_API_URL="http://your-suzieq-host:8000"
export SUZIEQ_API_KEY="your-api-key-here"

# Optional
export SUZIEQ_VERIFY_SSL="false"   # Set to false for self-signed certs
export SUZIEQ_TIMEOUT="30"         # Query timeout in seconds
```

### 3. Register in openclaw.json

Add to `config/openclaw.json` under `mcpServers`:

```json
{
  "suzieq-mcp": {
    "command": "python3",
    "args": ["-u", "mcp-servers/suzieq-mcp/server.py"],
    "env": {
      "SUZIEQ_API_URL": "${SUZIEQ_API_URL}",
      "SUZIEQ_API_KEY": "${SUZIEQ_API_KEY}",
      "SUZIEQ_VERIFY_SSL": "${SUZIEQ_VERIFY_SSL:-true}",
      "SUZIEQ_TIMEOUT": "${SUZIEQ_TIMEOUT:-30}"
    }
  }
}
```

### 4. Run the server (standalone test)

```bash
python3 -u mcp-servers/suzieq-mcp/server.py
```

The server communicates via stdio. It will wait for JSON-RPC messages on stdin.

## Usage Examples

Once registered with an MCP client (Claude Desktop, OpenClaw, etc.):

- "Show me all BGP peers across the network"
- "What did the routing table look like yesterday at 2pm?"
- "Assert that all BGP sessions are established"
- "Summarize interface health across all devices"
- "Trace the path from 10.0.1.1 to 10.0.2.1 in the datacenter namespace"
- "What are the unique BGP peer states?"

## Verification

To verify the server is working:

1. Ensure SuzieQ REST API is accessible: `curl -k https://your-suzieq-host:8000/api/docs`
2. Start the MCP server and issue a test query via your MCP client
3. Check stderr output for connection and query logs
