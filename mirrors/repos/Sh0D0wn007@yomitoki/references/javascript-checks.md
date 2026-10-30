# JavaScriptの機械検査

先に [共通手順](language-checks.md#共通手順) を確認する。

以下は`node_modules`へ導入済みの場合の例で、全ツールを続けて実行する指示ではない。モノレポでは対象パッケージの作業ディレクトリと設定を使う。

通常のJavaScriptはESLint単体で検査でき、typescript-eslintは必須ではない。`.js`・`.mjs`・`.cjs`・`.jsx`が実際の検査対象に含まれることを確認し、ブラウザ用・Node.js用、ES Modules・CommonJSの設定を合わせる。JSXでは既存のReact関連ルールも利用する。

| 導入済みツール | 自動修正しない実行例 | 用途・注意 |
| --- | --- | --- |
| ESLint | `./node_modules/.bin/eslint src --format json` | `complexity`・`max-depth`・`max-lines-per-function`・`max-params`・`no-nested-ternary`を候補にする |
| Biome | `./node_modules/.bin/biome check src` | lint・整形・assistの検査。`noExcessiveCognitiveComplexity`など、必要なルールの有効化を確認する |
| Oxlint | `./node_modules/.bin/oxlint src` | JS/TSのlint。既存の`.oxlintrc.json`等と実行スクリプトを使う。必要なルール・プラグインの対応を確認する |
| Prettier | `./node_modules/.bin/prettier --check src` | 整形のみ。複雑さや不具合の検査とは区別する |

ESLintで可読性のルールが未設定なら、初期候補は`complexity: 10`、`max-depth: 3`、`max-lines-per-function: 50`、`max-params: 4`。行数では空行・コメントを含めるかも固定する。既存設定を尊重し、必要なら一時設定または検査時の`--rule`で追加する。実際に有効な設定を確認してから、数値を測定済みと報告する。

Biome・OxlintをESLintの全ルールの代替と決めつけない。Vue・Svelte・Astro等はファイル形式やプラグインの対応範囲を確認し、解析されないファイルを除外範囲に記載する。

変更前後の比較では、保存したJSONからルール別の件数を出す。ESLintの`null`はルールに属さない構文エラー等で、指摘なしとは扱わない。Biomeは`--reporter=summary`でルール別の件数を表示する。Biomeの`--reporter=json`は実験的で、パッチリリースでも形式が変わり得る。

```bash
jq -r '.[].messages[].ruleId' eslint.json | sort | uniq -c   # ESLint（--format json）
jq -r '.diagnostics[].code' oxlint.json | sort | uniq -c     # Oxlint（--format json）
```

根拠：[ESLintルール](https://eslint.org/docs/latest/rules/)、[Biome CLI](https://biomejs.dev/reference/cli/)、[Oxlint](https://oxc.rs/docs/guide/usage/linter.html)、[Prettier CLI](https://prettier.io/docs/cli)。
