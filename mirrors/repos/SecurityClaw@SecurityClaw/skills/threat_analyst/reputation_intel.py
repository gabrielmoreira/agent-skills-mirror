"""
skills/threat_analyst/reputation_intel.py

Fetches reputation intelligence for IPs and domains from public APIs:
- AbuseIPDB: IP abuse history
- Talos: IP intelligence
- AlienVault OTX: Domain/IP threat data
- VirusTotal: File/URL/IP/Domain intelligence
- MITRE ATT&CK: Vulnerability and technique data

Gracefully handles missing API keys and network failures.
"""
from __future__ import annotations

import logging
import os
import re
from typing import Optional
from datetime import datetime

import requests

logger = logging.getLogger(__name__)

# API endpoints and configuration
ABUSEIPDB_URL = "https://api.abuseipdb.com/api/v2/check"
ABUSEIPDB_KEY = os.getenv("ABUSEIPDB_API_KEY", "")

ALIENVAULT_URL = "https://otx.alienvault.com/api/v1"
ALIENVAULT_KEY = os.getenv("ALIENVAULT_API_KEY", "")

VIRUSTOTAL_URL = "https://www.virustotal.com/api/v3"
VIRUSTOTAL_KEY = os.getenv("VIRUSTOTAL_API_KEY", "")

TALOS_URL = "https://api.amp.cisco.com/v1"
TALOS_KEY = os.getenv("TALOS_CLIENT_ID", "")
TALOS_SECRET = os.getenv("TALOS_CLIENT_SECRET", "")

MITRE_URL = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack"

REQUEST_TIMEOUT = 5
MAX_RETRIES = 1


def get_ip_reputation(ip: str) -> dict:
    """
    Fetch reputation scores for an IP from multiple sources.
    
    Returns dict with reputation data from available APIs:
    {
        "ip": "1.2.3.4",
        "abuseipdb": {"abuse_score": 75, "reports": 5, "last_reported": "2026-03-02"},
        "alienvault": {"pulses": 2, "reputation": "malicious", "tags": ["botnet", "c2"]},
        "talos": {"reputation": -50, "categories": ["spam", "malware"]},
        "virustotal": {"malicious": 5, "undetected": 60, "suspicious": 2},
        "combined_risk": "HIGH"  # HIGH/MEDIUM/LOW based on multiple sources
    }
    """
    result = {
        "ip": ip,
        "queries": [],
        "combined_risk": "UNKNOWN",
    }

    # Validate IP format
    if not _is_valid_ip(ip):
        logger.warning(f"[reputation_intel] Invalid IP format: {ip}")
        return result

    # Try AbuseIPDB
    if ABUSEIPDB_KEY:
        try:
            abuse_data = _query_abuseipdb(ip)
            if abuse_data:
                result["abuseipdb"] = abuse_data
                result["queries"].append("abuseipdb")
        except Exception as e:
            logger.debug(f"[reputation_intel] AbuseIPDB query failed for {ip}: {e}")

    # Try AlienVault OTX
    if ALIENVAULT_KEY:
        try:
            alien_data = _query_alienvault(ip, "ip")
            if alien_data:
                result["alienvault"] = alien_data
                result["queries"].append("alienvault")
        except Exception as e:
            logger.debug(f"[reputation_intel] AlienVault query failed for {ip}: {e}")

    # Try Talos
    if TALOS_KEY and TALOS_SECRET:
        try:
            talos_data = _query_talos(ip)
            if talos_data:
                result["talos"] = talos_data
                result["queries"].append("talos")
        except Exception as e:
            logger.debug(f"[reputation_intel] Talos query failed for {ip}: {e}")

    # Try VirusTotal
    if VIRUSTOTAL_KEY:
        try:
            vt_data = _query_virustotal(ip, "ip")
            if vt_data:
                result["virustotal"] = vt_data
                result["queries"].append("virustotal")
        except Exception as e:
            logger.debug(f"[reputation_intel] VirusTotal query failed for {ip}: {e}")

    # Calculate combined risk
    result["combined_risk"] = _calculate_combined_risk(result)

    return result


def get_domain_reputation(domain: str) -> dict:
    """
    Fetch reputation scores for a domain from multiple sources.
    
    Returns dict with reputation data from available APIs.
    """
    result = {
        "domain": domain,
        "queries": [],
        "combined_risk": "UNKNOWN",
    }

    # Validate domain format
    if not _is_valid_domain(domain):
        logger.warning(f"[reputation_intel] Invalid domain format: {domain}")
        return result

    # Try AlienVault OTX
    if ALIENVAULT_KEY:
        try:
            alien_data = _query_alienvault(domain, "domain")
            if alien_data:
                result["alienvault"] = alien_data
                result["queries"].append("alienvault")
        except Exception as e:
            logger.debug(f"[reputation_intel] AlienVault query failed for {domain}: {e}")

    # Try VirusTotal
    if VIRUSTOTAL_KEY:
        try:
            vt_data = _query_virustotal(domain, "domain")
            if vt_data:
                result["virustotal"] = vt_data
                result["queries"].append("virustotal")
        except Exception as e:
            logger.debug(f"[reputation_intel] VirusTotal query failed for {domain}: {e}")

    # Calculate combined risk
    result["combined_risk"] = _calculate_combined_risk(result)

    return result


def get_mitre_data(tactic: str = None, technique: str = None) -> dict:
    """
    Fetch MITRE ATT&CK data for tactics and techniques.
    
    Returns dict with MITRE framework information.
    """
    result = {
        "framework": "MITRE ATT&CK",
        "data": {},
    }

    try:
        # This would require downloading and parsing MITRE CTI data
        # For now, return a placeholder that can be enhanced
        logger.debug("[reputation_intel] MITRE ATT&CK data fetch (not yet implemented)")
    except Exception as e:
        logger.debug(f"[reputation_intel] MITRE data fetch failed: {e}")

    return result


# ──────────────────────────────────────────────────────────────────────────────
# Private API Query Functions
# ──────────────────────────────────────────────────────────────────────────────

def _query_abuseipdb(ip: str) -> dict:
    """Query AbuseIPDB API for IP reputation."""
    if not ABUSEIPDB_KEY:
        return {}

    headers = {
        "Key": ABUSEIPDB_KEY,
        "Accept": "application/json",
    }
    params = {
        "ipAddress": ip,
        "maxAgeInDays": 90,
        "verbose": "",
    }

    try:
        resp = requests.get(
            ABUSEIPDB_URL,
            headers=headers,
            params=params,
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        report = data.get("data", {})
        
        return {
            "abuse_score": report.get("abuseConfidenceScore", 0),
            "reports": report.get("totalReports", 0),
            "last_reported": report.get("lastReportedAt", "never"),
            "is_whitelisted": report.get("isWhitelisted", False),
            "usage_type": report.get("usageType", "unknown"),
        }
    except Exception as e:
        logger.debug(f"[reputation_intel] AbuseIPDB error: {e}")
        return {}


def _query_alienvault(entity: str, entity_type: str) -> dict:
    """Query AlienVault OTX API for entity reputation."""
    if not ALIENVAULT_KEY:
        return {}

    url = f"{ALIENVAULT_URL}/{entity_type}/{entity}/general"
    headers = {"X-OTX-API-KEY": ALIENVAULT_KEY}

    try:
        resp = requests.get(
            url,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        
        pulses = data.get("pulse_info", {}).get("pulses", [])
        tags = set()
        for pulse in pulses:
            tags.update(pulse.get("tags", []))
        
        reputation = "clean"
        if len(pulses) > 5:
            reputation = "malicious"
        elif len(pulses) > 2:
            reputation = "suspicious"
        
        return {
            "pulses": len(pulses),
            "reputation": reputation,
            "tags": list(tags)[:10],  # Top 10 tags
        }
    except Exception as e:
        logger.debug(f"[reputation_intel] AlienVault error: {e}")
        return {}


def _query_talos(ip: str) -> dict:
    """Query Cisco Talos API for IP reputation."""
    if not TALOS_KEY or not TALOS_SECRET:
        return {}

    try:
        # Talos API requires OAuth - simplified version
        # Real implementation would need OAuth flow
        logger.debug("[reputation_intel] Talos query (OAuth not configured)")
        return {}
    except Exception as e:
        logger.debug(f"[reputation_intel] Talos error: {e}")
        return {}


def _query_virustotal(entity: str, entity_type: str) -> dict:
    """Query VirusTotal API for entity reputation."""
    if not VIRUSTOTAL_KEY:
        return {}

    headers = {"x-apikey": VIRUSTOTAL_KEY}
    
    try:
        # VirusTotal v3 API endpoints
        url = f"{VIRUSTOTAL_URL}/{entity_type}/{entity}"
        resp = requests.get(
            url,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        
        stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
        
        return {
            "malicious": stats.get("malicious", 0),
            "suspicious": stats.get("suspicious", 0),
            "undetected": stats.get("undetected", 0),
            "harmless": stats.get("harmless", 0),
        }
    except Exception as e:
        logger.debug(f"[reputation_intel] VirusTotal error: {e}")
        return {}


# ──────────────────────────────────────────────────────────────────────────────
# Validation and Risk Calculation
# ──────────────────────────────────────────────────────────────────────────────

def _is_valid_ip(ip: str) -> bool:
    """Validate IPv4 address format."""
    pattern = r"^(?:\d{1,3}\.){3}\d{1,3}$"
    if not re.match(pattern, ip):
        return False
    parts = ip.split(".")
    return all(0 <= int(p) <= 255 for p in parts)


def _is_valid_domain(domain: str) -> bool:
    """Validate domain format."""
    pattern = r"^(?:[a-z0-9](?:[a-z0-9\-]{0,61}[a-z0-9])?\.)+[a-z]{2,}$"
    return bool(re.match(pattern, domain.lower()))


def _calculate_combined_risk(intel_result: dict) -> str:
    """Calculate combined risk level from multiple sources."""
    risk_score = 0
    
    # AbuseIPDB score (0-100)
    if "abuseipdb" in intel_result:
        abuse_score = intel_result["abuseipdb"].get("abuse_score", 0)
        if abuse_score > 75:
            risk_score += 40
        elif abuse_score > 50:
            risk_score += 25
        elif abuse_score > 25:
            risk_score += 10
    
    # AlienVault reputation
    if "alienvault" in intel_result:
        reputation = intel_result["alienvault"].get("reputation", "clean")
        if reputation == "malicious":
            risk_score += 40
        elif reputation == "suspicious":
            risk_score += 20
    
    # VirusTotal detection ratio
    if "virustotal" in intel_result:
        stats = intel_result["virustotal"]
        malicious = stats.get("malicious", 0)
        suspicious = stats.get("suspicious", 0)
        total = malicious + suspicious + stats.get("harmless", 0) + stats.get("undetected", 0)
        if total > 0:
            detection_ratio = (malicious + suspicious) / total
            if detection_ratio > 0.5:
                risk_score += 40
            elif detection_ratio > 0.2:
                risk_score += 20
    
    # Determine risk level
    if risk_score >= 60:
        return "HIGH"
    elif risk_score >= 30:
        return "MEDIUM"
    else:
        return "LOW"
