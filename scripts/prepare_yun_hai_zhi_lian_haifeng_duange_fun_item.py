#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from pypinyin import Style, pinyin
import pykakasi


ROOT = Path(__file__).resolve().parents[1]
SONGS = ROOT.parent / "MusiaSongs"
MEDIA_ID = "yun-hai-zhi-lian-haifeng-duange"
LONG_ID = "yun-hai-zhi-lian"
PUBLIC_AUDIO = "https://lazyingart.github.io/MusiaSongs/audio/yun-hai-zhi-lian-haifeng-duange-zh-Hans-ace-20260630.mp3"
PROJECT = ROOT / "data/creative_projects/yun-hai-zhi-lian-haifeng-duange-20260630"
SELECTED_AUDIO = PROJECT / "selected/yun-hai-zhi-lian-haifeng-duange-zh-Hans-ace-20260630.mp3"
ANALYSIS = ROOT / "data/runs/yun-hai-zhi-lian-haifeng-duange-20260630-analysis"


LANG = {
    "en": {"code": "en", "label": "English", "nativeLabel": "English", "script": "Latn"},
    "zh-Hans": {
        "code": "zh-Hans",
        "label": "Mandarin Chinese",
        "nativeLabel": "中文",
        "script": "Hans",
        "pronunciation": "pinyin",
    },
    "ja": {
        "code": "ja",
        "label": "Japanese",
        "nativeLabel": "日本語",
        "script": "Jpan",
        "pronunciation": "furigana",
    },
}

KAKASI = pykakasi.kakasi()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def duration(path: Path) -> float:
    return float(
        subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nk=1:nw=1", str(path)],
            text=True,
        ).strip()
    )


def is_cjk(text: str) -> bool:
    return any("\u3400" <= char <= "\u9fff" for char in text)


def zh_pinyin(char: str) -> str:
    if not is_cjk(char):
        return ""
    values = pinyin(char, style=Style.TONE3, strict=False, neutral_tone_with_five=True)
    return values[0][0] if values and values[0] else ""


def ja_reading(text: str) -> str:
    if not is_cjk(text):
        return ""
    converted = KAKASI.convert(text)
    hira = "".join(item.get("hira") or item.get("orig") or "" for item in converted)
    return hira if hira and hira != text else ""


def split_en(text: str) -> list[str]:
    spaced = text
    for mark in [",", ".", "?", "!", ";", ":"]:
        spaced = spaced.replace(mark, f" {mark} ")
    return [part for part in spaced.split() if part]


def split_visible(text: str, code: str) -> list[str]:
    if code == "en":
        return split_en(text)
    return [char for char in text if not char.isspace()]


def tokens_for(line: dict[str, Any], code: str) -> list[dict[str, Any]]:
    parts = split_visible(line["text"], code)
    if not parts:
        return []
    start = float(line["start"])
    end = float(line["end"])
    step = (end - start) / len(parts)
    tokens: list[dict[str, Any]] = []
    for index, part in enumerate(parts):
        item = {"text": part, "start": round(start + step * index, 3), "end": round(start + step * (index + 1), 3)}
        if code == "zh-Hans":
            reading = zh_pinyin(part)
            if reading:
                item["pinyin"] = reading
        elif code == "ja":
            reading = ja_reading(part)
            if reading:
                item["reading"] = reading
        tokens.append(item)
    return tokens


def make_line(line_id: str, start: float, end: float, text: str, code: str) -> dict[str, Any]:
    line = {"id": line_id, "start": round(start, 3), "end": round(end, 3), "text": text, "singableText": text, "role": "lyric"}
    line["tokens"] = tokens_for(line, code)
    return line


def track(code: str, lines: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema": "fun.lazying.media.text-track.v1",
        "version": 1,
        "mediaId": MEDIA_ID,
        "language": LANG[code],
        "lines": lines,
        "provenance": {
            "vocalSet": "zh-vocal",
            "correction": (
                "Active Mandarin lyrics corrected from selected-audio small ASR, vocal-stem medium ASR, "
                "no-VAD base/small/medium ASR, user listening feedback, and the reference lyric. "
                "Opening and outro 天蓝蓝/海蓝蓝 lines were restored because no-VAD ASR recovered them "
                "as sound-close variants and the user confirmed the audio contains them. Skipped bridge "
                "draft lines remain unpublished."
            ),
        },
    }


def corrected_rows() -> list[tuple[str, float, float, str, str, str]]:
    return [
        ("l01", 14.68, 16.20, "天蓝蓝", "The sky is blue.", "空は青く"),
        ("l02", 16.20, 17.78, "海蓝蓝", "The sea is blue.", "海は青く"),
        ("l03", 17.78, 20.82, "云在天地间", "Clouds rest between heaven and earth.", "雲は天地の間に"),
        ("l04", 20.82, 24.12, "想念像风，靠近你身边", "Longing moves like wind, drawing close beside you.", "想いは風のように、君のそばへ"),
        ("l05", 24.12, 25.96, "望着那么远", "I gaze toward the far distance.", "遠くを見つめて"),
        ("l06", 25.96, 28.98, "却像在眼前", "Yet it feels right before my eyes.", "それでも目の前みたい"),
        ("l07", 30.36, 33.50, "慢慢地靠近，一点一点", "Slowly drawing near, little by little.", "ゆっくり近づく、一歩ずつ"),
        ("l08", 33.50, 36.20, "穿过云海", "Crossing the sea of clouds.", "雲海を越えて"),
        ("l09", 36.20, 38.94, "落进心里面", "Falling into the heart.", "心の奥へ落ちていく"),
        ("l10", 38.94, 40.76, "我随流年", "I move with the passing years.", "流れる歳月とともに"),
        ("l11", 40.76, 43.06, "来到你身边", "To come beside you.", "君のそばへ行きたい"),
        ("l12", 43.06, 46.16, "看清你的容颜", "To see your face clearly.", "その顔を見つめたい"),
        ("l13", 46.16, 48.88, "隔着山海万千", "Though mountains and seas divide us.", "山も海も隔てても"),
        ("l14", 48.88, 51.60, "也想和你相见", "I still want to meet you.", "それでも君に会いたい"),
        ("l15", 51.60, 54.40, "似水流年", "Years flow like water.", "流れる歳月"),
        ("l16", 54.40, 58.38, "时光慢慢转，这一眼", "Time turns slowly in this one gaze.", "この一目に、時はゆっくり巡る"),
        ("l17", 58.38, 61.00, "越过千年不变", "Unchanged beyond a thousand years.", "千年を越えても変わらない"),
        ("l18", 61.00, 62.65, "云海之间", "Between clouds and sea.", "雲海の間で"),
        ("l19", 62.65, 64.66, "梦也缱绻", "Even dreams linger tenderly.", "夢さえも名残惜しい"),
        ("l20", 64.66, 68.05, "我把爱写成一条线", "I write love into one line.", "愛を一本の糸にして"),
        ("l21", 68.05, 71.60, "牵向你的天边", "Pulling toward your horizon.", "君の空の果てへつなぐ"),
        ("l22", 72.64, 74.20, "天蓝蓝", "The sky is blue.", "空は青く"),
        ("l23", 74.20, 75.76, "海蓝蓝", "The sea is blue.", "海は青く"),
        ("l24", 76.44, 80.22, "我在远方", "I am far away.", "僕は遠い場所にいて"),
        ("l25", 80.22, 83.46, "仍想回到你身边", "Still wanting to return beside you.", "それでも君のそばへ帰りたい"),
    ]


def build_tracks() -> dict[str, list[dict[str, Any]]]:
    lines = {"zh-Hans": [], "en": [], "ja": []}
    for line_id, start, end, zh, en, ja in corrected_rows():
        lines["zh-Hans"].append(make_line(line_id, start, end, zh, "zh-Hans"))
        lines["en"].append(make_line(line_id, start, end, en, "en"))
        lines["ja"].append(make_line(line_id, start, end, ja, "ja"))
    return lines


def load_chords() -> list[dict[str, Any]]:
    chords: list[dict[str, Any]] = []
    with (ANALYSIS / "analysis/chords.csv").open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            chords.append(
                {
                    "start": round(float(row["start"]), 3),
                    "end": round(float(row["end"]), 3),
                    "name": row["chord"],
                    "degree": "",
                }
            )
    return chords


def copy_cover() -> str:
    source = ROOT / "website/assets/covers/yun-hai-zhi-lian-imagegen-16x9.png"
    if not source.exists():
        source = ROOT / "website/assets/covers/yun-hai-zhi-lian-16x9.png"
    target = ROOT / f"website/assets/covers/{MEDIA_ID}-16x9.png"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return f"assets/covers/{MEDIA_ID}-16x9.png"


def copy_audio() -> None:
    target = SONGS / "audio/yun-hai-zhi-lian-haifeng-duange-zh-Hans-ace-20260630.mp3"
    target.parent.mkdir(parents=True, exist_ok=True)
    if not SELECTED_AUDIO.exists():
        raise FileNotFoundError(SELECTED_AUDIO)
    shutil.copy2(SELECTED_AUDIO, target)
    subprocess.run(["node", "scripts/build-audio-json.js"], cwd=SONGS, check=True)


def write_media_item() -> None:
    media_dir = ROOT / "website/data/songs" / MEDIA_ID
    cover = copy_cover()
    tracks = build_tracks()
    for code, lines in tracks.items():
        write_json(media_dir / "lyrics/zh-vocal" / f"{code}.json", track(code, lines))
    timeline = [{"id": line["id"], "start": line["start"], "end": line["end"], "text": line["text"]} for line in tracks["zh-Hans"]]

    manifest = {
        "schema": "fun.lazying.media.manifest.v1",
        "version": 1,
        "id": MEDIA_ID,
        "kind": "song",
        "title": "云海之恋 · 海风短歌",
        "localizedTitles": {
            "zh-Hans": "云海之恋 · 海风短歌",
            "en": "Cloud Sea Love · Sea-Breeze Song",
            "ja": "雲海の恋・海風短歌",
        },
        "artist": "Musia",
        "description": "A concise ACE-Step Mandarin cloud-sea love ballad, corrected against its selected vocal render.",
        "caption": "A short sea-breeze version of the cloud-and-sea love song.",
        "duration": round(duration(SELECTED_AUDIO), 3),
        "canonicalUrl": f"https://fun.lazying.art/#{MEDIA_ID}",
        "share": {
            "title": "云海之恋 · 海风短歌 - Fun Lazying Art",
            "description": "A Musia ACE-Step Mandarin cloud-sea love ballad with corrected trilingual lyrics.",
            "url": f"https://fun.lazying.art/#{MEDIA_ID}",
            "image": cover,
            "siteName": "Fun Lazying Art",
        },
        "assets": {
            "cover": {"id": "cover", "label": "云海之恋 · 海风短歌 cover", "role": "cover", "src": cover, "mime": "image/png", "width": 1600, "height": 900},
            "poster": {"id": "poster", "label": "16:9 Poster", "role": "poster", "src": cover, "mime": "image/png", "width": 1600, "height": 900},
            "primaryAudio": {
                "id": "haifeng-duange-zh",
                "label": "中文",
                "roleLabel": "Vocal",
                "role": "vocal",
                "languageCode": "zh-Hans",
                "languageLabel": "中文",
                "lyricSetId": "zh-vocal",
                "src": PUBLIC_AUDIO,
                "mime": "audio/mpeg",
            },
            "alternateAudio": [],
        },
        "musical": {
            "key": "D major / detected A-centered cadence",
            "bpm": 75.99954044117646,
            "timeSignature": "4/4",
            "chords": load_chords(),
        },
        "textTracks": [],
        "lyricSets": [
            {
                "id": "zh-vocal",
                "label": "中文 vocal",
                "languageCode": "zh-Hans",
                "tracks": [
                    {"code": "zh-Hans", "label": "Mandarin Chinese", "nativeLabel": "中文", "script": "Hans", "features": ["pinyin", "active-vocal"], "path": "lyrics/zh-vocal/zh-Hans.json"},
                    {"code": "en", "label": "English", "nativeLabel": "English", "script": "Latn", "features": ["translation"], "path": "lyrics/zh-vocal/en.json"},
                    {"code": "ja", "label": "Japanese", "nativeLabel": "日本語", "script": "Jpan", "features": ["furigana", "translation"], "path": "lyrics/zh-vocal/ja.json"},
                ],
            }
        ],
        "timeline": {"unit": "seconds", "lines": timeline},
        "provenance": {
            "createdBy": "Musia",
            "generationProject": str(PROJECT.relative_to(ROOT)),
            "audioSource": "ACE-Step 1.5 XL Turbo seed 731531 selected from three tested seeds.",
            "analysisRun": str(ANALYSIS.relative_to(ROOT)),
            "quality": {"asrOverlap": 0.5235602094240838, "gate": "pass"},
            "lyricCorrection": "Corrected from same-vocal small ASR, vocal-stem medium ASR, no-VAD base/small/medium ASR, user listening feedback, and reference lyric. Opening/outro 天蓝蓝 and 海蓝蓝 were restored; ASR variants such as 天来了/海来了/天烂烂 are treated as sound-close recognition of the intended color lines. Draft bridge/final chorus were skipped/compressed by the render and are intentionally omitted from public lyrics.",
            "coverSource": cover,
            "publicAudio": "yun-hai-zhi-lian-haifeng-duange-zh-Hans-ace-20260630.mp3",
        },
        "artifacts": [],
    }
    write_json(media_dir / "manifest.json", manifest)


def rename_long_version() -> None:
    path = ROOT / "website/data/songs/yun-hai-zhi-lian/manifest.json"
    manifest = read_json(path)
    manifest["title"] = "云海之恋 · 云海长歌"
    manifest["localizedTitles"] = {
        "zh-Hans": "云海之恋 · 云海长歌",
        "en": "Cloud Sea Love · Long Cloud-Sea Song",
        "ja": "雲海の恋・雲海長歌",
    }
    manifest["share"]["title"] = "云海之恋 · 云海长歌 - Fun Lazying Art"
    write_json(path, manifest)


def update_catalog() -> None:
    path = ROOT / "website/data/catalog.json"
    catalog = read_json(path)
    new_item = {
        "id": MEDIA_ID,
        "kind": "song",
        "title": "云海之恋 · 海风短歌",
        "artist": "Musia",
        "summary": "A concise ACE-Step Mandarin cloud-sea love ballad with ASR-corrected trilingual lyrics, pinyin, furigana, and chord timing.",
        "manifest": f"data/songs/{MEDIA_ID}/manifest.json",
        "cover": f"assets/covers/{MEDIA_ID}-16x9.png",
        "languages": ["zh-Hans", "en", "ja"],
        "tags": ["music", "love", "cloud-sea", "Mandarin", "ACE-Step", "short-song", "pinyin", "furigana"],
    }
    items = [item for item in catalog["items"] if item.get("id") != MEDIA_ID]
    for item in items:
        if item.get("id") == LONG_ID:
            item["title"] = "云海之恋 · 云海长歌"
            item["summary"] = "A longer spacious Mandarin cloud-sea love ballad with corrected trilingual lyrics, pinyin, furigana, and chord timing."
    long_index = next((index for index, item in enumerate(items) if item.get("id") == LONG_ID), 0)
    items.insert(long_index + 1, new_item)
    catalog["items"] = items
    write_json(path, catalog)


def main() -> None:
    copy_audio()
    rename_long_version()
    write_media_item()
    update_catalog()
    print(ROOT / "website/data/songs" / MEDIA_ID / "manifest.json")


if __name__ == "__main__":
    main()
