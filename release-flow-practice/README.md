# Release Flow Practice

リリース戦略とバージョン管理を実践的に学ぶプロジェクト。Blue-greenデプロイ、カナリアリリース、Docker/package.jsonのバージョン管理を GCP Cloud Run で実装・練習します。

## 概要

このプロジェクトは以下のデプロイメント戦略を実装して理解することを目的としています：

- **Blue-Green デプロイ**: 本番環境と同一の環境を並行実行して、ゼロダウンタイムでスイッチオーバー
- **カナリアリリース**: 新バージョンを段階的にロールアウトしてリスク最小化
- **バージョン管理**: Docker イメージと package.json の統一的なバージョン戦略

## 技術スタック

- **API フレームワーク**: [Hono](https://hono.dev/)（軽量な Web フレームワーク）
- **ランタイム**: Node.js
- **コンテナ化**: Docker
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

- Node.js 18+
- Docker
- gcloud CLI（GCP プロジェクト設定済み）

### ローカルセットアップ

```bash
# プロジェクトに移動
cd api

# 依存関係をインストール
npm install

# ローカルで実行
npm run dev
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

### package.json と Docker イメージの同期

```json
{
  "version": "1.2.0",
  "name": "release-flow-api"
}
```

```dockerfile
FROM node:18.19.0-alpine
LABEL version="1.2.0"
```

バージョン更新フロー：
1. `package.json` の version を更新
2. Docker イメージをビルド（同じバージョンでタグ付け）
3. Git タグを作成（`v1.2.0`）
4. Cloud Run にデプロイ

### Semantic Versioning

`MAJOR.MINOR.PATCH` の形式を採用：
- **MAJOR**: 互換性を破る変更
- **MINOR**: 互換性を保つ機能追加
- **PATCH**: バグ修正

## ローカルテスト

### 開発環境での実行

```bash
cd api
npm run dev
```

API が `http://localhost:8000` で起動します。

### API の確認

```bash
curl http://localhost:8000/
curl http://localhost:8000/health
```

### Docker イメージのビルド

```bash
cd api
docker build -t release-flow-api:v1.0.0 .
docker run -p 8000:8000 release-flow-api:v1.0.0
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
