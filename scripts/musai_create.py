#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from musai.creative import CreativeMaterials, create_project, list_projects, load_project, MODEL_REGISTRY
from musai.studio import (
    artifact_payload,
    create_session,
    list_artifacts,
    list_jobs,
    list_sessions,
    load_job,
    load_messages,
    send_chat_message,
    setup_status,
)


def read_file_arg(path: str | None) -> str:
    if not path:
        return ""
    return Path(path).expanduser().read_text(encoding="utf-8").strip()


def cmd_models(_: argparse.Namespace) -> None:
    print(json.dumps(MODEL_REGISTRY, indent=2, ensure_ascii=False))


def cmd_list(_: argparse.Namespace) -> None:
    projects = list_projects()
    if not projects:
        print("No creative projects yet.")
        return
    for project in projects:
        materials = project.get("materials", {})
        print(f"{project.get('project_id')}  {project.get('workflow')}  {materials.get('title')}")


def cmd_show(args: argparse.Namespace) -> None:
    project = load_project(args.project_id)
    brief_path = Path(project["artifacts"]["brief_md"])
    print(brief_path.read_text(encoding="utf-8"))


def cmd_plan(args: argparse.Namespace) -> None:
    lyrics = args.lyrics or read_file_arg(args.lyrics_file)
    chords = args.chords or read_file_arg(args.chords_file)
    notation = args.notation or read_file_arg(args.notation_file)
    melody = args.melody or read_file_arg(args.melody_file)
    reference_lyrics = args.reference_lyrics or read_file_arg(args.reference_lyrics_file)
    materials = CreativeMaterials(
        title=args.title,
        idea=args.idea or "",
        lyrics=lyrics,
        chords=chords,
        notation=notation,
        melody=melody,
        style=args.style or "",
        genre=args.genre or "",
        mood=args.mood or "",
        language=args.language,
        vocal_language=args.vocal_language or args.language,
        reference_audio=args.reference_audio or "",
        reference_lyrics=reference_lyrics,
        target_language=args.target_language or "",
        generation_mode=args.generation_mode,
        control_level=args.control_level,
        style_references=args.style_references or "",
        voice_notes=args.voice_notes or "",
        rights_confirmed=args.rights_confirmed,
        voice_consent=args.voice_consent,
        duration=args.duration,
        bpm=args.bpm,
        keyscale=args.keyscale or "",
        time_signature=args.time_signature or "4",
        notes=args.notes or "",
    )
    project = create_project(
        materials,
        provider=args.provider,
        model=args.model,
        analyze_reference=args.analyze_reference,
    )
    print(project.root)
    print(f"Brief: {project.artifacts['brief_md']}")
    print(f"ACE-Step config: {project.artifacts['ace_step_config']}")
    print(f"Commands: {project.artifacts['commands']}")


def cmd_setup(_: argparse.Namespace) -> None:
    print(json.dumps(setup_status(), indent=2, ensure_ascii=False))


def cmd_sessions(_: argparse.Namespace) -> None:
    sessions = list_sessions()
    if not sessions:
        print("No Studio chat sessions yet.")
        return
    for session in sessions:
        print(
            f"{session.get('id')}  "
            f"{session.get('message_count', 0)} msg  "
            f"{session.get('artifact_count', 0)} art  "
            f"{session.get('title', '')}"
        )


def cmd_new_session(args: argparse.Namespace) -> None:
    session = create_session(args.title)
    print(json.dumps(session, indent=2, ensure_ascii=False))


def cmd_messages(args: argparse.Namespace) -> None:
    for message in load_messages(args.session_id):
        print(f"[{message.get('created_at')}] {message.get('role')} {message.get('profile') or ''}")
        print(message.get("content") or "")
        print()


def cmd_chat(args: argparse.Namespace) -> None:
    message = args.message or sys.stdin.read().strip()
    if not message:
        raise SystemExit("Provide a message argument or pipe stdin.")
    result = send_chat_message(args.session_id, message, args.mode)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def cmd_jobs(args: argparse.Namespace) -> None:
    jobs = list_jobs(args.session_id)
    if not jobs:
        print("No jobs.")
        return
    for job in jobs:
        print(f"{job.get('id')}  {job.get('status')}  {job.get('profile')}  {job.get('message', '')[:90]}")


def cmd_job(args: argparse.Namespace) -> None:
    job = load_job(args.job_id)
    if not job:
        raise SystemExit(f"Job not found: {args.job_id}")
    print(json.dumps(job, indent=2, ensure_ascii=False))


def cmd_artifacts(args: argparse.Namespace) -> None:
    data = list_artifacts(args.session_id)
    if args.read:
        payload = artifact_payload(args.session_id, args.read)
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return
    items = data.get("items", [])
    if not items:
        print("No artifacts.")
        return
    for item in items:
        selected = "*" if item.get("id") == data.get("selected_artifact_id") else " "
        print(f"{selected} {item.get('id')}  {item.get('kind')}  {item.get('tab')}  {item.get('title')}  {item.get('filename')}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Musai creative song CLI: idea/lyrics/chords/reference audio to model-ready song projects.")
    sub = parser.add_subparsers(dest="command", required=True)

    models = sub.add_parser("models", help="List local/API model roles.")
    models.set_defaults(func=cmd_models)

    list_cmd = sub.add_parser("list", help="List creative projects.")
    list_cmd.set_defaults(func=cmd_list)

    show = sub.add_parser("show", help="Show a project brief.")
    show.add_argument("project_id")
    show.set_defaults(func=cmd_show)

    setup = sub.add_parser("setup", help="Show local Studio/Codex/API setup status.")
    setup.set_defaults(func=cmd_setup)

    sessions = sub.add_parser("sessions", help="List Studio chat sessions.")
    sessions.set_defaults(func=cmd_sessions)

    new_session = sub.add_parser("new-session", help="Create a Studio chat session.")
    new_session.add_argument("--title", default="Musai chat")
    new_session.set_defaults(func=cmd_new_session)

    messages = sub.add_parser("messages", help="Show messages in a Studio chat session.")
    messages.add_argument("session_id")
    messages.set_defaults(func=cmd_messages)

    chat = sub.add_parser("chat", help="Send a message through the Studio chat/worker router.")
    chat.add_argument("message", nargs="?")
    chat.add_argument("--session-id")
    chat.add_argument("--mode", choices=["auto", "chat", "worker"], default="auto")
    chat.set_defaults(func=cmd_chat)

    jobs = sub.add_parser("jobs", help="List Studio worker jobs.")
    jobs.add_argument("--session-id")
    jobs.set_defaults(func=cmd_jobs)

    job = sub.add_parser("job", help="Show one Studio worker job.")
    job.add_argument("job_id")
    job.set_defaults(func=cmd_job)

    artifacts = sub.add_parser("artifacts", help="List or read Studio artifacts for a session.")
    artifacts.add_argument("session_id")
    artifacts.add_argument("--read", help="Artifact id to read as JSON payload.")
    artifacts.set_defaults(func=cmd_artifacts)

    plan = sub.add_parser("plan", help="Create a song project brief and backend commands.")
    plan.add_argument("--title", required=True)
    plan.add_argument("--idea")
    plan.add_argument("--lyrics")
    plan.add_argument("--lyrics-file")
    plan.add_argument("--chords")
    plan.add_argument("--chords-file")
    plan.add_argument("--notation", help="Staff notation, numbered notation, MIDI notes, or a melody sketch as text.")
    plan.add_argument("--notation-file")
    plan.add_argument("--melody", help="Melody / xuanlv / rhythm brief. Use this for 旋律, motif, contour, phrase rhythm, or hook shape.")
    plan.add_argument("--melody-file")
    plan.add_argument("--style")
    plan.add_argument("--genre")
    plan.add_argument("--mood")
    plan.add_argument("--language", default="en")
    plan.add_argument("--vocal-language")
    plan.add_argument("--target-language")
    plan.add_argument("--reference-audio")
    plan.add_argument("--reference-lyrics")
    plan.add_argument("--reference-lyrics-file")
    plan.add_argument(
        "--generation-mode",
        choices=[
            "auto",
            "free_vocal",
            "melody_generation",
            "full_production",
            "controlled_song",
            "localization",
        ],
        default="auto",
        help="Top-level route: vocal-only, melody/rhythm, full song, controlled materials, or licensed localization.",
    )
    plan.add_argument(
        "--control-level",
        choices=[
            "auto",
            "free",
            "lyrics",
            "lyrics_chords",
            "melody_sheet",
            "reference_audio",
            "strict_localization",
        ],
        default="auto",
        help="How tightly generation should follow supplied material.",
    )
    plan.add_argument("--style-references", help="Broad style/influence references; not a request to impersonate a real voice.")
    plan.add_argument("--voice-notes", help="Vocal range, timbre, emotion, language, pronunciation, or consented voice notes.")
    plan.add_argument("--rights-confirmed", action="store_true", help="Mark that rights/permission are confirmed for localization or adaptation.")
    plan.add_argument("--voice-consent", action="store_true", help="Mark that voice/timbre consent is confirmed for any voice reference.")
    plan.add_argument("--duration", type=int, default=120)
    plan.add_argument("--bpm", type=int)
    plan.add_argument("--keyscale")
    plan.add_argument("--time-signature", default="4")
    plan.add_argument("--notes")
    plan.add_argument("--provider", choices=["deepseek", "openai", "offline"], default="deepseek")
    plan.add_argument("--model")
    plan.add_argument("--analyze-reference", action="store_true", help="Run Demucs/ASR/beats/chords on --reference-audio while creating the project.")
    plan.set_defaults(func=cmd_plan)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
