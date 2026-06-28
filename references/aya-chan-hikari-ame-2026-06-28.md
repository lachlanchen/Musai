# Aya Chan Hikari Ame - 2026-06-28

This records the local Japanese song package generated for future `../LALACHAN` video work.

## Project

```text
data/creative_projects/aya-chan-hikari-ame-20260628/
```

This folder is ignored by git because it contains generated WAV/MP3 media.

## Selected Audio

```text
data/creative_projects/aya-chan-hikari-ame-20260628/final/aya-chan-hikari-ame-selected.wav
data/creative_projects/aya-chan-hikari-ame-20260628/final/aya-chan-hikari-ame-selected.mp3
data/creative_projects/aya-chan-hikari-ame-20260628/final/aya-chan-hikari-ame-en-selected.wav
data/creative_projects/aya-chan-hikari-ame-20260628/final/aya-chan-hikari-ame-en-selected.mp3
data/creative_projects/aya-chan-hikari-ame-20260628/final/aya-chan-hikari-ame-zh-Hans-selected.wav
data/creative_projects/aya-chan-hikari-ame-20260628/final/aya-chan-hikari-ame-zh-Hans-selected.mp3
```

Cover/poster:

```text
data/creative_projects/aya-chan-hikari-ame-20260628/assets/aya-chan-hikari-ame-cover-16x9.png
```

LALACHAN handoff:

```text
data/creative_projects/aya-chan-hikari-ame-20260628/LALACHAN_SONG_TO_VIDEO_HANDOFF.md
```

Selected version note:

```text
data/creative_projects/aya-chan-hikari-ame-20260628/SELECTED_VERSION.md
```

## Generation

- Backend: ACE-Step 1.5 XL turbo
- Languages: Japanese selected reference, English companion render, Mandarin companion render
- Duration: 68 seconds
- BPM: 92
- Key: G major
- Seeds: Japanese `731028`, English `731128`, Mandarin `731129`
- Vocal direction: clear upfront young female Japanese vocal; original fictional character theme; no real singer imitation.

Lyrics:

```text
data/creative_projects/aya-chan-hikari-ame-20260628/lyrics/ja.txt
data/creative_projects/aya-chan-hikari-ame-20260628/lyrics/en.txt
data/creative_projects/aya-chan-hikari-ame-20260628/lyrics/zh-Hans.txt
```

Prompt/config:

```text
data/creative_projects/aya-chan-hikari-ame-20260628/PROMPT.md
data/creative_projects/aya-chan-hikari-ame-20260628/ace_ja.toml
```

## Review And Analysis

Selected v1 review:

```text
data/creative_projects/aya-chan-hikari-ame-20260628/reviews/20260628-154234/SONG_REVIEW.md
data/creative_projects/aya-chan-hikari-ame-20260628/reviews/20260628-154234/quality.json
```

Full analysis:

```text
data/runs/aya-chan-hikari-ame-20260628-20260628-154133-analysis/
data/runs/aya-chan-hikari-ame-en-20260628-20260628-225631-analysis/
data/runs/aya-chan-hikari-ame-zh-20260628-20260628-225746-analysis/
```

Artifacts:

```text
stems/bass.wav
stems/drums.wav
stems/vocals.wav
stems/other.wav
stems/instrumental.wav
stems/human_sound.wav
analysis/lyrics.json
analysis/lyrics.txt
analysis/beats.csv
analysis/chords.csv
manifest.json
REPORT.md
```

Analysis result:

- Tempo: about 92.29 BPM.
- Beat analysis: 97 beats.
- Chord analysis: 60 chord segments.
- Stems: Demucs completed successfully.

The website item is:

```text
website/data/songs/aya-chan-hikari-ame/manifest.json
website/assets/audio/aya-chan-hikari-ame-ja.mp3
website/assets/audio/aya-chan-hikari-ame-en.mp3
website/assets/audio/aya-chan-hikari-ame-zh-Hans.mp3
website/assets/covers/aya-chan-hikari-ame-16x9.png
```

Each vocal has its own trilingual lyric set:

```text
website/data/songs/aya-chan-hikari-ame/lyrics/ja-vocal/{ja,en,zh-Hans}.json
website/data/songs/aya-chan-hikari-ame/lyrics/en-vocal/{en,ja,zh-Hans}.json
website/data/songs/aya-chan-hikari-ame/lyrics/zh-vocal/{zh-Hans,en,ja}.json
```

## Candidate Comparison

| Candidate | Result | Decision |
| --- | --- | --- |
| v1, 68s original lyric | ASR recovered partial lyric; best overall current candidate | selected |
| v2, 48s simplified lyric | ASR recovered only the first short phrase | rejected |
| v3, 48s kana-heavy lyric | ASR returned empty text | rejected |
| English v1, 68s | ASR recovered verse, pre-chorus, several chorus phrases, and outro | selected companion render |
| English compact, 68s | ASR recovered less text than English v1 | rejected |
| Mandarin v1, 68s | ASR recovered the main Mandarin phrases; lyric overlap passed basic gate | selected companion render |

## Quality Caveat

The selected song is usable as a first LALACHAN video reference, but not yet a final professional Japanese lyric-accurate release. The audio levels and music structure are usable; ASR only recovers part of the intended lyric. For a public music release, run a new correction pass with a Japanese-specialized vocal workflow or manually correct the vocal in a DAW.

For Fun Lazying Art publication, planned lyrics were not copied blindly. Each vocal language owns its own timing and visible text:

- Japanese: 6 ASR/listening-corrected lines.
- English: 12 ASR/listening-corrected lines from the selected v1 render.
- Mandarin: 5 ASR/listening-corrected lines from the selected Mandarin render.

Translations were checked line-by-line so `ja.json` and `zh-Hans.json` do not contain accidental English visible text. The stricter `scripts/audit_fun_media_item.py` visible-script check was added after fixing the earlier Take Care review item, where `Take care of yourself` had leaked into Japanese and Chinese tracks.

## Recommended LALACHAN Use

Use the selected MP3 as a timing and emotional reference for a musical short film. Do not ask the video model to render the lyrics as text. Let the video follow the song mood, beat, and phrase changes.
