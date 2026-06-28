#!/usr/bin/env python3
"""Prepare a Musia song folder for LALACHAN Xiaoyunque MV generation.

The script does not submit anything to Xiaoyunque. It creates a small handoff
pack with a trimmed/normalized audio reference, a prompt, a machine-readable
manifest, and the ffmpeg command for replacing the generated video audio with
the reviewed Musia track.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = ROOT / "data" / "mv_packs"
LALACHAN_ROOT = ROOT.parent / "LALACHAN"

DEFAULT_REFERENCE_FILES = [
    "words-card.jpg",
    "LazyingArtRobot.png",
    "raraxia.jpeg",
    "ayachan.png",
    "sasakun.jpeg",
    "Trio.png",
]


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip().lower()).strip("-")
    return cleaned or "musia-lalachan-mv"


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)


def probe_duration(audio_path: Path) -> float | None:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return None
    result = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(audio_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    try:
        return float(result.stdout.strip())
    except ValueError:
        return None


def default_prompt(args: argparse.Namespace, audio_name: str) -> str:
    title = args.title
    duration = args.duration
    ratio = args.ratio
    mood = args.mood
    scene = args.scene
    return f"""# Xiaoyunque Prompt

Use the uploaded Musia audio reference `{audio_name}` as the music and emotional timing reference.

Create a polished {duration}s MV in {ratio}. The four buddies appear together:

- Rara Xia: warm panda companion, gentle and brave.
- Aya Chan: small red panda girl, bright scarf, curious and kind.
- Sasa Kun: soft boy companion, protective and quiet.
- Zhuangzi Robot: friendly LazyingArt robot with the original logo preserved.

Song title: {title}
Musician credit: Musia
Mood: {mood}
Scene: {scene}

Visual direction:

The MV should feel like a finished music video, not a slideshow. Match camera movement and emotional cuts to the song. Keep the characters visually consistent with the uploaded references. Use cinematic warm light, clean composition, expressive faces, and a hopeful emotional arc. No subtitles, no extra screen text, no watermark-like fake logos, no distorted hands, no duplicate characters unless the shot intentionally shows a reflection.

Timing:

0-4s: establish the world and the four buddies listening to the first beat.
4-10s: move with the rhythm; show close-ups of Aya Chan and the robot reacting to the melody.
10-{duration}s: emotional lift; all four buddies walk forward together as the song resolves.
"""


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_pack(args: argparse.Namespace) -> Path:
    audio_path = Path(args.audio).expanduser().resolve()
    if not audio_path.exists():
        raise SystemExit(f"Audio file not found: {audio_path}")
    if not shutil.which("ffmpeg"):
        raise SystemExit("ffmpeg is required but was not found in PATH")

    slug = slugify(args.slug or args.title)
    output_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else DEFAULT_OUTPUT_ROOT / slug
    audio_dir = output_dir / "audio"
    refs_dir = output_dir / "references"
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)
    refs_dir.mkdir(parents=True, exist_ok=True)

    trimmed_audio = audio_dir / f"{slug}-{int(args.duration)}s.mp3"
    ffmpeg_cmd = [
        "ffmpeg",
        "-y",
        "-ss",
        str(args.start),
        "-t",
        str(args.duration),
        "-i",
        str(audio_path),
        "-af",
        "loudnorm=I=-14:LRA=11:TP=-1.5,afade=t=in:st=0:d=0.03,afade=t=out:st={:.3f}:d=0.30".format(
            max(args.duration - 0.30, 0)
        ),
        "-ar",
        "44100",
        "-ac",
        "2",
        "-b:a",
        "192k",
        str(trimmed_audio),
    ]
    run(ffmpeg_cmd)

    references: list[dict[str, str]] = []
    if args.copy_references:
        for name in DEFAULT_REFERENCE_FILES:
            src = LALACHAN_ROOT / name
            if src.exists():
                dst = refs_dir / name
                shutil.copy2(src, dst)
                references.append({"name": name, "path": str(dst)})

    prompt_path = output_dir / "PROMPT_XYQ.md"
    prompt = default_prompt(args, trimmed_audio.name)
    prompt_path.write_text(prompt, encoding="utf-8")

    replacement_script = output_dir / "replace_video_audio.sh"
    replacement_script.write_text(
        """#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 GENERATED_VIDEO.mp4 OUTPUT_VIDEO.mp4" >&2
  exit 2
fi

VIDEO="$1"
OUT="$2"
AUDIO="$(cd "$(dirname "$0")" && pwd)/audio/{audio_name}"

ffmpeg -y -i "$VIDEO" -i "$AUDIO" -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -shortest "$OUT"
""".format(audio_name=trimmed_audio.name),
        encoding="utf-8",
    )
    replacement_script.chmod(0o755)

    manifest = {
        "schema": "art.lazying.musia.mv-pack.v1",
        "created_at": iso_now(),
        "title": args.title,
        "musician": "Musia",
        "source_audio": str(audio_path),
        "audio_reference": str(trimmed_audio),
        "source_duration_seconds": probe_duration(audio_path),
        "mv_duration_seconds": args.duration,
        "start_seconds": args.start,
        "ratio": args.ratio,
        "target_platform": "LALACHAN Xiaoyunque controlled browser",
        "lalachan_root": str(LALACHAN_ROOT),
        "cdp_url": args.cdp_url,
        "chrome_profile": args.chrome_profile,
        "prompt": str(prompt_path),
        "references": references,
        "replace_audio_script": str(replacement_script),
        "recommended_output_dir": str(LALACHAN_ROOT / "outputs" / "MusiaVideo" / slug),
        "quality_gates": [
            "Audio reference plays and starts on the intended beat.",
            "Generated video follows the four-buddies references.",
            "If Xiaoyunque compresses or changes the music, replace final audio with the Musia mp3.",
            "Final video has no unwanted text, duplicated characters, or broken faces/hands.",
        ],
    }
    write_json(output_dir / "MUSIA_LALACHAN_MV_HANDOFF.json", manifest)

    readme = f"""# {args.title} MV Pack

Prepared for LALACHAN Xiaoyunque browser generation.

## Files

- Audio reference: `audio/{trimmed_audio.name}`
- Prompt: `PROMPT_XYQ.md`
- Handoff manifest: `MUSIA_LALACHAN_MV_HANDOFF.json`
- Final-audio replacement helper: `replace_video_audio.sh`

## Browser Route

In `../LALACHAN`:

```bash
PORT=9222 PROFILE_DIR="$HOME/.cache/xyq-chrome" scripts/xyq_chrome/launch_chrome.sh
```

Use the controlled browser/noVNC session to upload the reference images and the audio reference. Generate the MV. If the returned video audio is not exactly this Musia track, replace it:

```bash
./replace_video_audio.sh GENERATED_VIDEO.mp4 {slug}-final-musia-audio.mp4
```
"""
    (output_dir / "README.md").write_text(readme, encoding="utf-8")
    return output_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audio", required=True, help="Musia audio file to use as the MV soundtrack/reference.")
    parser.add_argument("--title", default="Musia Four Buddies MV", help="Song/MV title.")
    parser.add_argument("--slug", default="", help="Output slug. Defaults to slugified title.")
    parser.add_argument("--output-dir", default="", help="Output directory. Defaults to data/mv_packs/<slug>.")
    parser.add_argument("--duration", type=float, default=15.0, help="MV/audio reference length in seconds.")
    parser.add_argument("--start", type=float, default=0.0, help="Start offset in source audio.")
    parser.add_argument("--ratio", default="4:3", help="Xiaoyunque output aspect ratio.")
    parser.add_argument("--mood", default="warm, hopeful, cinematic, music-led")
    parser.add_argument("--scene", default="a glowing forest path at dusk, then a bright open sky")
    parser.add_argument("--cdp-url", default="http://127.0.0.1:9222")
    parser.add_argument("--chrome-profile", default="~/.cache/xyq-chrome")
    parser.add_argument("--copy-references", action="store_true", help="Copy standard LALACHAN character references into the pack.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    pack_dir = build_pack(args)
    print(f"\nCreated MV pack: {pack_dir}")
    print(f"Open prompt: {pack_dir / 'PROMPT_XYQ.md'}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(f"Command failed with exit code {exc.returncode}", file=sys.stderr)
        raise SystemExit(exc.returncode)
