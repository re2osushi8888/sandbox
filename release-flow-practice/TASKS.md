# Tasks - Release Flow Practice

## フェーズ 1: 基本セットアップ

### Task 1.1: Hono + Bun アプリケーション初期化
- [x] Bun がインストール済みであることを確認
  ```bash
  bun --version
  ```
- [x] Hono テンプレートで初期化
  ```bash
  bunx create-hono api
  ```
- [x] `api/` ディレクトリが作成される
- [x] `api/src/index.ts` を確認・カスタマイズ
  - [x] GET `/` - ホームエンドポイント
  - [x] GET `/health` - ヘルスチェック（末尾を `z` にしない。[ADR-0001](docs/adr/0001-version-management-approach.md) 参照）
  - [x] GET `/version` - バージョン情報（`version`, `gitSha`, `buildTime`, `env`, `revision` を返す）
- [ ] ~~`package.json` の初期バージョンを `0.1.0` に設定~~（廃止：バージョンは Git tag を単一の真実の源とし、`package.json` は人手で編集しない。[ADR-0001](docs/adr/0001-version-management-approach.md) 参照）
- [x] `cd api && bun install` で依存関係をインストール
- [x] `bun run dev` で開発サーバー起動確認
  - [x] `http://localhost:4000` で動作確認（`PORT` 環境変数で変更可能）

### Task 1.2: Dockerfile 作成
- [x] `api/Dockerfile` を作成
  - [x] `oven/bun:1.4.0-alpine` ベース（マルチステージ: install → release）
  - [x] `ARG VERSION` / `GIT_SHA` / `BUILD_TIME` をビルド時に注入し `ENV` と `LABEL` に反映
  - [x] レイヤーキャッシュ保護のため変動する値は最終ステージの末尾に配置
  - [x] `USER bun` で非 root 実行
  - [x] `bun install --frozen-lockfile --production` で依存関係を最小化
  - [x] `EXPOSE` をアプリの実リスンポート（`4000`）に統一（当初 `3000` と不一致があり `Connection reset by peer` の原因になっていたため修正）
- [x] `api/.dockerignore` を作成
- [x] `.env.build` + `scripts/build.sh` で VERSION / GIT_SHA / BUILD_TIME を渡してビルドできるようにする
- [x] ローカルで `docker build` と `docker run` でテスト
- [x] `curl localhost:4000/health` で動作確認（`/`, `/health`, `/version` すべて疎通確認済み）

### Task 1.4: ADR（アーキテクチャ決定記録）の作成
- [x] `docs/adr/README.md` を作成（ADR インデックス）
- [x] `docs/adr/0001-version-management-approach.md` を作成
  - [x] バージョン管理は Git tag を単一の真実の源とする方針を明記
  - [x] ビルド時に `VERSION` / `GIT_SHA` / `BUILD_TIME` をイメージへ焼き込む方式を明記
  - [x] `/health` と `/version` の役割分離、`/health` のパス命名規則（末尾 `z` 回避）を明記
- [x] `docs/adr/0002-secret-management-strategy.md` を作成
  - [x] ローカル開発は SOPS + age、Cloud Run（staging/production）は GCP Secret Manager に管理方式を分離する方針を明記

### Task 1.5: 機密情報管理のセットアップ（ADR-0002）
- [x] `.mise.toml` で `sops` / `age` / `gcloud` のバージョンを固定（CLI ツール限定、ランタイムは引き続き Bun）
  - [x] `mise install` で 3 ツールとも動作確認済み（sops 3.13.3 / age 1.3.1 / gcloud 581.0.0）
- [x] `.sops.yaml` を作成（`.env.enc` を age 鍵で暗号化する設定。staging/production は Secret Manager のため対象外）
- [x] `.env.enc` を作成（暗号化前のテンプレート、`PORT` / `ENVIRONMENT` / 将来の機密情報プレースホルダー）
- [x] `.gitignore` を修正（復号後の実ファイル `.env` のみ除外し、暗号化予定の `.env.enc` は Git 管理対象にする）
- [ ] `age-keygen` でチーム用鍵ペアを生成し、`.sops.yaml` の `age:` にプレースホルダーではなく実際の公開鍵を設定
- [ ] `sops -e -i .env.enc` で暗号化してからコミット（現状はまだ平文のため未コミット）
- [ ] GCP プロジェクト作成後、staging/production 用シークレットを Secret Manager に登録

---

## フェーズ 2: Blue-Green デプロイ

### Task 2.1: Cloud Run デプロイの基礎スクリプト
- [ ] `scripts/deploy-common.sh` を作成
  - [ ] GCP プロジェクト ID のバリデーション
  - [ ] Docker イメージビルド関数
  - [ ] Artifact Registry へのプッシュ関数
  - [ ] ロギング・エラーハンドリング

### Task 2.2: Blue-Green デプロイスクリプト実装
- [ ] `scripts/deploy-blue-green.sh` を作成
  - [ ] `--version` で新バージョン指定
  - [ ] Blue（現在）と Green（新規）の識別
  - [ ] Green 環境で新バージョンをデプロイ
  - [ ] ヘルスチェックが成功するまで待機
  - [ ] トラフィック切り替え（Cloud Run のトラフィック分割設定）
  - [ ] ロールバック機能
  - [ ] デプロイログ出力

### Task 2.3: Blue-Green デプロイのテスト
- [ ] GCP 環境でサービス作成（マニュアル確認用）
- [ ] スクリプトでの初回デプロイテスト（v0.1.0）
- [ ] バージョンアップ → Blue-Green デプロイ（v0.2.0）
- [ ] ヘルスチェック確認
- [ ] トラフィック切り替え動作確認
- [ ] 実際のリクエストで新バージョン動作確認

---

## フェーズ 3: カナリアリリース

### Task 3.1: カナリアリリーススクリプト実装
- [ ] `scripts/deploy-canary.sh` を作成
  - [ ] `--version` で新バージョン指定
  - [ ] `--percentage` でトラフィック割合指定（デフォルト 10%）
  - [ ] 新バージョンをデプロイ
  - [ ] Cloud Run のトラフィック分割で段階的配信
  - [ ] 進捗ログ出力
  - [ ] ロールバック機能

### Task 3.2: カナリアリリースの段階的ロールアウト
- [ ] `scripts/promote-canary.sh` を作成
  - [ ] トラフィック割合を段階的に増加
  - [ ] デフォルト段階: 10% → 25% → 50% → 100%
  - [ ] 各段階で確認時間を設ける
  - [ ] メトリクスチェック（エラーレート等の簡易確認）

### Task 3.3: カナリアリリースのテスト
- [ ] v0.2.0 でカナリアリリース開始（10%）
- [ ] トラフィック確認
- [ ] 段階的昇格テスト（25% → 50% → 100%）
- [ ] ロールバック動作確認

---

## フェーズ 4: 監視・ロールバック・運用スクリプト

### Task 4.1: 監視スクリプト
- [ ] `scripts/monitor-deployment.sh` を作成
  - [ ] Cloud Run の現在のバージョン情報取得
  - [ ] トラフィック分割状況表示
  - [ ] デプロイ状態確認
  - [ ] ヘルスチェック実行

### Task 4.2: ロールバックスクリプト
- [ ] `scripts/rollback.sh` を作成
  - [ ] 前のバージョンを確認
  - [ ] ワンコマンドでロールバック
  - [ ] 進行状況ログ出力

### Task 4.3: デプロイ状況確認スクリプト
- [ ] `scripts/deployment-status.sh` を作成
  - [ ] 現在の本番バージョン表示
  - [ ] トラフィック分割状況表示
  - [ ] 過去のデプロイ履歴表示

---

## フェーズ 5: ドキュメント・テスト

### Task 5.1: デプロイメント操作マニュアル作成
- [ ] `DEPLOYMENT.md` を作成
  - [ ] Blue-Green デプロイの手順
  - [ ] カナリアリリースの手順
  - [ ] ロールバック手順
  - [ ] トラブルシューティング

### Task 5.2: スクリプトのテスト と ドライラン
- [ ] 全スクリプトのドライラン（エラーハンドリング確認）
- [ ] GCP 環境でのエンドツーエンドテスト
  - [ ] v0.1.0 デプロイ
  - [ ] v0.2.0 への Blue-Green デプロイ
  - [ ] v0.3.0 へのカナリアリリース
  - [ ] 段階的昇格
  - [ ] ロールバック

### Task 5.3: CI/CD パイプライン（オプション）
- [ ] GitHub Actions ワークフロー作成（デプロイ自動化）
- [ ] タグプッシュで自動ビルド・デプロイ

---

## フェーズ 6: 応用・最適化

### Task 6.1: メトリクス監視スクリプト
- [ ] `scripts/check-metrics.sh` を作成
  - [ ] Cloud Monitoring からのエラーレート確認
  - [ ] レスポンスタイム確認
  - [ ] カナリアリリース判断の自動化

### Task 6.2: Istio/Service Mesh（オプション）
- [ ] Kubernetes マニフェスト作成（参考用）
- [ ] VirtualService / DestinationRule でトラフィック管理

---

## 進捗トラッキング

| フェーズ | 内容 | 進捗 |
|---------|------|------|
| 1 | 基本セットアップ | ⬜️ |
| 2 | Blue-Green デプロイ | ⬜️ |
| 3 | カナリアリリース | ⬜️ |
| 4 | 監視・ロールバック | ⬜️ |
| 5 | ドキュメント・テスト | ⬜️ |
| 6 | 応用・最適化 | ⬜️ |

---

## 学習ポイント

- **Blue-Green デプロイ**: ゼロダウンタイムと即座のロールバック
- **カナリアリリース**: リスク最小化とリアルタイム検証
- **バージョン管理の一貫性**: Git tag を単一の真実の源とし、ビルド時に Docker イメージへ焼き込む（[ADR-0001](docs/adr/0001-version-management-approach.md)）
- **スクリプト設計**: 冪等性、エラーハンドリング、ドライラン対応
- **GCP Cloud Run**: マネージドコンテナプラットフォームの活用
