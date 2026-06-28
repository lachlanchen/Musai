#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import re
from pathlib import Path

import numpy as np
import pycantonese


ROOT = Path(__file__).resolve().parents[1]
PHONE_SET = ROOT / "third_party" / "SoulX-Singer" / "soulxsinger" / "utils" / "phoneme" / "phone_set.json"


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


def load_phone_set() -> set[str]:
    phones = json.loads(PHONE_SET.read_text(encoding="utf-8"))
    return set(phones.keys() if isinstance(phones, dict) else phones)


def load_f0(path: Path) -> list[tuple[float, float]]:
    rows: list[tuple[float, float]] = []
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            raw = row.get("f0_hz") or ""
            try:
                rows.append((float(row["time"]), float(raw)))
            except ValueError:
                continue
    return rows


def hz_to_midi(frequency: float) -> int:
    if frequency <= 0:
        return 0
    return int(round(69 + 12 * math.log2(frequency / 440.0)))


def midi_to_hz(note: int) -> float:
    return 440.0 * (2.0 ** ((note - 69) / 12.0))


def f0_to_slots(f0_rows: list[tuple[float, float]], start: float, end: float, slots: int) -> list[int]:
    fallback = [62, 64, 65, 67, 69, 67, 65, 64]
    result: list[int] = []
    span = max(0.001, end - start)
    for slot_index in range(slots):
        a = start + span * slot_index / slots
        b = start + span * (slot_index + 1) / slots
        values = [freq for time, freq in f0_rows if a <= time < b and 90 <= freq <= 1200]
        if values:
            note = hz_to_midi(float(np.median(values)))
            result.append(max(48, min(78, note)))
        else:
            result.append(fallback[slot_index % len(fallback)])
    return result


def note_frames(duration: float, pitch: int, sample_rate: int = 24000, hop_size: int = 480) -> list[float]:
    frames = max(1, int(round(duration * sample_rate / hop_size)))
    if pitch <= 0:
        return [0.0] * frames
    base = midi_to_hz(pitch)
    return [round(base * (1.0 + 0.004 * math.sin(i * 0.5)), 1) for i in range(frames)]


def cjk_chars(text: str) -> list[str]:
    return [char for char in text if "\u3400" <= char <= "\u9fff"]


def char_jyutping(char: str) -> str:
    if char in MANUAL_JYUTPING:
        return MANUAL_JYUTPING[char]
    items = pycantonese.characters_to_jyutping(char)
    readings = [reading for _word, reading in items if reading]
    if not readings:
        raise ValueError(f"No Jyutping for {char}")
    syllables = readings[0].split()
    if not syllables:
        raise ValueError(f"Empty Jyutping for {char}")
    return syllables[0]


def tokens_and_phones(text: str) -> tuple[list[str], list[str]]:
    tokens: list[str] = []
    phones: list[str] = []
    for word, reading in pycantonese.characters_to_jyutping(text):
        chars = cjk_chars(word)
        if not chars:
            continue
        syllables = reading.split() if reading else []
        if len(chars) == len(syllables):
            for char, syllable in zip(chars, syllables):
                tokens.append(char)
                phones.append("yue_" + syllable.lower())
        else:
            for char in chars:
                tokens.append(char)
                phones.append("yue_" + char_jyutping(char).lower())
    if not tokens:
        raise ValueError(f"No CJK lyric tokens in {text!r}")
    return tokens, phones


def validate_phones(phones: list[str], phone_set: set[str]) -> None:
    missing = sorted({phone for phone in phones if phone not in phone_set})
    if missing:
        raise ValueError(f"Phones missing from SoulX phone_set: {missing}")


def load_source_lines(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["lines"]


def load_target_lines(path: Path) -> dict[str, str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return {item["id"]: item["text"] for item in data}
    if "lines" in data:
        return {item["id"]: item["text"] for item in data["lines"]}
    raise ValueError("target lines must be a list or an object with lines[]")


def lyric_durations(total: float, token_count: int) -> list[float]:
    lead = min(0.24, total * 0.07)
    tail = min(0.30, total * 0.08)
    available = max(0.2, total - lead - tail)
    base = available / token_count
    durations = [lead]
    for index in range(token_count):
        value = base
        if index == token_count - 1:
            value += min(0.20, base * 0.35)
        elif token_count > 1:
            value -= min(0.20 / (token_count - 1), base * 0.1)
        durations.append(max(0.07, value))
    durations.append(tail)
    scale = total / sum(durations)
    return [round(value * scale, 3) for value in durations]


def build_metadata(source_lines: list[dict], target_lines: dict[str, str], f0_rows: list[tuple[float, float]], phone_set: set[str]) -> list[dict]:
    items: list[dict] = []
    for line in source_lines:
        line_id = line["id"]
        text = target_lines.get(line_id)
        if not text:
            continue
        tokens, phones = tokens_and_phones(text)
        validate_phones(phones, phone_set)
        start = float(line["start"])
        end = float(line["end"])
        total = max(0.4, end - start)
        durations = lyric_durations(total, len(tokens))
        pitches = [0] + f0_to_slots(f0_rows, start, end, len(tokens)) + [0]
        note_type = [1] + [2] * len(tokens) + [1]
        if len(note_type) > 2:
            note_type[-2] = 3
        f0: list[float] = []
        for duration, pitch in zip(durations, pitches):
            f0.extend(note_frames(duration, pitch))
        items.append(
            {
                "index": line_id,
                "language": "Cantonese",
                "time": [int(round(start * 1000)), int(round(end * 1000))],
                "duration": " ".join(f"{value:.3f}" for value in durations),
                "text": " ".join(["<SP>"] + tokens + ["<SP>"]),
                "phoneme": " ".join(["<SP>"] + phones + ["<SP>"]),
                "note_pitch": " ".join(str(value) for value in pitches),
                "note_type": " ".join(str(value) for value in note_type),
                "f0": " ".join(f"{value:.1f}" for value in f0),
                "musia_source_line": line,
                "musia_target_text": text,
            }
        )
    return items


def main() -> None:
    parser = argparse.ArgumentParser(description="Create SoulX Cantonese score metadata from a website text track.")
    parser.add_argument("--source-track", type=Path, required=True)
    parser.add_argument("--target-lines", type=Path, required=True)
    parser.add_argument("--f0-csv", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--name", default="yue-Hant")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    source_lines = load_source_lines(args.source_track)
    target_lines = load_target_lines(args.target_lines)
    f0_rows = load_f0(args.f0_csv)
    phone_set = load_phone_set()
    metadata = build_metadata(source_lines, target_lines, f0_rows, phone_set)
    if not metadata:
        raise SystemExit("No metadata rows generated.")
    out = args.output_dir / f"soulx_target_{args.name}.json"
    out.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    phrase_map = {
        "schema": "musia.cantonese_same_score.v1",
        "sourceTrack": str(args.source_track),
        "targetLines": str(args.target_lines),
        "f0Csv": str(args.f0_csv),
        "items": [
            {
                "id": item["index"],
                "start": item["time"][0] / 1000,
                "end": item["time"][1] / 1000,
                "text": item["musia_target_text"],
                "tokens": item["text"].split()[1:-1],
                "phones": item["phoneme"].split()[1:-1],
            }
            for item in metadata
        ],
    }
    (args.output_dir / "phrase_map.json").write_text(json.dumps(phrase_map, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
