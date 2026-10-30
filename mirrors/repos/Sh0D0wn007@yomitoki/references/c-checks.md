# Cの機械検査：clang-tidy

先に [共通手順](language-checks.md#共通手順) を確認する。

既存の`.clang-tidy`と`compile_commands.json`を利用する。`-p`はコンパイルデータベースがあるディレクトリ。実際のincludeパス・マクロ・言語規格・ターゲットに合わせる。データベースがない場合も、正しいコンパイル引数を特定できれば`--`の後ろへ渡せる。引数を推測した不完全な解析を完了扱いしない。

```bash
clang-tidy --version
clang-tidy -p build src/example.c > clang-tidy.txt
grep -E ': (warning|error): ' clang-tidy.txt | grep -oE '\[[^]]+\]$' | sort | uniq -c
```

診断は標準出力、`N warnings generated.`などの要約は標準エラーに出る。集計は`note:`の行を除き、チェック名ごとに数える。

可読性の追加検査では`readability-function-size`と`readability-function-cognitive-complexity`を候補にする。前者の`LineThreshold`・`ParameterThreshold`・`NestingThreshold`、後者の`Threshold`を編集前に明示する。初期候補はそれぞれ50・4・3・10だが、プロジェクトの基準を優先する。関数行数などの定義はPythonの付属検査と異なり、数値を言語間で直接比較しない。

既存設定がない場合は対象外の一時ディレクトリへ`.clang-tidy`を保存し、`--config-file=/absolute/path/.clang-tidy`で渡せる。既存設定を上書きしない。

```yaml
Checks: '-*,readability-function-size,readability-function-cognitive-complexity'
CheckOptions:
  readability-function-size.LineThreshold: 50
  readability-function-size.ParameterThreshold: 4
  readability-function-size.NestingThreshold: 3
  readability-function-cognitive-complexity.Threshold: 10
```

この追加設定は可読性専用で、コンパイラ警告や不具合検査の代わりにはならない。

既存のCppcheckはメモリ操作や未定義動作などの不具合候補、clang-formatは整形を確認する。Cppcheckを関数の複雑さの測定と同一視しない。clang-formatは`--dry-run --Werror`で点検する。C++専用ルールをCの必須ルールとして扱わない。

根拠：[clang-tidy](https://clang.llvm.org/extra/clang-tidy/)、[関数サイズ](https://clang.llvm.org/extra/clang-tidy/checks/readability/function-size.html)、[認知的複雑度](https://clang.llvm.org/extra/clang-tidy/checks/readability/function-cognitive-complexity.html)、[Cppcheck](https://cppcheck.sourceforge.io/manual.html)、[clang-format](https://clang.llvm.org/docs/ClangFormat.html)。
