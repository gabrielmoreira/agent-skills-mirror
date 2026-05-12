<div align="center">

# Garden Skills

**Claude Code、Cursor、Codex、その他の AI コーディングエージェント向けに、本番環境ですぐに使える [Agent Skills](https://support.claude.com/en/articles/12512176-what-are-skills) を厳選したコレクション。**

<a id="skills-gallery"></a>

<table>
<tr>
<td width="50%" valign="top">
<a href="#web-video-presentation"><img src="./dist/imgs/web-video-presentation-skill.png" alt="Web Video Presentation Skill" width="100%"></a>
<br/><a href="#web-video-presentation"><strong>web-video-presentation</strong></a>
<br/><sub>Web 動画 / プレゼンテーション</sub>
</td>
<td width="50%" valign="top">
<a href="#web-design-engineer"><img src="./dist/imgs/web-design-skill.png" alt="Web Design Skill" width="100%"></a>
<br/><a href="#web-design-engineer"><strong>web-design-engineer</strong></a>
<br/><sub>デザイン / フロントエンド</sub>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<a href="#gpt-image-2"><img src="./dist/imgs/gpt-image-2-skill.png" alt="GPT Image 2 Skill" width="100%"></a>
<br/><a href="#gpt-image-2"><strong>gpt-image-2</strong></a>
<br/><sub>画像生成 / プロンプト</sub>
</td>
<td width="50%" valign="top">
<a href="#kb-retriever"><img src="./dist/imgs/kb-retriever-skill.png" alt="KB Retriever Skill" width="100%"></a>
<br/><a href="#kb-retriever"><strong>kb-retriever</strong></a>
<br/><sub>ローカル知識ベース検索</sub>
</td>
</tr>
</table>

[![License: MIT](https://img.shields.io/github/license/ConardLi/garden-skills?style=flat-square&color=blue)](./LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/ConardLi/garden-skills?style=flat-square)](https://github.com/ConardLi/garden-skills/stargazers)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)](#コントリビュート)
[![Skills count](https://img.shields.io/badge/skills-4-orange?style=flat-square)](#skills-gallery)
[![Spec](https://img.shields.io/badge/spec-SKILL.md-black?style=flat-square)](https://agentskills.io)

[English](./README.md) · [中文文档](./README.zh-CN.md) · [日本語](./README.ja-JP.md)

</div>

---

## 目次

| インストール | 使い方 | コントリビュート |
|---|---|---|
| [インストール](#インストール)<br>[`skills` CLI（npx）](#方法-a--skills-clinpx)<br>[Claude Code プラグインマーケットプレイス](#方法-b--claude-code-プラグインマーケットプレイス)<br>[Releases のバージョン固定 `.zip`](#方法-c--releases-のバージョン固定-zip)<br>[手動コピー](#方法-d--プロジェクトへ手動コピー)<br>[Git submodule](#方法-e--git-submodule) | [互換性](#互換性)<br>[Skill とは？](#skill-とは) | [コントリビュート](#コントリビュート)<br>[謝辞](#謝辞)<br>[ライセンス](#ライセンス) |

---

### [`web-video-presentation`](./skills/web-video-presentation)

![Web Video Presentation Skill](./dist/imgs/web-video-presentation-skill.png)

**カテゴリ:** Web 動画 / プレゼンテーションエンジニアリング  
**用途:** スクリプト、記事、レッスン、製品デモ、トークを、シネマティックな動画として画面録画できるクリック駆動の 16:9 Web プレゼンテーションに変換します。

`web-video-presentation` は、動画制作環境のように振る舞う録画対応の Vite + React + TypeScript プレゼンテーションを構築します。このワークフローでは、生の記事をナレーションスクリプトに変換し、スクリプトの各ビートをフルスクリーンシーンにマッピングし、必要なチェックポイントで一時停止し、ビジュアルアウトラインの承認後にオプションでナレーション音声を合成できます。

主な特徴:

- 安定した画面録画のため、ビューポートに合わせてスケールする固定 1920×1080 ステージ
- クリック / キーボード駆動の `(chapter, step)` カーソル、ビジュアルステップごとに 1 つのナレーションビート
- スクリプト、テーマ、アウトライン、実装モード、オプションの音声に対する厳格なコラボレーションチェックポイント
- 録画中もステージをクリーンに保つ、ホバー時のみ表示される進捗コントロール
- `paper-press` から `terminal-green` まで複数のビジュアル言語を持つテーマトークンアーキテクチャ
- 再利用可能なステージプリミティブと録画ガイダンスを備えた Vite + React + TypeScript プロジェクトのスキャフォールド

リンク: [README](./skills/web-video-presentation/README.md) · [SKILL.md](./skills/web-video-presentation/SKILL.md) · <!-- DOWNLOAD:web-video-presentation:start -->[Download v1.1.5 .zip](https://github.com/ConardLi/garden-skills/releases/download/web-video-presentation-v1.1.5/web-video-presentation-1.1.5.zip)<!-- DOWNLOAD:web-video-presentation:end -->

---

### [`web-design-engineer`](./skills/web-design-engineer)

![Web Design Skill](./dist/imgs/web-design-skill.png)

**カテゴリ:** デザイン / フロントエンド  
**用途:** Web ページ、ランディングページ、ダッシュボード、インタラクティブプロトタイプ、HTML スライドデッキ、アニメーション、UI モックアップ、データビジュアライゼーション、デザインシステムの探求。

`web-design-engineer` は、AI が生成する Web 成果物を単に機能するだけのものから、洗練され、意図的で、視覚的に印象に残るフロントエンド作品へと変えます。エージェントをデザインエンジニアとして扱い、まず製品コンテキストを理解し、次にデザインシステムを宣言し、初期 v0 を示し、フルエクスペリエンスを構築し、結果を検証します。

主な特徴:

- 要件 → コンテキスト → デザインシステム → v0 → フルビルド → 検証という 6 ステップのデザインワークフローを定義
- アンチクリシェのブロックリストとより強いビジュアル判断力で、一般的な AI UI パターンを超える
- HTML / CSS / JavaScript / React プロトタイプをカバーし、レスポンシブレイアウト、モーション、インタラクションの仕上げに関するガイダンスを提供
- インライン React + Babel、CSS トークン、`oklch()` カラー処理、コンテナクエリ、reduced-motion 対応の実装ルールを含む
- デバイスフレーム、スライドエンジン、アニメーションタイムライン、ダッシュボード、その他の再利用可能な Web 成果物のための高度なパターンリファレンスを同梱

リンク: [README](./skills/web-design-engineer/README.md) · [SKILL.md](./skills/web-design-engineer/SKILL.md) · [Website](./website/web-design-website) · [Demo](./demo/web-design-demo) · <!-- DOWNLOAD:web-design-engineer:start -->[Download v1.0.0 .zip](https://github.com/ConardLi/garden-skills/releases/download/web-design-engineer-v1.0.0/web-design-engineer-1.0.0.zip)<!-- DOWNLOAD:web-design-engineer:end -->

---

### [`gpt-image-2`](./skills/gpt-image-2)

![GPT Image 2 Skill](./dist/imgs/gpt-image-2-skill.png)

**カテゴリ:** 画像生成 / プロンプトエンジニアリング  
**用途:** ポスター、UI モックアップ、製品ビジュアル、インフォグラフィック、学術図、技術図、コミック、アバター、ストーリーボード、ブランディングボード、画像編集ワークフロー。

`gpt-image-2` は、GPT Image 2 および OpenAI 互換の画像 API に特化した画像生成スキルです。完全にローカルな Garden での生成、ホストネイティブの画像ツールへの委譲、画像ツールがない場合のプロンプトのみのアドバイザーモードなど、異なるエージェント環境で動作するように設計されています。

主な特徴:

- 3 つのランタイムモードをサポート: **モード A: Garden ローカル**、**モード B: ホストネイティブ委譲**、**モード C: アドバイザー専用プロンプト作成**
- すべてのタスクをモード検出から開始し、スキルが間違った実行パスを暗黙的に選択しないようにする
- `references/` 配下に 18 のビジュアルカテゴリと 80 以上の構造化プロンプトテンプレートを提供
- 専用のワークフローとスクリプトを通じて、画像生成と画像編集の両方をカバー
- Garden モードでは、再利用、レビュー、バージョン管理のためにプロンプトと生成画像を `garden-gpt-image-2/` 配下に保存

リンク: [README](./skills/gpt-image-2/README.md) · [SKILL.md](./skills/gpt-image-2/SKILL.md) · [Website](./website/gpt-image2-website) · <!-- DOWNLOAD:gpt-image-2:start -->[Download v1.0.3 .zip](https://github.com/ConardLi/garden-skills/releases/download/gpt-image-2-v1.0.3/gpt-image-2-1.0.3.zip)<!-- DOWNLOAD:gpt-image-2:end -->

---

### [`kb-retriever`](./skills/kb-retriever)

![Kb Retriever Skill](./dist/imgs/kb-retriever-skill.png)

**カテゴリ:** 検索 / ローカル知識ベース  
**用途:** ローカルの `knowledge/` ディレクトリから質問に答え、構造化されたドキュメントを検索し、エージェントのコンテキストを溢れさせることなく Markdown、テキスト、PDF、Excel ファイルから根拠を抽出します。

`kb-retriever` は、慎重で段階的な検索を中心に構築されたローカル知識ベースのリトリーバです。ファイル全体を読み込むのではなく、階層的なインデックスファイルをたどり、候補集合を絞り込み、複雑なファイルタイプを正しく処理し、出典付きで回答します。

主な特徴:

- 階層化された `data_structure.md` ファイルを使用して、コンテンツを検索する前に知識ベース内を移動
- PDF および Excel ファイルに対して**learn-before-process**ルールを強制し、抽出や分析の前に同梱のリファレンスドキュメントを使用
- 正確なキーワード検索、ローカルウィンドウ読み込み、同義語、反復的なリファインメントを組み合わせる
- 検索を最大 5 ラウンドに制限し、探索を制御された範囲に保つ
- `grep`、`pdftotext`、`pdfplumber`、`pandas` のワークフローと、出典を意識した回答フォーマットを含む

リンク: [README](./skills/kb-retriever/README.md) · [SKILL.md](./skills/kb-retriever/SKILL.md) · <!-- DOWNLOAD:kb-retriever:start -->[Download v1.0.0 .zip](https://github.com/ConardLi/garden-skills/releases/download/kb-retriever-v1.0.0/kb-retriever-1.0.0.zip)<!-- DOWNLOAD:kb-retriever:end -->

---

## インストール

サポートされているインストール方法は 5 つあります。自分のスタックに合うものを選んでください:

| # | 方法 | 用途 | バージョン固定？ |
|---|---|---|---|
| A | [`skills` CLI（`npx skills add`）](#方法-a--skills-clinpx) | あらゆるエージェント、ワンラインインストール、スキルをピンポイントで選択 | ✅ タグ URL 経由 |
| B | [Claude Code プラグインマーケットプレイス](#方法-b--claude-code-プラグインマーケットプレイス) | プラグインパックを購読したい Claude Code ユーザー | ✅ マーケットプレイスのバージョン経由 |
| C | [GitHub Releases のバージョン固定 `.zip`](#方法-c--releases-のバージョン固定-zip) | CI / エアギャップ環境 / 再現可能なインストール | ✅ ✅（不変） |
| D | [`git clone` 後の手動コピー](#方法-d--プロジェクトへ手動コピー) | スキル自体のローカルでのハック | ❌（`main` を追跡） |
| E | [Git submodule](#方法-e--git-submodule) | より大きなプロジェクトにベンダリングし、アップストリームの更新を取り込みたい | ✅ submodule の SHA 経由 |

> 上記の各スキルセクションには「Links:」行に **`Download v<version> .zip`** リンクがあり、
> 現在のバージョン固定リリースアーティファクトを指しています。これらの
> URL はリリースごとに [`scripts/release/update-readme.mjs`](./scripts/release/update-readme.mjs)
> によって自動的に書き換えられるため、常に最新の不変バージョンを示します。

### 方法 A · `skills` CLI（npx）

最速のエージェント非依存のパスです。エージェント（Claude Code、Cursor、Codex など）を
自動検出し、スキルを適切なディレクトリにドロップする標準的な [`npx skills` CLI](https://www.npmjs.com/package/skills) を使用します。

```bash
# 4 つのスキルすべてをインストール（最新）
npx skills add ConardLi/garden-skills

# 1 つのスキルだけをインストール（最新）
npx skills add ConardLi/garden-skills -s web-design-engineer

# プロジェクト単位（./.skills）ではなくグローバル（~/.skills）にインストール
npx skills add ConardLi/garden-skills -s gpt-image-2 --global

# 特定のエージェントをターゲットにする
npx skills add ConardLi/garden-skills -s kb-retriever -a claude-code
```

> **デフォルトは `main` の最新コミット。** これが 95% の場合に求められるものです。
> CLI は各スキルの最新の公開済み `SKILL.md` をソースツリーから直接追跡します。

**バージョンを固定したい？（CI / 本番）** タグスコープの `tree/` URL を使用します。
これはリリースが切られた正確なコミットを指します:

```bash
# 1 つのスキルを特定のリリースに固定
npx skills add ConardLi/garden-skills/tree/web-design-engineer-v1.0.0/skills/web-design-engineer
```

各スキルについて、現在のバージョン固定 `.zip` URL は上記の
「Links:」行にもインラインで表示されています（`Download v<version> .zip` リンク）。

便利なサブコマンド:

```bash
npx skills list                 # インストール済みのスキル
npx skills find web-design      # レジストリを検索
npx skills update               # すべてを更新
npx skills remove kb-retriever  # アンインストール
```

### 方法 B · Claude Code プラグインマーケットプレイス

[Claude Code](https://docs.anthropic.com/en/docs/claude-code) を使用している場合、
マーケットプレイスを購読して、1 つ以上のスキルをバンドルしたプラグインパックをインストールできます:

```bash
/plugin marketplace add ConardLi/garden-skills
/plugin install presentation-skills@garden-skills
/plugin install web-design-skills@garden-skills
/plugin install knowledge-base-skills@garden-skills
/plugin install image-generation-skills@garden-skills
```

プラグインパックは [`.claude-plugin/marketplace.json`](./.claude-plugin/marketplace.json) で宣言されています:

| プラグインパック | 含まれるスキル |
|---|---|
| `presentation-skills` | `web-video-presentation` |
| `web-design-skills` | `web-design-engineer` |
| `knowledge-base-skills` | `kb-retriever` |
| `image-generation-skills` | `gpt-image-2` |

### 方法 C · Releases のバージョン固定 `.zip`

正式なリリースごとに、不変の `.zip`（SHA-256 チェックサム付き）が
[GitHub Releases](https://github.com/ConardLi/garden-skills/releases) に公開されます。
正確なバイト列が後から変わらないことを保証する必要がある場合は、CI、Dockerfile、
エアギャップインストーラからこれにピン留めしてください。

```bash
# <skill> と <version> を希望するバージョンに置き換えてください。
SKILL=web-design-engineer
VERSION=1.0.0

curl -fsSL -o "${SKILL}.zip" \
  "https://github.com/ConardLi/garden-skills/releases/download/${SKILL}-v${VERSION}/${SKILL}-${VERSION}.zip"

# チェックサムを検証（無人インストールでは強く推奨）
curl -fsSL -o "${SKILL}.zip.sha256" \
  "https://github.com/ConardLi/garden-skills/releases/download/${SKILL}-v${VERSION}/${SKILL}-${VERSION}.zip.sha256"
shasum -a 256 -c "${SKILL}.zip.sha256"

# エージェントのスキルディレクトリにフォルダを展開
unzip -q "${SKILL}.zip" -d .claude/skills/   # または .agents/skills/、.codex/skills/ ...
```

フローティング「常に最新」の URL も利用可能で、ワンオフのインストールに便利です:

```bash
https://github.com/ConardLi/garden-skills/releases/latest/download/<skill>-<version>.zip
```

> **すべてのスキルのバージョン固定 URL は、この README にインラインでリストされています** -
> 上記の各スキルの「Links」エントリの下にある「Download」行を参照してください。
> これらはリリースパイプラインによって自動的に同期されます。

### 方法 D · プロジェクトへ手動コピー

リポジトリをクローンし、必要なスキルフォルダをコピーします。スキル自体を
フォークまたはハックしたい場合に便利です。

```bash
git clone https://github.com/ConardLi/garden-skills.git
cp -r garden-skills/skills/web-design-engineer  your-project/.claude/skills/
# Cursor / 汎用エージェント:
cp -r garden-skills/skills/web-design-engineer  your-project/.agents/skills/
```

次回エージェントがワークスペースをスキャンしたときに、スキルが検出されます。

### 方法 E · Git submodule

アップストリームの更新を追跡したい、より大きなプロジェクトへのベンダリング用:

```bash
git submodule add https://github.com/ConardLi/garden-skills.git vendor/garden-skills
ln -s ../../vendor/garden-skills/skills/web-design-engineer .claude/skills/web-design-engineer
```

再現性のためにリリースタグに固定:

```bash
cd vendor/garden-skills
git checkout web-design-engineer-v1.0.0
```

---

## 互換性

| エージェント / ランタイム | スキルの場所 | ステータス |
|---|---|---|
| **Claude Code** | `.claude/skills/<name>/` またはプラグインマーケットプレイス経由 | ✅ テスト済み |
| **Claude.ai**（Web） | Settings → Capabilities → Skills | ✅ テスト済み |
| **Cursor** | `.agents/skills/<name>/` | ✅ テスト済み |
| **Codex CLI** | `.codex/skills/<name>/` | ✅ テスト済み |
| **Gemini CLI** | extension manifest | ✅ テスト済み |
| **OpenCode** | `.opencode/skills/<name>/` | ✅ テスト済み |

> `SKILL.md` フォーマットは設計上ポータブルです。エージェントがスキルをサポートしていれば、フォルダをスキャンするディレクトリにコピーするだけで動作するはずです。このマトリクスを拡張する PR を歓迎します。

---

## Skill とは？

**Skill** は、エージェントがオンデマンドで読み込める自己完結型のフォルダです。
これは `SKILL.md`（YAML フロントマター + 指示）と、オプションでリファレンスドキュメント、
スクリプト、アセットで構成されます:

```text
<skill-name>/
├── SKILL.md      ← 必須: いつ使うか + どのように使うか
├── README.md     ← 人間向けドキュメント
├── references/   ← オプション: エージェントがオンデマンドで読み込む拡張ドキュメント
├── scripts/      ← オプション: 決定論的な実行可能ヘルパー
└── assets/       ← オプション: テンプレート、フォント、アイコン
```

エージェントは、フロントマターの `description` 行からスキルを有効化するかどうかを
決定します。したがって、description はあなたとエージェントの間の契約です。
詳細な仕様については、[agentskills.io](https://agentskills.io) および
[Anthropic のリファレンスリポジトリ](https://github.com/anthropics/skills) を参照してください。

---

## コントリビュート

バグレポート、新しいスキル、ツールの改善など、すべてを歓迎します。

メンテナー向けのドキュメント（リポジトリ構成、リリースプロセス、バージョン
ルール、CI ワークフロー、トラブルシューティング）は
[**`CONTRIBUTING.md`**](./CONTRIBUTING.md) ([中文](./CONTRIBUTING.zh-CN.md)) にあります。
スキルを追加したりリリースを切ったりしたい場合は、まずそちらを読んでください。

クイックオリエンテーション:

```bash
git clone https://github.com/ConardLi/garden-skills.git
cd garden-skills
npm run list      # すべてのスキル + マニフェストステータスを表示
npm run validate  # CI がすべての PR で実行するのと同じチェック
```

---

## 謝辞

このコレクションは、以下の肩の上に成り立っています:

- **[Anthropic](https://www.anthropic.com)** - [Agent Skills 仕様](https://agentskills.io) および [`anthropics/skills`](https://github.com/anthropics/skills) リファレンスリポジトリの提供。
- **[Claude Design](https://www.anthropic.com/news/claude-design-anthropic-labs)** - `web-design-engineer` のインスピレーションとなったシステムプロンプト。オリジナルは参考のため [`dist/prompt/claude-design-system-prompt.md`](./dist/prompt/claude-design-system-prompt.md) に保存されています。
- より広い OSS スキルコミュニティ - さらなる発見のために [`travisvn/awesome-claude-skills`](https://github.com/travisvn/awesome-claude-skills) と [`obra/superpowers`](https://github.com/obra/superpowers) を参照してください。

---

## ライセンス

[MIT](./LICENSE) © [ConardLi](https://github.com/ConardLi)
