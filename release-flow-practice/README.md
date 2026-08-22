# Release Flow Practice

リリース戦略とバージョン管理を実践的に学ぶプロジェクト。Blue-Green デプロイ、カナリアリリース、バージョン管理を GCP Cloud Run で実装・練習します。

## 概要

このプロジェクトは以下のデプロイメント戦略を実装して理解することを目的としています：

- **Blue-Green デプロイ**: 本番環境と同一の環境を並行実行して、ゼロダウンタイムでスイッチオーバー
- **カナリアリリース**: 新バージョンを段階的にロールアウトしてリスク最小化
- **バージョン管理**: Git tag を単一の真実の源とし、ビルド時に Docker イメージへ焼き込む戦略

詳細な設計方針は [ADR-0001: バージョン情報の管理元と実行時への伝播方式](docs/adr/0001-version-management-approach.md) を参照。

## 技術スタック

- **API フレームワーク**: [Hono](https://hono.dev/)（軽量な Web フレームワーク）
- **ランタイム**: [Bun](https://bun.sh/)（JavaScript ランタイム）
- **コンテナ化**: Docker（`oven/bun:1.4.0-alpine`）
- **デプロイメント先**: GCP Cloud Run
- **バージョン管理**: Git タグ + Semantic Versioning

## プロジェクト構成

```
release-flow-practice/
├── api/                    # Hono アプリケーション
│   ├── src/
│   │   └── index.ts
│   ├── Dockerfile
│   ├── package.json
│   └── tsconfig.json
├── scripts/                # デプロイメント・管理スクリプト
│   ├── deploy-blue-green.sh
│   ├── deploy-canary.sh
│   └── version-check.sh
├── k8s/                    # Kubernetes マニフェスト（参考）
└── README.md
```

## セットアップ

### 前提条件

- Bun
- Docker
- [mise](https://mise.jdx.dev/)（`sops` / `age` / `gcloud` のバージョン管理用。ランタイムの管理には使わない）

### 機密情報のセットアップ（新しい PC で clone した場合）

機密情報を含む環境変数は SOPS + age で暗号化して `.env.enc` として Git 管理している（[ADR-0002](docs/adr/0002-secret-management-strategy.md) 参照、仕組みの詳細は [docs/sops-and-age.md](docs/sops-and-age.md)）。復号には age の秘密鍵が必要で、これは Git に含まれていないため別途チームから受け取る必要がある。

```bash
# 1. リポジトリを clone
git clone <repository-url>
cd release-flow-practice

# 2. sops / age / gcloud をインストール（.mise.toml でバージョン固定済み）
mise install

# 3. チームメンバーから age の秘密鍵（key.txt）を安全なチャネル
#    （1Password、Slack DM 等）で受け取り、プロジェクトルートに配置する
#    ※ key.txt は .gitignore 対象。誰かに渡す/受け取る以外の方法で
#      入手することはできない

# 4. .env.enc を復号して .env を生成
mise run env:decrypt
```

これで `.env` が生成され、`bun run dev` や `mise run build` から利用できる状態になる。

### ローカルセットアップ

```bash
# プロジェクトに移動
cd api

# 依存関係をインストール
bun install

# ローカルで実行（デフォルトで http://localhost:4000）
bun run dev

# ポートを変更する場合
PORT=5000 bun run dev
```

## デプロイメント戦略

### 1. Blue-Green デプロイ

新しいバージョンを別環境で起動してテスト後、トラフィックを一括切り替え：

```bash
./scripts/deploy-blue-green.sh v1.2.0
```

**メリット**:
- ゼロダウンタイム
- ロールバックが即座
- テスト期間を確保可能

**デメリット**:
- 実行環境が2倍必要
- データベース接続の管理が必要

### 2. カナリアリリース

新バージョンを一部トラフィックで実行しながら段階的にロールアウト：

```bash
./scripts/deploy-canary.sh v1.2.0 --percentage 10
```

**メリット**:
- 実装環境の効率利用
- 本番環境でのリスク最小化
- ユーザー影響を限定的に検証

**デメリット**:
- ロジックがやや複雑
- 監視が重要

## バージョン管理戦略

Git tag を単一の真実の源とし、ビルド時に Docker イメージへ `VERSION` / `GIT_SHA` / `BUILD_TIME` を焼き込みます。詳細は [ADR-0001](docs/adr/0001-version-management-approach.md) を参照。

```dockerfile
ARG VERSION=dev
ARG GIT_SHA=unknown
ARG BUILD_TIME=unknown

ENV APP_VERSION=$VERSION \
    APP_GIT_SHA=$GIT_SHA \
    APP_BUILD_TIME=$BUILD_TIME
```

バージョン更新フロー：
1. Git タグを作成（`v1.2.0`）
2. `scripts/build.sh` で Docker イメージをビルド（タグから VERSION を注入）
3. Cloud Run にデプロイ

### Semantic Versioning

`MAJOR.MINOR.PATCH` の形式を採用：
- **MAJOR**: 互換性を破る変更
- **MINOR**: 互換性を保つ機能追加
- **PATCH**: バグ修正

## ローカルテスト

### 開発環境での実行

```bash
cd api
bun run dev
```

API が `http://localhost:4000` で起動します。

### API の確認

```bash
curl http://localhost:4000/
curl http://localhost:4000/health
curl http://localhost:4000/version
```

### Docker イメージのビルド

`VERSION` は `.env.enc`（SOPS + age で暗号化して Git 管理、[ADR-0002](docs/adr/0002-secret-management-strategy.md) 参照）に保持し、復号した `.env` から `mise run build` タスクが読み込みます（Git SHA とビルド時刻は自動取得）。詳しい暗号化の仕組みは [docs/sops-and-age.md](docs/sops-and-age.md) を参照。

miseの`sops` / `age` / `gcloud`と各タスクの定義は`.mise.toml`にある。

```bash
# 初回セットアップ（チームで共有された age 秘密鍵 key.txt を配置済みの前提）
mise run env:decrypt   # .env.enc を復号して .env を生成

# ビルド（プロジェクトルートから実行、.env の VERSION を使う）
mise run build

# .env.enc の内容を変更した場合は再暗号化してからコミット
mise run env:encrypt
```

内部的には以下と同等の処理を行います：

```bash
cd api
docker build \
  --build-arg VERSION=v0.1.0 \
  --build-arg GIT_SHA=$(git rev-parse --short HEAD) \
  --build-arg BUILD_TIME=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
  -t release-flow-api:v0.1.0 .
docker run -p 4000:4000 release-flow-api:v0.1.0
```

## GCP Cloud Run へのデプロイ

### 前提設定

```bash
# GCP プロジェクトを設定
gcloud config set project YOUR_PROJECT_ID

# Docker イメージを Artifact Registry へプッシュ
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/release-flow-api:v1.0.0
```

### デプロイコマンド

```bash
gcloud run deploy release-flow-api \
  --image gcr.io/YOUR_PROJECT_ID/release-flow-api:v1.0.0 \
  --region asia-northeast1 \
  --platform managed
```

## 監視とロールバック

### Cloud Run でのバージョン確認

```bash
gcloud run services describe release-flow-api --region asia-northeast1
```

### ロールバック手順

```bash
# 前のバージョンに戻す
gcloud run deploy release-flow-api \
  --image gcr.io/YOUR_PROJECT_ID/release-flow-api:v1.0.0 \
  --region asia-northeast1
```

## 次のステップ

- [ ] Hono アプリケーション実装
- [ ] Docker イメージの作成
- [ ] Blue-Green デプロイスクリプト実装
- [ ] カナリアリリーススクリプト実装
- [ ] Cloud Run でのデプロイテスト
- [ ] 監視・アラート設定
- [ ] カナリアリリースの自動化（Istio など）

## 参考資料

- [Hono 公式ドキュメント](https://hono.dev/)
- [GCP Cloud Run ドキュメント](https://cloud.google.com/run/docs)
- [Semantic Versioning](https://semver.org/lang/ja/)
- [Blue-Green Deployments](https://martinfowler.com/bliki/BlueGreenDeployment.html)

## ライセンス

MIT
