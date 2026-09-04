# Quickstart: Federated AI-Augmented Network Topology Visualization

**Feature**: 121-federated-topology-viz

## Prerequisites

- Spec 120 (`comfyui-topology-viz`) already merged and deployed — this feature extends it, does not
  replace it.
- `johns-risk/viz` federation member reachable (verify below — research.md R1 found it already live
  at planning time, but implementation must re-verify, not assume).
- ComfyUI reachable at `COMFYUI_URL` from the same host `johns-risk/viz` runs on (already true per
  spec 120's WSL2 mirrored-networking finding).

## 1. Verify the structural-diagram member is live (FR-007/SC-004)

```bash
# Via the n2n-mcp tool, same one Border's own skill code will call:
python3 $MCP_CALL "python3 mcp-servers/n2n-mcp/server.py" n2n_member_health '{"member_id":"johns-risk/viz"}'
```
Expect `state: "active"`, a live channel, recent `last_seen`. If not live:

**Confirmed live** (2026-08-30, `GET /n2n/members`):
```json
{"member_id": "johns-risk/viz", "state": "active", "live": true,
 "skills": [..., "topology-diagram-mcp/render_structural", "image-style-mcp/style_image"]}
```
```bash
systemctl --user start netclaw-member-johns-risk-viz.service
systemctl --user status netclaw-member-johns-risk-viz.service
```

## 2. Register and deploy the two new MCP servers

```bash
# Both new servers live under mcp-servers/, registered like any other (Constitution XI):
openclaw mcp set topology-diagram-mcp '{"command":"python3","args":["mcp-servers/topology-diagram-mcp/server.py"],"cwd":"/home/johncapobianco/netclaw"}'
openclaw mcp set image-style-mcp '{"command":"python3","args":["mcp-servers/image-style-mcp/server.py"],"cwd":"/home/johncapobianco/netclaw","env":{"COMFYUI_URL":"${COMFYUI_URL}"}}'
```

## 3. Grant `johns-risk/viz` the two new tool capabilities

Extend its `scope` (federation.db `member` row) with:
```json
{"name": "topology-diagram-mcp/render_structural", "type": "tool", "tier": "specialty"}
{"name": "image-style-mcp/style_image", "type": "tool", "tier": "specialty"}
```

## 4. Raise the federation tool-call timeout (research.md R7)

In Border's own service env AND `migration-staging/members/viz/.env`:
```
N2N_TOOL_TIMEOUT_S=600
```
Restart both the Border daemon and `netclaw-member-johns-risk-viz.service` after the change.

## 5. Run a request end to end

Same conversational entry point as spec 120 — no new command (FR-004a):

> "give me a stylized image of the CML lab topology"

Expected behavior:
- Snapshot is non-freeform → federated path attempted.
- `johns-risk/viz` reachable → `render_structural` called, returns a correct, real-icon,
  correctly-labeled diagram.
- `image-style-mcp/style_image` called on that diagram → styled image returned.
- Response indicates `generation_path: "federated"`, `structural_member` and `styling_member`
  both `"johns-risk/viz"`.

## 6. Verify fallback still works unchanged (FR-009/FR-012)

```bash
systemctl --user stop netclaw-member-johns-risk-viz.service
```
Repeat the same request. Expected: a real image is still produced via spec 120's unmodified
pipeline, `generation_path: "fallback"`, `reason: "johns-risk/viz unreachable"`.

## 7. Verify freeform still routes directly to fallback (FR-011)

> "sketch a topology where core1 connects to a switch called sw1"

Expected: `generation_path: "fallback"`, `reason: "freeform request"`, federated path never
attempted (no wasted round trip to a member that has no real device data to render).
