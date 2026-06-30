# 云海之恋 Main Generation - 2026-06-30

## Goal

Generate a cleaner main Mandarin version of `云海之恋` while preserving the
older generated item as `云海之恋 - Legacy`.

The user requirement was quality first: avoid forcing too many words into the
song, respect the original lyric where the audio is sound-close, and correct
published lyrics against ASR/STT evidence before website use.

## Source Lyric

Project source lyric:

```text
data/creative_projects/yun-hai-zhi-lian-main-20260630/lyrics/zh.txt
```

Timed DiffRhythm LRC:

```text
data/creative_projects/yun-hai-zhi-lian-main-20260630/lyrics/yun_hai_zhi_lian_160_full.lrc
```

## Generation Route

ACE-Step was tried first but missed too many Mandarin lyric lines. DiffRhythm
was then used because it accepts timed LRC input and better supports lyric
adherence.

Selected render:

```text
data/creative_projects/yun-hai-zhi-lian-main-20260630/diffrhythm_outputs/full_160/output.wav
data/creative_projects/yun-hai-zhi-lian-main-20260630/selected/yun-hai-zhi-lian-zh-Hans-diffrhythm-full-160.mp3
```

DiffRhythm local setup note:

```text
third_party/DiffRhythm/infer/infer_utils.py
```

was patched to prefer local checkpoints in:

```text
third_party/DiffRhythm/checkpoints/
```

This avoids re-downloading the large DiffRhythm model every run. First use still
downloaded MuQ / XLM-R style-conditioning dependencies into:

```text
third_party/DiffRhythm/pretrained/
```

## Quality Review

ASR quality report:

```text
data/creative_projects/yun-hai-zhi-lian-main-20260630/reviews/diffrhythm-full-160/QA.md
```

Key metrics:

```text
Duration: 159.985 s
RMS: 0.13051
Peak: 0.99997
ASR overlap: 0.61929
Gate: review
```

Post-correction decision:

- Preserve intended lyric when ASR is sound-close and the sentence is stronger.
- Do not force omitted or heavily compressed phrases into the public timing.
- Correct active Mandarin timing from the selected vocal's own ASR segments.

The generated vocal keeps the main cloud/sea/longing arc but compresses or drops
some phrases such as `一点，一点` and likely `梦也缱绻`; the website lyric set
reflects the audible structure rather than the full prompt lyric.

Follow-up listening correction:

- `一点，一点` is audible inside the long `慢慢，慢慢...穿过云海` phrase and was
  added back to the active Mandarin lyric line.
- `梦也缱绻` is likely audible in the timing gap between `云海之间` and
  `我把爱写成一线`, so it was added as its own timed line from `92.52` to
  `97.61` seconds.

## Analysis Artifacts

Full Musia analysis:

```text
data/runs/yun-hai-zhi-lian-main-diffrhythm-full-160-analysis/
```

Important files:

```text
data/runs/yun-hai-zhi-lian-main-diffrhythm-full-160-analysis/REPORT.md
data/runs/yun-hai-zhi-lian-main-diffrhythm-full-160-analysis/stems/vocals.wav
data/runs/yun-hai-zhi-lian-main-diffrhythm-full-160-analysis/stems/drums.wav
data/runs/yun-hai-zhi-lian-main-diffrhythm-full-160-analysis/stems/bass.wav
data/runs/yun-hai-zhi-lian-main-diffrhythm-full-160-analysis/stems/other.wav
data/runs/yun-hai-zhi-lian-main-diffrhythm-full-160-analysis/stems/human_sound.wav
data/runs/yun-hai-zhi-lian-main-diffrhythm-full-160-analysis/stems/instrumental.wav
data/runs/yun-hai-zhi-lian-main-diffrhythm-full-160-analysis/analysis/chords.csv
data/runs/yun-hai-zhi-lian-main-diffrhythm-full-160-analysis/analysis/beats.csv
data/runs/yun-hai-zhi-lian-main-diffrhythm-full-160-analysis/analysis/lyrics.json
```

Detected analysis:

```text
Tempo: 117.45 BPM
Chord segments: 137
First major center: Eb / Bb
```

## Website Update

New main item:

```text
website/data/songs/yun-hai-zhi-lian/manifest.json
website/data/songs/yun-hai-zhi-lian/lyrics/zh-vocal/zh-Hans.json
website/data/songs/yun-hai-zhi-lian/lyrics/zh-vocal/en.json
website/data/songs/yun-hai-zhi-lian/lyrics/zh-vocal/ja.json
```

Older generated item preserved as:

```text
website/data/songs/yun-hai-zhi-lian-legacy/manifest.json
```

MusiaSongs audio:

```text
/home/lachlan/ProjectsLFS/MusiaSongs/audio/yun-hai-zhi-lian-zh-Hans.mp3
/home/lachlan/ProjectsLFS/MusiaSongs/audio/yun-hai-zhi-lian-legacy-zh-Hans.mp3
/home/lachlan/ProjectsLFS/MusiaSongs/audio/yun-hai-zhi-lian-legacy-en.mp3
/home/lachlan/ProjectsLFS/MusiaSongs/audio/yun-hai-zhi-lian-legacy-ja.mp3
```

Validation:

```bash
npm run website:validate
node bin/musia.js fun-audit --media-id yun-hai-zhi-lian
node --check website/app.js
git diff --check
git -C ../MusiaSongs diff --check
```

All passed after adding cover provenance.

## Recording

No recording was created for this generation pass because the user explicitly
asked to start the new generation with no recording now.
