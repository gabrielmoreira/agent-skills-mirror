# Blender 3D Network Visualization

**MCP Server**: blender-mcp (community)
**Category**: Visualization
**Status**: Active

## Overview

Enables 3D network topology visualization in Blender. Network engineers can request topology drawings via natural language, and NetClaw translates CDP/LLDP neighbor data into 3D rendering commands sent to a locally-running Blender instance.

## Prerequisites

1. **Blender** installed on Windows (v3.0+)
2. **BlenderMCP addon** installed and connected (port 9876)
3. **WSL connectivity** to Windows host (BLENDER_HOST environment variable)

See `quickstart.md` in this directory for detailed setup instructions.

## Available MCP Tools

| Tool | Description |
|------|-------------|
| `get_scene_info` | Returns current Blender scene objects |
| `create_object` | Creates primitives (cube, sphere, cylinder) |
| `modify_object` | Transform position/rotation/scale |
| `set_material` | Apply colors and materials |
| `execute_blender_code` | Run arbitrary Python in Blender |

## User Story 1: Draw Network Topology (P1 - MVP)

**Goal**: Draw the network topology using CDP data in 3D

### Example Queries

```
"Draw the network topology in Blender using CDP data"
"Visualize the CDP neighbors for core-rtr-01 in 3D"
"Create a 3D network diagram from the LLDP data"
"Show me the network topology in Blender"
```

### Workflow

1. User requests topology visualization
2. NetClaw queries CDP/LLDP neighbor data (pyATS or SuzieQ)
3. Extract device hostnames and neighbor relationships
4. Infer device types from hostnames:
   - Contains "rtr" or "router" = Router (blue)
   - Contains "sw" or "switch" = Switch (green)
   - Contains "fw" or "firewall" or "asa" = Firewall (red)
   - Contains "ap" or "wap" or "wireless" = Access Point (yellow)
   - Otherwise = Unknown (gray)
5. Calculate layout positions (force-directed)
6. Clear Blender scene
7. Create cubes for each device at calculated positions
8. Apply colors based on device type
9. Create cylinders between connected devices
10. Report completion with device count

### Device Color Mapping

| Device Type | Color | RGB |
|-------------|-------|-----|
| Router | Blue | (0.2, 0.4, 0.8) |
| Switch | Green | (0.2, 0.7, 0.3) |
| Firewall | Red | (0.8, 0.2, 0.2) |
| Access Point | Yellow | (0.9, 0.8, 0.2) |
| Unknown | Gray | (0.5, 0.5, 0.5) |

### Device Limit

Maximum 25 devices rendered. If topology exceeds limit:
- Sort devices by neighbor count (most connected first)
- Render first 25 devices
- Display warning: "Topology truncated: showing 25 of N devices"

### Error Handling

| Condition | User Message |
|-----------|--------------|
| Blender not running | "Blender connection unavailable. Please start Blender and click 'Connect to Claude' in the BlenderMCP panel." |
| Addon not connected | "Blender addon not connected. Press 'N' in Blender to show the sidebar, find the BlenderMCP tab, and click 'Connect to Claude'." |
| No CDP data | "No CDP/LLDP neighbor data available. Query network devices first (e.g., 'show CDP neighbors for core-rtr-01')." |
| Connection timeout | "First command may timeout - this is normal. Please retry the same command." |

## User Story 2: Export Visualization (P2)

**Goal**: Export the 3D topology as PNG or video

### Example Queries

```
"Export the Blender scene as topology.png"
"Save the network diagram as a PNG file"
"Render the topology to an image"
"Export the 3D view as network-topology.png"
```

### PNG Export Workflow

Uses `execute_blender_code` to run:

```python
import bpy
# Set render settings
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.filepath = "/tmp/topology.png"
bpy.context.scene.render.image_settings.file_format = 'PNG'
# Render
bpy.ops.render.render(write_still=True)
```

### Video Export Workflow (If Supported)

```python
import bpy
bpy.context.scene.render.filepath = "/tmp/topology.mp4"
bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
bpy.context.scene.render.ffmpeg.format = 'MPEG4'
bpy.context.scene.render.ffmpeg.codec = 'H264'
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 120
bpy.ops.render.render(animation=True)
```

### Export Error Handling

| Condition | User Message |
|-----------|--------------|
| Blender minimized | "Export failed. Ensure Blender window is visible (not minimized)." |
| Invalid path | "Export failed: Invalid file path. Use a simple filename like 'topology.png'." |
| Render timeout | "Export taking longer than expected. Check Blender for progress." |

## User Story 3: Customize Visualization (P3)

**Goal**: Customize colors, add labels, highlight devices

### Example Queries - Color Customization

```
"Color router-1 red"
"Make all switches purple"
"Change the color of the firewalls to orange"
"Set router-core to bright blue"
```

### Example Queries - Labels

```
"Add labels to all devices"
"Label each device with its hostname"
"Add text labels showing device names"
```

### Example Queries - Highlighting

```
"Highlight router-1"
"Make core-rtr-01 stand out"
"Emphasize the firewalls"
```

### Color Customization Workflow

Uses `set_material` tool:

```json
{
  "object_name": "router-1",
  "color": [0.8, 0.2, 0.2],
  "metallic": 0.3,
  "roughness": 0.7
}
```

### Add Labels Workflow

Uses `execute_blender_code`:

```python
import bpy

# For each device object
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        # Add text above the device
        bpy.ops.object.text_add(location=(obj.location.x, obj.location.y, obj.location.z + 1))
        text_obj = bpy.context.active_object
        text_obj.data.body = obj.name
        text_obj.scale = (0.3, 0.3, 0.3)
        # Face the camera
        text_obj.rotation_euler = (1.5708, 0, 0)
```

### Highlighting Workflow

Uses combination of `set_material` (bright color) and `modify_object` (scale up):

```json
{
  "object_name": "router-1",
  "color": [1.0, 0.8, 0.0],
  "metallic": 0.8,
  "roughness": 0.2
}
```

```json
{
  "name": "router-1",
  "scale": [0.7, 0.7, 0.7]
}
```

## Scene Management

### Clear Scene

```
"Clear the Blender scene"
"Reset the 3D view"
"Remove all objects from Blender"
```

Uses `execute_blender_code`:

```python
import bpy
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
```

### Query Scene

```
"What objects are in the Blender scene?"
"List the devices in Blender"
"Show the current 3D scene contents"
```

Uses `get_scene_info` tool.

## Natural Language to MCP Tool Mapping

| Natural Language | MCP Tool(s) |
|------------------|-------------|
| "Draw the topology" | execute_blender_code (clear) + create_object (N times) + set_material (N times) |
| "Color device-X red" | set_material |
| "Add labels" | execute_blender_code |
| "Export as PNG" | execute_blender_code |
| "What's in the scene?" | get_scene_info |
| "Clear the scene" | execute_blender_code |
| "Highlight device-X" | set_material + modify_object |

## Troubleshooting

### Connection Issues

1. **Verify Blender is running** on Windows
2. **Check addon is connected**: Press 'N' in Blender, find BlenderMCP tab, verify "Server running on port 9876"
3. **Get Windows IP from WSL**:
   ```bash
   cat /etc/resolv.conf | grep nameserver | awk '{print $2}'
   ```
4. **Test connectivity**:
   ```bash
   ping -c 1 $WIN_IP
   ```

### Performance Issues

- **Large topologies**: Only 25 devices rendered (by design)
- **Slow rendering**: Normal for first command; subsequent commands faster
- **Blender freezes**: Save work, restart Blender, reconnect addon

## Related Skills

- `pyats-run` - Query CDP/LLDP neighbor data from live devices
- `suzieq-show` - Query network state from SuzieQ observability platform
- `canvas-a2ui` - Alternative 2D visualization in chat
