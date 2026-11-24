# anki-builder

授業で習った単語・文章・文法を `decks/<デッキ>/inbox.txt` に1行ずつ書き足し、スクリプトを実行すると Anki にカードができる。

- 説明を書かなかった行は、AI（Claude）が短い英語の説明を書く
- 先生の説明を日本語で書いた行は、AI が英語に直す（元の日本語はタップで開く Japanese 欄に残る）
- 英語のスペルミスは AI が直し、`inbox.txt` も書き換える（直した内容は実行時に `🔤` で表示。git の差分で確認・取り消しできる）
- 全カードに発音記号（IPA）、例文、同義語・反意語、音声（edge-tts）、画像（Pixabay）を付ける
- 表は英語と音声だけ。裏に画像・例文・説明・関連語を表示し、日本語訳はタップしたときだけ見える
- 一度カードにした行は AI を呼び直さないので、ファイルは消さずに追記し続けてよい

## デッキ（ディレクトリ）

```
decks/
  english-vocabulary/   → Anki: English Vocabulary（単語・フレーズ・文章）
    inbox.txt   ← 自分で書く
    cards.md    ← スクリプトが作る（読む・直す用）
  english-grammar/      → Anki: English Grammar（文法）
```

`decks/` の下にディレクトリを作って `inbox.txt` を置けば、デッキが増える。
`ANKI_DECK` に親デッキ名を設定すると、その下のサブデッキとして作る。
`inbox.txt` の行を別のデッキに移すと、次の実行で Anki のカードも移動する（学習履歴は残る）。
その場合は `cards.md` の該当セクションも一緒に移すと、AI を呼び直さずに済む。
`inbox.txt` から行を消すと `cards.md` からも消える（Anki のカードは消さない。不要なら Anki で削除する）。

## 流れ

`inbox.txt`（自分で書く）→ AI → `cards.md`（カードの中身。読む・直す用）→ Anki

- AI を呼ぶのは `cards.md` にまだない行と、`inbox.txt` で先生の説明を書き換えた行だけ
- `cards.md` を手で直すと、次の `mise run cards` で Anki に反映される（学習履歴は残る）
- `cards.md` をコミットしておけば、AI の出力や自分の手直しを git で見比べたり戻したりできる

## 入力 (`inbox.txt`)

```text
# 2026-11-17 Teacher Anna
procrastinate | 先延ばしにする。悪い意味で使う
I'm looking forward to seeing you.
```

`|`（全角の `｜` も可）の右が説明。`#` で始まる行と空行は無視する。

## 準備

1. Anki（PC版）に AnkiConnect アドオン（コード `2055492159`）を入れ、Anki を起動しておく
2. `mise install`（Python・uv・sops・age が入る）
3. API キーを sops で暗号化した `secrets.env` に書く（下記）

## API キーの管理（sops + age）

`secrets.env` は暗号化されているのでコミットしてよい。復号に使う秘密鍵は
`~/.config/sops/age/keys.txt` にあり、リポジトリには入れない。**この鍵はパスワードマネージャーなどにバックアップすること**（失くすと復号できない）。

```sh
mise run secrets   # エディタが開く。保存すると暗号化される
```

```dotenv
ANTHROPIC_API_KEY=sk-ant-...
PIXABAY_API_KEY=...        # 任意。なければ画像なし
```

## 実行

```sh
mise run cards     # secrets.env を復号し、環境変数として渡して add_cards.py を実行
mise run cards-regenerate  # 全カードを AI で作り直す（cards.md の手直しは上書きされる。学習履歴は残る）
```

特定のデッキだけ処理するなら `sops exec-env secrets.env 'uv run add_cards.py english-grammar'`。
デッキとノートタイプ「Cebu English」は初回実行時に自動で作られる（ノートタイプ名はカードの見た目に出ない）。

## 設定（環境変数）

| 変数 | 既定値 |
|---|---|
| `ANKI_DECK` | なし（親デッキ名。設定するとその下に作る） |
| `ANKI_NOTE_TYPE` | `Cebu English` |
| `CLAUDE_MODEL` | `claude-haiku-5-5` |
| `TTS_VOICE` | `en-US-AriaNeural`（英国英語なら `en-GB-SoniaNeural`） |
| `DECKS_DIR` | `./decks` |
| `ANKI_CONNECT_URL` | `http://127.0.0.1:8765` |
