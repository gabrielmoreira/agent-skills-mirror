---
name: network-service-discovery
description: Port and service enumeration for web targets including nmap, naabu, and HTTP multi-port probing
---

# Network Service Discovery

## When to Use
Map the services running on the target host(s) before vulnerability testing. Focus on the web ports plus any service that might expose an attack surface.

## Methodology

### Fast Port Scan (Default)
```bash
nmap -sV -sC -T2 --top-ports 200 --open -oN tmp/nmap_top200.txt TARGET
```
Rate-safe: `--max-rate 10 --scan-delay 100ms` when the target is production.

### Focused Web-Port Probe (when nmap unavailable)
```bash
for port in 80 443 8080 8443 8000 3000 5000 9000; do
  code=$(curl -sk -o /dev/null -w "%{http_code}" --max-time 5 "https://TARGET:$port/" 2>/dev/null)
  [ "$code" != "000" ] && echo "[PORT $port] HTTP $code"
done
```

### Deep Port Scan (Deep mode only)
```bash
nmap -sV -p- --open --max-rate 10 --scan-delay 200ms -oN tmp/nmap_full.txt TARGET
```
Only when the methodology demands full port coverage. Split into ranges if needed.

## Stopping Criteria
- Default: top-200 ports scanned (or equivalent multi-port HTTP probe)
- Deep: full port range for the primary host
- Do NOT re-run on the same host without a specific reason

## Common Misses
- UDP services (DNS, SNMP) — check 53, 161 for internal targets
- Non-standard HTTP ports (3000-9999 range)
- Services behind load balancers that only forward specific ports
- Admin panels on alternate ports (8080, 8443, 9090)

## Handoff
Produce a list of `host:port:service` for the Endpoint Inventory. Mark which services are web-based vs raw TCP.
