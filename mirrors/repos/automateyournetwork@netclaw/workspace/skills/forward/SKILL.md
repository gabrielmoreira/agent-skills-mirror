---
name: forward
description: "Read-only Forward Networks analysis through Forward's official MCP server: trace packet paths, look up devices, interfaces, VLANs, VRFs, hosts, cloud objects and subnet locations, check CVE exposure, summarize network complexity, and generate NQE queries. Use when a question is about what Forward's digital twin of the network says. Every call needs a networkId."
version: 2.0.0
license: Apache-2.0
author: forward
tags: [forward, digital-twin, nqe, paths, vulnerabilities]
mcp_servers: [forward-official-mcp]
metadata:
  openclaw:
    requires:
      env:
        - FORWARD_URL
        - FORWARD_AUTH_BASE64
---

# Forward Skill

**Skill**: `/forward`
**MCP Server**: `forward-official-mcp`
**Endpoint**: `<FORWARD_URL>/api/mcp` (streamable HTTP, served by Forward itself)

Forward builds a model of the network from collected configuration and state.
This skill queries that model through Forward's own MCP server. It reads
snapshots; it never touches a device and it cannot change Forward.

## Read-only, remote

`forward-official-mcp` is registered by URL in `config/openclaw.json`. There is
nothing to build or run locally. Authentication is a Forward API token sent as
HTTP Basic (`FORWARD_AUTH_BASE64` is the base64 of `accessKey:secret`).

Every tool Forward exposes over MCP is read-only. There is no tool to create,
change or delete anything, and none to collect, reprocess or delete snapshots.
Do not look for one. If the user asks for a change, say Forward's MCP cannot
make it and stop.

The token belongs to a real Forward user. The MCP reaches only the networks
and permissions that user has, so a tool can be listed and still be denied for
one network.

## Always supply a networkId

An MCP request carries no network context. **Every call needs `networkId`**
(required) and may take `snapshotId` (optional; omitted means the network's
latest processed snapshot).

**No tool lists networks or snapshots.** If the user has not given a network
ID, ask for it. Do not guess or iterate over IDs. Prefer an explicit
`snapshotId` when the user needs a repeatable answer or a before/after
comparison, and say which snapshot the answer came from.

## Tools

`tools/list` is the source of truth. Forward may add tools, and the list is
narrowed by license and by whether the organization has AI enabled. Read the
input schema there before the first call to a tool; do not guess argument names.

| User intent | Tool | Arguments (besides `networkId`, `snapshotId`) |
|-------------|------|-----------------------------------------------|
| "Can A reach B? Where does it fail?" | `get_paths` | `dstIp` (required) plus `srcIp` or `fromDevice` (one is required); optional `srcPort`, `dstPort` (strings, ranges like `8080-8088` allowed), `ipProto` (6 TCP, 17 UDP, 1 ICMP). `fromDevice` takes a device name only. Needs `VIEW_PATHS` |
| "Tell me about device X" | `get_device` | `deviceName` |
| "Tell me about interface Y" | `get_interface` | `deviceName`, `interfaceName` |
| "What is on VLAN N?" | `get_vlan` | `vlanId` (integer) |
| "What is in VRF V?" | `get_vrf` | `vrfName` |
| "Where is host H?" | `get_host` | `hostSpecifier` (name, cloud host ID, IP or MAC) |
| "What is this cloud resource?" | `get_cloud_object` | `objectId` |
| "Where does subnet S live?" | `get_subnet_locations` | `subnetAddress` (e.g. `10.0.0.0/24`) |
| "Which CVEs hit device X?" | `get_device_vulnerabilities` | `deviceName`; returns CVEs sorted by severity |
| "What is CVE-...?" | `get_vulnerability` | `cveId` |
| "How big is this network?" | `get_network_complexity` | none; returns exact counts: devices by vendor, type, model and OS version, plus VLANs, VRFs, ACLs, links and cloud objects |
| "Ask Forward a data question" | `nqe` | `prompt`: a complete, self-contained natural-language request. Forward writes and runs the query (needs `USE_NQE` and AI) |
| "Write an NQE query for..." | `generate_nqe_query` | `prompt`; returns a query without running it (needs `USE_NQE` and AI) |
| "How do I do X in NQE?" | `search_docs` | `query`: a self-contained search phrase; returns at most 2 documentation chunks (AI) |

These names come from `tools/list`; read it before the first call, because
Forward can change a tool's arguments.

Tools marked AI appear only when the organization has Forward AI enabled. If
`nqe` is absent from `tools/list`, say NQE is unavailable for this org; do not
work around it.

## Working rules

1. **Start narrow.** One call answers one object or one path. Chain calls for a
   bigger question (path, then the devices on it, then their CVEs).
2. **`get_paths` returns one path result**, not every possible path. It carries
   `forwardingOutcome`, `securityOutcome`, the `hops`, `totalHits` (which can be
   a lower bound), `timedOut`, and a `queryUrl` that opens the same trace in
   Forward. State the source, destination and snapshot, and give the link.
3. **`nqe` is generated, so check `status`.** The result has `query`,
   `summary`, `status` and, on success, an `executionKey` (the result key; the
   rows themselves are not returned, and the run reads at most 100 rows). Forward
   can generate a query that does not compile: then `status` is `INVALID_QUERY`,
   an `errors` field explains why, and the call still comes back as a normal
   result, not an error. Do not present a summary from an invalid query. Retry
   once with a clearer, more specific `prompt`; if it fails again, use
   `search_docs` or `generate_nqe_query`, show the user the query, and say it
   did not run.
4. **Treat the `nqe` summary as prose, not data.** It is written by a model and
   can be approximate (for example "more than 40 devices"). For an exact number
   use a `get_*` tool: `get_network_complexity` gives exact device, vendor, VLAN,
   VRF and link counts. Always show the generated `query` so the user can review
   it.
5. **Report the snapshot.** Results reflect a snapshot, not the live network.
   Several results carry the `snapshotId` they used; `get_paths` embeds it in
   `queryUrl`. Say which one, and that live state may differ.
6. **`get_device_vulnerabilities` lists every CVE it checked**, each with a
   `result`. Only `VULNERABLE` means the device is exposed; `NOT_VULNERABLE` rows
   are checked and clear. Count and report exposure from `VULNERABLE` rows only,
   by severity.
7. **Names match loosely, lookups can be empty.** Interface names match by alias
   (`Ethernet1` finds `et1`). A lookup that finds nothing (`get_vlan`,
   `get_host`) returns an empty list, not an error: say "not found in this
   snapshot". `get_vrf` and `get_subnet_locations` can return a long list; summarize
   it instead of pasting it.
8. **An error or an empty result is a finding.** Do not fill the gap from
   memory, and do not paste raw error text into tickets or chat; summarize it.

## Errors

Two kinds. HTTP errors come back before any tool runs; tool errors arrive as a
normal MCP result with `isError: true` and a plain-text message.

| Symptom | Meaning | What to tell the user |
|---------|---------|-----------------------|
| HTTP 403 on every call (the body says `MCP is not enabled for this organization`) | An admin turned off **Enable MCP server** for the org (Settings > System > Org preferences > Experimental features on self-hosted; Forward support on SaaS), or the license is expired/inactive | MCP is disabled for this org; an admin must re-enable it |
| HTTP 401 | The API token is wrong or revoked | Mint a new token at Settings > Account > API tokens and update `FORWARD_AUTH_BASE64` |
| HTTP 400, or 404, on a call after connecting | The endpoint is session-based: the call carried no MCP session id (400) or an unknown one (404) | Reconnect (run `initialize` again) and retry; a standard MCP client does this itself |
| `No processed snapshot for network N` | The network has no processed snapshot, **or** the ID does not exist (Forward gives the same message for both; the token may also lack access) | Check the ID and the token's access; do not try other IDs |
| `'networkId' is required` | The call omitted `networkId` | Ask the user for it |
| `Device 'X' not found in snapshot S` / `CVE-... not found in Snapshot S` | The object is not in that snapshot | Say so, with the snapshot; do not guess a near match |
| `Either 'fromDevice' or 'srcIp' must be specified` | `get_paths` was called with neither | Ask where the traffic starts |
| `The tool failed to execute` | Forward gave no detail (seen for a cloud object ID it could not find) | Say the lookup failed, check the ID, and try a different tool for the same object |
| A tool is missing from `tools/list` | Not licensed, or AI is not enabled for the org | Say it is unavailable here |

Clients that only support OAuth connectors (for example claude.ai custom
connectors) cannot connect; Forward authenticates with the static Basic header
only.

## Boundaries

This skill answers what Forward's model says. It does not:

- list networks or snapshots (ask the user for the ID);
- compare snapshots, list or run checks, read device configuration files, or
  show topology links as a list (the MCP has no such tool; say so);
- change anything in Forward or on a device;
- replace live device state. For what a device reports right now use the
  device-facing skills (`pyats-*`, `multivendor-device-query`).

## Safety

Never put the API token, its secret or `FORWARD_AUTH_BASE64` in repository
files, tickets or chat. They live in `~/.openclaw/.env`. Never print the
`Authorization` header. Treat the base64 value as the secret it is: it decodes
to the token.
