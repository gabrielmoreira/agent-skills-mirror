#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import html
import re
import subprocess
import tarfile
import urllib.request
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = SKILL_ROOT / "assets" / "cheatsheet-template.html"


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "paper"


def arxiv_id(value: str) -> str:
    value = value.strip()
    value = value.removeprefix("https://arxiv.org/abs/")
    value = value.removeprefix("https://arxiv.org/pdf/")
    value = value.removesuffix(".pdf")
    value = re.sub(r"v\d+$", "", value)
    return value


def safe_extract_tar(tar_path: Path, dest: Path) -> None:
    dest_resolved = dest.resolve()
    with tarfile.open(tar_path) as archive:
        for member in archive.getmembers():
            target = (dest / member.name).resolve()
            if target != dest_resolved and dest_resolved not in target.parents:
                raise RuntimeError(f"Unsafe tar member path: {member.name}")
        try:
            archive.extractall(dest, filter="data")
        except TypeError:
            archive.extractall(dest)


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as response:
        dest.write_bytes(response.read())


def run(cmd: list[str], cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def try_run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a repeatable paper2html workspace with source-boundary notes."
    )
    parser.add_argument("--title", required=True, help="Paper title.")
    parser.add_argument("--slug", help="Output slug. Defaults to title slug.")
    parser.add_argument(
        "--out",
        help="Exact output directory. Defaults to <out-root>/<slug>-html-YYYYMMDD.",
    )
    parser.add_argument(
        "--out-root",
        default=str(Path.cwd()),
        help="Root for default output directory.",
    )
    parser.add_argument("--arxiv", help="arXiv id or URL. Downloads PDF and source.")
    parser.add_argument("--github", help="Public GitHub repository URL to shallow clone.")
    parser.add_argument(
        "--public-source",
        action="append",
        default=[],
        help="Additional public evidence URL. Repeatable.",
    )
    parser.add_argument("--publish-to", default="", help="Intended /research/ path.")
    parser.add_argument(
        "--private-only",
        action="store_true",
        help="Mark the workspace private-only; do not publish publicly.",
    )
    parser.add_argument(
        "--template",
        default=str(DEFAULT_TEMPLATE),
        help="HTML template to copy to index.html.",
    )
    args = parser.parse_args()

    today = dt.date.today().strftime("%Y%m%d")
    slug = args.slug or slugify(args.title)
    out = Path(args.out) if args.out else Path(args.out_root) / f"{slug}-html-{today}"
    out = out.expanduser().resolve()

    notes = out / "notes"
    source = out / "source"
    repo = out / "repo"
    assets = out / "assets"
    for path in [notes, source, repo, assets / "raw", assets / "optimized"]:
        path.mkdir(parents=True, exist_ok=True)

    public_sources = list(args.public_source)
    source_status: list[str] = []

    if args.arxiv:
        aid = arxiv_id(args.arxiv)
        public_sources.extend(
            [f"https://arxiv.org/abs/{aid}", f"https://arxiv.org/pdf/{aid}"]
        )
        pdf_dest = source / f"arxiv-{aid}.pdf"
        src_dest = source / f"arxiv-{aid}-source.tar"
        download(f"https://arxiv.org/pdf/{aid}", pdf_dest)
        download(f"https://arxiv.org/e-print/{aid}", src_dest)
        unpacked = source / "unpacked"
        unpacked.mkdir(exist_ok=True)
        safe_extract_tar(src_dest, unpacked)
        source_status.append(f"- arXiv PDF/source: downloaded and unpacked for {aid}.")

    if args.github:
        public_sources.append(args.github)
        clone_name = slugify(Path(args.github.rstrip("/")).name.removesuffix(".git"))
        clone_dest = repo / clone_name
        if not clone_dest.exists():
            result = try_run(["git", "clone", "--depth", "1", args.github, str(clone_dest)])
            if result.returncode == 0:
                source_status.append(f"- GitHub: cloned to repo/{clone_name}.")
            else:
                message = (result.stderr or result.stdout or "git clone failed").strip()
                source_status.append(
                    f"- GitHub: unavailable at bootstrap time; clone exited {result.returncode}: "
                    f"{message.splitlines()[-1]}"
                )
                (notes / "github-status.txt").write_text(
                    "\n".join(
                        [
                            f"URL: {args.github}",
                            f"Clone destination: repo/{clone_name}",
                            f"Exit code: {result.returncode}",
                            "",
                            "stdout:",
                            result.stdout.strip(),
                            "",
                            "stderr:",
                            result.stderr.strip(),
                        ]
                    )
                    + "\n",
                    encoding="utf-8",
                )
        else:
            source_status.append(f"- GitHub: existing clone found at repo/{clone_name}.")

    template = Path(args.template).expanduser().resolve()
    index_path = out / "index.html"
    if template.exists() and not index_path.exists():
        title = args.title.strip()
        short_title = title if len(title) <= 48 else f"{title[:45]}..."
        source_badge = (
            f"arXiv {arxiv_id(args.arxiv)}"
            if args.arxiv
            else "GitHub source" if args.github else "Source pending"
        )
        replacements = {
            "__TITLE__": title,
            "__SHORT_TITLE__": short_title,
            "__DESCRIPTION__": f"Source-grounded deep-reading notes for {title}",
            "__DATE__": dt.date.today().isoformat(),
            "__TAGS__": "paper-reading,research",
            "__BADGE_1__": "Deep Reading",
            "__BADGE_2__": source_badge,
            "__SUBTITLE__": "Source-grounded Chinese deep-reading notes",
        }
        index_html = template.read_text(encoding="utf-8")
        for placeholder, value in replacements.items():
            index_html = index_html.replace(placeholder, html.escape(value, quote=True))
        index_path.write_text(index_html, encoding="utf-8")

    visibility = "private-only" if args.private_only else "public blog HTML"
    boundary = [
        "Source Boundary Note",
        "",
        "Deliverable:",
        f"- Type: {visibility}.",
        f"- Title: {args.title}.",
        f"- Target path: {args.publish_to or '(not decided)'}.",
        "",
        "Paper locator from user:",
        f"- {args.title}",
        "",
        "Primary reading sources:",
        f"- arXiv: {args.arxiv or '(not provided)'}",
        f"- GitHub: {args.github or '(not provided)'}",
        "- Local/private materials: (fill if any)",
        "",
        "Source retrieval status:",
        *(source_status or ["- (not recorded)"]),
        "",
        "Public evidence sources allowed in final page:",
    ]
    boundary.extend(f"- {url}" for url in dict.fromkeys(public_sources))
    boundary.extend(
        [
            "",
            "Forbidden in public page:",
            "- Local absolute paths.",
            "- Private TeX/source file names.",
            "- Hidden review metadata, unpublished logs, prompts outside public releases.",
            "",
            "Version note for HTML:",
            f"- Based on the public sources above; retrieved on {dt.date.today().isoformat()}.",
        ]
    )
    (notes / "source-boundary.md").write_text("\n".join(boundary) + "\n", encoding="utf-8")

    (notes / "material-pack.md").write_text(
        "\n".join(
            [
                "Material Pack Summary",
                "",
                "Metadata:",
                f"- Title: {args.title}",
                "- Authors:",
                "- Venue/status:",
                "",
                "Core method / modeling:",
                "-",
                "",
                "Experiments:",
                "-",
                "",
                "Key evidence:",
                "-",
                "",
                "Evidence-local figure notes:",
                "- Figure X: what it itself shows / what it must not overclaim.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    (notes / "figure-table-map.md").write_text(
        "\n".join(
            [
                "Figure / Table Evidence Map",
                "",
                "Each discovered paper figure needs either an Included marker matching the HTML data-figure basename or a Waiver reason.",
                "",
                "| Item | Source/page | Original caption | What it itself shows | Included marker | Waiver reason |",
                "| --- | --- | --- | --- | --- | --- |",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    (notes / "grounding-anchor.md").write_text(
        "\n".join(
            [
                "Grounding Anchor",
                "",
                "1. Human knowledge boundary",
                "- Status (solved / partially solved / unsolved):",
                "- Public evidence URL(s):",
                "- Boundary statement:",
                "",
                "2. Real contribution",
                "- One sentence from an independent reviewer perspective, relative to section 1:",
                "",
                "3. Writing anchor",
                "- Sections that establish the contribution:",
                "- Sections that are source-faithful background only:",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(out)
    print(f"Source boundary: {notes / 'source-boundary.md'}")
    print(f"Template index:   {out / 'index.html'}")


if __name__ == "__main__":
    main()
