# CSSの機械検査：Stylelint

先に [共通手順](language-checks.md#共通手順) を確認する。

既存のStylelint設定を優先する。設定がない場合は、導入するバージョンに対応した`stylelint-config-standard`を候補にする。プロパティ・値・単位・セレクタの誤りや重複などを、有効にしたルールの範囲で検査する。整形は既存のPrettier等へ任せる。

```bash
./node_modules/.bin/stylelint --version
./node_modules/.bin/stylelint "src/**/*.css" --formatter json --output-file stylelint.json
jq -r '.[].warnings[].rule' stylelint.json | sort | uniq -c
```

Stylelintは結果を標準エラーへ出す（17.16で確認）ため、`>`では保存できない。`--output-file`で保存する。構文エラーは`CssSyntaxError`として件数に含まれるため、指摘なしとは扱わない。

SCSS・Less・HTML内の`<style>`などは対応する`customSyntax`・プラグイン・設定を確認する。CSSファイルの検査だけで埋め込みCSSも検査済みとは扱わない。静的検査で表示崩れは保証できないため、レイアウトを変更した場合は実ブラウザでも確認する。

根拠：[Stylelint CLI](https://stylelint.io/user-guide/cli/)、[設定](https://stylelint.io/user-guide/configure/)、[検査ルール](https://stylelint.io/user-guide/rules/)。
