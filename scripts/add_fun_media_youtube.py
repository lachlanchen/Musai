#!/usr/bin/env python3
"""Add a YouTube-hosted media item to the Fun Lazying Art website catalog."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse


CATALOG_SCHEMA = "fun.lazying.media.catalog.v1"
MANIFEST_SCHEMA = "fun.lazying.media.manifest.v1"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def slug(value: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return text or "media"


def youtube_id(value: str) -> str:
    if re.fullmatch(r"[a-zA-Z0-9_-]{6,}", value):
        return value
    parsed = urlparse(value)
    if "youtu.be" in parsed.netloc:
        return parsed.path.strip("/")
    if "youtube.com" in parsed.netloc:
        query_id = parse_qs(parsed.query).get("v", [""])[0]
        if query_id:
            return query_id
        for pattern in (r"/embed/([^/?#]+)", r"/shorts/([^/?#]+)"):
            match = re.search(pattern, parsed.path)
            if match:
                return match.group(1)
    raise SystemExit(f"Could not parse YouTube video id from: {value}")


def data_dir_for_kind(kind: str) -> str:
    return {
        "song": "songs",
        "localized-song": "songs",
        "mv": "mvs",
        "short-film": "films",
        "video": "videos",
        "youtube-video": "youtube"
    }.get(kind, "videos")


def build_manifest(args, video_id: str, media_id: str) -> dict:
    watch_url = args.youtube_url if args.youtube_url.startswith("http") else f"https://www.youtube.com/watch?v={video_id}"
    thumbnail = args.cover or f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
    languages = [item.strip() for item in args.languages.split(",") if item.strip()]
    return {
        "schema": MANIFEST_SCHEMA,
        "version": 1,
        "id": media_id,
        "kind": args.kind,
        "title": args.title,
        "artist": args.artist,
        "subtitle": args.subtitle,
        "description": args.description,
        "caption": args.caption or args.title,
        "duration": args.duration,
        "canonicalUrl": f"https://fun.lazying.art/#{media_id}",
        "share": {
            "title": f"{args.title} - Fun Lazying Art",
            "description": args.description,
            "url": f"https://fun.lazying.art/#{media_id}",
            "image": thumbnail,
            "siteName": "Fun Lazying Art"
        },
        "assets": {
            "cover": {"id": "cover", "label": "YouTube thumbnail", "role": "cover", "src": thumbnail},
            "poster": {"id": "poster", "label": "YouTube thumbnail", "role": "poster", "src": thumbnail},
            "youtube": {
                "id": "youtube",
                "label": "YouTube",
                "provider": "youtube",
                "videoId": video_id,
                "url": watch_url,
                "role": "published-video"
            }
        },
        "provenance": {
            "source": args.source,
            "youtubeUrl": watch_url
        },
        "musical": {},
        "textTracks": [],
        "timeline": {
            "unit": "seconds",
            "lines": []
        },
        "chapters": [],
        "shots": [],
        "artifacts": [
            {"id": "youtube", "label": "YouTube watch page", "href": watch_url}
        ],
        "createCommand": args.create_command or f"python3 scripts/add_fun_media_youtube.py --title {json.dumps(args.title)} --youtube-url {json.dumps(watch_url)}",
        "languages": languages
    }


def update_catalog(catalog_path: Path, media_id: str, args, manifest_path: str, video_id: str) -> None:
    catalog = load_json(catalog_path)
    if catalog.get("schema") != CATALOG_SCHEMA:
        raise SystemExit(f"{catalog_path}: expected schema {CATALOG_SCHEMA}")
    languages = [item.strip() for item in args.languages.split(",") if item.strip()]
    thumbnail = args.cover or f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
    item = {
        "id": media_id,
        "kind": args.kind,
        "title": args.title,
        "artist": args.artist,
        "summary": args.description,
        "manifest": manifest_path,
        "cover": thumbnail,
        "languages": languages,
        "tags": args.tags
    }
    existing = [entry for entry in catalog.get("items", []) if entry.get("id") != media_id]
    catalog["items"] = existing + [item]
    write_json(catalog_path, catalog)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default="website", help="Website root directory")
    parser.add_argument("--id", help="Media id. Defaults to slugified title.")
    parser.add_argument("--title", required=True)
    parser.add_argument("--youtube-url", required=True, help="YouTube watch, shorts, embed URL, or video id")
    parser.add_argument("--kind", default="youtube-video", choices=["song", "localized-song", "mv", "short-film", "video", "youtube-video"])
    parser.add_argument("--artist", default="Lazying Art")
    parser.add_argument("--subtitle", default="")
    parser.add_argument("--description", default="A Fun Lazying Art media item published on YouTube.")
    parser.add_argument("--caption", default="")
    parser.add_argument("--duration", type=float, default=1.0, help="Duration in seconds. Update later if unknown.")
    parser.add_argument("--languages", default="en,zh-Hans,ja")
    parser.add_argument("--cover", default="", help="Optional local or remote cover image URL/path")
    parser.add_argument("--source", default="youtube-upload")
    parser.add_argument("--create-command", default="")
    parser.add_argument("--tags", nargs="*", default=["youtube", "lalachan"])
    args = parser.parse_args()

    root = Path(args.root)
    media_id = args.id or slug(args.title)
    video_id = youtube_id(args.youtube_url)
    kind_dir = data_dir_for_kind(args.kind)
    manifest_rel = f"data/{kind_dir}/{media_id}/manifest.json"
    manifest_path = root / manifest_rel
    manifest = build_manifest(args, video_id, media_id)
    write_json(manifest_path, manifest)
    update_catalog(root / "data/catalog.json", media_id, args, manifest_rel, video_id)
    print(f"added {media_id}: {manifest_path}")


if __name__ == "__main__":
    main()
