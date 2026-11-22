"""inbox.txt に書いた単語・文章からカードを作り、cards.md に保存して Anki に反映する。

inbox.txt の書式（1行1エントリ）:
    単語や文章 | 先生の説明
    単語や文章              ← 説明なしなら AI が英語で短い説明を書く
    先生の説明が日本語なら、AI が短い英語に直す（元の日本語はメモとして残す）
    # で始まる行と空行は無視

流れ: inbox.txt → (AI) → cards.md → Anki
    - AI を呼ぶのは cards.md にまだない行と、inbox.txt で先生の説明を書き換えた行だけ
    - cards.md を手で直すと、次の実行で Anki に反映される（学習履歴は残る）
    - --regenerate を付けると全カードを AI で作り直す（cards.md の手直しは上書きされる）
"""

import argparse
import asyncio
import base64
import hashlib
import html
import os
import re
import sys
import time
from dataclasses import dataclass, field, fields as dataclass_fields
from pathlib import Path

import anthropic
import edge_tts
import httpx
from pydantic import BaseModel, Field

HERE = Path(__file__).parent

ANKI_CONNECT_URL = os.environ.get("ANKI_CONNECT_URL", "http://127.0.0.1:8765")
DECK = os.environ.get("ANKI_DECK", "Cebu English")
NOTE_TYPE = os.environ.get("ANKI_NOTE_TYPE", "Cebu English")
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-haiku-5-5")
TTS_VOICE = os.environ.get("TTS_VOICE", "en-US-AriaNeural")
PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY", "")
DEFAULT_INBOX = os.environ.get("INBOX_PATH", str(HERE / "inbox.txt"))
DEFAULT_CARDS = os.environ.get("CARDS_PATH", str(HERE / "cards.md"))

FIELDS = ["Text", "Explanation", "IPA", "Example", "Audio", "Image", "Source", "Japanese", "Related"]

CSS = """
.card { font-family: -apple-system, "Hiragino Sans", sans-serif; font-size: 22px;
        text-align: center; color: #222; background: #fff; }
.nightMode .card, .night_mode .card { color: #eee; background: #1e1e1e; }
.text { font-size: 30px; font-weight: bold; margin: 12px 0; }
.ipa { color: #2a7ae2; font-family: "Lucida Sans Unicode", sans-serif; }
.explanation { text-align: left; margin: 16px auto; max-width: 560px; }
.example { text-align: left; margin: 12px auto; max-width: 560px; color: #666; font-size: 18px; }
.related { font-size: 16px; color: #888; margin: 8px 0; }
.japanese { text-align: left; margin: 12px auto; max-width: 560px; font-size: 16px; }
.source { font-size: 12px; color: #999; }
img { max-width: 100%; max-height: 260px; border-radius: 8px; }
"""

FRONT = """<div class="text">{{Text}}</div>
{{Audio}}"""

BACK = """{{FrontSide}}
<hr id="answer">
<div>{{Image}}</div>
<div class="ipa">{{IPA}}</div>
<div class="example">{{Example}}</div>
<div class="explanation">{{Explanation}}</div>
<div class="related">{{Related}}</div>
{{#Japanese}}<div class="japanese">{{hint:Japanese}}</div>{{/Japanese}}
<div class="source">{{Source}}</div>"""

JAPANESE_CHARS = re.compile(r"[぀-ヿ一-鿿]")


def has_japanese(text: str) -> bool:
    return bool(JAPANESE_CHARS.search(text))


@dataclass
class Entry:
    text: str
    explanation: str  # 空なら AI が埋める


@dataclass
class Card:
    """cards.md の1カード。label は cards.md に書く見出し。"""
    text: str
    explanation: str = field(default="", metadata={"label": "説明"})
    example: str = field(default="", metadata={"label": "例文"})
    ipa: str = field(default="", metadata={"label": "発音"})
    synonyms: str = field(default="", metadata={"label": "同義語"})
    antonyms: str = field(default="", metadata={"label": "反意語"})
    meaning_ja: str = field(default="", metadata={"label": "意味"})
    example_ja: str = field(default="", metadata={"label": "例文訳"})
    memo: str = field(default="", metadata={"label": "先生のメモ"})
    image_query: str = field(default="", metadata={"label": "画像検索"})
    source: str = field(default="", metadata={"label": "出典"})


CARD_LABELS = {f.metadata["label"]: f.name for f in dataclass_fields(Card) if "label" in f.metadata}


class CardInfo(BaseModel):
    explanation: str = Field(description="One short sentence in simple English (max 15 words)")
    ipa: str = Field(description="IPA 発音記号（米国英語）。スラッシュで囲む")
    example_en: str = Field(description="自然な英語の例文1つ。入力が文章なら似た場面で使える別の文")
    example_ja: str = Field(description="example_en の日本語訳")
    image_query: str = Field(description="画像検索用の英語キーワード（1〜3語、具体的な名詞）")
    teacher_note_en: str = Field(description="先生の説明の直訳（短い英語）。原文にない情報・例・解説は一切加えない。先生の説明がなければ空")
    meaning_ja: str = Field(description="日本語の意味（1語〜短い句）")
    synonyms: list[str] = Field(description="同じ意味で置き換えられる、易しい同義語を0〜2個。なければ空")
    antonyms: list[str] = Field(description="反意語を0〜1個。自然なものがなければ空")


# ---------- ファイル ----------

def parse_inbox(path: Path) -> list[Entry]:
    entries: list[Entry] = []
    seen: set[str] = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        text, _, explanation = line.replace("｜", "|").partition("|")
        text = text.strip()
        if text and text not in seen:
            seen.add(text)
            entries.append(Entry(text, explanation.strip()))
    return entries


CARDS_HEADER = """# Cards

<!-- add_cards.py が inbox.txt から作るファイル。手で直すと次の `mise run cards` で Anki に反映される。
     「## 」の後が見出し語（Anki で同じカードかどうかの判定に使うので変えない）。
     同義語・反意語はカンマ区切り。画像検索を変えると画像を取り直す。
     先生のメモは inbox.txt から来る。直すなら inbox.txt 側を直す（そのカードは AI で作り直される）。 -->
"""


def load_cards(path: Path) -> dict[str, Card]:
    cards: dict[str, Card] = {}
    if not path.exists():
        return cards
    current: Card | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            current = Card(text=line[3:].strip())
            cards[current.text] = current
        elif current and line.startswith("- "):
            label, _, value = line[2:].partition(":")
            if name := CARD_LABELS.get(label.strip()):
                setattr(current, name, value.strip())
    return cards


def save_cards(path: Path, cards: dict[str, Card]) -> None:
    out = [CARDS_HEADER]
    for card in cards.values():
        out.append(f"## {card.text}")
        for label, name in CARD_LABELS.items():
            if value := getattr(card, name):
                out.append(f"- {label}: {value}")
        out.append("")
    path.write_text("\n".join(out), encoding="utf-8")


def split_list(value: str) -> list[str]:
    return [v.strip() for v in value.split(",") if v.strip()]


# ---------- AI ----------

def ask_claude(client: anthropic.Anthropic, entry: Entry) -> CardInfo:
    teacher = f"\n先生の説明: {entry.explanation}" if entry.explanation else ""
    response = client.messages.parse(
        model=CLAUDE_MODEL,
        max_tokens=2000,
        output_config={"effort": "low"},
        system=(
            "あなたはフィリピンで英語を学ぶ日本人学習者のための単語カード作成アシスタントです。"
            "学習者が授業で習った英単語・フレーズ・文章について、Anki カード用の情報を作ります。"
            "先生の説明があればそれと矛盾しない内容にしてください。"
            "学習者は英語を英語のまま理解したいので、日本語訳は補助としてだけ使います。"
            "explanation は英語で、1文・15語以内の、初心者にもすぐ分かる平易な英語にしてください。"
        ),
        messages=[{"role": "user", "content": f"英語: {entry.text}{teacher}"}],
        output_format=CardInfo,
    )
    if response.stop_reason == "refusal" or response.parsed_output is None:
        raise RuntimeError(f"Claude が応答できませんでした (stop_reason={response.stop_reason})")
    return response.parsed_output


def generate_card(client: anthropic.Anthropic, entry: Entry) -> Card:
    info = ask_claude(client, entry)
    if not entry.explanation:
        explanation, source = info.explanation, "AI"
    elif has_japanese(entry.explanation):
        explanation, source = info.teacher_note_en, "先生（AIが英訳）"
    else:
        explanation, source = entry.explanation, "先生"
    return Card(
        text=entry.text,
        explanation=explanation,
        example=info.example_en,
        ipa=info.ipa,
        synonyms=", ".join(info.synonyms[:2]),
        antonyms=", ".join(info.antonyms[:1]),
        meaning_ja=info.meaning_ja,
        example_ja=info.example_ja,
        memo=entry.explanation,
        image_query=info.image_query,
        source=source,
    )


# ---------- AnkiConnect ----------

def anki(action: str, **params):
    res = httpx.post(
        ANKI_CONNECT_URL,
        json={"action": action, "version": 6, "params": params},
        timeout=60,
    ).json()
    if res.get("error"):
        raise RuntimeError(f"AnkiConnect {action}: {res['error']}")
    return res["result"]


def ensure_deck_and_note_type() -> None:
    anki("createDeck", deck=DECK)
    if NOTE_TYPE in anki("modelNames"):
        # 既存のノートタイプにもフィールド・テンプレート・CSSの変更を反映する
        existing = anki("modelFieldNames", modelName=NOTE_TYPE)
        for name in FIELDS:
            if name not in existing:
                anki("modelFieldAdd", modelName=NOTE_TYPE, fieldName=name)
        anki("updateModelTemplates", model={"name": NOTE_TYPE, "templates": {"Card 1": {"Front": FRONT, "Back": BACK}}})
        anki("updateModelStyling", model={"name": NOTE_TYPE, "css": CSS})
        return
    anki(
        "createModel",
        modelName=NOTE_TYPE,
        inOrderFields=FIELDS,
        css=CSS,
        cardTemplates=[{"Name": "Card 1", "Front": FRONT, "Back": BACK}],
    )
    print(f"ノートタイプ「{NOTE_TYPE}」を作成しました")


def existing_notes() -> dict[str, dict]:
    """デッキ内のノートを Text → {id, fields, tags} で返す。"""
    ids = anki("findNotes", query=f'"deck:{DECK}"')
    return {
        n["fields"]["Text"]["value"]: {
            "id": n["noteId"],
            "fields": {k: v["value"] for k, v in n["fields"].items()},
            "tags": n["tags"],
        }
        for n in anki("notesInfo", notes=ids)
    }


def store_media(filename: str, *, data: bytes | None = None, url: str | None = None) -> str:
    if data is not None:
        return anki("storeMediaFile", filename=filename, data=base64.b64encode(data).decode())
    return anki("storeMediaFile", filename=filename, url=url)


# ---------- 音声・画像 ----------

async def _tts(text: str) -> bytes:
    audio = bytearray()
    async for chunk in edge_tts.Communicate(text, TTS_VOICE).stream():
        if chunk["type"] == "audio":
            audio.extend(chunk["data"])
    return bytes(audio)


def find_image_url(query: str) -> str | None:
    if not PIXABAY_API_KEY or not query:
        return None
    res = httpx.get(
        "https://pixabay.com/api/",
        params={"key": PIXABAY_API_KEY, "q": query, "image_type": "photo",
                "safesearch": "true", "per_page": 3},
        timeout=30,
    )
    res.raise_for_status()
    hits = res.json().get("hits", [])
    return hits[0]["webformatURL"] if hits else None


def image_html(key: str, query: str) -> str:
    if image_url := find_image_url(query):
        name = store_media(f"cebu_{key}.jpg", url=image_url)
        # alt に検索語を残し、cards.md で検索語が変わったら取り直す
        return f'<img src="{name}" alt="{html.escape(query)}">'
    return ""


# ---------- Anki に反映 ----------

def format_related(card: Card) -> str:
    parts = []
    if synonyms := split_list(card.synonyms):
        parts.append("≈ " + ", ".join(synonyms))
    if antonyms := split_list(card.antonyms):
        parts.append("↔ " + ", ".join(antonyms))
    return "&nbsp;&nbsp;&nbsp;".join(parts)


def format_japanese(card: Card) -> str:
    lines = []
    if card.meaning_ja:
        lines.append(f"意味: {card.meaning_ja}")
    if card.example_ja:
        lines.append(f"例文: {card.example_ja}")
    if has_japanese(card.memo):
        lines.append(f"メモ: {card.memo}")
    return "<br>".join(lines)


def anki_fields(card: Card, existing: dict | None) -> dict[str, str]:
    key = hashlib.sha1(card.text.encode()).hexdigest()[:12]
    old = existing["fields"] if existing else {}

    audio = old.get("Audio") or f"[sound:{store_media(f'cebu_{key}.mp3', data=asyncio.run(_tts(card.text)))}]"
    image = old.get("Image", "")
    if f'alt="{html.escape(card.image_query)}"' not in image:
        image = image_html(key, card.image_query) or image

    return {
        "Text": card.text,
        "Explanation": card.explanation,
        "IPA": card.ipa,
        "Example": card.example,
        "Audio": audio,
        "Image": image,
        "Source": f"説明: {card.source}" if card.source else "",
        "Japanese": format_japanese(card),
        "Related": format_related(card),
    }


def sync_card(card: Card, existing: dict | None) -> str:
    """Anki にカードを追加・更新する。戻り値は表示用の記号。"""
    fields = anki_fields(card, existing)
    tags = ["ai-explained"] if card.source == "AI" else ["teacher"]
    if existing is None:
        anki("addNote", note={
            "deckName": DECK, "modelName": NOTE_TYPE, "fields": fields, "tags": tags,
            "options": {"allowDuplicate": False, "duplicateScope": "deck"},
        })
        return "✅"
    if fields == {k: existing["fields"].get(k, "") for k in fields} and set(tags) <= set(existing["tags"]):
        return ""
    anki("updateNote", note={"id": existing["id"], "fields": fields, "tags": tags})
    return "🔄"


def with_retry(fn, attempts: int = 3):
    """通信エラーなど一時的な失敗はやり直す。"""
    for i in range(attempts):
        try:
            return fn()
        except (httpx.TransportError, OSError, edge_tts.exceptions.EdgeTTSException):
            if i == attempts - 1:
                raise
            time.sleep(2 * (i + 1))


def main() -> int:
    parser = argparse.ArgumentParser(description="inbox.txt からカードを作り、cards.md と Anki に反映する")
    parser.add_argument("inbox", nargs="?", default=DEFAULT_INBOX, help="入力ファイル")
    parser.add_argument("--cards", default=DEFAULT_CARDS, help="カードの保存先 (cards.md)")
    parser.add_argument("--regenerate", action="store_true",
                        help="全カードを AI で作り直す（cards.md の手直しは上書きされる）")
    args = parser.parse_args()

    try:
        anki("version")
    except httpx.ConnectError:
        print("Anki に接続できません。Anki を起動し、AnkiConnect アドオンを入れてください。")
        return 1

    cards_path = Path(args.cards)
    cards = load_cards(cards_path)
    entries = parse_inbox(Path(args.inbox))
    to_generate = [
        e for e in entries
        if args.regenerate or e.text not in cards or e.explanation != cards[e.text].memo
    ]
    if not PIXABAY_API_KEY:
        print("（PIXABAY_API_KEY が未設定なので画像はスキップします）")

    failed = 0
    if to_generate:
        print(f"AI でカードを作成: {len(to_generate)} 件")
        client = anthropic.Anthropic()
        for i, entry in enumerate(to_generate, 1):
            try:
                cards[entry.text] = with_retry(lambda: generate_card(client, entry))
                save_cards(cards_path, cards)  # 途中で止まっても作った分は残す
                print(f"  [{i}/{len(to_generate)}] ✏️  {entry.text}")
            except Exception as e:  # 1件の失敗で全体を止めない
                failed += 1
                print(f"  [{i}/{len(to_generate)}] ❌ {entry.text}: {e}", file=sys.stderr)
    save_cards(cards_path, cards)

    ensure_deck_and_note_type()
    notes = existing_notes()
    added = updated = 0
    for card in cards.values():
        try:
            mark = with_retry(lambda: sync_card(card, notes.get(card.text)))
        except Exception as e:
            failed += 1
            print(f"  ❌ Anki 反映失敗 {card.text}: {e}", file=sys.stderr)
            continue
        if mark:
            print(f"  {mark} {card.text}")
            added += mark == "✅"
            updated += mark == "🔄"

    print(f"完了: Anki に {added} 件追加, {updated} 件更新, {failed} 件失敗（cards.md: {len(cards)} 件）")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
