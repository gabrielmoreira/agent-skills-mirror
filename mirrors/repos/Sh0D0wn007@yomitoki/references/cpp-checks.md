# C++の機械検査：clang-tidy

先に [共通手順](language-checks.md#共通手順) を確認する。[Cの検査](c-checks.md) に記載したclang-tidyの準備、可読性ルール、閾値、件数の集計、Cppcheckとclang-formatの使い分けはC++でも共通のため、その手順を利用する。

```bash
clang-tidy --version
clang-tidy -p build src/example.cpp
```

C++の言語規格・標準ライブラリ・コンパイル条件は、対象プロジェクトの`compile_commands.json`に合わせる。ヘッダーはそれを利用する翻訳単位を通じた診断も確認する。`modernize-*`や`cppcoreguidelines-*`などのC++向けルールは既存設定と依頼範囲に従い、可読性改善だけを理由にAPIや所有権の設計を変更しない。
