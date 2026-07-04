# Quickstart: Telemetry & Event Receivers

**Feature Branch**: `010-telemetry-receivers`
**Date**: 2026-03-28

This guide shows how to start the telemetry receivers and test with a Cisco Catalyst 9300.

---

## Prerequisites

- Python 3.10+
- Cisco Catalyst 9300 with IOS-XE 17.2+ (for TLS syslog)
- UDP tunnel service (Pinggy, LocalXpose, or Tailscale) - ngrok does NOT support UDP
- Network connectivity from Catalyst 9300 to receiver endpoints

---

## Installation

```bash
# Clone and navigate to netclaw
cd netclaw

# Install dependencies for each receiver
pip install -r mcp-servers/syslog-mcp/requirements.txt
pip install -r mcp-servers/snmptrap-mcp/requirements.txt
pip install -r mcp-servers/ipfix-mcp/requirements.txt
```

---

## Quick Start (All Receivers)

### 1. Set Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit with your settings
nano .env
```

Required variables:
```bash
# Syslog
SYSLOG_PORT=514

# SNMP Traps
SNMPTRAP_PORT=162
SNMPTRAP_COMMUNITY=netclaw-traps
# For SNMPv3: SNMPTRAP_V3_USERS='[{"user":"admin","auth":"SHA","auth_key":"authpass123","priv":"AES","priv_key":"privpass123"}]'

# IPFIX/NetFlow
IPFIX_PORT=2055
```

### 2. Start Receivers

Each receiver runs as a separate MCP server:

```bash
# Terminal 1: Syslog
python mcp-servers/syslog-mcp/syslog_mcp_server.py

# Terminal 2: SNMP Traps
python mcp-servers/snmptrap-mcp/snmptrap_mcp_server.py

# Terminal 3: IPFIX
python mcp-servers/ipfix-mcp/ipfix_mcp_server.py
```

Or register in OpenClaw config and start via the gateway.

### 3. Expose Receivers via UDP Tunnel

**Important**: ngrok does NOT support UDP. Use one of these alternatives:

#### Option A: Pinggy (Recommended)

```bash
# Install pinggy
curl -sL https://pinggy.io/install.sh | bash

# Start UDP tunnels
pinggy -udp 514    # Syslog
pinggy -udp 162    # SNMP traps
pinggy -udp 2055   # IPFIX
```

#### Option B: Tailscale

```bash
# Install and authenticate Tailscale
curl -fsSL https://tailscale.com/install.sh | sh
tailscale up

# Your Tailscale IP is now accessible from Catalyst 9300
# if both are on the same Tailscale network
tailscale ip -4
```

#### Option C: LocalXpose

```bash
# Install localxpose
npm install -g localxpose

# Start UDP tunnels
loclx tunnel udp --port 514
loclx tunnel udp --port 162
loclx tunnel udp --port 2055
```

---

## Cisco Catalyst 9300 Configuration

### gNMI (Existing - Validation Only)

```
! Enable gNMI
feature netconf-yang

! Configure gNMI
gnmi-yang
 port 57400
 vrf management
```

### Syslog

```
! Basic UDP syslog
logging host <RECEIVER-IP> transport udp port 514
logging trap informational

! OR Syslog over TLS (IOS-XE 17.2+, no UDP tunnel needed)
crypto pki trustpoint SYSLOG-TLS
 enrollment terminal
 revocation-check none

! Import CA certificate (copy/paste from your CA)
crypto pki authenticate SYSLOG-TLS

logging host <RECEIVER-IP> transport tls profile SYSLOG-TLS port 6514
```

### SNMP Traps

```
! SNMPv2c
snmp-server community netclaw-traps RO
snmp-server enable traps
snmp-server enable traps snmp linkdown linkup
snmp-server host <RECEIVER-IP> version 2c netclaw-traps udp-port 162

! OR SNMPv3 (more secure)
snmp-server group v3group v3 priv
snmp-server user admin v3group v3 auth sha authpass123 priv aes 128 privpass123
snmp-server enable traps
snmp-server host <RECEIVER-IP> version 3 priv admin udp-port 162
```

### Flexible NetFlow (IPFIX Export)

```
! Define flow record
flow record NETCLAW-RECORD
 match ipv4 source address
 match ipv4 destination address
 match ipv4 protocol
 match transport source-port
 match transport destination-port
 collect counter bytes
 collect counter packets
 collect timestamp sys-uptime first
 collect timestamp sys-uptime last

! Define flow exporter
flow exporter NETCLAW-EXPORTER
 destination <RECEIVER-IP>
 source Vlan1
 transport udp 2055
 export-protocol ipfix
 template data timeout 60

! Define flow monitor
flow monitor NETCLAW-MONITOR
 record NETCLAW-RECORD
 exporter NETCLAW-EXPORTER

! Apply to interface
interface GigabitEthernet1/0/1
 ip flow monitor NETCLAW-MONITOR input
 ip flow monitor NETCLAW-MONITOR output
```

---

## Testing

### Test Syslog Reception

```bash
# On Catalyst 9300, generate a log message
conf t
interface GigabitEthernet1/0/24
 description Test interface
 shutdown
 no shutdown
end

# Query received messages via MCP tool
# (via Claude or direct tool call)
```

Expected: `%LINK-3-UPDOWN` and `%LINEPROTO-5-UPDOWN` messages received.

### Test SNMP Trap Reception

```bash
# On Catalyst 9300, trigger a link trap
conf t
interface GigabitEthernet1/0/24
 shutdown
end

# Wait a few seconds, then bring it back up
conf t
interface GigabitEthernet1/0/24
 no shutdown
end

# Query traps via MCP tool
```

Expected: linkDown and linkUp traps with ifIndex and ifDescr varbinds.

### Test IPFIX Reception

```bash
# Generate traffic through monitored interface
# From a host connected to Gi1/0/1:
ping 8.8.8.8 -c 100
curl https://www.google.com

# Query flows via MCP tool
```

Expected: Flow records showing source/destination IPs, ports, bytes, and packets.

---

## Example Queries (via Claude/NetClaw)

Once data is flowing, ask questions like:

**Syslog:**
- "Show me critical syslog events from the last 5 minutes"
- "What errors occurred on switch-01 today?"
- "List all authentication failures"

**SNMP Traps:**
- "Show interface link events from the last hour"
- "Which interfaces had link flaps today?"
- "Show all SNMP traps from 10.1.1.1"

**IPFIX:**
- "What are the top 10 talkers by bytes?"
- "Show traffic to destination port 443"
- "What protocols are using the most bandwidth?"

**Cross-Receiver (Correlation):**
- "Show all events from router-01 in the last 10 minutes" (combines syslog + traps + flows)
- "What happened around the time interface Gi1/0/1 went down?"

---

## Troubleshooting

### Syslog messages not received

1. Verify UDP connectivity: `nc -u <receiver-ip> 514`
2. Check receiver is running: `syslog_get_status` tool
3. Verify Catalyst config: `show logging`
4. Check UDP tunnel is active

### SNMP traps not received

1. Verify community string matches
2. Check SNMPv3 credentials if using v3
3. Verify trap host config: `show snmp host`
4. Test with snmptrap command: `snmptrap -v 2c -c netclaw-traps <receiver-ip>:162 '' 1.3.6.1.6.3.1.1.5.1`

### IPFIX flows not received

1. Verify exporter destination IP
2. Check flow monitor is applied: `show flow monitor NETCLAW-MONITOR`
3. Verify template timeout: `show flow exporter NETCLAW-EXPORTER`
4. Ensure traffic is flowing through monitored interfaces

### ngrok not working

ngrok does NOT support UDP. Use Pinggy, LocalXpose, Tailscale, or Localtonet instead.

---

## Next Steps

1. Register receivers in `config/openclaw.json`
2. Create skills in `workspace/skills/` for common workflows
3. Update GAIT logging configuration
4. Configure alerting for critical events
