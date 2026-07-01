# 蜀道难 Original-Text Reordered Song Check

Date: 2026-07-01

## Goal

Generate a beautiful, attractive song version of 李白《蜀道难》 using only
original poem text/fragments, with selection, repetition, and reordering allowed.
The desired opening is immediate and memorable, not a long prelude.

## Source-Text Arrangement

Full arrangement:

```text
poetries/derived/shu-dao-nan-original-text-song-2026-07-01.md
```

Compact lyric files used for the checked attempts:

```text
data/creative_projects/shu-dao-nan-20260701/lyrics/zh-original-text-ultra.txt
data/creative_projects/shu-dao-nan-20260701/lyrics/zh-original-text-ultra-phonetic.txt
data/creative_projects/shu-dao-nan-20260701/lyrics/zh-original-text-simple.txt
data/creative_projects/shu-dao-nan-20260701/lyrics/shu_dao_nan_original_hook_95.lrc
data/creative_projects/shu-dao-nan-20260701/lyrics/shu_dao_nan_original_hook_95_phonetic.lrc
data/creative_projects/shu-dao-nan-20260701/lyrics/shu_dao_nan_original_hook_95_simple.lrc
```

## Attempts

### ACE-Step XL SFT

Config:

```text
data/creative_projects/shu-dao-nan-20260701/ace_zh_original_text_ultra_sft.toml
```

Result: rejected. One candidate produced subtitle-credit leakage, and another
had no intelligible ASR recovery.

### ACE-Step XL Turbo, Long/Direct Original Text

Configs:

```text
data/creative_projects/shu-dao-nan-20260701/ace_zh_original_text_direct_xl.toml
data/creative_projects/shu-dao-nan-20260701/ace_zh_original_text_hook_xl.toml
```

Result: rejected. The best large-v3 lyric overlap was only about `0.252`, with
the opening and several classical phrases garbled.

### DiffRhythm Hook-First LRC

Project:

```text
data/creative_projects/shu-dao-nan-original-text-dr-20260701
```

Best draft:

```text
data/creative_projects/shu-dao-nan-original-text-dr-20260701/diffrhythm_outputs/hook_95_b_phonetic/output.wav
data/creative_projects/shu-dao-nan-original-text-dr-20260701/selected/shu-dao-nan-original-text-dr-hook-95-b-draft.mp3
```

Large-v3 check:

```text
data/creative_projects/shu-dao-nan-original-text-dr-20260701/reviews/hook_95_b_phonetic_large_public/QA.md
```

Large-v3 ASR overlap: `0.4380165289256198`.

ASR recovered a sound-close opening:

```text
书道之难 难遇上晴天 一许兮 为乎高哉
书道之难 难遇上晴天
```

This is close enough to inspect as a draft, but not clean enough for public
website publishing without regeneration or manual acceptance.

### ACE-Step Compact Source Text

Configs:

```text
data/creative_projects/shu-dao-nan-20260701/ace_zh_original_text_simple_xl.toml
data/creative_projects/shu-dao-nan-20260701/ace_zh_original_text_simple_v15.toml
```

Result: rejected. The compact XL pass produced almost no recoverable lyric, and
the smaller v15 pass produced empty or near-empty ASR on all four seeds.

## Analysis Artifacts For Selected Draft

Full Musia pipeline run:

```text
data/runs/shu-dao-nan-original-text-dr-hook-95-b-analysis/
```

Important outputs:

```text
data/runs/shu-dao-nan-original-text-dr-hook-95-b-analysis/REPORT.md
data/runs/shu-dao-nan-original-text-dr-hook-95-b-analysis/stems/vocals.wav
data/runs/shu-dao-nan-original-text-dr-hook-95-b-analysis/stems/drums.wav
data/runs/shu-dao-nan-original-text-dr-hook-95-b-analysis/stems/bass.wav
data/runs/shu-dao-nan-original-text-dr-hook-95-b-analysis/stems/other.wav
data/runs/shu-dao-nan-original-text-dr-hook-95-b-analysis/stems/human_sound.wav
data/runs/shu-dao-nan-original-text-dr-hook-95-b-analysis/stems/instrumental.wav
data/runs/shu-dao-nan-original-text-dr-hook-95-b-analysis/analysis/chords.csv
data/runs/shu-dao-nan-original-text-dr-hook-95-b-analysis/analysis/beats.csv
data/runs/shu-dao-nan-original-text-dr-hook-95-b-analysis/analysis/lyrics.json
```

Detected tempo: about `198.77 BPM`.

## Decision

Do not publish this original-text reordered version as a final-quality song.
Keep it as a checked `DR Draft`. This route showed that DiffRhythm with timed
LRC can align lyrics, but the melody and singing quality are not good enough for
Musia's beautiful-song standard. Use ACE/ACE-Step as the default/final route for
future beautiful songs.

Tail correction after user listening and isolated no-VAD ASR:

```text
small no-VAD:  暗示萬河雷 / 已負擔 / 萬富臥鎧 / 京城遂雲了 / 不如早還假
medium no-VAD: 三十万盒泪 已负担 / 万夫我开 京城碎云了 / 不如早还家
```

Public subtitle tail:

```text
砯崖转石万壑雷
一夫当关
万夫莫开
锦城虽云乐
不如早还家
```

For the next attempt:

- keep the hook-first opening `蜀道之难 / 难于上青天`;
- keep the compact source-text selection rather than the full poem;
- use ACE/ACE-Step first for song quality;
- only use DiffRhythm LRC for an explicitly experimental lyric-adherence check;
- add manual timing gaps and fewer long phrases;
- only reintroduce `噫吁嚱` after the opening hook is stable;
- publish only if large-v3 plus listening supports the corrected lyric text.
