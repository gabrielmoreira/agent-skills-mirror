"""Search the bundled catalog without loading every prompt. Python 3.10+."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["search", "show", "list"])
    parser.add_argument("query", nargs="?", default="")
    parser.add_argument("--series", help="AG, M, K, Z, H, L, V, X, R, O")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    data = json.loads((ROOT / "references/catalog.json").read_text(encoding="utf-8"))
    rows = data["entries"]
    if args.series:
        series = args.series.upper()
        if series not in {m["id"] for m in data["series"]}:
            parser.error("Unknown series: " + args.series)
        rows = [e for e in rows if e["series"] == series]
    if args.limit < 1:
        parser.error("--limit must be positive")
    if args.command in {"show", "search"} and not args.query.strip():
        parser.error("query / style ID is required")
    query = args.query.casefold().strip()
    if args.command == "show":
        rows = [e for e in rows if e["id"].casefold() == query]
    elif args.command == "search":
        terms = query.split()
        rows = [e for e in rows if all(t in " ".join([
            e["id"], e["name"], e["category"], e["description"],
            e["fit"], *e["tags"]]).casefold() for t in terms)]
        rows.sort(key=lambda e: e["id"].casefold() != query)
    if not rows:
        print("No matching styles. B6 is an example, not a catalog entry.", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(rows[:args.limit], ensure_ascii=False, indent=2))
    elif args.command == "show":
        print((ROOT / rows[0]["file"]).read_text(encoding="utf-8"))
    else:
        for e in rows[:args.limit]:
            print(f'{e["id"]:>4}  {e["name"]}  [{e["series"]}]  ' + ("有静帧" if e["image"] else "文字参考"))
            print(f'      {e["description"]}\n      {e["file"]}')
        print(f"\n{len(rows)} matches; showing {min(len(rows), args.limit)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
