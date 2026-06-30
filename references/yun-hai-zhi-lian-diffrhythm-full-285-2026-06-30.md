# Yun Hai Zhi Lian DiffRhythm Full 285 Pass

Date: 2026-06-30

## Goal

Regenerate `云海之恋` through the DiffRhythm route because this route can follow
a full timed lyric file more closely than the short ACE route. The target was a
smooth full Mandarin ballad that keeps the user's complete cloud-sea lyric,
then updates the Fun Lazying Art website with corrected lyrics, translations,
pinyin/furigana, chords, and public audio.

## Source Lyric

Project:

```text
data/creative_projects/yun-hai-zhi-lian-diffrhythm-full-20260630/
```

Primary lyric files:

```text
data/creative_projects/yun-hai-zhi-lian-diffrhythm-full-20260630/lyrics/zh_full.txt
data/creative_projects/yun-hai-zhi-lian-diffrhythm-full-20260630/lyrics/yun_hai_zhi_lian_full_285.lrc
```

The LRC uses 63 timed lyric lines and fits inside DiffRhythm's 285-second full
song window.

## Generation

Selected render:

```text
data/creative_projects/yun-hai-zhi-lian-diffrhythm-full-20260630/diffrhythm_outputs/full_285_clean/output.wav
```

Rejected render:

```text
data/creative_projects/yun-hai-zhi-lian-diffrhythm-full-20260630/diffrhythm_outputs/full_285_prompt/output.wav
```

The rejected render followed the lyric broadly, but the ASR tail contained a
credit-like hallucination: `词曲 李宗盛`. The selected clean render used a
stricter prompt: only sing the supplied LRC lyrics, with no spoken words,
credits, songwriter names, artist names, or extra outro text.

Quality report:

```text
data/creative_projects/yun-hai-zhi-lian-diffrhythm-full-20260630/reviews/full-285-clean/QA.md
```

Key values:

```text
duration: 284.955 seconds
rms: 0.14191
peak: 0.99997
ASR overlap: 0.6332378223495702
gate: review
```

## Analysis

Pipeline run:

```text
data/runs/yun-hai-zhi-lian-diffrhythm-full-285-clean-analysis/
```

Important outputs:

```text
data/runs/yun-hai-zhi-lian-diffrhythm-full-285-clean-analysis/REPORT.md
data/runs/yun-hai-zhi-lian-diffrhythm-full-285-clean-analysis/analysis/chords.csv
data/runs/yun-hai-zhi-lian-diffrhythm-full-285-clean-analysis/analysis/beats.csv
data/runs/yun-hai-zhi-lian-diffrhythm-full-285-clean-analysis/analysis/lyrics.json
data/runs/yun-hai-zhi-lian-diffrhythm-full-285-clean-analysis/stems/vocals.wav
data/runs/yun-hai-zhi-lian-diffrhythm-full-285-clean-analysis/stems/drums.wav
data/runs/yun-hai-zhi-lian-diffrhythm-full-285-clean-analysis/stems/bass.wav
data/runs/yun-hai-zhi-lian-diffrhythm-full-285-clean-analysis/stems/other.wav
data/runs/yun-hai-zhi-lian-diffrhythm-full-285-clean-analysis/stems/instrumental.wav
data/runs/yun-hai-zhi-lian-diffrhythm-full-285-clean-analysis/stems/human_sound.wav
```

Detected tempo:

```text
60.09265988372093 BPM
```

## Lyric Correction Policy Used

The published active Mandarin track keeps the user's intended full lyric and
uses the LRC timing, cross-validated with same-vocal ASR and the pipeline ASR.
The model sang the structure of the song, but ASR garbled many CJK phrases. For
sound-close phrases, the website corrects back to the intended lyric instead of
publishing the recognizer's weaker guesses.

This follows the Musia rule:

```text
actual audible structure > close intended lyric > ASR guess > translation draft
```

The production caveat is that this render is a usable full-length DiffRhythm
candidate, not a perfect commercial master. Some phrases are still soft or
slightly garbled, but the public lyric timing now represents the intended
full-song structure and avoids the rejected candidate's credit hallucination.

## Website Update

Preparation script:

```text
scripts/prepare_yun_hai_zhi_lian_diffrhythm_full_285_fun_item.py
```

Updated website files:

```text
website/data/catalog.json
website/data/songs/yun-hai-zhi-lian/manifest.json
website/data/songs/yun-hai-zhi-lian/lyrics/zh-vocal/zh-Hans.json
website/data/songs/yun-hai-zhi-lian/lyrics/zh-vocal/en.json
website/data/songs/yun-hai-zhi-lian/lyrics/zh-vocal/ja.json
```

Public media id:

```text
yun-hai-zhi-lian
```

Website URL:

```text
https://fun.lazying.art/#yun-hai-zhi-lian
```

Public audio file in `../MusiaSongs`:

```text
audio/yun-hai-zhi-lian-yunhai-changge-diffrhythm-full-285-20260630.mp3
```

Public audio URL:

```text
https://lazyingart.github.io/MusiaSongs/audio/yun-hai-zhi-lian-yunhai-changge-diffrhythm-full-285-20260630.mp3
```

The older short ACE item remains separate:

```text
yun-hai-zhi-lian-haifeng-duange
```

## Validation

Commands run:

```bash
npm run website:validate
node bin/musia.js fun-audit --media-id yun-hai-zhi-lian
node bin/musia.js fun-audit --media-id yun-hai-zhi-lian-haifeng-duange
node --check website/app.js
git diff --check
git -C ../MusiaSongs diff --check
```

Results:

```text
ok: website follows fun.lazying.media.v1
ok: yun-hai-zhi-lian passed Fun media item audit
ok: yun-hai-zhi-lian-haifeng-duange passed Fun media item audit
```
