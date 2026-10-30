# 退避と前後検査をまとめる

既存コードの修正では `review_session.py` で、現在のソースの退避と前後比較をまとめられる。検査対象のコードを変更・import・実行せず、既存の `run_checks.py`・`compare_reports.py`・`diff_code.py` を使う。プロジェクトのテスト・lint・型チェック・ビルドは別途実行する。

```bash
/path/to/yomitoki/.venv/bin/python /path/to/yomitoki/scripts/review_session.py begin \
  --state-root /path/outside/project/reviews \
  --context \
  /path/to/project/module.py /path/to/project/test_module.py
# 必要な変更と、構造変更直後の構文確認を行う
/path/to/yomitoki/.venv/bin/python /path/to/yomitoki/scripts/review_session.py finish \
  --state-dir /path/outside/project/reviews/review-xxxx \
  --include-diffs --review-notes /path/outside/project/reviews/review-xxxx/review-notes.json
```

`review-xxxx` は例示。`begin` の結果にある `stateDir`・`reviewNotesPath` の実際の値を使う。`finishCommand` に同じ引数配列も含まれる。依存を導入済みの実行環境を使い、Ruffを明示する場合は `begin --ruff /path/to/ruff` を指定する。

Windowsでは、最初の読込・実行からUTF-8を設定する。新しいPowerShellプロセスで実行するときも同じ設定を使う。

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = 'utf-8'
$reviewPython = 'C:\path\to\yomitoki\.venv\Scripts\python.exe'
& $reviewPython 'C:\path\to\yomitoki\scripts\review_session.py' begin --state-root 'C:\outside\reviews' --context 'C:\project\module.py'
```

- `begin` は現在のファイルを保存し、対象の絶対パス・ハッシュ・検査設定と `before.json` を記録する。未コミットの変更も含み、GitのHEADには置き換えない。
- `begin --context` は退避した全ソース、14項目の基準、この実行手順を結果に含める。省略・要約したソースを読んだことにはしない。大きな対象ではこのオプションを省き、関連ファイルをまとまりごとに読む。必要な確認範囲は変えない。
- `begin --state-root` は検査対象ディレクトリや対象ファイルの親ディレクトリの外に保存用親ディレクトリを指定する。親は既存でもよく、毎回一意な子ディレクトリを作成する。ほかの作業の保存内容を上書きしない。存在しない親は作成する。
- 保存先の名前を固定する場合は、従来の `begin --state-dir` を使える。この場合は未作成のパスが必要で、既存のディレクトリは拒否する。作成済みの作業用親を使う場合は `--state-root` を選ぶ。両オプションは同時に指定できない。権限のある保存先を選び、拒否された操作を形だけ変えて繰り返さない。
- `finish` は同じ対象・設定で `after.json`、指標比較、全変更ファイルのテキスト差分、変更したPythonの構造差分を保存する。繰り返す場合は新しい結果ディレクトリへ保存し、過去の結果は上書きしない。
- `finish --include-diffs` は保存する全差分も結果に含める。後続のファイル読み込みだけの呼び出しを減らせる。大きな差分では省略し、保存された全差分をまとまりごとに読む。
- 出力する短いJSONと、そこに示す詳細成果物を読む。表示形式を変えるためだけに同じ検査を再実行しない。対象・設定が変わった場合や、未解決の失敗がある場合は必要な検査を再実行する。
- `finish` は予定した編集・整形を終えてから実行する。整形後に構造を直す予定があるなら、その途中では呼ばない。短いJSONにも指摘と主要な比較結果が入るため、それを読み、ソース差分は保存先から読む。
- `begin` は有効な比較元を保存できれば終了コード `0`。`finish` は同条件で指摘・最大指標の増加なしなら `0`、増加通知なら `1`。どちらも実行失敗・未完了・比較条件不一致は `2`。変更前検査が失敗した状態を有効な比較元にしない。
- 検査器自体の終了コードは短いJSONの `checkExitCode` と詳細レポートに残る。指摘があっても比較元の保存や比較は成功するため、補助処理の `0` は「指摘なし」ではない。残った指摘を読み、維持する理由を報告する。ファイルの追加・削除を改善として扱わない。
- 保存された差分を読み、契約・評価順序・副作用・コメントの正確さを人が点検する。指摘数やASTの一致だけで挙動の同一性を保証しない。

`begin` は `--line-length`・`--quote-style`・`--target-version` に対応する。独自の構文指標の閾値や許容リストを使う場合は、[個別実行手順](workflow-checks.md)を使う。新規コードや読み取りだけのレビューでは退避セッションは不要で、`run_checks.py` を単独で実行する。

## 呼び出しをまとめる順序

1. 対象・契約を確認し、資料と変更前検査をまとめて読む。`context.sources` に受け取った全ソースをそのまま使い、同じ版を個別に再読込しない。途中省略や未取得の呼び出し元は追加で読む。判断前に編集しない。
2. 14項目をそれぞれ確認して方針を決め、関連する編集と、その直後の構文確認を同じ呼び出し内で順に行う。構文確認に失敗したら先へ進まない。
3. 予定した編集を終えてから、整形・構文確認・必要なテスト等・`finish` をまとめて実行する。各結果を別々に保持する。`finish` 自体はプロジェクトのテスト等を実行しない。
4. 返された全差分とレビュー記録を読んで契約と照合する。必要な修正があれば再編集・再検証する。呼び出し数は上限を決めず、確認を省略しない。

出力の途中省略があった場合は、未読部分を回収してから確認記録を確定する。内側のコマンドだけでなく、それを呼ぶ外側の実行ツールにも十分な出力予算を指定する。省略が残った実行は「全14項目を確認できた時間短縮」の検証結果として扱わない。

## 14項目の確認記録

`finish --review-notes FILE` にJSON配列を渡す。項目1〜14を各1件、重複なく記録し、各要素は `item`・`status`・`evidence` の3フィールドにする。例えば1件は `{"item": 2, "status": "checked", "evidence": "module.py:calculate_order — 金額の段階が変数名から分かることを確認"}`。同じ形式で全14項目を記載する。

`status` は `checked`（確認済み）、`not-applicable`（対象外）、`unverified`（未確認）。`evidence` は空にせず、確認箇所と根拠、対象外の理由、または未確認の理由を書く。記録は差分と同じ成果物へ保存される。欠けた項目や重複・不正な形式はエラー、未確認があれば未完了（終了コード2）として示す。後方互換のため、オプションを省いた実行も可能だが、その場合は確認記録なしと表示する。

この検査は記録の網羅性だけを確認する。14件あることや、すべてが確認済みと書かれていることから、判断の正しさや見落としゼロを保証しない。コード・全差分・根拠を別途照合する。

### PowerShellでの整形と構文確認

既存のプロジェクト設定がない場合にRuffで整形するときは、保存した `before.json` の引数配列をPythonから実行できる。PowerShell 5.1でも `format.quote-style` の引用符を手で組み直さずに渡せる。パスは実在するものへ置き換える。既存のフォーマッター設定がある場合は、そのプロジェクトのコマンドを使う。

```powershell
$reviewPython = 'C:\path\to\yomitoki\.venv\Scripts\python.exe'
& $reviewPython -c "import json,subprocess,sys; report=json.load(open(sys.argv[1],encoding='utf-8')); subprocess.run(report['ruff']['formatCommand']+sys.argv[2:],check=True)" 'C:\review\before.json' '.\module.py' '.\test_module.py'
```

構造の編集直後は、複数ファイルをまとめて構文確認できる。対象コードは実行しない。

```powershell
& $reviewPython -c "import sys; from pathlib import Path; [compile(Path(p).read_bytes(),p,'exec') for p in sys.argv[1:]]" '.\module.py' '.\test_module.py'
```

PowerShellにはbashの `python - <<'PY'` は使えない。here-stringをPythonの末尾引数に付けても標準入力にはならない。複数行を渡す必要があるときは、`$OutputEncoding = [System.Text.Encoding]::UTF8` を設定し、here-stringを変数に代入して `$code | & $reviewPython -B -` とパイプで渡す。
