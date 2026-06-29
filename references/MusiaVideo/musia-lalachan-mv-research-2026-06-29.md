# Musia To LALACHAN MV Research

Date: 2026-06-29

This note records the current practical path for turning a reviewed Musia song into a LALACHAN/Xiaoyunque music video.

## Current Feasibility

The pipeline is feasible now:

```text
Musia reviewed song
-> website/public audio package in MusiaSongs
-> LALACHAN character/image references
-> Xiaoyunque/Seedance video generation
-> verify generated video
-> mux exact Musia audio back if the video model changes the soundtrack
-> optional LazyEdit portrait/publish path
```

The important limitation is that Xiaoyunque may treat uploaded audio as mood/timing reference instead of an exact final soundtrack. Therefore the Musia song remains the audio authority, and the final publishable MP4 should be song-locked with FFmpeg when needed.

## Recommended Routes

### Full-song MV

Use this when the song is already reviewed and the user wants a real MV. For a song longer than about 45 seconds, prefer Xiaoyunque `创作 Agent` or the most suitable long-video workflow. Ask the video tool to build scene timing around the uploaded audio duration, then correct duration before paid render if the generated storyboard drifts.

### Hook / Chorus MV

Use this for testing, low-credit runs, social clips, or when the hook is much stronger than the full song. Trim a 15-30 second section from Musia, usually the first chorus or final chorus, then generate a short visual idea with fewer story beats.

Example for Xiao Xiao Zhu:

```text
Full song: 0.00-92.00s
First chorus: 27.91-43.99s
Final chorus: 62.59-80.07s
```

## Handoff Requirements

Every MV handoff should include:

- reviewed audio path and public URL;
- duration, language, BPM/key if available;
- actual lyric timing or section timing;
- asset upload order for LALACHAN references;
- no-path Xiaoyunque prompt;
- short agent message for another Codex/LALACHAN session;
- final audio replacement command;
- explicit no-subtitle/no-file-path instruction.

## Quality Rules

- The video follows the song. Do not change the song to match the video.
- Dialogue must be sparse and placed in musical gaps.
- For LALACHAN character MVs, one character can be lead singer while the others dance, clap, echo, or call out short lines.
- Do not burn lyrics/subtitles into Xiaoyunque output unless specifically asked.
- If the song title or lyric is teasing, frame it as affectionate and cute in the MV. Avoid literal insult visuals.
- Verify final MP4 duration, resolution, and audio stream with `ffprobe`.

## Relevant Local Paths

Musia skill:

```text
/home/lachlan/.codex/skills/musia-lalachan-mv-workflow/SKILL.md
```

LALACHAN references:

```text
/home/lachlan/ProjectsLFS/LALACHAN/references/MusiaVideo/
```

Musia references:

```text
/home/lachlan/ProjectsLFS/Musia/references/MusiaVideo/
```

