---
sidebar_position: 2
---

# backup

ターゲットディレクトリのバックアップを作成、一覧表示、管理します。

```bash
skillshare backup              # すべての Skill ターゲットをバックアップ
skillshare backup claude       # 特定のターゲットをバックアップ
skillshare backup agents       # すべての agent ターゲットをバックアップ
skillshare backup --all        # Skill と agent をバックアップ
skillshare backup --list       # すべてのバックアップを一覧表示
skillshare backup --cleanup    # 古いバックアップを削除
```

## こんなときに使う

- 危険な変更を行う前に手動でバックアップを作成する
- 既存のバックアップを一覧表示して復元の選択肢を確認する
- 古いバックアップをクリーンアップしてディスク容量を確保する

## 自動バックアップ

バックアップは、以下の前に **自動的に** 作成されます。
- `skillshare sync`（Skill ターゲットと agent ターゲット）
- `skillshare sync agents`（agent ターゲットのみ）
- `skillshare target remove`

保存場所: `~/.local/share/skillshare/backups/<timestamp>/`（グローバル）、`.skillshare/backups/`（プロジェクトモード、agent のみ）

保持ポリシーは、自動バックアップのたびに `--cleanup` と同じポリシーで自動的に適用されます。スナップショットを手動で整理する必要はありません。

## コマンド

### バックアップの作成

```bash
skillshare backup              # すべてのターゲット
skillshare backup claude       # 特定のターゲット
skillshare backup --dry-run    # プレビュー
```

### バックアップの一覧表示

```bash
skillshare backup --list
```

```
All backups (15.3 MB total)
  2026-01-20_15-30-00  claude, cursor     4.2 MB  ~/.local/share/.../2026-01-20_15-30-00
  2026-01-19_10-00-00  claude             2.1 MB  ~/.local/share/.../2026-01-19_10-00-00
  2026-01-18_09-00-00  claude, cursor     4.0 MB  ~/.local/share/.../2026-01-18_09-00-00
```

### 古いバックアップのクリーンアップ

```bash
skillshare backup --cleanup           # 古いバックアップを削除
skillshare backup --cleanup --dry-run # クリーンアップをプレビュー
```

デフォルトのクリーンアップポリシー:
- 直近 10 個のバックアップを保持
- 30 日以上前のバックアップを削除
- 合計サイズの上限を 500 MB に設定

最新のスナップショットは、それ単体でサイズ上限を超えていても常に保持されます — 復元ポイントがまったくない状態にはなりません。

このポリシーはすべての `sync` の後に自動的に実行されるため、`--cleanup` はオンデマンドで整理したいときにのみ必要です。

## オプション

| フラグ | 説明 |
|------|-------------|
| `--all` | Skill と agent の両方をバックアップ |
| `--project, -p` | プロジェクトモードを使用（`.skillshare/backups/`）。**agent のみ** |
| `--global, -g` | グローバルモードを使用（Skill のデフォルト） |
| `--list, -l` | すべてのバックアップを一覧表示 |
| `--cleanup, -c` | 古いバックアップを削除 |
| `--target, -t <name>` | 特定のバックアップを対象にする（位置引数の代替） |
| `--dry-run, -n` | 変更を加えずにプレビュー |

`backup` は位置引数として種類も受け付けます。`skillshare backup agents` は、バックアップを agent ターゲットのみに限定します。

## バックアップの構造

```
~/.local/share/skillshare/backups/
├── 2026-01-20_15-30-00/
│   ├── claude/
│   │   ├── skill-a/
│   │   └── skill-b/
│   └── cursor/
│       ├── skill-a/
│       └── skill-b/
└── 2026-01-19_10-00-00/
    └── claude/
        └── ...
```

存在する Skill ディレクトリは、ターゲットのモードによって異なります — [何がバックアップされるか](#what-gets-backed-up) を参照してください。

## 何がバックアップされるか {#what-gets-backed-up}

バックアップが保護するのは、`sync` が破壊し得るものだけです。すなわち **ターゲットには存在するがソースには存在しないローカルコンテンツ** です。

- ターゲット内の通常のファイルやディレクトリはバックアップされます
- merge モードのターゲットにあるシンボリックリンクは **スキップ** されます — これらはソース（唯一の信頼できる情報源）を指しており、すでに安全だからです。`skillshare sync` がこれらを再作成します

つまり:
- merge モードでは: ローカル（シンボリックリンクされていない）Skill のみがバックアップされます。sync 済みの Skill はソースに存在します
- copy モードでは: 管理下のすべての Skill ディレクトリがバックアップされます（実体ファイルであるため）
- symlink モードでは: 何もバックアップされません（ディレクトリ全体が単一のシンボリックリンクであるため）

ターゲットにシンボリックリンクしか含まれていない場合、バックアップは作成されず、`backup` は「何もすることがない」と報告します — 中身のない復元ポイントは意味がないからです。

## バックアップとディスク容量 {#backups--disk-space}

バックアップはソースをコピーしないため、サイズは小さく保たれます。混同しやすい 3 つの独立した仕組みがあります。

| 仕組み | 範囲 | 制御する対象 |
|-----------|-------|------------------|
| ソース内の `.gitignore` | Git のみ | Git が追跡する対象。無視されたファイルもディスク上には存在する |
| `config.yaml` の `ignore:` | `sync` | `sync` がターゲットにコピーするファイル（主に copy モード）。[sync](/docs/reference/commands/sync) を参照 |
| Backup | スナップショット | ローカルのターゲットコンテンツのみ — シンボリックリンク、したがってソースの成果物は除外される |

シンボリックリンクされた Skill は辿られないため、ソース Skill 内にある重いアーティファクト（モデルの重み、`.venv`、ブラウザプロファイル、メディアなど）は、`.gitignore` や `ignore:` に記載されているかどうかにかかわらず、スナップショットに **決して** コピーされません。

保持処理はすべての `sync` の後に、以下のデフォルトポリシーで自動的に実行されます。使用状況を手動で調べるには:

```bash
du -sh ~/.local/share/skillshare/backups   # ディスク上の合計サイズ
skillshare backup --list                   # スナップショットごとのサイズ
skillshare backup --cleanup --dry-run      # 保持ポリシーが何を削除するかプレビュー
```

Copy モードのターゲットは、スナップショットが依然として大きくなり得る唯一のケースです。これらは実体ファイルであるため、Skill ディレクトリ配下のあらゆるものがコピーされます。ランタイムキャッシュや大きなアーティファクトは Skill ツリーの外に置くか、`ignore:` で除外して、そもそもターゲットに届かないようにしてください。

## Agent のバックアップ {#agent-backup}

Agent には、Skill のバックアップと並行して動作する独自のバックアップフローがあり、知っておくべき 2 つの違いがあります。

**エントリの命名。** Agent のバックアップは、各タイムスタンプディレクトリ内の `<target>-agents/` に、Skill のバックアップと並んで保存されます。例えば、`skillshare backup --all` の後のレイアウトは次のようになります。

```
~/.local/share/skillshare/backups/2026-01-20_15-30-00/
├── claude/          # Skills backup for claude
├── claude-agents/   # Agents backup for claude
└── cursor/
```

**プロジェクトモードは Skill と逆になります。** プロジェクトモード（`-p`）では、`backup` は Skill ターゲットのバックアップを拒否しますが、agent ターゲットのバックアップは **行います**。`agents` フィルタを忘れると、次のエラーが表示されます。

```
backup is not supported in project mode (except for agents)
```

そのため、プロジェクトモードでは `skillshare backup -p agents` または `skillshare backup -p --all` のいずれかを指定する必要があります。

```bash
skillshare backup agents                  # すべての agent ターゲット（グローバル）
skillshare backup agents claude           # claude の agent のみ
skillshare backup agents -p               # プロジェクトの agent ターゲット
skillshare backup --all                   # 一度に Skill と agent の両方
```

agent のリソースモデルについては [Agents](/docs/understand/agents) を、復旧については [restore](/docs/reference/commands/restore) を参照してください。

## 関連項目

- [restore](/docs/reference/commands/restore) — バックアップから復元
- [sync](/docs/reference/commands/sync) — 自動的にバックアップを作成
- [target remove](/docs/reference/commands/target) — 自動的にバックアップを作成
