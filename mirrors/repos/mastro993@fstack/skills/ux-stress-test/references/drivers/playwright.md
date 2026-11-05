# Driver: playwright-cli

Your browser is a `playwright-cli` session. Every command carries your session flag, so the other personas' browsers stay out of yours.

## Start and stop

```bash
PLAYWRIGHT_MCP_OUTPUT_DIR=<output-dir>/.pw playwright-cli -s=<session> open --browser=chrome <App URL>
```

Setting `PLAYWRIGHT_MCP_OUTPUT_DIR` on `open` keeps the session's snapshots and logs in your output dir, out of the project. When you're done: `playwright-cli -s=<session> close`.

## Actions

| To | Do |
|----|----|
| See the screen | `playwright-cli -s=<session> screenshot --filename=<output-dir>/NN-slug.png`, then open the PNG |
| Find what you can act on | `playwright-cli -s=<session> snapshot`: element refs such as `e12` |
| Click or tap | `click e12` |
| Double-click | `dblclick e12` |
| Type into a field | `click e12`, then `type "text"`: key by key |
| Paste into a field | `fill e12 "text"`: the whole value lands at once |
| Press a key | `press Enter` |
| Back, forward, reload | `go-back`, `go-forward`, `reload` |
| Answer a dialog | `dialog-accept`, `dialog-dismiss` |
| Open a second tab | `tab-new <url>`, then `tab-select <index>` to switch |
| Evidence after a failure | `console` and `requests` |

`playwright-cli --help` lists the rest. The snapshot is the DOM: use it to find refs, and the screenshot to decide what a person sees.

## Mobile

Open on a blank phone, throttle it, then go to the app. Opening on `about:blank` first means the landing page itself loads throttled; every later page and tab inherits the throttle.

```bash
PLAYWRIGHT_MCP_OUTPUT_DIR=<output-dir>/.pw playwright-cli -s=<session> open --browser=chrome --device="iPhone SE (3rd gen)" about:blank
playwright-cli -s=<session> run-code --filename=<skill-dir>/scripts/slow-3g.js
playwright-cli -s=<session> goto <App URL>
```

Check each screen with:

```bash
playwright-cli -s=<session> --raw eval "$(cat <skill-dir>/scripts/mobile-audit.js)"
```

## Fresh session for a retest

Open a second session `-s=<session>-retest` with the same setup.
