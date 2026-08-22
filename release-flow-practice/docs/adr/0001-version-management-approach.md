# ADR-0001: バージョン情報の管理元と実行時への伝播方式

- **ステータス**: Accepted
- **決定日**: 2026-08-21
- **決定者**: （記入）
- **関連**: ADR-0002 デプロイ戦略（Blue-Green / Canary）

---

## コンテキスト

コンテナ化した API をマネージドコンテナ基盤（Cloud Run / ECS）にデプロイしている。バージョンを表現しうる場所が複数存在する。

- Git タグ
- `package.json` の `version` フィールド
- コンテナイメージのタグ
- デプロイ時の環境変数

これらが個別に管理されると、以下の問題が発生する。

- **障害対応時にコードが特定できない。** 稼働中のイメージからコミットを逆引きできず、原因調査の初手で時間を失う。
- **ロールバック先が信頼できない。** コンテナイメージのタグは可変であり、同じタグへの再 push で内容が入れ替わりうる。真に不変な識別子は sha256 digest のみである。
- **手動更新の同期漏れ。** `package.json` を手で更新して Git タグを打ち忘れる、という乖離が起きる。

なお本サービスは npm パッケージとして公開しないため、`package.json` の `version` は外部への公開契約ではない。

## 決定要因

1. 「稼働中のバイナリ」から「元のコミット」へ一意に辿れること
2. バージョンを決定する主体が単一であること（人手による同期を要求しない）
3. ステージング環境で検証したアーティファクトと同一のものを本番へ昇格できること
4. デプロイ設定の変更で値が矛盾しうる経路を構造的に排除すること

---

## 決定

### 1. バージョンの管理元は Git タグとする

Conventional Commits に基づき semantic-release がバージョンを算出し、Git タグを作成する。`package.json` の `version` はその派生物として自動更新され、**人手では編集しない**。

### 2. イメージには 2 系統のタグを付与する

| タグ | 用途 |
|---|---|
| `v1.2.3` | 人間が読むための識別子 |
| `<short-sha>` | コミットへの一意な逆引き |

`latest` は本番デプロイに使用しない。

### 3. デプロイ対象は digest で pin する

IaC およびデプロイ定義では `image@sha256:...` を参照する。タグは可変であるため、ロールバック先の同一性を保証できない。

### 4. バージョン情報はビルド時にイメージへ焼き込む

**イメージの属性**（version, Git SHA, ビルド時刻）はビルド引数から環境変数および OCI ラベルへ焼き込む。**デプロイの属性**（環境名, ログレベル, 接続先）はデプロイ時の環境変数で注入する。

判断基準は「同一の digest が複数の値を取りうるか」。取りうるなら焼き込まない。

### 5. `/version` と `/health` は分離する

- `/health` — 監視用。外部依存を持たず即時応答する。レスポンス契約を変更しない。
- `/version` — 情報提供用。稼働バージョンの確認およびデプロイ後の検証に用いる。

ヘルスチェック用パスは末尾を `z` にしない（`/healthz` は避け `/health` とする）。Cloud Run の既知の問題として、末尾が `z` のパスは予約済みパターンと競合する可能性があるため非推奨とされている。デプロイ先を Cloud Run に限定していなくても、将来の移行や共存を妨げないよう本プロジェクト全体で `/health` に統一する。

参照: [Cloud Run の既知の問題](https://docs.cloud.google.com/run/docs/known-issues?hl=ja)

---

## 実装

### Dockerfile

変わりやすい `ARG` / `ENV` は**最終ステージの末尾**に配置する。前段に置くと、コミットごとに以降のレイヤーキャッシュがすべて無効化される。

```dockerfile
FROM node:22-slim
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules

# 変動する値は最後に置く（レイヤーキャッシュ保護）
ARG VERSION=dev
ARG GIT_SHA=unknown
ARG BUILD_TIME=unknown

ENV APP_VERSION=$VERSION \
    APP_GIT_SHA=$GIT_SHA \
    APP_BUILD_TIME=$BUILD_TIME

LABEL org.opencontainers.image.version=$VERSION \
      org.opencontainers.image.revision=$GIT_SHA

CMD ["node", "dist/index.js"]
```

`ENV` および `ARG` の値は `docker history` から参照可能なため、**シークレットをこの経路で渡さない**。

### CI（Cloud Build の例）

```yaml
- name: gcr.io/cloud-builders/docker
  args:
    - build
    - --build-arg=VERSION=${TAG_NAME}
    - --build-arg=GIT_SHA=${SHORT_SHA}
    - --build-arg=BUILD_TIME=${_BUILD_TIME}
    - -t=${_IMAGE}:${TAG_NAME}
    - -t=${_IMAGE}:${SHORT_SHA}
    - .
```

トリガーは**タグ push** に設定する。ブランチ push トリガーでは `TAG_NAME` が空になる。

semantic-release によるタグ作成とイメージビルドは**別ジョブに分離**する。同一ジョブ内で連続実行すると、タグが未作成の状態でビルドが走りうる。

### エンドポイント

```ts
app.get('/version', (_req, res) => {
  res.json({
    version:   process.env.APP_VERSION    ?? 'dev',      // ビルド時に焼き込み
    gitSha:    process.env.APP_GIT_SHA    ?? 'unknown',  // ビルド時に焼き込み
    buildTime: process.env.APP_BUILD_TIME ?? 'unknown',  // ビルド時に焼き込み
    env:       process.env.ENVIRONMENT    ?? 'local',    // デプロイ時に注入
    revision:  process.env.K_REVISION     ?? 'local',    // プラットフォームが注入
  });
});
```

`K_REVISION` は Cloud Run が自動注入する。ECS の場合は同等の情報をタスクメタデータエンドポイントから取得する。

ローカル開発ではすべてフォールバック値になり、`docker build` を経ずに起動できる。

---

## 影響

### 得られるもの

- 稼働中のイメージから 1 回のリクエストでコミットを特定できる
- ロールバック先が digest で確定するため、切り戻し対象の同一性が保証される
- バージョン決定が完全自動化され、手動同期の失敗経路が消える
- Canary 実行中に `/version` を反復取得することで、トラフィック分割の実挙動をアプリ側から観測できる
- 同一アーティファクトの環境間昇格が可能

### 支払うコスト

- Conventional Commits の遵守がチーム全体に要求される。lint による強制が必要
- バージョン文字列の修正に再ビルドが必要となる（意図した制約）
- Git SHA が無認証で公開される。許容できない場合は `/version` の一部項目を内部向けに限定するが、障害対応の初動が遅くなるトレードオフを伴う
- タグ push トリガーへの CI 移行に伴い、既存パイプラインの改修が必要

---

## 検討した代替案

### A. `package.json` を管理元とし、実行時に import する

**却下。** マルチステージビルドで `package.json` を最終イメージへコピーしていない場合や、バンドラー（esbuild / tsup）使用時に解決が壊れる。加えて Git SHA を保持できず、コミットへの逆引きができない。

### B. 実行時に `git describe` で取得する

**却下。** 本番イメージに `.git` ディレクトリは含まれない。含めた場合はイメージ肥大とリポジトリ履歴の同梱という別の問題が生じる。

### C. バージョンをデプロイ時の環境変数で注入する

**却下。** 同一 digest が環境ごとに異なるバージョンを名乗りうるため、digest → version の対応が 1:N に壊れる。

デプロイ済みの組み合わせ自体は不変である（Cloud Run のリビジョン、ECS のタスク定義リビジョン）が、真実の源が「ビルドした CI」と「デプロイ設定を書いた IaC」の 2 箇所に分かれ、両者の同期責任が発生する。`/version` の目的が「稼働コードの一意な特定」である以上、値が誤りうる経路を残すことは目的と矛盾する。

### D. `/healthz` にバージョン情報を含める

**却下。** 監視系が高頻度で叩くエンドポイントのレスポンス契約に可変情報が混入する。将来の項目追加が監視設定の変更を誘発する。

---

## 参考

- Semantic Versioning 2.0.0
- OCI Image Spec — Annotations（`org.opencontainers.image.*`）
- Cloud Run — コンテナ ランタイムの契約（組み込み環境変数）
- [Cloud Run の既知の問題](https://docs.cloud.google.com/run/docs/known-issues?hl=ja) — 末尾が `z` のパスは予約済みのため非推奨
