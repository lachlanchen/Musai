#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pykakasi
from pypinyin import Style, pinyin


ROOT = Path(__file__).resolve().parents[1]
SONGS = ROOT.parent / "MusiaSongs"
MEDIA_ID = "xia-ke-xing-original-poem"
PROJECT = ROOT / "data/creative_projects/xia-ke-xing-original-poem-rerun-20260701"
SELECTED_WAV = PROJECT / "ace_outputs/zh_turbo_direct_start/6cafb2cb-ed99-9aa6-bb76-de0b56df38d0.wav"
ANALYSIS = ROOT / "data/runs/xia-ke-xing-original-poem-rerun-20260701-seed734114-analysis"
PUBLIC_AUDIO_NAME = "xia-ke-xing-original-poem-zh-Hans-ace-rerun-20260701.mp3"
PUBLIC_AUDIO = f"https://lazyingart.github.io/MusiaSongs/audio/{PUBLIC_AUDIO_NAME}"
COVER = "assets/covers/xia-ke-xing-original-poem-16x9.png"

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


def zh_pinyin_for(line_text: str, char: str) -> str:
    if not is_cjk(char):
        return ""
    overrides = {
        ("飒沓", "沓"): "ta4",
        ("事了", "了"): "liao3",
        ("不留行", "行"): "xing2",
        ("五岳倒为轻", "为"): "wei2",
        ("烜赫", "烜"): "xuan3",
    }
    for (needle, target), reading in overrides.items():
        if needle in line_text and char == target:
            return reading
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
        token = {"text": part, "start": round(start + step * index, 3), "end": round(start + step * (index + 1), 3)}
        if code == "zh-Hans":
            reading = zh_pinyin_for(line["text"], part)
            if reading:
                token["pinyin"] = reading
        elif code == "ja":
            reading = ja_reading(part)
            if reading:
                token["reading"] = reading
        tokens.append(token)
    return tokens


def make_line(line_id: str, start: float, end: float, text: str, code: str) -> dict[str, Any]:
    line = {
        "id": line_id,
        "start": round(start, 3),
        "end": round(end, 3),
        "text": text,
        "singableText": text,
        "role": "lyric",
    }
    line["tokens"] = tokens_for(line, code)
    return line


def corrected_rows() -> list[tuple[str, float, float, str, str, str]]:
    # Rerun seed 734114 was selected from fifteen exact-poem ACE passes. Timings
    # and line choices are based on selected-audio and vocal-stem large-v3 ASR,
    # with no-VAD segments used for repeated/soft phrases. Preserve Li Bai's
    # wording where the rendered syllables are sound-close; show repeats where
    # the model actually repeats a phrase.
    return [
        ("l01", 10.66, 14.92, "赵客缦胡缨，吴钩霜雪明", "Zhao knights wear rough Hu tassels; Wu hooks gleam like frost and snow.", "趙の侠客は胡の冠紐をまとい、呉鉤は霜雪のように明るい"),
        ("l02", 16.46, 21.20, "银鞍照白马，飒沓如流星", "Silver saddles shine on white horses, swift as falling stars.", "銀の鞍は白馬を照らし、颯沓として流星のように駆ける"),
        ("l03", 22.18, 26.78, "十步杀一人，千里不留行", "In ten steps, one man falls; across a thousand miles, no trace remains.", "十歩に一人を斬り、千里にも行跡を残さない"),
        ("l04", 26.78, 31.66, "事了拂衣去，千里不留行", "The deed done, he brushes his robe and leaves, leaving no trace.", "事が終われば衣を払って去り、行跡を残さない"),
        ("l05", 31.66, 36.24, "事了拂衣去，深藏身与名", "The deed done, he brushes his robe and hides both body and name.", "事が終われば衣を払って去り、身も名も深く隠す"),
        ("l06", 39.88, 43.94, "闲过信陵饮，脱剑膝前横", "At ease he drinks with Xinling, sword laid across his knees.", "信陵のもとで酒を飲み、剣を脱いで膝前に横たえる"),
        ("l07", 45.52, 49.82, "将炙啖朱亥，持觞劝侯嬴", "He offers roast meat to Zhu Hai and raises a cup to Hou Ying.", "炙り肉を朱亥にすすめ、杯を持って侯嬴に勧める"),
        ("l08", 51.00, 55.42, "三杯吐然诺，五岳倒为轻", "After three cups, his pledge is spoken; the Five Peaks seem light.", "三杯の後に約束を口にすれば、五岳も軽くなる"),
        ("l09", 55.42, 59.90, "眼花耳热后，意气素霓生", "Eyes dazzle, ears burn, and his spirit rises like a white rainbow.", "目はくらみ耳は熱し、意気は白い虹のように生じる"),
        ("l10", 60.42, 65.60, "救赵挥金槌，邯郸先震惊", "To rescue Zhao, he swings the golden hammer; Handan trembles first.", "趙を救わんと金槌を振るい、邯鄲はまず震え驚く"),
        ("l11", 65.60, 71.02, "千秋二壮士，烜赫大梁城", "For a thousand autumns, the two heroes blaze through Daliang city.", "千秋に二人の壮士あり、大梁の城に赫々と名をあげる"),
        ("l12", 71.02, 75.98, "纵死侠骨香，不惭世上英", "Even in death, knightly bones are fragrant, not ashamed before heroes.", "たとえ死しても侠骨は香り、世の英傑に恥じない"),
        ("l13", 77.10, 81.18, "谁能书阁下，白首太玄经", "Who would write below the tower, white-haired over the Taixuan classic?", "誰が閣下に記し、白髪で太玄経に向かうのか"),
        ("l14", 90.50, 93.42, "白首太玄经", "White-haired over the Taixuan classic.", "白髪で太玄経に向かう"),
    ]


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
                "Original-poem ACE rerun. Seed 734114 selected from fifteen exact-poem candidates. "
                "Timings use selected-audio and vocal-stem large-v3 ASR plus no-VAD segment anchors. "
                "The active Mandarin text preserves Li Bai's original poem where rendered syllables are sound-close, "
                "shows the rendered repeat around 千里不留行/事了拂衣去, and omits no-VAD hallucinated credits "
                "inside the silent intro."
            ),
        },
    }


def build_tracks() -> dict[str, list[dict[str, Any]]]:
    lines = {"zh-Hans": [], "en": [], "ja": []}
    for line_id, start, end, zh, en, ja in corrected_rows():
        lines["zh-Hans"].append(make_line(line_id, start, end, zh, "zh-Hans"))
        lines["en"].append(make_line(line_id, start, end, en, "en"))
        lines["ja"].append(make_line(line_id, start, end, ja, "ja"))
    return lines


def load_chords() -> list[dict[str, Any]]:
    raw_path = ANALYSIS / "analysis/chords.json"
    if raw_path.exists():
        raw = read_json(raw_path).get("chords", [])
        return [
            {
                "start": round(float(item["start"]), 3),
                "end": round(float(item["end"]), 3),
                "name": item.get("chord") or item.get("name") or "N.C.",
                "degree": "",
            }
            for item in raw
        ]
    chords: list[dict[str, Any]] = []
    with (ANALYSIS / "analysis/chords.csv").open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            chords.append({"start": round(float(row["start"]), 3), "end": round(float(row["end"]), 3), "name": row["chord"], "degree": ""})
    return chords


def ensure_audio() -> None:
    if not SELECTED_WAV.exists():
        raise FileNotFoundError(f"Missing selected WAV: {SELECTED_WAV}")
    target = SONGS / "audio" / PUBLIC_AUDIO_NAME
    target.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(SELECTED_WAV),
            "-codec:a",
            "libmp3lame",
            "-b:a",
            "320k",
            str(target),
        ],
        check=True,
    )
    subprocess.run(["node", "scripts/build-audio-json.js"], cwd=SONGS, check=True)


def write_media_item() -> None:
    cover_path = ROOT / "website" / COVER
    if not cover_path.exists():
        raise FileNotFoundError(f"Missing cover: {cover_path}")
    media_dir = ROOT / "website/data/songs" / MEDIA_ID
    tracks = build_tracks()
    for code, lines in tracks.items():
        write_json(media_dir / "lyrics/zh-vocal" / f"{code}.json", track(code, lines))
    timeline = [{"id": line["id"], "start": line["start"], "end": line["end"], "text": line["text"]} for line in tracks["zh-Hans"]]
    run_manifest = read_json(ANALYSIS / "manifest.json")
    manifest = {
        "schema": "fun.lazying.media.manifest.v1",
        "version": 1,
        "id": MEDIA_ID,
        "kind": "song",
        "title": "侠客行 · 原诗版",
        "localizedTitles": {
            "zh-Hans": "侠客行 · 原诗版",
            "en": "Knight-Errant Ballad · Original Poem",
            "ja": "侠客行・原詩版",
        },
        "artist": "Musia",
        "description": "An ACE-Step original-poem rerun using Li Bai's 侠客行 text as the lyric source, with large-v3 ASR-audited trilingual website lyrics.",
        "caption": "A white horse, moonlit sword light, and Li Bai's original poem set as a wuxia art song.",
        "duration": round(duration(SELECTED_WAV), 3),
        "canonicalUrl": f"https://fun.lazying.art/#{MEDIA_ID}",
        "share": {
            "title": "侠客行 · 原诗版 - Fun Lazying Art",
            "description": "Musia ACE original-poem version of Li Bai's 侠客行.",
            "url": f"https://fun.lazying.art/#{MEDIA_ID}",
            "image": COVER,
            "siteName": "Fun Lazying Art",
        },
        "assets": {
            "cover": {"id": "cover", "label": "侠客行 原诗版 cover", "role": "cover", "src": COVER, "mime": "image/png", "width": 1600, "height": 900},
            "poster": {"id": "poster", "label": "16:9 Poster", "role": "poster", "src": COVER, "mime": "image/png", "width": 1600, "height": 900},
            "primaryAudio": {
                "id": "xia-ke-xing-original-poem-zh",
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
        "playback": {"defaultMode": "single"},
        "musical": {
            "key": "D minor requested / detected mixed E minor centered wuxia progression",
            "bpm": round(float(run_manifest.get("tempo_bpm", 86.1328125)), 3),
            "timeSignature": "4/4",
            "chords": load_chords(),
        },
        "lyricSets": [
            {
                "id": "zh-vocal",
                "label": "中文 vocal",
                "languageCode": "zh-Hans",
                "tracks": [
                    {
                        "code": "zh-Hans",
                        "label": "Mandarin Chinese",
                        "nativeLabel": "中文",
                        "script": "Hans",
                        "features": ["pinyin", "active-vocal"],
                        "path": "lyrics/zh-vocal/zh-Hans.json",
                    },
                    {
                        "code": "en",
                        "label": "English",
                        "nativeLabel": "English",
                        "script": "Latn",
                        "features": ["translation"],
                        "path": "lyrics/zh-vocal/en.json",
                    },
                    {
                        "code": "ja",
                        "label": "Japanese",
                        "nativeLabel": "日本語",
                        "script": "Jpan",
                        "features": ["furigana", "translation"],
                        "path": "lyrics/zh-vocal/ja.json",
                    },
                ],
            }
        ],
        "textTracks": [],
        "timeline": {"unit": "seconds", "lines": timeline},
        "artifacts": [],
        "provenance": {
            "createdBy": "Musia",
            "generationProject": "data/creative_projects/xia-ke-xing-original-poem-rerun-20260701",
            "audioSource": "ACE-Step 1.5 non-XL turbo direct-start seed 734114, selected from fifteen exact-poem rerun candidates.",
            "analysisRun": str(ANALYSIS.relative_to(ROOT)),
            "quality": {
                "quickSmallAsrOverlap": 0.275,
                "selectedAudioLargeV3Overlap": 0.3333333333333333,
                "vocalStemLargeV3Overlap": 0.3416666666666667,
                "gate": "rerun-selected-review",
            },
            "lyricCorrection": (
                "ASR-realigned original-poem rerun, updated 2026-07-01 after quick small screening of fifteen candidates and "
                "large-v3 correction on selected audio plus separated vocal stem. The active Mandarin lyric preserves the original poem "
                "where sound-close, reflects the rendered repeat around 千里不留行/事了拂衣去, and keeps a repeated 白首太玄经 tail. "
                "A vocal-stem no-VAD pass hallucinated 作词/作曲 李宗盛 during the silent intro; silencedetect and full-mix ASR do not support publishing that as lyric. "
                "This is improved over the old seed 731903 item but remains an imperfect exact classical-poem render."
            ),
            "coverSource": "/home/lachlan/.codex/generated_images/019f0842-25ba-7bd2-9d4b-0b1c60d8a951/ig_0075c3bed0eb0cd1016a440b08763c8191833a70b775131ef6.png",
            "publicAudio": PUBLIC_AUDIO_NAME,
        },
    }
    write_json(media_dir / "manifest.json", manifest)

    catalog_path = ROOT / "website/data/catalog.json"
    catalog = read_json(catalog_path)
    item = {
        "id": MEDIA_ID,
        "kind": "song",
        "title": "侠客行 · 原诗版",
        "artist": "Musia",
        "manifest": f"data/songs/{MEDIA_ID}/manifest.json",
        "cover": COVER,
        "tags": ["song", "li-bai", "tang-poetry", "wuxia", "ace", "original-poem", "rerun"],
        "languages": ["zh-Hans", "en", "ja"],
    }
    catalog["items"] = [entry for entry in catalog.get("items", []) if entry.get("id") != MEDIA_ID]
    insert_at = 1 if catalog.get("items") else 0
    catalog["items"].insert(insert_at, item)
    write_json(catalog_path, catalog)


def main() -> None:
    ensure_audio()
    write_media_item()
    print(f"https://fun.lazying.art/#{MEDIA_ID}")


if __name__ == "__main__":
    main()
