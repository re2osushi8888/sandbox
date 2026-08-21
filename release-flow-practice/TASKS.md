# Tasks - Release Flow Practice

## フェーズ 1: 基本セットアップ

### Task 1.0: Nix 開発環境のセットアップ
- [ ] `flake.nix` が存在することを確認
- [ ] `nix develop` で開発環境に入る
  ```bash
  nix develop
  ```
- [ ] `node --version` → v18.x 確認
- [ ] `npm --version` 確認

### Task 1.1: Hono + Vite アプリケーション初期化
- [ ] `nix develop` で開発環境に入っている状態で実行
- [ ] Vite + Hono テンプレートで初期化
  ```bash
  npm create hono@latest api -- --template vite
  ```
- [ ] `api/` ディレクトリが作成される
- [ ] `api/src/index.ts` を確認・カスタマイズ
  - [ ] GET `/` - ホームエンドポイント
  - [ ] GET `/health` - ヘルスチェック
  - [ ] GET `/version` - バージョン情報
- [ ] `package.json` の初期バージョンを `0.1.0` に設定
- [ ] `cd api && npm install` で依存関係をインストール
- [ ] `npm run dev` で Vite 開発サーバー起動確認
  - [ ] `http://localhost:5173` で動作確認
  - [ ] ホットモジュールリロード（HMR）確認

### Task 1.2: Dockerfile 作成
- [ ] `api/Dockerfile` を作成
  - [ ] Node.js 18.19.0-alpine ベース
  - [ ] バージョンラベル追加
  - [ ] 本番最適化（multi-stage build）
  - [ ] `npm run build` の出力を本番で使用
- [ ] `api/.dockerignore` を作成
- [ ] ローカルで `docker build` と `docker run` でテスト
- [ ] `curl localhost:3000/health` で動作確認

### Task 1.3: Git リポジトリの初期化と初回コミット
- [ ] `.gitignore` を作成（Node.js + Vite + Nix用）
  ```
  node_modules/
  dist/
  .env.local
  .DS_Store
  result
  result-*
  ```
- [ ] 初回コミット: "chore: initialize project with Vite + Hono and Nix setup"
- [ ] タグ `v0.1.0` を作成

---

## フェーズ 2: バージョン管理スクリプト

### Task 2.1: 共有バージョン管理モジュール
- [ ] `scripts/version-manager.sh` を作成
  - [ ] 現在のバージョンを取得する関数
  - [ ] package.json のバージョンを更新する関数
  - [ ] Dockerfile のバージョンラベルを更新する関数
  - [ ] Git タグを作成する関数
- [ ] 使用例やテストを作成

### Task 2.2: バージョンアップスクリプト
- [ ] `scripts/bump-version.sh` を作成
  - [ ] `--major`, `--minor`, `--patch` フラグをサポート
  - [ ] Semantic Versioning に準拠
  - [ ] package.json と Dockerfile を同期更新
  - [ ] コミットとタグを自動作成
  - [ ] 入力値のバリデーション
- [ ] 手動でテスト: `./scripts/bump-version.sh --minor`

### Task 2.3: バージョン確認スクリプト
- [ ] `scripts/version-check.sh` を作成
  - [ ] package.json のバージョン表示
  - [ ] Dockerfile のバージョンラベル確認
  - [ ] Git タグのリスト表示
  - [ ] 不一致があれば警告

---

## フェーズ 3: Blue-Green デプロイ

### Task 3.1: Cloud Run デプロイの基礎スクリプト
- [ ] `scripts/deploy-common.sh` を作成
  - [ ] GCP プロジェクト ID のバリデーション
  - [ ] Docker イメージビルド関数
  - [ ] Artifact Registry へのプッシュ関数
  - [ ] ロギング・エラーハンドリング

### Task 3.2: Blue-Green デプロイスクリプト実装
- [ ] `scripts/deploy-blue-green.sh` を作成
  - [ ] `--version` で新バージョン指定
  - [ ] Blue（現在）と Green（新規）の識別
  - [ ] Green 環境で新バージョンをデプロイ
  - [ ] ヘルスチェックが成功するまで待機
  - [ ] トラフィック切り替え（Cloud Run のトラフィック分割設定）
  - [ ] ロールバック機能
  - [ ] デプロイログ出力

### Task 3.3: Blue-Green デプロイのテスト
- [ ] GCP 環境でサービス作成（マニュアル確認用）
- [ ] スクリプトでの初回デプロイテスト（v0.1.0）
- [ ] バージョンアップ → Blue-Green デプロイ（v0.2.0）
- [ ] ヘルスチェック確認
- [ ] トラフィック切り替え動作確認
- [ ] 実際のリクエストで新バージョン動作確認

---

## フェーズ 4: カナリアリリース

### Task 4.1: カナリアリリーススクリプト実装
- [ ] `scripts/deploy-canary.sh` を作成
  - [ ] `--version` で新バージョン指定
  - [ ] `--percentage` でトラフィック割合指定（デフォルト 10%）
  - [ ] 新バージョンをデプロイ
  - [ ] Cloud Run のトラフィック分割で段階的配信
  - [ ] 進捗ログ出力
  - [ ] ロールバック機能

### Task 4.2: カナリアリリースの段階的ロールアウト
- [ ] `scripts/promote-canary.sh` を作成
  - [ ] トラフィック割合を段階的に増加
  - [ ] デフォルト段階: 10% → 25% → 50% → 100%
  - [ ] 各段階で確認時間を設ける
  - [ ] メトリクスチェック（エラーレート等の簡易確認）

### Task 4.3: カナリアリリースのテスト
- [ ] v0.2.0 でカナリアリリース開始（10%）
- [ ] トラフィック確認
- [ ] 段階的昇格テスト（25% → 50% → 100%）
- [ ] ロールバック動作確認

---

## フェーズ 5: 監視・ロールバック・運用スクリプト

### Task 5.1: 監視スクリプト
- [ ] `scripts/monitor-deployment.sh` を作成
  - [ ] Cloud Run の現在のバージョン情報取得
  - [ ] トラフィック分割状況表示
  - [ ] デプロイ状態確認
  - [ ] ヘルスチェック実行

### Task 5.2: ロールバックスクリプト
- [ ] `scripts/rollback.sh` を作成
  - [ ] 前のバージョンを確認
  - [ ] ワンコマンドでロールバック
  - [ ] 進行状況ログ出力

### Task 5.3: デプロイ状況確認スクリプト
- [ ] `scripts/deployment-status.sh` を作成
  - [ ] 現在の本番バージョン表示
  - [ ] トラフィック分割状況表示
  - [ ] 過去のデプロイ履歴表示

---

## フェーズ 6: ドキュメント・テスト

### Task 6.1: デプロイメント操作マニュアル作成
- [ ] `DEPLOYMENT.md` を作成
  - [ ] Blue-Green デプロイの手順
  - [ ] カナリアリリースの手順
  - [ ] ロールバック手順
  - [ ] トラブルシューティング

### Task 6.2: スクリプトのテスト と ドライラン
- [ ] 全スクリプトのドライラン（エラーハンドリング確認）
- [ ] GCP 環境でのエンドツーエンドテスト
  - [ ] v0.1.0 デプロイ
  - [ ] v0.2.0 への Blue-Green デプロイ
  - [ ] v0.3.0 へのカナリアリリース
  - [ ] 段階的昇格
  - [ ] ロールバック

### Task 6.3: CI/CD パイプライン（オプション）
- [ ] GitHub Actions ワークフロー作成（デプロイ自動化）
- [ ] タグプッシュで自動ビルド・デプロイ

---

## フェーズ 7: 応用・最適化

### Task 7.1: メトリクス監視スクリプト
- [ ] `scripts/check-metrics.sh` を作成
  - [ ] Cloud Monitoring からのエラーレート確認
  - [ ] レスポンスタイム確認
  - [ ] カナリアリリース判断の自動化

### Task 7.2: Istio/Service Mesh（オプション）
- [ ] Kubernetes マニフェスト作成（参考用）
- [ ] VirtualService / DestinationRule でトラフィック管理

---

## 進捗トラッキング

| フェーズ | 内容 | 進捗 |
|---------|------|------|
| 1 | 基本セットアップ | ⬜️ |
| 2 | バージョン管理スクリプト | ⬜️ |
| 3 | Blue-Green デプロイ | ⬜️ |
| 4 | カナリアリリース | ⬜️ |
| 5 | 監視・ロールバック | ⬜️ |
| 6 | ドキュメント・テスト | ⬜️ |
| 7 | 応用・最適化 | ⬜️ |

---

## 学習ポイント

- **Blue-Green デプロイ**: ゼロダウンタイムと即座のロールバック
- **カナリアリリース**: リスク最小化とリアルタイム検証
- **バージョン管理の一貫性**: Docker イメージと package.json の同期
- **スクリプト設計**: 冪等性、エラーハンドリング、ドライラン対応
- **GCP Cloud Run**: マネージドコンテナプラットフォームの活用
