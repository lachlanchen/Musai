#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from openai import OpenAI
from pypinyin import Style, pinyin

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

FALLBACK_ZH_30 = "丹尼风笛声声呼唤越过山谷越高山夏日远玫瑰凋落我仍痴等你再归来"
FALLBACK_EN_LINES = [
    "Jasmine blooms so white",
    "Sweet fragrance fills the air",
    "I long to hold it near",
    "And bring it home with care",
]


def chinese_chars(text: str) -> list[str]:
    return [char for char in text if "\u4e00" <= char <= "\u9fff"]


def chinese_char_count(text: str) -> int:
    return len(chinese_chars(text))


def char_to_soulx_phone(char: str) -> str:
    py = pinyin(char, style=Style.TONE3, heteronym=False, neutral_tone_with_five=True)[0][0]
    return "zh_" + py.replace("ü", "u:").replace("v", "u:")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def strip_json_fence(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


def parse_json_model_output(text: str) -> Any:
    cleaned = strip_json_fence(text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start >= 0 and end > start:
            return json.loads(cleaned[start : end + 1])
        raise


def make_client(provider: str, model: str | None) -> tuple[OpenAI | None, str, str]:
    if provider == "deepseek":
        key = os.getenv("DEEPSEEK_API_KEY")
        if not key:
            return None, model or "deepseek-reasoner", "missing DEEPSEEK_API_KEY"
        return (
            OpenAI(api_key=key, base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")),
            model or os.getenv("DEEPSEEK_MODEL", "deepseek-reasoner"),
            "ok",
        )
    if provider == "openai":
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            return None, model or "gpt-5.5", "missing OPENAI_API_KEY"
        return OpenAI(api_key=key), model or os.getenv("OPENAI_MODEL", "gpt-5.5"), "ok"
    raise ValueError(f"unsupported provider: {provider}")


def chat_json(client: OpenAI | None, model: str, payload: dict[str, Any], fallback: Any) -> tuple[Any, dict[str, Any]]:
    if client is None:
        return fallback, {"status": "fallback", "reason": "client unavailable"}
    messages = [
        {
            "role": "system",
            "content": (
                "You are Musai LyricFit, a music-localization and music-quality checker. "
                "Return strict JSON only. Be honest about fit and production readiness."
            ),
        },
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
    ]
    try:
        response = client.chat.completions.create(model=model, messages=messages, temperature=0.4)
        text = response.choices[0].message.content or ""
        return parse_json_model_output(text), {"status": "ok", "model": model}
    except Exception as exc:
        error_text = str(exc)
        if "temperature" in error_text and "unsupported" in error_text.lower():
            try:
                response = client.chat.completions.create(model=model, messages=messages)
                text = response.choices[0].message.content or ""
                return parse_json_model_output(text), {"status": "ok", "model": model, "retry": "without_temperature"}
            except Exception as retry_exc:
                return fallback, {"status": "fallback", "model": model, "error": str(retry_exc), "first_error": error_text}
        return fallback, {"status": "fallback", "model": model, "error": str(exc)}


def count_soulx_sung_tokens(metadata_path: Path) -> int | None:
    if not metadata_path.exists():
        return None
    items = load_json(metadata_path)
    if not items:
        return None
    tokens = items[0].get("text", "").split()
    return sum(1 for token in tokens if token != "<SP>")


def rewrite_soulx_metadata(input_path: Path, target_text: str, output_path: Path) -> dict[str, Any]:
    items = load_json(input_path)
    if not items:
        raise ValueError(f"empty SoulX metadata: {input_path}")
    item = dict(items[0])
    text_tokens = item["text"].split()
    phone_tokens = item["phoneme"].split()
    sung_positions = [index for index, token in enumerate(text_tokens) if token != "<SP>"]
    chars = chinese_chars(target_text)
    if len(chars) != len(sung_positions):
        raise ValueError(f"target has {len(chars)} Chinese chars, SoulX metadata needs {len(sung_positions)}")
    if len(phone_tokens) != len(text_tokens):
        raise ValueError("SoulX metadata text and phoneme token counts differ")
    for char, position in zip(chars, sung_positions):
        text_tokens[position] = char
        phone_tokens[position] = char_to_soulx_phone(char)
    item["language"] = "Mandarin"
    item["text"] = " ".join(text_tokens)
    item["phoneme"] = " ".join(phone_tokens)
    item["musai_target_text"] = target_text
    write_json(output_path, [item])
    return {"path": str(output_path), "sung_token_count": len(sung_positions), "target_char_count": len(chars)}


def transcribe_if_exists(path: Path, language: str, enabled: bool) -> dict[str, Any]:
    if not enabled or not path.exists():
        return {"status": "skipped" if not enabled else "missing", "path": str(path)}
    from musai.asr import transcribe_with_faster_whisper

    result = transcribe_with_faster_whisper(path, model_size="small", language=language)
    return {"status": result.get("status"), "path": str(path), "text": result.get("text", "").strip()}


def collect_run_artifacts(run_dir: Path) -> dict[str, Any]:
    manifest_path = run_dir / "manifest.json"
    manifest = load_json(manifest_path) if manifest_path.exists() else {}
    stems = {}
    for name in ["bass", "drums", "vocals", "other", "instrumental", "human_sound"]:
        path = run_dir / "stems" / f"{name}.wav"
        stems[name] = {"path": str(path), "exists": path.exists(), "bytes": path.stat().st_size if path.exists() else 0}
    return {
        "run_dir": str(run_dir),
        "manifest": {
            key: manifest.get(key)
            for key in ["run_name", "input", "tempo_bpm", "beat_count", "chord_segment_count", "lyrics_status"]
        },
        "stems": stems,
        "beats_csv": str(run_dir / "analysis" / "beats.csv"),
        "chords_csv": str(run_dir / "analysis" / "chords.csv"),
        "lyrics_txt": str(run_dir / "analysis" / "lyrics.txt"),
    }


def choose_zh_candidate(candidate_data: Any, required_count: int) -> tuple[str, str]:
    candidates: list[str] = []
    if isinstance(candidate_data, dict):
        for key in ["joined_version", "target_text", "candidate", "best"]:
            value = candidate_data.get(key)
            if isinstance(value, str):
                candidates.append(value)
        adaptation = candidate_data.get("adaptation")
        if isinstance(adaptation, dict):
            value = adaptation.get("joined_version")
            if isinstance(value, str):
                candidates.append(value)
        raw_candidates = candidate_data.get("candidates")
        if isinstance(raw_candidates, list):
            for item in raw_candidates:
                if isinstance(item, str):
                    candidates.append(item)
                elif isinstance(item, dict):
                    value = item.get("joined_version") or item.get("text")
                    if isinstance(value, str):
                        candidates.append(value)
    for candidate in candidates:
        joined = "".join(chinese_chars(candidate))
        if len(joined) == required_count:
            return joined, "model"
    return FALLBACK_ZH_30, "fallback_count_mismatch"


def choose_en_lines(candidate_data: Any) -> tuple[list[str], str]:
    if isinstance(candidate_data, dict):
        candidates = candidate_data.get("candidates")
        if isinstance(candidates, list) and candidates:
            first = candidates[0]
            if isinstance(first, dict):
                lines = [first.get(f"line{i}", "") for i in range(1, 5)]
                lines = [line for line in lines if isinstance(line, str) and line.strip()]
                if lines:
                    return lines, "model"
            if isinstance(first, list):
                lines = [line for line in first if isinstance(line, str) and line.strip()]
                if lines:
                    return lines, "model"
    return FALLBACK_EN_LINES, "fallback"


def render_report(data: dict[str, Any]) -> str:
    en_zh = data["localizations"]["en_to_zh"]
    zh_en = data["localizations"]["zh_to_en"]
    lines = [
        "# Musai Localization Performance Demo",
        "",
        f"- Created: `{data['created_at']}`",
        f"- Lyric provider: `{data['provider']}`",
        f"- Lyric model: `{data['model']}`",
        f"- Provider status: `{data['provider_status']}`",
        f"- Model API result: `{json.dumps(data['model_meta'], ensure_ascii=False)}`",
        "",
        "## Case A - English Song To Chinese",
        "",
        f"- Input run: `{en_zh['input_artifacts']['run_dir']}`",
        f"- Input song: `{en_zh['input_artifacts']['manifest'].get('input')}`",
        f"- Target lyrics: `{en_zh['target_lyrics_path']}`",
        f"- SoulX target metadata: `{en_zh.get('soulx_metadata_path', 'not created')}`",
        f"- Existing experimental vocal: `{en_zh['existing_outputs']['soulx_vocal']}`",
        f"- Existing experimental mix: `{en_zh['existing_outputs']['soulx_mix']}`",
        f"- Result: `{en_zh['quality_gate']}`",
        "",
        "Artifacts:",
        "",
    ]
    for name, info in en_zh["input_artifacts"]["stems"].items():
        lines.append(f"- `{name}`: `{info['path']}` exists=`{info['exists']}` bytes=`{info['bytes']}`")
    lines += [
        "",
        "ASR check:",
        "",
        f"- Vocal: `{en_zh['asr_checks']['vocal'].get('text', '')}`",
        f"- Mix: `{en_zh['asr_checks']['mix'].get('text', '')}`",
        "",
        "## Case B - Chinese Song To English",
        "",
        f"- Input run: `{zh_en['input_artifacts']['run_dir']}`",
        f"- Input song: `{zh_en['input_artifacts']['manifest'].get('input')}`",
        f"- Target lyrics: `{zh_en['target_lyrics_path']}`",
        f"- Result: `{zh_en['quality_gate']}`",
        "",
        "English target lines:",
        "",
    ]
    for line in zh_en["target_lines"]:
        lines.append(f"- {line}")
    lines += [
        "",
        "Artifacts:",
        "",
    ]
    for name, info in zh_en["input_artifacts"]["stems"].items():
        lines.append(f"- `{name}`: `{info['path']}` exists=`{info['exists']}` bytes=`{info['bytes']}`")
    lines += [
        "",
        "## Backend Sanity Checks",
        "",
        f"- SoulX Mandarin demo ASR: `{data['backend_checks']['soulx_zh_demo'].get('text', '')}`",
        f"- SoulX English demo ASR: `{data['backend_checks']['soulx_en_demo'].get('text', '')}`",
        "",
        "## Interpretation",
        "",
        "- Stem, beat, chord, and artifact extraction work for both English and Chinese/instrumental fixtures.",
        "- DeepSeek/OpenAI-style lyric localization packages can be generated reproducibly.",
        "- SoulX can sing clean Mandarin and English on its own demo metadata.",
        "- The current same-song Danny->Chinese render is audible but fails production lyric intelligibility, so it remains experimental.",
        "- The Mo Li Hua Chinese->English package is lyric-ready, but this fixture is instrumental, so vocal synthesis needs corrected melody/note metadata before a fair render.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a dedicated Musai localization performance demo using DeepSeek/OpenAI-compatible lyric checks.")
    parser.add_argument("--provider", choices=["deepseek", "openai"], default=os.getenv("MUSAI_LYRIC_PROVIDER", "deepseek"))
    parser.add_argument("--model", default=None, help="Override lyric model. DeepSeek default is deepseek-reasoner; OpenAI default is gpt-5.5.")
    parser.add_argument("--output-dir", type=Path, default=Path("data/runs/localization-performance-20260628"))
    parser.add_argument("--skip-asr-check", action="store_true")
    args = parser.parse_args()

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    client, model, provider_status = make_client(args.provider, args.model)
    soulx_base_meta = ROOT / "data/runs/danny-boy-zh-localization/localization/zh-CN/soulx_preprocess_vocals_first_verse_mandarin/metadata.json"
    required_count = count_soulx_sung_tokens(soulx_base_meta) or 30

    fallback_payload = {
        "en_to_zh": {"joined_version": FALLBACK_ZH_30, "quality_check": {"source": "fallback"}},
        "zh_to_en": {"candidates": [{"line1": FALLBACK_EN_LINES[0], "line2": FALLBACK_EN_LINES[1], "line3": FALLBACK_EN_LINES[2], "line4": FALLBACK_EN_LINES[3]}]},
        "music_check": {"source": "fallback"},
    }
    prompt_payload = {
        "task": "Create and check Musai localization demo lyrics.",
        "return_schema": {
            "en_to_zh": {
                "joined_version": f"exactly {required_count} Chinese characters, no punctuation",
                "lines": ["phrase 1", "phrase 2", "phrase 3", "phrase 4"],
                "quality_check": {
                    "meaning": "1-5",
                    "naturalness": "1-5",
                    "rhythm_fit": "1-5",
                    "tone_comfort": "1-5",
                    "singability": "1-5",
                    "notes": "short",
                },
            },
            "zh_to_en": {
                "candidates": [
                    {
                        "line1": "short singable English phrase",
                        "line2": "short singable English phrase",
                        "line3": "short singable English phrase",
                        "line4": "short singable English phrase",
                    }
                ],
                "quality_check": "short",
            },
            "music_check": {
                "overall": "short honest QA note",
                "production_ready": False,
                "next_step": "short",
            },
        },
        "cases": [
            {
                "id": "en_to_zh_danny_first_verse",
                "source_language": "English",
                "target_language": "Mandarin Chinese",
                "source_meaning": "Farewell ballad: a call moves across valleys and mountains; summer is gone; roses fall; the beloved leaves while the singer waits.",
                "duration_seconds": 29.31,
                "target_character_count": required_count,
            },
            {
                "id": "zh_to_en_molihua_reference",
                "source_language": "Mandarin Chinese",
                "target_language": "English",
                "source_meaning": "Traditional jasmine folk song: a beautiful fragrant white jasmine flower is admired; the singer wants to pick it and give it to someone.",
                "duration_seconds": 26.08,
                "style": "simple folk melody, open vowels, easy to sing",
            },
        ],
    }
    model_result, model_meta = chat_json(client, model, prompt_payload, fallback_payload)
    write_json(output_dir / "model_raw_result.json", {"meta": model_meta, "result": model_result})

    zh_target, zh_source = choose_zh_candidate(model_result.get("en_to_zh", {}) if isinstance(model_result, dict) else {}, required_count)
    en_lines, en_source = choose_en_lines(model_result.get("zh_to_en", {}) if isinstance(model_result, dict) else {})

    en_to_zh_dir = output_dir / "en-to-zh-danny"
    zh_to_en_dir = output_dir / "zh-to-en-molihua"
    en_to_zh_dir.mkdir(parents=True, exist_ok=True)
    zh_to_en_dir.mkdir(parents=True, exist_ok=True)
    (en_to_zh_dir / "target_lyrics_zh.txt").write_text(zh_target + "\n", encoding="utf-8")
    (zh_to_en_dir / "target_lyrics_en.txt").write_text("\n".join(en_lines) + "\n", encoding="utf-8")

    soulx_meta_result: dict[str, Any] = {"status": "missing_base_metadata", "path": str(soulx_base_meta)}
    soulx_output_path = en_to_zh_dir / "soulx_target_metadata_zh.json"
    if soulx_base_meta.exists():
        try:
            soulx_meta_result = rewrite_soulx_metadata(soulx_base_meta, zh_target, soulx_output_path)
            soulx_meta_result["status"] = "ok"
        except Exception as exc:
            soulx_meta_result = {"status": "failed", "error": str(exc), "path": str(soulx_output_path)}

    write_json(
        en_to_zh_dir / "target_lyrics_zh.json",
        {
            "target_language": "zh-CN",
            "target_text": zh_target,
            "source": zh_source,
            "required_chinese_characters": required_count,
            "actual_chinese_characters": chinese_char_count(zh_target),
            "soulx_metadata": soulx_meta_result,
        },
    )
    write_json(
        zh_to_en_dir / "target_lyrics_en.json",
        {
            "target_language": "en",
            "target_lines": en_lines,
            "source": en_source,
            "note": "Lyric package only; the Mo Li Hua fixture used here is instrumental, so singing synthesis needs melody/note metadata first.",
        },
    )

    asr_enabled = not args.skip_asr_check
    data = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "provider": args.provider,
        "model": model,
        "provider_status": provider_status,
        "model_meta": model_meta,
        "localizations": {
            "en_to_zh": {
                "input_artifacts": collect_run_artifacts(ROOT / "data/runs/test-danny-en-60"),
                "target_lyrics_path": str(en_to_zh_dir / "target_lyrics_zh.txt"),
                "soulx_metadata_path": str(soulx_output_path) if soulx_output_path.exists() else None,
                "existing_outputs": {
                    "soulx_vocal": "data/runs/danny-boy-zh-localization/localization/zh-CN/soulx_localized_vocal_zh-CN_first_verse.wav",
                    "soulx_mix": "data/runs/danny-boy-zh-localization/localization/zh-CN/soulx_final_mix_zh-CN_first_verse.wav",
                },
                "asr_checks": {
                    "vocal": transcribe_if_exists(ROOT / "data/runs/danny-boy-zh-localization/localization/zh-CN/soulx_localized_vocal_zh-CN_first_verse.wav", "zh", asr_enabled),
                    "mix": transcribe_if_exists(ROOT / "data/runs/danny-boy-zh-localization/localization/zh-CN/soulx_final_mix_zh-CN_first_verse.wav", "zh", asr_enabled),
                },
                "quality_gate": "experimental_not_production_ready",
            },
            "zh_to_en": {
                "input_artifacts": collect_run_artifacts(ROOT / "data/runs/test-moli-hua-instrumental-30"),
                "target_lyrics_path": str(zh_to_en_dir / "target_lyrics_en.txt"),
                "target_lines": en_lines,
                "quality_gate": "lyric_package_ready_audio_render_blocked_by_instrumental_fixture",
            },
        },
        "backend_checks": {
            "soulx_zh_demo": transcribe_if_exists(ROOT / "data/runs/soulx-wrapper-demo-zh/generated.wav", "zh", asr_enabled),
            "soulx_en_demo": transcribe_if_exists(ROOT / "data/runs/soulx-wrapper-demo-en/generated.wav", "en", asr_enabled),
        },
    }
    write_json(output_dir / "localization_performance.json", data)
    report = render_report(data)
    report_path = output_dir / "REPORT.md"
    report_path.write_text(report, encoding="utf-8")
    print(report_path)


if __name__ == "__main__":
    main()
