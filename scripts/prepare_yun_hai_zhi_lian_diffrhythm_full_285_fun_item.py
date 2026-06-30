#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from pypinyin import Style, pinyin
import pykakasi


ROOT = Path(__file__).resolve().parents[1]
SONGS = ROOT.parent / "MusiaSongs"
MEDIA_ID = "yun-hai-zhi-lian"
PROJECT = ROOT / "data/creative_projects/yun-hai-zhi-lian-diffrhythm-full-20260630"
ANALYSIS = ROOT / "data/runs/yun-hai-zhi-lian-diffrhythm-full-285-clean-analysis"
SELECTED_AUDIO = PROJECT / "selected/yun-hai-zhi-lian-yunhai-changge-diffrhythm-full-285-20260630.mp3"
PUBLIC_AUDIO = "https://lazyingart.github.io/MusiaSongs/audio/yun-hai-zhi-lian-yunhai-changge-diffrhythm-full-285-20260630.mp3"

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

ZH_LINES = [
    "天蓝蓝",
    "海蓝蓝",
    "云在天地间",
    "想念像风一样",
    "依偎在你身边",
    "望着那么远",
    "却像在眼前",
    "慢慢，慢慢",
    "一点，一点",
    "穿过云海",
    "落进心里面",
    "我好想来到你身边",
    "看清你的容颜",
    "哪怕隔着山海万千",
    "也想与你相见",
    "似水流年",
    "时光轮转",
    "这一眼，越过千年不变",
    "云海之间",
    "梦也缱绻",
    "我把爱写成一线",
    "牵向你的天边",
    "你在那么远",
    "远过了人间",
    "像星光沉入海面",
    "明灭之间",
    "我在云的这边",
    "你在海的那边",
    "一念成渊",
    "一望无边",
    "越是想靠近",
    "越怕渐行渐远",
    "我好想来到你身边",
    "听清你的心愿",
    "哪怕风把岁月吹散",
    "也记得初见",
    "似水流年",
    "时光轮转",
    "这一眼，越过千年不变",
    "云海之间",
    "爱也深浅",
    "我把心化作一线",
    "追向你的天边",
    "若有一天",
    "云散海也安眠",
    "愿我仍能在风里",
    "听见你的誓言",
    "若这一生",
    "只够遥遥一眼",
    "我也愿把所有思念",
    "留在云海之间",
    "似水流年",
    "时光轮转",
    "这一念，越过千年不变",
    "云海之间",
    "山河悠远",
    "你是我望不尽的天",
    "也是我回不去的岸",
    "天蓝蓝",
    "海蓝蓝",
    "云在天地间",
    "我在无尽远方",
    "仍想回到你身边",
]

EN_LINES = [
    "The sky is blue.",
    "The sea is blue.",
    "Clouds rest between heaven and earth.",
    "Longing is like the wind.",
    "It nestles close beside you.",
    "I gaze so far away.",
    "Yet you seem before my eyes.",
    "Slowly, slowly.",
    "Little by little.",
    "Crossing the sea of clouds.",
    "Falling into my heart.",
    "I long to come beside you.",
    "To see your face clearly.",
    "Though mountains and seas divide us.",
    "I still want to meet you.",
    "Years flow like water.",
    "Time turns and turns.",
    "This one glance crosses a thousand years unchanged.",
    "Between clouds and sea.",
    "Even dreams linger tenderly.",
    "I write love into one line.",
    "And lead it toward your horizon.",
    "You are so far away.",
    "Far beyond the human world.",
    "Like starlight sinking into the sea.",
    "Flickering between light and dark.",
    "I am on this side of the clouds.",
    "You are on that side of the sea.",
    "One thought becomes an abyss.",
    "One gaze becomes endless.",
    "The more I want to come near.",
    "The more I fear we drift apart.",
    "I long to come beside you.",
    "To hear your wish clearly.",
    "Even if wind scatters the years.",
    "I still remember our first meeting.",
    "Years flow like water.",
    "Time turns and turns.",
    "This one glance crosses a thousand years unchanged.",
    "Between clouds and sea.",
    "Love has depths and shallows.",
    "I turn my heart into one line.",
    "And chase it toward your horizon.",
    "If one day.",
    "The clouds part and the sea sleeps.",
    "May I still hear in the wind.",
    "The vow you once made.",
    "If this life.",
    "Allows only one distant glance.",
    "I would still place all my longing.",
    "Between the clouds and sea.",
    "Years flow like water.",
    "Time turns and turns.",
    "This one thought crosses a thousand years unchanged.",
    "Between clouds and sea.",
    "Mountains and rivers stretch far.",
    "You are the sky I cannot finish gazing at.",
    "And the shore I can never return to.",
    "The sky is blue.",
    "The sea is blue.",
    "Clouds rest between heaven and earth.",
    "I am in the endless distance.",
    "Still longing to return beside you.",
]

JA_LINES = [
    "空は青く",
    "海は青く",
    "雲は天地の間に",
    "想いは風のように",
    "君のそばに寄り添う",
    "あんなに遠く見えて",
    "それでも目の前みたい",
    "ゆっくり、ゆっくり",
    "少しずつ、少しずつ",
    "雲海を越えて",
    "心の奥へ落ちていく",
    "君のそばへ行きたい",
    "その顔を見つめたい",
    "山も海も隔てても",
    "それでも君に会いたい",
    "流れる歳月",
    "時はめぐる",
    "この一目は千年を越えても変わらない",
    "雲海の間で",
    "夢さえ名残惜しく",
    "愛を一本の線にして",
    "君の空の果てへつなぐ",
    "君はあんなに遠く",
    "人の世よりも遠く",
    "星明かりが海へ沈むように",
    "明滅のあいだ",
    "僕は雲のこちら側",
    "君は海のあちら側",
    "一念は深淵となり",
    "一望は果てしなく",
    "近づきたいほど",
    "離れていくのが怖い",
    "君のそばへ行きたい",
    "その願いを聞きたい",
    "風が歳月を散らしても",
    "初めて会った日を覚えている",
    "流れる歳月",
    "時はめぐる",
    "この一目は千年を越えても変わらない",
    "雲海の間で",
    "愛にも深さと浅さがある",
    "心を一本の線にして",
    "君の空の果てへ追いかける",
    "いつかの日に",
    "雲が晴れ海も眠るなら",
    "それでも風の中で",
    "君の誓いを聞きたい",
    "もしこの一生が",
    "遠い一目だけなら",
    "すべての想いを",
    "雲海の間に残したい",
    "流れる歳月",
    "時はめぐる",
    "この一念は千年を越えても変わらない",
    "雲海の間で",
    "山河は遥か",
    "君は見尽くせない空",
    "そして帰れない岸",
    "空は青く",
    "海は青く",
    "雲は天地の間に",
    "僕は果てない遠方にいて",
    "それでも君のそばへ帰りたい",
]


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


def lrc_times(path: Path) -> list[float]:
    times: list[float] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"\[(\d+):(\d+(?:\.\d+)?)\]", line.strip())
        if match:
            times.append(int(match.group(1)) * 60 + float(match.group(2)))
    return times


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
        token = {"text": part, "start": round(start + step * index, 3), "end": round(start + step * (index + 1), 3)}
        if code == "zh-Hans":
            reading = zh_pinyin(part)
            if reading:
                token["pinyin"] = reading
        elif code == "ja":
            reading = ja_reading(part)
            if reading:
                token["reading"] = reading
        tokens.append(token)
    return tokens


def make_line(line_id: str, start: float, end: float, text: str, code: str) -> dict[str, Any]:
    line = {"id": line_id, "start": round(start, 3), "end": round(end, 3), "text": text, "singableText": text, "role": "lyric"}
    line["tokens"] = tokens_for(line, code)
    return line


def build_lines(code: str, texts: list[str], starts: list[float], song_duration: float) -> list[dict[str, Any]]:
    lines = []
    for index, text in enumerate(texts):
        start = starts[index]
        if index + 1 < len(starts):
            end = max(start + 1.2, starts[index + 1] - 0.12)
        else:
            end = min(song_duration, start + 5.5)
        lines.append(make_line(f"l{index + 1:02d}", start, end, text, code))
    return lines


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
                "Active Mandarin timing follows the DiffRhythm 285-second LRC conditioning, "
                "cross-checked against same-vocal ASR. Sound-close ASR substitutions are corrected "
                "to the intended lyric; the selected clean render avoided the earlier credit-like outro hallucination."
            ),
            "asrRun": "data/runs/yun-hai-zhi-lian-diffrhythm-full-285-clean-analysis/analysis/lyrics.json",
        },
    }


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


def copy_audio() -> None:
    target = SONGS / "audio/yun-hai-zhi-lian-yunhai-changge-diffrhythm-full-285-20260630.mp3"
    if not SELECTED_AUDIO.exists():
        raise FileNotFoundError(SELECTED_AUDIO)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SELECTED_AUDIO, target)
    subprocess.run(["node", "scripts/build-audio-json.js"], cwd=SONGS, check=True)


def update_manifest() -> None:
    media_dir = ROOT / "website/data/songs" / MEDIA_ID
    manifest_path = media_dir / "manifest.json"
    manifest = read_json(manifest_path)
    song_duration = duration(SELECTED_AUDIO)
    starts = lrc_times(PROJECT / "lyrics/yun_hai_zhi_lian_full_285.lrc")
    if not (len(starts) == len(ZH_LINES) == len(EN_LINES) == len(JA_LINES)):
        raise SystemExit("line count mismatch")

    tracks = {
        "zh-Hans": build_lines("zh-Hans", ZH_LINES, starts, song_duration),
        "en": build_lines("en", EN_LINES, starts, song_duration),
        "ja": build_lines("ja", JA_LINES, starts, song_duration),
    }
    for code, lines in tracks.items():
        write_json(media_dir / "lyrics/zh-vocal" / f"{code}.json", track(code, lines))

    manifest["title"] = "云海之恋 · 云海长歌"
    manifest["localizedTitles"] = {
        "zh-Hans": "云海之恋 · 云海长歌",
        "en": "Cloud Sea Love · Long Cloud-Sea Song",
        "ja": "雲海の恋・雲海長歌",
    }
    manifest["description"] = "A full-length DiffRhythm Mandarin cloud-sea love ballad with LRC-conditioned lyrics corrected against ASR evidence."
    manifest["caption"] = "Between sky and sea, longing becomes one line through time."
    manifest["duration"] = round(song_duration, 3)
    manifest["share"]["title"] = "云海之恋 · 云海长歌 - Fun Lazying Art"
    manifest["share"]["description"] = "A full-length Musia DiffRhythm Mandarin cloud-sea love ballad with corrected trilingual lyrics."
    manifest["assets"]["primaryAudio"]["src"] = PUBLIC_AUDIO
    manifest["assets"]["primaryAudio"]["label"] = "中文"
    manifest["assets"]["primaryAudio"]["languageCode"] = "zh-Hans"
    manifest["assets"]["primaryAudio"]["languageLabel"] = "中文"
    manifest["assets"]["primaryAudio"]["lyricSetId"] = "zh-vocal"
    manifest["assets"]["alternateAudio"] = []
    manifest["musical"] = {
        "key": "detected C/F center",
        "bpm": 60.09265988372093,
        "timeSignature": "4/4",
        "chords": load_chords(),
    }
    manifest["timeline"] = {
        "unit": "seconds",
        "lines": [{"id": line["id"], "start": line["start"], "end": line["end"], "text": line["text"]} for line in tracks["zh-Hans"]],
    }
    manifest["provenance"] = {
        "createdBy": "Musia",
        "generationProject": "data/creative_projects/yun-hai-zhi-lian-diffrhythm-full-20260630",
        "audioSource": "DiffRhythm 1.2 full, 285-second LRC-conditioned clean prompt render.",
        "analysisRun": "data/runs/yun-hai-zhi-lian-diffrhythm-full-285-clean-analysis",
        "quality": {"asrOverlap": 0.6332378223495702, "gate": "review"},
        "lyricCorrection": "Published active Mandarin lyrics use the full user lyric with LRC timing, cross-validated with same-vocal ASR. ASR garbling is corrected back to intended phrases when sound-close.",
        "rejectedCandidate": "full_285_prompt had a credit-like ASR tail `词曲 李宗盛`; clean prompt render was selected instead.",
        "coverPrompt": "Existing Musia cloud-sea 16:9 cover: bright blue sky, ocean, soft clouds, one white line of longing, title 云海之恋.",
        "coverSource": "website/assets/covers/yun-hai-zhi-lian-16x9.png",
        "publicAudio": "yun-hai-zhi-lian-yunhai-changge-diffrhythm-full-285-20260630.mp3",
    }
    manifest["artifacts"] = [
        {
            "id": "qa-clean",
            "label": "DiffRhythm full 285 QA",
            "kind": "markdown",
            "path": "data/creative_projects/yun-hai-zhi-lian-diffrhythm-full-20260630/reviews/full-285-clean/QA.md",
        },
        {
            "id": "analysis-report",
            "label": "Musia full analysis report",
            "kind": "markdown",
            "path": "data/runs/yun-hai-zhi-lian-diffrhythm-full-285-clean-analysis/REPORT.md",
        },
    ]
    write_json(manifest_path, manifest)


def update_catalog() -> None:
    path = ROOT / "website/data/catalog.json"
    catalog = read_json(path)
    catalog["defaultMedia"] = MEDIA_ID
    for item in catalog["items"]:
        if item.get("id") == MEDIA_ID:
            item["title"] = "云海之恋 · 云海长歌"
            item["summary"] = "A full-length DiffRhythm Mandarin cloud-sea love ballad with corrected trilingual lyrics, pinyin, furigana, and chord timing."
            item["tags"] = ["music", "love", "cloud-sea", "Mandarin", "pinyin", "furigana", "DiffRhythm", "full-song"]
    write_json(path, catalog)


def main() -> None:
    copy_audio()
    update_manifest()
    update_catalog()
    print(ROOT / "website/data/songs" / MEDIA_ID / "manifest.json")


if __name__ == "__main__":
    main()
