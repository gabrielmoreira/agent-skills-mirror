# Curated fonts

OpenMotion ships a small, inspectable catalog of 40 font families with editorial use cases, role and language tags, pairing suggestions, spacing guidance and pinned resource identities. These suggestions help an Agent choose; they do not establish that a face improves a particular film.

The catalog is not a system-font installation or a new Studio picker. Existing brand, accepted template and reference choices retain priority.

Each family now includes construction traits and conditional brand fit (`brandFit`), reading-role guidance and phone-size risks (`readability`), and pairing conditions (`when` / `avoidWhen`). These editorial fields describe tradeoffs, not measured quality scores or a fixed style system. A pairing is neither a mandatory second family nor a brand substitute. The compact MCP index exposes character traits and reading use; full conditions remain in the family detail.

The shared typography guide distinguishes original marks/packaging, prescribed brand reading text and open creative roles. Phone-led reviews inspect required titles, claims, supporting labels and CTA/URL at a stated display width with actual copy and timing. Its illustrative size ranges are editing starting points, not universal gates; actual legibility and the applicable identity decide the result.

Open choices use a role-led actual-copy comparison: state the visible distinction, compare relevant constructions at equal display conditions, then tune the selected treatment in the real frame. The optional offline `scripts/font-specimen.ts <request.json> <new-output-directory>` helper checks supplied prepared resources against catalog hashes and produces portable HTML, copied fonts/licenses and a JSON input/resource record. It performs no downloads or project writes. Its [input schema and review procedure](../skills/openmotion-production/references/fonts.md#compare-prepared-faces-with-actual-copy) cover mixed-script stacks and explicit coverage gaps; generated output is comparison material, not visual acceptance.

| Family ID | Family | Language focus | Character / likely role |
| --- | --- | --- | --- |
| notosanssc | Noto Sans SC | Simplified Chinese | Neutral sans; subtitles, body, data |
| notoserifsc | Noto Serif SC | Simplified Chinese | Editorial serif; literary titles |
| lxgwwenkai | LXGW WenKai | Simplified Chinese | Human handwriting; notes, stories |
| zcoolxiaowei | ZCOOL XiaoWei | Simplified Chinese | Expressive serif display |
| zcoolqingkehuangyou | ZCOOL QingKe HuangYou | Simplified Chinese | Narrow mechanical display |
| mashanzheng | Ma Shan Zheng | Simplified Chinese | Brush calligraphy; short titles |
| zcoolkuaile | ZCOOL KuaiLe | Simplified Chinese | Playful rounded display |
| longcang | Long Cang | Simplified Chinese | Casual handwritten overlays |
| inter | Inter | Latin | Neutral sans; clear product text |
| ibmplexsans | IBM Plex Sans | Latin | Humanist technical sans |
| barlowcondensed | Barlow Condensed | Latin | Industrial condensed titles |
| archivoblack | Archivo Black | Latin | Heavy poster display |
| bebasneue | Bebas Neue | Latin | Tall sports/poster display |
| ebgaramond | EB Garamond | Latin | Classical editorial serif |
| fraunces | Fraunces | Latin | Expressive retro serif |
| bodonimoda | Bodoni Moda | Latin | High-contrast fashion display |
| spacemono | Space Mono | Latin | Retro monospace; short data |
| jetbrainsmono | JetBrains Mono | Latin | Code and aligned technical values |
| caveat | Caveat | Latin | Personal handwritten notes |
| orbitron | Orbitron | Latin | Geometric science-fiction display |
| liujianmaocao | Liu Jian Mao Cao | Simplified Chinese | Connected, cursive Han brush gestures |
| chirongoroundtc | Chiron GoRound TC | Traditional Chinese | Rounded Traditional Chinese sans with a broad weight range |
| zenmarugothic | Zen Maru Gothic | Japanese | Soft rounded Japanese gothic forms |
| shipporimincho | Shippori Mincho | Japanese | Japanese Mincho contrast and expressive terminals |
| yomogi | Yomogi | Japanese | Loose Japanese pen handwriting with kana |
| dotgothic16 | DotGothic16 | Japanese | Japanese dot-grid Gothic construction |
| gowundodum | Gowun Dodum | Korean | Soft Korean Hangul sans proportions |
| notonaskharabic | Noto Naskh Arabic | Arabic / Persian | Naskh Arabic construction with joining and mark positioning |
| notosansdevanagari | Noto Sans Devanagari | Devanagari / Hindi | Devanagari headline and combining-mark structure |
| nunito | Nunito | Latin | Rounded Latin terminals and open sans rhythm |
| atkinsonhyperlegiblenext | Atkinson Hyperlegible Next | Latin | Distinctive letter and numeral construction for identification |
| jost | Jost | Latin | Geometric Latin bowls with a structured display rhythm |
| zillaslab | Zilla Slab | Latin | Substantial slab serifs and sturdy text shapes |
| unbounded | Unbounded | Latin | Broad geometric Latin forms and counters |
| blackopsone | Black Ops One | Latin | Stencil breaks in heavy Latin forms |
| unifrakturcook | UnifrakturCook | Latin | Dense blackletter shapes and sharp ornamental rhythm |
| bangers | Bangers | Latin | Hand-drawn comic display with an emphatic slant |
| pressstart2p | Press Start 2P | Latin | Blocky Latin pixel-grid construction |
| dancingscript | Dancing Script | Latin | Connected Latin script strokes and lively joins |
| monoton | Monoton | Latin | Repeated-line decorative Latin construction |

## Coverage and expansion rationale

The initial twenty retain their pinned resources and editorial records. They cover neutral Chinese/Latin reading, several editorial serifs, brush/handwritten accents, condensed posters, monospace and a geometric science-fiction display. The additional twenty fill separate construction and script gaps rather than concentrating on a single mood:

| Missing construction or script | Added choices |
| --- | --- |
| Soft rounded reading | Chiron GoRound TC, Zen Maru Gothic, Nunito |
| Distinct letters, geometric and wide sans | Atkinson Hyperlegible Next, Jost, Unbounded |
| Slab serif, stencil and blackletter | Zilla Slab, Black Ops One, UnifrakturCook |
| Cursive Han, comic and connected script | Liu Jian Mao Cao, Bangers, Dancing Script |
| Pixel and multiline display | DotGothic16, Press Start 2P, Monoton |
| Japanese literary and handwritten text | Shippori Mincho, Yomogi |
| Korean, Arabic/Persian and Hindi reading | Gowun Dodum, Noto Naskh Arabic, Noto Sans Devanagari |

The language-specific additions include Traditional Chinese, Japanese, Korean, Arabic/Persian and Devanagari. Japanese/Traditional Han coverage does not establish Simplified Chinese regional fidelity. Direction, joining, combining marks and actual names need their own rendered review. Low-vision-oriented construction is not a universal accessibility guarantee. These are available choices, not a preset system or evidence of reduced AI/template appearance.

## How an Agent uses the catalog

1. Read `openmotion://fonts/index`, filter by the film's actual language and text roles, then read only relevant `openmotion://fonts/<id>` details.
2. Run the returned preparation command on the host, optionally appending `--weight <available-weight>` (400 when available, otherwise the first available upright weight). It fetches only the selected upright resource and license, verifies size/SHA-256 and reuses verified cached files. The script can also run directly from the installed runtime: `node --experimental-strip-types scripts/prepare-font.ts <id> [--weight 400]`.
3. Import the returned local `importItems` with the existing `openmotion_import_assets` Tool. Font files and optional license text become one versioned project change; the Tool returns actual font metadata and project-relative @font-face CSS.
4. Read the new revision/version, save the relevant CSS/text through `openmotion_edit_project`, then inspect the actual copy and reading window. For nested stylesheets, resolve CSS URLs relative to their location.

The authoritative [metadata](../skills/openmotion-production/fonts/catalog.json) lives with the Skill so installed Skill-only hosts can filter it locally. MCP's index and family details are projections of the same file. [Typography guidance](../skills/openmotion-production/references/typography.md) and the [resource workflow](../skills/openmotion-production/references/fonts.md) describe selection and validation.

## Storage and delivery

Only metadata and code ship with the application/Skills, not the complete font binaries. Selected resources are downloaded from fixed upstream commits into `~/.cache/openmotion/fonts/<source-commit>/<id>/`. First use needs network access; verified cache entries work offline. Preparation does not modify projects or install system fonts. A finished portable project carries the actual selected font files and applicable license, so subsequent rendering and text changes do not depend on the author's system fonts.

The catalog contains upright resources only. Variable axes and real weight ranges, glyph sample results, byte sizes, hashes and source revisions come from the pinned files. Language tags are not a guarantee for every character or regional glyph form; inspect actual copy. No visual-quality or anti-template effect has been established merely by catalog inclusion.

Font parsing uses the existing locked dependency runtime, including when a plugin is extracted without its own `node_modules`. For the offline specimen command in that layout, select that already installed directory with `--runtime-root <existing-locked-runtime>`; the helper performs no dependency installation.

## Sources

Font binaries and licenses are pinned individually from [Google Fonts](https://github.com/google/fonts) and [LXGW WenKai](https://github.com/lxgw/LxgwWenKai); each family records its upstream commit, exact file URLs and OFL license hash. Original bytes are preserved. Editorial metadata was curated for Motion, informed by the role-based structure of [UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill), and does not copy a fixed style prescription or claim those projects' endorsement.
