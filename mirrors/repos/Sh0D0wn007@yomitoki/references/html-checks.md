# HTMLの機械検査：HTML-validate

先に [共通手順](language-checks.md#共通手順) を確認する。

既存のHTML用lint設定を優先する。HTMLHintを採用済みなら`./node_modules/.bin/htmlhint "src/**/*.html"`、html-eslintならHTML用設定のあるESLintを実行する。設定がない場合はHTML-validateの`html-validate:recommended`を初期候補にし、実際に使われた設定を記録する。要素の入れ子、属性、重複ID、代替テキストやラベルなど、有効にしたルールの範囲で点検する。

HTML-validateの実行例：

```bash
./node_modules/.bin/html-validate --version
./node_modules/.bin/html-validate --formatter json "src/**/*.html"
```

変更前後の比較では、保存したJSONからルール別の件数を出す。HTMLHintは`--format json`で保存する。html-eslintの集計はJavaScriptの検査のESLintと同じ。

```bash
jq -r '.[].messages[].ruleId' html-validate.json | sort | uniq -c   # HTML-validate
jq -r '.[].messages[].rule.id' htmlhint.json | sort | uniq -c        # HTMLHint
```

拡張子を対象へ追加するだけでテンプレート構文に対応したとは扱わない。

HTML構造の検査だけで、`<script>`内のJavaScriptや`<style>`内のCSSも検査済みとは報告しない。外部の`.js`・`.css`もそれぞれの言語の検査へ含める。埋め込みJavaScriptは導入済みの`eslint-plugin-html`等のprocessorを使い、元HTMLの行へ診断位置を対応付ける。手動で抽出する場合は、共有スコープ・`type="module"`・テンプレート構文による制約を記録する。

Vue・Svelte・Astroやサーバー側テンプレートでは、その構文を理解する既存ツール・transformerを使う。対応できない場合は、既存の方法で生成したHTMLの検査と、元テンプレートの検査を区別する。BiomeのHTML全体の対応には実験的な設定があるため、導入バージョンと有効な機能を確認し、HTMLを完全に検査できると仮定しない。

静的なHTML検査だけで、表示、DOM操作、キーボード操作、アクセシビリティ全体を検証したとは扱わない。UIを変更した場合は、可能なら実ブラウザでも確認する。

根拠：[HTML-validate CLI](https://html-validate.org/usage/cli.html)、[検査ルール](https://html-validate.org/rules/)、[HTMLHint CLI](https://htmlhint.com/usage/cli/)、[html-eslint](https://html-eslint.org/docs/getting-started)、[eslint-plugin-html](https://github.com/BenoitZugmeyer/eslint-plugin-html)、[BiomeのHTML設定と制限](https://biomejs.dev/reference/configuration/#html)。
