# AGENTS.md

## プロジェクト概要

これは初心者にウェブ開発の基礎を教えるための教育用カリキュラムリポジトリです。カリキュラムはMicrosoft Cloud Advocatesによって開発された包括的な12週間のコースで、JavaScript、CSS、HTMLをカバーする24の実践的なレッスンが含まれています。

### 主な構成要素

- <strong>教育コンテンツ</strong>: プロジェクトベースのモジュールに整理された24の構造化レッスン
- <strong>実践プロジェクト</strong>: テラリウム、タイピングゲーム、ブラウザ拡張機能、スペースゲーム、銀行アプリ、コードエディター、AIチャットアシスタント
- <strong>インタラクティブなクイズ</strong>: 各3問の48のクイズ（レッスン前後の評価）
- <strong>多言語サポート</strong>: GitHub Actionsによる50以上の言語への自動翻訳
- <strong>技術スタック</strong>: HTML、CSS、JavaScript、Vue.js 3、Vite、Node.js、Express、Python（AIプロジェクト向け）

### アーキテクチャ

- レッスンベースの構造を持つ教育用リポジトリ
- 各レッスンフォルダーにREADME、コード例、解答が含まれる
- 独立したプロジェクトは別のディレクトリに配置（quiz-app、各レッスンのプロジェクト）
- GitHub Actions（co-op-translator）を利用した翻訳システム
- Docsifyによるドキュメンテーション配信およびPDF形式で利用可能

## セットアップコマンド

このリポジトリは主に教育用コンテンツの利用を目的としています。特定のプロジェクトで作業する場合:

### メインリポジトリのセットアップ

```bash
git clone https://github.com/microsoft/Web-Dev-For-Beginners.git
cd Web-Dev-For-Beginners
```

### クイズアプリセットアップ (Vue 3 + Vite)

```bash
cd quiz-app
npm install
npm run dev        # 開発サーバーを起動する
npm run build      # 本番用にビルドする
npm run lint       # ESLintを実行する
```

### 銀行プロジェクトAPI (Node.js + Express)

```bash
cd 7-bank-project/api
npm install
npm start          # APIサーバーを起動する
npm run lint       # ESLint を実行する
npm run format     # Prettier で整形する
```

### ブラウザ拡張機能プロジェクト

```bash
cd 5-browser-extension/solution
npm install
# ブラウザ固有の拡張機能読み込み手順に従ってください
```

### スペースゲームプロジェクト

```bash
cd 6-space-game/solution
npm install
# ブラウザーでindex.htmlを開くか、Live Serverを使用してください
```

### チャットプロジェクト (Pythonバックエンド)

```bash
cd 9-chat-project/solution/backend/python
pip install openai
# GITHUB_TOKEN 環境変数を設定する
python api.py
```

## 開発ワークフロー

### コンテンツ寄稿者向け

1. リポジトリをGitHubアカウントに<strong>フォーク</strong>
2. フォークをローカルに<strong>クローン</strong>
3. 変更用に<strong>新しいブランチを作成</strong>
4. レッスン内容やコード例の変更を行う
5. 関連プロジェクトディレクトリでコード変更をテスト
6. コントリビューションガイドラインに従いプルリクエストを提出

### 学習者向け

1. リポジトリをフォークまたはクローン
2. レッスンディレクトリを順に移動
3. 各レッスンのREADMEを読む
4. https://ff-quizzes.netlify.app/web/ でレッスン前クイズを完了
5. レッスンフォルダ内のコード例を進める
6. 課題やチャレンジを完了する
7. レッスン後クイズを受ける

### ライブ開発

- <strong>ドキュメント</strong>: ルートで `docsify serve` 実行（ポート3000）
- <strong>クイズアプリ</strong>: quiz-appディレクトリで `npm run dev` 実行
- <strong>プロジェクト</strong>: HTMLプロジェクトはVS Code Live Server拡張を使用
- **APIプロジェクト**: 対応するAPIディレクトリで `npm start` 実行

## テスト手順

### クイズアプリテスト

```bash
cd quiz-app
npm run lint       # コードスタイルの問題をチェックする
npm run build      # ビルドが成功することを確認する
```

### 銀行APIテスト

```bash
cd 7-bank-project/api
npm run lint       # コーディングスタイルの問題を確認する
node server.js     # サーバーがエラーなく起動することを確認する
```

### 一般的なテストアプローチ

- このリポジトリは包括的な自動テストを備えていない教育用
- 手動テストは以下に注力:
  - コード例がエラーなく動作すること
  - ドキュメント内リンクが動作すること
  - プロジェクトビルドが成功すること
  - 例がベストプラクティスに沿っていること

### 提出前チェックポイント

- package.jsonがあるディレクトリで `npm run lint` を実行
- マークダウンリンクが有効か確認
- ブラウザやNode.jsでコード例をテスト
- 翻訳が正しい構造を維持していることを確認

## コードスタイルガイドライン

### JavaScript

- モダンなES6+構文を使用
- プロジェクト提供の標準ESLint設定に従う
- 教育的明確さを考慮した意味のある変数・関数名を使用
- 学習者向けに概念を説明するコメントを追加
- Prettier設定がある場合は整形使用

### HTML/CSS

- セマンティックなHTML5要素
- レスポンシブデザイン原則の適用
- 明確なクラス命名規則
- CSS手法を説明するコメントを学習者向けに追加

### Python

- PEP 8スタイルガイドに従う
- 分かりやすい教育的コード例
- 学習に役立つ場合はタイプヒントを使用

### Markdownドキュメンテーション

- 明確な見出し階層
- 言語指定付きコードブロック
- 追加リソースへのリンク
- `images/`フォルダ内のスクリーンショット・画像
- アクセシビリティのための画像のaltテキスト

### ファイル構成

- レッスンは連番（1-getting-started-lessons、2-js-basicsなど）
- 各プロジェクトは `solution/`、場合によっては `start/` や `your-work/` ディレクトリを持つ
- 画像はレッスンごとの `images/` フォルダ内に格納
- 翻訳ファイルは `translations/{language-code}/` フォルダ構造

## ビルドとデプロイ

### クイズアプリのデプロイ (Azure Static Web Apps)

quiz-appはAzure Static Web Apps用に設定されています:

```bash
cd quiz-app
npm run build      # dist/フォルダーを作成します
# mainブランチへのプッシュ時にGitHub Actionsワークフローを介してデプロイします
```

Azure Static Web Appsの設定:
- <strong>アプリ場所</strong>: `/quiz-app`
- <strong>出力場所</strong>: `dist`
- <strong>ワークフロー</strong>: `.github/workflows/azure-static-web-apps-ashy-river-0debb7803.yml`

### ドキュメントPDF生成

```bash
npm install                    # docsify-to-pdf をインストールする
npm run convert               # docs から PDF を生成する
```

### Docsifyドキュメント

```bash
npm install -g docsify-cli    # Docsify をグローバルにインストールする
docsify serve                 # localhost:3000 で提供する
```

### プロジェクト固有のビルド

各プロジェクトディレクトリは独自のビルドプロセスを持つ場合がある:
- Vueプロジェクト: `npm run build` で本番バンドル作成
- 静的プロジェクト: ビルド不要でファイルを直接配信

## プルリクエストガイドライン

### タイトルフォーマット

明確で説明的なタイトルを使用:
- `[Quiz-app] レッスンXの新しいクイズを追加`
- `[Lesson-3] テラリウムプロジェクトの誤字修正`
- `[Translation] レッスン5のスペイン語翻訳を追加`
- `[Docs] セットアップ手順を更新`

### 必須チェック

PR提出前に:

1. <strong>コード品質</strong>:
   - 影響を受けるプロジェクトディレクトリで `npm run lint` 実行
   - すべてのエラー・警告を修正

2. <strong>ビルド検証</strong>:
   - 該当すれば `npm run build` 実行
   - ビルドエラーなしを確認

3. <strong>リンク検証</strong>:
   - すべてのマークダウンリンクをテスト
   - 画像参照が有効か確認

4. <strong>コンテンツレビュー</strong>:
   - スペル・文法を校正
   - コード例が正しく教育的か確認
   - 翻訳が意味を維持しているか検証

### コントリビューション要件

- Microsoft CLAに同意（初回PRで自動チェック）
- [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/)に従う
- 詳細は[CONTRIBUTING.md](./CONTRIBUTING.md)参照
- PR説明に該当する場合はイシュー番号を記載

### レビュー手順

- PRはメンテナーとコミュニティがレビュー
- 教育的明確さを最優先
- コード例は最新のベストプラクティスに従うこと
- 翻訳は正確性と文化的適切性をレビュー

## 翻訳システム

### 自動翻訳

- GitHub Actionsのco-op-translatorワークフローを使用
- 50以上の言語に自動翻訳
- ソースファイルはメインディレクトリ内
- 翻訳ファイルは `translations/{language-code}/` に格納

### 手動での翻訳改善追加

1. `translations/{language-code}/` 内のファイルを特定
2. 構造を維持しつつ改善を行う
3. コード例の機能を維持
4. ローカライズされたクイズ内容を確認

### 翻訳メタデータ

翻訳ファイルには以下のようなメタデータヘッダーが含まれます:
```markdown
<!--
CO_OP_TRANSLATOR_METADATA:
{
  "original_hash": "...",
  "translation_date": "...",
  "source_file": "...",
  "language_code": "..."
}
-->
```

## デバッグとトラブルシューティング

### よくある問題

<strong>クイズアプリが起動しない</strong>:
- Node.jsバージョンを確認（v14+推奨）
- `node_modules` と `package-lock.json` を削除し `npm install` 実行
- ポート競合を確認（デフォルト: Viteはポート5173）

**APIサーバーが起動しない**:
- Node.jsのバージョン確認（node >=10必要）
- ポートがすでに使われていないかチェック
- 依存関係がすべて `npm install` でインストールされているか確認

<strong>ブラウザ拡張機能が読み込まれない</strong>:
- manifest.jsonのフォーマットが正しいか確認
- ブラウザのコンソールでエラーをチェック
- ブラウザ別の拡張機能インストール手順に従う

**Pythonチャットプロジェクトの問題**:
- OpenAIパッケージがインストールされているか: `pip install openai`
- GITHUB_TOKEN環境変数が設定されているか
- GitHub Modelsアクセス権限を確認

**Docsifyがドキュメントを配信しない**:
- docsify-cliをグローバルにインストール: `npm install -g docsify-cli`
- リポジトリルートから実行
- `docs/_sidebar.md` が存在するか確認

### 開発環境ヒント

- HTMLプロジェクトにはVS CodeのLive Server拡張を使用
- ESLintとPrettierの拡張をインストールしてコード整形を統一
- JavaScriptのデバッグにはブラウザの開発者ツールを使用
- VueプロジェクトにはVue DevToolsブラウザ拡張を導入

### パフォーマンスの考慮点

- 翻訳ファイルは多数（50以上の言語）あり、フルクローンは大きい
- コンテンツ作業のみなら浅いクローンを推奨: `git clone --depth 1`
- 英語コンテンツ作業時は翻訳ファイルを検索対象から除外
- 初回実行はビルドや依存インストールのため遅い可能性あり

## セキュリティ考慮事項

### 環境変数

- APIキーはリポジトリにコミットしない
- `.env`ファイルを利用（`.gitignore`に含まれている）
- 必要な環境変数は各プロジェクトのREADMEに記載

### Pythonプロジェクト

- 仮想環境の利用推奨: `python -m venv venv`
- 依存関係は常に最新に保つ
- GitHubトークンは必要最小限の権限で

### GitHub Modelsアクセス

- GitHub Models用の個人アクセストークン（PAT）が必要
- トークンは環境変数として管理
- トークンや認証情報をコミットしない

## 追加ノート

### 対象ユーザー

- ウェブ開発の完全初心者
- 学生や自己学習者
- 教室でカリキュラムを使用する教師
- コンテンツはアクセシビリティと段階的スキル習得を目標

### 教育的理念

- プロジェクトベース学習
- 頻繁な知識確認（クイズ）
- ハンズオンコーディング演習
- 実世界の応用例
- フレームワークより基礎重視

### リポジトリのメンテナンス

- 活発な学習者と寄稿者コミュニティ
- 依存関係とコンテンツの定期的な更新
- イシューや議論はメンテナーが監視
- GitHub Actionsで翻訳更新を自動化

### 関連リソース

- [Microsoft Learn モジュール](https://docs.microsoft.com/learn/)
- [Student Hub リソース](https://docs.microsoft.com/learn/student-hub/)
- 学習者向けに [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) 推奨
- 追加コース: ジェネレーティブAI、データサイエンス、ML、IoTカリキュラム

### 個別プロジェクトでの作業

各プロジェクトの詳細手順はREADMEを参照:
- `quiz-app/README.md` - Vue 3クイズアプリケーション
- `7-bank-project/README.md` - 認証付き銀行アプリケーション
- `5-browser-extension/README.md` - ブラウザ拡張開発
- `6-space-game/README.md` - Canvasベースゲーム開発
- `9-chat-project/README.md` - AIチャットアシスタントプロジェクト

### モノレポ構造

厳密なモノレポではありませんが複数の独立プロジェクトを含む:
- 各レッスンは自己完結型
- プロジェクトは依存関係を共有しない
- 個別プロジェクトに影響を与えず作業可能
- 全カリキュラム体験にはリポジトリ全体をクローン

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
**免責事項**:  
本書類はAI翻訳サービス [Co-op Translator](https://github.com/Azure/co-op-translator) を使用して翻訳されています。正確を期していますが、自動翻訳には誤りや不正確な部分が含まれる場合があります。原文の母国語版が正式な情報源とみなされるべきです。重要な情報については、専門の人間による翻訳を推奨します。本翻訳の使用により生じた誤解や誤訳に関して当方は一切の責任を負いません。
<!-- CO-OP TRANSLATOR DISCLAIMER END -->