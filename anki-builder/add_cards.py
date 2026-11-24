"""decks/<名前>/inbox.txt に書いた単語・文章からカードを作り、cards.md に保存して Anki に反映する。

decks/ の下のディレクトリが1つのデッキになる（例: decks/english-grammar → English Grammar）。
ディレクトリを作って inbox.txt を置けばデッキが増える。

inbox.txt の書式（1行1エントリ）:
    単語や文章 | 先生の説明
    単語や文章              ← 説明なしなら AI が英語で短い説明を書く
    先生の説明が日本語なら、AI が短い英語に直す（元の日本語はメモとして残す）
    英語のスペルミスは AI が直し、inbox.txt も書き換える（git の差分で確認・取り消しできる）
    綴りを直した行は、Anki の古いカードを引き継ぐ（学習履歴は残し、音声・画像は作り直す）
    # で始まる行と空行は無視

カードは2種類:
    Card 1（認識）: 英語 → 意味
    Card 2（産出）: 英語の定義 → 英語を当てる。単語・短いフレーズだけに作る。
    同じ日に両方が出ないよう、デッキに「兄弟カードを延期」を設定したプリセットを使う

流れ: inbox.txt → (AI) → cards.md → Anki
    - AI を呼ぶのは cards.md にまだない行と、inbox.txt で先生の説明を書き換えた行だけ
    - cards.md を手で直すと、次の実行で Anki に反映される（学習履歴は残る）
    - --regenerate を付けると全カードを AI で作り直す（cards.md の手直しは上書きされる）
"""

import argparse
import asyncio
import base64
import difflib
import functools
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
ROOT_DECK = os.environ.get("ANKI_DECK", "")  # 親デッキ。空ならトップレベルに作る
NOTE_TYPE = os.environ.get("ANKI_NOTE_TYPE", "Cebu English")
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-haiku-5-5")
TTS_VOICE = os.environ.get("TTS_VOICE", "en-US-AriaNeural")
PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY", "")
DECKS_DIR = Path(os.environ.get("DECKS_DIR", str(HERE / "decks")))

DECK_PRESET = os.environ.get("ANKI_DECK_PRESET", "English")  # 兄弟カードを延期するプリセット
PRODUCTION_MAX_WORDS = 4  # これより長い文には産出カードを作らない

FIELDS = ["Text", "Explanation", "IPA", "Example", "Audio", "Image", "Source", "Japanese", "Related", "Reverse"]

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
.hint { font-family: Menlo, monospace; font-size: 26px; letter-spacing: 4px; margin: 16px 0; }
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

# 産出カード: 説明（答えは伏せる）＋最初の1文字と文字数のヒント → 英語
# Reverse が空のノートには Card 2 を作らないよう、表面全体を {{#Reverse}} で囲む
FRONT2 = """{{#Reverse}}<div>{{Image}}</div>
{{Reverse}}{{/Reverse}}"""

BACK2 = """{{FrontSide}}
<hr id="answer">
<div class="text">{{Text}}</div>
{{Audio}}
<div class="ipa">{{IPA}}</div>
<div class="example">{{Example}}</div>
{{#Japanese}}<div class="japanese">{{hint:Japanese}}</div>{{/Japanese}}"""

TEMPLATES = {
    "Card 1": {"Front": FRONT, "Back": BACK},
    "Card 2": {"Front": FRONT2, "Back": BACK2},
}

JAPANESE_CHARS = re.compile(r"[\u3040-\u30ff\u4e00-\u9fff]")


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
    definition: str = field(default="", metadata={"label": "定義"})  # 産出カード用。常に AI の短い定義
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
    corrected_text: str = Field(description=(
        "入力の英語のスペルミスだけを直したもの。ミスがなければ入力をそのまま返す。"
        "文法・言い回し・大文字小文字・句読点・~ などの記号は変えない"
    ))
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


def fix_inbox_text(path: Path, old: str, new: str) -> None:
    """inbox.txt の見出し語 old を new に書き換える（説明部分はそのまま）。"""
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    for i, raw in enumerate(lines):
        if not raw.strip().startswith("#") and raw.replace("｜", "|").partition("|")[0].strip() == old:
            lines[i] = raw.replace(old, new, 1)
    path.write_text("".join(lines), encoding="utf-8")


CARDS_HEADER = """# Cards

<!-- add_cards.py が inbox.txt から作るファイル。手で直すと次の `mise run cards` で Anki に反映される。
     「## 」の後が見出し語（Anki で同じカードかどうかの判定に使うので変えない）。
     定義は産出カード（定義 → 英語を当てる）の問題文。同義語・反意語はカンマ区切り。画像検索を変えると画像を取り直す。
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

@functools.cache
def claude() -> anthropic.Anthropic:
    return anthropic.Anthropic()


def ask_claude(entry: Entry) -> CardInfo:
    teacher = f"\n先生の説明: {entry.explanation}" if entry.explanation else ""
    response = claude().messages.parse(
        model=CLAUDE_MODEL,
        max_tokens=2000,
        output_config={"effort": "low"},
        system=(
            "あなたはフィリピンで英語を学ぶ日本人学習者のための単語カード作成アシスタントです。"
            "学習者が授業で習った英単語・フレーズ・文章について、Anki カード用の情報を作ります。"
            "先生の説明があればそれと矛盾しない内容にしてください。"
            "学習者は英語を英語のまま理解したいので、日本語訳は補助としてだけ使います。"
            "explanation は英語で、1文・15語以内の、初心者にもすぐ分かる平易な英語にしてください。"
            "入力は授業中のメモなのでスペルミスがありえます。corrected_text 以外の項目は、直したあとの英語について作ってください。"
        ),
        messages=[{"role": "user", "content": f"英語: {entry.text}{teacher}"}],
        output_format=CardInfo,
    )
    if response.stop_reason == "refusal" or response.parsed_output is None:
        raise RuntimeError(f"Claude が応答できませんでした (stop_reason={response.stop_reason})")
    return response.parsed_output


def generate_card(entry: Entry) -> Card:
    info = ask_claude(entry)
    if not entry.explanation:
        explanation, source = info.explanation, "AI"
    elif has_japanese(entry.explanation):
        explanation, source = info.teacher_note_en, "先生（AIが英訳）"
    else:
        explanation, source = entry.explanation, "先生"
    return Card(
        text=info.corrected_text.strip() or entry.text,
        explanation=explanation,
        definition=info.explanation,
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


def deck_name(deck_dir: Path) -> str:
    # english-grammar → English Grammar
    name = " ".join(w.capitalize() for w in deck_dir.name.split("-"))
    return f"{ROOT_DECK}::{name}" if ROOT_DECK else name


def ensure_note_type() -> None:
    if NOTE_TYPE in anki("modelNames"):
        # 既存のノートタイプにもフィールド・テンプレート・CSSの変更を反映する
        existing = anki("modelFieldNames", modelName=NOTE_TYPE)
        for name in FIELDS:
            if name not in existing:
                anki("modelFieldAdd", modelName=NOTE_TYPE, fieldName=name)
        existing_templates = anki("modelTemplates", modelName=NOTE_TYPE)
        for name, tmpl in TEMPLATES.items():
            if name not in existing_templates:
                anki("modelTemplateAdd", modelName=NOTE_TYPE, template={"Name": name, **tmpl})
        anki("updateModelTemplates", model={"name": NOTE_TYPE, "templates": TEMPLATES})
        anki("updateModelStyling", model={"name": NOTE_TYPE, "css": CSS})
        return
    anki(
        "createModel",
        modelName=NOTE_TYPE,
        inOrderFields=FIELDS,
        css=CSS,
        cardTemplates=[{"Name": name, **tmpl} for name, tmpl in TEMPLATES.items()],
    )
    print(f"ノートタイプ「{NOTE_TYPE}」を作成しました")


def existing_notes() -> dict[str, dict]:
    """このノートタイプのノートを Text → {id, fields, tags, cards, decks} で返す。"""
    notes = anki("notesInfo", notes=anki("findNotes", query=f'"note:{NOTE_TYPE}"'))
    card_ids = [c for n in notes for c in n["cards"]]
    deck_of = {c["cardId"]: c["deckName"] for c in anki("cardsInfo", cards=card_ids)}
    return {
        n["fields"]["Text"]["value"]: {
            "id": n["noteId"],
            "fields": {k: v["value"] for k, v in n["fields"].items()},
            "tags": n["tags"],
            "cards": n["cards"],
            "decks": {deck_of[c] for c in n["cards"]},
        }
        for n in notes
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


def wants_production(text: str) -> bool:
    return len(text.split()) <= PRODUCTION_MAX_WORDS and not text.rstrip().endswith((".", "?", "!"))


def mask_answer(explanation: str, text: str) -> str:
    """説明の中の答え（とその活用形）を ____ に置き換える。"""
    core = re.sub(r"\s*~\S*", "", text).strip()  # get used to ~ing → get used to
    words = [w for w in re.findall(r"[A-Za-z]+", text) if len(w) >= 4] + [text, core]
    for w in sorted(set(words), key=len, reverse=True):
        explanation = re.sub(rf"\b{re.escape(w)}\w*", "____", explanation, flags=re.IGNORECASE)
    return explanation


def letter_hint(text: str) -> str:
    """procrastinate → p____________ (13)。空白や記号はそのまま見せる。"""
    pattern = text[0] + "".join("_" if c.isalpha() else c for c in text[1:])
    letters = sum(c.isalpha() for c in text)
    return f"{html.escape(pattern)} <small>({letters})</small>"


def format_reverse(card: Card) -> str:
    """産出カードの表。空ならそのノートに Card 2 は作られない。"""
    if not card.definition or not wants_production(card.text):
        return ""
    return (f'<div class="explanation">{html.escape(mask_answer(card.definition, card.text))}</div>'
            f'<div class="hint">{letter_hint(card.text)}</div>')


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
        "Reverse": format_reverse(card),
    }


def sync_card(card: Card, existing: dict | None, deck: str) -> str:
    """Anki にカードを追加・更新・移動する。戻り値は表示用の記号。"""
    fields = anki_fields(card, existing)
    tags = ["ai-explained"] if card.source == "AI" else ["teacher"]
    if existing is None:
        anki("addNote", note={
            "deckName": deck, "modelName": NOTE_TYPE, "fields": fields, "tags": tags,
            "options": {"allowDuplicate": False, "duplicateScope": "deck"},
        })
        return "✅"
    mark = ""
    if existing["decks"] != {deck}:
        anki("changeDeck", cards=existing["cards"], deck=deck)
        mark += "📦"
    if fields != {k: existing["fields"].get(k, "") for k in fields} or not set(tags) <= set(existing["tags"]):
        anki("updateNote", note={"id": existing["id"], "fields": fields, "tags": tags})
        mark += "🔄"
    return mark


def find_renamed(text: str, orphans: dict[str, dict]) -> str | None:
    """綴りを直した行に対応する、Anki にだけ残っている古いカードを探す。"""
    by_lower = {t.lower(): t for t in orphans}
    match = difflib.get_close_matches(text.lower(), list(by_lower), n=1, cutoff=0.85)
    return by_lower[match[0]] if match else None


def suspend_empty_production_cards() -> None:
    """対象外（Reverse が空）の Card 2 は停止する。Anki の「ツール → 空のカード」で削除できる。"""
    if empty := anki("findCards", query=f'"note:{NOTE_TYPE}" card:2 Reverse: -is:suspended'):
        anki("suspend", cards=empty)


def ensure_deck(deck: str) -> None:
    """デッキを作り、兄弟カードを延期するプリセットを割り当てる（他のデッキのプリセットは変えない）。"""
    anki("createDeck", deck=deck)
    config = anki("getDeckConfig", deck=deck)
    if config["name"] == DECK_PRESET:
        return
    preset_id = next(
        (c["id"] for d in anki("deckNames") if (c := anki("getDeckConfig", deck=d))["name"] == DECK_PRESET),
        None,
    )
    if preset_id is None:
        preset_id = anki("cloneDeckConfigId", name=DECK_PRESET, cloneFrom=config["id"])
        preset = anki("getDeckConfig", deck=deck) | {"id": preset_id, "name": DECK_PRESET}
        preset["new"]["bury"] = preset["rev"]["bury"] = True
        anki("saveDeckConfig", config=preset)
        print(f"プリセット「{DECK_PRESET}」を作成（兄弟カードを延期）")
    anki("setDeckConfigId", decks=[deck], configId=preset_id)


def with_retry(fn, attempts: int = 3):
    """通信エラーなど一時的な失敗はやり直す。"""
    for i in range(attempts):
        try:
            return fn()
        except (httpx.TransportError, OSError, edge_tts.exceptions.EdgeTTSException):
            if i == attempts - 1:
                raise
            time.sleep(2 * (i + 1))


def generate_missing(deck_dir: Path, regenerate: bool) -> tuple[dict[str, Card], int]:
    """inbox.txt のうち cards.md にない行を AI で作り、cards.md に保存する。"""
    cards_path = deck_dir / "cards.md"
    entries = parse_inbox(deck_dir / "inbox.txt")
    # cards.md は inbox.txt の行だけを inbox.txt の順に持つ（消した行・別デッキへ移した行は落とす）
    loaded = load_cards(cards_path)
    cards = {e.text: loaded[e.text] for e in entries if e.text in loaded}
    to_generate = [
        e for e in entries
        if regenerate or e.text not in cards or e.explanation != cards[e.text].memo
    ]
    generating = {e.text for e in to_generate}
    failed = 0
    # 定義がないカード（定義の項目を足す前に作ったもの）は、手直しを残したまま定義だけ AI で埋める
    for card in cards.values():
        if card.definition or card.text in generating:
            continue
        if card.source == "AI":
            card.definition = card.explanation
            continue
        try:
            card.definition = with_retry(lambda: ask_claude(Entry(card.text, card.memo))).explanation
            print(f"  📖 定義を追加: {card.text}")
        except Exception as e:
            failed += 1
            print(f"  ❌ 定義の追加に失敗 {card.text}: {e}", file=sys.stderr)
    for i, entry in enumerate(to_generate, 1):
        try:
            card = with_retry(lambda: generate_card(entry))
            if card.text != entry.text:
                fix_inbox_text(deck_dir / "inbox.txt", entry.text, card.text)
                cards.pop(entry.text, None)
                print(f"  🔤 スペル修正: {entry.text} → {card.text}")
            cards[card.text] = card
            save_cards(cards_path, cards)  # 途中で止まっても作った分は残す
            print(f"  [{i}/{len(to_generate)}] ✏️  {card.text}")
        except Exception as e:  # 1件の失敗で全体を止めない
            failed += 1
            print(f"  [{i}/{len(to_generate)}] ❌ {entry.text}: {e}", file=sys.stderr)
    save_cards(cards_path, cards)
    return cards, failed


def main() -> int:
    parser = argparse.ArgumentParser(description="decks/*/inbox.txt からカードを作り、cards.md と Anki に反映する")
    parser.add_argument("decks", nargs="*", help="対象のデッキ（ディレクトリ名）。省略で全部")
    parser.add_argument("--regenerate", action="store_true",
                        help="カードを AI で作り直す（cards.md の手直しは上書きされる）")
    args = parser.parse_args()

    deck_dirs = sorted(d for d in DECKS_DIR.iterdir() if (d / "inbox.txt").exists())
    if args.decks:
        deck_dirs = [d for d in deck_dirs if d.name in args.decks]
    if not deck_dirs:
        print(f"{DECKS_DIR} に inbox.txt のあるディレクトリがありません")
        return 1

    try:
        anki("version")
    except httpx.ConnectError:
        print("Anki に接続できません。Anki を起動し、AnkiConnect アドオンを入れてください。")
        return 1
    if not PIXABAY_API_KEY:
        print("（PIXABAY_API_KEY が未設定なので画像はスキップします）")

    ensure_note_type()
    notes = existing_notes()
    failed = added = updated = 0

    generated: list[tuple[Path, dict[str, Card]]] = []
    for deck_dir in deck_dirs:
        print(f"■ {deck_name(deck_dir)}  (decks/{deck_dir.name})")
        cards, gen_failed = generate_missing(deck_dir, args.regenerate)
        failed += gen_failed
        generated.append((deck_dir, cards))

    # どの cards.md にもない Anki のカード（綴りを直す前の古いカードなど）
    active = {t for d in DECKS_DIR.iterdir() if (d / "cards.md").exists() for t in load_cards(d / "cards.md")}
    orphans = {t: n for t, n in notes.items() if t not in active}

    for deck_dir, cards in generated:
        deck = deck_name(deck_dir)
        print(f"■ {deck} → Anki")
        ensure_deck(deck)
        for card in cards.values():
            existing = notes.get(card.text)
            if existing is None and (old := find_renamed(card.text, orphans)):
                # 綴りを直す前のカードを引き継ぐ。音声・画像は新しい綴りで作り直す
                existing = orphans.pop(old)
                existing["fields"] = {k: v for k, v in existing["fields"].items() if k not in ("Audio", "Image")}
                print(f"  🔤 Anki のカードを引き継ぎ: {old} → {card.text}")
            try:
                mark = with_retry(lambda: sync_card(card, existing, deck))
            except Exception as e:
                failed += 1
                print(f"  ❌ Anki 反映失敗 {card.text}: {e}", file=sys.stderr)
                continue
            if mark:
                print(f"  {mark} {card.text}")
                added += "✅" in mark
                updated += "✅" not in mark
        print(f"  cards.md: {len(cards)} 件")

    suspend_empty_production_cards()

    if orphans:
        print(f"⚠️  Anki にだけあるカード（どの inbox.txt にもない）: {', '.join(orphans)}")
        print("   不要なら Anki のブラウザで削除してください")
    print(f"完了: Anki に {added} 件追加, {updated} 件更新・移動, {failed} 件失敗")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
