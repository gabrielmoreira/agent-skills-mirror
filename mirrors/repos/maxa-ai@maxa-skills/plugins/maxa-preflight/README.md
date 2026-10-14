# maxa-preflight

Automate Autopilot Preflight workflows — date-filter spec generation, binary installation, and guided usage for data engineers extracting source system data into DuckDB.

> **Not released yet.** This plugin is not listed in the marketplace, so `/plugin install` won't find it. Load it locally to try it out.

## Skills

| Skill | Description |
|-------|-------------|
| `date-filter-spec` | Generate a per-table date-filtering decision spec |
| `install` | Install the autopilot-preflight binary |
| `guide` | Learn what commands are available and how to use them |

## Testing Locally

From the repository root:

```bash
claude --plugin-dir ./plugins/maxa-preflight
```

## Usage

Once loaded, invoke skills with the plugin namespace:

```
/maxa-preflight:date-filter-spec  # Generate a per-table date-filtering decision spec
/maxa-preflight:install           # Install the autopilot-preflight binary
/maxa-preflight:guide             # Learn what commands are available and how to use them
```
