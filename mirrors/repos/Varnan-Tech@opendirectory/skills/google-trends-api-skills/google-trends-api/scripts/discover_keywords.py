#!/usr/bin/env python3
"""
Google Trends Keyword Discovery Script

Discovers trending keywords and related topics for a given query using SerpApi.
Designed for SEO keyword research before blog generation.

Usage:
    python discover_keywords.py "your topic"
    python discover_keywords.py "your topic" --geo US --date "today 3-m"
    python discover_keywords.py "your topic" --full  # includes timeseries validation

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
CACHE_DIR = Path.home() / ".cache" / "google-trends-api"
CACHE_DAYS = 7


def get_api_key():
    key = os.environ.get("SERPAPI_KEY")
    if not key:
        print("Error: SERPAPI_KEY environment variable not set.")
        print("Get a free key at https://serpapi.com/ (250 searches/month)")
        sys.exit(1)
    return key


def get_cache_path(query, data_type, geo, date):
    safe_name = f"{query}_{data_type}_{geo}_{date}".replace(" ", "_").replace("/", "_")
    return CACHE_DIR / f"{safe_name}.json"


def load_cache(cache_path):
    if not cache_path.exists():
        return None
    try:
        data = json.loads(cache_path.read_text(encoding="utf-8"))
        cached_at = datetime.fromisoformat(data.get("_cached_at", "2000-01-01"))
        if datetime.now() - cached_at < timedelta(days=CACHE_DAYS):
            return data
    except (json.JSONDecodeError, ValueError):
        pass
    return None


def save_cache(cache_path, data):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    data["_cached_at"] = datetime.now().isoformat()
    cache_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def query_trends(query, data_type, api_key, geo="", date="today 3-m"):
    cache_path = get_cache_path(query, data_type, geo, date)
    cached = load_cache(cache_path)
    if cached:
        print(f"  [cached] {data_type}")
        return cached

    params = {
        "engine": "google_trends",
        "q": query,
        "data_type": data_type,
        "date": date,
        "api_key": api_key,
    }
    if geo:
        params["geo"] = geo

    print(f"  [api call] {data_type}...")
    resp = requests.get(API_BASE, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    if data.get("search_metadata", {}).get("status") != "Success":
        error = data.get("error", "Unknown error")
        print(f"  [error] {data_type}: {error}")
        return None

    save_cache(cache_path, data)
    return data


def extract_keywords(related_queries):
    """Extract and categorize keywords from RELATED_QUERIES response."""
    if not related_queries:
        return {"breakout": [], "high_growth": [], "moderate": [], "long_tail": [], "top": []}

    rq = related_queries.get("related_queries", {})
    rising = rq.get("rising", [])
    top = rq.get("top", [])

    question_words = ("how", "what", "why", "when", "where", "which", "can", "is", "does", "should")

    breakout = []
    high_growth = []
    moderate = []
    long_tail = []

    for item in rising:
        query = item.get("query", "")
        formatted = item.get("formatted_value", "")

        if formatted == "Breakout":
            breakout.append({"query": query, "growth": "Breakout (5000%+)"})
        elif "%" in formatted:
            pct = int(formatted.replace("+", "").replace("%", "").replace(",", ""))
            entry = {"query": query, "growth": formatted}
            if pct >= 100:
                high_growth.append(entry)
            elif pct >= 50:
                moderate.append(entry)

        if query.lower().startswith(question_words):
            long_tail.append(query)

    # Also check top queries for long-tail
    for item in top:
        query = item.get("query", "")
        if query.lower().startswith(question_words) and query not in long_tail:
            long_tail.append(query)

    top_kws = [{"query": item["query"], "score": item.get("value", 0)} for item in top[:10]]

    return {
        "breakout": breakout,
        "high_growth": high_growth,
        "moderate": moderate,
        "long_tail": long_tail,
        "top": top_kws,
    }


def extract_topics(related_topics):
    """Extract topics from RELATED_TOPICS response."""
    if not related_topics:
        return {"rising": [], "top": []}

    rt = related_topics.get("related_topics", {})

    rising = [
        {"title": item["topic"]["title"], "type": item["topic"].get("type", "Topic"),
         "growth": item.get("formatted_value", "")}
        for item in rt.get("rising", [])
        if "topic" in item
    ]

    top = [
        {"title": item["topic"]["title"], "type": item["topic"].get("type", "Topic"),
         "score": item.get("extracted_value", 0)}
        for item in rt.get("top", [])
        if "topic" in item
    ]

    return {"rising": rising[:10], "top": top[:10]}


def check_trend_direction(timeseries_data):
    """Analyze TIMESERIES data to determine if trend is rising or falling."""
    if not timeseries_data:
        return None

    timeline = timeseries_data.get("interest_over_time", {}).get("timeline_data", [])
    if len(timeline) < 4:
        return None

    values = [entry["values"][0]["extracted_value"] for entry in timeline if entry.get("values")]
    if not values:
        return None

    midpoint = len(values) // 2
    first_half_avg = sum(values[:midpoint]) / midpoint
    second_half_avg = sum(values[midpoint:]) / (len(values) - midpoint)

    if second_half_avg > first_half_avg * 1.1:
        direction = "RISING"
    elif second_half_avg < first_half_avg * 0.9:
        direction = "DECLINING"
    else:
        direction = "STABLE"

    return {
        "direction": direction,
        "early_avg": round(first_half_avg, 1),
        "recent_avg": round(second_half_avg, 1),
        "change_pct": round(((second_half_avg - first_half_avg) / max(first_half_avg, 1)) * 100, 1),
    }


def select_primary_keyword(keywords, original_query):
    """Select the best primary keyword for blog targeting."""
    if keywords["breakout"]:
        return keywords["breakout"][0]["query"], "BREAKOUT"
    if keywords["high_growth"]:
        return keywords["high_growth"][0]["query"], "HIGH_GROWTH"
    if keywords["top"]:
        return keywords["top"][0]["query"], "TOP"
    return original_query, "ORIGINAL"


def print_report(query, keywords, topics, trend=None):
    """Print a formatted keyword research report."""
    primary, priority = select_primary_keyword(keywords, query)

    print("\n" + "=" * 60)
    print(f"  KEYWORD RESEARCH REPORT: {query}")
    print("=" * 60)

    print(f"\n  PRIMARY KEYWORD: {primary}")
    print(f"  PRIORITY LEVEL:  {priority}")

    if keywords["breakout"]:
        print(f"\n  BREAKOUT KEYWORDS (5000%+ growth):")
        for kw in keywords["breakout"]:
            print(f"    >>> {kw['query']} — {kw['growth']}")

    if keywords["high_growth"]:
        print(f"\n  HIGH-GROWTH KEYWORDS (100%+):")
        for kw in keywords["high_growth"]:
            print(f"    >> {kw['query']} — {kw['growth']}")

    if keywords["moderate"]:
        print(f"\n  MODERATE-GROWTH KEYWORDS (50-99%):")
        for kw in keywords["moderate"]:
            print(f"    > {kw['query']} — {kw['growth']}")

    if keywords["long_tail"]:
        print(f"\n  LONG-TAIL KEYWORDS (question-based):")
        for q in keywords["long_tail"][:8]:
            print(f"    ? {q}")

    if keywords["top"]:
        print(f"\n  TOP QUERIES (by popularity):")
        for kw in keywords["top"][:5]:
            print(f"    - {kw['query']} (score: {kw['score']})")

    if topics["rising"]:
        print(f"\n  RISING TOPICS (use as H2 headings):")
        for t in topics["rising"][:5]:
            print(f"    ^ {t['title']} — {t['growth']}")

    if topics["top"]:
        print(f"\n  TOP TOPICS:")
        for t in topics["top"][:5]:
            print(f"    - {t['title']} (score: {t['score']})")

    if trend:
        arrow = {"RISING": "^", "DECLINING": "v", "STABLE": "="}
        print(f"\n  TREND DIRECTION: {arrow.get(trend['direction'], '?')} {trend['direction']}")
        print(f"    Early avg: {trend['early_avg']} -> Recent avg: {trend['recent_avg']} ({trend['change_pct']:+}%)")

    # Blog structure suggestion
    h2_topics = [t["title"] for t in (topics["rising"] + topics["top"])[:5]]
    h3_questions = keywords["long_tail"][:8]

    print(f"\n  SUGGESTED BLOG STRUCTURE:")
    print(f"    Title: {primary} — Complete Guide {datetime.now().year}")
    if h2_topics:
        for i, topic in enumerate(h2_topics, 1):
            print(f"    H2 [{i}]: {topic}")
            matching = [q for q in h3_questions if any(word in q.lower() for word in topic.lower().split())]
            for q in matching[:2]:
                print(f"      H3: {q}")
    print()

    print("=" * 60)
    return {
        "primary_keyword": primary,
        "priority": priority,
        "keywords": keywords,
        "topics": topics,
        "trend": trend,
        "h2_suggestions": h2_topics,
        "h3_suggestions": h3_questions,
    }


def main():
    parser = argparse.ArgumentParser(description="Discover trending keywords via Google Trends")
    parser.add_argument("query", help="The topic to research")
    parser.add_argument("--geo", default="", help="Geographic filter (e.g., US, GB, US-CA)")
    parser.add_argument("--date", default="today 3-m", help="Time range (default: today 3-m)")
    parser.add_argument("--full", action="store_true", help="Include timeseries validation (uses extra API credit)")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--no-cache", action="store_true", help="Skip cache, force fresh API calls")
    args = parser.parse_args()

    if args.no_cache:
        global CACHE_DAYS
        CACHE_DAYS = 0

    api_key = get_api_key()

    print(f"\nResearching: \"{args.query}\"")
    print(f"Region: {args.geo or 'Worldwide'} | Date: {args.date}")
    print("-" * 40)

    # Required calls (2 API credits)
    rq_data = query_trends(args.query, "RELATED_QUERIES", api_key, args.geo, args.date)
    rt_data = query_trends(args.query, "RELATED_TOPICS", api_key, args.geo, args.date)

    keywords = extract_keywords(rq_data)
    topics = extract_topics(rt_data)

    # Optional: trend validation (1 extra API credit)
    trend = None
    if args.full:
        ts_data = query_trends(args.query, "TIMESERIES", api_key, args.geo, "today 12-m")
        trend = check_trend_direction(ts_data)

    if args.json:
        result = {
            "query": args.query,
            "primary_keyword": select_primary_keyword(keywords, args.query)[0],
            "priority": select_primary_keyword(keywords, args.query)[1],
            "keywords": keywords,
            "topics": topics,
            "trend": trend,
        }
        print(json.dumps(result, indent=2))
    else:
        print_report(args.query, keywords, topics, trend)


if __name__ == "__main__":
    main()
