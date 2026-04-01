"""
skills/geoip_lookup/logic.py

Minimal MaxMind GeoIP maintenance + lookup skill.

Behavior:
- On first use, download the configured GeoLite2 MMDB if it is missing.
- Once per Tuesday/Friday (GeoLite City schedule), refresh the MMDB if it is stale.
- When an IP is provided, return local geolocation details from the MMDB.

NOTE: This uses the direct MaxMind API endpoint. For production, consider using
the official geoipupdate tool (https://github.com/maxmind/geoipupdate) which handles
automatic updates, archival, and database rotation.
"""
from __future__ import annotations

import ipaddress
import logging
import os
import re
import tarfile
from datetime import datetime, timedelta, timezone
from io import BytesIO
from pathlib import Path
from typing import Any

import requests

logger = logging.getLogger(__name__)

SKILL_NAME = "geoip_lookup"
ROOT_DIR = Path(__file__).parents[2]
DEFAULT_DB_PATH = ROOT_DIR / "data" / "geoip" / "GeoLite2-City.mmdb"
# Use official MaxMind download API endpoint
DEFAULT_DOWNLOAD_URL = "https://download.maxmind.com/app/geoip_download"
# Alternative endpoint: https://updates.maxmind.com
IP_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")


def _cfg_get(cfg: Any, section: str, key: str, default: Any = None) -> Any:
    if cfg is None:
        return default
    getter = getattr(cfg, "get", None)
    if callable(getter):
        try:
            return getter(section, key, default=default)
        except TypeError:
            return getter(section, key, default)
    return default


def _settings_from_config(cfg: Any) -> dict[str, Any]:
    db_path = Path(_cfg_get(cfg, "geoip", "db_path", default=str(DEFAULT_DB_PATH)))
    if not db_path.is_absolute():
        db_path = ROOT_DIR / db_path

    return {
        "db_path": db_path,
        "edition_id": _cfg_get(cfg, "geoip", "edition_id", default="GeoLite2-City"),
        "license_key": _cfg_get(cfg, "geoip", "license_key", default=os.getenv("MAXMIND_LICENSE_KEY")),
        "download_url": _cfg_get(cfg, "geoip", "download_url", default=DEFAULT_DOWNLOAD_URL),
        "update_interval_days": int(_cfg_get(cfg, "geoip", "update_interval_days", default=7) or 7),
        "timeout_seconds": int(_cfg_get(cfg, "geoip", "timeout_seconds", default=60) or 60),
    }


def _extract_ip(parameters: dict) -> str | None:
    if not isinstance(parameters, dict):
        return None

    direct_ip = parameters.get("ip")
    if isinstance(direct_ip, str) and _is_valid_ip(direct_ip):
        return direct_ip

    question = parameters.get("question") or parameters.get("query") or ""
    for candidate in IP_PATTERN.findall(str(question)):
        if _is_valid_ip(candidate):
            return candidate
    return None


def _extract_ips(parameters: dict, previous_results: dict | None = None) -> list[str]:
    ips: list[str] = []
    seen: set[str] = set()

    def _add(value: Any) -> None:
        if isinstance(value, str) and _is_valid_ip(value) and value not in seen:
            seen.add(value)
            ips.append(value)

    if isinstance(parameters, dict):
        direct_ips = parameters.get("ips")
        if isinstance(direct_ips, list):
            for value in direct_ips:
                _add(value)

        direct_ip = _extract_ip(parameters)
        if direct_ip:
            _add(direct_ip)

    previous_results = previous_results or {}
    os_result = previous_results.get("opensearch_querier") or {}
    if isinstance(os_result, dict):
        for row in os_result.get("results", []) or []:
            if not isinstance(row, dict):
                continue
            for value in (
                row.get("src_ip"),
                row.get("dest_ip"),
                row.get("source.ip"),
                row.get("destination.ip"),
                row.get("source", {}).get("ip") if isinstance(row.get("source"), dict) else None,
                row.get("destination", {}).get("ip") if isinstance(row.get("destination"), dict) else None,
            ):
                _add(value)

    return ips


def _is_valid_ip(value: str) -> bool:
    try:
        ipaddress.ip_address(str(value).strip())
        return True
    except ValueError:
        return False


def _is_stale(db_path: Path, update_interval_days: int) -> bool:
    if not db_path.exists():
        return True
    modified = datetime.fromtimestamp(db_path.stat().st_mtime, tz=timezone.utc)
    return datetime.now(timezone.utc) - modified >= timedelta(days=update_interval_days)


def _download_database(settings: dict[str, Any]) -> Path:
    db_path: Path = settings["db_path"]
    edition_id = settings["edition_id"]
    license_key = settings.get("license_key")
    download_url = settings["download_url"]
    timeout_seconds = settings["timeout_seconds"]

    if not license_key:
        raise ValueError("MAXMIND_LICENSE_KEY is required to download the GeoIP database")

    response = requests.get(
        download_url,
        params={
            "edition_id": edition_id,
            "license_key": license_key,
            "suffix": "tar.gz",
        },
        timeout=timeout_seconds,
    )
    response.raise_for_status()

    with tarfile.open(fileobj=BytesIO(response.content), mode="r:gz") as archive:
        mmdb_members = [member for member in archive.getmembers() if member.name.endswith(".mmdb")]
        if not mmdb_members:
            raise RuntimeError("Downloaded MaxMind archive did not contain an .mmdb file")

        selected = next((member for member in mmdb_members if edition_id in member.name), mmdb_members[0])
        extracted = archive.extractfile(selected)
        if extracted is None:
            raise RuntimeError("Could not extract MaxMind .mmdb from archive")
        payload = extracted.read()

    db_path.parent.mkdir(parents=True, exist_ok=True)
    db_path.write_bytes(payload)
    logger.info("[%s] Wrote MaxMind DB to %s", SKILL_NAME, db_path)
    return db_path


def _ensure_database(settings: dict[str, Any], force_update: bool = False) -> dict[str, Any]:
    db_path: Path = settings["db_path"]
    existed_before = db_path.exists()
    stale = _is_stale(db_path, settings["update_interval_days"])

    if db_path.exists() and not stale and not force_update:
        return {"action": "ready", "db_path": str(db_path)}

    if not settings.get("license_key"):
        if db_path.exists():
            return {
                "action": "stale" if stale or force_update else "ready",
                "db_path": str(db_path),
                "warning": "Database exists locally but MAXMIND_LICENSE_KEY is not configured for refresh",
            }
        raise ValueError("GeoIP database missing and MAXMIND_LICENSE_KEY is not configured")

    downloaded_path = _download_database(settings)
    return {
        "action": "downloaded" if not existed_before else "updated",
        "db_path": str(downloaded_path),
    }


def _open_reader(db_path: Path):
    try:
        from geoip2.database import Reader
    except ImportError as exc:
        raise RuntimeError("geoip2 package is not installed; install dependencies to use geoip_lookup") from exc
    return Reader(str(db_path))


def _extract_subdivision(response: Any) -> tuple[str | None, str | None]:
    subdivisions = getattr(response, "subdivisions", None)
    if subdivisions is None:
        return None, None

    most_specific = getattr(subdivisions, "most_specific", None)
    if most_specific is not None:
        return getattr(most_specific, "name", None), getattr(most_specific, "iso_code", None)

    try:
        first = subdivisions[0]
        return getattr(first, "name", None), getattr(first, "iso_code", None)
    except Exception:
        return None, None


def _lookup_ip(db_path: Path, ip: str) -> dict[str, Any]:
    try:
        from geoip2.errors import AddressNotFoundError
    except ImportError:
        class AddressNotFoundError(Exception):
            pass

    try:
        with _open_reader(db_path) as reader:
            response = reader.city(ip)
    except AddressNotFoundError:
        return {"status": "not_found", "ip": ip, "reason": "address not present in database"}

    subdivision_name, subdivision_code = _extract_subdivision(response)
    geo = {
        "continent": getattr(getattr(response, "continent", None), "name", None),
        "country": getattr(getattr(response, "country", None), "name", None),
        "country_iso_code": getattr(getattr(response, "country", None), "iso_code", None),
        "registered_country": getattr(getattr(response, "registered_country", None), "name", None),
        "subdivision": subdivision_name,
        "subdivision_iso_code": subdivision_code,
        "city": getattr(getattr(response, "city", None), "name", None),
        "postal_code": getattr(getattr(response, "postal", None), "code", None),
        "timezone": getattr(getattr(response, "location", None), "time_zone", None),
        "latitude": getattr(getattr(response, "location", None), "latitude", None),
        "longitude": getattr(getattr(response, "location", None), "longitude", None),
        "accuracy_radius": getattr(getattr(response, "location", None), "accuracy_radius", None),
    }
    return {"status": "ok", "ip": ip, "geo": geo}


def run(context: dict) -> dict:
    parameters = context.get("parameters", {}) or {}
    cfg = context.get("config")
    memory = context.get("memory")
    previous_results = context.get("previous_results", {}) or {}
    force_update = bool(parameters.get("force_update", False))
    checked_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    settings = _settings_from_config(cfg)

    try:
        maintenance = _ensure_database(settings, force_update=force_update)
    except Exception as exc:
        logger.error("[%s] Failed to ensure GeoIP DB: %s", SKILL_NAME, exc)
        return {"status": "error", "error": str(exc), "checked_at": checked_at}

    ips = _extract_ips(parameters, previous_results=previous_results)
    result = {
        "status": "ok",
        "action": maintenance.get("action", "ready"),
        "db_path": maintenance.get("db_path", str(settings["db_path"])),
        "checked_at": checked_at,
    }
    if maintenance.get("warning"):
        result["warning"] = maintenance["warning"]

    if len(ips) == 1:
        ip = ips[0]
        try:
            lookup = _lookup_ip(settings["db_path"], ip)
            result.update(lookup)
        except Exception as exc:
            logger.error("[%s] GeoIP lookup failed for %s: %s", SKILL_NAME, ip, exc)
            return {"status": "error", "error": str(exc), "ip": ip, "checked_at": checked_at}
    elif ips:
        lookups: list[dict[str, Any]] = []
        for ip in ips[:25]:
            try:
                lookup = _lookup_ip(settings["db_path"], ip)
            except Exception as exc:
                logger.error("[%s] GeoIP lookup failed for %s: %s", SKILL_NAME, ip, exc)
                lookup = {"status": "error", "ip": ip, "error": str(exc)}
            lookups.append(lookup)
        result["ips"] = ips[:25]
        result["lookups"] = lookups

    if memory and result.get("action") in {"downloaded", "updated"}:
        memory.add_decision(
            f"GeoIPLookup {result['action']} the MaxMind database at {result['db_path']}"
        )

    return result
