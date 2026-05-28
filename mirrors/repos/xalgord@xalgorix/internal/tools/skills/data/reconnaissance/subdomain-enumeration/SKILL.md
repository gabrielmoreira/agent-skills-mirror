---
name: subdomain-enumeration
description: Advanced multi-source subdomain enumeration combining passive, active, brute-force, and certificate transparency techniques
---

# Subdomain Enumeration

## Methodology

### Passive Enumeration (No Target Contact)

```bash
# Certificate Transparency
curl -s "https://crt.sh/?q=%.TARGET&output=json" | jq -r '.[].name_value' | sort -u

# DNS aggregators
subfinder -d TARGET -all -recursive -o subs_subfinder.txt
findomain -t TARGET -q -u subs_findomain.txt
assetfinder --subs-only TARGET > subs_assetfinder.txt

# Archives
curl -s "https://web.archive.org/cdx/search/cdx?url=*.TARGET/*&output=json&fl=original" | jq -r '.[].original' | cut -d/ -f3 | sort -u

# SecurityTrails, VirusTotal, Shodan (API keys required)
```

### Active Enumeration

```bash
# DNS brute-force
shuffledns -d TARGET -w /usr/share/wordlists/subdomains-top1m.txt -r resolvers.txt -o subs_brute.txt

# DNS resolution and probing
cat all_subs.txt | dnsx -silent -a -resp -o resolved.txt
cat all_subs.txt | httpx -silent -status-code -title -tech-detect -follow-redirects -o live.txt
```

### Subdomain Takeover Detection

```bash
# CNAME pointing to deprovisioned services
cat all_subs.txt | while read sub; do
  cname=$(dig CNAME "$sub" +short)
  [ -n "$cname" ] && host "$cname" >/dev/null 2>&1 || echo "[TAKEOVER?] $sub -> $cname"
done
subjack -w all_subs.txt -t 100 -timeout 30 -ssl -o takeovers.txt
```

## Pro Tips

1. Merge ALL sources before resolving — passive + active + brute-force
2. Use multiple resolvers from different networks to avoid DNS filtering
3. Test wildcard DNS (`*.TARGET`) — some domains resolve all subdomains to one IP
4. Check for subdomain takeover on EVERY CNAME — dangling CNAMEs are free bounties
5. Use `httpx -tech-detect` to identify technology stack per subdomain
