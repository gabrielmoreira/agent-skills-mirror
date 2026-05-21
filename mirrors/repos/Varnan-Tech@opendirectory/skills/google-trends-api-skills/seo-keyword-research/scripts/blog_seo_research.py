#!/usr/bin/env python3
"""
Blog SEO Research Script

Complete workflow: research keywords -> build structure -> output blog outline.
Designed for tech/developer-focused blog content.

Usage:
    python blog_seo_research.py "kubernetes deployment"
    python blog_seo_research.py "AI code review" --geo US
    python blog_seo_research.py "rust programming" --full --output outline.md

Requirements:
    pip install requests

Environment:
    SERPAPI_KEY - your SerpApi API key (required)
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: 'requests' package required. Install with: pip install requests")
    sys.exit(1)

API_BASE = "https://serpapi.com/search"
CACHE_DIR = Path.home() / ".cache" / "seo-keyword-research"
CACHE_DAYS = 7
CURRENT_YEAR = datetime.now().year

QUESTION_WORDS = ("how", "what", "why", "when", "where", "which", "can", "is", "does", "should")


def get_api_key():
    key = os.environ.get("SERPAPI_KEY")
    if not key:
        print("Error: SERPAPI_KEY environment variable not set.")
        print("Get a free key at https://serpapi.com/ (250 searches/month)")
        sys.exit(1)
    return key


def cached_api_call(query, data_type, api_key, geo="", date="today 3-m"):
    """Make an API call with file-based caching."""
    safe = f"{query}_{data_type}_{geo}_{date}".replace(" ", "_").replace("/", "_")
    cache_path = CACHE_DIR / f"{safe}.json"

    # Check cache
    if cache_path.exists():
        try:
            data = json.loads(cache_path.read_text(encoding="utf-8"))
            cached_at = datetime.fromisoformat(data.get("_cached_at", "2000-01-01"))
            if datetime.now() - cached_at < timedelta(days=CACHE_DAYS):
                return data, True
        except (json.JSONDecodeError, ValueError):
            pass

    # Fresh API call
    params = {
        "engine": "google_trends",
        "q": query,
        "data_type": data_type,
        "date": date,
        "api_key": api_key,
    }
    if geo:
        params["geo"] = geo

    resp = requests.get(API_BASE, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    if data.get("search_metadata", {}).get("status") != "Success":
        return None, False

    # Save cache
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    data["_cached_at"] = datetime.now().isoformat()
    cache_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data, False


def research_keywords(topic, api_key, geo="", date="today 3-m", full=False):
    """Run the complete keyword research workflow."""
    credits_used = 0
    results = {
        "topic": topic,
        "primary_keyword": None,
        "priority": None,
        "breakout": [],
        "high_growth": [],
        "moderate": [],
        "long_tail": [],
        "top_queries": [],
        "h2_topics": [],
        "trend": None,
    }

    # Step 1: RELATED_QUERIES
    print(f"\n[1/{'3' if full else '2'}] Finding keywords...")
    rq_data, was_cached = cached_api_call(topic, "RELATED_QUERIES", api_key, geo, date)
    if not was_cached:
        credits_used += 1

    if rq_data:
        rq = rq_data.get("related_queries", {})
        for item in rq.get("rising", []):
            query = item.get("query", "")
            fv = item.get("formatted_value", "")

            if fv == "Breakout":
                results["breakout"].append({"query": query, "growth": "Breakout (5000%+)"})
            elif "%" in fv:
                pct = int(fv.replace("+", "").replace("%", "").replace(",", ""))
                if pct >= 100:
                    results["high_growth"].append({"query": query, "growth": fv})
                elif pct >= 50:
                    results["moderate"].append({"query": query, "growth": fv})

            if query.lower().startswith(QUESTION_WORDS):
                results["long_tail"].append(query)

        for item in rq.get("top", []):
            query = item.get("query", "")
            results["top_queries"].append({"query": query, "score": item.get("value", 0)})
            if query.lower().startswith(QUESTION_WORDS) and query not in results["long_tail"]:
                results["long_tail"].append(query)

    # Select primary keyword
    if results["breakout"]:
        results["primary_keyword"] = results["breakout"][0]["query"]
        results["priority"] = "BREAKOUT"
    elif results["high_growth"]:
        results["primary_keyword"] = results["high_growth"][0]["query"]
        results["priority"] = "HIGH_GROWTH"
    elif results["top_queries"]:
        results["primary_keyword"] = results["top_queries"][0]["query"]
        results["priority"] = "TOP"
    else:
        results["primary_keyword"] = topic
        results["priority"] = "ORIGINAL"

    # Step 2: RELATED_TOPICS
    print(f"[2/{'3' if full else '2'}] Building content structure...")
    rt_data, was_cached = cached_api_call(topic, "RELATED_TOPICS", api_key, geo, date)
    if not was_cached:
        credits_used += 1

    if rt_data:
        rt = rt_data.get("related_topics", {})
        for item in rt.get("rising", []) + rt.get("top", []):
            if "topic" in item:
                title = item["topic"]["title"]
                if title not in [t["title"] for t in results["h2_topics"]]:
                    results["h2_topics"].append({
                        "title": title,
                        "growth": item.get("formatted_value", ""),
                    })

    # Step 3: TIMESERIES (optional)
    if full:
        print("[3/3] Validating trend direction...")
        ts_data, was_cached = cached_api_call(topic, "TIMESERIES", api_key, geo, "today 12-m")
        if not was_cached:
            credits_used += 1

        if ts_data:
            timeline = ts_data.get("interest_over_time", {}).get("timeline_data", [])
            values = []
            for entry in timeline:
                if entry.get("values"):
                    values.append(entry["values"][0].get("extracted_value", 0))

            if len(values) >= 4:
                mid = len(values) // 2
                early = sum(values[:mid]) / mid
                recent = sum(values[mid:]) / (len(values) - mid)
                change = ((recent - early) / max(early, 1)) * 100

                if recent > early * 1.1:
                    direction = "RISING"
                elif recent < early * 0.9:
                    direction = "DECLINING"
                else:
                    direction = "STABLE"

                results["trend"] = {
                    "direction": direction,
                    "early_avg": round(early, 1),
                    "recent_avg": round(recent, 1),
                    "change_pct": round(change, 1),
                }

    results["credits_used"] = credits_used
    return results


def generate_outline(results):
    """Generate a markdown blog outline from research results."""
    pk = results["primary_keyword"]
    h2s = [t["title"] for t in results["h2_topics"][:5]]
    h3s = results["long_tail"][:12]

    lines = []
    lines.append(f"# Blog Outline: {pk}")
    lines.append("")
    lines.append(f"**Primary Keyword**: {pk} ({results['priority']})")
    lines.append(f"**Target Length**: 1500-2500 words")
    lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Title
    lines.append(f"## Title")
    lines.append(f"```")
    lines.append(f"{pk.title()} — Complete Guide {CURRENT_YEAR}")
    lines.append(f"```")
    lines.append("")

    # Meta
    secondary = ""
    if results["high_growth"]:
        secondary = results["high_growth"][0]["query"]
    elif results["top_queries"]:
        secondary = results["top_queries"][0]["query"]

    meta_parts = [f"Learn about {pk}"]
    if h2s:
        meta_parts.append(f"Covers {', '.join(h2s[:3])}")
    meta = ". ".join(meta_parts) + "."

    lines.append(f"## Meta Description")
    lines.append(f"```")
    lines.append(meta[:160])
    lines.append(f"```")
    lines.append("")

    # Blog structure
    lines.append(f"## Blog Structure")
    lines.append("")
    lines.append(f"### Introduction (150 words)")
    lines.append(f"- Include \"{pk}\" in first 100 words")
    lines.append(f"- Hook with a problem or trending statistic")
    lines.append(f"- Preview the key topics covered")
    lines.append("")

    h3_idx = 0
    for i, h2 in enumerate(h2s, 1):
        lines.append(f"### {h2}")

        # Assign relevant H3s
        assigned = 0
        while h3_idx < len(h3s) and assigned < 3:
            lines.append(f"- H3: {h3s[h3_idx]}")
            lines.append(f"  - Answer in 150-200 words")
            h3_idx += 1
            assigned += 1

        # If no long-tail matched, suggest generic H3s
        if assigned == 0:
            lines.append(f"- H3: What Is {h2}?")
            lines.append(f"- H3: How {h2} Works")

        lines.append("")

    lines.append(f"### Conclusion (100 words)")
    lines.append(f"- Summarize key points")
    lines.append(f"- Mention \"{pk}\" once")
    lines.append(f"- Include call-to-action")
    lines.append("")

    # Keywords summary
    lines.append("---")
    lines.append("")
    lines.append("## Keywords to Include")
    lines.append("")
    lines.append(f"**Primary** (1-2% density): {pk}")

    secondaries = []
    for kw in (results["high_growth"] + results["moderate"])[:4]:
        secondaries.append(kw["query"])
    if secondaries:
        lines.append(f"**Secondary** (0.5-1% each): {', '.join(secondaries)}")

    if results["long_tail"]:
        lines.append(f"**Long-tail** (H3 headings): {', '.join(results['long_tail'][:6])}")

    return "\n".join(lines)


def print_report(results):
    """Print a formatted research report to terminal."""
    pk = results["primary_keyword"]
    pr = results["priority"]

    print("\n" + "=" * 60)
    print(f"  SEO KEYWORD RESEARCH: {results['topic']}")
    print("=" * 60)
    print(f"\n  PRIMARY KEYWORD: {pk}")
    print(f"  PRIORITY:        {pr}")

    if results["trend"]:
        t = results["trend"]
        print(f"  TREND:           {t['direction']} ({t['change_pct']:+.1f}%)")

    if results["breakout"]:
        print("\n  BREAKOUT KEYWORDS:")
        for kw in results["breakout"]:
            print(f"    >>> {kw['query']}")

    if results["high_growth"]:
        print("\n  HIGH-GROWTH KEYWORDS:")
        for kw in results["high_growth"][:5]:
            print(f"    >> {kw['query']} ({kw['growth']})")

    if results["long_tail"]:
        print("\n  LONG-TAIL (H3 candidates):")
        for q in results["long_tail"][:6]:
            print(f"    ? {q}")

    if results["h2_topics"]:
        print("\n  H2 TOPICS:")
        for t in results["h2_topics"][:5]:
            growth = f" — {t['growth']}" if t["growth"] else ""
            print(f"    # {t['title']}{growth}")

    print(f"\n  API CREDITS USED: {results['credits_used']}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Blog SEO keyword research via Google Trends")
    parser.add_argument("topic", help="Blog topic to research")
    parser.add_argument("--geo", default="", help="Geographic filter (e.g., US, GB)")
    parser.add_argument("--date", default="today 3-m", help="Time range (default: today 3-m)")
    parser.add_argument("--full", action="store_true", help="Include trend validation (+1 API credit)")
    parser.add_argument("--output", "-o", help="Save blog outline to file (markdown)")
    parser.add_argument("--json", action="store_true", help="Output raw results as JSON")

    args = parser.parse_args()
    api_key = get_api_key()

    print(f"Researching: \"{args.topic}\"")
    print(f"Region: {args.geo or 'Worldwide'} | Date: {args.date}")

    results = research_keywords(args.topic, api_key, args.geo, args.date, args.full)

    if args.json:
        output = {k: v for k, v in results.items() if k != "credits_used"}
        print(json.dumps(output, indent=2))
        return

    print_report(results)

    # Generate and display outline
    outline = generate_outline(results)
    print("\n" + outline)

    if args.output:
        Path(args.output).write_text(outline, encoding="utf-8")
        print(f"\nOutline saved to: {args.output}")


if __name__ == "__main__":
    main()
