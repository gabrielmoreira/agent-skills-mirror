---
name: technology-fingerprinting
description: Deep technology stack identification including frameworks, CDNs, WAFs, and server-side runtimes
---

# Technology Fingerprinting

## When to Use
Identify the full technology stack to select the right exploitation techniques and vulnerability classes. A single `Server: nginx` header is NOT comprehensive fingerprinting.

## Methodology

### Response Header Analysis
```bash
curl -sI https://TARGET/ | head -50
# Record: Server, X-Powered-By, X-AspNet-Version, X-Runtime, X-Generator,
# X-Frame-Options, Content-Security-Policy, Strict-Transport-Security,
# Set-Cookie patterns (session names reveal frameworks)
```

### WhatWeb (if available)
```bash
whatweb -a 3 https://TARGET/ | tee tmp/whatweb.txt
```

### Framework-Specific Signals
```bash
# Check for common framework fingerprints
curl -sk -o /dev/null -w "%{http_code}" https://TARGET/wp-login.php      # WordPress
curl -sk -o /dev/null -w "%{http_code}" https:////TARGET/admin/config     # Django
curl -sk -o /dev/null -w "%{http_code}" https://TARGET/_next/static/       # Next.js
curl -sk -o /dev/null -w "%{http_code}" https://TARGET/angular.js         # Angular
curl -sk -o /dev/null -w "%{http_code}" https://TARGET/favicon.ico       # Favicon hash
```

### CDN / WAF / Proxy Detection
```bash
# Check for CDN
curl -sI https://TARGET/ | grep -iE "cf-ray|cloudfront|x-served-by|x-cache"
# Check for WAF
curl -sk "https://TARGET/?q=<script>alert(1)</script>" -o /dev/null -w "%{http_code}\n"
```

### Cookie / Session Analysis
```bash
curl -sI https://TARGET/ | grep -i set-cookie
# PHPSESSID = PHP, JSESSIONID = Java/Tomcat, ASP.NET_SessionId = ASP.NET,
# rack.session = Ruby, connect.sid = Node.js/Express
```

## Stopping Criteria
- At minimum: response headers analyzed, one fingerprinting tool run, framework identified or confirmed unknown
- Record ALL detected technologies, not just the first

## Common Misses
- Backend languages hidden behind reverse proxies
- Multiple technologies on different paths (admin panel = different stack)
- Version-specific vulnerabilities from X-Powered-By headers
- Debug endpoints that leak stack traces (check /debug, /trace, /actuator)
