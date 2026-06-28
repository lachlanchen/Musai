# Cantonese vocal additions

Date: 2026-06-28

## Goal

Add separate Cantonese vocal versions to the existing Fun Lazying Art songs:

```text
rain-day-full-song-trilingual
mars-red-sky-trilingual
one-sky-three-lights-mixed
```

The Cantonese versions are same-guide vocal alternates, not independent full-song generations.

## Guide Choices

```text
Rain Day Full Song: Japanese vocal guide
Small Under the Red Sky: English vocal guide
One Sky, Three Lights: public mixed vocal guide
```

Reasoning:

```text
Rain: Japanese guide has cleaner full-song phrase timing than the sparse English guide.
Mars: English guide has the most complete 14-line phrase map.
One Sky: must use data/runs/one-sky-three-lights-ace-phonetic-analysis, because that is the 64-second public website asset.
```

## New Public Assets

```text
website/assets/audio/rain-day-full-song-yue-Hant.mp3
website/assets/audio/mars-red-sky-yue-Hant.mp3
website/assets/audio/one-sky-three-lights-yue-Hant.mp3
```

Durations:

```text
Rain Cantonese: 78.00s
Mars Cantonese: 82.00s
One Sky Cantonese: 64.00s
```

Level check:

```text
Rain Cantonese: RMS 0.11002, peak 0.81650
Mars Cantonese: RMS 0.14252, peak 0.91116
One Sky Cantonese: RMS 0.12723, peak 0.79800
```

## Website Data

Each song now has:

```text
assets.alternateAudio[] entry with languageCode yue-Hant
lyricSets[] entry yue-vocal
lyrics/yue-vocal/yue-Hant.json
lyrics/yue-vocal/en.json
lyrics/yue-vocal/zh-Hans.json
```

The active Cantonese track includes Jyutping tokens. English and Mandarin tracks are aligned translation tracks for the Cantonese vocal timing.

## Reusable Scripts

```text
scripts/create_soulx_cantonese_from_track.py
scripts/add_fun_cantonese_vocal.py
```

`create_soulx_cantonese_from_track.py`:

```text
website text-track timing + Cantonese target lines + F0 CSV
→ SoulX score metadata
```

`add_fun_cantonese_vocal.py`:

```text
manifest + source timing + target lines + audio src
→ yue-vocal lyric JSON + manifest audio/lyricSet update
```

Dependency added:

```text
pycantonese
```

## Quality / Smoke Test

Commands:

```bash
npm run website:validate
python3 -m py_compile scripts/add_fun_cantonese_vocal.py scripts/create_soulx_cantonese_from_track.py
```

Browser smoke test:

```text
http://127.0.0.1:8782/?media=rain-day-full-song-trilingual
http://127.0.0.1:8782/?media=mars-red-sky-trilingual
http://127.0.0.1:8782/?media=one-sky-three-lights-mixed
```

Verified:

```text
Rain: option 廣東話 -> rain-day-full-song-yue-Hant.mp3, title 雨天全曲, Jyutping visible
Mars: option 廣東話 -> mars-red-sky-yue-Hant.mp3, title 紅天下好渺小, Jyutping visible
One Sky: option 廣東話 -> one-sky-three-lights-yue-Hant.mp3, title 一片天三盞燈, Jyutping visible
```

UI fix:

```text
website/app.js now resets lyric language selection when the selected vocal switches to a different lyricSetId.
```
