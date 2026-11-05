# Turns the attached browser-use tab into a 375x667 touch phone (iPhone SE) on Chrome DevTools'
# "Slow 3G" preset: 2 s latency, 400 kbit/s each way. The overrides belong to the tab, so rerun
# this after opening or switching to another tab.
# Usage: <env prefix> browser-use < <skill-dir>/scripts/mobile-setup.py
IPHONE_UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
             "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")
cdp("Emulation.setDeviceMetricsOverride", width=375, height=667, deviceScaleFactor=2, mobile=True)
cdp("Emulation.setTouchEmulationEnabled", enabled=True, maxTouchPoints=5)
cdp("Emulation.setUserAgentOverride", userAgent=IPHONE_UA, platform="iPhone")
cdp("Network.emulateNetworkConditions", offline=False, latency=2000, downloadThroughput=50000, uploadThroughput=50000)
print("phone 375x667 on slow 3G:", page_info()["url"])
