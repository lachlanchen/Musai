# 云海之恋 · 海风短歌

Date: 2026-06-30

## Goal

Create a shorter ACE-Step version of `云海之恋` that is not over-simplified.
The target is closer to prior successful Musia ACE songs: around 80-95 seconds,
short breathable lines, a real chorus, and enough lyric density to carry the
emotion without cramming the melody.

## Lyric Density Lesson

The failed sparse pass had only 21 short lines and about 101 Chinese lyric
characters. That made the song feel too empty. Stronger previous ACE examples
such as `你是一只猪` used many short lines, roughly 40+ lines, with average CJK
line length around 4-7 characters and enough repeated hook material.

For this pass, the draft used:

- 42 sung draft lines
- 191 Chinese characters
- 90-96 second target duration
- short line lengths and repeated chorus language

The practical rule is: do not reduce an emotional short song to a few phrases.
Use compact lines, leave space, but keep a complete verse / pre-chorus / chorus
shape.

## Tested Renders

| Seed | Duration | ASR overlap | Gate | Result |
| --- | ---: | ---: | --- | --- |
| 731531 | 90s | 0.524 | pass | selected |
| 731532 | 96s | 0.508 | pass | more final material but more garbled middle |
| 731231 | 92s | 0.267 | review | rejected |

Selected audio:

```text
data/creative_projects/yun-hai-zhi-lian-haifeng-duange-20260630/ace_outputs/zh/dc783051-1c6c-979a-6600-3f2f49193131.wav
```

Selected MP3:

```text
data/creative_projects/yun-hai-zhi-lian-haifeng-duange-20260630/selected/yun-hai-zhi-lian-haifeng-duange-zh-Hans-ace-20260630.mp3
../MusiaSongs/audio/yun-hai-zhi-lian-haifeng-duange-zh-Hans-ace-20260630.mp3
```

Analysis run:

```text
data/runs/yun-hai-zhi-lian-haifeng-duange-20260630-analysis
```

## Lyric Correction

The selected render did not sing the full draft. It mostly kept the verse,
pre-chorus, first chorus, and outro, while skipping or heavily compressing the
bridge and final chorus. The website item therefore publishes corrected lyrics
that match the selected vocal structure, not the full prompt.

Important correction choices:

- `想念像风，靠近你身边` was kept from the prompt because the ASR variants were
  sound-close and less grammatical.
- The first published pass used `我想了五年`, but the later deeper correction
  replaced it with `我随流年` because multiple ASR passes heard a
  `水/睡/流年`-like phrase.
- Draft bridge/final-chorus lines are omitted from the public lyric JSON because
  they were not supported by the selected vocal.

### 2026-06-30 Deep Correction Update

After user listening feedback, the short-song lyric track was checked again
against:

```text
data/runs/yun-hai-zhi-lian-haifeng-duange-20260630-analysis/analysis/lyrics.json
data/creative_projects/yun-hai-zhi-lian-haifeng-duange-20260630/reviews/selected-medium-asr-20260630/QA.md
data/creative_projects/yun-hai-zhi-lian-haifeng-duange-20260630/reviews/vocal-stem-medium-asr-20260630/QA.md
```

The earlier public track missed sung material that ASR swallowed or garbled:

- opening `天蓝蓝 / 海蓝蓝`;
- outro repeat `天蓝蓝 / 海蓝蓝`;
- a `水/睡/流年`-like phrase before `来到你身边`.

No-VAD ASR recovered the opening and outro as sound-close variants such as
`天来了 / 海来了` and `天烂烂 / 海烂烂`. Because these are close to the reference
lyric and confirmed by listening feedback, the website now publishes them as:

```text
14.68-16.20 天蓝蓝
16.20-17.78 海蓝蓝
72.64-74.20 天蓝蓝
74.20-75.76 海蓝蓝
```

The middle phrase previously published as `我想了五年` is now corrected to
`我随流年`, because the selected-audio and vocal-stem ASR repeatedly heard
`水/睡/流年` rather than the original prompt line. This keeps the lyric closer
to the actual rendered sound while still reading naturally.

The updated active Mandarin website track now has 25 timed lines:

```text
website/data/songs/yun-hai-zhi-lian-haifeng-duange/lyrics/zh-vocal/zh-Hans.json
```

Website media item:

```text
website/data/songs/yun-hai-zhi-lian-haifeng-duange/manifest.json
```

The prior long item was renamed for clarity:

```text
云海之恋 · 云海长歌
```

The new ACE item is:

```text
云海之恋 · 海风短歌
```

## Validation

Passed locally:

```bash
npm run website:validate
node bin/musia.js fun-audit --media-id yun-hai-zhi-lian-haifeng-duange
node bin/musia.js fun-audit --media-id yun-hai-zhi-lian
node --check website/app.js
git diff --check
git -C ../MusiaSongs diff --check
```
