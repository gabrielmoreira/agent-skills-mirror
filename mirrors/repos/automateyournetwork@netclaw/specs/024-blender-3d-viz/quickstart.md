# Quickstart: Blender 3D Network Visualization

**Feature**: 024-blender-3d-viz
**Date**: 2026-04-05

## Prerequisites

- Windows 10/11 (for Blender GUI)
- WSL2 with NetClaw installed
- Internet connection (for addon download)
- Network devices with CDP/LLDP enabled (for topology data)

## Step 1: Install Blender on Windows

### Option A: Using winget (Recommended)
```powershell
# Open PowerShell as Administrator
winget install BlenderFoundation.Blender
```

### Option B: Direct Download
1. Go to https://www.blender.org/download/
2. Click "Download Blender" (Windows Installer 64-bit)
3. Run the installer, accept defaults

### Verify Installation
- Open Start Menu, search "Blender"
- Launch Blender - you should see the splash screen

## Step 2: Install the BlenderMCP Addon

### Download the Addon
1. Go to https://github.com/ahujasid/blender-mcp
2. Click on `addon.py` in the file list
3. Click the "Raw" button (top right of code view)
4. Right-click → "Save As" → save as `addon.py`

### Install in Blender
1. Open Blender
2. Go to **Edit → Preferences**
3. Click **Add-ons** in the left sidebar
4. Click **"Install..."** (top right)
5. Navigate to your downloaded `addon.py`
6. Select it and click **"Install Add-on"**
7. **Check the checkbox** next to "Interface: Blender MCP"
8. Close Preferences

## Step 3: Start the Blender Connection

1. In Blender's main 3D viewport, press **N** on your keyboard
   - This opens the right sidebar
2. Look for the **"BlenderMCP"** tab in the sidebar
3. Click on it to expand
4. Click **"Connect to Claude"**
5. You should see: "Server running on port 9876"

**Keep Blender open with this connection active!**

## Step 4: Configure NetClaw for Windows Connection

```bash
# In WSL terminal, get your Windows host IP
WIN_IP=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')
echo "Your Windows IP is: $WIN_IP"

# Add to your .env file
cd /path/to/netclaw
echo "" >> .env
echo "# Blender MCP Connection" >> .env
echo "BLENDER_HOST=$WIN_IP" >> .env
echo "BLENDER_PORT=9876" >> .env

# Verify
grep BLENDER .env
```

## Step 5: Test the Connection

### Start NetClaw
```bash
cd /path/to/netclaw
netclaw
```

### Test Basic Command
```
You: Create a blue cube in Blender
```

You should see:
1. NetClaw processes the command
2. A blue cube appears in Blender's 3D viewport

### Test Scene Query
```
You: What objects are in the Blender scene?
```

## Step 6: Draw Network Topology

### Prerequisite: Have CDP/LLDP Data Available
First, query your network devices:
```
You: Show CDP neighbors for core-rtr-01
```

### Visualize the Topology
```
You: Draw the network topology in Blender using the CDP data
```

NetClaw will:
1. Parse the CDP neighbor relationships
2. Create 3D objects for each device
3. Color them by type (routers=blue, switches=green)
4. Connect neighbors with visual links
5. Position devices in a readable layout

### Customize
```
You: Color the firewalls red
You: Add labels to all devices
```

### Export
```
You: Export the Blender scene as topology.png
```

## Troubleshooting

### "Connection refused" error
- **Check**: Is Blender running?
- **Check**: Did you click "Connect to Claude" in Blender?
- **Check**: Is the BlenderMCP tab showing "Server running"?

### First command times out
- This is normal - the first command often times out
- Just retry the same command
- Subsequent commands should work faster

### Can't find BlenderMCP tab in Blender
- Press 'N' to show the right sidebar
- Go to Edit → Preferences → Add-ons
- Search for "Blender MCP" and ensure it's checked

### WSL can't reach Windows
```bash
# Verify Windows IP
cat /etc/resolv.conf | grep nameserver

# Test connectivity
ping -c 1 $WIN_IP

# Check if port 9876 is blocked
# On Windows: Check Windows Defender Firewall
```

### Blender crashes or freezes
- Complex commands may overwhelm Blender
- Save your work before running new commands
- Try breaking complex operations into smaller steps
- Restart Blender and reconnect if needed

### "Topology truncated" warning
- Your network has more than 25 devices
- Only the 25 most-connected devices are rendered
- Use filtering or query a smaller segment

## Example Workflow

```
# 1. Start with a fresh scene
You: Clear the Blender scene

# 2. Get network data
You: Show CDP neighbors for distribution layer switches

# 3. Visualize
You: Draw this topology in Blender

# 4. Enhance
You: Color the core routers dark blue
You: Add hostname labels to each device

# 5. Export for documentation
You: Export the scene as network-topology.png

# 6. Save Blender file (optional)
You: Tell me how to save the Blender file
```

## Next Steps

- Explore more complex topologies
- Try different color schemes
- Export videos for presentations
- Combine with Grafana metrics for health visualization
