#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pykakasi
from pypinyin import Style, pinyin


ROOT = Path(__file__).resolve().parents[1]
SONGS = ROOT.parent / "MusiaSongs"
MEDIA_ID = "meng-you-tian-mu-original-poem"
PROJECT = ROOT / "data/creative_projects/meng-you-tian-mu-original-poem-20260701"
SELECTED_WAV = PROJECT / "selected/meng-you-tian-mu-original-poem-zh-Hans-ace-20260701-trimmed.wav"
ANALYSIS = ROOT / "data/runs/meng-you-tian-mu-original-poem-20260701-selected-trimmed-analysis"
PUBLIC_AUDIO_NAME = "meng-you-tian-mu-original-poem-zh-Hans-ace-20260701.mp3"
PUBLIC_AUDIO = f"https://lazyingart.github.io/MusiaSongs/audio/{PUBLIC_AUDIO_NAME}"
COVER = "assets/covers/meng-you-tian-mu-16x9.png"

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


def zh_pinyin_for(line_text: str, index: int, char: str) -> str:
    if not is_cjk(char):
        return ""
    overrides = {
        ("天姥", "姥"): "mu3",
        ("语天姥", "语"): "yu4",
        ("天台", "台"): "tai1",
        ("剡溪", "剡"): "shan4",
        ("渌水", "渌"): "lu4",
        ("脚著", "著"): "zhuo2",
        ("殷岩泉", "殷"): "yin3",
        ("澹澹", "澹"): "dan4",
        ("列缺", "缺"): "que1",
        ("訇然", "訇"): "hong1",
        ("霓为衣", "为"): "wei2",
        ("风为马", "为"): "wei2",
        ("鸾回车", "鸾"): "luan2",
        ("惟觉时", "惟"): "wei2",
        ("惟觉时", "觉"): "jue2",
        ("须行即骑", "行"): "xing2",
        ("须行即骑", "骑"): "qi2",
        ("安能", "能"): "neng2",
        ("摧眉折腰", "折"): "zhe2",
    }
    for needle, target in overrides:
        if needle in line_text and char == target:
            return overrides[(needle, target)]
    values = pinyin(char, style=Style.TONE3, strict=False, neutral_tone_with_five=True)
    return values[0][0] if values and values[0] else ""


def ja_reading(text: str) -> str:
    if not is_cjk(text):
        return ""
    overrides = {
        "剡": "せん",
        "溪": "けい",
    }
    if text in overrides:
        return overrides[text]
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
            reading = zh_pinyin_for(line["text"], index, part)
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
    # Timings use large-v3 no-VAD ASR on the public trimmed audio and separated
    # vocal stem. The Mandarin text keeps the original poem when the rendered
    # sound is close; unsupported skipped/garbled prompt lines are not forced.
    return [
        ("l00", 0.00, 1.38, "啊", "Ah.", "ああ"),
        ("l01", 31.72, 35.10, "海客谈瀛洲", "Sea travelers speak of Yingzhou.", "海の旅人は瀛洲を語る"),
        ("l02", 37.82, 41.24, "烟涛微茫信难求", "Mist and waves are dim, truly hard to seek.", "煙る波はかすかで、まことに求めがたい"),
        ("l03", 41.24, 47.34, "云霞明灭或可睹", "Clouds and rosy light flicker, perhaps visible.", "雲霞は明滅し、あるいは見ることができる"),
        ("l04", 49.48, 53.88, "天姥连天向天横", "Tianmu joins the sky and stretches across heaven.", "天姥は天に連なり、空へ横たわる"),
        ("l05", 54.88, 59.46, "天台四万八千丈", "Tiantai rises forty-eight thousand zhang.", "天台は四万八千丈"),
        ("l06", 60.60, 65.16, "对此欲倒东南倾", "Before it, one would lean and fall southeast.", "これに向かえば東南へ倒れ傾くほどだ"),
        ("l07", 66.78, 69.02, "湖月照我影", "The lake moon shines on my shadow.", "湖の月がわが影を照らす"),
        ("l08", 69.02, 71.22, "送我至剡溪", "It sends me to Shanxi stream.", "私を剡溪へ送る"),
        ("l09", 72.10, 74.00, "谢公宿处", "Where Lord Xie once stayed.", "謝公が宿ったところ"),
        ("l10", 74.00, 77.10, "渌水荡漾清猿啼", "Green waters ripple; clear gibbons cry.", "緑の水は揺れ、清い猿が啼く"),
        ("l11", 77.10, 79.66, "脚著谢公屐", "My feet wear Xie Gong's clogs.", "足には謝公の木履を履く"),
        ("l12", 79.66, 82.48, "身登青云梯", "My body climbs the ladder of blue clouds.", "身は青雲の梯を登る"),
        ("l13", 83.74, 87.42, "迷花倚石忽已暝", "Lost among flowers and leaning on stone, dusk suddenly falls.", "花に迷い石にもたれ、忽ち日が暮れる"),
        ("l14", 88.66, 92.70, "半壁见海日，空中闻天鸡", "On the cliffside I see the sea sun; in the air I hear the heavenly rooster.", "半壁に海日を見、空中に天鶏を聞く"),
        ("l15", 94.24, 99.82, "千岩万转路不定，迷花倚石忽已暝", "A thousand cliffs twist; the road is uncertain; among flowers and stone, dusk arrives.", "千岩万転して道は定まらず、花に迷い石に倚れば忽ち暝い"),
        ("l16", 99.82, 106.70, "熊咆龙吟殷岩泉，栗深林兮惊层巅", "Bears roar, dragons chant, the rock springs rumble; deep woods tremble, peaks are startled.", "熊は咆え龍は吟じ岩泉は殷と鳴り、深林は慄き峰を驚かす"),
        ("l17", 106.70, 112.50, "水澹澹兮生烟", "The waters shimmer and give birth to mist.", "水は澹澹として煙を生む"),
        ("l18", 116.40, 117.92, "列缺霹雳", "Lightning splits and thunder crashes.", "稲妻が裂け霹靂が鳴る"),
        ("l19", 120.88, 122.58, "丘峦崩摧", "Hills and ridges collapse and break.", "丘や峰が崩れ砕ける"),
        ("l20", 124.08, 125.74, "洞天石扉", "The stone doors of the cave heaven.", "洞天の石の扉"),
        ("l21", 127.30, 130.08, "訇然中开", "Open in a thunderous crash.", "轟然として中から開く"),
        ("l22", 132.10, 137.96, "青冥浩荡不见底，日月照耀金银台", "The blue vastness has no bottom; sun and moon shine on gold and silver towers.", "青冥は浩蕩として底も見えず、日月は金銀台を照らす"),
        ("l23", 137.96, 141.40, "霓为衣兮风为马", "Rainbow is their robe, wind is their horse.", "虹を衣とし、風を馬とする"),
        ("l24", 141.40, 146.60, "云之君兮纷纷而来下", "Lords of the clouds descend in profusion.", "雲の君が次々と降りて来る"),
        ("l25", 150.04, 152.02, "虎鼓瑟兮", "Tigers beat the zithers.", "虎が瑟を鼓す"),
        ("l26", 152.02, 156.98, "鸾回车，仙之人兮列如麻", "Phoenixes wheel the carriages; immortals stand thick as hemp.", "鸞は車を巡らせ、仙人は麻のように列なる"),
        ("l27", 156.98, 164.40, "忽魂悸以魄动，恍惊起而长嗟", "Suddenly my soul trembles; startled awake, I sigh long.", "忽ち魂が悸き魄が動き、恍として驚き起き長く嘆く"),
        ("l28", 164.40, 168.16, "惟觉时之枕席", "I find only the pillow and mat when awake.", "ただ目覚めた時の枕席のみがある"),
        ("l29", 168.16, 172.36, "世间行乐亦如此", "The pleasures of the world are like this.", "世の楽しみもまたこのようなもの"),
        ("l30", 175.86, 179.58, "古来万事东流水", "Since ancient times, all things flow east like water.", "古来万事は東へ流れる水"),
        ("l31", 204.94, 209.62, "列缺霹雳，丘峦崩摧", "Lightning and thunder; hills and ridges collapse.", "列缺霹靂し、丘巒は崩れ砕ける"),
        ("l32", 210.80, 215.64, "洞天石扉，訇然中开", "The stone doors of cave heaven open with a crash.", "洞天の石扉は轟然として開く"),
        ("l33", 218.72, 223.32, "云之君兮纷纷而来下", "Lords of the clouds descend in profusion.", "雲の君が次々と降りて来る"),
        ("l34", 225.42, 228.20, "虎鼓瑟兮鸾回车", "Tigers beat the zithers; phoenixes wheel the carriages.", "虎は瑟を鼓し、鸞は車を巡らせる"),
        ("l35", 228.20, 231.02, "仙之人兮列如麻", "Immortals stand in rows like hemp.", "仙人は麻のように列なる"),
        ("l36", 231.02, 236.52, "忽魂悸以魄动，恍惊起而长嗟", "My soul trembles; startled awake, I sigh long.", "魂は悸き魄は動き、驚き起きて長く嘆く"),
        ("l37", 238.24, 241.16, "惟觉时之枕席", "I find only the pillow and mat when awake.", "ただ目覚めた時の枕席のみがある"),
        ("l38", 243.20, 245.88, "失向来之烟霞", "The mists and cloudlight just seen are lost.", "さきほどの煙霞は失われる"),
        ("l39", 247.08, 251.14, "世间行乐亦如此", "The pleasures of the world are like this.", "世の楽しみもまたこのようなもの"),
        ("l40", 251.14, 253.34, "古来万事东流水", "Since ancient times, all things flow east like water.", "古来万事は東へ流れる水"),
        ("l41", 254.90, 260.08, "别君去兮何时还", "I leave you; when shall I return?", "君に別れて去れば、いつ帰るだろう"),
        ("l42", 260.08, 264.48, "须行即骑访名山", "When I must go, I ride to visit famous mountains.", "行くべき時はすぐ騎って名山を訪ねる"),
        ("l43", 264.48, 271.54, "安能摧眉折腰事权贵", "How could I bow my brows and bend my waist to serve the powerful?", "どうして眉を低くし腰を折って権貴に仕えようか"),
        ("l44", 271.54, 276.72, "使我不得开心颜", "And lose my free and happy face?", "それで私の晴れやかな顔を失うなど"),
        ("l45", 286.70, 293.88, "使我不得开心颜", "And lose my free and happy face?", "それで私の晴れやかな顔を失うなど"),
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
                "Original-poem ACE route selected from seven candidates. Public audio is the trimmed seed 733105 render. "
                "Large-v3 ASR on the trimmed mix and vocal stem was used for timing. The active Mandarin track keeps Li Bai's "
                "original wording where the audio is sound-close, reflects repeated gate/immortal sections, and omits prompt "
                "lines that were skipped or too garbled to publish truthfully."
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
    raw = read_json(ANALYSIS / "analysis/chords.json").get("chords", [])
    return [
        {
            "start": round(float(item["start"]), 3),
            "end": round(float(item["end"]), 3),
            "name": item.get("chord") or item.get("name") or "N.C.",
            "degree": "",
        }
        for item in raw
    ]


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
            "-vn",
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
        "title": "梦游天姥吟留别 · 原诗版",
        "localizedTitles": {
            "zh-Hans": "梦游天姥吟留别 · 原诗版",
            "en": "Dreaming of Tianmu · Original Poem",
            "ja": "夢遊天姥吟留別・原詩版",
        },
        "artist": "Musia",
        "description": "A Mandarin ACE-Step original-poem render using Li Bai's 梦游天姥吟留别 as the lyric source, with large-v3 ASR-corrected timing.",
        "caption": "A long dream-mountain poem song: sea mist, moonlit flight, thunder gates, immortals, waking, and the refusal to bow.",
        "duration": round(duration(SELECTED_WAV), 3),
        "canonicalUrl": f"https://fun.lazying.art/#{MEDIA_ID}",
        "share": {
            "title": "梦游天姥吟留别 · 原诗版 - Fun Lazying Art",
            "description": "Musia ACE-Step original-poem version of Li Bai's 梦游天姥吟留别.",
            "url": f"https://fun.lazying.art/#{MEDIA_ID}",
            "image": COVER,
            "siteName": "Fun Lazying Art",
        },
        "assets": {
            "cover": {"id": "cover", "label": "梦游天姥吟留别 原诗版 cover", "role": "cover", "src": COVER, "mime": "image/png", "width": 1600, "height": 900},
            "poster": {"id": "poster", "label": "16:9 Poster", "role": "poster", "src": COVER, "mime": "image/png", "width": 1600, "height": 900},
            "primaryAudio": {
                "id": "meng-you-tian-mu-original-poem-zh",
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
            "key": "D minor requested; detected mixed cinematic progression",
            "bpm": round(float(run_manifest.get("tempo_bpm", 172.265625)), 3),
            "timeSignature": "4/4",
            "chords": load_chords(),
        },
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
        "textTracks": [],
        "timeline": {"unit": "seconds", "lines": timeline},
        "artifacts": [],
        "provenance": {
            "createdBy": "Musia",
            "generationProject": str(PROJECT.relative_to(ROOT)),
            "audioSource": "ACE-Step 1.5 turbo long-form no-label original-poem route, seed 733105; public version trimmed from 330s to 296s.",
            "analysisRun": str(ANALYSIS.relative_to(ROOT)),
            "quality": {
                "smallAsrOverlap": 0.3543859649122807,
                "selectedLargeV3Overlap": 0.43859649122807015,
                "vocalStemLargeV3Overlap": 0.4456140350877193,
                "gate": "pass-with-caveats",
            },
            "lyricCorrection": (
                "Corrected 2026-07-01 from large-v3 normal/no-VAD ASR on the trimmed selected audio and trimmed vocal stem. "
                "The source prompt used the full original poem. The render is beautiful and song-like but not a perfect classical recitation: "
                "the opening and several dense classical phrases are blurred, while the heaven-gate/immortal/freedom sections are clearer and partly repeated."
            ),
            "lyricCorrectionEvidence": [
                str((PROJECT / "correction_packets/selected-trimmed-large-v3/CORRECTION_PACKET.md").relative_to(ROOT)),
                str((PROJECT / "correction_packets/selected-trimmed-large-v3/selected-large-v3-no-vad.json").relative_to(ROOT)),
                str((PROJECT / "correction_packets/selected-trimmed-large-v3/vocal-stem-large-v3-no-vad.json").relative_to(ROOT)),
            ],
            "pronunciationGuide": str((PROJECT / "source/pronunciation-guide.md").relative_to(ROOT)),
            "coverSource": COVER,
            "publicAudio": PUBLIC_AUDIO_NAME,
        },
    }
    write_json(media_dir / "manifest.json", manifest)


def update_catalog() -> None:
    path = ROOT / "website/data/catalog.json"
    catalog = read_json(path)
    item = {
        "id": MEDIA_ID,
        "kind": "song",
        "title": "梦游天姥吟留别 · 原诗版",
        "artist": "Musia",
        "summary": "A long-form ACE-Step Mandarin original-poem version of Li Bai's 梦游天姥吟留别, with ASR-corrected trilingual lyrics, pinyin, furigana, and chord timing.",
        "manifest": f"data/songs/{MEDIA_ID}/manifest.json",
        "cover": COVER,
        "languages": ["zh-Hans", "en", "ja"],
        "tags": ["music", "Li Bai", "Tang poetry", "Mandarin", "ACE-Step", "original-poem", "xianxia", "pinyin", "furigana"],
    }
    items = [entry for entry in catalog.get("items", []) if entry.get("id") != MEDIA_ID]
    insert_at = next((index for index, entry in enumerate(items) if entry.get("id") == "meng-you-tian-mu"), len(items))
    items.insert(insert_at, item)
    catalog["items"] = items
    write_json(path, catalog)


def main() -> None:
    ensure_audio()
    write_media_item()
    update_catalog()
    print(f"https://fun.lazying.art/#{MEDIA_ID}")


if __name__ == "__main__":
    main()
