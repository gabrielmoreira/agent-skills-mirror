---
"@tutti-os/desktop-update-admission": patch
"@tutti-os/desktop": patch
---

Add the shared desktop minimum-version admission package and migrate Tutti Desktop to its common policy validation, updater lease, Electron controller, preload bridge, localization, and React UI. Keep loopback policy configuration exclusively in the mock-server process while clients own current-version and updater simulation.
