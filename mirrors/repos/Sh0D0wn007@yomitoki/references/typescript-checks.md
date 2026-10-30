# TypeScriptの機械検査

先に [共通手順](language-checks.md#共通手順) を確認する。[JavaScriptの検査](javascript-checks.md) の手順に、以下の型に関する検査を追加する。

`.ts`・`.tsx`・`.mts`・`.cts`が実際の検査対象に含まれることを確認する。ESLintではtypescript-eslintの既存設定を使い、型情報が必要なルールは対象のtsconfigに結び付ける。型情報なしのlintを、型を使ったlintとして報告しない。

| 導入済みツール | 自動修正しない実行例 | 用途・注意 |
| --- | --- | --- |
| ESLint＋typescript-eslint | `./node_modules/.bin/eslint src --format json` | TypeScriptの構文・規約と、設定済みなら型を使ったlint |
| TypeScript | `./node_modules/.bin/tsc --noEmit -p tsconfig.json` | プロジェクト全体の型チェック。ビルド参照を使う場合は既存のtypecheckタスクを優先する |

Biome・Oxlintの型を使ったlintも、TypeScriptコンパイラの型チェックとは別に扱う。型チェックが通っても、ランタイムの入力値やDOM操作の正しさまでは保証しない。

ESLintの集計はJavaScriptの検査と同じ。tscは保存した出力からエラーコード別の件数を出す。

```bash
grep -oE 'error TS[0-9]+' tsc.txt | sort | uniq -c
```

根拠：[typescript-eslintの型情報を使う検査](https://typescript-eslint.io/getting-started/typed-linting/)、[TypeScript noEmit](https://www.typescriptlang.org/tsconfig/noEmit)。
