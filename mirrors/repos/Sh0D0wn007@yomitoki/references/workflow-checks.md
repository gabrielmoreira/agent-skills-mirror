# 一括検査と修正前後の比較

## 退避と前後検査をまとめる

退避・前後検査・比較をまとめる `review_session.py` の使い方とPowerShellの実行例は、[退避と前後検査](review-session.md) を参照する。以下は個別に検査する場合の詳細。

## 一括検査

```bash
python3 /path/to/yomitoki/scripts/run_checks.py /path/to/project
```

`run_checks.py`は既存の構文指標検査と、Pythonファイルに対するRuffの次の検査を実行する。Python以外のファイルは構文指標だけを検査し、Pythonファイルがなければ Ruffは不要。Python以外を含む場合は、`requirements.txt`を導入したスキル直下の`.venv/bin/python`で実行する。Windowsでは、コマンドの`python3`を`python`に、`.venv/bin/`を`.venv\Scripts\`（Git Bashでは`.venv/Scripts/`）に読み替える。

- `F401`：未使用import
- `F841`：未使用のローカル変数
- `SIM`：条件式などの簡略化候補
- `RET`：return周辺の冗長な処理
- `ruff format --check`：整形設定との差分（1ファイルにつき1件）

Ruffには構文検査で正常に読めた`.py`を渡す。UTF-8のファイルは最大100件ずつパスで渡し、1回の起動でまとめて検査する。UTF-8以外のエンコーディングとBOM付きのファイルは、一つずつ標準入力から渡す。まとめた検査が失敗したときは一つずつ検査し直し、原因のファイルをエラーとして示す。検査対象のコードをimport・実行・変更せず、Ruffのキャッシュも生成しない。Ruffに渡す直前と終了後に元ファイルのハッシュを照合し、途中で変わったらエラーにする。Ruffが解析できなかったファイルや異常終了もエラーにする。

Ruffは独立した検査設定（`--isolated`）で実行する。対象プロジェクトやユーザーのRuff設定ファイル、`RUFF_*`環境変数は取り込まない。`noqa`によるlint抑制も無効にする。これにより設定による検査漏れを防ぎ、設定に`fix = true`があっても対象を書き換えない。フォーマッターが解釈する`fmt: off`などのコメントは有効。

整形の既定は行幅88、引用符は現状維持（`preserve`）。プロジェクトの規約に合わせて実行前に指定する。

```bash
python3 /path/to/yomitoki/scripts/run_checks.py \
  --line-length 100 --quote-style single --target-version py312 \
  --max-lines 60 --max-depth 4 /path/to/project
```

`--target-version`の既定は実行中のPythonのバージョン。構文指標は実行中のPythonが解釈できる構文に限られる。Ruffの設定だけ新しいバージョンにしても、この制約は変わらない。

既存のlintやフォーマッターを置き換えず、独立した設定との違いをプロジェクトの規約違反と断定しない。通常表示の「プロジェクトの検査: 未実行」はこのコマンドの範囲を表し、別途実行した検査の結果ではない。

## Ruffの導入

Ruffの検索順は`--ruff`で指定した実行ファイル、スキル直下の`.venv/bin/ruff`（Windowsでは`.venv\Scripts\ruff.exe`）、`PATH`上の`ruff`。Pythonの`-m ruff`を自動探索することはない。検証済みバージョンは [../requirements.txt](../requirements.txt) に固定している。

```bash
python3 -m venv /path/to/yomitoki/.venv
/path/to/yomitoki/.venv/bin/python -m pip install -r /path/to/yomitoki/requirements.txt
```

既存環境のRuffを利用する場合：

```bash
python3 /path/to/yomitoki/scripts/run_checks.py \
  --ruff /path/to/project/.venv/bin/ruff /path/to/project
```

未導入時はインストールせず、エラーを返す。構文指標の結果はJSONに残るが、一括検査完了とは扱わない。

## 整形の適用

`run_checks.py`は対象を書き換えない。`format-required`が出ると、検査と同じRuff・設定で整形するコマンドを「同じ設定で整形するには:」の行に表示する。JSONでは`ruff.formatCommand`（ファイルを除いた引数の配列）に入る。

表示するコマンドは、POSIXシェル（bash・zsh、WindowsではGit Bash）向けに引用符を付けている。PowerShell 7.3以降では、先頭に`& `を付ければそのまま実行できる。Windows PowerShell 5.1は引数の中の`"`を落とし、cmdは`'`を引用符として扱わないため、どちらでも動かない。その場合はGit Bashで実行するか、`ruff.formatCommand`の配列にファイルを加えて実行する。

- プロジェクトに既存のフォーマッター設定があれば、そちらで整形する。表示されたコマンドで既存のスタイルを上書きしない。
- 既存の設定がない場合や新規コードの場合は、表示されたコマンドをそのまま実行する。Ruffの場所や引数を推測して組み立てない。
- 整形した後は`run_checks.py`を同じ引数で再実行し、`format-required`が消えたことを確かめる。

## 理由付きの許容

分割するとかえって読みにくくなるなど、理由があって残す構文指標の指摘は`--accepted`で許容リストに記録できる。`check.py`と`run_checks.py`の両方で使える。閾値を緩める手段ではない。

```json
[
  {"path": "src/draw.py", "function": "circle", "rule": "max-params", "actual": 5, "reason": "strokeとwidthはキーワード専用で、呼び出し側に名前が見える"}
]
```

```bash
python3 /path/to/yomitoki/scripts/run_checks.py --accepted accepted.json /path/to/project
```

- `path`はリストファイルのあるディレクトリからの相対パス（区切りは`/`と`\`のどちらでもよく、MacとWindowsで同じリストを使える。`/`や`C:`で始まる絶対パスはどのOSでもエラー）、`function`は関数名（関数の外の三項式は`null`）、`rule`はルール名、`actual`は許容した時点の実測値、`reason`は空にできない理由。項目はこの5つで、過不足があればエラーにする。
- 照合は行番号を使わず、パス・関数名・ルールで行う。同じファイル内の同名の関数（別クラスの同名メソッドなど）は同じ項目に一致する。
- 対象は構文指標（`max-*`、`no-nested-ternary`）だけ。Ruffのlintと整形は許容できない（`noqa`を無効にしているのと同じ方針）。
- 一致し、実測値が`actual`以下の指摘は`issues`から`accepted`へ理由付きで移り、終了コードの判定から外れる。通常表示でも「許容済み: N件」と各指摘・理由を必ず表示する。
- 実測値が`actual`を超えた指摘は許容せず、`issues`に残す（`acceptedActual`付き）。通常表示では「許容時より悪化」と示す。許容を続けるなら、理由を見直してから`actual`を更新する。
- 一致する指摘がなくなった項目は「不要になった許容」（JSONでは`unusedAccepted`）として表示する。リストから削除する。
- 許容した指摘と理由は、作業の報告に転記する。

## 前後比較

### 編集直後の構文確認

`py_compile` による確認は構文・コンパイル時の確認であり、lint・型チェック・テストの代わりにはならない。`py_compile` はキャッシュを生成する。生成を避ける場合は、次の方法で対象を実行せずに確認できる。ファイルが複数なら列挙する。

```bash
python3 -B - /path/to/changed.py /path/to/another.py <<'PY'
import sys
from pathlib import Path
for name in sys.argv[1:]:
    compile(Path(name).read_bytes(), name, 'exec')
PY
```

### レポートの保存と比較

修正前後に同じコマンドでJSONを保存する。`before.json`を上書きしない。

```bash
python3 /path/to/yomitoki/scripts/run_checks.py --json /path/to/project > before.json
# 対象コードを修正する
python3 /path/to/yomitoki/scripts/run_checks.py --json /path/to/project > after.json
python3 /path/to/yomitoki/scripts/compare_reports.py before.json after.json
python3 /path/to/yomitoki/scripts/compare_reports.py --json before.json after.json
```

PowerShellで`>`を使って保存するときは、先に`[Console]::OutputEncoding = [System.Text.Encoding]::UTF8`を実行する。Windows PowerShell 5.1では、実行しないと日本語を含む出力が壊れ、JSONとして読めなくなる。5.1は保存したファイルをUTF-16にするが、`compare_reports.py`はUTF-8・UTF-16・BOM付きのどれでも読める（許容リストも同じ）。

検査コマンドは指摘があれば終了コード`1`を返すため、`&&`で比較処理を繋ぐとそこで止まる。JSONを保存したうえで、各結果を確認して次のコマンドを実行する。

比較は`check.py`同士、または`run_checks.py`同士で行う。異なる種類を混ぜると比較条件不一致になる。検査器のハッシュを含まない旧レポートは再生成が必要。

表示する内容：

- 指摘数の合計と、ファイル・ツール・ルールごとの増減。どちらも許容した指摘を含めて数えるため、許容を増やしても減少とは表示しない
- 許容した指摘の件数の増減（どちらかのレポートで`--accepted`を使った場合）
- 各ファイル内の関数指標の最大値（行数・引数数・深さ・複雑さ）の変化と、関数数の変化
- 閾値、Python/Ruff/tree-sitterのバージョン、検査スクリプトのハッシュ、Ruff設定の変更
- 検査済みファイルの追加・除外、探索時の除外ディレクトリやシンボリックリンクの変更

ファイルは同じ絶対パスで対応付ける。異なるチェックアウトや改名は追加・除外として表示し、自動で同じファイルと推測しない。行番号の移動は指摘の増減に数えない。そのため、同じファイル・同じルールの指摘が別の箇所へ移った場合は、件数が同じなら増減なしとなる。詳細位置は元のJSONで確認する。

エラーがある、条件が変わった、検査対象が増減した場合も算術上の差分は表示するが、`comparable`を`false`にし、改善とは判断しない。非対応拡張子のファイルの増減は比較条件に含めない。

指摘数の減少や指標の低下は、挙動の同一性や設計の適切さを証明しない。関数数の変化も併記し、無意味な関数分割で数値だけを下げていないか確認する。

### ファイルを追加・削除した場合

比較には、前後とも同じファイルの一覧を使う。ディレクトリを指定するとファイルの増減で検査対象が変わり、比較条件不一致になるため、前後の両方に存在するファイルを個別に並べる。

```bash
python3 /path/to/yomitoki/scripts/run_checks.py --json src/a.py src/b.py > before.json
# 対象コードを修正し、src/c.py を追加する
python3 /path/to/yomitoki/scripts/run_checks.py --json src/a.py src/b.py > after.json
python3 /path/to/yomitoki/scripts/compare_reports.py before.json after.json
python3 /path/to/yomitoki/scripts/run_checks.py src/c.py
```

新しいファイルは比較の相手がないため単独で検査し、指摘が0件か、残した指摘すべてに理由があることを確かめる。修正の途中で削除が決まり比較不能になった場合も、共通のファイルの指標の変化は表示される。削除が依頼の範囲内かは差分で確認する。

## 終了コードとJSON

`run_checks.py`は、`0`が検査した範囲で許容していない指摘なし、`1`が許容していない指摘あり、`2`が検査未完了・実行失敗。

`compare_reports.py`の通常表示とJSONの `status`・`message` は以下を区別する。

| status | 意味 | 終了コード |
| --- | --- | --- |
| `no-increase` | 同条件で指摘件数・最大指標の増加なし。既存の指摘が残っていても返り得る | 0 |
| `increase-notice` | いずれかのルールの件数または最大指標の増加通知。実行失敗ではない。関数数の増加だけでは返さない | 1 |
| `not-comparable` | 検査条件や対象の不一致 | 2 |
| `error` | 検査エラー・検査対象なし・レポート読み込みや形式の問題 | 2 |

説明的な名前による行の折り返しやdocstring追加でも行数は増える。`1` の場合は増加理由と可読性への影響を確認し、数値だけのために説明を削らない。`2` の場合は未完了の理由を解消するか、未検証として報告する。

一括検査JSONは構文検査のJSONに`ruff`（バージョン、設定、整形コマンドなど）と、検査範囲を示す `scope` を加える。検査の成功は `errors`・`issues`・`exitCode` で確認する。Ruffの指摘と、Python以外で構文を解析できない範囲（`parse-error`）の指摘は`tool`、`rule`、`message`と位置を持つ。ASTの列位置はUTF-8バイト単位、Ruffの列位置はRuffが出力した値をそのまま使う。整形指摘の位置`1:1`はファイル全体を表す。

## スクリプトの検証

```bash
YOMITOKI_RUFF=/path/to/yomitoki/.venv/bin/ruff \
  /path/to/yomitoki/.venv/bin/python -B -m unittest discover -s /path/to/yomitoki/tests -v
```

Windows（PowerShell）：

```powershell
$env:YOMITOKI_RUFF = "C:\path\to\yomitoki\.venv\Scripts\ruff.exe"
C:\path\to\yomitoki\.venv\Scripts\python.exe -B -m unittest discover -s C:\path\to\yomitoki\tests -v
```

`YOMITOKI_RUFF`を指定しないと実Ruffを使う結合テストはスキップされる。Python 3.9では`match`構文のテストも、tree-sitterがなければ他言語のテストもスキップされる。

外部ツールの根拠：[Ruffルール](https://docs.astral.sh/ruff/rules/)、[Ruffの設定](https://docs.astral.sh/ruff/configuration/)、[Ruff Formatter](https://docs.astral.sh/ruff/formatter/)。
