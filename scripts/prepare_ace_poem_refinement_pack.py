#!/usr/bin/env python3
"""Create a reusable ACE-Step classical-poem refinement package.

This script does not generate audio. It prepares the assets that made the
Musia `越人歌` route work: source text, pinyin/pronunciation notes, private
phonetic-control lyrics, repeated-hook lyric layouts, ACE config templates,
review checklist, and a commands.sh wrapper for candidate generation/review.
"""

from __future__ import annotations

import argparse
import json
import re
import stat
from datetime import datetime
from pathlib import Path
from typing import Iterable

try:
    from pypinyin import Style, pinyin
except Exception:  # pragma: no cover - script still useful without pypinyin.
    Style = None
    pinyin = None


ROOT = Path(__file__).resolve().parents[1]
PROJECTS_ROOT = ROOT / "data" / "creative_projects"
ACE_ROOT = ROOT / "third_party" / "ACE-Step-1.5"
ACE_CHECKPOINTS = ACE_ROOT / "checkpoints"

RISKY_PINYIN = {
    "兮": "xi1",
    "搴": "qian1",
    "訾": "zi3",
    "几": "ji1",
    "被": "pi1",
    "将": "qiang1/jiang1",
    "行": "xing2/hang2",
    "了": "liao3/le5",
    "乐": "le4/yue4",
    "倒": "dao3/dao4",
    "著": "zhuo2/zhe5",
}


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip().lower()).strip("-")
    return cleaned or "poem-song"


def read_source(args: argparse.Namespace) -> str:
    if args.poem_file:
        return Path(args.poem_file).expanduser().read_text(encoding="utf-8").strip()
    if args.poem:
        return args.poem.strip()
    raise SystemExit("Provide --poem-file or --poem.")


def normalize_poem_lines(text: str) -> list[str]:
    cleaned = re.sub(r"\([^)]*\)", "", text)
    cleaned = re.sub(r"（[^）]*）", "", cleaned)
    raw_lines: list[str] = []
    for line in cleaned.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("#") or line.startswith("《") or line in {"唐", "宋", "先秦", "佚名"}:
            continue
        if re.search(r"[·〔〕]", line) and len(line) < 20:
            continue
        pieces = re.split(r"[，,。.;；!！?？]", line)
        for piece in pieces:
            piece = piece.strip()
            if piece:
                raw_lines.append(piece)
    return raw_lines


def parse_substitutions(values: Iterable[str]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise SystemExit(f"Bad substitution {value!r}; use ORIGINAL=MODEL_TEXT.")
        source, target = value.split("=", 1)
        source = source.strip()
        target = target.strip()
        if not source or not target:
            raise SystemExit(f"Bad substitution {value!r}; both sides are required.")
        mapping[source] = target
    return mapping


def apply_substitutions(lines: list[str], mapping: dict[str, str]) -> list[str]:
    output: list[str] = []
    for line in lines:
        edited = line
        for source, target in mapping.items():
            edited = edited.replace(source, target)
        output.append(edited)
    return output


def pinyin_for_char(char: str) -> str:
    if char in RISKY_PINYIN:
        return RISKY_PINYIN[char]
    if not ("\u3400" <= char <= "\u9fff"):
        return ""
    if pinyin is None or Style is None:
        return ""
    values = pinyin(char, style=Style.TONE3, strict=False, neutral_tone_with_five=True)
    if values and values[0]:
        return values[0][0]
    return ""


def line_pinyin(line: str) -> str:
    readings = [pinyin_for_char(char) for char in line if "\u3400" <= char <= "\u9fff"]
    return " ".join(reading or "?" for reading in readings)


def choose_hook(lines: list[str], requested: str | None) -> list[str]:
    if requested:
        hook_lines = normalize_poem_lines(requested)
        return hook_lines or [requested.strip()]
    if len(lines) >= 2:
        return lines[-2:]
    return lines[-1:]


def repeated_original(lines: list[str], hook: list[str]) -> list[str]:
    if not lines:
        return []
    intro = lines[: min(4, len(lines))]
    middle = lines[min(4, len(lines)) : min(8, len(lines))]
    body = lines[min(8, len(lines)) :]
    output: list[str] = []
    output.extend(intro)
    output.extend(hook)
    if middle:
        output.append("")
        output.extend(middle)
        output.extend(hook)
    if body:
        output.append("")
        output.extend(body)
    output.append("")
    output.extend(hook)
    return output


def repeated_hook(lines: list[str], hook: list[str]) -> list[str]:
    if not lines:
        return []
    output: list[str] = []
    first = lines[: min(4, len(lines))]
    rest = lines[min(4, len(lines)) :]
    output.extend(first)
    output.extend(hook)
    output.append("")
    output.extend(rest)
    output.extend(hook)
    output.append("")
    output.extend(hook)
    return output


def sectioned(lines: list[str], hook: list[str]) -> list[str]:
    output: list[str] = ["[Verse]"]
    midpoint = max(1, len(lines) // 2)
    output.extend(lines[:midpoint])
    output.extend(["", "[Chorus]"])
    output.extend(hook)
    output.extend(["", "[Verse 2]"])
    output.extend(lines[midpoint:])
    output.extend(["", "[Final Chorus]"])
    output.extend(hook)
    return output


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def toml_string(value: str | Path) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def ace_config(
    project_dir: Path,
    output_name: str,
    lyrics_path: Path,
    model: str,
    caption: str,
    duration: int,
    bpm: int,
    keyscale: str,
    seed_start: int,
    steps: int,
    batch_size: int,
) -> str:
    seeds = ", ".join(str(seed_start + i) for i in range(batch_size))
    return "\n".join(
        [
            "# Generated by prepare_ace_poem_refinement_pack.py.",
            f"project_root = {toml_string(ACE_ROOT)}",
            f"checkpoint_dir = {toml_string(ACE_CHECKPOINTS)}",
            f"save_dir = {toml_string(project_dir / 'ace_outputs' / output_name)}",
            f"config_path = {toml_string(model)}",
            'task_type = "text2music"',
            f"caption = {toml_string(caption)}",
            f"lyrics = {toml_string(lyrics_path)}",
            f"duration = {int(duration)}",
            f"bpm = {int(bpm)}",
            f"keyscale = {toml_string(keyscale)}",
            'timesignature = "4"',
            'vocal_language = "zh"',
            "thinking = false",
            "use_cot_lyrics = false",
            "use_cot_caption = false",
            f"inference_steps = {int(steps)}",
            "guidance_scale = 1.0",
            "use_random_seed = false",
            f"seeds = [{seeds}]",
            f"batch_size = {int(batch_size)}",
            'audio_format = "wav"',
            "",
        ]
    )


def command_script(project_dir: Path) -> str:
    return f"""#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="{ROOT}"
PROJECT_DIR="{project_dir}"
CONDA_ENV="${{MUSIA_CONDA_ENV:-musia}}"
cd "$ROOT_DIR"

latest_audio() {{ find "$PROJECT_DIR/ace_outputs" -type f -name "*.wav" 2>/dev/null | sort | tail -n 1; }}

case "${{1:-help}}" in
  generate-sft)
    cd third_party/ACE-Step-1.5
    .venv/bin/python cli.py -c "$PROJECT_DIR/configs/ace_xl_sft_repeated_hook.toml" --backend "${{ACE_BACKEND:-vllm}}"
    ;;
  generate-turbo-hook)
    cd third_party/ACE-Step-1.5
    .venv/bin/python cli.py -c "$PROJECT_DIR/configs/ace_xl_turbo_repeated_hook.toml" --backend "${{ACE_BACKEND:-vllm}}"
    ;;
  generate-turbo-original)
    cd third_party/ACE-Step-1.5
    .venv/bin/python cli.py -c "$PROJECT_DIR/configs/ace_xl_turbo_repeated_original.toml" --backend "${{ACE_BACKEND:-vllm}}"
    ;;
  quality)
    audio="$(latest_audio)"
    if [[ -z "${{audio:-}}" ]]; then echo "No generated WAV found." >&2; exit 1; fi
    PYTHONNOUSERSITE=1 conda run -n "$CONDA_ENV" python scripts/musia_quality_check.py "$audio" --language zh --expected-lyrics-file "$PROJECT_DIR/lyrics/original-public.txt" --asr-model large-v3 --output-dir "$PROJECT_DIR/reviews/$(basename "${{audio%.wav}}")-large"
    ;;
  analyze)
    audio="$(latest_audio)"
    if [[ -z "${{audio:-}}" ]]; then echo "No generated WAV found." >&2; exit 1; fi
    PYTHONNOUSERSITE=1 conda run -n "$CONDA_ENV" python scripts/run_pipeline.py "$audio" --run-name "$(basename "$PROJECT_DIR")-analysis" --max-duration 180 --asr-model large-v3 --language zh --demucs-device "${{MUSIA_DEMUCS_DEVICE:-cuda}}"
    ;;
  show)
    sed -n "1,260p" "$PROJECT_DIR/REFINEMENT_PLAN.md"
    ;;
  help|*)
    echo "Usage: commands.sh generate-sft|generate-turbo-hook|generate-turbo-original|quality|analyze|show"
    ;;
esac
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title", required=True)
    parser.add_argument("--poem-file")
    parser.add_argument("--poem")
    parser.add_argument("--project-id")
    parser.add_argument("--output-root", default=str(PROJECTS_ROOT))
    parser.add_argument("--hook")
    parser.add_argument("--duration", type=int, default=100)
    parser.add_argument("--bpm", type=int, default=72)
    parser.add_argument("--keyscale", default="A minor")
    parser.add_argument("--seed-start", type=int, default=736000)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument(
        "--substitution",
        action="append",
        default=[],
        help="Private model-facing substitution, e.g. '搴=牵'. Can be repeated.",
    )
    parser.add_argument(
        "--caption-extra",
        default=(
            "Cinematic Mandarin Chinese ancient art song, clear upfront expressive female vocal, "
            "beautiful connected melody, natural classical diction, spacious breath, no real singer imitation."
        ),
    )
    args = parser.parse_args()

    source = read_source(args)
    lines = normalize_poem_lines(source)
    if not lines:
        raise SystemExit("No poem lyric lines found after normalization.")

    project_id = args.project_id or f"{slugify(args.title)}-{datetime.now().strftime('%Y%m%d')}"
    project_dir = Path(args.output_root).expanduser() / project_id
    mapping = parse_substitutions(args.substitution)
    hook_public = choose_hook(lines, args.hook)
    control_lines = apply_substitutions(lines, mapping)
    hook_control = apply_substitutions(hook_public, mapping)

    lyrics_dir = project_dir / "lyrics"
    source_dir = project_dir / "source"
    configs_dir = project_dir / "configs"

    write_text(source_dir / "source-poem.md", f"# {args.title}\n\n```text\n{source}\n```")
    write_text(lyrics_dir / "original-public.txt", "\n".join(lines))
    write_text(lyrics_dir / "phonetic-control.txt", "\n".join(control_lines))
    write_text(lyrics_dir / "repeated-original-public.txt", "\n".join(repeated_original(lines, hook_public)))
    write_text(lyrics_dir / "repeated-original-control.txt", "\n".join(repeated_original(control_lines, hook_control)))
    write_text(lyrics_dir / "repeated-hook-public.txt", "\n".join(repeated_hook(lines, hook_public)))
    write_text(lyrics_dir / "repeated-hook-control.txt", "\n".join(repeated_hook(control_lines, hook_control)))
    write_text(lyrics_dir / "sectioned-public.txt", "\n".join(sectioned(lines, hook_public)))
    write_text(lyrics_dir / "sectioned-control.txt", "\n".join(sectioned(control_lines, hook_control)))

    risky_rows = []
    for line in lines:
        risky = [char for char in line if char in RISKY_PINYIN or char in mapping]
        risky_rows.append((line, line_pinyin(line), "".join(risky) or "-"))

    guide_lines = [
        f"# {args.title} Pronunciation And Refinement Guide",
        "",
        "## Public Lines",
        "",
        "| Line | Pinyin baseline | Risky characters |",
        "| --- | --- | --- |",
    ]
    for line, reading, risky in risky_rows:
        guide_lines.append(f"| {line} | {reading} | {risky} |")
    guide_lines.extend(
        [
            "",
            "## Private Model-Facing Substitutions",
            "",
            "| Public | Control |",
            "| --- | --- |",
        ]
    )
    if mapping:
        for source_text, target_text in mapping.items():
            guide_lines.append(f"| {source_text} | {target_text} |")
    else:
        guide_lines.append("| - | - |")
    write_text(source_dir / "pronunciation-guide.md", "\n".join(guide_lines))

    caption = (
        f"{args.caption_extra} Title: {args.title}. The lyric uses only the original poem words, "
        f"with the main hook centered on {' '.join(hook_public)}. "
        f"Arrangement: guqin, pipa, xiao, soft strings, warm piano, restrained drums, spacious reverb. "
        f"{args.keyscale}, {args.bpm} BPM, 4/4."
    )

    write_text(
        configs_dir / "ace_xl_sft_repeated_hook.toml",
        ace_config(
            project_dir,
            "xl_sft_repeated_hook",
            lyrics_dir / "repeated-hook-control.txt",
            "acestep-v15-xl-sft",
            caption,
            args.duration,
            args.bpm,
            args.keyscale,
            args.seed_start,
            50,
            min(args.batch_size, 2),
        ),
    )
    write_text(
        configs_dir / "ace_xl_turbo_repeated_hook.toml",
        ace_config(
            project_dir,
            "xl_turbo_repeated_hook",
            lyrics_dir / "repeated-hook-control.txt",
            "acestep-v15-xl-turbo",
            caption,
            args.duration,
            args.bpm,
            args.keyscale,
            args.seed_start + 20,
            8,
            args.batch_size,
        ),
    )
    write_text(
        configs_dir / "ace_xl_turbo_repeated_original.toml",
        ace_config(
            project_dir,
            "xl_turbo_repeated_original",
            lyrics_dir / "repeated-original-control.txt",
            "acestep-v15-xl-turbo",
            caption,
            args.duration,
            args.bpm,
            args.keyscale,
            args.seed_start + 40,
            8,
            args.batch_size,
        ),
    )

    plan = [
        f"# {args.title} Recursive ACE Poem Refinement Plan",
        "",
        "## Philosophy",
        "",
        "Do not trust a single render. Use the poem as intent, generate multiple controlled candidates, reject by ASR/listening, and publish only corrected lyrics that match the selected audio.",
        "",
        "Priority:",
        "",
        "```text",
        "beautiful melody > smooth audible vocal > hook recovery > truthful lyric timing > literal full coverage",
        "```",
        "",
        "## Candidate Order",
        "",
        "1. `./commands.sh generate-sft` for the slow high-detail XL SFT route.",
        "2. `./commands.sh generate-turbo-hook` if SFT loses lyric structure or sounds less musical.",
        "3. `./commands.sh generate-turbo-original` if the hook route over-repeats.",
        "4. Run `./commands.sh quality` after each candidate batch.",
        "5. Run `./commands.sh analyze` only on a finalist.",
        "",
        "## Selection Checklist",
        "",
        "- [ ] Melody is memorable and emotionally right.",
        "- [ ] Vocal is smooth, upfront, and not clipped.",
        "- [ ] ASR recovers the hook or central couplet.",
        "- [ ] Rare characters are sound-close to the pronunciation guide.",
        "- [ ] Any skipped or repeated lines are documented.",
        "- [ ] Website JSON uses actual-audio timing, not prompt timing.",
        "",
        "## Public Hook",
        "",
        "```text",
        "\n".join(hook_public),
        "```",
        "",
        "## Commands",
        "",
        "```bash",
        "./commands.sh generate-sft",
        "./commands.sh quality",
        "./commands.sh generate-turbo-hook",
        "./commands.sh quality",
        "./commands.sh analyze",
        "```",
    ]
    write_text(project_dir / "REFINEMENT_PLAN.md", "\n".join(plan))

    commands_path = project_dir / "commands.sh"
    write_text(commands_path, command_script(project_dir))
    commands_path.chmod(commands_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    print(project_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
