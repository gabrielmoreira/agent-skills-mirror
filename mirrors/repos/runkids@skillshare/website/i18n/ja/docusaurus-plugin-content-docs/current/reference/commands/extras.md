---
sidebar_position: 2
---

# extras

Skill と一緒に sync される、Skill 以外のリソース（rules、commands、prompts など）を管理します。

## 概要

Extras は skillshare が管理する追加のリソースタイプです — いわば「Skill 以外のコンテンツ用の Skill」と考えてください。よくある用途としては、AI の rules、エディタの commands、prompt テンプレートをツール間で sync することが挙げられます。

各 Extras は以下を持ちます。
- **名前**（例: `rules`、`prompts`、`commands`）
- **Source ディレクトリ** — `extras_source` または Extras ごとの `source` で設定可能。デフォルトは `~/.config/skillshare/extras/<name>/`（グローバル）または `.skillshare/extras/<name>/`（Project）
- 同期先となる 1 つ以上の **Target**

## コマンド

### `extras init`

新しい Extras リソースタイプを作成します。

```bash
# インタラクティブウィザード
skillshare extras init

# CLI フラグ
skillshare extras init <name> --target <path> [--target <path2>] [--mode <mode>]
```

**オプション:**

| フラグ | 説明 |
|------|-------------|
| `--target <path>` | Target ディレクトリのパス（複数指定可） |
| `--mode <mode>` | sync モード: `merge`（デフォルト）、`copy`、または `symlink` |
| `--flatten` | サブディレクトリ内のファイルを Target のルート直下に sync する（`symlink` モードとは併用不可） |
| `--source <path>` | この Extras 用のカスタム Source ディレクトリ（`extras_source` とデフォルトを上書き。**グローバルモードのみ**） |
| `--force` | すでに存在する Extras を上書き |
| `--no-tui` | インタラクティブウィザードをスキップし、CLI フラグのみを使用 |
| `--project, -p` | Project 設定（`.skillshare/`）内に作成 |
| `--global, -g` | グローバル設定内に作成 |

:::note
`--source` はグローバルモードでのみサポートされています。Project mode では常に `.skillshare/extras/<name>/` が Source ディレクトリとして使われます。
:::

**例:**

```bash
# rules を Claude と Cursor に sync
skillshare extras init rules --target ~/.claude/rules --target ~/.cursor/rules

# カスタムの Source ディレクトリを使う
skillshare extras init rules --target ~/.claude/rules --source ~/company-shared/rules

# 既存の Extras を新しい Target で上書きする
skillshare extras init rules --target ~/.cursor/rules --force

# copy モードの Project スコープ Extras
skillshare extras init prompts --target .claude/prompts --mode copy -p

# agents をフラットに sync（Claude Code のようなツールはフラットなファイルしか検出しない）
skillshare extras init agents --target ~/.claude/agents --flatten
```

### `extras list`

設定済みのすべての Extras と、その sync 状態を一覧表示します。デフォルトでインタラクティブ TUI を起動します。

```bash
skillshare extras list [--json] [--no-tui] [-p|-g]
```

**オプション:**

| フラグ | 説明 |
|------|-------------|
| `--json` | JSON 出力（`source_type`: `per-extra` / `extras_source` / `default`、および設定されている場合は Target ごとの `extension` フィールドを含む） |
| `--no-tui` | インタラクティブ TUI を無効化し、プレーンテキスト出力を使用 |
| `--project, -p` | Project モードの Extras（`.skillshare/`）を使用 |
| `--global, -g` | グローバルの Extras（`~/.config/skillshare/`）を使用 |

#### インタラクティブ TUI

TUI は、左側に Extras リスト、右側に詳細パネルを配置した分割ペイン UI を提供します。キーバインド:

| キー | 動作 |
|-----|--------|
| `↑↓` | リストを移動 |
| `/` | 名前でフィルタ |
| `Enter` | コンテンツビューア（Source ファイルを閲覧） |
| `N` | 新しい Extras を作成 |
| `X` | Extras を削除（確認あり） |
| `S` | Extras を Target に sync |
| `C` | Target から collect |
| `M` | Target の sync モードを変更 |
| `F` | Target の flatten を切り替え |
| `Ctrl+U/D` | 詳細パネルをスクロール |
| `q` / `Ctrl+C` | 終了 |

各行のカラーバーは、集約された sync 状態を反映します: シアン = すべて sync 済み、黄色 = drift、赤 = 未 sync、灰色 = Source なし。

複数 Target を持つ Extras の場合、`S`、`C`、`M`、`F` は Target のサブメニューを開きます。`S` と `C` はすべての Target を一括選択できますが、`M` と `F` は特定の Target を選ぶ必要があります。

TUI は `skillshare tui off` で完全に無効化できます。

#### プレーンテキスト出力

TUI が無効な場合（`--no-tui`、`skillshare tui off`、またはパイプされた出力）:

```
$ skillshare extras list --no-tui

Extras
─────────────────────────────────────────
→ rules  ~/.config/skillshare/extras/rules/ · 2 files
  ✓ ~/.claude/rules  merge
  ✓ ~/.cursor/rules  copy

→ codex-agents  ~/.config/skillshare/agents · 3 files
  ✓ ~/.codex/agents  extension: codex-agents
```

sync 済みの行にはアイコン、パス、モードのみが表示されます。未 sync の行にはステータス語（`drift`、`not synced`、`no source`）が追記されます。変換拡張子（extension）を持つ Target は、sync モードの代わりに `extension: <name>` と表示されます（実際のモードは常に `copy` です）。

### `extras source`

グローバルな `extras_source` ディレクトリを表示または設定します。これは Extras の Source ファイルが格納されるデフォルトの親ディレクトリです。

```bash
skillshare extras source            # 現在の値を表示
skillshare extras source <path>     # 新しい値を設定
```

引数なしの場合、現在の `extras_source` パスを表示します（自動検出された場合は `(default)` が付きます）。パスを引数に渡すと、グローバル設定の `extras_source` を更新します。

:::note
このコマンドはグローバル専用です。Project mode では常に `.skillshare/extras/` が使われ、`extras_source` はサポートされません。
:::

**例:**

```bash
# 現在の extras_source を表示
skillshare extras source

# 共有ディレクトリに設定
skillshare extras source ~/company-shared/extras
```

### 既存の Extras を操作する

`extras <name>` へのフラグを通じて、Target の sync モードや flatten 設定の変更、Target の追加・削除を行います。これらは設定のみの変更のため、変更をディスクに適用するには後で `skillshare sync extras` を実行してください。

```bash
skillshare extras <name> --mode <mode> [--target <path>] [-p|-g]
skillshare extras <name> --flatten | --no-flatten [--target <path>]
skillshare extras <name> --add-target <path> [--mode <mode>] [--flatten] [-p|-g]
skillshare extras <name> --remove-target <path> [--prune] [-p|-g]
```

**オプション:**

| フラグ | 説明 |
|------|-------------|
| `--mode <mode>` | 新しい sync モード: `merge`、`copy`、または `symlink` |
| `--flatten` | flatten を有効化（サブディレクトリのファイルを Target ルートに sync） |
| `--no-flatten` | flatten を無効化 |
| `--add-target <path>` | Extras に新しい Target を追加 |
| `--remove-target <path>` | Extras から Target を削除（デフォルトでは設定のみ） |
| `--prune` | `--remove-target` と併用: その Target 配下の skillshare 管理ファイルも削除 |
| `--target <path>` | Target ディレクトリのパス（複数 Target を持つ Extras で `--mode` を使う場合は必須。省略時、`--flatten`/`--no-flatten` はすべての Target に適用される） |
| `--project, -p` | Project モードの Extras（`.skillshare/`）を使用 |
| `--global, -g` | グローバルの Extras（`~/.config/skillshare/`）を使用 |

**例:**

```bash
# rules のモードを変更（単一 Target — 自動解決）
skillshare extras rules --mode copy

# Target を明示的に指定する（複数 Target の Extras では必須）
skillshare extras rules --mode copy --target ~/.claude/rules

# すべての Target で flatten を一括有効化/無効化
skillshare extras agents --flatten
skillshare extras agents --no-flatten

# 既存の Extras に新しい Target を追加する（その後 sync）
skillshare extras rules --add-target ~/.cursor/rules
skillshare extras commands --add-target ~/.config/opencode/commands --mode copy

# Target を削除する（sync 済みファイルはそのまま残す）
skillshare extras rules --remove-target ~/.cursor/rules

# Target を削除し、その sync 済みファイルも削除する
skillshare extras rules --remove-target ~/.cursor/rules --prune
```

TUI（`M` キー）と Web UI（各 Target のモードのドロップダウンと flatten チェックボックス）からも操作できます。

### `extras remove`

設定から Extras を削除します。

```bash
skillshare extras remove <name> [--force] [-p|-g]
```

Source ファイルと sync 済みの Target は削除されません — 設定エントリのみが削除されます。

### `extras collect`

Target 内のローカルファイルを Extras の Source ディレクトリに集約します。ファイルは Source にコピーされ、シンボリックリンクに置き換えられます。

```bash
skillshare extras collect <name> [--from <path>] [--dry-run] [-p|-g]
```

**オプション:**

| フラグ | 説明 |
|------|-------------|
| `--from <path>` | collect 元の Target ディレクトリ（複数 Target がある場合は必須） |
| `--dry-run` | 変更を加えずに、collect される内容をプレビュー |

**例:**

```bash
# rules を Claude から Source に collect する
skillshare extras collect rules --from ~/.claude/rules

# collect される内容をプレビュー
skillshare extras collect rules --from ~/.claude/rules --dry-run
```

---

## Sync モード

| モード | 動作 |
|------|----------|
| `merge`（デフォルト） | Target から Source へのファイルごとのシンボリックリンク |
| `copy` | ファイルごとのコピー |
| `symlink` | ディレクトリ全体のシンボリックリンク |

モードを切り替える場合（例: `merge` から `copy` へ）、次の `sync` で既存のシンボリックリンクが自動的に新しいモードの形式に置き換えられます。`--force` は不要です — シンボリックリンクは常に安全に置き換えられます。ローカルで作成された通常のファイルを上書きするには `--force` が必要です。

---

## フラット化（Flatten）

一部の AI ツール（例: Claude Code の `/agents`）は、設定ディレクトリの**トップレベル**にあるファイルしか検出しません — サブディレクトリを再帰的には探索しません。Extras の Source が整理用にサブディレクトリを使っている場合、sync されたファイルはそのツールから見えなくなってしまいます。

`flatten` オプションは、Source 内のサブディレクトリの深さに関係なく、すべてのファイルを Target ルート直下に sync することでこれを解決します。

```yaml
extras:
  - name: agents
    targets:
      - path: ~/.claude/agents
        flatten: true
```

**動作:**
- `flatten: true`: `source/curriculum/tactician.md` → `target/tactician.md`
- `flatten: false`（デフォルト）: `source/curriculum/tactician.md` → `target/curriculum/tactician.md`

**ファイル名の衝突:** 異なるサブディレクトリにある 2 つのファイルが同じ名前を持つ場合（例: `team-a/agent.md` と `team-b/agent.md`）、最初のファイル（パスのアルファベット順でソート）が優先されます。以降の衝突は警告付きでスキップされます。

**制約:**
- `merge` モードと `copy` モードでのみ動作します — `symlink` モードとは併用できません
- `collect` は新しく collect したファイルを Source のルートに配置します（新規ファイルにはサブディレクトリへのマッピングはありません）

---

## 拡張子変換（Extension transforms）

一部のツールは markdown を読み込みません。Gemini CLI は TOML の commands を、Codex CLI は TOML の agents を期待します。Target の `extension` フィールドは、sync 時に各 Source ファイルを Target のネイティブ形式に変換する外部スクリプトを実行します。

```yaml
extras:
  - name: commands
    targets:
      - path: .claude/commands        # extension なし — そのまま sync
      - path: .gemini/commands
        extension: gemini-commands           # sync 時に変換
```

**解決方法** — 裸の名前は extensions ディレクトリ配下（グローバルは `~/.config/skillshare/extensions/<name>`、Project は `.skillshare/extensions/<name>`）で解決されます。パス（`./x.sh`、`/abs/x`）はそのまま使われます。

**コピーの意味論** — `extension` は `copy` モードを暗黙的に指定します。`extension` を持つ Target に `mode: merge` または `mode: symlink` を設定するとエラーになります。

**一方向** — 変換は Source → Target の方向のみ実行されます。`extras collect` は extension を持つ Target をスキップします。

**上書きの安全性** — 生成される出力は `copy` モードと同じ衝突ルールに従います。出力先に残っているシンボリックリンクは自動的に置き換えられますが、ローカルで作成した既存の通常ファイルやディレクトリはそのまま残り、`--force` を指定しない限りスキップされます（`--force` を指定すると、衝突するディレクトリは生成されたファイルで丸ごと置き換えられます）。

### Extension のレイアウト

単一の実行ファイル、またはマニフェスト付きのディレクトリのいずれかです。

```
.skillshare/extensions/gemini-commands/
├── extension.yaml
├── convert.js        # 編集するマッピングルール
└── md-toml.js        # markdown/frontmatter/TOML 用のヘルパー
```

`extension.yaml`:

```yaml
run: ["node", "convert.js"]      # 明示的なコマンド（argv）。直接 exec される
output_ext: toml                  # .md → .toml。省略すると Source の拡張子を維持
description: "Markdown command → Gemini CLI TOML"
```

マニフェストのない単一ファイルの実行ファイルは直接 exec され（Unix 上ではシェバンに依存）、Source の拡張子を維持します。拡張子を変更する変換にはディレクトリ形式を使う必要があります。

### 実行契約

- Source ファイルの内容は **stdin** で渡され、スクリプトは変換後の内容を **stdout** に書き出します。
- 環境変数: `SS_SRC_PATH`、`SS_REL_PATH`（Source ルートからの相対パス — Gemini の `/namespace:command` の命名に便利）、`SS_TARGET_DIR`、`SS_MODE`。
- 非ゼロの終了コードはそのファイルを失敗としてマークします。他のファイルの処理は継続されます。

### クロスプラットフォーム対応

この仕組み自体はクロスプラットフォームですが、extension が実行されるかどうかはそのインタープリタ次第です。`run` は明示的なコマンドであるため、`node` や `python3` 用に書かれた extension は Windows、macOS、Linux で動作します。純粋な `bash` スクリプトは、シェルが利用可能な環境（Unix、または Git Bash のある Windows）でのみ動作します。参照用の extension には Node が推奨インタープリタです。プラットフォームを問わず一様に提供されるためです。

### 参照用の Extension

skillshare リポジトリは、`extensions/` 配下にサンプル extension（`gemini-commands`、`codex-agents`）を同梱しています。いずれかを自分の extensions ディレクトリにコピーして調整してください — これらは参照用であり、自動的にはインストールされません。各参照用 extension は、フィールドマッピングだけを編集すれば済むよう `convert.js` を短く保っています。`md-toml.js` が markdown の読み込み、簡易フロントマターの解析、TOML の書き出しを担当します。

### レシピ: Codex agents

Codex CLI は markdown ではなく TOML の agents を期待します。`source` は任意のディレクトリを指せるため、agents の Source を Extras の Source として再利用し、`codex-agents` で変換できます。

```yaml
extras:
  - name: codex-agents
    source: ~/.config/skillshare/agents   # agents の source を再利用
    targets:
      - path: ~/.codex/agents
        extension: codex-agents
```

`skillshare sync extras` は各 `<agent>.md` を `~/.codex/agents/<agent>.toml` に変換し、フロントマターの `name`、`description`、`model` をマッピングし、markdown 本文を `developer_instructions` に折り込みます（その他のフロントマターキーは破棄されます）。[Codex custom agent schema](https://developers.openai.com/codex/subagents#custom-agent-file-schema) は `name`、`description`、`developer_instructions` を必須としているため、参照用の変換スクリプトは解決された name、description、または markdown 本文が空の場合に明確なエラーを報告します。agents の別コピーを用意する必要はありません。

---

## レシピ: 複数の Agent 間で共有する指示

現在、多くのコーディング Agent は標準の指示として `AGENTS.md` を読み込みますが、それぞれユーザーレベルのコピーを別々のディレクトリに保持しています。複数の Target を持つ 1 つの Extras で、単一の Source ファイルをそれらすべてに配布できます。

```bash
skillshare extras init instructions \
  --target ~/.codex \
  --target ~/.config/opencode \
  --target ~/.claude \
  --target ~/.gemini \
  --no-tui
```

`AGENTS.md` を解決済みの Source ディレクトリ（デフォルトでは `~/.config/skillshare/extras/instructions/`）に置き、`skillshare sync extras` を実行します。

| Agent | グローバルパス | `AGENTS.md` の読み方 |
|-------|-------------|-------------------|
| Codex CLI | `~/.codex/AGENTS.md` | 直接読み込む |
| opencode | `~/.config/opencode/AGENTS.md` | 直接読み込む |
| Claude Code | `~/.claude/AGENTS.md` | `CLAUDE.md` の import 経由 |
| Antigravity | `~/.gemini/AGENTS.md` | `GEMINI.md` の import 経由 |

2 つの Agent はユーザーレベルで固定のファイル名を読み込むため、それぞれ sync されたファイルの隣に 1 行だけのファイルが必要です。これらは一度書けば、skillshare が以降触れることはありません。

```markdown title="~/.claude/CLAUDE.md"
@AGENTS.md
```

```markdown title="~/.gemini/GEMINI.md"
@AGENTS.md
```

Claude Code は `AGENTS.md` ではなく `CLAUDE.md` を読み込みます。import は、他の Agent と 1 つのファイルを共有するための方法として、[memory に関するドキュメント](https://code.claude.com/docs/en/memory)が推奨しているアプローチです。Antigravity はグローバルな rules を `~/.gemini/GEMINI.md` に保持し、相対的な `@filename` を rules ファイル自体のディレクトリを基準に解決するため、同じ 1 行で sync された `AGENTS.md` が取り込まれます。`~/.gemini` の Target は、同じグローバルファイルを読み込む Antigravity CLI もカバーします。

Source ファイルの名前は `AGENTS.md` のままにしておいてください。`memory.md` のような中立的な名前でも sync は同様にできますが、読み込まれなくなります。Codex は `AGENTS.md` を名前で連結しており、import の構文を持たないため、その名前でしかファイルを認識しません。

Target はディレクトリであるため、各 Target はそれぞれの Source 名でファイルを受け取ります。余計なファイルが 4 つの Target すべてに配布されてしまわないよう、Source ディレクトリには配布したいファイルだけを置いてください。

:::note
このレシピは、あなたが書いた指示を共有するものであり、Agent 自身が書くメモリを共有するものではありません。Agent は自身の学習内容を、Claude Code ならディレクトリ内の Markdown、Codex ならデータベース、Cursor ならファイル以外のストレージといった独自の形式で保存しており、Target 間でファイルをコピーしても移植できるものではありません。
:::

---

## ディレクトリ構造

```
~/.config/skillshare/
├── config.yaml          # extras の設定はここにあります
├── skills/              # skill のソース
└── extras/              # extras のソースルート
    ├── rules/           # extras/rules/ のソースファイル
    │   ├── coding.md
    │   └── testing.md
    └── prompts/
        └── review.md
```

---

## 設定

`config.yaml` の場合:

```yaml
# 任意: グローバルなデフォルト extras source ディレクトリを設定
extras_source: ~/my-extras

extras:
  - name: rules
    source: ~/company-shared/rules    # extras ごとの任意の上書き
    targets:
      - path: ~/.claude/rules
      - path: ~/.cursor/rules
        mode: copy
  - name: agents
    targets:
      - path: ~/.claude/agents
        flatten: true                  # サブディレクトリのファイルをフラットに sync
  - name: prompts
    targets:
      - path: ~/.claude/prompts
```

### Source の解決優先順位

各 Extras の Source ディレクトリは、3 段階の優先順位で解決されます。

1. **Extras ごとの `source`**（最優先） — 正確なパスをそのまま使用
2. **`extras_source`** — `<extras_source>/<name>/`
3. **デフォルト** — `~/.config/skillshare/extras/<name>/`（グローバル）または `.skillshare/extras/<name>/`（Project）

`extras list --json` の出力には、どのレベルでパスが解決されたかを示す `source_type` フィールド（`per-extra`、`extras_source`、または `default`）が含まれます。

:::tip 自動設定
`extras_source` は、`skillshare init` を実行したとき、または `extras init` で最初の Extras を作成したときに、デフォルトパス（`~/.config/skillshare/extras/`）へ自動的に設定されます。後で変更するには `skillshare extras source <path>` を使用してください。
:::

---

## Sync

Extras は以下で sync されます。

```bash
skillshare sync extras        # extras のみを sync
skillshare sync --all         # skills + extras を一緒に sync
```

`--json`、`--dry-run`、`--force` オプションを含む sync の完全なドキュメントは [sync extras](/docs/reference/commands/sync#sync-extras) を参照してください。

---

## ワークフロー

```bash
# 1. 新しい extras を作成
skillshare extras init rules --target ~/.claude/rules --target ~/.cursor/rules

# 1b. またはカスタムの source ディレクトリを指定
skillshare extras init rules --target ~/.claude/rules --source ~/my-rules

# 1c. 既存の extras を再構成する（上書き）
skillshare extras init rules --target ~/.cursor/rules --force

# 2. source ディレクトリにファイルを追加する
# （解決済みの source ディレクトリを編集: skillshare extras list --json で確認）

# 3. target へ sync する
skillshare sync extras

# 4. ステータスを一覧表示する（source_type で各 extras の source の解決元がわかる）
skillshare extras list

# 5. target で編集したファイルを source に collect する
skillshare extras collect rules --from ~/.claude/rules

# 6. グローバルな extras source ディレクトリを変更する
skillshare extras source ~/company-shared/extras
```

---

## 関連項目

- [sync](/docs/reference/commands/sync#sync-extras) — Extras を Target へ sync
- [status](/docs/reference/commands/status) — Extras のファイル数と Target 数を表示
- [Configuration](/docs/reference/targets/configuration#extras) — Extras の設定リファレンス
