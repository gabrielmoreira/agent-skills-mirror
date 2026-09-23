---
sidebar_position: 3
---

# mcp

ポータブルな MCP 接続定義を管理し、ネイティブな Agent 設定を同期します。
まずは [Set up MCP once](/docs/how-to/daily-tasks/sharing-mcp) から始めてください。

## コマンド

```bash
skillshare mcp
skillshare mcp add
skillshare mcp edit
skillshare mcp edit docs --url https://updated.example/mcp --no-tui
skillshare mcp add docs --url https://example.com/mcp --target claude --sync
skillshare mcp add local --target codex -- company-mcp --workspace /path/to/workspace
skillshare mcp import docs --from claude --target claude --target cursor --sync
skillshare mcp import docs --file ./provider.json --target claude
skillshare mcp list --json
skillshare mcp remove docs --sync
skillshare mcp remove docs --keep-files
skillshare mcp restore BACKUP_ID --dry-run
skillshare sync mcp --dry-run --json
skillshare sync mcp
skillshare sync --all
```

| オプション | 意味 |
|---|---|
| `--target CLIENT` | 受け取り側クライアント。複数のクライアントを選択するには繰り返し指定。`--target none` はサーバーをどのクライアントにも書き込まずに Skillshare 内に保持する。[下記](#keep-a-server-without-syncing-it)を参照 |
| `--url URL` | `add` 用の Streamable HTTP エンドポイント |
| `-- command args...` | `add` 用のローカル実行ファイルとリテラルな引数 |
| `--disabled` | project mode で `add` と併用: Agent の global config が定義するサーバーをオフにする。[下記](#turn-off-a-global-server-in-one-project)を参照 |
| `--pi-extension PACKAGE` | target に Pi を含む場合は必須。`add`、`edit`、`import` と併用: `pi-mcp-adapter` または `pi-mcp-extension` のうち、Pi にインストールした方。[下記](#pi-choose-your-mcp-extension)を参照 |
| `--direct-tools VALUE` | `pi-mcp-adapter` を使う Pi で `add` または `edit` と併用: `true`、`false`、`search`、またはカンマ区切りのツール名。[下記](#pi-direct-tools)を参照 |
| `--pi-options JSON` | `pi-mcp-adapter` を使う Pi で `add` または `edit` と併用: その他の adapter フィールドを JSON オブジェクトで指定する。`{}` でクリアする。[下記](#pi-options)を参照 |
| `--from CLIENT` | インポート元の既存クライアント、または `--file` のフォーマット |
| `--file PATH` | ネイティブの JSON/JSONC、TOML、または Goose の YAML。`.toml` はデフォルトで Codex とみなされ、他のフォーマットはその MCP セクションから検出される。明示的な方言を指定するには `--from` を使う |
| `--sync` | 保存して同期する。非インタラクティブな add/import/remove ではそうしない限り保存のみ |
| `--keep-files` | `remove` と併用: サーバーの管理をやめ、Agent のエントリはそのまま残す。`--sync` とは併用できない。[下記](#stop-managing-a-server)を参照 |
| `--replace` | add/import 中に既存の source 定義を明示的に置き換える。import では、インポート元クライアントのエントリが異なる場合にそれも書き換える |
| `--dry-run`, `-n` | 保存もネイティブ設定への書き込みも行わずにプレビュー |
| `--json` | 構造化出力。sync/preview のレポートには name、path、action が含まれ、サーバーの値は含まれない |
| `--no-tui` | インタラクティブメニューを無効化。`tui: false`、`--json`、または非ターミナルの入出力でも無効になる |
| `--revision ID` | add/import/remove または `sync mcp` に一致するプレビューを要求する |
| `--global`, `-g` | global の Skillshare 設定を使う |
| `--project`, `-p` | project の Skillshare 設定を使う |

サブコマンドを指定しない場合、`mcp` はインタラクティブなターミナルで検索可能なマネージャーを開くか、非インタラクティブモードではステータスを表示します。名前を指定しない非インタラクティブなインポートは、解析済みの候補を選択のために一覧表示し、保存は行いません。候補にはポータブルな定義が含まれ、認識可能な secret は参照に変換されます。Agent 固有のフィールドは警告として一覧表示され除外されます。無効化されたサーバーと非対応のトランスポートは候補をブロックします。`restore` は適用前に必ず再度プレビューします。適用せずに確認するには `--dry-run` を使ってください。

`sync mcp` は scope フラグ、`--dry-run`、`--json`、`--no-tui`、`--revision` を受け付けます。
`sync --all` には skills、agents、extras、MCP が含まれます。単なる `sync` は既存のリソースの動作を維持します。MCP の競合は、`--all` が他のリソースを変更する前にチェックされます。リソース種別とネイティブファイルは、単一のトランザクションではなく別々の操作です。

## インタラクティブ管理

`skillshare mcp` または `skillshare mcp list` を実行します。Skill 一覧と同様に、マネージャーは検索用の `/` と詳細表示用の `Enter` に対応しています。接続一覧では、引数・ヘッダー・環境変数の値は非表示になり、URL のクエリも省略されます。

| キー | 動作 |
|---|---|
| `a` | 接続を追加 |
| `i` | 1 つ以上の接続をインポート |
| `e` | 選択した接続を編集 |
| `x` | 選択した接続を削除 |
| `s` | 同期をプレビューして確認 |
| `b` | クライアント別にバックアップを閲覧し、新しい順に表示 |
| `r` | ステータスを更新 |
| `q` | 終了 |

`mcp edit`、`mcp remove`、`mcp restore` は、name またはバックアップ ID が省略された場合に選択メニューを提供します。エディタは command/URL、引数、環境変数、HTTP ヘッダー、bearer-token の環境変数参照、受け取り側の target をカバーします。引数は 1 行につき 1 つのリテラル引数、または JSON 配列で受け付けます。トランスポートを切り替えると、新しい接続タイプに適用されないフィールドはクリアされます。

Add、edit、remove、import では、**Save and sync** または **Save only** の前にプレビューが表示されます。Remove には **Stop managing** もあり、`--keep-files` と同じ動作です。Escape で保留中のドラフトをキャンセルできます。Restore は Agent のエントリへの変更をプレビューし確認しますが、source 定義自体は書き換えません。

サーバー名を指定しないインポートは複数選択に対応しています（`Space` でトグル、`a` ですべて選択）。無効な候補はスキップされます。既存の source 名は `--replace` を指定しない限りスキップされます。バッチに対しては、互換性のある受け取り側クライアントを 1 セット選択してください。バッチ全体が検証された後、source は一度だけ保存されます。その後のネイティブファイル I/O 失敗については、既存の復旧動作が維持されます。

スクリプトからは、name とフラグを指定します。`mcp edit NAME --url URL`、`mcp edit NAME --target CLIENT`、`mcp edit NAME -- command args...` は、他の該当する設定を保持したまま指定されたフィールドを更新します。`--sync` を追加しない限り保存のみを行います。`--no-tui` の場合、remove には name が、restore にはバックアップ ID が必要です。`--dry-run` は変更を保存も同期も行いません。

## Source フィールド

インラインの `mcp.servers`、または `sources.mcp` で指定した外部ファイルのいずれかを選べます。外部ファイルにはトップレベルの `servers` マッピングが必要です。`mcp.targets` と [`mcp.projects`](#manage-several-projects-from-the-global-config) は Skillshare の config に残ります。スキーマはリポジトリ内の `schemas/mcp.schema.json` です。

| サーバーフィールド | 意味 |
|---|---|
| `command` | ローカル実行ファイル。`url` とは併用不可 |
| `args` | ローカル実行ファイルのリテラルな引数のリスト |
| `env` | ローカルの環境変数値: 文字列または `{fromEnv: VARIABLE}` |
| `url` | HTTP(S) の MCP エンドポイント。埋め込みの認証情報やフラグメントは不可 |
| `headers` | HTTP ヘッダー: 文字列または `{fromEnv: VARIABLE}` |
| `bearerToken` | `{fromEnv: VARIABLE}`。Authorization ヘッダーと共存不可 |
| `transport` | 任意の `stdio` または `streamable-http`。省略時は推測される |
| `targets` | 任意の受け取り側クライアント。`mcp.targets` を上書きする。空のリストにすると、サーバーは Skillshare 内にのみ保持される。[下記](#keep-a-server-without-syncing-it)を参照 |
| `directTools` | `pi-mcp-adapter` を使う Pi 限定: `true`、`false`、`"search"`、またはツール名のリスト。[下記](#pi-direct-tools)を参照 |
| `piOptions` | `pi-mcp-adapter` を使う Pi 限定: その他の adapter フィールド。Pi のエントリにそのまま書き込まれる。[下記](#pi-options)を参照 |
| `disabled` | `true` のみ、他の接続フィールドを伴わない、かつ project がスコープ内にあること: project mode、または `mcp.projects` 配下の root。[下記](#turn-off-a-global-server-in-one-project)を参照 |

クライアント ID は `claude`、`codex`、`cursor`、`vscode`、`opencode`、`kilocode`、
`grok`、`antigravity`、`amp`、`claude-desktop`、`cline`、`copilot`、`factory`、`gemini`、
`goose`、`junie`、`kiro`、`lmstudio`、`warp`、`windsurf`、`pi` です。
`grok` は公式の xAI Grok CLI を意味します。サーバー名には文字、
数字、ドット、アンダースコア、ハイフンを使用します。サーバーは同期前に、直接または
`mcp.targets` 経由で少なくとも 1 つのクライアントを選択する必要があります。ただし、サーバー自身の
`targets` が空のリストである場合は除きます。

### 同期せずにサーバーを保持する {#keep-a-server-without-syncing-it}

`targets: []` を持つサーバーは Skillshare の source に残り、どのクライアントにも書き込まれません。
定義を後のために残したまま、サーバーをすべてのクライアントから外したいときに使います。
以前に同期されていた場合、次の sync でそれらのクライアントからエントリが削除されます。

```yaml
mcp:
  targets: [claude, codex]
  servers:
    docs:
      url: https://example.com/mcp
      targets: []
```

```bash
skillshare mcp add docs --url https://example.com/mcp --target none
skillshare mcp edit docs --target none
skillshare mcp edit docs --target claude   # 元に戻す
```

- **`targets` を省略するのとは異なります。** その場合、サーバーは `mcp.targets` を継承し、
  そのリストも空であれば拒否されます。
- `none` はクライアントと組み合わせられません。
- ターミナルの選択メニューでは、クライアントを何も選択せずに確定します。ダッシュボードでは、
  すべてのクライアントのチェックを外します。サーバーには **Agent 未選択** のタグが付きます。
- project のサーバーでも、`mcp.projects` 配下のサーバーでも同じように動作します。
- `disabled` エントリには引き続き少なくとも 1 つのクライアントが必要です。どこかでサーバーを
  オフにする必要があるためです。
- `mcp list` では、このようなサーバーは `kept no targets` と表示されます。

Grok の場合、名前は文字またはアンダースコアで始まり、文字、数字、ハイフン、単一のアンダースコアのみを含み、アンダースコアで終わってはいけません。
`company-docs` のような名前は、すべての対応クライアントで動作します。

## ネイティブな送信先 {#native-destinations}

| クライアント | Global | Project | セクション |
|---|---|---|---|
| Claude Code | `~/.claude.json` | `.mcp.json` | `mcpServers` |
| Codex | `~/.codex/config.toml` | `.codex/config.toml` | `mcp_servers` |
| Cursor | `~/.cursor/mcp.json` | `.cursor/mcp.json` | `mcpServers` |
| VS Code | User `mcp.json`（下記） | `.vscode/mcp.json` | `servers` |
| OpenCode | `~/.config/opencode/opencode.json` | `opencode.json` | `mcp` |
| Kilo Code | `~/.config/kilo/kilo.jsonc` | `kilo.jsonc` | `mcp` |
| Grok CLI | `~/.grok/config.toml` | `.grok/config.toml` | `mcp_servers` |
| Antigravity (AGY) | `~/.gemini/config/mcp_config.json` | `.agents/mcp_config.json` | `mcpServers` |
| [Amp](https://ampcode.com/docs/customize/mcp) | `~/.config/amp/settings.json` | `.amp/settings.json` | `amp.mcpServers`（リテラルキー） |
| [Claude Desktop](https://modelcontextprotocol.io/docs/develop/connect-local-servers) | Claude のアプリケーションデータディレクトリ、`claude_desktop_config.json` | Global のみ | `mcpServers` |
| [Cline](https://github.com/cline/cline/tree/main/apps/vscode/src/services/mcp) | `~/.cline/data/settings/cline_mcp_settings.json` | Global のみ | `mcpServers` |
| [Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-mcp-servers) | `~/.copilot/mcp-config.json` | `.github/mcp.json` | `mcpServers` |
| [Factory Droid](https://docs.factory.ai/harness/mcp) | `~/.factory/mcp.json` | `.factory/mcp.json` | `mcpServers` |
| [Gemini CLI](https://geminicli.com/docs/tools/mcp-server/) | `~/.gemini/settings.json` | `.gemini/settings.json` | `mcpServers` |
| [Goose](https://block.github.io/goose/docs/guides/config-files/) | `~/.config/goose/config.yaml` | Global のみ | `extensions`（YAML） |
| [Junie](https://junie.jetbrains.com/docs/junie-cli-mcp-configuration.html) | `~/.junie/mcp/mcp.json` | `.junie/mcp/mcp.json` | `mcpServers` |
| [Kiro](https://kiro.dev/docs/mcp/configuration/) | `~/.kiro/settings/mcp.json` | `.kiro/settings/mcp.json` | `mcpServers` |
| [LM Studio](https://lmstudio.ai/docs/app/mcp) | `~/.lmstudio/mcp.json` | Global のみ | `mcpServers` |
| [Warp](https://docs.warp.dev/agents/capabilities/mcp/) | `~/.warp/.mcp.json` | `.warp/.mcp.json` | `mcpServers` |
| [Windsurf (Cascade)](https://docs.devin.ai/desktop/cascade/mcp) | `~/.codeium/windsurf/mcp_config.json` | Global のみ | `mcpServers` |

ダッシュボードのサーバーフォームは、HTTP ヘッダーを環境変数と同じ方法で編集し、`fromEnv` 参照にも対応します。サーバーのメニューとフォーム内のファイル数の横にある **View what each Agent gets** は、選択したクライアントに対して Sync が書き込む予定のネイティブテキストを読み取り専用で表示します。フォーム内では、まだ保存されていない編集内容が反映されます。secret は参照のままです。

JSON エントリは、そのファイル自体のインデントに合わせて 1 行に 1 フィールドで書き込まれます。Skillshare が所有しているにもかかわらず 1 行にまとまっているエントリは `update` として報告され、改めてレイアウトされて書き込まれます。Skillshare が所有していないエントリや、手動でフォーマットされたエントリは、そのレイアウトを保持します。

ダッシュボードは、現在の scope とホストのプラットフォームで利用可能な送信先のみを提供します。各サーバーは 1 行として表示され、右側のカウントボタンからそのサーバーの全クライアント一覧を開けます。Global 専用のクライアントは project mode では選択できません。
右側の **Sync** ボックスには、まだ書き込まれていない変更が一覧表示されます。クライアントにチェックを入れるだけでは source のみが編集されます。**Sync MCP** はそれらの変更を一覧表示し、確認後に MCP の設定ファイルだけを書き込み、それぞれのバックアップを保存します。その下の **Agents** には、このマシン上で検出されたクライアントが一覧表示されます。クライアントの MCP ファイルが存在するか、そのクライアントが設定を保存するフォルダが存在すれば「検出済み」と見なされるため、MCP ファイルがまだない新規インストールでも表示されます。project mode では、project が MCP ファイルを持っているか、そのクライアントが global で検出されている場合に一覧表示されます。

追加のクライアント詳細:

- `codex` の送信先は、Codex CLI、Codex IDE 拡張機能、ChatGPT デスクトップアプリが共有する 1 つの `config.toml` です。そのため、`codex` に同期したサーバーはこの 3 つすべてに表示されます。ChatGPT デスクトップアプリでは **Settings → MCP servers** の下に表示されます。
  Codex は、trust している project でのみ `.codex/config.toml` を読み込みます。trust していない project では、同期されたサーバーはエラーなく読み込まれません。`cwd`、
  `http_headers_helper`、ツール一覧と承認モード、タイムアウト、`oauth` テーブルにはポータブルな形式がありません。インポートではこれらを警告付きで除外し、sync は既存のエントリ内にそれらを維持します。Codex の plugin が同梱する MCP サーバーは `plugins.<plugin>.mcp_servers` の下に設定され、ここでは管理されません。
- Claude Desktop のファイル sync は macOS と Windows で **stdio のみ**に対応します。
  ディレクトリは macOS では `~/Library/Application Support/Claude`、
  Windows では `%APPDATA%/Claude` です。リモートコネクタはアプリケーション内で設定してください。
- Cline はデフォルトの VS Code Stable プロファイルを対象とし、Cline CLI や他の IDE は対象外です。
- Copilot CLI は新規エントリに対して `tools: ["*"]` をエクスポートし、既存のツールフィルタは保持します。project の `.mcp.json` が存在する場合、Copilot はその ファイルを `.github/mcp.json` より先に読み込むため sync は停止します。先にファイルを統合してください。
  project mode で Claude Code と Copilot CLI を同時に選択することも、いずれかのファイルを書き込む前にブロックされます。これらのクライアントの一方には global mode を使ってください。
- Gemini は Streamable HTTP に `httpUrl` を使用します。その `url` フィールドはレガシーな SSE を意味し、インポート時に拒否されます。Cline は `type: streamableHttp` を、Goose は
  `type: streamable_http` と `uri` を使用します。Skillshare はこれらを自動的に変換します。
- Goose は Windows で `%APPDATA%/Block/goose/config/config.yaml` を使用します。YAML の編集は
  関連のない設定、コメント、組み込みの extension を保持しますが、フォーマットが変わる場合があります。Alias、merge、重複キー、複数ドキュメントは編集をブロックします。
  組み込みの extension とキーチェーンの `env_keys` は、ポータブルな MCP 接続としてインポートできません。
- Claude Code は、組み込みサーバー用に予約されている `workspace`、`claude-in-chrome`、`computer-use` という名前のサーバーをスキップします。また、リモートサーバーに自身の認証情報を送ることは決してありません。`ANTHROPIC_API_KEY`、`ANTHROPIC_AUTH_TOKEN`、`AWS_BEARER_TOKEN_BEDROCK`、
  `HTTPS_PROXY`、`NPM_TOKEN` は `url` と `headers` では空として読み込まれます。Skillshare は Claude に対してその両方を拒否します。認証情報は自分で名前を付けた変数にコピーしてください。
- Claude Code にはローカルスコープもあります。`--scope` を指定せずに `claude mcp add` で追加したサーバーは、project ごとに `~/.claude.json` に保存されます。ローカルサーバーは、
  `.mcp.json` や user scope にある同名のものより丸ごと優先されます。project mode では、Skillshare はそのようなサーバーを、隠しているエントリの隣に、sync をブロックすることなく報告します。project フォルダから `claude mcp remove NAME -s local` で削除してください。
- Cline の VS Code 拡張機能、CLI、SDK は `~/.cline/data/settings/` を共有します。拡張機能は
  古い VS Code の `globalStorage` ファイルを一度だけそこに移行し、以降はそれを読まなくなります。そのため Skillshare は `~/.cline/data` がまだ存在しない場合のみ古いファイルに書き込みます。`CLINE_MCP_SETTINGS_PATH`、`CLINE_DATA_DIR`、`CLINE_DIR` はこの順序で尊重されます。
- Windsurf のサポートは、ドキュメント化された Cascade 設定を対象としています。Windsurf の新しい
  Devin Local agent は独自の `~/.config/devin/mcp_config.json` を読み込みますが、Skillshare はこれを管理しません。Warp の project 接続は、セッションごとに Warp 内での承認が引き続き必要です。
- Amp は、`amp mcp approve <name>` を実行した後にのみ、project の `.amp/settings.json` からサーバーを実行します。Global のサーバーには承認は不要です。
- Kiro は、その「Mcp Approved Env Vars」設定に一覧されている名前についてのみ `${VARIABLE}` を展開し、localhost に限り `http://` URL を受け付けます。
- VS Code は、デフォルト以外の各プロファイルについて `User/profiles/` 以下に別々の `mcp.json` を保持します。Skillshare はデフォルトプロファイルのファイルを管理します。

環境変数参照は、Amp、Copilot CLI、Factory、Gemini CLI、Kiro については `${VARIABLE}` として、Cline と Windsurf については `${env:VARIABLE}` としてエクスポートされます。
Claude Desktop、Goose、Junie、LM Studio、Warp は、そのネイティブな変数展開が検証されていないため、現時点では `fromEnv` と
`bearerToken` のエクスポートを拒否します。カスタム認証情報を使わない接続を利用するか、対応している受け取り側クライアントで認証してください。Skillshare は参照を平文に解決することは決してありません。

Antigravity は現在の[公式 MCP 設定](https://antigravity.google/docs/mcp)を使用し、
リモート接続には `serverUrl` を含みます。Skillshare はポータブルな `url` を自動的に
変換します。古い `.gemini/antigravity/` と `.gemini/antigravity-cli/` の設定
場所は管理対象外です。Antigravity の `fromEnv` と `bearerToken` のエクスポートは、そのドキュメント化された設定が環境変数の展開を規定していないためブロックされます。カスタムの secret ヘッダーを必要としない接続を使用し、
Antigravity 内で対応している OAuth ログインを完了してください。Skillshare は参照を平文の認証情報に展開することは決してありません。

OpenCode は、global ディレクトリについて `XDG_CONFIG_HOME` を尊重します。既存の
`opencode.jsonc` は `opencode.json` を作成する代わりに使用されます。project では、OpenCode は `.opencode/` からも両方の名前を読み込みます。そのため、そこに置かれたファイルがあれば Skillshare はそのファイルに書き込み、新しいファイルは project ルートに作成されます。複数存在する場合は、sync する前に統合してください。カスタムの OpenCode config パス、ディレクトリオーバーライド、インラインの config、継承された祖先ファイルは管理対象外です。これらは OpenCode 内で選択した送信先を上書きすることがあります。

Kilo Code は OpenCode と同じフォーマットを使用します。project ルートと `.kilo/` から `kilo.jsonc` と `kilo.json` を読み込み、
それらをマージします。そのため Skillshare は既に存在する方に書き込み、どちらも存在しない場合にのみ `kilo.jsonc` を作成します。
両方が存在する場合は、sync する前に統合してください。`KILO_CONFIG`、
`KILO_CONFIG_DIR`、および古い VS Code 拡張機能の `mcp_settings.json` は管理対象外です。

Kilo Code は project の config を信頼されていないものとして扱います。そこでの `{env:VARIABLE}`
参照は許可されず、project ファイルが見つかった場合はそのファイル全体を無視します。そのため project
mode では、Skillshare は `fromEnv` または `bearerToken` を使う Kilo Code サーバーを拒否します。そのようなサーバーは、参照が許可される global mode で定義してください。

OpenCode と Kilo Code は `local`/`remote` タイプと `{env:VARIABLE}` 参照を使用し、Grok は
`${VARIABLE}` 参照を使用します。Skillshare はこれらを自動的に変換します。Claude の
`"type": "streamable-http"` は HTTP としてインポートされます。無効化された接続はインポートをブロックします。
Codex の `startup_timeout_sec` や `envFile` のような、ポータブルな対応形式がないその他のネイティブオプションは、
警告付きでインポートから除外されます。sync はそれらを Agent の既存エントリ内に維持します。Pi は明示的に
選択されたサードパーティ拡張機能を通じてサポートされます。下記を参照してください。

VS Code Stable のデフォルトのユーザーファイルは以下のとおりです。

- macOS: `~/Library/Application Support/Code/User/mcp.json`
- Linux: `${XDG_CONFIG_HOME:-~/.config}/Code/User/mcp.json`
- Windows: `%APPDATA%/Code/User/mcp.json`

Global の Claude、Codex、Grok、Copilot のパスは、`CLAUDE_CONFIG_DIR`、`CODEX_HOME`、
`GROK_HOME`、`COPILOT_HOME` を尊重します。`OPENCODE_CONFIG` と `OPENCODE_CONFIG_DIR` は管理対象外です。Amp と Goose は、`.config` パスを使うプラットフォームでは `XDG_CONFIG_HOME` を尊重します。
project の送信先は、選択された project ルートからの相対パスです。project の trust、
サーバーの承認、認証は引き続き受け取り側 Agent の責任です。

### Agent の別のアカウント {#accounts}

[Agent の別のアカウント](/docs/reference/targets/configuration#agent-config-dir)として宣言された Target は、`claude`（`CLAUDE_CONFIG_DIR`）、`codex`（`CODEX_HOME`）、`pi`（`PI_CODING_AGENT_DIR`）については MCP の Target でもあります。そのサーバーは、その Agent のフォーマットで、アカウント自身のファイル（Claude は `<config_dir>/.claude.json`、Codex は `<config_dir>/config.toml`、Pi は `<config_dir>/mcp.json`）に書き込まれます。

```yaml
targets:
  claude-work:
    agent: claude
    config_dir: ~/.claude-work

mcp:
  targets: [claude, claude-work]      # 両方のアカウントがすべてのサーバーを受け取る
  servers:
    docs:
      url: https://example.com/mcp
    jira:
      command: jira-mcp
      targets: [claude-work]          # 仕事用アカウントのみ
```

この例では、`docs` は `~/.claude.json` と `~/.claude-work/.claude.json` に、`jira` は 2 つ目のファイルにのみ書き込まれます。`--target claude-work` は `mcp add` と `mcp edit` で使え、ダッシュボードではそのアカウントが Agent と並んで一覧表示されます。

`pi-mcp-extension` は常に `~/.pi/agent/mcp.json` を読み込むため、Pi のアカウントには `piExtension: pi-mcp-adapter` が必要です。

どのアカウントも同じ project ファイルを読み込むため、`mcp.projects` 内と project mode では Agent 自身の名前を使ってください。Claude Code は project のオフリストを各アカウントのファイルに保持します。[project でサーバーをオフにする](#turn-off-a-global-server-in-one-project)と、そのサーバーを持つすべてのアカウントにスイッチが書き込まれます。`mcp import --from claude-work` とダッシュボードの Import from target は、そのアカウント自身のファイルを読み込みます。`mcp import --file <path> --from claude-work` は、自分でエクスポートしたファイルを、そのアカウントの Agent のフォーマットとして読み込みます。

## 1 つの project だけで global サーバーをオフにする {#turn-off-a-global-server-in-one-project}

Agent は自身の global MCP ファイルと project のファイルを合わせて読み込みます。そのため、global
ファイルで定義されたサーバーはすべての project で読み込まれます。1 つの project だけでそれを読み込まれないようにするには、**Agent の global ファイルが使っているのと同じ名前**のエントリを追加し、
`disabled` を指定します。

これは以下の 4 つのクライアントでのみ機能します。

| クライアント | 対応 | Skillshare が書き込む内容 |
|---|---|---|
| Claude Code | Yes | `~/.claude.json`: この project の `disabledMcpServers` リストにその名前を追加 |
| OpenCode | Yes | `opencode.json`: `"NAME": {"enabled": false}` |
| Kilo Code | Yes | `kilo.jsonc`: `"NAME": {"enabled": false}` |
| `pi-mcp-adapter` を使う Pi | Yes | `.pi/mcp.json`: `"NAME": {"disabled": true}` |
| `pi-mcp-extension` を使う Pi | No | disable 用のフィールドがない |
| Codex | No | 下記参照 |
| その他すべてのクライアント | No | 選択するとエラー。何も書き込まれない |

書き込まれるのはスイッチのみです。Agent は global エントリのコマンドまたは URL をそのまま保持します。他のクライアントが拒否されるのは、global エントリ全体を project 側のものに置き換えてしまうか、project ファイルを持たないため、スイッチだけを書き込むとオフにするどころかサーバーを壊してしまうからです。

Codex が拒否されるのは別の理由によります。Codex は `.codex/config.toml` を global ファイルの上にフィールド単位でマージするため、
global config がそのサーバーを定義しているマシンでは `enabled = false` 単体でも機能します。しかしそれを定義していないマシンでは、マージされたエントリに
`command` も `url` もなくなり、Codex は `invalid transport` で設定全体の読み込みに失敗します。`.codex/config.toml` は通常コミットされるため、あるチームメンバーのスイッチが
別のメンバーの Codex の起動を止めてしまう可能性があります。代わりに、マシンごとに `~/.codex/config.toml` で
`enabled = false` を指定してサーバーをオフにしてください。

### OpenCode と Kilo Code

```bash
cd my-project
skillshare mcp add company-docs --disabled --target opencode --target kilocode
skillshare sync mcp
```

```yaml
# .skillshare/config.yaml
mcp:
  servers:
    company-docs:
      disabled: true
      targets: [opencode, kilocode]
```

### Claude Code

Claude Code は 1 つのスコープからサーバーエントリ全体を取得し、フィールドをマージすることは決してないため、`.mcp.json` 内のスイッチはサーバーをオフにするのではなく置き換えてしまいます。Claude Code は
`/mcp` パネルが編集するのと同じ、project ごとの独自のオフリストを `~/.claude.json` に保持しています。
Skillshare はこの project の絶対パスの下にその名前を追加し、`.mcp.json` には何も書き込みません。

```bash
skillshare mcp add company-docs --disabled --target claude
skillshare sync mcp
```

- このリストはリポジトリではなく自分のマシン上に存在します。各チームメンバーは自分のチェックアウトで一度
  `skillshare sync mcp` を実行してください。
- `/mcp` 内で自分でオフにした名前は、決して奪われたり削除されたりしません。
- `/mcp` でサーバーを再度オンにすると、次の sync は競合を報告します。
  `.skillshare/config.yaml` からそのエントリを削除するか、再度オフにするために replace してください。
- このリストは project のパスをキーにしているため、project を移動すると新しい sync が必要になります。

### Pi

Pi には、すべての Pi エントリと同様に `piExtension` が必要であり、それは `pi-mcp-adapter` でなければなりません。
OpenCode と Kilo Code はそのフィールドを無視するため、1 つのエントリで 3 つすべてをカバーできます。

```bash
skillshare mcp add company-docs --disabled --target pi --pi-extension pi-mcp-adapter
```

```yaml
mcp:
  servers:
    company-docs:
      disabled: true
      piExtension: pi-mcp-adapter
      targets: [opencode, pi]
```

### ルール

- **project がスコープ内にある必要があります。** `.skillshare/config.yaml` を持つ project 内で実行するか
  （`skillshare init -p` で作成）、`-p` を渡すか、
  [`mcp.projects`](#manage-several-projects-from-the-global-config) 内の project root の下にエントリを
  置いてください。project がスコープ内にない global の `mcp.servers` では拒否されます。
- **`disabled` は単独で指定します。** このエントリが取れるのは `targets` と、Pi の場合は
  `piExtension` のみです。`command`、`url`、`env`、`headers` を追加するとエラーになります。
- **`targets` は省略できます。** その場合、エントリは project の target に従います。sync のたびに、
  project が使うクライアントのうち、project ごとのスイッチを持つものに書き込まれます。Skillshare が同名の
  global サーバーも把握している `mcp.projects` 配下では、そのサーバーの書き込み先クライアントにさらに
  絞り込まれ、Pi は global サーバーの `piExtension` を引き継ぎます。後から project の target を変更しても、
  エントリの編集は不要です。自分で決めたい場合は `targets` を列挙してください。そのリスト内の
  非対応クライアントはエラーになります。
- **名前は一致している必要があります。** Skillshare は Agent の global ファイルを読み込まないため、
  この名前のサーバーがそこに存在するかを確認できません。何にも一致しない名前は無害です。Agent はそれを無視します。
- **再びオンにするには**、エントリを削除し（`skillshare mcp remove company-docs`）
  sync してください。スイッチは、それが書き込まれたファイル（project 自身のファイル、または
  Claude Code の場合は `~/.claude.json`）から削除されます。
- **Skillshare 自身が定義したサーバーにはこれは不要です。** 代わりにそのサーバーで Agent の選択を外せば、
  次の sync でそのエントリが削除されます。

ダッシュボードでは、**サーバーを追加** の横にある **グローバルサーバーをオフにする** ボタンがこれに当たります。project mode と、project の MCP タブに表示されます。

## global config から複数の project を管理する {#manage-several-projects-from-the-global-config}

project mode では、各 project の MCP 設定をその project の `.skillshare/config.yaml` に保持し、
そのフォルダー内から sync します。すべての project を 1 か所で管理したい場合は、**global** config の
`mcp.projects` の下に project フォルダーを列挙してください。そうすれば、どこからでも `skillshare sync mcp` を
1 回実行するだけで、global のファイルとすべての project のファイルが 1 つのプランでまとめて書き込まれます。

```yaml
# ~/.config/skillshare/config.yaml
mcp:
  servers:
    context7:
      command: npx
      args: ["-y", "@upstash/context7-mcp"]
      targets: [opencode, pi]
      piExtension: pi-mcp-adapter
  projects:
    ~/work/project01:
      targets: [opencode, pi]
      servers:
        context7:                  # この project だけでオフ
          disabled: true
          piExtension: pi-mcp-adapter
    ~/work/project02:
      servers:
        internal-docs:             # この project にだけ存在する
          url: https://example.com/mcp
          targets: [opencode]
```

project には、global config と異なる部分だけを書きます。`context7` のような global サーバーは、ここに
エントリを書く必要がありません。Agent は自身の global ファイルと project のファイルを合わせて読み込むため、
すでにすべての project で読み込まれます。`disabled` エントリは、そこに列挙したすべての
クライアントについて、[そのフォルダーでそのサーバーをオフにします](#turn-off-a-global-server-in-one-project)。

各キーは project フォルダーで、絶対パスか `~` で始まるパスを指定します。その下には、その project 自身の
`config.yaml` が `mcp` の下に持つのと同じ `targets` と `servers` を書き、それらは同じ
[project ファイル](#native-destinations)に書き込まれます。`targets` を持たない project は、global の
`mcp.targets` を継承し、`directTools` を持たない project は global の
[`mcp.directTools`](#pi-direct-tools) を継承します。

1 つのサーバーが複数の場所に現れる場合、プレビューにはファイル名が表示されます。

```text
context7     add          opencode (~/.config/opencode/opencode.json)
context7     add          opencode (~/work/project01/opencode.json)
```

リストから project を削除すると、サーバーを削除した場合と同様に、Skillshare がそこに書き込んだエントリが
次の sync で削除されます。

複数の project に同じサーバーを持たせるには、YAML アンカーで一度だけ定義して再利用します。

```yaml
mcp:
  projects:
    ~/work/project01:
      servers:
        internal-docs: &internal-docs
          url: https://example.com/mcp
          targets: [opencode]
    ~/work/project02:
      servers:
        internal-docs: *internal-docs
```

アンカーは `mcp.projects` の中に置いてください。`mcp.servers` 上のアンカーへのエイリアスも機能しますが、
`skillshare mcp add` とダッシュボードは `mcp.servers` を書き換えます。保存時には、ファイルが有効なままになるよう
そうしたエイリアスを完全な形に展開して書き出すため、それ以降は global サーバーへの編集に追従しなくなります。

### ダッシュボードでの project {#projects-in-the-dashboard}

global mode では、ダッシュボードに **プロジェクト** ページがあります。[`projects`](/docs/reference/targets/configuration#projects) と
`mcp.projects` の下にあるすべてのフォルダーが一覧され、各 project には **MCP** タブがあります。

- **プロジェクトを追加** では、フォルダーとその target を指定します。**MCP** にチェックを入れると、そのフォルダーは
  `mcp.projects` にも一覧されます。
- **MCP** タブには、すべての global サーバーがスイッチ付きで一覧表示されます。オフにすると、`targets` を
  持たない `disabled` エントリが保存されるため、[上記](#turn-off-a-global-server-in-one-project)のとおり
  project の target に従います。オンに戻すとそのエントリは削除されます。
  その下には、その project にのみ存在するサーバーが並びます。
- オフになっているサーバーには、オフになっている Agent のロゴが表示されます。project の Agent の中に
  project ごとのスイッチを持たないものがある場合、その行にはサーバーがそこでは引き続き読み込まれることが
  表示されます。project のものとは異なる独自の `targets` を持つエントリには **プロジェクトに合わせる** が
  表示され、`targets` なしでそのエントリを保存し直します。
- タブの Sync ボックスにある **Sync MCP** は MCP の計画全体を書き込み、そのうち何件の変更がこの project の外に
  あるかを表示します。project ページの上部にある **Sync project** は、この project の skills、agents、MCP だけを
  書き込みます。
- MCP ページの一番下にある **デフォルト** では、`mcp.targets` と `mcp.directTools` を編集します。
- project 自身の Agent ファイルに Skillshare が管理していないサーバーがある場合、タブの一覧の上にそのことが
  **Import** 付きで表示されます。[下記](#unmanaged-servers)を参照してください。

保存時に書き換えられるのは、変更した project だけです。他の project は、アンカーやエイリアスも含めて
YAML が書かれたまま保持され、`~/work/app` と書かれたフォルダーは `~` のまま残ります。このページの他の箇所と同様に、
保存で変更されるのは `config.yaml` だけで、ファイルを書き込むのは Sync です。

制限事項:

- `mcp.projects` は global config からのみ読み込まれます。これを含む project config は拒否されます。
- これを編集するコマンドはありません。`skillshare mcp add` は `mcp.servers` を管理し、
  `mcp.projects` は書かれたままにします。編集は `config.yaml`、または
  [ダッシュボード](#projects-in-the-dashboard)で行ってください。
- Claude Code 向けの `disabled` エントリは、global サーバーが書き込まれるのと同じファイルである
  `~/.claude.json` に書き込まれます。Claude Code は project ごとのオフリストをそこに保持しているためです。
  サーバー自体はそのままにされます。
- フォルダーが同じエントリを管理する独自の `.skillshare/config.yaml` も持っている場合、プランは上書きせずに
  競合を報告します。

## サーバーの管理をやめる {#stop-managing-a-server}

```bash
skillshare mcp remove docs --keep-files
```

これは source から `docs` を削除し、Skillshare がそのために書き込んだ Agent のエントリの記録を消去します。
Agent ファイルは変更されません。以降、それらのエントリはあなたのものになり、sync は削除も更新もしません。
`--keep-files` は `--sync` と併用できません。ターミナルの削除ウィザードでは **Stop managing** として表示され、
ダッシュボードの削除ダイアログでも、MCP ページと project の **MCP** タブの両方で同じ選択肢が表示されます。

変更されるのは削除したスコープだけです。global サーバーの管理をやめても、同じ名前の project のサーバーは
管理されたままで、その逆も同様です。エントリを再び管理するには、それをインポートしてください。

## Skillshare が管理していないサーバー {#unmanaged-servers}

ダッシュボードは、現在のスコープと `mcp.projects` の下にあるすべてのフォルダーの Agent 設定ファイルを読み、
この source が定義しておらず、どの Skillshare 設定も管理していないサーバーを探します。見つかった場合は、
サーバー一覧の上に、その件数とどの Agent にあるかが表示されます。**Import** は、それらの Agent のうち
最初のものを選択した状態でインポートを開きます。project の **MCP** タブでは、その project 自身のファイルに
ついて同じ表示が出ます。そのインポートは project のファイルを読み、サーバーをその project に保存します。
Goose の組み込み拡張機能のように接続先を持たないエントリは数に含まれません。

### Agent がすでに持っているエントリを引き継ぐ

Agent ファイルがすでに使っている名前でサーバーを追加しても、sync はそのエントリを上書きしません。
プランは競合 `existing entry is not managed` を報告し、そのエントリについて次のどちらかを選ぶまで
ファイルを書き込みません。

- その Agent からインポートする: `skillshare mcp import NAME --from CLIENT`、またはダッシュボードの
  競合にある **Import from** ボタン（**Import from Cursor** など）。source と一致するエントリはそのまま
  採用されます。`mcp.projects` 配下のフォルダーでの競合では、ボタンはそのフォルダーのファイルを読み込み、
  その project にインポートします。
- source の定義で置き換える: ダッシュボードの **Replace with source**、またはインポート時の `--replace`。

## 安全性と制限事項

- JSONC のコメントと無関係な設定は保持されます。変更された所有エントリは
  ひとまとまりとして置き換えられるため、それらのエントリ内のコメントは変わる可能性があります。比較・置換の対象となるのは
  Skillshare が書き込むフィールドのみで、タイムアウトなどの Agent 固有のフィールドは保持されます。
  `"type": "stdio"`、空の `env`、ヘッダー名の大文字小文字などの Agent が補完するデフォルト値は
  変更とはみなされません。管理下のサーバーを `enabled: false` や `disabled: true` でオフにすることは
  競合として報告されます。
- Claude Code が `~/.claude.json` で行うように、Agent が同じファイル内の無関係な設定を書き換えている間も、プレビューは有効なままです。その
  ファイルの MCP エントリへの変更のみが新しいプレビューを必要とします。
- Codex と Grok の編集は、通常の `[mcp_servers.NAME]` テーブルとそのサブテーブルに対応しています。
  更新されたエントリはその場に留まり、CRLF の改行も保持されます。
  インライン/ドット記法の MCP 定義はテーブルに変換してから書き込む必要があり、
  変換されていない場合はファイルを変更せずに拒否されます。
- ネイティブファイルの symlink、不正な形式のファイル、重複した JSON プロパティは
  書き込みをブロックします。Symlink された Skillshare の `config.yaml` は、そのターゲットへ書き込まれます。ファイルパーミッションは保持されます。新規のネイティブ
  ファイル、所有権の記録、バックアップにはプライベートなパーミッションが使われます。
- すでに source と一致しているエントリは、例えばチームメンバーの変更を pull した後などに、
  書き込みなしで unchanged として報告されます。この config がそれ以前にそのエントリを管理していなかった場合、
  例えば project を移動した後などでは、そのエントリは管理外のままです。
  サーバーを削除しても、インポートするまではそのまま残ります。別の
  管理外エントリには、インポートまたは明示的なエントリ単位の replace が必要です。別の
  Skillshare config の所有権は、その config ファイルがまだ存在する限り上書きできません。そのファイルがなくなっている場合、それは決して
  そのエントリを解放しないため、競合はそのエントリが取り残されていることを伝え、該当するファイルの名前を示します。そして
  ターミナルでも、ダッシュボードのその競合からでも、明示的なインポートまたは replace によってそれを引き継げます。
  マウントされていないドライブ上のファイルなど、読み取れないだけのファイルは、所有者がまだ存在しているものとみなされます。
- ダッシュボードの MCP 設定は、ブラウザがダッシュボードを `localhost` または IP アドレスで開いている場合にのみ機能します。ドメイン名経由（reverse proxy を含む）では、MCP リクエストは 403 を返します。
  なぜなら DNS rebinding 攻撃は常にドメイン名を使うからです。
- 認証情報は環境変数参照を使用します。secret ストア、OAuth セッション同期、
  ランタイムヘルスチェック、package のインストール、gateway、レジストリ、plugin の同期はありません。
- VS Code Insiders、カスタムプロファイル、リモート workspace、レガシー SSE は、このバージョンでは
  対応していません。
- VS Code は現在、`headers` 内で `${env:VARIABLE}` を置換しません
  （[microsoft/vscode#336232](https://github.com/microsoft/vscode/issues/336232)）。
  そのため、VS Code に同期されたヘッダーと `bearerToken` の参照は、それが修正されるまで解決されないままサーバーに届きます。
- ローカルの操作記録は Skillshare の state ディレクトリの `mcp/` 配下にあります。
  `state.json`、書き込み中の `pending.json`、そして `backups/`（Agent ファイルごとに最新 20 件）です。この
  ディレクトリをポータブルなマニフェストとして共有しないでください。


## Pi: MCP 拡張機能を選ぶ {#pi-choose-your-mcp-extension}

Pi は [pi-mcp-adapter](https://pi.dev/packages/pi-mcp-adapter)
または [pi-mcp-extension](https://pi.dev/packages/pi-mcp-extension) のいずれかを通じて MCP を使用できます。これらは Pi の Web サイトに掲載されているサードパーティの
package であり、Pi に組み込まれた機能ではありません。Pi には**どちらか一方**をインストールしてください。

```bash
pi install npm:pi-mcp-adapter
```

インストール後は Pi を再起動してください。Skillshare の MCP フォームで **Pi** を選択し、
インストールした package を選んでください。インポートダイアログでも同じ選択肢が提示されます。ターミナルでは
`mcp add` / `mcp edit` が選択をガイドします。スクリプトでは `--pi-extension` を指定する必要があります。

```bash
skillshare mcp add docs --url https://example.com/mcp --target pi --pi-extension pi-mcp-adapter --no-tui
skillshare sync mcp --dry-run
skillshare sync mcp
```

保存されるサーバー定義は次のとおりです。

```yaml
mcp:
  servers:
    docs:
      url: https://example.com/mcp
      targets: [pi]
      piExtension: pi-mcp-adapter
```

もう一方の package を使う場合は、インストールコマンドと選択の両方で `pi-mcp-extension` を使ってください。Pi を対象とする
Skillshare source 内のすべてのサーバーは、同じ送信先ファイルを読み込むため、同じ package を選択する必要があります。

| Package | ネイティブ出力 | sync 後にすべきこと |
|---|---|---|
| `pi-mcp-adapter` | `command`/`args` または `url`。`${VARIABLE}` 参照 | Pi を再起動/再読み込みし、`/mcp` で接続を確認する。ツールはオンデマンドで接続される。 |
| `pi-mcp-extension` | 明示的な `transport: stdio` または `streamable-http` | Pi を再起動する。新しいサーバーはデフォルトで `/mcp:start <server>` による手動起動になる。既存の `lifecycle` 設定は保持される。 |

どちらも global では `~/.pi/agent/mcp.json` を、project mode では `.pi/mcp.json` を使用します。
Skillshare はこれらの Pi 専用ファイルを使用し、adapter の共有 `.mcp.json` や
`~/.config/mcp/mcp.json` の入力は使用しません。project のエントリは、同じ名前の global エントリを上書きします。adapter の場合、global の `PI_CODING_AGENT_DIR` オーバーライドは尊重されます。
extension はそのオーバーライドを尊重しません。global の sync は、extension が無視してしまうファイルを書き込むのではなく、それを拒否します。

adapter は環境変数と HTTP ヘッダーで `fromEnv` に対応しています。
extension は環境変数参照を**展開しません**。一致する stdio 変数（例えば `TOKEN: {fromEnv: TOKEN}`）は
Pi のプロセスから継承される代わりに使われます。変数のリネームと環境変数に紐づく HTTP 認証情報は拒否されます。
これらのケースでは adapter を使ってください。Skillshare は secret の値を読み取ったりコピーしたりすることは決してありません。

### ダイレクトツール {#pi-direct-tools}

`pi-mcp-adapter` は通常、サーバーのツールに 1 つの proxy ツールを介してアクセスします。その
`directTools` 設定を使うと、代わりにそれらを個別の Pi ツールとして登録します。設定はサーバーに対して行ってください。受け取るのは Pi だけなので、同じサーバーを他の Agent にも引き続き送れます。

```yaml
mcp:
  servers:
    context7:
      command: npx
      args: ["-y", "@upstash/context7-mcp"]
      piExtension: pi-mcp-adapter
      directTools: true            # または [resolve-library-id]、または "search"
      targets: [opencode, pi]
```

| 値 | adapter の動作 |
|---|---|
| `true` | このサーバーのすべてのツールを登録する |
| 名前のリスト | 元の MCP 名で指定したツールのみを登録する |
| `"search"` | ツールを非アクティブな状態で登録する。検索で一致したものがアクティブになる |
| `false` | proxy のみ。明示的に書き込まれる |
| 省略 | Skillshare はこのフィールドに手を加えない |

省略は「変更しない」という意味です。Pi のファイルに自分で追加した `directTools` はそのまま残り、
config からフィールドを削除してもファイルからは削除されません。オフにするには
`directTools: false` と書いてください。これには `piExtension: pi-mcp-adapter` が必要で、
`disabled` とは併用できません。

コマンドラインからは、`mcp add` または `mcp edit` に `--direct-tools` を渡します。ダッシュボードでは、
`pi-mcp-adapter` を選択すると Pi extension の下に同じ選択肢が表示されます。

```bash
skillshare mcp add context7 --target pi --pi-extension pi-mcp-adapter --direct-tools true -- npx -y @upstash/context7-mcp
skillshare mcp edit context7 --direct-tools resolve-library-id,get-library-docs
```

すべてのサーバーに一度で設定するには、`directTools` を `mcp` の直下に置きます。これは、自分の
`directTools` を持たない各 `pi-mcp-adapter` サーバーに補完されます。サーバー自身の値が優先されます。
これは Skillshare のデフォルト値であり、各サーバーのエントリに書き込まれます。adapter 自身の
`settings.directTools` はサーバーと同じファイルにあり、これはユーザーに委ねられています。

```yaml
mcp:
  directTools: search              # 以下の pi-mcp-adapter サーバーすべてに適用（個別に指定されている場合を除く）
  servers:
    context7:
      command: npx
      args: ["-y", "@upstash/context7-mcp"]
      piExtension: pi-mcp-adapter
      targets: [pi]
```

[`mcp.projects`](#manage-several-projects-from-the-global-config) 配下の project は、独自の
`directTools` を持つことができ、その project ではグローバルのデフォルトを置き換えます。このデフォルトを
編集するコマンドはありません。`config.yaml` で設定するか、ダッシュボードの MCP ページにある
**デフォルト** で設定します。この項目は、Pi がデフォルトの target の 1 つになると表示されます。

`--from pi` によるインポートは、Pi 専用のファイルを読み込みます。`directTools` を持つエントリは、その値とともに、`pi-mcp-adapter` が選択された状態でインポートされます。このフィールドを持つのは adapter だけだからです。インポートした接続を保存する際は
`--pi-extension` を選択してください。ファイル単体では、どちらの package がインストールされているかを識別できません。非対応のレガシー SSE は引き続きブロックされます。OAuth と package 固有のオプションは
Pi 側で管理されたままになります。sync の成功は、設定が書き込まれたことを意味するだけであり、
extension がインストールされていることやサーバーが接続されたことを意味しません。

### その他の adapter 設定 {#pi-options}

`pi-mcp-adapter` には、`excludeTools` や `approveTools` のように、Skillshare に設定項目がない
サーバーごとのフィールドがほかにもあります。それらを `piOptions` の下に置くと、Pi のファイルにある
そのサーバーのエントリにそのまま書き込まれます。

```yaml
mcp:
  servers:
    github:
      command: npx
      args: [-y, "@modelcontextprotocol/server-github"]
      piExtension: pi-mcp-adapter
      targets: [pi]
      piOptions:
        excludeTools: ["*emulator*"]
        approveTools: ["delete_*", "merge_pull_request"]
```

コマンドラインからは、`mcp add` または `mcp edit` に JSON オブジェクトを渡します。これは
`piOptions` 全体を置き換え、`{}` でクリアします。ダッシュボードでは、サーバーのダイアログの
**Direct tools** の下に同じ入力欄があり、保存する前にテキストが JSON オブジェクトであることを確認します。
Pi にチェックが入り、**Direct tools** または **Other adapter settings** が設定されているサーバーは、その行に
アイコンが表示されます。ホバーすると設定されている項目がわかり、クリックするとダイアログが開きます。編集中に Pi の
チェックを外しても両方とも source に残るため、Pi に再びチェックを入れると元に戻ります。

```bash
skillshare mcp edit github --pi-options '{"excludeTools":["*emulator*"]}'
```

- Skillshare はフィールド名や値をチェックしません。それらを知っているのは adapter だけです。
- Skillshare 自身が書き込むフィールドは、ここでは拒否されます: `command`、`args`、`env`、`url`、
  `headers`、`transport`、`enabled`、`disabled`、`directTools`。
- 値はそのままコピーされます。認証情報はここではなく、`fromEnv` を使って `env` または `headers` に
  置いてください。
- `directTools` と同様に、`piOptions` から削除したフィールドは Pi のファイルに残ります。そちらで
  削除してください。
- これには `piExtension: pi-mcp-adapter` が必要で、`disabled` とは併用できません。他の Agent が
  これを受け取ることはなく、`import --from pi` はこれらのフィールドを読み戻しません。
