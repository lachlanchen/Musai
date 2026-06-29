# Generation Plan

## Goal

Create a high-quality, resonant, playful song in three languages:

```text
1. Chinese master: 你是一只猪
2. English companion: You Little Piggy
3. Japanese companion: きみはこぶた
```

The Chinese version is the master because the title `你是一只猪` and the hook
`小小猪` carry the original teasing comfort. English and Japanese should be
culturally suitable singable adaptations, not literal translations. English uses
`You Little Piggy`, because `You Are a Pig` sounds too insulting in English.
Japanese uses `きみはこぶた`, because it keeps the affectionate tone.

## Step 1 - Chinese Master

Create a Musia song project:

```bash
PYTHONNOUSERSITE=1 conda run -n musia python scripts/musia_song_workbench.py init \
  --title "你是一只猪" \
  --idea "Cute joyful comfort song about wanting to become a small happy pig and escape homework, work, papers, and assessments for one night." \
  --vocal-language zh \
  --language zh \
  --lyrics-file ideas-and-inspirations/xiao-xiao-zhu/lyrics.zh-Hans.txt \
  --genre "joyful bedroom pop, cute indie folk" \
  --style "ukulele, soft acoustic guitar, light piano, gentle drums, warm bass, handclaps, playful ooh-ooh backing vocals" \
  --mood "cute, joyful, slightly whiny, comforting, funny, emotionally resonant" \
  --voice-notes "clear upfront Mandarin Chinese vocal, cute lazy phrasing, natural pronunciation, no real singer imitation" \
  --duration 88 \
  --bpm 104 \
  --keyscale "G major" \
  --seed 731231 \
  --inference-steps 12 \
  --guidance-scale 1.0
```

Generate:

```bash
data/creative_projects/<project>/commands.sh generate
```

Review:

```bash
data/creative_projects/<project>/commands.sh review
```

Accept the Chinese master only if:

- vocal is clearly audible;
- Mandarin is recognizable enough;
- chorus hook `小小猪` is memorable;
- the song feels joyful but a little whiny;
- the melody has space and does not cram lines;
- phrase endings are not clipped.

## Step 2 - Deep Analysis

Run Musia analysis on the accepted Chinese master:

```bash
data/creative_projects/<project>/commands.sh analyze
```

Expected evidence:

```text
stems/vocals.wav
stems/drums.wav
stems/bass.wav
stems/other.wav
analysis/beats.csv
analysis/chords.csv
analysis/melody_f0.csv
analysis/lyrics.json
```

## Step 3 - Master-Companion Package

Use the selected Chinese master audio and lyrics:

```bash
PYTHONNOUSERSITE=1 conda run -n musia python scripts/musia_master_companion_pipeline.py \
  --title "你是一只猪" \
  --idea "Joyful cute comfort song about becoming a small pig to escape pressure while keeping warmth and hope." \
  --master-language zh \
  --master-audio <selected-chinese-master.wav-or-mp3> \
  --master-lyrics-file ideas-and-inspirations/xiao-xiao-zhu/lyrics.zh-Hans.txt \
  --run-analysis \
  --target-languages en ja \
  --control-policy quality-first \
  --writer-provider deepseek \
  --reviewer-provider openai \
  --final-provider deepseek
```

Outputs:

```text
phrase_map.json
master_summary.json
targets/en/target_lyrics.txt
targets/en/ACE_SOFT_COMPANION_PROMPT.md
targets/en/STRICT_SVS_HANDOFF.md
targets/ja/target_lyrics.txt
targets/ja/ACE_SOFT_COMPANION_PROMPT.md
targets/ja/STRICT_SVS_HANDOFF.md
```

## Step 4 - English Companion

Use the English `ACE_SOFT_COMPANION_PROMPT.md` first. The goal is:

```text
same emotional arc
same BPM/key/chord feel
similar phrase density
natural English stress and rhyme
beautiful vocal over strict sameness
```

If the generated English vocal is beautiful but not identical in melody, keep it
as the public companion. Use strict SVS only if it sounds better.

## Step 5 - Japanese Companion

Use the Japanese `ACE_SOFT_COMPANION_PROMPT.md` first. The goal is:

```text
same cute comfort emotion
Japanese mora flow
こぶた hook is memorable
押韵 through vowel/mora echoes
natural particles and no cramped lines
```

If native Japanese generation has unclear lyrics, simplify the lyric and
regenerate rather than forcing exact translation.

## Publication

Only publish after:

- ASR/listening pass for each vocal;
- lyric correction against actual audio;
- per-vocal lyric JSON if timings differ;
- pinyin for Chinese;
- furigana for Japanese;
- cover image;
- Fun website validation and audit.

## Completed Prototype Run - 2026-06-29

Project:

```text
data/creative_projects/ni-shi-yi-zhi-zhu-20260629
```

Selected audio:

```text
data/creative_projects/ni-shi-yi-zhi-zhu-20260629/selected/ni-shi-yi-zhi-zhu-zh-master.wav
data/creative_projects/ni-shi-yi-zhi-zhu-20260629/selected/you-little-piggy-en.wav
data/creative_projects/ni-shi-yi-zhi-zhu-20260629/selected/kimi-wa-kobuta-ja.wav
```

Selected lyrics:

```text
data/creative_projects/ni-shi-yi-zhi-zhu-20260629/selected/lyrics.zh-Hans.master.txt
data/creative_projects/ni-shi-yi-zhi-zhu-20260629/selected/lyrics.en.txt
data/creative_projects/ni-shi-yi-zhi-zhu-20260629/selected/lyrics.ja.txt
```

Reviews:

```text
data/creative_projects/ni-shi-yi-zhi-zhu-20260629/reviews/20260629-192414/SONG_REVIEW.md
data/creative_projects/ni-shi-yi-zhi-zhu-20260629/companions/en/reviews/20260629-193403/SONG_REVIEW.md
data/creative_projects/ni-shi-yi-zhi-zhu-20260629/companions/ja/reviews/20260629-193836/SONG_REVIEW.md
```

Analysis runs:

```text
data/runs/ni-shi-yi-zhi-zhu-20260629-20260629-192414-analysis
data/runs/en-20260629-193403-analysis
data/runs/ja-20260629-193836-analysis
```

Master-companion package:

```text
data/creative_projects/ni-shi-yi-zhi-zhu-20260629/master-companion-zh-to-en-ja
```

Notes:

- The first Mandarin render was too word-dense, so the accepted master used `lyrics.zh-Hans.master-spacious.txt`.
- The automatic companion lyric package succeeded with DeepSeek and OpenAI, but inherited some ASR mistakes from the Mandarin source. The final EN/JP render lyrics were manually corrected before generation.
- English produced a strong first companion pass.
- Japanese needed two correction passes. The selected take is the shorter kana-heavy correction, which avoided the long filler intro and preserved most of the lyric structure.
