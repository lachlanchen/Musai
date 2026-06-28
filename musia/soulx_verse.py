from __future__ import annotations

import json
import math
import os
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf
from pypinyin import Style, pinyin

from .creative import make_client, parse_json_output, provider_defaults
from .io import ensure_dir, write_json


ROOT = Path(__file__).resolve().parents[1]
SOULX_EXAMPLE_AUDIO = ROOT / "third_party" / "SoulX-Singer" / "example" / "audio"
SOULX_SCRIPT = ROOT / "scripts" / "run_soulx_svs.sh"
VERSE_ROOT = ROOT / "data" / "soulx_verses"

DEFAULT_RAIN_LINES = [
    "雨落窗前 rain on my mind",
    "街灯微亮 I walk through time",
    "风把旧梦 wash into blue",
    "等云散开 I sing with you",
]

DEFAULT_EN_PHONES = {
    "a": "AH0",
    "again": "AH0-G-EH1-N",
    "all": "AO1-L",
    "and": "AH0-N-D",
    "away": "AH0-W-EY1",
    "blue": "B-L-UW1",
    "city": "S-IH1-T-IY0",
    "cloud": "K-L-AW1-D",
    "clouds": "K-L-AW1-D-Z",
    "cold": "K-OW1-L-D",
    "day": "D-EY1",
    "door": "D-AO1-R",
    "down": "D-AW1-N",
    "dream": "D-R-IY1-M",
    "dreams": "D-R-IY1-M-Z",
    "echo": "EH1-K-OW0",
    "echoes": "EH1-K-OW0-Z",
    "fall": "F-AO1-L",
    "falling": "F-AO1-L-IH0-NG",
    "falls": "F-AO1-L-Z",
    "light": "L-AY1-T",
    "lights": "L-AY1-T-S",
    "glow": "G-L-OW1",
    "heart": "HH-AA1-R-T",
    "here": "HH-IY1-R",
    "home": "HH-OW1-M",
    "i": "AY1",
    "in": "IH0-N",
    "inside": "IH2-N-S-AY1-D",
    "into": "IH1-N-T-UW0",
    "mind": "M-AY1-N-D",
    "me": "M-IY1",
    "moon": "M-UW1-N",
    "my": "M-AY1",
    "near": "N-IH1-R",
    "night": "N-AY1-T",
    "on": "AA1-N",
    "open": "OW1-P-AH0-N",
    "outside": "AW1-T-S-AY1-D",
    "rain": "R-EY1-N",
    "rainfall": "R-EY1-N-F-AO2-L",
    "rainy": "R-EY1-N-IY0",
    "sing": "S-IH1-NG",
    "sky": "S-K-AY1",
    "slow": "S-L-OW1",
    "so": "S-OW1",
    "soft": "S-AO1-F-T",
    "softly": "S-AO1-F-T-L-IY0",
    "stay": "S-T-EY1",
    "still": "S-T-IH1-L",
    "street": "S-T-R-IY1-T",
    "streets": "S-T-R-IY1-T-S",
    "the": "DH-AH0",
    "through": "TH-R-UW1",
    "time": "T-AY1-M",
    "to": "T-UW1",
    "walk": "W-AO1-K",
    "warm": "W-AO1-R-M",
    "wash": "W-AA1-SH",
    "we": "W-IY1",
    "whisper": "W-IH1-S-P-ER0",
    "whispers": "W-IH1-S-P-ER0-Z",
    "with": "W-IH1-DH",
    "window": "W-IH1-N-D-OW0",
    "windows": "W-IH1-N-D-OW0-Z",
    "you": "Y-UW1",
}

SAFE_EN_WORDS = sorted(DEFAULT_EN_PHONES)


@dataclass
class SoulXVerseRequest:
    title: str = "Rain Day Bilingual Verse"
    idea: str = "A gentle rainy-day verse in Chinese and English."
    lyrics: str = ""
    output_dir: str = ""
    provider: str = "deepseek"
    model: str = ""
    refine: bool = True
    run_soulx: bool = True
    prompt_wav: str = ""
    prompt_metadata: str = ""
    control: str = "score"
    device: str = "cuda"
    pitch_shift: int = 0
    bpm: int = 78
    key: str = "D minor"


@dataclass
class SoulXVerseResult:
    output_dir: str
    lyrics_md: str
    target_metadata: str
    prompt_wav: str
    prompt_metadata: str
    melody_wav: str
    vocal_wav: str
    mix_wav: str
    manifest: str
    handoff: str
    model_meta: dict[str, Any]


def slugify(text: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", text.strip().lower()).strip("-")
    return cleaned or "soulx-verse"


def default_output_dir(title: str) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return VERSE_ROOT / f"{stamp}-{slugify(title)[:48]}"


def lyric_lines_from_text(text: str) -> list[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[:8]


def tokenise_line(line: str) -> list[str]:
    tokens: list[str] = []
    for part in re.findall(r"[\u4e00-\u9fff]|[A-Za-z]+(?:'[A-Za-z]+)?|<SP>", line):
        if part == "<SP>":
            tokens.append(part)
        elif re.fullmatch(r"[\u4e00-\u9fff]", part):
            tokens.append(part)
        else:
            tokens.append(part.lower())
    return tokens


def count_sung_tokens(line: str) -> int:
    return len([token for token in tokenise_line(line) if token != "<SP>"])


def en_phone(word: str) -> str:
    cleaned = re.sub(r"[^A-Za-z']", "", word).lower()
    try:
        from g2p_en import G2p  # type: ignore

        phones = [p for p in G2p()(cleaned) if re.fullmatch(r"[A-Z]+[0-2]?", p)]
        if phones:
            return "en_" + "-".join(phones)
    except Exception:
        pass
    if cleaned in DEFAULT_EN_PHONES:
        return "en_" + DEFAULT_EN_PHONES[cleaned]
    if cleaned.endswith("s") and cleaned[:-1] in DEFAULT_EN_PHONES:
        return "en_" + DEFAULT_EN_PHONES[cleaned[:-1]] + "-Z"
    raise ValueError(
        f"Cannot phonemize English word '{word}'. Install g2p_en or use common words in the fallback dictionary."
    )


def zh_phone(char: str) -> str:
    py = pinyin(char, style=Style.TONE3, heteronym=False, neutral_tone_with_five=True)[0][0]
    return "zh_" + py.replace("ü", "u:").replace("v", "u:")


def token_phone(token: str) -> str:
    if token == "<SP>":
        return "<SP>"
    if re.fullmatch(r"[\u4e00-\u9fff]", token):
        return zh_phone(token)
    return en_phone(token)


def midi_to_hz(note: int) -> float:
    return 440.0 * (2.0 ** ((note - 69) / 12.0))


def note_frames(duration: float, pitch: int, sample_rate: int = 24000, hop_size: int = 480) -> list[float]:
    frames = max(1, int(round(duration * sample_rate / hop_size)))
    if pitch <= 0:
        return [0.0] * frames
    base = midi_to_hz(pitch)
    return [round(base * (1.0 + 0.006 * math.sin(i * 0.55)), 1) for i in range(frames)]


def line_pattern(line_index: int, sung_count: int) -> list[int]:
    patterns = [
        [62, 64, 65, 67, 69, 67, 65, 64, 62, 60, 62, 64],
        [64, 65, 67, 69, 71, 69, 67, 65, 64, 62, 64, 65],
        [65, 64, 62, 60, 62, 64, 65, 67, 65, 64, 62, 60],
        [62, 64, 65, 67, 69, 72, 71, 69, 67, 65, 64, 62],
    ]
    pattern = patterns[line_index % len(patterns)]
    return [pattern[i % len(pattern)] for i in range(sung_count)]


def build_metadata(lines: list[str]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    cursor_ms = 0
    for line_index, line in enumerate(lines):
        raw_tokens = tokenise_line(line)
        sung_tokens = [token for token in raw_tokens if token != "<SP>"]
        pitches = line_pattern(line_index, len(sung_tokens))
        text_tokens = ["<SP>"] + raw_tokens + ["<SP>"]
        durations: list[float] = [0.30]
        note_pitch: list[int] = [0]
        note_type: list[int] = [1]
        phone_tokens: list[str] = ["<SP>"]
        sung_i = 0
        for token_i, token in enumerate(raw_tokens):
            if token == "<SP>":
                durations.append(0.16)
                note_pitch.append(0)
                note_type.append(1)
                phone_tokens.append("<SP>")
                continue
            is_last_sung = sung_i == len(sung_tokens) - 1
            duration = 0.42 if not is_last_sung else 0.76
            if token_i % 3 == 1 and not is_last_sung:
                duration = 0.48
            durations.append(duration)
            note_pitch.append(pitches[sung_i])
            note_type.append(3 if is_last_sung else 2)
            phone_tokens.append(token_phone(token))
            sung_i += 1
        durations.append(0.48)
        note_pitch.append(0)
        note_type.append(1)
        phone_tokens.append("<SP>")
        segment_duration_ms = int(round(sum(durations) * 1000))
        f0: list[float] = []
        for duration, pitch in zip(durations, note_pitch):
            f0.extend(note_frames(duration, pitch))
        items.append(
            {
                "index": f"musia_verse_{line_index + 1}",
                "language": "Mandarin",
                "time": [cursor_ms, cursor_ms + segment_duration_ms],
                "duration": " ".join(f"{value:.2f}" for value in durations),
                "text": " ".join(text_tokens),
                "phoneme": " ".join(phone_tokens),
                "note_pitch": " ".join(str(value) for value in note_pitch),
                "note_type": " ".join(str(value) for value in note_type),
                "f0": " ".join(f"{value:.1f}" for value in f0),
                "musia_line": line,
            }
        )
        cursor_ms += segment_duration_ms
    return items


def synthesize_melody(metadata: list[dict[str, Any]], output: Path, sample_rate: int = 24000) -> None:
    total_seconds = metadata[-1]["time"][1] / 1000.0 if metadata else 0.0
    audio = np.zeros(max(1, int(total_seconds * sample_rate)), dtype=np.float32)
    for item in metadata:
        cursor = int(item["time"][0] / 1000.0 * sample_rate)
        durations = [float(value) for value in item["duration"].split()]
        pitches = [int(value) for value in item["note_pitch"].split()]
        for duration, pitch in zip(durations, pitches):
            length = max(1, int(duration * sample_rate))
            if pitch > 0:
                t = np.arange(length, dtype=np.float32) / sample_rate
                freq = midi_to_hz(pitch)
                tone = 0.12 * np.sin(2 * np.pi * freq * t)
                tone += 0.035 * np.sin(2 * np.pi * freq * 2.0 * t)
                env = np.ones(length, dtype=np.float32)
                edge = min(length // 2, int(0.025 * sample_rate))
                if edge > 1:
                    ramp = np.linspace(0.0, 1.0, edge, dtype=np.float32)
                    env[:edge] *= ramp
                    env[-edge:] *= ramp[::-1]
                audio[cursor : cursor + length] += tone.astype(np.float32) * env
            cursor += length
    peak = float(np.max(np.abs(audio))) if audio.size else 0.0
    if peak > 0:
        audio = audio / peak * 0.28
    output.parent.mkdir(parents=True, exist_ok=True)
    sf.write(output, audio, sample_rate)


def mix_audio(vocal: Path, melody: Path, output: Path, sample_rate: int = 24000) -> None:
    vocal_audio, vocal_sr = sf.read(vocal, always_2d=False)
    melody_audio, melody_sr = sf.read(melody, always_2d=False)
    if vocal_sr != sample_rate or melody_sr != sample_rate:
        raise ValueError(f"Expected {sample_rate} Hz audio. Got vocal={vocal_sr}, melody={melody_sr}.")
    vocal_arr = np.asarray(vocal_audio, dtype=np.float32)
    melody_arr = np.asarray(melody_audio, dtype=np.float32)
    if vocal_arr.ndim > 1:
        vocal_arr = vocal_arr.mean(axis=1)
    if melody_arr.ndim > 1:
        melody_arr = melody_arr.mean(axis=1)
    length = max(len(vocal_arr), len(melody_arr))
    vocal_pad = np.zeros(length, dtype=np.float32)
    melody_pad = np.zeros(length, dtype=np.float32)
    vocal_pad[: len(vocal_arr)] = vocal_arr
    melody_pad[: len(melody_arr)] = melody_arr
    mix = 1.0 * vocal_pad + 0.18 * melody_pad
    peak = float(np.max(np.abs(mix))) if mix.size else 0.0
    if peak > 0.96:
        mix = mix / peak * 0.96
    output.parent.mkdir(parents=True, exist_ok=True)
    sf.write(output, mix, sample_rate)


def refine_lines(request: SoulXVerseRequest) -> tuple[list[str], dict[str, Any]]:
    fallback = lyric_lines_from_text(request.lyrics) or DEFAULT_RAIN_LINES
    if not request.refine:
        return fallback, {"status": "skipped"}
    provider, model, api_key = provider_defaults(request.provider, request.model or None)
    client = make_client(provider, api_key)
    if client is None:
        return fallback, {"status": "fallback", "reason": f"missing {provider} api key"}
    prompt = {
        "task": "Write one high-quality singable bilingual Chinese/English verse for SoulX singing synthesis.",
        "title": request.title,
        "idea": request.idea,
        "draft_lyrics": request.lyrics,
        "constraints": [
            "Return strict JSON only.",
            "Use 4 lyric lines.",
            "Each line should have 7 to 10 sung tokens total.",
            "Mix Mandarin Chinese characters and simple English words.",
            "Theme: rainy day, tender, cinematic, emotionally clear.",
            "Avoid real-person voice imitation, copyrighted lyric fragments, and unsafe or deceptive requests.",
            "Use simple English words that are easy to phonemize.",
            f"Use English words only from this allowlist when possible: {', '.join(SAFE_EN_WORDS)}.",
        ],
        "schema": {
            "lyrics_lines": ["line 1", "line 2", "line 3", "line 4"],
            "quality_notes": ["short note"],
        },
    }
    messages = [
        {
            "role": "system",
            "content": "You are Musia LyricFit. Return strict JSON. Make lyrics singable and legally original.",
        },
        {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
    ]
    try:
        response = client.chat.completions.create(model=model, messages=messages, temperature=0.45)
        parsed = parse_json_output(response.choices[0].message.content or "")
        lines = [str(line).strip() for line in parsed.get("lyrics_lines", []) if str(line).strip()]
        if len(lines) < 2:
            raise ValueError("model returned too few lyric lines")
        for line in lines:
            count = count_sung_tokens(line)
            if count < 4 or count > 14:
                raise ValueError(f"lyric line token count out of range ({count}): {line}")
            for token in tokenise_line(line):
                if token != "<SP>":
                    token_phone(token)
        return lines[:6], {"status": "ok", "provider": provider, "model": model, "quality_notes": parsed.get("quality_notes", [])}
    except Exception as exc:
        return fallback, {"status": "fallback", "provider": provider, "model": model, "error": str(exc)}


def render_lyrics_md(request: SoulXVerseRequest, lines: list[str], model_meta: dict[str, Any]) -> str:
    body = [
        f"# {request.title}",
        "",
        "## Lyrics",
        "",
    ]
    body.extend(lines)
    body.extend(
        [
            "",
            "## Production Notes",
            "",
            f"- Idea: {request.idea}",
            f"- BPM: {request.bpm}",
            f"- Key: {request.key}",
            "- Language: Mandarin Chinese + English",
            "- Backend: SoulX-Singer score-conditioned vocal render",
            f"- Lyric refinement: `{model_meta.get('status', 'unknown')}`",
            "",
            "## Safety",
            "",
            "Original rainy-day lyric. No request to imitate a real singer or use copyrighted lyric fragments.",
            "",
        ]
    )
    return "\n".join(body)


def render_handoff(request: SoulXVerseRequest, result_paths: dict[str, Path], model_meta: dict[str, Any]) -> str:
    return f"""# LALACHAN / Musia Musical Short Film Handoff

Use this package when a video or animation tool needs a short original musical-film soundtrack.

## Source Intent

- Title: {request.title}
- Idea: {request.idea}
- Mood: rainy day, tender, cinematic, bilingual Chinese/English.
- Safety: original lyrics, no real-person voice impersonation, no copyrighted source-song localization.

## Audio Artifacts

- Lyrics: `{result_paths['lyrics_md']}`
- Melody guide: `{result_paths['melody_wav']}`
- SoulX vocal: `{result_paths['vocal_wav']}`
- Vocal + melody mix: `{result_paths['mix_wav']}`
- SoulX metadata: `{result_paths['target_metadata']}`

Use `mix.wav` as the first soundtrack candidate for a musical short film. Use `vocal.wav` if the video tool wants to build the instrumental/ambience separately. Use `lyrics.md` for subtitles, shot timing, and multilingual caption overlays.

## Input Checks For Other Tools

1. Confirm the user wants an original song or has rights/consent for any reference material.
2. Treat celebrity names only as broad style references; do not clone a real voice without consent.
3. If using animation, align shot changes to lyric lines and phrase endings.
4. If the vocal is too dry, add rain ambience, piano/pad, room reverb, and light mastering outside SoulX.
5. Keep this package path in the video project manifest so the soundtrack can be regenerated.

## AI Refinement

Lyric/model refinement status: `{json.dumps(model_meta, ensure_ascii=False)}`

Future workers may call:

```bash
musia soulx-verse --title "{request.title}" --idea "{request.idea}" --provider deepseek
```
"""


def run_soulx(request: SoulXVerseRequest, target_metadata: Path, output_dir: Path) -> Path:
    prompt_wav = Path(request.prompt_wav).expanduser() if request.prompt_wav else SOULX_EXAMPLE_AUDIO / "zh_prompt.mp3"
    prompt_metadata = (
        Path(request.prompt_metadata).expanduser() if request.prompt_metadata else SOULX_EXAMPLE_AUDIO / "zh_prompt.json"
    )
    if not prompt_wav.exists():
        raise FileNotFoundError(f"Missing SoulX prompt wav: {prompt_wav}")
    if not prompt_metadata.exists():
        raise FileNotFoundError(f"Missing SoulX prompt metadata: {prompt_metadata}")
    if not SOULX_SCRIPT.exists():
        raise FileNotFoundError(f"Missing SoulX script: {SOULX_SCRIPT}")
    soulx_dir = output_dir / "soulx"
    env = {
        **os.environ,
        "CONTROL": request.control,
        "DEVICE": request.device,
        "PITCH_SHIFT": str(request.pitch_shift),
    }
    subprocess.run(
        ["bash", str(SOULX_SCRIPT), str(prompt_wav), str(prompt_metadata), str(target_metadata), str(soulx_dir)],
        cwd=ROOT,
        env=env,
        check=True,
    )
    generated = soulx_dir / "generated.wav"
    if not generated.exists():
        raise FileNotFoundError(f"SoulX did not write {generated}")
    return generated


def generate_soulx_verse(request: SoulXVerseRequest) -> SoulXVerseResult:
    output_dir = Path(request.output_dir).expanduser() if request.output_dir else default_output_dir(request.title)
    output_dir = ensure_dir(output_dir)
    lines, model_meta = refine_lines(request)
    metadata = build_metadata(lines)
    target_metadata = output_dir / "target_metadata.json"
    lyrics_md = output_dir / "lyrics.md"
    melody_wav = output_dir / "melody.wav"
    vocal_wav = output_dir / "vocal.wav"
    mix_wav = output_dir / "mix.wav"
    manifest = output_dir / "manifest.json"
    handoff = output_dir / "LALACHAN_HANDOFF.md"
    write_json(target_metadata, metadata)
    lyrics_md.write_text(render_lyrics_md(request, lines, model_meta), encoding="utf-8")
    synthesize_melody(metadata, melody_wav)
    if request.run_soulx:
        generated = run_soulx(request, target_metadata, output_dir)
        shutil.copy2(generated, vocal_wav)
        mix_audio(vocal_wav, melody_wav, mix_wav)
    else:
        vocal_wav.write_bytes(b"")
        shutil.copy2(melody_wav, mix_wav)
    prompt_wav = Path(request.prompt_wav).expanduser() if request.prompt_wav else SOULX_EXAMPLE_AUDIO / "zh_prompt.mp3"
    prompt_metadata = (
        Path(request.prompt_metadata).expanduser() if request.prompt_metadata else SOULX_EXAMPLE_AUDIO / "zh_prompt.json"
    )
    result_paths = {
        "lyrics_md": lyrics_md,
        "target_metadata": target_metadata,
        "prompt_wav": prompt_wav,
        "prompt_metadata": prompt_metadata,
        "melody_wav": melody_wav,
        "vocal_wav": vocal_wav,
        "mix_wav": mix_wav,
        "handoff": handoff,
    }
    handoff.write_text(render_handoff(request, result_paths, model_meta), encoding="utf-8")
    result = SoulXVerseResult(
        output_dir=str(output_dir),
        lyrics_md=str(lyrics_md),
        target_metadata=str(target_metadata),
        prompt_wav=str(prompt_wav),
        prompt_metadata=str(prompt_metadata),
        melody_wav=str(melody_wav),
        vocal_wav=str(vocal_wav),
        mix_wav=str(mix_wav),
        manifest=str(manifest),
        handoff=str(handoff),
        model_meta=model_meta,
    )
    write_json(
        manifest,
        {
            "request": asdict(request),
            "result": asdict(result),
            "lyrics_lines": lines,
            "metadata_segments": len(metadata),
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    return result
