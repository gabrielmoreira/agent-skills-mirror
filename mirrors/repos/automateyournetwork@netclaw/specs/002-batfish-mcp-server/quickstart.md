# Quickstart: Batfish MCP Server

## Prerequisites

1. **Docker**: Batfish runs as a Docker container
2. **Python 3.10+**: For the MCP server
3. **NetClaw**: Existing NetClaw installation

## Step 1: Start Batfish

```bash
docker run -d --name batfish \
  -p 9997:9997 -p 9996:9996 \
  batfish/batfish
```

Verify Batfish is running:
```bash
curl -s http://localhost:9997/v2/diagnostics/status
```

## Step 2: Install Dependencies

```bash
cd mcp-servers/batfish-mcp/
pip install -r requirements.txt
```

## Step 3: Configure Environment

Add to your `.env` file:
```bash
# Batfish MCP Server
BATFISH_HOST=localhost
BATFISH_PORT=9997
```

## Step 4: Register in OpenClaw

The MCP server is registered in `config/openclaw.json` during installation. To verify:
```bash
cat config/openclaw.json | python -m json.tool
```

## Step 5: Test the Server

```bash
# Start the server directly (for testing)
python mcp-servers/batfish-mcp/batfish_mcp_server.py
```

## Example Usage

### Upload and Validate a Configuration

1. Upload a snapshot:
```
Use the upload_snapshot tool with:
- snapshot_name: "my-site-configs"
- config_path: "/path/to/configs/"
```

2. Validate the configuration:
```
Use the validate_config tool with:
- snapshot_name: "my-site-configs"
```

### Test Reachability

```
Use the test_reachability tool with:
- snapshot_name: "my-site-configs"
- src_ip: "10.1.1.1"
- dst_ip: "10.2.2.1"
- protocol: "TCP"
- dst_port: 443
```

### Trace an ACL

```
Use the trace_acl tool with:
- snapshot_name: "my-site-configs"
- device: "fw-01"
- filter_name: "outside-in"
- src_ip: "10.1.1.100"
- dst_ip: "10.2.2.200"
- protocol: "TCP"
- dst_port: 22
```

### Compare Two Configurations

1. Upload both snapshots (before and after)
2. Run differential analysis:
```
Use the diff_configs tool with:
- reference_snapshot: "before-change"
- candidate_snapshot: "after-change"
```

### Check Compliance

```
Use the check_compliance tool with:
- snapshot_name: "my-site-configs"
- policy_type: "interface_descriptions"
```
