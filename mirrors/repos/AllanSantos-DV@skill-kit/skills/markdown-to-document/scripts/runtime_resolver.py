"""
Generic runtime dependency discovery script.

Usage:
    python runtime_resolver.py java --min-version 11
    python runtime_resolver.py pandoc
    python runtime_resolver.py libreoffice --extra-paths "/opt/libreoffice" "C:\\LibreOffice"
    python runtime_resolver.py node --min-version 18

Supported runtimes: java, pandoc, libreoffice, node

Output: JSON with discovery results:
    {"found": true, "version": "17.0.2", "path": "/usr/bin/java", "all_installations": [...]}

Exit codes:
    0: Runtime found and meets version requirements.
    1: Runtime not found or version too low.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import subprocess
import sys
from pathlib import Path

RUNTIMES: dict[str, dict] = {
    "java": {
        "env_vars": ["JAVA_HOME"],
        "commands": ["java"],
        "version_args": ["-version"],
        "version_regex": r'version "(\d+)(?:\.(\d+))?(?:\.(\d+))?',
        "version_stream": "stderr",
        "known_paths": {
            "Windows": [
                r"C:\Program Files\Java\*",
                r"C:\Program Files\Eclipse Adoptium\*",
                r"C:\Program Files\Microsoft\jdk-*",
                r"C:\Program Files\Amazon Corretto\*",
                r"C:\Program Files\Zulu\*",
            ],
            "Linux": [
                "/usr/lib/jvm/*",
                "/usr/java/*",
                "/opt/java/*",
            ],
            "Darwin": [
                "/Library/Java/JavaVirtualMachines/*/Contents/Home",
                "/usr/local/opt/openjdk*/libexec/openjdk.jdk/Contents/Home",
            ],
        },
        "bin_subdir": "bin",
        "executable": "java.exe" if platform.system() == "Windows" else "java",
    },
    "pandoc": {
        "env_vars": [],
        "commands": ["pandoc"],
        "version_args": ["--version"],
        "version_regex": r"pandoc(?:\.exe)?\s+(\d+)\.(\d+)(?:\.(\d+))?",
        "version_stream": "stdout",
        "known_paths": {
            "Windows": [
                r"C:\Program Files\Pandoc\*",
                r"C:\Users\*\AppData\Local\Pandoc\*",
            ],
            "Linux": ["/usr/bin", "/usr/local/bin"],
            "Darwin": ["/usr/local/bin", "/opt/homebrew/bin"],
        },
        "bin_subdir": None,
        "executable": "pandoc.exe" if platform.system() == "Windows" else "pandoc",
    },
    "libreoffice": {
        "env_vars": [],
        "commands": ["libreoffice", "soffice"],
        "version_args": ["--version"],
        "version_regex": r"(\d+)\.(\d+)(?:\.(\d+))?",
        "version_stream": "stdout",
        "known_paths": {
            "Windows": [
                r"C:\Program Files\LibreOffice\program",
                r"C:\Program Files (x86)\LibreOffice\program",
            ],
            "Linux": ["/usr/bin", "/usr/lib/libreoffice/program"],
            "Darwin": ["/Applications/LibreOffice.app/Contents/MacOS"],
        },
        "bin_subdir": None,
        "executable": "soffice.exe" if platform.system() == "Windows" else "soffice",
    },
    "node": {
        "env_vars": ["NODE_HOME"],
        "commands": ["node"],
        "version_args": ["--version"],
        "version_regex": r"v(\d+)\.(\d+)\.(\d+)",
        "version_stream": "stdout",
        "known_paths": {
            "Windows": [
                r"C:\Program Files\nodejs",
                r"C:\Program Files (x86)\nodejs",
            ],
            "Linux": ["/usr/bin", "/usr/local/bin"],
            "Darwin": ["/usr/local/bin", "/opt/homebrew/bin"],
        },
        "bin_subdir": None,
        "executable": "node.exe" if platform.system() == "Windows" else "node",
    },
}


def parse_version(version_str: str) -> tuple[int, ...]:
    """Parse a version string like '17.0.2' into a tuple of ints."""
    parts = re.findall(r"\d+", version_str)
    return tuple(int(p) for p in parts[:3])


def get_version(executable: str, config: dict) -> str | None:
    """Run the executable and extract the version string."""
    try:
        result = subprocess.run(
            [executable] + config["version_args"],
            capture_output=True, text=True, timeout=15
        )
        output = result.stderr if config["version_stream"] == "stderr" else result.stdout
        if not output:
            output = result.stdout + result.stderr
        match = re.search(config["version_regex"], output)
        if match:
            groups = [g for g in match.groups() if g is not None]
            return ".".join(groups)
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass
    return None


def find_installations(runtime_name: str, extra_paths: list[str] | None = None) -> list[dict]:
    """Find all installations of a runtime."""
    config = RUNTIMES[runtime_name]
    system = platform.system()
    installations: list[dict] = []
    seen_paths: set[str] = set()

    def try_executable(exe_path: str) -> None:
        exe_path = str(Path(exe_path).resolve())
        if exe_path in seen_paths:
            return
        seen_paths.add(exe_path)
        if not Path(exe_path).is_file():
            return
        version = get_version(exe_path, config)
        if version:
            installations.append({"path": exe_path, "version": version})

    # 1. Check env vars
    for env_var in config["env_vars"]:
        env_val = os.environ.get(env_var)
        if env_val:
            base = Path(env_val)
            if config["bin_subdir"]:
                candidate = base / config["bin_subdir"] / config["executable"]
            else:
                candidate = base / config["executable"]
            try_executable(str(candidate))

    # 2. Check PATH
    for cmd in config["commands"]:
        version = get_version(cmd, config)
        if version:
            # Resolve full path
            import shutil
            full_path = shutil.which(cmd)
            if full_path:
                path_str = str(Path(full_path).resolve())
                if path_str not in seen_paths:
                    seen_paths.add(path_str)
                    installations.append({"path": path_str, "version": version})

    # 3. Check known OS paths
    known = config["known_paths"].get(system, [])
    import glob
    for pattern in known:
        for match_path in glob.glob(pattern):
            base = Path(match_path)
            if config["bin_subdir"]:
                candidate = base / config["bin_subdir"] / config["executable"]
            else:
                candidate = base / config["executable"]
            try_executable(str(candidate))

    # 4. Check extra paths
    for extra in extra_paths or []:
        base = Path(extra)
        if config["bin_subdir"]:
            candidate = base / config["bin_subdir"] / config["executable"]
        else:
            candidate = base / config["executable"]
        try_executable(str(candidate))
        # Also check without bin subdir
        try_executable(str(base / config["executable"]))

    return installations


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Discover runtime dependencies on the current system."
    )
    parser.add_argument(
        "runtime",
        choices=list(RUNTIMES.keys()),
        help=f"Runtime to check: {', '.join(RUNTIMES.keys())}."
    )
    parser.add_argument(
        "--min-version",
        type=str,
        default=None,
        help="Minimum required version (e.g., '11', '17.0.2')."
    )
    parser.add_argument(
        "--extra-paths",
        nargs="*",
        default=[],
        help="Additional paths to search for the runtime."
    )
    args = parser.parse_args()

    installations = find_installations(args.runtime, args.extra_paths)

    if not installations:
        result = {
            "found": False,
            "version": None,
            "path": None,
            "all_installations": [],
            "runtime": args.runtime,
        }
        print(json.dumps(result, indent=2))
        sys.exit(1)

    # Sort by version descending
    installations.sort(
        key=lambda x: parse_version(x["version"]),
        reverse=True
    )

    best = installations[0]
    found = True

    # Check minimum version
    if args.min_version:
        min_ver = parse_version(args.min_version)
        best_ver = parse_version(best["version"])
        if best_ver < min_ver:
            # Find any installation meeting the minimum
            suitable = [i for i in installations if parse_version(i["version"]) >= min_ver]
            if suitable:
                best = suitable[0]
            else:
                found = False

    result = {
        "found": found,
        "version": best["version"],
        "path": best["path"],
        "all_installations": installations,
        "runtime": args.runtime,
    }

    if args.min_version and not found:
        result["error"] = f"Found {args.runtime} {best['version']} but minimum required is {args.min_version}"

    print(json.dumps(result, indent=2))
    sys.exit(0 if found else 1)


if __name__ == "__main__":
    main()
