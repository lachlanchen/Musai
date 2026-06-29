# 你是一只猪 / You Little Piggy / きみはこぶた

## Core Idea

A cute, joyful, slightly whiny comfort song about wanting to become a small pig:
eat well, sleep deeply, avoid homework, work, papers, reports, and pressure.

The emotional target is not pure comedy. It should feel playful on the surface,
but quietly resonate with tired students, researchers, office workers, and anyone
who wants to hide in a warm blanket for one night.

## Localized Titles

| Language | Title | Note |
| --- | --- | --- |
| Chinese | `你是一只猪` | Direct, funny, memorable, slightly teasing. |
| English | `You Little Piggy` | Softer and more affectionate than literal `You Are a Pig`. |
| Japanese | `きみはこぶた` | Cute and intimate; avoids the harsher feel of literal `あなたは豚`. |

## Desired Feeling

```text
joyful bedroom pop
sweet indie folk
slightly whiny / 撒娇 / a little complainy
warm, catchy, comforting
cute but not childish
funny but emotionally true
```

## Music Direction

```text
Tempo: 100-108 BPM
Key: G major or C major
Time: 4/4
Arrangement: ukulele or soft acoustic guitar, light piano, handclaps,
             warm bass, gentle drums, playful ooh/ohoh backing vocals
Vocal: clear upfront Chinese vocal first; cute, natural, slightly lazy;
       no real-singer imitation
Structure: verse -> pre-chorus -> chorus -> verse -> bridge -> final chorus
```

## Quality Rules

- Quality first: leave space, keep joy, and do not cram the melody.
- Use short lines, repeated hooks, held vowels, and rests.
- Chinese master first, because this is the emotional source language.
- After the Chinese master is selected, analyze stems, beats, chords, phrase
  timing, and melody/F0.
- Use the master analysis as a soft lead-sheet guide for English and Japanese.
- If same-melody control hurts quality, keep the target-language version as a
  high-quality companion instead of forcing exact melody.

## Files

| File | Purpose |
| --- | --- |
| `source-and-cleaned-idea.md` | Original input and cleaned lyric seed |
| `lyrics.zh-Hans.txt` | Chinese master lyric for first generation |
| `lyrics.en.txt` | English singable adaptation |
| `lyrics.ja.txt` | Japanese singable adaptation |
| `lyrics.zh-Hans.master-spacious.txt` | Selected Mandarin master lyric used for the best Chinese render |
| `lyrics.zh-Hans.performance-master.txt` | Alternate Mandarin performance lyric tested during correction |
| `lyrics.en.performance-companion.txt` | Final English companion lyric used for generation |
| `lyrics.ja.performance-companion.txt` | Japanese companion lyric with kanji/kana mix |
| `lyrics.ja.kana-performance-companion.txt` | Final kana-heavy Japanese companion lyric used for selected generation |
| `producer-brief.md` | Song prompt and quality direction |
| `generation-plan.md` | One-by-one Musia master-companion plan |

## Generated Project

The first generated project is:

```text
data/creative_projects/ni-shi-yi-zhi-zhu-20260629
```

Selected outputs:

```text
data/creative_projects/ni-shi-yi-zhi-zhu-20260629/selected/ni-shi-yi-zhi-zhu-zh-master.wav
data/creative_projects/ni-shi-yi-zhi-zhu-20260629/selected/you-little-piggy-en.wav
data/creative_projects/ni-shi-yi-zhi-zhu-20260629/selected/kimi-wa-kobuta-ja.wav
```

The actual production run used a quality-first master-companion workflow:

1. Render Mandarin first.
2. Review with ASR and Musia analysis.
3. Select the best Mandarin master.
4. Extract stems, beats, chords, and melody/F0.
5. Use DeepSeek writer/finalizer plus OpenAI reviewer for companion lyric packages.
6. Manually fix the EN/JP companion lyrics to remove ASR-induced mistakes.
7. Render EN/JP as soft companions, not strict melody clones.
