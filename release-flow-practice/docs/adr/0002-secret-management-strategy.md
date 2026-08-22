# ADR-0002: 機密情報を含む環境変数の管理戦略

- **ステータス**: Accepted
- **決定日**: 2026-08-21
- **決定者**: （記入）
- **関連**: [ADR-0001](0001-version-management-approach.md) バージョン情報の管理元と実行時への伝播方式

---

## コンテキスト

[ADR-0001](0001-version-management-approach.md) では `VERSION` / `GIT_SHA` / `BUILD_TIME` のような非機密のビルド属性を環境変数として扱う方針を決めた。一方、今後 `DATABASE_URL` や外部 API キーのような機密情報を含む環境変数を扱う必要が生じる。

要件は次の通り：

- ローカル開発では、チームメンバー間で環境変数をシンプルに共有・バージョン管理したい
- Cloud Run（staging / production）にデプロイする機密情報は、Git の差分やコミット履歴に一切残したくない
- ローカル開発者全員に GCP プロジェクトの IAM 権限やクラウド認証を要求せず、開発を始められるようにしたい

当初は SOPS + GCP KMS に環境（local / staging / production）を問わず統一する方針を検討したが、ローカル開発者にも GCP KMS への復号権限（IAM）が必要になり、「クラウド認証なしですぐに開発を始められる」という要件と衝突することがわかった。

## 決定要因

1. ローカル開発のセットアップ障壁を最小化する（GCP 認証なしで開発を始められる）
2. Cloud Run にデプロイする本番・staging の機密情報は、暗号化した状態であっても Git 履歴に残さない
3. Cloud Run のネイティブなシークレット機能（ローテーション、バージョニング、IAM 監査ログ）を本番運用で最大限活用する
4. 環境ごとに鍵管理の手段を使い分けても、開発者が迷わない程度にシンプルであること

---

## 決定

**ローカル開発と Cloud Run 環境で、機密情報の管理方式を分ける。**

| 環境 | 管理方式 | 値の置き場所 |
|---|---|---|
| ローカル開発 | SOPS + age | `.env.enc`（暗号化して Git 管理） |
| staging / production（Cloud Run） | GCP Secret Manager | Secret Manager のみ（Git には一切値を置かない） |

### ローカル開発: SOPS + age

age は GCP や KMS に依存しない軽量な鍵ペア方式。チーム内で秘密鍵を共有するだけで、誰でも `.env.enc` を復号して開発を始められる。

sops / age / gcloud は `.mise.toml` でバージョンを固定し、`mise install` でセットアップする（Bun ランタイムの管理には使わない）。

```bash
# 開発チームの age 鍵ペアを生成（一度だけ）
mise exec -- age-keygen -o key.txt
# Public key: age1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# .sops.yaml に公開鍵を登録
```

```yaml
# .sops.yaml
creation_rules:
  - path_regex: \.env\.enc$
    age: age1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

暗号化・復号は `.mise.toml` に定義したタスク経由で行う（`.env.enc` という複合拡張子は SOPS の自動フォーマット判定が効かないため、タスク内で `--input-type`/`--output-type dotenv` を明示している）。

```bash
# 暗号化して Git 管理
mise run env:encrypt
git add .env.enc

# 復号してローカルで使う（SOPS_AGE_KEY_FILE はタスク内で ./key.txt を指定済み）
mise run env:decrypt
```

秘密鍵ファイル（`key.txt`）は Git に含めず、チームで安全なチャネル（1Password、Slack DM 等）を通じて共有する。

### Cloud Run（staging / production）: GCP Secret Manager

本番・staging の機密情報は Git に一切置かず、Secret Manager に直接登録し、Cloud Run のネイティブ統合で環境変数として注入する。

```bash
# シークレットの登録
echo -n "postgres://prod-user:***@host:5432/db" | \
  gcloud secrets create database-url-production --data-file=-

# バージョン追加（更新時）
echo -n "postgres://prod-user:***@host:5432/db" | \
  gcloud secrets versions add database-url-production --data-file=-
```

```bash
# Cloud Run デプロイ時に注入
gcloud run deploy release-flow-api \
  --image gcr.io/PROJECT_ID/release-flow-api:v1.0.0 \
  --set-secrets=DATABASE_URL=database-url-production:latest,API_KEY=api-key-production:latest
```

シークレットへのアクセスは Cloud Run サービスアカウントに対する `roles/secretmanager.secretAccessor` の IAM 権限で制御する。IaC（Terraform 等）でシークレット**の存在**や IAM バインディングは Git 管理するが、シークレットの**値**自体はコードに書かない。

**検討した代替案：**

- **SOPS + GCP KMS に統一**（local / staging / production すべて）: ローカル開発者にも GCP IAM の KMS 復号権限が必要になり、クラウド認証なしで開発を始めたいという要件と衝突するため却下。
- **GCP Secret Manager に統一**（local も含む）: ローカル開発のたびにクラウド接続・認証が必要になり非効率。ローカルではネットワーク切断時に開発できない問題もあるため却下。
- **dotenvx**: 導入は簡単だが、鍵管理の考え方は age とほぼ同等でありながら GCP エコシステムとの親和性がない。本番側で Secret Manager を使う以上、ローカル側だけ別ツールを増やすメリットが薄いため却下。
- **git-crypt**: リポジトリ単位でしか暗号化範囲を制御できず、local 用ファイルだけを対象にする柔軟性がない。SOPS + age の方がファイル単位で制御しやすいため却下。

## 結果

**利点：**

- ローカル開発者は GCP プロジェクトへのアクセス権がなくても、共有された age 鍵さえあれば開発を始められる
- 本番・staging の実際の機密値は Git の履歴に一度も現れない（暗号文としてもコミットされない）
- Cloud Run のネイティブなシークレット機能（バージョニング、ローテーション、IAM 監査ログ）を本番運用でフル活用できる
- ローカルはシンプルな age 鍵、本番は堅牢な Secret Manager と、リスクに応じて手段を使い分けられる

**欠点：**

- 環境によって値の取得経路が異なる（ローカルはファイル復号、本番は Secret Manager 経由の環境変数）という非対称性が生まれる
- age の秘密鍵ファイルの配布・ローテーション運用は、KMS のような IAM 統合がなく手動管理になる
- ローカルの `.env.enc` にある値（開発用のダミー値等）と本番 Secret Manager の値は完全に別物のため、「ローカルでは動くが本番の Secret 登録を忘れている」という設定漏れのリスクは残る（デプロイ前のチェックリストや `deployment-status.sh` 等での検証でカバーする）

**中立的な影響：**

- `.sops.yaml` は age 鍵のみを対象とし、`.env.enc` にのみ適用する
- `.gitignore` は復号後の実ファイルである `.env` のみを除外し、暗号化済みの `.env.enc` は Git 管理対象とする
- Secret Manager 側のシークレット作成・IAM 権限付与は Terraform 等の IaC で宣言的に管理する（値そのものは含めない）
- Cloud Run デプロイスクリプト（`scripts/deploy-*.sh`）に `--set-secrets` オプションを組み込む必要がある

---

## 参考

- [SOPS (getsops/sops)](https://github.com/getsops/sops)
- [age](https://github.com/FiloSottile/age)
- [Cloud RunからSecret Managerのシークレットにアクセスする](https://blog.g-gen.co.jp/entry/secret-manager-with-cloud-run)
- [GCP Secret Manager 実践ガイド](https://zenn.dev/correlate_dev/articles/gcp-secret-manager)
