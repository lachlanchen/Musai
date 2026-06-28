---
name: musia-music-production
description: Use when generating, correcting, reviewing, or handing off original music in Musia, including idea-to-song, lyrics-to-song, melody/chord-controlled songs, ACE-Step/YuE/SoulX route selection, vocal quality checks, song review reports, and LALACHAN song-first video handoffs.
---

# Musia Music Production

Use this skill for original song creation and review. For strict same-song localization, also use `musia-song-localization`.

## Default Repo

```text
/home/lachlan/ProjectsLFS/Musia
```

## Core Rule

Do not accept a generated song just because a WAV exists. A usable song needs:

- audible sung vocal;
- healthy levels;
- coherent tempo/chord analysis;
- saved lyrics and prompt;
- review report;
- human listening pass when the result matters.

Quality comes before same-melody control. If a same-score/same-F0 route makes
the vocal, pronunciation, phrasing, or arrangement worse, label that render
experimental and leave it out of the public/final path. Regenerate with the
best full-song model instead, even if EN/JP/ZH end up as independent high-quality
versions rather than one perfectly shared melody.

Avoid real singer imitation or voice cloning unless the user owns or has explicit consent.

Before generating or accepting EN/JP/ZH lyrics, do an LLM lyric-quality pass
when an API/model is available. Use OpenAI, DeepSeek, or a strong Codex/GPT-5.5
reasoning pass to check rhythm fit, line length, breath points, rhyme / 押韵,
English stress, Chinese tone comfort, Japanese mora flow, and emotional clarity.
Revise lyrics before generation if the LLM flags awkward rhythm, weak rhyme,
overlong lines, or unnatural CJK wording.

Do not cram words into the song just to preserve every detail. Use musical
space: 留白, held vowels, rests, repeated hooks, and breath-friendly pauses.
Some lines should be sparse and some can be fuller; the goal is a proper fit
to the melody and emotion, not the fewest words and not the most words.

## Fast Workflow

Create a song package:

```bash
musia song init \
  --title "Song Title" \
  --idea "short concept" \
  --vocal-language ja \
  --lyrics-file lyrics.txt \
  --genre "cinematic J-pop" \
  --style "piano, warm strings, gentle drums" \
  --voice-notes "clear upfront young female vocal, no real singer imitation"
```

Generate:

```bash
data/creative_projects/<song-id>/commands.sh generate
```

Review:

```bash
data/creative_projects/<song-id>/commands.sh review
```

Correct:

```bash
musia song correct \
  --project-dir data/creative_projects/<song-id> \
  --issues "vocal unclear or endings clipped" \
  --caption-extra "clearer vocal, fewer words per line" \
  --lyrics-file corrected-lyrics.txt
```

Handoff to LALACHAN:

```bash
musia song handoff \
  --project-dir data/creative_projects/<song-id> \
  --audio data/creative_projects/<song-id>/final/selected.mp3 \
  --cover data/creative_projects/<song-id>/assets/cover-16x9.png
```

## Reusable Script

Primary script:

```text
scripts/musia_song_workbench.py
```

It supports:

```text
init
review
correct
handoff
find-audio
```

Generated song folders are intentionally ignored by git:

```text
data/creative_projects/<song-id>/
```

## Model Routing

- Idea/lyrics to full song: ACE-Step 1.5 first.
- Vocal-only controlled short hook: SoulX if language metadata is supported.
- Strict source-song localization: Demucs/analysis plus YingMusic/SoulX prep, not full-song generation.
- Same melody is optional when it hurts quality. Prefer high-quality independent ACE/YuE language renders over low-quality same-score vocals.
- If Japanese/Chinese lyric accuracy is poor: shorten lines, reduce kanji ambiguity, increase vocal clarity in caption, try new seed/model, or use a specialized vocal workflow.

## References

Read only as needed:

```text
references/musia-song-workbench.md
references/lalachan-song-first-video-workflow.md
references/musia-full-capability-guide.md
references/musia-creative-studio.md
```
