# anki-builder

授業で習った単語・文章を `inbox.txt` に1行ずつ書き足し、スクリプトを実行すると Anki にカードができる。

- 説明を書かなかった行は、AI（Claude）が短い英語の説明を書く
- 先生の説明を日本語で書いた行は、AI が英語に直す（元の日本語はタップで開く Japanese 欄に残る）
- 全カードに発音記号（IPA）、例文、同義語・反意語、音声（edge-tts）、画像（Pixabay）を付ける
- 表は英語と音声だけ。裏に画像・例文・説明・関連語を表示し、日本語訳はタップしたときだけ見える
- 登録済みの行は Anki 側で重複を判定してスキップするので、ファイルは消さずに追記し続けてよい

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
`INBOX_PATH` 環境変数を設定すれば、iCloud Drive などに置いたファイルを読める。

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

デッキ「Cebu English」とノートタイプ「Cebu English」は初回実行時に自動で作られる。

## 設定（環境変数）

| 変数 | 既定値 |
|---|---|
| `ANKI_DECK` | `Cebu English` |
| `ANKI_NOTE_TYPE` | `Cebu English` |
| `CLAUDE_MODEL` | `claude-haiku-5-5` |
| `TTS_VOICE` | `en-US-AriaNeural`（英国英語なら `en-GB-SoniaNeural`） |
| `INBOX_PATH` | `./inbox.txt` |
| `ANKI_CONNECT_URL` | `http://127.0.0.1:8765` |
