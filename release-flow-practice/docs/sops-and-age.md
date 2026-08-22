# SOPS + age の仕組み

このプロジェクトでは、ローカル開発用の機密情報を管理するために SOPS + age を採用している（[ADR-0002](adr/0002-secret-management-strategy.md) 参照）。ここではその仕組みと、GCP KMS をバックエンドにした場合との違いを解説する。

## SOPSの役割：暗号化の「フォーマット層」

SOPS（Secrets OPerationS）自体は暗号アルゴリズムを実装していない。SOPSがやっているのは：

- YAML/JSON/ENV などの構造を理解し、**value だけを暗号化して key 名は平文で残す**
- 実際の暗号鍵の管理（鍵ペアの生成・保管・アクセス制御）は age・GPG・AWS KMS・GCP KMS など**外部のバックエンドに委任する**

このプロジェクトでは、そのバックエンドとして **age** を選んだ。

## ageの中身：モダンな公開鍵暗号

age は `ssh-keygen` の暗号版のようなツールで、GPG の後継として作られた。

```bash
age-keygen -o key.txt
```

これで生成されるのは：
- **公開鍵（Recipient）**: `age1xxxxxxxxxxxxxxxxxxxxxxxxxxxx...` — 誰かに「これで暗号化して送って」と渡す鍵
- **秘密鍵（Identity）**: `AGE-SECRET-KEY-1xxxxxxx...` — 復号できる唯一の鍵、絶対に共有しない

内部的には **X25519**（楕円曲線鍵交換）で鍵合意を行い、実際のデータは **ChaCha20-Poly1305**（対称暗号）で暗号化する。GPG のような「Web of Trust」や鍵サーバーが不要で、鍵の文字列も短くシンプル。

## SOPS + age の実際の流れ（エンベロープ暗号化）

```
┌─────────────────────────────────────────────────────────┐
│ 1. SOPSがランダムな「データキー」(32バイト)を生成          │
│                                                           │
│ 2. .env.enc の中身の value だけをそのデータキーで暗号化 │
│    PORT=4000                    → そのまま（keyは平文）  │
│    DATABASE_URL=postgres://...  → ENC[AES256_GCM,...]    │
│                                                           │
│ 3. データキー自体を age の公開鍵で暗号化してラップし、    │
│    ファイルのメタデータ部分に埋め込む                     │
└─────────────────────────────────────────────────────────┘
```

復号時は逆に：
1. ファイルに埋め込まれた「age で暗号化されたデータキー」を、手元の**秘密鍵**（`key.txt`）で復号
2. 復元したデータキーで、各 value を復号

```bash
# 暗号化
sops -e -i .env.enc

# 復号（秘密鍵の場所を指定）
SOPS_AGE_KEY_FILE=./key.txt sops -d .env.enc > .env
```

## なぜこの組み合わせが便利か

| 特性 | 効果 |
|---|---|
| **key名は平文のまま** | Git の diff で「どの設定が追加/変更されたか」が PR でレビューできる |
| **複数recipient対応** | `.sops.yaml` に複数の age 公開鍵を並べれば、チームメンバー全員がそれぞれの秘密鍵で復号できる（同じデータキーが各公開鍵で個別にラップされる） |
| **KMS不要** | GCP や AWS のアカウントがなくても、`age-keygen` 一発で鍵ペアが作れる |
| **鍵が軽量** | X25519 ベースなので GPG より鍵が短く扱いやすい |

## 実際に暗号化した`.env.enc`のイメージ

```
PORT=4000
ENVIRONMENT=local
DATABASE_URL=ENC[AES256_GCM,data:Cg8xk2...,iv:...,tag:...,type:str]
API_KEY=ENC[AES256_GCM,data:Xy2p9a...,iv:...,tag:...,type:str]
sops_age__list_0__map_enc=age1xxxxx...(暗号化されたデータキー)...
sops_mac=ENC[...]  # ファイル全体の改ざん検知用MAC
```

`PORT` や `ENVIRONMENT` のような非機密の値も SOPS は同じファイル内で扱えるが、暗号化するのは value 全部（key 名だけが平文）。

---

## GCP KMS をバックエンドにした場合の違い

age との一番の違いは、**「秘密鍵というモノがローカルに存在しない」**こと。暗号化・復号の演算自体を GCP のサーバー側で行い、SOPS は API を呼び出すだけになる。

```
【age の場合】暗号化・復号ともにローカルで完結
┌──────────────────────────────────────────┐
│ SOPS がデータキーを生成                    │
│   ↓ ローカルで X25519 + ChaCha20-Poly1305 │
│ age公開鍵でデータキーをラップ              │
│   ↓                                       │
│ ファイルに埋め込んで保存（ネット不要）      │
└──────────────────────────────────────────┘

【GCP KMS の場合】暗号化・復号を GCP に委任
┌──────────────────────────────────────────┐
│ SOPS がデータキーを生成                    │
│   ↓ データキー(平文)を GCP KMS API に送信 │
│ GCP KMS がサーバー側で暗号化               │
│   ↓ 暗号化されたデータキーが返ってくる     │
│ ファイルに埋め込んで保存（要ネット接続）    │
└──────────────────────────────────────────┘
```

復号時も同様に、暗号化されたデータキーを KMS の `Decrypt` API に送り、GCP 側で復号された平文データキーを受け取る。**KMS キーの実体（鍵材料）は一度も GCP の外に出ない。**

### `.sops.yaml`の書き方の違い

```yaml
# age（今回採用した方式）
creation_rules:
  - path_regex: \.env\.enc$
    age: age1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# GCP KMS（最初に検討した方式）
creation_rules:
  - path_regex: \.env\.production$
    gcp_kms: projects/PROJECT_ID/locations/global/keyRings/release-flow/cryptoKeys/prod-key
```

### 比較表

| 項目 | age | GCP KMS |
|---|---|---|
| **鍵の実体** | ローカルの`key.txt`ファイル | GCP 内部（外に出ない） |
| **アクセス制御** | 秘密鍵ファイルを持っているか否か | IAM ロール（`roles/cloudkms.cryptoKeyDecrypter`等） |
| **権限の剥奪** | 鍵を持つ全員で再暗号化が必要（面倒） | IAM ロールを外すだけで即座に無効化 |
| **監査ログ** | 残らない（誰が復号したか追跡不可） | Cloud Audit Logs に `Decrypt` 呼び出しが記録される |
| **オフライン利用** | 可能（ネット不要） | 不可（GCP へのネットワーク接続と ADC 認証が必須） |
| **セットアップ** | `age-keygen` だけ、クラウド不要 | GCP プロジェクト・KMS キーリング作成が必要 |
| **鍵ローテーション** | 手動（新しい鍵で全ファイル再暗号化） | KMS 側でキーバージョンを自動ローテーション可能 |

### なぜ今回はageを選んだか（振り返り）

[ADR-0002](adr/0002-secret-management-strategy.md) で決めた通り、**ローカル開発者全員に GCP IAM 権限を要求したくない**という理由で age を選んだ。もし production/staging の機密情報も Git 管理する設計だったら、監査ログや IAM による細かい権限剥奪ができる KMS の方が適していたはず（そのため、production/staging 側は SOPS ではなく直接 **GCP Secret Manager** を使う設計にしている）。

つまり「SOPS でどのバックエンドを使うか」という選択は、**「鍵をローカルファイルとして持ち回るか、クラウドのアクセス制御に一元化するか」**というトレードオフである。

## 参考

- [Age | SOPS: Secrets OPerationS](https://getsops.io/docs/usage/identities/age/)
- [Secrets management with SOPS and age](https://aorith.github.io/posts/secrets-sops/)
- [age vs GPG: Modern File Encryption](https://sumguy.com/age-vs-gpg-modern-encryption/)
