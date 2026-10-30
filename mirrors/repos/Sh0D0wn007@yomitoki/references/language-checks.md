# 言語別の機械検査

共通手順を確認し、対象言語の資料だけを読む。複数言語を編集する場合は、それぞれの資料を参照する。付属スクリプトは下表の言語の構文指標（[定義](mechanical-checks.md)）と、PythonのRuff検査を行う。lint・整形・型チェックなどそれ以外の検査は、各資料に沿って導入済みツールを実行する。他言語ツールの結果を付属スクリプトへ渡さない。

| 対象 | 検査資料 | 主なツール |
| --- | --- | --- |
| Python | [一括検査と比較](workflow-checks.md)、[構文指標](mechanical-checks.md) | 付属スクリプト・Ruff |
| C | [Cの検査](c-checks.md) | 付属スクリプト（構文指標）・clang-tidy・Cppcheck |
| C++ | [C++の検査](cpp-checks.md) | 付属スクリプト（構文指標）・clang-tidy・Cppcheck |
| Java | [Javaの検査](java-checks.md) | 付属スクリプト（構文指標）・PMD・Checkstyle・SpotBugs |
| JavaScript | [JavaScriptの検査](javascript-checks.md) | 付属スクリプト（構文指標）・ESLint・Biome・Oxlint |
| TypeScript | [TypeScriptの検査](typescript-checks.md) | 付属スクリプト（構文指標）・typescript-eslint・tsc |
| HTML | [HTMLの検査](html-checks.md) | HTML-validate・HTMLHint・html-eslint |
| CSS | [CSSの検査](css-checks.md) | Stylelint |

## 共通手順

各資料のツールは2026-10-21に公式資料を確認した選択肢。流行だけを理由に既存の検査基盤を移行しない。

1. 対象の拡張子と、CI・package.json・lockfile・ビルド設定・lint設定を確認する。既存の検査コマンドに自動修正が含まれる場合は、検査専用の実行方法を選ぶ。
2. 使用バージョン、ルール、閾値、対象ファイル、除外、抑制コメント、コンパイル条件を控える。既存の検査と、今回追加する可読性の検査は区別する。
3. 変更前に実行し、出力と終了コードを対象外の一時ディレクトリへ保存する。変更後に同じ条件で再実行し、ルール・位置・実測値を比較する。ルール別の件数は各資料の集計コマンドで出し、変更前後を`diff`で比べる。件数が同じでも位置は変わり得る。対象ファイルが実際に解析されたことも確認する。
4. 構文エラー・設定エラー・依存不足は「指摘なし」に含めない。警告だけなら終了コード0になるツールもあるため、診断本文も読む。終了コードは各ツールの定義に従い、Pythonの0/1/2へ読み替えない。

検査では自動修正・自動整形・抑制コメントの追加を行わない。clang-tidyの`--fix`・`--fix-errors`、clang-formatの`-i`、ESLint・Oxlint・Stylelint・HTML-validateの`--fix`、Biomeの`--write`・`--fix`・`--suppress`、Prettierの`--write`を付けない。新しい依存や設定を追加する場合は依頼の範囲を確認し、プロジェクトの方法でバージョンを固定する。検査のために最新版を暗黙に取得する`npx ...@latest`や、未導入パッケージの自動取得を避ける。

各言語のコマンド例はプロジェクトのルートで使う。パスは実在する対象に置き換え、導入済みバージョンの`--help`でオプションを確認する。検査対象のソースは変更しないが、ビルドツール等はキャッシュやレポートを生成し得る。集計コマンドはjqを使う。jqがなければ、Pythonの`json`モジュールで同じ値を取り出す。
