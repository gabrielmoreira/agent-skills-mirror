# Data Exfiltration Review Checklist

## Data Sources

- Workspace files
- Home directory files
- Environment variables
- Git history
- Browser/profile data
- Customer records
- Logs/traces
- MCP resources

## Data Sinks

- HTTP requests
- Package install hooks
- CLI telemetry
- Logs and screenshots
- Generated reports
- Issue/PR comments
- Customer messages
- External paste or storage services

## Red Flags

- Broad recursive file reads
- Secret file paths
- Encoded or obfuscated payloads
- Unexplained network calls
- Uploads in helper scripts
- Instructions to summarize private data into public outputs
- Missing redaction rules

## Mitigations

- Narrow file scope.
- Use read-only defaults.
- Require explicit approval for outbound sends.
- Redact secrets and private data.
- Document allowed data sources and sinks.
