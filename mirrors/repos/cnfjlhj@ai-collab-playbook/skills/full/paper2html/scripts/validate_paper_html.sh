#!/usr/bin/env bash
set -Eeuo pipefail

usage() {
  cat <<'USAGE'
Usage:
  validate_paper_html.sh <index.html> [--public]

Checks:
  - file exists and is HTML
  - no common placeholders
  - no private local-source leaks in public mode
  - all seven MIT Other Discussion Roles occur exactly once
  - each role preserves its complete source prompt verbatim
  - each role has a substantive response and roles keep the source order
  - Other Discussion Roles is the final substantive section before references
  - figure inventory entries match HTML data-figure markers or carry waivers
  - KaTeX auto-render creates math nodes and no katex-error
  - desktop and mobile screenshots can be rendered by Chrome
USAGE
}

HTML_PATH="${1:-}"
MODE_PUBLIC=0
shift || true
for arg in "$@"; do
  case "$arg" in
    --public) MODE_PUBLIC=1 ;;
    --help|-h) usage; exit 0 ;;
    *) echo "Unknown option: $arg" >&2; usage; exit 2 ;;
  esac
done

if [[ -z "$HTML_PATH" ]]; then usage; exit 2; fi
if [[ ! -f "$HTML_PATH" ]]; then echo "Missing HTML file: $HTML_PATH" >&2; exit 1; fi
if [[ "${HTML_PATH##*.}" != "html" ]]; then echo "Expected .html: $HTML_PATH" >&2; exit 1; fi

python3 - "$HTML_PATH" "$MODE_PUBLIC" <<'PY'
import re
import sys
import html as html_lib
from html.parser import HTMLParser
from pathlib import Path

html_path = Path(sys.argv[1])
public = sys.argv[2] == "1"
html = html_path.read_text(encoding="utf-8", errors="replace")

role_prompts = {
    "scientific-peer-reviewer": "The paper has not been published yet and is currently submitted to a top conference where you’ve been assigned as a peer reviewer. Complete a full review of the paper answering all prompts of the official review form of the top venue in this research area (e.g., NeurIPS). This includes recommending whether to accept or reject the paper.",
    "archaeologist": "This paper was found buried under ground in the desert. You’re an archeologist who must determine where this paper sits in the context of previous and subsequent work. Find and report on one older paper cited within the current paper that substantially influenced the current paper and one newer paper that cites this current paper.",
    "academic-researcher": "You’re a researcher who is working on a new project in this area. Propose an imaginary follow-up project not just based on the current but only possible due to the existence and success of the current paper.",
    "industry-practitioner": "You work at a company or organization developing an application or product of your choice (that has not already been suggested in a prior session). Bring a convincing pitch for why you should be paid to implement the method in the paper, and discuss at least one positive and negative impact of this application.",
    "hacker": "You’re a hacker who needs a demo of this paper ASAP. Implement a small part or simplified version of the paper on a small dataset or toy problem. Prepare to share the core code of the algorithm to the class and demo your implementation. Do not simply download and run an existing implementation – though you are welcome to use (and give credit to) an existing implementation for “backbone” code.",
    "private-investigator": "You are a detective who needs to run a background check on one of the paper’s authors. Where have they worked? What did they study? What previous projects might have led to working on this one? What motivated them to work on this project? Feel free to contact the authors, but remember to be courteous, polite, and on-topic.",
    "social-impact-assessor": "Identify how this paper self-assesses its (likely positive) impact on the world. Have any additional positive social impacts left out? What are possible negative social impacts that were overlooked or omitted?",
}

def normalize_text(value: str) -> str:
    return " ".join(html_lib.unescape(value).split())

class DiscussionRoleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.current_role = None
        self.prompt_depth = 0
        self.insight_depth = 0
        self.prompts = {role: [] for role in role_prompts}
        self.insights = {role: [] for role in role_prompts}
        self.counts = {role: 0 for role in role_prompts}
        self.seen_roles = []

        self.section_ids = []
        self.figure_markers = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "section":
            self.section_ids.append(attrs.get("id", ""))
        if tag == "figure":
            marker = attrs.get("data-figure")
            if marker:
                self.figure_markers.append(Path(marker).name)
        role = attrs.get("data-discussion-role")
        if role in self.counts:
            self.current_role = role
            self.counts[role] += 1
            self.seen_roles.append(role)
        classes = set(attrs.get("class", "").split())
        if self.current_role and "role-prompt" in classes:
            self.prompt_depth += 1
        if self.current_role and "role-insight" in classes:
            self.insight_depth += 1

    def handle_endtag(self, tag):
        if self.prompt_depth and tag == "blockquote":
            self.prompt_depth -= 1
        if self.insight_depth and tag == "div":
            self.insight_depth -= 1
        if tag == "article" and self.current_role:
            self.current_role = None

    def handle_data(self, data):
        if self.current_role and self.prompt_depth:
            self.prompts[self.current_role].append(data)
        if self.current_role and self.insight_depth:
            self.insights[self.current_role].append(data)

role_parser = DiscussionRoleParser()
role_parser.feed(html)
expected_order = list(role_prompts)
if role_parser.seen_roles != expected_order:
    print(
        f"{html_path}: discussion role order mismatch: {role_parser.seen_roles}; "
        f"expected {expected_order}",
        file=sys.stderr,
    )
    raise SystemExit(1)
for role, expected_prompt in role_prompts.items():
    count = role_parser.counts[role]
    if count != 1:
        print(f"{html_path}: discussion role {role!r} occurs {count} times; expected exactly 1", file=sys.stderr)
        raise SystemExit(1)
    actual_prompt = normalize_text("".join(role_parser.prompts[role]))
    if actual_prompt != normalize_text(expected_prompt):
        print(f"{html_path}: verbatim prompt drift for discussion role {role!r}", file=sys.stderr)
        raise SystemExit(1)
    insight = normalize_text("".join(role_parser.insights[role]))
    if len(insight) < 120:
        print(
            f"{html_path}: discussion role {role!r} response is too short "
            f"({len(insight)} characters; expected at least 120)",
            file=sys.stderr,
        )
        raise SystemExit(1)

section_ids = role_parser.section_ids
if "discussion-roles" not in section_ids or "references" not in section_ids:
    print(f"{html_path}: missing discussion-roles or references section", file=sys.stderr)
    raise SystemExit(1)
discussion_index = section_ids.index("discussion-roles")
if section_ids[discussion_index + 1 :] != ["references"]:
    print(
        f"{html_path}: Other Discussion Roles must be the final substantive section before "
        f"Reference / Evidence; trailing sections: {section_ids[discussion_index + 1 :]}",
        file=sys.stderr,
    )
    raise SystemExit(1)

figure_map_path = html_path.parent / "notes" / "figure-table-map.md"
if not figure_map_path.is_file():
    print(f"{html_path}: missing figure inventory: {figure_map_path}", file=sys.stderr)
    raise SystemExit(1)

empty_values = {"", "-", "tbd", "todo", "n/a"}
included_markers = set()
for line_no, line in enumerate(figure_map_path.read_text(encoding="utf-8").splitlines(), start=1):
    if not line.lstrip().startswith("|"):
        continue
    cells = [cell.strip().replace(r"\|", "|") for cell in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
    if not cells or cells[0].lower() == "item" or all(set(cell) <= {"-", ":"} for cell in cells):
        continue
    if len(cells) != 6:
        print(f"{figure_map_path}:{line_no}: expected 6 table columns, got {len(cells)}", file=sys.stderr)
        raise SystemExit(1)
    item, _source, _caption, _shows, included, waiver = cells
    normalized_included = included.strip("` ")
    if normalized_included.lower() not in empty_values:
        marker = Path(normalized_included).name
        if marker != normalized_included:
            print(f"{figure_map_path}:{line_no}: Included marker must be a basename", file=sys.stderr)
            raise SystemExit(1)
        included_markers.add(marker)
    elif waiver.strip().lower() in empty_values:
        print(f"{figure_map_path}:{line_no}: {item!r} needs an Included marker or Waiver reason", file=sys.stderr)
        raise SystemExit(1)

html_markers = role_parser.figure_markers
if len(html_markers) != len(set(html_markers)):
    print(f"{html_path}: duplicate data-figure markers: {html_markers}", file=sys.stderr)
    raise SystemExit(1)
missing_markers = sorted(included_markers - set(html_markers))
unexpected_markers = sorted(set(html_markers) - included_markers)
if missing_markers or unexpected_markers:
    print(
        f"{html_path}: figure inventory mismatch; missing={missing_markers}, "
        f"unexpected={unexpected_markers}",
        file=sys.stderr,
    )
    raise SystemExit(1)

# Base64 payloads can accidentally contain strings like TODO. Do static text
# checks on a masked copy, while browser checks still use the original file.
masked = re.sub(
    r"""(?P<prefix>\b(?:src|href)=["'])data:[^"']+(?P<suffix>["'])""",
    r"\g<prefix>data:masked\g<suffix>",
    html,
    flags=re.IGNORECASE,
)

patterns = [
    ("placeholder", re.compile(r"(__[A-Z0-9_]+__|TODO|PLACEHOLDER|FIXME|katex-error)")),
]

if public:
    patterns.append(
        (
            "local/private source leak",
            re.compile(
                r"(/home/|file://|main\.tex|main\.pdf|sections/|appendices/|figures/|"
                r"本地论文|本地 LaTeX|本地 PDF|未做外部 Web 检索|"
                r"private review draft|not public-published)"
            ),
        )
    )

for label, pattern in patterns:
    for line_no, line in enumerate(masked.splitlines(), start=1):
        match = pattern.search(line)
        if match:
            print(f"{html_path}:{line_no}: {label}: {match.group(0)}", file=sys.stderr)
            raise SystemExit(1)
PY

if ! command -v google-chrome >/dev/null 2>&1; then
  echo "google-chrome not found; skipped browser render checks." >&2
  exit 0
fi

tmpdir="$(mktemp -d)"
cleanup() {
  if [[ -n "${server_pid:-}" ]]; then kill "$server_pid" >/dev/null 2>&1 || true; fi
}
trap cleanup EXIT

src_dir="$(cd "$(dirname "$HTML_PATH")" && pwd)"
src_file="$(basename "$HTML_PATH")"
port="$(python3 - <<'PY'
import socket
s = socket.socket()
s.bind(("127.0.0.1", 0))
print(s.getsockname()[1])
s.close()
PY
)"

(cd "$src_dir" && python3 -m http.server "$port" --bind 127.0.0.1 >"$tmpdir/server.log" 2>&1) &
server_pid="$!"
sleep 0.5
url="http://127.0.0.1:${port}/${src_file}"

dom="$tmpdir/dom.txt"
google-chrome --headless=new --disable-gpu --no-sandbox --dump-dom "$url" >"$dom" 2>"$tmpdir/chrome-dom.err"

if grep -q 'katex-error' "$dom"; then
  echo "Rendered DOM contains katex-error." >&2
  exit 1
fi
if ! grep -q 'class="katex' "$dom"; then
  echo "Rendered DOM contains no KaTeX nodes; check math initialization or source formulas." >&2
  exit 1
fi

google-chrome --headless=new --disable-gpu --no-sandbox --window-size=1440,1200 --screenshot="$tmpdir/desktop.png" "$url" >/dev/null 2>"$tmpdir/chrome-desktop.err"

python3 - "$url" "$tmpdir/mobile.png" <<'PY'
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

url, out = sys.argv[1], Path(sys.argv[2])
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
    page = browser.new_page(viewport={"width": 390, "height": 1000}, device_scale_factor=1, is_mobile=True)
    page.goto(url, wait_until="networkidle")
    dims = page.evaluate("""() => ({
      innerWidth,
      docClient: document.documentElement.clientWidth,
      docScroll: document.documentElement.scrollWidth,
      bodyScroll: document.body.scrollWidth
    })""")
    page.screenshot(path=str(out), full_page=False)
    browser.close()

print(dims)
if dims["docScroll"] > dims["innerWidth"]:
    raise SystemExit(f"document overflows horizontally: {dims}")
PY

echo "paper2html validation passed"
echo "Desktop screenshot: $tmpdir/desktop.png"
echo "Mobile screenshot:  $tmpdir/mobile.png"
