# 構文指標の検査

Pythonは、Python 3.9以上の標準ライブラリだけで検査する。`ast`による構文解析、実行しないコンパイルによる構文検証、`tokenize`による行数測定を行う。C・C++・Java・JavaScript・TypeScriptは、`requirements.txt`で固定したtree-sitterと各言語の文法パッケージ（Python 3.10以上）で構文木を作り、同じルールで測る。どちらも対象コードをimport・実行・変更しない。コメントの検査抑制記法は解釈しない。

このページは`check.py`の説明。一括検査`run_checks.py`と前後比較`compare_reports.py`は [workflow-checks.md](workflow-checks.md) を参照する。

## 実行

```bash
# ファイル、ディレクトリ、複数の対象を指定可能
python3 /path/to/yomitoki/scripts/check.py /path/to/project
python3 /path/to/yomitoki/scripts/check.py --json file_a.py file_b.py

# プロジェクトの基準に合わせて閾値を明示する
python3 /path/to/yomitoki/scripts/check.py --max-lines 60 --max-depth 4 /path/to/project

# Python以外を含む場合は、requirements.txtを導入した.venvのPythonで実行する
/path/to/yomitoki/.venv/bin/python /path/to/yomitoki/scripts/check.py /path/to/project
```

Windowsでは、コマンドの`python3`を`python`に、`.venv/bin/`を`.venv\Scripts\`（Git Bashでは`.venv/Scripts/`）に読み替える。

対象コードで使われている構文を理解できるPythonで実行する。例えばPython 3.9では`match`構文を解析できず、検査エラーとなる。

理由があって残す指摘は、`--accepted 許容リスト.json`で許容できる。形式と注意点は [workflow-checks.md](workflow-checks.md#理由付きの許容) を参照する。

終了コード：`0`は検査した範囲で指摘なし（許容した指摘を除く）、`1`は可読性の指摘あり、`2`は構文エラー・読み取り失敗・対象なしなどの検査エラー。エラーと指摘が同時にあれば`2`を返す。引数の誤りはargparseが終了コード`2`と使い方を標準エラーへ出す。

## 初期ルールと定義

| ルール | 初期値 | 測定内容 |
| --- | ---: | --- |
| `max-lines` | 50 | 関数定義行から末尾までのコード行数。空行とコメントだけの行を除く。複数行文字列・docstring・内部に定義した関数の行は含む。デコレータの行は除く。 |
| `max-params` | 4 | 宣言された引数の数。位置専用・キーワード専用・`*args`・`**kwargs`を含む。`self`や`cls`も含む。 |
| `max-depth` | 3 | 関数本体内のif・ループ・with・try・matchのブロック深さ。elifは同じ深さ。else配下の独立したifは一段深い。except/finallyはtryと同じ深さ。 |
| `max-complexity` | 10 | 初期値1に、if/elif・ループ・三項式・exceptを各1、and/orの接続数、内包表記のforとifの数を加える。matchは無条件の捕捉パターン以外のcaseとガードを各1加える。 |
| `no-nested-ternary` | 禁止 | 三項式の内部に別の三項式が含まれる箇所。関数・クラス・lambdaの境界でリセットする。 |

関数指標の対象は`def`と`async def`（メソッドを含む）。内部関数は別に測定し、外側の深さ・複雑さへ加算しない。内部クラスとlambdaも外側の深さ・複雑さへ加算しない。トップレベルとlambda自体の関数指標は測定しない。三項式の検査はファイル全体で行う。

### Python以外の言語

| 言語 | 拡張子 |
| --- | --- |
| C | `.c`・`.h`（C++の宣言がないもの） |
| C++ | `.cc`・`.cpp`・`.cxx`・`.h`（C++の宣言があるもの）・`.hh`・`.hpp`・`.hxx` |
| Java | `.java` |
| JavaScript | `.js`・`.jsx`・`.mjs`・`.cjs` |
| TypeScript | `.ts`・`.mts`・`.cts`・`.tsx` |

`.h`はCとC++で共用されるため、ファイルの中身で解析する言語を決める。行頭（インデントは可）に`namespace`・`template<`（`template <`を含む）・`class 名前`・`public:`・`private:`・`protected:`のいずれかがあればC++、なければCとして解析する。`::`は、Cのヘッダーでもコメントに`std::`などと書かれるため判定に使わない。

ルールの意味はPythonにそろえ、各言語の構文を次のように対応させる。

- 関数：関数定義・メソッド・コンストラクタ・関数式・アロー関数・ラムダ式。内部の関数は別に測定し、外側の深さ・複雑さへ加算しない。名前のない関数は代入先の名前、なければ`<anonymous>`とする。
- `max-lines`：関数の構文の開始行から末尾まで。前の行にある戻り値の型・注釈・デコレーターも含む。複数行の文字列やテンプレートリテラルは含む。
- `max-params`：宣言された引数の数。既定値付き・可変長（`...`）・TypeScriptの`this`を含む。Cの`(void)`は0。
- `max-depth`：if・ループ（do-whileを含む）・switch・try・with・Javaのsynchronizedのブロック深さ。`else if`は同じ深さ、`else { if }`は一段深い。catch/finallyはtryと同じ深さ。波括弧のない本体も数える。
- `max-complexity`：初期値1に、if・ループ・三項演算子・catch・`default`以外のcaseを各1、`&&`・`||`・`??`の数を加える。C++の畳み込み式（`(a || ...)`・`(... && a)`など）も、演算子が`&&`か`||`なら1を加える。`#if`などのプリプロセッサ条件はコンパイル時の分岐なので数えない。
- `no-nested-ternary`：三項演算子の内部に別の三項演算子が含まれる箇所。関数の境界でリセットする。

tree-sitterが解析できない範囲は、`tool`が`tree-sitter`、`rule`が`parse-error`の指摘として位置を報告し、その範囲を含む関数は測定しない。終了コードは指摘ありの`1`になり、「指摘なし」には含めない。C・C++のマクロ（`#ifdef __cplusplus`で分けた`extern "C" {`や、型の前に並べた`static`・`inline`相当のマクロなど）や、文法パッケージより新しい構文で起こる。実際の構文エラーとの区別はしないため、ビルド・型チェックで確認する。

TypeScriptの変性注釈（`<in T>`・`<out T>`・`<in out T>`）は、固定しているtree-sitter-typescript 0.23.2が読めない。そのため構文木にエラーがあるときだけ、型引数の中のエラーの直前やエラーの先頭にある`in`・`out`を同じバイト数の空白に置き換えて解析し直す。行と列の位置は変わらない。`for (k in o)`や`out`という名前など、型引数の外のコードは置き換えない。ファイルは変更せず、`files`のSHA-256も元の内容で計算する。`parse-error`は許容リストで許容できない。Pythonは構文エラーなら不正なコードなので、従来どおりファイル全体を検査エラーにする。tree-sitterと文法パッケージがない環境では、該当ファイルが検査エラーになる。

初期値は見直し候補を拾うための設定で、普遍的な基準ではない。関数の種類やコードの用途に合わせて、編集前にプロジェクトの基準を決める。長い宣言的な設定や単純な一覧などは、閾値超過だけを理由に分割しない。

## 範囲と出力

再帰探索では`.py`と、上表の拡張子のファイルを検査する。`.git`、`.venv`、`venv`、`__pycache__`、`node_modules`、`.next`、`build`、`dist`を除外する。シンボリックリンクのファイルとディレクトリは辿らない。明示した通常のファイルやディレクトリは、名前にかかわらず探索対象とする。`.gitignore`は解釈しない。

JSONは次の情報を含む。

- `files`：検査できたファイルの絶対パスと元ファイルのSHA-256
- `functions`：関数ごとの行数・引数数・最大深さ・複雑さ
- `issues`：ルール名、位置、実測値、閾値、関数名（関数の外は`null`）
- `accepted`、`unusedAccepted`：`--accepted`を指定したときだけ入る。許容した指摘（理由と許容時の実測値付き）と、一致する指摘がなかった許容項目
- `errors`：検査できなかった対象と理由
- `skipped`：非対応拡張子や探索時の除外対象と理由
- `limits`、`pythonVersion`、`schemaVersion`、`kind`、`checkerSha256`：再現・比較に必要な条件と検査器のSHA-256
- `parsers`：Python以外の解析に使ったtree-sitterと文法パッケージのバージョン。比較条件に含む

位置は1始まり。`issues.column`はUTF-8バイト位置であり、日本語を含む行では表示上の文字位置と一致しないことがある。出力順序は固定し、実行日時を含めない。同じコード・パス・Pythonバージョン・解析器のバージョン・閾値なら同じ結果になる。

`check.py`・`run_checks.py`・`compare_reports.py`・`diff_code.py`の標準出力と標準エラーは、OSのロケールにかかわらずUTF-8で出す。日本語版Windowsのcp932では表せない文字（絵文字など）を含むパスでも、出力の途中で失敗しないためである。WindowsのPowerShellで出力を変数やパイプで受け取るとき、`>`でファイルに保存するときは、先に`[Console]::OutputEncoding = [System.Text.Encoding]::UTF8`を設定する。

## 結果の読み方

「深さ4で上限3を超えた」は機械的に確認できる事実。「早期returnへ直すべき」は周辺の契約を読んで判断する提案。両者を区別する。

指摘なしは読みやすさの保証ではない。名前の意味、適切な責務、重複の意味、コメントの正確さ、仕様の正しさ、変更前後の挙動は、この検査では証明できない。既存のlint・型チェック・テストを置き換えない。

構文解析の根拠：[Python ast](https://docs.python.org/3/library/ast.html)、行数測定の根拠：[Python tokenize](https://docs.python.org/3/library/tokenize.html)、他言語の構文解析：[tree-sitter](https://tree-sitter.github.io/tree-sitter/)。指標の定義はこのスクリプト独自のもので、他ツールの循環的複雑度と常に一致するわけではない。
