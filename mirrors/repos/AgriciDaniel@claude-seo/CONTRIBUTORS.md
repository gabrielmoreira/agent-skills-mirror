# Contributors

Claude SEO is created and maintained by [@AgriciDaniel](https://github.com/AgriciDaniel).

This project thrives thanks to community contributions from the
[AI Marketing Hub](https://www.skool.com/ai-marketing-hub) Pro Hub Challenge
and open-source pull requests.

## Pro Hub Challenge (v1.9.0)

The Pro Hub Challenge invited community members to build extensions for Claude SEO
and Claude Blog. These submissions were reviewed, security-audited, and integrated
into v1.9.0 with the contributors' permission.

| Contributor | Submission | Repo | Integrated As |
|------------|------------|------|--------------|
| **Lutfiya Miller** (Winner) | Semantic Cluster Engine | [Drfiya/semantic-cluster-engine](https://github.com/Drfiya/semantic-cluster-engine) | `seo-cluster` (core skill) |
| **Chris Muller** | Multi-lingual SEO | [Chriss54/claude-blog-multilingual](https://github.com/Chriss54/claude-blog-multilingual) | `seo-hreflang` enhancements (cultural profiles, locale formats, content parity) |
| **Florian Schmitz** | SXO Skill | [tools-enerix/claude-sxo-skill](https://github.com/tools-enerix/claude-sxo-skill) | `seo-sxo` (core skill) |
| **Dan Colta** | SEO Drift Monitor | [dancolta/seo-drift-monitor](https://github.com/dancolta/seo-drift-monitor) | `seo-drift` (core skill) |
| **Matej Marjanovic** | E-commerce + DataForSEO Cost Config + ASO + Platform Support | [matej-marjanovic/claude-seo](https://github.com/matej-marjanovic/claude-seo) | `seo-ecommerce` (core), cost infrastructure, `seo-aso` (extension), `AGENTS.md` |
| **Benjamin Samar** | SEO Dungeon | n/a | Reviewed (not integrated in v1.9.0) |

## Framework Integration (v1.9.5)

| Source | Type | License | Integrated As |
|--------|------|---------|--------------|
| **[FLOW](https://github.com/AgriciDaniel/flow)** by Daniel Agrici | 41 AI prompts + framework doc + bibliography | CC BY 4.0 | `seo-flow` skill + `skills/seo-flow/references/` |

Attribution header on every bundled prompt file (automated by `scripts/sync_flow.py`).

## Community Pull Requests

### v2.2.0

| Contributor | PR | What |
|------------|-----|------|
| [@manishpaulsimon](https://github.com/manishpaulsimon) | [#117](https://github.com/AgriciDaniel/claude-seo/pull/117) | Cross-platform `drift_baseline` fetch -> parse handoff (synthesis basis) |
| [@solbergryan](https://github.com/solbergryan) | [#128](https://github.com/AgriciDaniel/claude-seo/pull/128) | Windows compatibility for drift scripts and installer |
| [@GieriGuru](https://github.com/GieriGuru) | [#111](https://github.com/AgriciDaniel/claude-seo/pull/111) | Handle Windows Store Python alias in `install.ps1` |
| [@Shieldxx](https://github.com/Shieldxx) | [#115](https://github.com/AgriciDaniel/claude-seo/pull/115) | Windows + non-Latin-1 baseline portability |
| [@imranaliraqi](https://github.com/imranaliraqi) | [#125](https://github.com/AgriciDaniel/claude-seo/pull/125) | Windows path + UTF-8 baseline portability |
| [@eduardofortesr](https://github.com/eduardofortesr) | [#101](https://github.com/AgriciDaniel/claude-seo/pull/101) | Cross-platform JSON-LD validator hook (python3) |
| [@fayerman-source](https://github.com/fayerman-source) | [#104](https://github.com/AgriciDaniel/claude-seo/pull/104) | Move Google API key from URL to request header |
| [@nickgraynews](https://github.com/nickgraynews) | [#113](https://github.com/AgriciDaniel/claude-seo/pull/113) | Drop deprecated GSC Sitemaps `indexed` field |
| [@PenthouseWaldkirchen](https://github.com/PenthouseWaldkirchen) | [#118](https://github.com/AgriciDaniel/claude-seo/pull/118) | Add authors and keywords to `pyproject.toml` |
| [@chat2deskmx](https://github.com/chat2deskmx) | [#123](https://github.com/AgriciDaniel/claude-seo/pull/123) | Add ruff config and lint cleanup |

### v1.9.7

| Contributor | PR | What |
|------------|-----|------|
| [@xiaolai](https://github.com/xiaolai) | [#62](https://github.com/AgriciDaniel/claude-seo/pull/62) | Sync `extensions/dataforseo` skill with core |
| [@xiaolai](https://github.com/xiaolai) | [#63](https://github.com/AgriciDaniel/claude-seo/pull/63) | Sync `extensions/banana` `seo-image-gen` skill |
| [@xiaolai](https://github.com/xiaolai) | [#64](https://github.com/AgriciDaniel/claude-seo/pull/64) | Pin MCP server package versions in extension installers |
| [@CrepuscularIRIS](https://github.com/CrepuscularIRIS) | [#67](https://github.com/AgriciDaniel/claude-seo/pull/67) | Detect marketplace plugin install path in DataForSEO extension |
| [@evanlu14](https://github.com/evanlu14) | [#69](https://github.com/AgriciDaniel/claude-seo/pull/69) | `pagespeed_check` KeyError fix (`audit_details`) |
| [@EDSprog](https://github.com/EDSprog) | [#70](https://github.com/AgriciDaniel/claude-seo/pull/70) | Update README install section |
| [@NicT89](https://github.com/NicT89) | [#73](https://github.com/AgriciDaniel/claude-seo/pull/73) | Migrate `moz_api` to v2 REST endpoints |
| [@AndronMan](https://github.com/AndronMan) | [#74](https://github.com/AgriciDaniel/claude-seo/pull/74) | Add `Write` tool to `seo-geo` agent |
| [@puneetindersingh](https://github.com/puneetindersingh) | [#56](https://github.com/AgriciDaniel/claude-seo/pull/56) | Add `seo-content-brief` skill |

### v1.9.0 and earlier

| Contributor | PR | What |
|------------|-----|------|
| [@edocltd](https://github.com/edocltd) | [#50](https://github.com/AgriciDaniel/claude-seo/pull/50) | Ukrainian localization |
| [@MalteBerlin](https://github.com/MalteBerlin) | [#45](https://github.com/AgriciDaniel/claude-seo/pull/45) | Sub-skills count correction |
| [@olivierroy](https://github.com/olivierroy) | [#43](https://github.com/AgriciDaniel/claude-seo/pull/43) | Extension install fix |

## Security Disclosures

Responsible disclosures incorporated into v2.2.0. Thank you for reporting privately or via issues:

| Reporter | Report | What |
|----------|--------|------|
| [@Fushuling](https://github.com/Fushuling) | [#110](https://github.com/AgriciDaniel/claude-seo/issues/110) | SSRF parser-differential bypass in `validate_url` |
| [@webgunnz](https://github.com/webgunnz) | [#122](https://github.com/AgriciDaniel/claude-seo/issues/122), [#121](https://github.com/AgriciDaniel/claude-seo/issues/121) | Google API key leak in error output; UTF-8 double-encode |
| [@fayerman-source](https://github.com/fayerman-source) | [#130](https://github.com/AgriciDaniel/claude-seo/issues/130), [#103](https://github.com/AgriciDaniel/claude-seo/issues/103) | GSC false "0 clicks" totals; NLP V1 entity metadata |

## How to Contribute

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on submitting pull requests,
creating extensions, and participating in future challenges.

Join the community:
- Free: https://www.skool.com/ai-marketing-hub
- Pro: https://www.skool.com/ai-marketing-hub-pro
