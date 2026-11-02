# Vendored WebUI fonts

Rubik and Roboto Mono are vendored from the official
[`google/fonts`](https://github.com/google/fonts) repository at commit
`7ff85c87f93ea6cca5f41c69f2e4edcb90240f26`.

| Local artifact | Upstream artifact | License |
| --- | --- | --- |
| `rubik-variable.ttf` | `ofl/rubik/Rubik[wght].ttf` | `rubik-OFL.txt` |
| `rubik-italic-variable.ttf` | `ofl/rubik/Rubik-Italic[wght].ttf` | `rubik-OFL.txt` |
| `roboto-mono-variable.ttf` | `ofl/robotomono/RobotoMono[wght].ttf` | `roboto-mono-OFL.txt` |
| `roboto-mono-italic-variable.ttf` | `ofl/robotomono/RobotoMono-Italic[wght].ttf` | `roboto-mono-OFL.txt` |

`fonts.css` exposes the upstream variable weight ranges through local
`@font-face` declarations. The WebUI must not fall back to a remote font host.
