# Javaの機械検査：PMD

先に [共通手順](language-checks.md#共通手順) を確認する。

既存のMaven/GradleタスクとPMDルールセットを優先する。JDK・ソースの言語バージョン・依存クラスパスを揃える。PMDの型解決に必要なクラスパスが不足する場合は、影響するルールの検査を未完了として報告する。

PMD 7を導入済みで、既存のルールセットがない場合の可読性検査例：

```bash
pmd --version
pmd check --dir src/main/java \
  --rulesets category/java/design.xml/CyclomaticComplexity,category/java/design.xml/CognitiveComplexity,category/java/design.xml/ExcessiveParameterList \
  --format json --no-cache > pmd.json
jq -r '.files[].violations[].rule' pmd.json | sort | uniq -c
```

この例は各ルールの既定閾値を使う。採用するバージョンの既定値を控え、変更する場合は専用のルールセットへ記録して前後で固定する。テストコードも編集対象なら`src/test/java`も検査する。JSONの`processingErrors`・`configurationErrors`を確認し、違反一覧だけで合否を決めない。PMD 7の終了コード4は違反あり、5は回復可能な処理エラーを示す。実行バージョンの定義も確認する。

Checkstyleは命名・行数・引数数などの規約、SpotBugsはバイトコードの不具合パターンを点検する。SpotBugsはコンパイルが必要で、PMDのソース解析とは検査範囲が異なる。設定がないツールを一度に全部追加しない。

根拠：[PMD CLIと終了コード](https://pmd.github.io/pmd/pmd_userdocs_cli_reference.html)、[PMDのJavaルール](https://pmd.github.io/pmd/pmd_rules_java_design.html)、[Checkstyle](https://checkstyle.org/checks.html)、[SpotBugs](https://spotbugs.readthedocs.io/en/stable/introduction.html)。
