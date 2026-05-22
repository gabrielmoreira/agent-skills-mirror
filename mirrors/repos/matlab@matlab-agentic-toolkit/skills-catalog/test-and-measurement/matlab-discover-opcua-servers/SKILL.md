---
name: matlab-discover-opcua-servers
description: >
  Discover OPC UA servers using opcuaserverinfo and the OPC UA Local Discovery
  Service (LDS). Use when finding available OPC UA servers, getting server
  discovery URLs, querying server endpoints and security policies, or
  troubleshooting empty discovery results. Covers LDS-based discovery,
  direct endpoint discovery, and passing results to opcua() for connection.
  Trigger on: opcuaserverinfo, OPC UA discovery, find OPC UA servers,
  server discovery URL, LDS setup, Industrial Communication Toolbox discovery.
license: MathWorks BSD-3-Clause
compatibility: ">=R2020b"
metadata:
  author: MathWorks
  version: "1.0"
---

# OPC UA Server Discovery

Discover available OPC UA servers on the network using `opcuaserverinfo`

## When to Use

- Finding available OPC UA servers on the local network
- Getting the discovery URL or endpoint information for a known server
- Querying server security policies and supported authentication types
- Troubleshooting empty discovery results (LDS issues, certificate trust)
- Setting up prerequisites for OPC UA server discovery

## When NOT to Use

- Creating OPC UA client connections (use `opcua()` directly)
- Reading, writing, or subscribing to OPC UA node values
- Configuring OPC UA connection security (message security, certificates)
- Working with non-OPC UA protocols (Modbus, MQTT)
- Discovering OPC Classic servers (OPC DA, OPC HDA)

## Workflow

### 1. Check prerequisites

Before calling `opcuaserverinfo`, ensure:
1. The OPC UA Local Discovery Service (LDS) is installed and running
2. The target server is registered with the LDS
3. The server's certificate is trusted by the LDS certificate store at
   `C:\ProgramData\OPC Foundation\UA\pki\trusted\certs\`

**Warning:** A `pki\` folder may also exist under `UA\Discovery\` — that is a
backward-compatibility fallback from older LDS deployments. The primary store
is `UA\pki\`. Always place certificates in `UA\pki\trusted\certs\`.

See [references/lds-setup-and-troubleshooting.md](references/lds-setup-and-troubleshooting.md) for paths and setup details.

### 2. Discover servers

**Preferred approach — LDS-based discovery (finds all registered servers):**

```matlab
serverInfo = opcuaserverinfo('localhost');
```

A single call to `opcuaserverinfo` with a hostname queries that host's LDS on
port 4840. The LDS returns information about ALL servers registered with it.
Do not scan IP ranges or iterate over hosts — the LDS aggregates this.

**Alternative — direct endpoint discovery (when you know the server URL):**

```matlab
serverInfo = opcuaserverinfo('opc.tcp://myserver:53530/OPCUA/SimulationServer');
```

Use this when connecting to a specific known server that may not be registered
with the LDS, or when the LDS is not available.

### 3. Inspect results

```matlab
for k = 1:numel(serverInfo)
    fprintf('Server: %s (port %d)\n', serverInfo(k).Hostname, serverInfo(k).Port);
    fprintf('  Best security: %s / %s\n', ...
        serverInfo(k).BestMessageSecurity, serverInfo(k).BestChannelSecurity);
    fprintf('  Endpoints: %d available\n', numel(serverInfo(k).Endpoints));
end
```

### 4. Connect to a discovered server

```matlab
uaClient = opcua(serverInfo(1));
connect(uaClient);
```

The `opcua()` function accepts a `ServerInfo` object directly — no need to
extract hostname and port manually.

## Key Functions

| Function | Syntax | Purpose |
|----------|--------|---------|
| `opcuaserverinfo` | `opcuaserverinfo(hostname)` | Query LDS on a host for all registered servers |
| `opcuaserverinfo` | `opcuaserverinfo(discoveryUrl)` | Query a specific discovery endpoint URL |
| `opcua` | `opcua(serverInfoObj)` | Create client from ServerInfo object |
| `findDescription` | `findDescription(serverInfo, text)` | Filter servers by description text |
| `findAuthentication` | `findAuthentication(serverInfo, type)` | Filter servers by auth type |

**There is no `opcuaserverinfo(hostname, port)` syntax.** To specify a port,
use the discovery URL form: `opcuaserverinfo('opc.tcp://hostname:port')`.

## opc.ua.ServerInfo Properties

| Property | Type | Description |
|----------|------|-------------|
| `Hostname` | char | Host name of the OPC UA server |
| `Port` | double | TCP port for connections |
| `Description` | char | Human-readable server description |
| `UserTokenTypes` | cell array | Supported auth types (e.g., `{'Anonymous', 'Username', 'Certificate'}`) |
| `BestMessageSecurity` | enum | Highest message security: `SignAndEncrypt`, `Sign`, or `None` |
| `BestChannelSecurity` | enum | Highest channel security policy |
| `Endpoints` | array | Array of `opc.ua.EndpointDescription` objects |

**Note:** `opc.ua.ServerInfo` has `Description`, not `Name`. The `Name` property
belongs to `opc.ua.Client`, not `ServerInfo`.

## opc.ua.EndpointDescription Properties

| Property | Type | Description |
|----------|------|-------------|
| `EndpointUrl` | char | Full endpoint URL for connection |
| `MessageSecurityMode` | enum | Security mode for this endpoint |
| `ChannelSecurityPolicy` | enum | Channel security policy for this endpoint |
| `UserAuthTypes` | cell array | Auth types supported on this endpoint |

## Patterns

### Discover all servers via LDS

```matlab
serverInfo = opcuaserverinfo('localhost');
if isempty(serverInfo)
    disp('No servers found. Check LDS prerequisites.');
else
    disp(serverInfo);
end
```

### Discover a specific server by URL

```matlab
serverInfo = opcuaserverinfo('opc.tcp://myserver:53530/OPCUA/SimulationServer');
disp(serverInfo);
```

### Filter servers by authentication type

```matlab
serverInfo = opcuaserverinfo('localhost');
anonServers = findAuthentication(serverInfo, 'Anonymous');
certServers = findAuthentication(serverInfo, 'Certificate');
```

### Pass discovery result to opcua() for connection

```matlab
serverInfo = opcuaserverinfo('localhost');
uaClient = opcua(serverInfo(1));
connect(uaClient);
```

## Common Mistakes

| Mistake | Why It's Wrong | Correct Approach |
|---------|---------------|-----------------|
| `opcuaserverinfo(host, port)` | Two-argument syntax does not exist | `opcuaserverinfo('opc.tcp://host:port')` |
| Scanning subnet IPs in a loop | LDS already aggregates all registered servers | `opcuaserverinfo('localhost')` returns all servers |
| Using `serverInfo.Name` | Property does not exist on `ServerInfo` | Use `serverInfo.Description` |
| Using `serverInfo.EndpointUrl` | Property belongs to `opc.ua.Client`, not `ServerInfo` | Use `serverInfo.Endpoints(k).EndpointUrl` |
| Assuming empty result means LDS is down | Empty result can also mean no servers registered or cert not trusted | First run `sc query UALDS` to confirm LDS status, then check registration and trust |
| Using `UA\Discovery\pki\` as the cert store | `Discovery\pki\` is a backward-compatibility fallback (only has `trusted\`) — not the primary store | The LDS primary cert store is at `C:\ProgramData\OPC Foundation\UA\pki\` (has both `trusted\` and `rejected\`) — check `rejected\certs\` for untrusted certs, copy to `trusted\certs\` to trust them |
| Not mentioning LDS prerequisites | Discovery returns empty without proper setup | Always check: LDS running, server registered, certificate trusted |

## Conventions

- Always prefer LDS-based discovery (`opcuaserverinfo(hostname)`) over direct endpoint queries when finding all servers on a network
- Always mention the three LDS prerequisites when discussing discovery setup
- Use `serverInfo.Description` for display — not `Name` (which doesn't exist)
- Pass the `ServerInfo` object directly to `opcua()` — don't extract hostname/port manually
- When discovery returns empty, do NOT assume the LDS is down — first verify with `sc query UALDS`, then check server registration, then certificate trust (in that order)

----

Copyright 2026 The MathWorks, Inc.

----
