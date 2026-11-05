# Prints the failed requests (HTTP 400+ or no response) and JS errors in the attached browser-use tab
# since the last call. The daemon keeps only the latest 500 events, so run it right after a failure.
# Usage: <env prefix> browser-use < <skill-dir>/scripts/failures.py
urls, found = {}, []
for e in drain_events():
    m, p = e["method"], e["params"]
    if m == "Network.requestWillBeSent":
        urls[p["requestId"]] = f'{p["request"]["method"]} {p["request"]["url"]}'
    elif m == "Network.responseReceived" and p["response"]["status"] >= 400:
        found.append(f'HTTP {p["response"]["status"]} {urls.get(p["requestId"], p["response"]["url"])}')
    elif m == "Network.loadingFailed" and not p.get("canceled"):
        found.append(f'FAILED {urls.get(p["requestId"], "?")}: {p["errorText"]}')
    elif m == "Runtime.exceptionThrown":
        d = p["exceptionDetails"]
        found.append(f'JS error: {d.get("exception", {}).get("description") or d.get("text")}')
    elif m == "Runtime.consoleAPICalled" and p["type"] == "error":
        found.append("console.error: " + " ".join(str(a.get("value", a.get("description", ""))) for a in p["args"]))
print("\n".join(found) or "no failed requests or JS errors")
