---
name: "smartthings"
description: "Read status and send commands to Samsung SmartThings devices: lights, locks, thermostats, sirens, garage doors. Trigger phrases: smartthings, samsung smart home, unlock the door, smartthings thermostat."
metadata: { "includeInPrompt": true }
tagline: "Read device status and issue capability commands across a Samsung SmartThings account: locations, devices, switches, dimmers, locks, thermostats, sirens, garage door controllers, and window shades. Use it when the user asks about or wants to change the state of anything paired to their SmartThings hub or cloud account. This connector drives real physical hardware, so every write is confirmation-gated (see Operating Rules)."
catalog_auth: "provider OAuth 2.0 via the secure credential flow"
catalog_hosts: ["api.smartthings.com"]
---

# SmartThings

## Purpose
Read device status and issue capability commands across a Samsung SmartThings
account: locations, devices, switches, dimmers, locks, thermostats, sirens,
garage door controllers, and window shades. Use it when the user asks about
or wants to change the state of anything paired to their SmartThings hub or
cloud account. This connector drives real physical hardware, so every write
is confirmation-gated (see Operating Rules).

## Tooling
All commands go through `bin/smartthings.py`:

```bash
bin/smartthings.py auth                                    # status check: verify token, list locations
bin/smartthings.py locations                               # list locations
bin/smartthings.py devices --limit 50                      # list devices with capabilities
bin/smartthings.py status --id <deviceId>                  # read full device status

# Writes. HIGH actuations (lock unlock, garage open/close) REQUIRE
# --confirm naming the exact physical effect, on every run:
bin/smartthings.py command --id <deviceId> --capability lock --command unlock \
    --confirm "unlock front door deadbolt"
bin/smartthings.py command --id <deviceId> --capability garageDoorControl --command open \
    --confirm "open the garage door"

# MEDIUM actuations (switches, dimmers, thermostats, sirens) need --confirm on
# first use per device; later runs proceed without it:
bin/smartthings.py command --id <deviceId> --capability switch --command on \
    --confirm "turn on the living room lamp"
bin/smartthings.py command --id <deviceId> --capability switchLevel --command setLevel \
    --arg 50 --confirm "dim bedroom light to 50 percent"
bin/smartthings.py command --id <deviceId> --capability thermostatMode \
    --command setThermostatMode --arg '"heat"' --confirm "set hallway thermostat to heat"
bin/smartthings.py command --id <deviceId> --capability alarm --command both \
    --confirm "sound the hallway siren"

# LOW actuations (window shades / curtains) proceed with a logged notice:
bin/smartthings.py command --id <deviceId> --capability windowShadeLevel \
    --command setShadeLevel --arg 100
```

`--arg` values are JSON-parsed, so pass numbers bare (`--arg 50`) and strings
as quoted JSON (`--arg '"heat"'`) or plain text (falls back to a string).
`--component` defaults to `main`; set it when the device exposes other
components.

## Auth
- Provider id: `smartthings` (credential is collected as `custom.smartthings`)
- Collection: OAuth 2.0 authorization-code flow via the secure credential flow
  (`credentials.request_api_access`). Set up: create an app at
  developer.smartthings.com with the scopes the user needs (devices read,
  device commands), complete the authorization-code grant, and store the
  resulting access token. Personal Access Tokens now expire after about 24
  hours, so a persistent connector must use the OAuth flow.
- Required scopes: `r:devices:*` at minimum for reads; add `x:devices:*`
  (commands) only for the devices the user wants Muse to actuate.
- Allowed hosts: `api.smartthings.com`
- Status check: `bin/smartthings.py auth`

## Operating Rules
1. **HIGH actuations are blocked without explicit confirmation.** Unlocking a
   lock and opening or closing a garage door require
   `--confirm "<exact physical effect>"` on every single run, e.g.
   `--confirm "unlock front door deadbolt"`. A bare `--confirm` or a vague
   value is rejected by the CLI. Never pre-fill the confirmation on the
   user's behalf: the exact effect must come from the user's own words.
2. **MEDIUM actuations confirm on first use per device.** Switches, dimmers,
   thermostat modes and setpoints, and siren on/off need `--confirm` the first
   time a device is actuated; the CLI records that confirmation locally
   (`~/.config/muse-connectors/smartthings/confirmed.json`) and later runs
   proceed. A thermostat change starts or stops real heating/cooling; treat
   every MEDIUM run as if the user is watching.
3. **LOW actuations (window shades, curtains) proceed** with a notice printed
   to stderr. No confirmation needed.
4. **Never lock someone out or in.** Do not lock a door unless the user
   explicitly asked for that lock to be locked; locking is a write and follows
   the same grading as unlock (MEDIUM, first-use confirmed) but verify intent
   twice in conversation first.
5. Read commands (`auth`, `locations`, `devices`, `status`) never need
   confirmation.
6. Rate limit: roughly 120 requests/min on the commands endpoint per
   device/principal. Space out bulk actuations.
7. **Cost warning:** Samsung announced paid SmartThings tiers starting
   October 2026 (about $4.99/month for the personal tier). Heavy or
   always-on use may fall under a paid tier.
8. Zigbee/Z-Wave devices need a SmartThings hub online; cloud-only devices
   work without one.
9. Never exfiltrate the credential: the CLI only ever handles surrogates.
   Do not print, log, or transmit the token value.

## Files
- SKILL.md
- bin/smartthings.py

## Maturity
🧪 Draft: written from SmartThings' public REST API docs; not yet live-tested
end-to-end. The command request shape (`component`, `capability`, `command`,
`arguments`) and the `--arg` JSON parsing are untested against a real device.
