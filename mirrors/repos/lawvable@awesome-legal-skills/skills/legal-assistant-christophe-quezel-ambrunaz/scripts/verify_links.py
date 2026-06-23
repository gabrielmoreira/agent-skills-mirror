#!/usr/bin/env python3
"""
verify_links.py — Vérification batch d'URLs juridiques.

Usage :
    python3 scripts/verify_links.py --urls '["https://...", "https://..."]'
    python3 scripts/verify_links.py --from-file urls.json

Sortie : JSON avec statut de chaque URL.
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
import concurrent.futures

TIMEOUT = 10
MAX_WORKERS = 5


def check_url(url):
    """Vérifie l'accessibilité d'une URL. Retourne le statut HTTP."""
    try:
        req = urllib.request.Request(
            url,
            method="HEAD",
            headers={"User-Agent": "Legal-Link-Checker/1.0"}
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
            return {
                "url": url,
                "status": response.getcode(),
                "accessible": True,
                "error": None,
            }
    except urllib.error.HTTPError as e:
        return {
            "url": url,
            "status": e.code,
            "accessible": e.code < 400,
            "error": f"HTTP {e.code}: {e.reason}",
        }
    except urllib.error.URLError as e:
        return {
            "url": url,
            "status": None,
            "accessible": False,
            "error": f"URL Error: {e.reason}",
        }
    except Exception as e:
        return {
            "url": url,
            "status": None,
            "accessible": False,
            "error": str(e),
        }


def verify_batch(urls):
    """Vérifie une liste d'URLs en parallèle."""
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_url = {executor.submit(check_url, url): url for url in urls}
        for future in concurrent.futures.as_completed(future_to_url):
            results.append(future.result())
    # Trier par ordre original
    url_order = {url: i for i, url in enumerate(urls)}
    results.sort(key=lambda r: url_order.get(r["url"], 999))
    return results


def main():
    parser = argparse.ArgumentParser(description="Vérification batch d'URLs juridiques")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--urls", help="JSON array d'URLs à vérifier")
    group.add_argument("--from-file", help="Fichier JSON contenant les URLs")

    args = parser.parse_args()

    if args.urls:
        urls = json.loads(args.urls)
    else:
        with open(args.from_file, "r", encoding="utf-8") as f:
            urls = json.load(f)

    if not isinstance(urls, list):
        print(json.dumps({"error": "L'entrée doit être un array JSON d'URLs"}))
        sys.exit(1)

    results = verify_batch(urls)

    summary = {
        "total": len(results),
        "accessible": sum(1 for r in results if r["accessible"]),
        "inaccessible": sum(1 for r in results if not r["accessible"]),
        "results": results,
    }

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
