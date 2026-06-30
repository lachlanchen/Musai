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
MEDIA_ID = "qiang-jin-jiu"
PROJECT = ROOT / "data/creative_projects/qiang-jin-jiu-20260630"
SELECTED_WAV = PROJECT / "ace_outputs/zh_corrected_20260701-000444/d9fba6aa-69e6-040c-765d-cb781f2d901b.wav"
SELECTED_MP3 = PROJECT / "selected/qiang-jin-jiu-zh-Hans-ace-20260701.mp3"
ANALYSIS = ROOT / "data/runs/qiang-jin-jiu-20260630-20260701-000551-analysis"
PUBLIC_AUDIO_NAME = "qiang-jin-jiu-zh-Hans-ace-20260701.mp3"
PUBLIC_AUDIO = f"https://lazyingart.github.io/MusiaSongs/audio/{PUBLIC_AUDIO_NAME}"

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
JA_READING_OVERRIDES = {
    "馔": "せん",
    "饌": "せん",
}


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def duration(path: Path) -> float:
    return float(
        subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nk=1:nw=1", str(path)],
            text=True,
        ).strip()
    )


def is_cjk(text: str) -> bool:
    return any("\u3400" <= char <= "\u9fff" for char in text)


def zh_pinyin_for(line_text: str, index: int, char: str) -> str:
    if not is_cjk(char):
        return ""
    if line_text.startswith("将进酒") and char == "将" and index == 0:
        return "qiang1"
    if line_text.startswith("朝如") and char == "朝" and index == 0:
        return "zhao1"
    if index > 0 and line_text[index - 1 : index + 1] == "白发" and char == "发":
        return "fa4"
    if line_text.startswith("烹羊宰牛且为乐") and char == "为":
        return "wei2"
    if line_text.startswith("烹羊宰牛且为乐") and char == "乐":
        return "le4"
    if line_text.startswith("请君为我") and char == "为":
        return "wei4"
    if line_text.startswith("千金散尽还复来") and char == "还":
        return "huan2"
    if line_text.startswith("陈王昔时宴平乐") and char == "乐":
        return "le4"
    if line_text.startswith("主人何为言少钱") and char == "为":
        return "wei2"
    if line_text.startswith("斗酒") and char == "斗":
        return "dou3"
    values = pinyin(char, style=Style.TONE3, strict=False, neutral_tone_with_five=True)
    return values[0][0] if values and values[0] else ""


def ja_reading(text: str) -> str:
    if not is_cjk(text):
        return ""
    if text in JA_READING_OVERRIDES:
        return JA_READING_OVERRIDES[text]
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
            reading = zh_pinyin_for(line["text"], index, part)
            if reading:
                item["pinyin"] = reading
        elif code == "ja":
            reading = ja_reading(part)
            if reading:
                item["reading"] = reading
        tokens.append(item)
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
    return [
        ("l01", 28.28, 33.82, "君不见黄河之水天上来", "Do you not see the Yellow River's waters descending from the sky?", "見よ、黄河の水が天より来る"),
        ("l02", 36.56, 41.98, "奔流到海不复回", "Rushing to the sea, never to return.", "奔流して海へ至り、二度と帰らない"),
        ("l03", 43.18, 46.80, "君不见高堂", "Do you not see the high hall?", "高堂を見るがよい"),
        ("l04", 46.80, 50.08, "明镜悲白发", "The bright mirror grieves over white hair.", "明鏡は白髪を悲しむ"),
        ("l05", 50.08, 54.46, "朝如青丝暮成雪", "Morning like black silk, by evening turned to snow.", "朝は青き糸、暮れには雪となる"),
        ("l06", 54.46, 58.10, "人生得意须尽欢", "When life is proud, take joy to the full.", "人生得意の時は歓びを尽くせ"),
        ("l07", 58.10, 61.82, "莫使金樽空对月", "Do not let the golden cup face the moon empty.", "金の盃を空しく月に向けるな"),
        ("l08", 61.82, 64.82, "天生我材必有用", "Heaven made my talent; it must have its use.", "天が我が才を生んだ、必ず用いられる"),
        ("l09", 64.82, 70.16, "千金散尽还复来", "A thousand gold pieces spent will return again.", "千金は散じ尽くしてもまた戻る"),
        ("l10", 70.16, 73.94, "烹羊宰牛且为乐", "Cook lamb, slaughter oxen, and take delight.", "羊を煮、牛を屠って楽しもう"),
        ("l11", 73.94, 77.66, "会须一饮三百杯", "We must drink three hundred cups.", "必ず三百杯を飲もう"),
        ("l12", 77.66, 80.90, "岑夫子，丹丘生", "Master Cen, Danqiu my friend.", "岑夫子よ、丹丘生よ"),
        ("l13", 80.90, 84.68, "将进酒，杯莫停", "Please drink; let the cup not stop.", "酒を勧めよう、杯を止めるな"),
        ("l14", 84.24, 87.46, "与君歌一曲", "I sing one song for you.", "君のために一曲歌おう"),
        ("l15", 87.46, 90.92, "请君为我倾耳听", "Please lean your ear and listen to me.", "どうか耳を傾けて聞いてほしい"),
        ("l16", 90.92, 94.28, "钟鼓馔玉不足贵", "Bells, drums, and jade banquets are not worth prizing.", "鐘鼓と饌玉は貴ぶに足りない"),
        ("l17", 94.28, 97.76, "但愿长醉不愿醒", "I only wish to stay long drunk, never wishing to wake.", "ただ長く酔い、醒めたくない"),
        ("l18", 100.70, 104.34, "钟鼓馔玉不足贵", "Bells, drums, and jade banquets are not worth prizing.", "鐘鼓と饌玉は貴ぶに足りない"),
        ("l19", 105.18, 108.32, "但愿长醉不愿醒", "I only wish to stay long drunk, never wishing to wake.", "ただ長く酔い、醒めたくない"),
        ("l20", 112.96, 115.44, "古来圣贤皆寂寞", "Since ancient times, sages and worthies have all been lonely.", "古来、聖賢は皆寂寞としている"),
        ("l21", 115.44, 119.24, "惟有饮者留其名", "Only drinkers leave their names behind.", "ただ飲む者だけが名を残す"),
        ("l22", 119.24, 122.72, "陈王昔时宴平乐", "Long ago Prince Chen feasted at Pingle.", "陳王は昔、平楽で宴を開いた"),
        ("l23", 122.72, 126.84, "斗酒十千恣欢谑", "Wine by the peck, ten thousand coins, freely laughing and jesting.", "斗酒十千、歓謔をほしいままにした"),
        ("l24", 126.84, 130.28, "古来圣贤皆寂寞", "Since ancient times, sages and worthies have all been lonely.", "古来、聖賢は皆寂寞としている"),
        ("l25", 130.28, 133.82, "惟有饮者留其名", "Only drinkers leave their names behind.", "ただ飲む者だけが名を残す"),
        ("l26", 134.58, 137.58, "陈王昔时宴平乐", "Long ago Prince Chen feasted at Pingle.", "陳王は昔、平楽で宴を開いた"),
        ("l27", 138.10, 141.58, "斗酒十千恣欢谑", "Wine by the peck, ten thousand coins, freely laughing and jesting.", "斗酒十千、歓謔をほしいままにした"),
        ("l28", 141.58, 145.90, "主人何为言少钱", "Host, why speak of having too little money?", "主人よ、なぜ金が少ないと言うのか"),
        ("l29", 145.90, 149.48, "径须沽取对君酌", "Just buy wine at once, and pour it for you.", "ただちに買い求め、君と酌もう"),
        ("l30", 149.48, 153.90, "五花马，千金裘", "The dappled horse, the thousand-gold fur robe.", "五花の馬、千金の裘"),
        ("l31", 153.90, 159.06, "呼儿将出换美酒", "Call the boy to bring them out and trade them for fine wine.", "童を呼び、持ち出して美酒に替えよう"),
        ("l32", 159.06, 164.34, "与尔同销万古愁", "Together with you, I will dissolve ten thousand ages of sorrow.", "君とともに万古の愁いを消そう"),
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
                "Active Mandarin lyrics corrected from same-vocal ASR, large-v3 vocal-stem ASR, "
                "medium/small cross-ASR, and the original poem. "
                "The lyric display preserves the user's requested original text where ASR is sound-close, "
                "including 将进酒 as qiang jin jiu. The ACE render repeats 钟鼓馔玉/但愿长醉 and "
                "古来圣贤/陈王 sections; the website reflects those repeats."
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
    chords: list[dict[str, Any]] = []
    with (ANALYSIS / "analysis/chords.csv").open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            chords.append({"start": round(float(row["start"]), 3), "end": round(float(row["end"]), 3), "name": row["chord"], "degree": ""})
    return chords


def ensure_audio() -> None:
    if not SELECTED_WAV.exists():
        raise FileNotFoundError(SELECTED_WAV)
    SELECTED_MP3.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-i", str(SELECTED_WAV), "-vn", "-codec:a", "libmp3lame", "-q:a", "2", str(SELECTED_MP3)], check=True)
    target = SONGS / "audio" / PUBLIC_AUDIO_NAME
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SELECTED_MP3, target)
    subprocess.run(["node", "scripts/build-audio-json.js"], cwd=SONGS, check=True)


def copy_cover() -> str:
    target = ROOT / f"website/assets/covers/{MEDIA_ID}-16x9.png"
    if not target.exists():
        fallback = ROOT / "website/assets/covers/xia-ke-xing-16x9.png"
        shutil.copy2(fallback, target)
    return f"assets/covers/{MEDIA_ID}-16x9.png"


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
        "title": "将进酒 · ACE Poetry Demo",
        "localizedTitles": {
            "zh-Hans": "将进酒 · ACE 诗歌版",
            "en": "Bring In the Wine · ACE Poetry Demo",
            "ja": "将進酒・ACE詩歌版",
        },
        "artist": "Musia",
        "description": "An ACE-Step female Mandarin poetry-song using Li Bai's original 将进酒 text, with pronunciation notes and ASR-corrected trilingual lyric timing.",
        "caption": "Heroic and tender Li Bai poetry-song, vast as the Yellow River and intimate as a wine cup under the moon.",
        "duration": round(duration(SELECTED_MP3), 3),
        "canonicalUrl": f"https://fun.lazying.art/#{MEDIA_ID}",
        "share": {
            "title": "将进酒 · ACE Poetry Demo - Fun Lazying Art",
            "description": "A Musia ACE-Step female Mandarin poetry-song from Li Bai's 将进酒.",
            "url": f"https://fun.lazying.art/#{MEDIA_ID}",
            "image": cover,
            "siteName": "Fun Lazying Art",
        },
        "assets": {
            "cover": {"id": "cover", "label": "将进酒 cover", "role": "cover", "src": cover, "mime": "image/png", "width": 1600, "height": 900},
            "poster": {"id": "poster", "label": "16:9 Poster", "role": "poster", "src": cover, "mime": "image/png", "width": 1600, "height": 900},
            "primaryAudio": {
                "id": "qiang-jin-jiu-zh",
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
            "key": "D minor requested / detected Abm-C#m-F# centered progression",
            "bpm": 143.5546875,
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
            "audioSource": "ACE-Step 1.5 XL Turbo seed 732002, selected from three original-text candidates.",
            "analysisRun": str(ANALYSIS.relative_to(ROOT)),
            "quality": {"asrOverlap": 0.3522727272727273, "gate": "pass"},
            "lyricCorrection": "Deep-corrected 2026-07-01 using large-v3 vocal-stem ASR plus medium/small cross-ASR. The selected render is a poetry-song using the original poem as prompt text. Because ACE does not perfectly recite every classical line, the website displays sound-close original text with actual line timing and repeats.",
            "lyricCorrectionEvidence": [
                "data/creative_projects/qiang-jin-jiu-20260630/corrections/deep-large-20260701/CORRECTION_PACKET.md",
                "data/creative_projects/qiang-jin-jiu-20260630/corrections/deep-20260701/CORRECTION_PACKET.md",
            ],
            "pronunciationGuide": str((PROJECT / "source/pronunciation-guide.md").relative_to(ROOT)),
            "coverSource": cover,
            "publicAudio": PUBLIC_AUDIO_NAME,
        },
        "artifacts": [],
    }
    write_json(media_dir / "manifest.json", manifest)


def update_catalog() -> None:
    path = ROOT / "website/data/catalog.json"
    catalog = read_json(path)
    new_item = {
        "id": MEDIA_ID,
        "kind": "song",
        "title": "将进酒 · ACE Poetry Demo",
        "artist": "Musia",
        "summary": "A female Mandarin ACE-Step poetry-song from Li Bai's original 将进酒, with pinyin, furigana, translations, and chord timing.",
        "manifest": f"data/songs/{MEDIA_ID}/manifest.json",
        "cover": f"assets/covers/{MEDIA_ID}-16x9.png",
        "languages": ["zh-Hans", "en", "ja"],
        "tags": ["music", "Li Bai", "Tang poetry", "Mandarin", "ACE-Step", "poetry-demo", "pinyin", "furigana"],
    }
    items = [item for item in catalog["items"] if item.get("id") != MEDIA_ID]
    insert_at = next((index + 1 for index, item in enumerate(items) if item.get("id") == "xia-ke-xing"), 2)
    items.insert(insert_at, new_item)
    catalog["items"] = items
    write_json(path, catalog)


def main() -> None:
    ensure_audio()
    write_media_item()
    update_catalog()
    print(ROOT / "website/data/songs" / MEDIA_ID / "manifest.json")


if __name__ == "__main__":
    main()
