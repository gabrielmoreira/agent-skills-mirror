#!/usr/bin/env python3
"""
Discover package-level Playwright/Lighthouse audit entry points and PWA signals.

Usage:
    discover_audit_targets.py [repo_root] [--json]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

AUDIT_SCRIPT_PATTERN = re.compile(r"(playwright|lighthouse|perf|e2e|smoke)", re.IGNORECASE)
RUNNER_NAME_PATTERN = re.compile(r"(playwright|lighthouse|e2e|smoke|audit)", re.IGNORECASE)
PLAYWRIGHT_PATTERN = re.compile(r"\bplaywright\b", re.IGNORECASE)
LIGHTHOUSE_PATTERN = re.compile(r"\blighthouse\b", re.IGNORECASE)
MANIFEST_LINK_PATTERN = re.compile(r"""rel\s*=\s*["']manifest["']""", re.IGNORECASE)
SERVICE_WORKER_PATTERN = re.compile(
    r"""navigator\.serviceWorker|serviceWorker\s*\.\s*register\s*\(""",
    re.IGNORECASE,
)

RUNNER_SUFFIXES = {".js", ".cjs", ".mjs", ".ts", ".sh", ".py"}
CODE_SUFFIXES = {".astro", ".js", ".cjs", ".mjs", ".ts", ".tsx", ".jsx", ".html"}
MAX_TEXT_BYTES = 512_000


def unique_strings(values: list[str]) -> list[str]:
    return sorted(set(values))


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str | None:
    if not path.is_file() or path.stat().st_size > MAX_TEXT_BYTES:
        return None
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def relative_path(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def package_command(package_dir: Path, repo_root: Path, script_name: str) -> str:
    relative_dir = package_dir.relative_to(repo_root).as_posix()
    if relative_dir == ".":
        return f"npm run {script_name}"
    return f"npm --prefix {relative_dir} run {script_name}"


def classify_runner(path: Path, content: str | None) -> str:
    haystack = f"{path.name}\n{content or ''}"
    has_playwright = bool(PLAYWRIGHT_PATTERN.search(haystack))
    has_lighthouse = bool(LIGHTHOUSE_PATTERN.search(haystack))

    if has_playwright and has_lighthouse:
        return "combined"
    if has_playwright:
        return "playwright"
    if has_lighthouse:
        return "lighthouse"
    return "other"


def discover_runner_files(package_dir: Path, repo_root: Path) -> list[dict]:
    results = []
    candidate_dirs = ("perf", "scripts", "e2e", "tests")

    for subdir_name in candidate_dirs:
        subdir = package_dir / subdir_name
        if not subdir.exists():
            continue
        for path in subdir.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix not in RUNNER_SUFFIXES:
                continue
            if not RUNNER_NAME_PATTERN.search(path.name):
                continue
            content = read_text(path)
            results.append(
                {
                    "path": relative_path(path, repo_root),
                    "type": classify_runner(path, content),
                }
            )
    return sorted(results, key=lambda item: item["path"])


def discover_scripts(package_json: dict, package_dir: Path, repo_root: Path) -> list[dict]:
    scripts = package_json.get("scripts", {})
    discovered = []
    if not isinstance(scripts, dict):
        return discovered

    for name, command in scripts.items():
        if not isinstance(command, str):
            continue
        haystack = f"{name}\n{command}"
        if not AUDIT_SCRIPT_PATTERN.search(haystack):
            continue
        script_type = classify_runner(Path(name), command)
        discovered.append(
            {
                "name": name,
                "command": command,
                "type": script_type,
                "run": package_command(package_dir, repo_root, name),
            }
        )
    return sorted(discovered, key=lambda item: item["name"])


def discover_pwa_signals(package_dir: Path, repo_root: Path) -> dict:
    manifest_paths: list[str] = []
    service_worker_paths: list[str] = []
    manifest_link_files: list[str] = []
    service_worker_ref_files: list[str] = []

    for path in package_dir.rglob("*"):
        if not path.is_file():
            continue

        if path.name in {"site.webmanifest", "manifest.webmanifest", "manifest.json"}:
            manifest_paths.append(relative_path(path, repo_root))

        if "service-worker" in path.name.lower() and path.suffix in CODE_SUFFIXES.union({".json"}):
            service_worker_paths.append(relative_path(path, repo_root))

        if path.suffix not in CODE_SUFFIXES:
            continue

        content = read_text(path)
        if content is None:
            continue

        if MANIFEST_LINK_PATTERN.search(content):
            manifest_link_files.append(relative_path(path, repo_root))

        if SERVICE_WORKER_PATTERN.search(content):
            service_worker_ref_files.append(relative_path(path, repo_root))

    has_manifest = bool(manifest_paths or manifest_link_files)
    has_service_worker = bool(service_worker_paths or service_worker_ref_files)

    if has_manifest and has_service_worker:
        readiness = "likely"
    elif has_manifest:
        readiness = "partial"
    else:
        readiness = "none"

    return {
        "readiness": readiness,
        "manifest_files": unique_strings(manifest_paths + manifest_link_files),
        "service_worker_files": unique_strings(service_worker_paths + service_worker_ref_files),
    }


def discover_packages(repo_root: Path) -> list[dict]:
    package_json_paths = sorted(repo_root.rglob("package.json"))
    packages = []

    for package_json_path in package_json_paths:
        if "node_modules" in package_json_path.parts:
            continue

        package_dir = package_json_path.parent
        rel_dir = package_dir.relative_to(repo_root).as_posix()
        package_data = read_json(package_json_path)

        packages.append(
            {
                "package_dir": rel_dir,
                "scripts": discover_scripts(package_data, package_dir, repo_root),
                "runners": discover_runner_files(package_dir, repo_root),
                "pwa": discover_pwa_signals(package_dir, repo_root),
            }
        )

    return packages


def summarize(packages: list[dict]) -> str:
    if not packages:
        return "No package.json files found. This may not be a web repo."

    lines = []
    for package in packages:
        lines.append(f"Package: {package['package_dir']}")

        scripts = package["scripts"]
        if scripts:
            lines.append("  Scripts:")
            for script in scripts:
                lines.append(f"    - [{script['type']}] {script['run']}")
        else:
            lines.append("  Scripts: none")

        runners = package["runners"]
        if runners:
            lines.append("  Runner files:")
            for runner in runners[:10]:
                lines.append(f"    - [{runner['type']}] {runner['path']}")
            if len(runners) > 10:
                lines.append(f"    - ... {len(runners) - 10} more")
        else:
            lines.append("  Runner files: none")

        pwa = package["pwa"]
        lines.append(f"  PWA readiness: {pwa['readiness']}")
        if pwa["manifest_files"]:
            lines.append(f"    manifest: {', '.join(pwa['manifest_files'][:3])}")
        if pwa["service_worker_files"]:
            lines.append(f"    service worker: {', '.join(pwa['service_worker_files'][:3])}")

    return "\n".join(lines)


def build_output(repo_root: Path, packages: list[dict]) -> dict:
    return {
        "repo_root": str(repo_root),
        "packages": packages,
        "summary": {
            "package_count": len(packages),
            "has_playwright_or_lighthouse": any(
                pkg["scripts"] or pkg["runners"] for pkg in packages
            ),
        },
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo_root", nargs="?", default=".")
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    if not repo_root.exists():
        print(f"Repo root does not exist: {repo_root}", file=sys.stderr)
        return 1

    packages = discover_packages(repo_root)

    if args.as_json:
        print(json.dumps(build_output(repo_root, packages), indent=2))
    else:
        print(summarize(packages))

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
