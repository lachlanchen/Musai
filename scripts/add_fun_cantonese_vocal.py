#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pycantonese
from pypinyin import Style, pinyin


LANGUAGES = {
    "yue-Hant": {
        "code": "yue-Hant",
        "label": "Cantonese",
        "nativeLabel": "廣東話",
        "script": "Hant",
        "pronunciation": "jyutping",
    },
    "en": {
        "code": "en",
        "label": "English",
        "nativeLabel": "English",
        "script": "Latn",
    },
    "zh-Hans": {
        "code": "zh-Hans",
        "label": "Mandarin Chinese",
        "nativeLabel": "中文",
        "script": "Hans",
        "pronunciation": "pinyin",
    },
}

MANUAL_JYUTPING = {
    "冇": "mou5",
    "佢": "keoi5",
    "哋": "dei6",
    "唔": "m4",
    "喺": "hai2",
    "嚟": "lai4",
    "嘅": "ge3",
    "咗": "zo2",
    "啲": "di1",
    "搵": "wan2",
    "攰": "gui6",
    "凍": "dung3",
    "係": "hai6",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def distribute_times(start: float, end: float, count: int) -> list[tuple[float, float]]:
    if count <= 0:
        return []
    span = max(0.001, end - start)
    return [
        (round(start + span * index / count, 3), round(start + span * (index + 1) / count, 3))
        for index in range(count)
    ]


def cjk_chars(text: str) -> list[str]:
    return [char for char in text if "\u3400" <= char <= "\u9fff"]


def char_jyutping(char: str) -> str:
    if char in MANUAL_JYUTPING:
        return MANUAL_JYUTPING[char]
    readings = pycantonese.characters_to_jyutping(char)
    for _word, reading in readings:
        if reading:
            return reading.split()[0]
    return ""


def yue_tokens(text: str, start: float, end: float) -> list[dict]:
    pairs: list[tuple[str, str]] = []
    for word, reading in pycantonese.characters_to_jyutping(text):
        chars = cjk_chars(word)
        if not chars:
            continue
        syllables = reading.split() if reading else []
        if len(chars) == len(syllables):
            pairs.extend(zip(chars, syllables))
        else:
            pairs.extend((char, char_jyutping(char)) for char in chars)
    times = distribute_times(start, end, len(pairs))
    return [
        {"text": char, "start": a, "end": b, "reading": reading}
        for (char, reading), (a, b) in zip(pairs, times)
    ]


def zh_tokens(text: str, start: float, end: float) -> list[dict]:
    chars = cjk_chars(text)
    times = distribute_times(start, end, len(chars))
    result = []
    for char, (a, b) in zip(chars, times):
        reading = pinyin(char, style=Style.TONE3, heteronym=False, neutral_tone_with_five=True)[0][0]
        result.append({"text": char, "start": a, "end": b, "pinyin": reading})
    return result


def en_tokens(text: str, start: float, end: float) -> list[dict]:
    words = re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", text)
    times = distribute_times(start, end, len(words))
    return [{"text": word, "start": a, "end": b} for word, (a, b) in zip(words, times)]


def build_track(media_id: str, lyric_set_id: str, language_code: str, source_lines: list[dict], target_by_id: dict[str, dict]) -> dict:
    lines = []
    for source in source_lines:
        target = target_by_id.get(source["id"])
        if not target:
            continue
        start = float(source["start"])
        end = float(source["end"])
        text = target["text"] if language_code == "yue-Hant" else target.get(language_code, "")
        if not text:
            continue
        if language_code == "yue-Hant":
            tokens = yue_tokens(text, start, end)
            role = "active-vocal"
        elif language_code == "zh-Hans":
            tokens = zh_tokens(text, start, end)
            role = "translation"
        else:
            tokens = en_tokens(text, start, end)
            role = "translation"
        lines.append(
            {
                "id": source["id"],
                "start": start,
                "end": end,
                "text": text,
                "singableText": text,
                "role": role,
                "tokens": tokens,
            }
        )
    return {
        "schema": "fun.lazying.media.text-track.v1",
        "version": 1,
        "mediaId": media_id,
        "songId": media_id,
        "lyricSetId": lyric_set_id,
        "language": LANGUAGES[language_code],
        "lines": lines,
    }


def upsert_audio(manifest: dict, asset: dict) -> None:
    assets = manifest.setdefault("assets", {})
    alternate = assets.get("alternateAudio")
    if alternate is None:
        alternate = []
        assets["alternateAudio"] = alternate
    alternate[:] = [item for item in alternate if item.get("id") != asset["id"] and item.get("languageCode") != asset["languageCode"]]
    alternate.append(asset)


def upsert_lyric_set(manifest: dict, lyric_set_id: str) -> None:
    sets = manifest.setdefault("lyricSets", [])
    sets[:] = [item for item in sets if item.get("id") != lyric_set_id]
    sets.append(
        {
            "id": lyric_set_id,
            "label": "Cantonese vocal lyric set",
            "languageCode": "yue-Hant",
            "tracks": [
                {"code": "yue-Hant", "label": "Cantonese", "nativeLabel": "廣東話", "script": "Hant", "features": ["active-timing", "jyutping", "word-highlight"], "path": "lyrics/yue-vocal/yue-Hant.json"},
                {"code": "en", "label": "English", "nativeLabel": "English", "script": "Latn", "features": ["translation", "rough-highlight"], "path": "lyrics/yue-vocal/en.json"},
                {"code": "zh-Hans", "label": "Mandarin Chinese", "nativeLabel": "中文", "script": "Hans", "features": ["translation", "pinyin", "rough-highlight"], "path": "lyrics/yue-vocal/zh-Hans.json"},
            ],
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Add a Cantonese vocal asset and lyric set to a Fun media manifest.")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source-track", type=Path, required=True)
    parser.add_argument("--target-lines", type=Path, required=True)
    parser.add_argument("--audio-src", required=True)
    parser.add_argument("--asset-id", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--guide", required=True)
    parser.add_argument("--quality-gate", default="review-pass")
    args = parser.parse_args()

    manifest = load_json(args.manifest)
    source = load_json(args.source_track)
    target = load_json(args.target_lines)
    media_id = manifest["id"]
    lyric_set_id = "yue-vocal"
    target_by_id = {line["id"]: line for line in target["lines"]}
    lyric_dir = args.manifest.parent / "lyrics" / lyric_set_id
    for language_code in ["yue-Hant", "en", "zh-Hans"]:
        save_json(lyric_dir / f"{language_code}.json", build_track(media_id, lyric_set_id, language_code, source["lines"], target_by_id))

    upsert_audio(
        manifest,
        {
            "id": args.asset_id,
            "label": "Cantonese vocal",
            "roleLabel": "Vocal",
            "role": "same-score-localized-vocal",
            "languageCode": "yue-Hant",
            "languageLabel": "廣東話",
            "lyricSetId": lyric_set_id,
            "sourceModel": "SoulX-Singer",
            "qualityGate": args.quality_gate,
            "src": args.audio_src,
            "mime": "audio/mpeg",
            "guide": args.guide,
        },
    )
    upsert_lyric_set(manifest, lyric_set_id)
    manifest.setdefault("localizedTitles", {})["yue-Hant"] = args.title
    manifest.setdefault("provenance", {})["cantoneseVocal"] = {
        "backend": "SoulX-Singer",
        "guide": args.guide,
        "targetLines": str(args.target_lines),
        "audio": args.audio_src,
    }
    save_json(args.manifest, manifest)
    print(args.manifest)


if __name__ == "__main__":
    main()
