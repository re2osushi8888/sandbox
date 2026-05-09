# hs-atcoder

Haskell AtCoder 環境。

## セットアップ

```bash
nix develop  # または direnv を使っていれば自動で入る
```

## 使えるコマンド

| コマンド | 内容 |
|---------|------|
| `hfmt <file>` | fourmolu でフォーマット |
| `run <file>` | runghc で実行 |
| `acc` | AtCoder CLI |
| `oj` | Online Judge Tools |

## 典型的な作業フロー

```bash
# コンテストの雛形作成
acc new abc400
cd abc400/a

# サンプルケースをダウンロード
oj download https://atcoder.jp/contests/abc400/tasks/abc400_a

# コードを書く...

# テスト
oj test -c "runghc main.hs"

# 提出
acc submit main.hs
```

## acc コマンド

| コマンド | 内容 |
|---------|------|
| `acc login` | AtCoder にログイン |
| `acc new <contest-id>` | コンテストの雛形ディレクトリ作成 |
| `acc submit <file>` | 提出 |
| `acc config-dir` | 設定ディレクトリのパスを確認 |

## oj コマンド

| コマンド | 内容 |
|---------|------|
| `oj login https://atcoder.jp` | AtCoder にログイン |
| `oj download <url>` | サンプルケースをダウンロード |
| `oj test -c "<command>"` | サンプルケースでテスト実行 |

## acc / oj ログインできない場合

通常のログイン：

```bash
acc login
oj login https://atcoder.jp
```

ログインできない場合は Cookie を直接編集する。

### 1. ブラウザで REVEL_SESSION を取得

ブラウザの開発者ツール → Application → Cookies → `https://atcoder.jp` → `REVEL_SESSION` の Value をコピー。

### 2. acc の Cookie を更新

```bash
acc config-dir  # 設定ディレクトリのパスを確認
```

表示されたディレクトリの `session.json` を開き、`REVEL_SESSION` の値を貼り替える。

### 3. oj の Cookie を更新

```bash
oj -h  # cookie.jar のパスを確認
```

表示された `cookie.jar` を開き、`REVEL_SESSION` の値を貼り替える。
セミコロン以降（`path` 等）は削除しないよう注意。

参考: https://kaiyou9.com/acc_and_oj_login_failed/
