---
name: minecraft-modpack-server
description: "Sets up CurseForge/Modrinth NeoForge or Forge Minecraft server packs: Java match, server.properties, JVM args, backups, firewall. Use when hosting a modded Minecraft server or troubleshooting start/kick issues. Not for vanilla-only servers without a pack, Windows-native hosting (Linux/macOS skill), or client-side modpack install."
version: 1.0.1
tags: [minecraft, gaming, server, neoforge, forge, modpack]
platforms: [linux, macos]
---

# Minecraft Modpack Server Setup

## When to Use

Use this skill when the user wants to:
- Set up a modded Minecraft server from a server pack zip (CurseForge, Modrinth)
- Configure NeoForge or Forge server settings
- Tune Minecraft server performance (JVM args, view distance, simulation distance)
- Set up automated world backups for a Minecraft server
- Troubleshoot a modded server that won't start or kicks players

Trigger keywords: minecraft server, modpack server, neoforge, forge, server.properties, user_jvm_args, server pack, modded minecraft, ATM, all the mods, enigmatica, create above and beyond.

## Prerequisites

- A Linux or macOS host with sufficient RAM (minimum 16 GB for 100+ mod packs; 32 GB+ for 200+ mod packs)
- Sudo access for package installation and firewall configuration
- A server pack zip URL or local file (from CurseForge or Modrinth)
- The user's preferences gathered before generating configs (see step 1)

## Procedure

### 1. Gather User Preferences

Before generating any configuration, ask the user for the following. Use sensible defaults only if the user explicitly says they don't care:

| Preference | Options | Default if unspecified |
|---|---|---|
| Server name / MOTD | Free text | "Minecraft Server" |
| Seed | Specific seed or random | Random |
| Difficulty | peaceful / easy / normal / hard | hard |
| Gamemode | survival / creative / adventure | survival |
| Online mode | true (Mojang auth) or false (LAN/cracked) | true |
| Player count | Number of expected players | 4 |
| RAM allocation | GB or let agent decide | Agent decides based on mod count |
| View / simulation distance | Specific or let agent pick | Agent picks based on player count |
| PvP | on or off | on |
| Whitelist | Open or whitelist only | Open |
| Backups | Automated? How often? | Hourly, keep 24 |

### 2. Download and Inspect the Pack

```bash
mkdir -p ~/minecraft-server
cd ~/minecraft-server
wget -O serverpack.zip "<URL>"
unzip -o serverpack.zip -d server
ls server/
```

Look for these files in the extracted directory:
- `startserver.sh` — the pack's launch script (read it to determine mod loader type, version, and required Java version)
- Installer jar (e.g., `neoforge-*-installer.jar` or `forge-*-installer.jar`)
- `user_jvm_args.txt` — JVM argument template
- `mods/` folder — contains all mod jars

Check the start script to determine the mod loader type, version, and required Java version:
```bash
cat ~/minecraft-server/server/startserver.sh
```

### 3. Install Java

Match the Java version to the Minecraft version:

| Minecraft Version | Java Version | Install Command |
|---|---|---|
| 1.21+ | Java 21 | `sudo apt install openjdk-21-jre-headless` |
| 1.18–1.20 | Java 17 | `sudo apt install openjdk-17-jre-headless` |
| 1.16 and below | Java 8 | `sudo apt install openjdk-8-jre-headless` |

Verify the installation:
```bash
java -version
```

### 4. Install the Mod Loader

Most server packs include an install script. Use the `INSTALL_ONLY` environment variable to install libraries without launching the server:

```bash
cd ~/minecraft-server/server
ATM10_INSTALL_ONLY=true bash startserver.sh
```

For generic Forge packs without an install script:
```bash
java -jar forge-*-installer.jar --installServer
```

This downloads libraries, patches the server jar, and generates the args files needed for launch.

Some packs use pack-specific env vars to control behavior. For example, ATM10 uses:
- `ATM10_JAVA` — path to Java executable
- `ATM10_RESTART` — enable/disable auto-restart loop
- `ATM10_INSTALL_ONLY` — install only, don't launch

Check the pack's `startserver.sh` for pack-specific variables.

### 5. Accept the EULA

```bash
echo "eula=true" > ~/minecraft-server/server/eula.txt
```

### 6. Configure server.properties

Key settings for modded servers:

```properties
motd=\u00a7b\u00a7lServer Name \u00a7r\u00a78| \u00a7aModpack Name
server-port=25565
online-mode=true
enforce-secure-profile=true
difficulty=hard
allow-flight=true
spawn-protection=0
max-tick-time=180000
enable-command-block=true
```

**HARD RULES for modded server.properties:**
- `allow-flight=true` is REQUIRED — mods with jetpacks, flight rings, or flying mounts will kick players without it
- `max-tick-time=180000` or higher — modded servers often have long ticks during worldgen; the default 60000 will crash the server
- If `online-mode=false`, you MUST also set `enforce-secure-profile=false` or clients get rejected
- `spawn-protection=0` lets all players build at spawn (most modpacks expect this)

Performance settings — scale to hardware and player count:

```properties
# 2 players, beefy machine:
view-distance=16
simulation-distance=10

# 4-6 players, moderate machine:
view-distance=10
simulation-distance=6

# 8+ players or weaker hardware:
view-distance=8
simulation-distance=4
```

### 7. Tune JVM Args (user_jvm_args.txt)

Scale RAM to player count and mod count. Rule of thumb for modded:

| Mod Count | Recommended RAM | Minimum Free for OS |
|---|---|---|
| 100–200 mods | 6–12 GB | 8 GB |
| 200–350+ mods | 12–24 GB | 8 GB |

Write the JVM args file:
```bash
cat > ~/minecraft-server/server/user_jvm_args.txt << 'EOF'
-Xms12G
-Xmx24G
-XX:+UseG1GC
-XX:+ParallelRefProcEnabled
-XX:MaxGCPauseMillis=200
-XX:+UnlockExperimentalVMOptions
-XX:+DisableExplicitGC
-XX:+AlwaysPreTouch
-XX:G1NewSizePercent=30
-XX:G1MaxNewSizePercent=40
-XX:G1HeapRegionSize=8M
-XX:G1ReservePercent=20
-XX:G1HeapWastePercent=5
-XX:G1MixedGCCountTarget=4
-XX:InitiatingHeapOccupancyPercent=15
-XX:G1MixedGCLiveThresholdPercent=90
-XX:G1RSetUpdatingPauseTimePercent=5
-XX:SurvivorRatio=32
-XX:+PerfDisableSharedMem
-XX:MaxTenuringThreshold=1
EOF
```

Adjust `-Xms` and `-Xmx` based on the RAM table above. Always leave at least 8 GB free for the OS and other tasks.

### 8. Open Firewall

```bash
sudo ufw allow 25565/tcp comment "Minecraft Server"
```

Verify:
```bash
sudo ufw status | grep 25565
```

### 9. Create a Clean Launch Script

The pack's `startserver.sh` often has an auto-restart loop. Create a clean launch script without it:

```bash
cat > ~/start-minecraft.sh << 'EOF'
#!/bin/bash
cd ~/minecraft-server/server
java @user_jvm_args.txt @libraries/net/neoforged/neoforge/<VERSION>/unix_args.txt nogui
EOF
chmod +x ~/start-minecraft.sh
```

For Forge (not NeoForge), the args file path differs. Check `startserver.sh` for the exact path — it is typically `@libraries/net/minecraftforge/forge/<VERSION>/unix_args.txt`.

### 10. Set Up Automated Backups

Create the backup script:

```bash
cat > ~/minecraft-server/backup.sh << 'SCRIPT'
#!/bin/bash
SERVER_DIR="$HOME/minecraft-server/server"
BACKUP_DIR="$HOME/minecraft-server/backups"
WORLD_DIR="$SERVER_DIR/world"
MAX_BACKUPS=24
mkdir -p "$BACKUP_DIR"
[ ! -d "$WORLD_DIR" ] && echo "[BACKUP] No world folder" && exit 0
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_FILE="$BACKUP_DIR/world_${TIMESTAMP}.tar.gz"
echo "[BACKUP] Starting at $(date)"
tar -czf "$BACKUP_FILE" -C "$SERVER_DIR" world
SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
echo "[BACKUP] Saved: $BACKUP_FILE ($SIZE)"
BACKUP_COUNT=$(ls -1t "$BACKUP_DIR"/world_*.tar.gz 2>/dev/null | wc -l)
if [ "$BACKUP_COUNT" -gt "$MAX_BACKUPS" ]; then
    REMOVE=$((BACKUP_COUNT - MAX_BACKUPS))
    ls -1t "$BACKUP_DIR"/world_*.tar.gz | tail -n "$REMOVE" | xargs rm -f
    echo "[BACKUP] Pruned $REMOVE old backup(s)"
fi
echo "[BACKUP] Done at $(date)"
SCRIPT
chmod +x ~/minecraft-server/backup.sh
```

Add hourly cron job:

```bash
(crontab -l 2>/dev/null | grep -v "minecraft/backup.sh"; echo "0 * * * * $HOME/minecraft-server/backup.sh >> $HOME/minecraft-server/backups/backup.log 2>&1") | crontab -
```

### 11. First Launch

```bash
~/start-minecraft.sh
```

First startup is SLOW — several minutes for big packs. Do not panic. "Can't keep up!" warnings on first launch are normal and settle after initial chunk generation completes.

## Pitfalls

1. **`allow-flight=true` is mandatory for modded** — mods with jetpacks, flight rings, or flying mounts will kick players without it. Never set this to false on a modded server.

2. **`max-tick-time` must be 180000 or higher** — modded servers often have long ticks during worldgen. The vanilla default of 60000 will crash the server on first load with large modpacks.

3. **First startup is very slow** — several minutes for big packs. Do not kill the process thinking it's hung. Wait for "Done!" in the log.

4. **"Can't keep up!" warnings are normal on first launch** — these settle after initial chunk generation completes.

5. **`online-mode=false` requires `enforce-secure-profile=false`** — if you set one without the other, clients get rejected with cryptic errors.

6. **The pack's `startserver.sh` often has an auto-restart loop** — always create a clean launch script (step 9) without the restart loop for production use.

7. **Delete the `world/` folder to regenerate with a new seed** — changing `level-seed` in `server.properties` only affects new chunks, not existing worlds.

8. **Pack-specific env vars** — some packs have env vars that control behavior (e.g., ATM10 uses `ATM10_JAVA`, `ATM10_RESTART`, `ATM10_INSTALL_ONLY`). Always read `startserver.sh` to find these.

9. **Forge vs NeoForge args paths differ** — NeoForge uses `@libraries/net/neoforged/neoforge/<VERSION>/unix_args.txt`; Forge uses `@libraries/net/minecraftforge/forge/<VERSION>/unix_args.txt`. Check `startserver.sh` for the exact path.

10. **Never allocate more RAM than physically available minus 8 GB** — the OS and other processes need headroom. Oversubscribing RAM causes swap thrashing and worse performance than under-allocating.

## Verification

1. **Check if the server process is running:**
   ```bash
   pgrep -fa neoforge
   # or
   pgrep -fa minecraft
   ```

2. **Monitor server logs in real time:**
   ```bash
   tail -f ~/minecraft-server/server/logs/latest.log
   ```

3. **Confirm server is ready** — look for this line in the log:
   ```
   Done (Xs)! For help, type "help"
   ```
   This means the server is accepting connections.

4. **Test player connection** — add the server IP in Minecraft Multiplayer and verify it appears in the server list with the correct MOTD.

5. **Verify firewall is open:**
   ```bash
   sudo ufw status | grep 25565
   ```
   Expected output:
   ```
   25565/tcp                  ALLOW       Anywhere                   # Minecraft Server
   ```

6. **Verify backups are working:**
   ```bash
   ls -lh ~/minecraft-server/backups/
   ```
   Should show `world_YYYY-MM-DD_HH-MM-SS.tar.gz` files.

7. **Verify cron is scheduled:**
   ```bash
   crontab -l | grep backup
   ```
   Expected output:
   ```
   0 * * * * /home/<user>/minecraft-server/backup.sh >> /home/<user>/minecraft-server/backups/backup.log 2>&1
   ```
