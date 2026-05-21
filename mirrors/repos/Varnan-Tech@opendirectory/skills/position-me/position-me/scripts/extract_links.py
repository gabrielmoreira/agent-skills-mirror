import sys
import urllib.request
from urllib.parse import urljoin, urlparse
import re


def extract_links(url):
    print(f"[*] Crawling {url} to map website architecture...")
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req) as response:
            html = response.read().decode("utf-8")

        # Extract hrefs
        links = re.findall(r'<a\s+(?:[^>]*?\s+)?href="([^"]*)"', html, re.IGNORECASE)

        domain = "{0.scheme}://{0.netloc}".format(urlparse(url))

        unique_internal_links = set()
        external_links = set()

        for link in links:
            if link.startswith("/") and not link.startswith("//"):
                unique_internal_links.add(urljoin(domain, link))
            elif link.startswith(domain):
                unique_internal_links.add(link)
            elif link.startswith("http"):
                external_links.add(link)

        print("\n=== INTERNAL LINKS (Site Structure) ===")
        for l in sorted(unique_internal_links):
            print(l)

        print("\n=== EXTERNAL LINKS (Outbound/Socials) ===")
        for l in sorted(external_links):
            if "linkedin" in l or "github" in l or "twitter" in l or "calendly" in l:
                print(l)

    except Exception as e:
        print(f"Error extracting links: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        extract_links(sys.argv[1])
    else:
        print("Usage: python extract_links.py <url>")
