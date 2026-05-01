#!/usr/bin/env python3
# pyright: reportMissingTypeArgument=false, reportUnknownParameterType=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnusedImport=false, reportUnusedCallResult=false, reportArgumentType=false, reportOptionalMemberAccess=false, reportOptionalIterable=false, reportAttributeAccessIssue=false
"""Parse Cisco switch log files into devices.json and topology.json."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path


PROMPT_CMD_RE = re.compile(r"^(?P<host>[^#\s]+(?:\([^\)]*\))?)#\s*(?P<cmd>.*)$")


def warn(warnings: list[str], message: str) -> None:
    warnings.append(message)


def read_log(file_path: Path) -> list[str]:
    content = file_path.read_text(encoding="utf-8-sig", errors="replace")
    return content.splitlines()


def canonical_command(cmd_text: str) -> str | None:
    cmd = cmd_text.strip().lower()
    if not cmd:
        return None
    if cmd.startswith("show version") or cmd.startswith("sh version"):
        return "show version"
    if cmd.startswith("show inv") or cmd.startswith("show inventory") or cmd.startswith("sh inv"):
        return "show inventory"
    if cmd.startswith("show vlan") or cmd.startswith("sh vlan"):
        return "show vlan brief"
    if "cdp" in cmd and "nei" in cmd and "detail" in cmd:
        return "show cdp nei detail"
    if "cdp" in cmd and "nei" in cmd:
        return "show cdp nei"
    if "int" in cmd and "description" in cmd:
        return "show int description"
    if "interface" in cmd and "description" in cmd:
        return "show int description"
    if "int" in cmd and "status" in cmd:
        return "show int status"
    if "interface" in cmd and "status" in cmd:
        return "show int status"
    if cmd.startswith("show run") or cmd.startswith("show running") or cmd.startswith("sh run"):
        return "show running-config"
    if cmd.startswith("show ip") and ("inter" in cmd or "int" in cmd) and (
        "bri" in cmd or "brief" in cmd
    ):
        return "show ip int brief"
    if "trunk" in cmd and ("show inter" in cmd or "show int" in cmd or "show interface" in cmd):
        return "show inter trunk"
    return None


def parse_command_sections(lines: list[str]) -> list[dict]:
    sections: list[dict] = []
    current: dict | None = None

    for line in lines:
        match = PROMPT_CMD_RE.match(line)
        if match:
            if current:
                sections.append(current)
                current = None
            cmd_text = match.group("cmd").strip()
            if not cmd_text:
                continue
            cmd_key = canonical_command(cmd_text)
            if cmd_key:
                current = {
                    "cmd": cmd_key,
                    "raw_cmd": cmd_text,
                    "hostname": match.group("host"),
                    "lines": [],
                }
            else:
                current = None
            continue

        if current:
            current["lines"].append(line)

    if current:
        sections.append(current)

    return sections


def normalize_device_id(device_id: str) -> str:
    base = device_id.strip()
    base = re.sub(r"\(.*\)$", "", base)
    if "." in base:
        base = base.split(".", 1)[0]
    return base


def normalize_interface_name(name: str) -> str:
    if not name:
        return name
    raw = name.strip()
    if not re.search(r"\d", raw):
        return raw
    compact = re.sub(r"\s+", "", raw)
    match = re.match(r"^([A-Za-z]+)([\d/].*)$", compact)
    if not match:
        return compact
    prefix, rest = match.groups()
    prefix_map = {
        "Gi": "GigabitEthernet",
        "Gig": "GigabitEthernet",
        "Te": "TenGigabitEthernet",
        "Ten": "TenGigabitEthernet",
        "Fa": "FastEthernet",
        "Eth": "Ethernet",
        "Po": "Port-channel",
        "Vl": "Vlan",
    }
    full_prefix = prefix_map.get(prefix, prefix)
    return f"{full_prefix}{rest}"


def default_interface_config() -> dict:
    return {
        "switchport_mode": None,
        "switchport_access_vlan": None,
        "switchport_trunk_allowed_vlans": None,
        "switchport_voice_vlan": None,
        "switchport_trunk_native_vlan": None,
        "description": None,
        "shutdown": False,
        "spanning_tree_portfast": False,
        "speed": None,
        "channel_group": None,
        "ip_address": None,
    }


def ensure_interface(interfaces: dict, name: str) -> dict:
    normalized = normalize_interface_name(name)
    if normalized not in interfaces:
        interfaces[normalized] = {
            "description": None,
            "oper_status": None,
            "protocol": None,
            "vlan": None,
            "duplex": None,
            "speed": None,
            "media_type": None,
            "config": default_interface_config(),
        }
    return interfaces[normalized]


def parse_show_version(section: dict) -> dict:
    lines = section.get("lines", [])
    hostname = section.get("hostname")
    ios_version = None
    uptime = None
    serial_number = None
    model = None
    platform_type = None

    # Try to extract a meaningful version string
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        # NX-OS: look for kickstart or system version
        m = re.match(r"^\s*(?:kickstart|system):\s*version\s+(.+)", stripped, re.IGNORECASE)
        if m:
            ios_version = m.group(1).strip()
            break
        # IOS / IOS-XE: look for "Cisco IOS Software" or "Cisco IOS XE Software" line
        if "Cisco IOS" in stripped and "Version" in stripped:
            ios_version = stripped
            break

    for line in lines:
        if platform_type is None:
            if "Nexus Operating System" in line or "NX-OS" in line:
                platform_type = "NX-OS"
            elif "IOS XE" in line or "IOS-XE" in line:
                platform_type = "IOS-XE"
            elif "Cisco IOS Software" in line:
                platform_type = "IOS"

        if uptime is None:
            match = re.search(r"\buptime is (.+)", line, re.IGNORECASE)
            if match:
                uptime = match.group(1).strip()
            else:
                match = re.search(r"Kernel uptime is (.+)", line, re.IGNORECASE)
                if match:
                    uptime = match.group(1).strip()

        if serial_number is None:
            match = re.search(r"System serial number\s*[: ]\s*(\S+)", line, re.IGNORECASE)
            if match:
                serial_number = match.group(1).strip()
            else:
                match = re.search(r"Processor\s+Board\s+ID\s+(\S+)", line, re.IGNORECASE)
                if match:
                    serial_number = match.group(1).strip()

        if model is None:
            match = re.search(r"^cisco\s+(\S+)", line, re.IGNORECASE)
            if match and ("processor" in line.lower() or "chassis" in line.lower()):
                model = match.group(1).strip()
            else:
                match = re.search(r"Model Number\s*:\s*(\S+)", line, re.IGNORECASE)
                if match:
                    model = match.group(1).strip()

    if platform_type is None:
        platform_type = "IOS"

    return {
        "hostname": hostname,
        "ios_version": ios_version,
        "uptime": uptime,
        "serial_number": serial_number,
        "model": model,
        "platform_type": platform_type,
    }


def parse_inventory(sections: list[dict]) -> dict:
    entries = []
    for section in sections:
        current = None
        for line in section.get("lines", []):
            if "NAME:" in line and "DESCR:" in line:
                name_match = re.search(r"NAME:\s*\"([^\"]+)\"", line)
                descr_match = re.search(r"DESCR:\s*\"([^\"]+)\"", line)
                current = {
                    "name": name_match.group(1).strip() if name_match else None,
                    "description": descr_match.group(1).strip() if descr_match else None,
                }
                continue
            if current and "PID:" in line:
                pid_match = re.search(r"PID:\s*([^,]+)", line)
                sn_match = re.search(r"SN:\s*([^,\s]+)", line)
                current["pid"] = pid_match.group(1).strip() if pid_match else None
                current["sn"] = sn_match.group(1).strip() if sn_match else None
                entries.append(current)
                current = None

    sfp_modules = []
    for entry in entries:
        name = entry.get("name") or ""
        if not re.search(r"\d", name):
            continue
        if "/" not in name and not re.match(r"^[A-Za-z]+\d", name):
            continue
        sfp_modules.append(
            {
                "interface": normalize_interface_name(name),
                "pid": entry.get("pid"),
                "sn": entry.get("sn"),
                "description": entry.get("description"),
            }
        )

    return {"entries": entries, "sfp_modules": sfp_modules}


def pick_model_from_inventory(entries: list[dict]) -> str | None:
    preferred = ("chassis", "switch", "stack")
    for entry in entries:
        name = (entry.get("name") or "").lower()
        if any(key in name for key in preferred):
            return entry.get("pid")
    if entries:
        return entries[0].get("pid")
    return None


def pick_serial_from_inventory(entries: list[dict]) -> str | None:
    preferred = ("chassis", "switch", "stack")
    for entry in entries:
        name = (entry.get("name") or "").lower()
        if any(key in name for key in preferred):
            return entry.get("sn")
    if entries:
        return entries[0].get("sn")
    return None


def parse_vlan_brief(sections: list[dict]) -> list[dict]:
    vlans = []
    for section in sections:
        in_table = False
        for line in section.get("lines", []):
            if re.search(r"VLAN\s+Name\s+Status", line):
                in_table = True
                continue
            if not in_table:
                continue
            if not line.strip():
                continue
            match = re.match(r"^\s*(\d+)\s+(\S+)\s+(\S+)", line)
            if match:
                vlans.append(
                    {
                        "id": int(match.group(1)),
                        "name": match.group(2),
                        "status": match.group(3),
                    }
                )
    unique = {}
    for vlan in vlans:
        unique[vlan["id"]] = vlan
    return list(unique.values())


def parse_int_description(sections: list[dict], interfaces: dict) -> None:
    for section in sections:
        mode = None
        for line in section.get("lines", []):
            if re.search(r"Interface\s+Status\s+Protocol", line):
                mode = "ios"
                continue
            if re.search(r"Port\s+Type\s+Speed\s+Description", line):
                mode = "nxos_physical"
                continue
            if re.search(r"Interface\s+Description", line) and "Status" not in line:
                mode = "nxos_logical"
                continue
            if not line.strip() or line.strip().startswith("----"):
                continue
            if mode == "ios":
                match = re.match(r"^\s*(\S+)\s{2,}(.+?)\s{2,}(\S+)\s*(.*)$", line)
                if not match:
                    continue
                iface, status, protocol, description = match.groups()
                entry = ensure_interface(interfaces, iface)
                entry["oper_status"] = status.strip()
                entry["protocol"] = protocol.strip()
                if description.strip():
                    entry["description"] = description.strip()
            elif mode == "nxos_physical":
                match = re.match(r"^\s*(\S+)\s+(\S+)\s+(\S+)\s*(.*)$", line)
                if not match:
                    continue
                iface, _iface_type, _speed, description = match.groups()
                entry = ensure_interface(interfaces, iface)
                if description.strip():
                    entry["description"] = description.strip()
            elif mode == "nxos_logical":
                match = re.match(r"^\s*(\S+)\s+(.*)$", line)
                if not match:
                    continue
                iface, description = match.groups()
                entry = ensure_interface(interfaces, iface)
                if description.strip():
                    entry["description"] = description.strip()


def parse_int_status(sections: list[dict], interfaces: dict) -> None:
    for section in sections:
        in_table = False
        col_pos = None
        for line in section.get("lines", []):
            if re.search(r"Port\s+Name\s+Status\s+Vlan\s+Duplex\s+Speed\s+Type", line):
                in_table = True
                col_pos = {
                    "Port": line.find("Port"),
                    "Name": line.find("Name"),
                    "Status": line.find("Status"),
                    "Vlan": line.find("Vlan"),
                    "Duplex": line.find("Duplex"),
                    "Speed": line.find("Speed"),
                    "Type": line.find("Type"),
                }
                continue
            if not in_table:
                continue
            if not line.strip():
                continue
            if col_pos and col_pos.get("Type", -1) > -1 and len(line) >= col_pos["Type"]:
                port = line[col_pos["Port"] : col_pos["Name"]].strip()
                name = line[col_pos["Name"] : col_pos["Status"]].strip()
                status = line[col_pos["Status"] : col_pos["Vlan"]].strip()
                vlan = line[col_pos["Vlan"] : col_pos["Duplex"]].strip()
                duplex = line[col_pos["Duplex"] : col_pos["Speed"]].strip()
                speed = line[col_pos["Speed"] : col_pos["Type"]].strip()
                media = line[col_pos["Type"] :].strip()
            else:
                parts = line.split()
                if len(parts) < 6:
                    continue
                port, status, vlan, duplex, speed = parts[:5]
                name = ""
                media = " ".join(parts[5:]).strip()

            if not port:
                continue
            entry = ensure_interface(interfaces, port)
            if name:
                entry["description"] = name
            entry["oper_status"] = status
            entry["vlan"] = vlan
            entry["duplex"] = duplex
            entry["speed"] = speed
            entry["media_type"] = media


def parse_cdp_neighbors(sections: list[dict]) -> list[dict]:
    neighbors = []
    seen = set()
    for section in sections:
        in_table = False
        col_pos = None
        pending_device = None
        parse_mode = None
        for line in section.get("lines", []):
            if re.search(
                r"Device[\s-]ID\s+Local Intrfce\s+H[ol]*dtme\s+Capability\s+Platform\s+Port ID",
                line,
            ):
                in_table = True
                parse_mode = "nxos" if "Device-ID" in line or "Hldtme" in line else "ios"

                def find_col(*labels: str) -> int:
                    for label in labels:
                        match = re.search(re.escape(label), line)
                        if match:
                            return match.start()
                    return -1

                col_pos = {
                    "Device ID": find_col("Device ID", "Device-ID"),
                    "Local": find_col("Local Intrfce", "Local"),
                    "Holdtme": find_col("Holdtme", "Hldtme"),
                    "Capability": find_col("Capability"),
                    "Platform": find_col("Platform"),
                    "Port ID": find_col("Port ID"),
                }
                if any(pos < 0 for pos in col_pos.values()):
                    in_table = False
                    col_pos = None
                continue
            if not in_table:
                continue
            if not line.strip():
                continue
            if line.strip().startswith("Total cdp entries"):
                break
            if line.strip().startswith("Capability Codes"):
                continue

            stripped = line.strip()
            if col_pos and len(line) < col_pos["Port ID"]:
                if stripped and not re.search(r"\s{2,}", stripped):
                    pending_device = stripped
                continue

            if parse_mode == "nxos":
                def split_platform_port(text: str) -> tuple[str, str]:
                    parts = re.split(r"\s+(?=\S+$)", text.strip(), maxsplit=1)
                    if len(parts) == 2:
                        return parts[0], parts[1]
                    return text.strip(), ""

                def is_interface_like(value: str) -> bool:
                    return bool(re.match(r"^(?:Eth|Po|Port-channel|Vlan|Lo|mgmt)\S*", value))

                raw_parts = re.split(r"\s{2,}", line.rstrip())
                while raw_parts and raw_parts[0] == "":
                    raw_parts.pop(0)
                if not raw_parts:
                    continue
                if len(raw_parts) == 6:
                    device_id, local_if, holdtme, capability, platform, port_id = (
                        part.strip() for part in raw_parts
                    )
                elif len(raw_parts) == 5:
                    if pending_device or is_interface_like(raw_parts[0]):
                        device_id = ""
                        local_if, holdtme, capability, platform, port_id = (
                            part.strip() for part in raw_parts
                        )
                    else:
                        device_id = raw_parts[0].strip()
                        local_if = raw_parts[1].strip()
                        holdtme = raw_parts[2].strip()
                        capability = raw_parts[3].strip()
                        platform, port_id = split_platform_port(raw_parts[4])
                elif len(raw_parts) == 4:
                    device_id = ""
                    local_if = raw_parts[0].strip()
                    holdtme = raw_parts[1].strip()
                    capability = raw_parts[2].strip()
                    platform, port_id = split_platform_port(raw_parts[3])
                else:
                    continue
            elif col_pos and len(line) >= col_pos["Port ID"]:
                device_id = line[col_pos["Device ID"] : col_pos["Local"]].strip()
                local_if = line[col_pos["Local"] : col_pos["Holdtme"]].strip()
                holdtme = line[col_pos["Holdtme"] : col_pos["Capability"]].strip()
                capability = line[col_pos["Capability"] : col_pos["Platform"]].strip()
                platform = line[col_pos["Platform"] : col_pos["Port ID"]].strip()
                port_id = line[col_pos["Port ID"] :].strip()
            else:
                continue

            if device_id and not local_if and not holdtme and not port_id:
                pending_device = device_id
                continue

            if not device_id and pending_device:
                device_id = pending_device
                pending_device = None

            if not device_id or not local_if:
                continue

            dedup_key = (
                normalize_device_id(device_id).lower(),
                normalize_interface_name(local_if).lower(),
                normalize_interface_name(port_id).lower(),
            )
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            neighbors.append(
                {
                    "device_id": device_id,
                    "local_interface": local_if,
                    "capability": capability,
                    "platform": platform,
                    "remote_port": port_id,
                }
            )

    return neighbors


def parse_cdp_detail(sections: list[dict]) -> list[dict]:
    details = []
    for section in sections:
        current = None
        in_version = False
        version_lines = []
        for line in section.get("lines", []):
            stripped = line.strip()
            if stripped.startswith("Device ID:"):
                if current:
                    if version_lines:
                        current["software_version"] = version_lines[0]
                    details.append(current)
                device_id = stripped.split("Device ID:", 1)[1].strip()
                current = {
                    "device_id": device_id,
                    "ip_address": None,
                    "platform": None,
                    "capabilities": [],
                    "local_interface": None,
                    "remote_interface": None,
                    "native_vlan": None,
                    "software_version": None,
                    "power_drawn": None,
                }
                in_version = False
                version_lines = []
                continue

            if current is None:
                continue

            if stripped.startswith("Version"):
                in_version = True
                version_lines = []
                continue

            if in_version:
                if not stripped:
                    if version_lines:
                        current["software_version"] = version_lines[0]
                    in_version = False
                    continue
                version_lines.append(stripped)
                continue

            ip_match = re.search(r"IP address:\s*([0-9.]+)", line)
            if ip_match:
                current["ip_address"] = ip_match.group(1)
                continue

            platform_match = re.search(r"Platform:\s*([^,]+),\s*Capabilities:\s*(.+)$", line)
            if platform_match:
                current["platform"] = platform_match.group(1).strip()
                caps_text = platform_match.group(2).strip()
                current["capabilities"] = [cap for cap in caps_text.split() if cap]
                continue

            iface_match = re.search(r"Interface:\s*([^,]+),\s*Port ID \(outgoing port\):\s*(.+)$", line)
            if iface_match:
                current["local_interface"] = iface_match.group(1).strip()
                current["remote_interface"] = iface_match.group(2).strip()
                continue

            native_match = re.search(r"Native VLAN:\s*(\S+)", line)
            if native_match:
                current["native_vlan"] = native_match.group(1).strip()
                continue

            power_match = re.search(r"Power drawn:\s*(.+)$", line)
            if power_match:
                current["power_drawn"] = power_match.group(1).strip()
                continue

        if current:
            if version_lines and not current.get("software_version"):
                current["software_version"] = version_lines[0]
            details.append(current)

    return details


def is_phone_neighbor(capabilities: list[str], platform: str | None, remote_port: str | None) -> bool:
    caps = " ".join(capabilities).lower()
    platform_text = (platform or "").lower()
    port_text = (remote_port or "").lower()
    # Network infrastructure devices are never phones, even if they advertise
    # "phone" capability (e.g. Nexus 5K with CVTA advertises "phone port")
    infra_keywords = ("switch", "router", "bridge")
    if any(kw in caps for kw in infra_keywords):
        return False
    if "phone" in caps or ("h" in capabilities and "p" in capabilities):
        return True
    if "t27g" in platform_text or "yealink" in platform_text or "spa" in platform_text:
        return True
    if "wan port" in port_text:
        return True
    return False


def merge_cdp(brief: list[dict], detail: list[dict]) -> tuple[list[dict], list[dict]]:
    detail_index = {}
    for entry in detail:
        device_id = normalize_device_id(entry["device_id"]).lower()
        local_if = normalize_interface_name(entry.get("local_interface") or "").lower()
        key = (device_id, local_if)
        detail_index[key] = entry
        if device_id:
            detail_index.setdefault((device_id, ""), entry)

    neighbors = []
    phones = []
    for item in brief:
        device_id_norm = normalize_device_id(item["device_id"])
        local_if = normalize_interface_name(item["local_interface"])
        detail_entry = detail_index.get((device_id_norm.lower(), local_if.lower()))
        if not detail_entry:
            detail_entry = detail_index.get((device_id_norm.lower(), ""))

        platform = (detail_entry or {}).get("platform") or item.get("platform")
        capabilities = (detail_entry or {}).get("capabilities") or item.get("capability", "").split()
        remote_port = (detail_entry or {}).get("remote_interface") or item.get("remote_port")
        remote_port = normalize_interface_name(remote_port) if remote_port else None
        neighbor_ip = (detail_entry or {}).get("ip_address")

        neighbor = {
            "neighbor_device": device_id_norm,
            "local_interface": local_if,
            "remote_interface": remote_port,
            "neighbor_platform": platform,
            "neighbor_ip": neighbor_ip,
            "capabilities": capabilities,
            "is_phone": is_phone_neighbor(capabilities, platform, remote_port),
        }
        neighbors.append(neighbor)

        if neighbor["is_phone"]:
            phones.append(
                {
                    "device_id": device_id_norm,
                    "local_interface": local_if,
                    "ip": neighbor_ip,
                    "platform": platform,
                    "power_drawn": (detail_entry or {}).get("power_drawn"),
                }
            )

    return neighbors, phones


def parse_running_config(sections: list[dict]) -> tuple[dict, str | None]:
    configs = {}
    hostname = None
    for section in sections:
        current = None
        for line in section.get("lines", []):
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("hostname "):
                hostname = stripped.split(None, 1)[1].strip()
                continue
            if stripped.startswith("interface "):
                iface = normalize_interface_name(stripped.split(None, 1)[1])
                current = iface
                configs.setdefault(current, default_interface_config())
                continue
            if current is None:
                continue

            cfg = configs[current]
            if stripped.startswith("description "):
                cfg["description"] = stripped.split(None, 1)[1].strip()
            elif stripped.startswith("switchport mode "):
                mode = stripped.split()[-1]
                if mode in {"access", "trunk"}:
                    cfg["switchport_mode"] = mode
            elif stripped.startswith("switchport access vlan "):
                parts = stripped.split()
                if parts[-1].isdigit():
                    cfg["switchport_access_vlan"] = int(parts[-1])
            elif stripped.startswith("switchport trunk allowed vlan"):
                allowed = stripped.split("vlan", 1)[1].strip()
                if allowed.lower().startswith("add "):
                    allowed = allowed[4:].strip()
                cfg["switchport_trunk_allowed_vlans"] = allowed
            elif stripped.startswith("switchport voice vlan "):
                parts = stripped.split()
                if parts[-1].isdigit():
                    cfg["switchport_voice_vlan"] = int(parts[-1])
            elif stripped.startswith("switchport trunk native vlan "):
                parts = stripped.split()
                if parts[-1].isdigit():
                    cfg["switchport_trunk_native_vlan"] = int(parts[-1])
            elif stripped == "shutdown":
                cfg["shutdown"] = True
            elif stripped == "no shutdown":
                cfg["shutdown"] = False
            elif stripped.startswith("spanning-tree portfast"):
                cfg["spanning_tree_portfast"] = True
            elif stripped.startswith("speed "):
                cfg["speed"] = stripped.split(None, 1)[1].strip()
            elif stripped.startswith("channel-group "):
                parts = stripped.split()
                if len(parts) >= 2 and parts[1].isdigit():
                    cfg["channel_group"] = int(parts[1])
            elif stripped.startswith("ip address "):
                parts = stripped.split()
                if len(parts) >= 3 and parts[2] != "dhcp":
                    cfg["ip_address"] = parts[2]
            elif stripped.startswith("no ip address"):
                cfg["ip_address"] = None

    return configs, hostname


def parse_ip_int_brief(sections: list[dict]) -> list[dict]:
    interfaces = []
    for section in sections:
        mode = None
        for line in section.get("lines", []):
            if re.search(r"Interface\s+IP-Address\s+OK\?\s+Method", line):
                mode = "ios"
                continue
            if re.search(r"Interface\s+IP Address\s+Interface Status", line):
                mode = "nxos"
                continue
            if not mode or not line.strip():
                continue
            parts = line.split()
            if mode == "ios":
                if len(parts) < 6:
                    continue
                iface = normalize_interface_name(parts[0])
                ip = parts[1]
                status = " ".join(parts[4:-1]) if len(parts) > 5 else parts[4]
                interfaces.append({"interface": iface, "ip_address": ip, "status": status})
            elif mode == "nxos":
                if len(parts) < 3:
                    continue
                iface = normalize_interface_name(parts[0])
                ip = parts[1]
                status = " ".join(parts[2:])
                interfaces.append({"interface": iface, "ip_address": ip, "status": status})
    return interfaces


def parse_interface_trunks(sections: list[dict]) -> list[dict]:
    trunks = {}
    mode = None
    native_col_pos = None
    for section in sections:
        for line in section.get("lines", []):
            if re.search(r"Port\s+Mode\s+Encapsulation\s+Status\s+Native", line, re.IGNORECASE):
                mode = "native"
                native_col_pos = {
                    "Port": line.find("Port"),
                    "Mode": line.find("Mode"),
                    "Encapsulation": line.find("Encapsulation"),
                    "Status": line.find("Status"),
                    "Native": line.lower().find("native"),
                }
                continue
            if re.search(r"Port\s+Vlans allowed on trunk", line, re.IGNORECASE):
                mode = "allowed"
                continue
            if not line.strip():
                continue
            if mode == "native" and native_col_pos:
                port = line[native_col_pos["Port"] : native_col_pos["Mode"]].strip()
                if not port:
                    continue
                native_vlan = line[native_col_pos["Native"] :].strip().split()[0]
                trunks.setdefault(normalize_interface_name(port), {})["native_vlan"] = native_vlan
            elif mode == "allowed":
                if line.strip().startswith("Port"):
                    continue
                parts = line.split()
                if len(parts) < 2:
                    continue
                port = normalize_interface_name(parts[0])
                allowed = " ".join(parts[1:]).strip()
                trunks.setdefault(port, {})["allowed_vlans"] = allowed

    return [
        {
            "interface": iface,
            "native_vlan": data.get("native_vlan"),
            "allowed_vlans": data.get("allowed_vlans"),
        }
        for iface, data in trunks.items()
    ]


def choose_management_ip(ip_interfaces: list[dict]) -> str | None:
    candidates = [
        iface
        for iface in ip_interfaces
        if iface.get("ip_address")
        and iface["ip_address"].lower() not in {"unassigned", "0.0.0.0"}
    ]
    if not candidates:
        return None

    def score(entry: dict) -> tuple[int, int]:
        name = entry.get("interface", "").lower()
        status = entry.get("status", "").lower()
        status_rank = 0 if status.startswith("up") else 1
        if name in {"mgmt0", "management0"}:
            return (0, status_rank)
        if name.startswith("vlan102"):
            return (1, status_rank)
        if name.startswith("vlan1"):
            return (2, status_rank)
        if name.startswith("vlan"):
            return (3, status_rank)
        return (4, status_rank)

    return sorted(candidates, key=score)[0].get("ip_address")


def derive_port_channels(configs: dict) -> list[dict]:
    channel_members: dict[int, list[str]] = {}
    channel_configs: dict[int, dict] = {}
    for iface, cfg in configs.items():
        group = cfg.get("channel_group")
        if group:
            channel_members.setdefault(group, []).append(iface)
        if iface.lower().startswith("port-channel") or iface.lower().startswith("po"):
            match = re.search(r"(\d+)$", iface)
            if match:
                channel_configs[int(match.group(1))] = cfg

    port_channels = []
    for group, members in channel_members.items():
        name = f"Port-channel{group}"
        cfg = channel_configs.get(group, {})
        port_channels.append(
            {
                "name": name,
                "members": sorted(members),
                "mode": cfg.get("switchport_mode"),
            }
        )
    return port_channels


def interface_speed_label(speed: str | None) -> str | None:
    if not speed:
        return None
    normalized = speed.lower()
    if "10g" in normalized or "10000" in normalized:
        return "10G"
    if "1000" in normalized or "1g" in normalized:
        return "1G"
    if "100" in normalized:
        return "100M"
    return None


def external_device_type(capabilities: list[str], platform: str | None) -> str:
    caps = {cap.lower() for cap in capabilities}
    platform_text = (platform or "").lower()
    if "router" in caps or "r" in caps or "c1111" in platform_text:
        return "router"
    return "switch"


def role_from_model(model: str | None) -> str:
    model_text = (model or "").upper()
    if "N5K" in model_text or "NEXUS5548" in model_text or "C9300" in model_text:
        return "core"
    if "C9200" in model_text:
        return "distribution"
    if "2960" in model_text or "C2960" in model_text:
        return "access"
    return "access"


def parse_device_log(file_path: Path, warnings: list[str]) -> dict:
    lines = read_log(file_path)
    sections = parse_command_sections(lines)
    sections_by_cmd: dict[str, list[dict]] = {}
    for section in sections:
        sections_by_cmd.setdefault(section["cmd"], []).append(section)

    device = {
        "hostname": None,
        "model": None,
        "serial_number": None,
        "ios_version": None,
        "uptime": None,
        "platform_type": None,
        "management_ip": None,
        "vlans": [],
        "interfaces": {},
        "cdp_neighbors": [],
        "phones": [],
        "ip_interfaces": [],
        "trunks": [],
        "port_channels": [],
        "sfp_modules": [],
    }

    if "show version" in sections_by_cmd:
        version_info = parse_show_version(sections_by_cmd["show version"][0])
        device.update(version_info)
    else:
        warn(warnings, f"{file_path.name}: missing show version")

    inventory_info = {"entries": [], "sfp_modules": []}
    if "show inventory" in sections_by_cmd:
        inventory_info = parse_inventory(sections_by_cmd["show inventory"])
        device["sfp_modules"] = inventory_info["sfp_modules"]
    else:
        warn(warnings, f"{file_path.name}: missing show inventory")

    running_configs = {}
    running_hostname = None
    if "show running-config" in sections_by_cmd:
        running_configs, running_hostname = parse_running_config(
            sections_by_cmd["show running-config"]
        )
    else:
        warn(warnings, f"{file_path.name}: missing show running-config")

    if not device["hostname"] and running_hostname:
        device["hostname"] = running_hostname
    if not device["hostname"]:
        device["hostname"] = file_path.stem

    if not device["model"]:
        device["model"] = pick_model_from_inventory(inventory_info["entries"])
    if not device["serial_number"]:
        device["serial_number"] = pick_serial_from_inventory(inventory_info["entries"])

    if "show vlan brief" in sections_by_cmd:
        device["vlans"] = parse_vlan_brief(sections_by_cmd["show vlan brief"])
    else:
        warn(warnings, f"{file_path.name}: missing show vlan brief")

    interfaces = device["interfaces"]
    for iface, cfg in running_configs.items():
        entry = ensure_interface(interfaces, iface)
        entry["config"].update(cfg)
        if cfg.get("description"):
            entry["description"] = cfg.get("description")

    if "show int description" in sections_by_cmd:
        parse_int_description(sections_by_cmd["show int description"], interfaces)
    else:
        warn(warnings, f"{file_path.name}: missing show int description")

    if "show int status" in sections_by_cmd:
        parse_int_status(sections_by_cmd["show int status"], interfaces)
    else:
        warn(warnings, f"{file_path.name}: missing show int status")

    if "show cdp nei" in sections_by_cmd:
        cdp_brief = parse_cdp_neighbors(sections_by_cmd["show cdp nei"])
    else:
        warn(warnings, f"{file_path.name}: missing show cdp nei")
        cdp_brief = []

    if "show cdp nei detail" in sections_by_cmd:
        cdp_detail = parse_cdp_detail(sections_by_cmd["show cdp nei detail"])
    else:
        warn(warnings, f"{file_path.name}: missing show cdp nei detail")
        cdp_detail = []

    neighbors, phones = merge_cdp(cdp_brief, cdp_detail)
    device["cdp_neighbors"] = neighbors
    device["phones"] = phones

    if "show ip int brief" in sections_by_cmd:
        device["ip_interfaces"] = parse_ip_int_brief(sections_by_cmd["show ip int brief"])
    else:
        warn(warnings, f"{file_path.name}: missing show ip int brief")
    device["management_ip"] = choose_management_ip(device["ip_interfaces"])

    if "show inter trunk" in sections_by_cmd:
        device["trunks"] = parse_interface_trunks(sections_by_cmd["show inter trunk"])
    else:
        warn(warnings, f"{file_path.name}: missing show inter trunk")

    if not device["trunks"]:
        for iface, cfg in running_configs.items():
            if cfg.get("switchport_mode") == "trunk":
                device["trunks"].append(
                    {
                        "interface": iface,
                        "native_vlan": (
                            str(cfg.get("switchport_trunk_native_vlan"))
                            if cfg.get("switchport_trunk_native_vlan") is not None
                            else None
                        ),
                        "allowed_vlans": cfg.get("switchport_trunk_allowed_vlans"),
                    }
                )

    device["port_channels"] = derive_port_channels(running_configs)

    for ip_iface in device["ip_interfaces"]:
        entry = ensure_interface(interfaces, ip_iface["interface"])
        if entry["config"].get("ip_address") is None and ip_iface.get("ip_address") not in {
            "unassigned",
            "0.0.0.0",
        }:
            entry["config"]["ip_address"] = ip_iface.get("ip_address")

    return device


def build_topology(devices: list[dict]) -> dict:
    device_lookup = {normalize_device_id(d["hostname"]).lower(): d for d in devices}
    trunk_map = {
        d["hostname"]: {normalize_interface_name(t["interface"]) for t in d.get("trunks", [])}
        for d in devices
    }

    nodes = []
    for device in devices:
        nodes.append(
            {
                "id": device["hostname"],
                "model": device.get("model"),
                "serial": device.get("serial_number"),
                "role": role_from_model(device.get("model")),
                "management_ip": device.get("management_ip"),
                "platform_type": device.get("platform_type"),
            }
        )

    links_by_pair = {}
    external_devices = []
    seen_external = set()

    for device in devices:
        local_name = device["hostname"]
        for neighbor in device.get("cdp_neighbors", []):
            if neighbor.get("is_phone"):
                continue
            neighbor_id = normalize_device_id(neighbor.get("neighbor_device", ""))
            if not neighbor_id:
                continue
            remote_device = device_lookup.get(neighbor_id.lower())
            local_port = neighbor.get("local_interface")
            remote_port = neighbor.get("remote_interface")
            if remote_device:
                remote_name = remote_device["hostname"]
                if local_name == remote_name:
                    continue
                source, target = sorted([local_name, remote_name])
                if source == local_name:
                    source_port = local_port
                    target_port = remote_port
                else:
                    source_port = remote_port
                    target_port = local_port

                link_type = None
                if local_port and local_port in trunk_map.get(local_name, set()):
                    link_type = "trunk"
                if remote_port and remote_port in trunk_map.get(remote_name, set()):
                    link_type = "trunk"
                if link_type is None:
                    link_type = "access"

                speed = None
                media = None
                local_interface_data = device["interfaces"].get(
                    normalize_interface_name(local_port or "")
                )
                if local_interface_data:
                    speed = interface_speed_label(local_interface_data.get("speed"))
                    media = local_interface_data.get("media_type")

                link = {
                    "source": source,
                    "source_port": source_port,
                    "target": target,
                    "target_port": target_port,
                    "speed": speed,
                    "link_type": link_type,
                    "media": media,
                }

                pair_key = (
                    source.lower(),
                    target.lower(),
                    (source_port or "").lower(),
                    (target_port or "").lower(),
                )
                existing = links_by_pair.get(pair_key)
                if not existing or link_score(link) > link_score(existing):
                    links_by_pair[pair_key] = link
            else:
                ext_key = (neighbor_id.lower(), local_name.lower(), local_port)
                if ext_key in seen_external:
                    continue
                seen_external.add(ext_key)
                external_devices.append(
                    {
                        "device_id": neighbor_id,
                        "platform": neighbor.get("neighbor_platform"),
                        "ip": neighbor.get("neighbor_ip"),
                        "connected_to": local_name,
                        "connected_port": local_port,
                        "type": external_device_type(
                            neighbor.get("capabilities", []), neighbor.get("neighbor_platform")
                        ),
                    }
                )

    return {
        "nodes": nodes,
        "links": list(links_by_pair.values()),
        "external_devices": external_devices,
    }


def link_score(link: dict) -> int:
    score = 0
    for key in ("speed", "media", "link_type"):
        if link.get(key):
            score += 1
    return score


def main() -> int:
    base_dir = Path(__file__).resolve().parent
    log_files = sorted(base_dir.glob("*.log"))
    if not log_files:
        print("Parsed 0 devices, 0 links, 0 phones")
        return 0

    warnings: list[str] = []
    devices = []
    total_phones = 0

    for log_file in log_files:
        device = parse_device_log(log_file, warnings)
        devices.append(device)
        total_phones += len(device.get("phones", []))

    topology = build_topology(devices)

    devices_path = base_dir / "devices.json"
    topology_path = base_dir / "topology.json"
    devices_path.write_text(json.dumps(devices, indent=2, ensure_ascii=False))
    topology_path.write_text(json.dumps(topology, indent=2, ensure_ascii=False))

    for message in warnings:
        print(f"Warning: {message}", file=sys.stderr)

    print(
        f"Parsed {len(devices)} devices, {len(topology['links'])} links, {total_phones} phones"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
