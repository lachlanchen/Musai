# LALACHAN To Fun Lazying Art Publishing

`fun.lazying.art` can show LALACHAN media alongside Musia media:

- LALACHAN short films
- LALACHAN music videos
- pure songs and musical shorts
- localized songs
- videos already uploaded to YouTube

The website is static, so publishing means writing media assets and JSON manifests under `website/`, then pushing to GitHub Pages.

## Two Publishing Modes

### Local Asset Mode

Use this when we have the final file locally from `../LALACHAN`.

Best for:

- high-quality local playback
- synced subtitles
- synced lyrics
- exact timing
- local cover/poster control
- music-video or short-film review pages

Typical files:

```text
website/assets/video/<media-id>.mp4
website/assets/audio/<media-id>.mp3
website/assets/covers/<media-id>.png
website/data/films/<media-id>/manifest.json
website/data/films/<media-id>/subtitles/en.json
website/data/films/<media-id>/subtitles/zh-Hans.json
website/data/films/<media-id>/subtitles/ja.json
```

Use `kind: "short-film"` for films, `kind: "mv"` for music videos, `kind: "song"` for original songs, and `kind: "localized-song"` for localized song versions.

### YouTube Embed Mode

Use this when the video is already uploaded to YouTube and we want the website to display it.

Best for:

- public share pages
- final published videos
- YouTube-hosted LALACHAN shorts
- YouTube-hosted MVs
- fast catalog pages without copying large video files into git

The local player embeds YouTube and uses the YouTube player controls. If frame-accurate subtitle/lyric sync is required, publish a local MP4 version as `assets.primaryVideo` too.

## Add A YouTube Video

Use the helper:

```bash
npm run website:add-youtube -- \
  --title "LALACHAN Rain Day Short Film" \
  --youtube-url "https://www.youtube.com/watch?v=VIDEO_ID" \
  --kind short-film \
  --artist "LALACHAN" \
  --description "A LALACHAN musical short film." \
  --duration 120 \
  --languages "en,zh-Hans,ja"
```

This creates:

```text
website/data/films/lalachan-rain-day-short-film/manifest.json
```

and updates:

```text
website/data/catalog.json
```

For a YouTube-only general video:

```bash
npm run website:add-youtube -- \
  --title "Behind The Scenes" \
  --youtube-url "https://youtu.be/VIDEO_ID" \
  --kind youtube-video \
  --artist "Lazying Art" \
  --duration 300
```

## Manual YouTube Manifest Shape

```json
{
  "schema": "fun.lazying.media.manifest.v1",
  "version": 1,
  "id": "my-youtube-video",
  "kind": "youtube-video",
  "title": "My YouTube Video",
  "artist": "LALACHAN",
  "duration": 120,
  "assets": {
    "cover": {
      "src": "https://i.ytimg.com/vi/VIDEO_ID/hqdefault.jpg"
    },
    "poster": {
      "src": "https://i.ytimg.com/vi/VIDEO_ID/hqdefault.jpg"
    },
    "youtube": {
      "provider": "youtube",
      "videoId": "VIDEO_ID",
      "url": "https://www.youtube.com/watch?v=VIDEO_ID",
      "label": "YouTube"
    }
  },
  "textTracks": [],
  "timeline": {
    "unit": "seconds",
    "lines": []
  }
}
```

The player also accepts:

```json
{
  "assets": {
    "externalVideos": [
      {
        "id": "youtube",
        "label": "YouTube",
        "provider": "youtube",
        "videoId": "VIDEO_ID"
      }
    ]
  }
}
```

## Local LALACHAN Short Film Manifest Shape

```json
{
  "schema": "fun.lazying.media.manifest.v1",
  "version": 1,
  "id": "lalachan-my-short-film",
  "kind": "short-film",
  "title": "LALACHAN My Short Film",
  "artist": "LALACHAN",
  "duration": 180,
  "assets": {
    "cover": {
      "src": "assets/covers/lalachan-my-short-film.png"
    },
    "poster": {
      "src": "assets/covers/lalachan-my-short-film.png"
    },
    "primaryVideo": {
      "id": "film",
      "label": "Film",
      "src": "assets/video/lalachan-my-short-film.mp4",
      "mime": "video/mp4"
    }
  },
  "textTracks": [
    {
      "code": "zh-Hans",
      "label": "Chinese",
      "nativeLabel": "中文",
      "script": "Hans",
      "features": ["subtitles"],
      "path": "subtitles/zh-Hans.json"
    },
    {
      "code": "en",
      "label": "English",
      "nativeLabel": "English",
      "script": "Latn",
      "features": ["subtitles"],
      "path": "subtitles/en.json"
    }
  ],
  "timeline": {
    "unit": "seconds",
    "lines": [
      {
        "id": "line-001",
        "start": 0,
        "end": 3.5,
        "sourceText": "Opening subtitle"
      }
    ]
  }
}
```

## Catalog Item Shape

Add one item to `website/data/catalog.json`:

```json
{
  "id": "lalachan-my-short-film",
  "kind": "short-film",
  "title": "LALACHAN My Short Film",
  "artist": "LALACHAN",
  "summary": "A musical short film.",
  "manifest": "data/films/lalachan-my-short-film/manifest.json",
  "cover": "assets/covers/lalachan-my-short-film.png",
  "languages": ["zh-Hans", "en", "ja"],
  "tags": ["lalachan", "short-film", "music"]
}
```

## Suggested Pipeline From `../LALACHAN`

1. Export or locate the final video/audio from `../LALACHAN`.
2. Copy the public-ready file into `website/assets/video/` or `website/assets/audio/`.
3. Generate or choose a clean cover/poster and save it under `website/assets/covers/`.
4. Write `manifest.json`.
5. Add subtitles or lyrics as separate per-language JSON files.
6. Add the item to `website/data/catalog.json`.
7. Run validation.
8. Commit and push.

Validation:

```bash
npm run website:validate
node --check website/app.js
```

Deploy:

```bash
git add website references scripts package.json
git commit -m "Add LALACHAN media item"
git push origin main
```

The GitHub Pages workflow deploys `website/` to:

```text
https://fun.lazying.art/
```

## Notes

- Use `localized-song` when the main value is a same-song language adaptation.
- Use `song` when the item is original audio music.
- Use `mv` when video is primarily a music video.
- Use `short-film` when story/visual narrative is primary.
- Use `youtube-video` when the only playable asset is a YouTube embed.
- Local MP4/MP3 assets give the best synced lyrics/subtitles.
- YouTube embeds are best for final public share pages and YouTube uploads.
