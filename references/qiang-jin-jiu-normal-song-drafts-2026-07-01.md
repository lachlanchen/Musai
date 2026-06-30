# 将进酒 Normal Song Drafts

Date: 2026-07-01

## Purpose

Create a normal adapted song from Li Bai's 《将进酒》, separate from the literal
original-poem `ACE Poetry Demo`.

Preferred workflow:

```text
poem spirit -> rewritten singable lyric -> ACE normal song -> large-v3 review -> website only after selection
```

The default future goal is a beautiful normal song. The original poem-recitation
workflow is kept only as an option.

## Project

- Project dir: `data/creative_projects/qiang-jin-jiu-normal-song-20260701/`
- Draft selection note: `data/creative_projects/qiang-jin-jiu-normal-song-20260701/SELECTED_VERSION.md`

Generated project data and audio are ignored by git.

## Candidates

Candidate 1 is the best current automated candidate:

- WAV: `data/creative_projects/qiang-jin-jiu-normal-song-20260701/ace_outputs/zh/6efc268a-3338-d611-f6ac-4d2b60384f49.wav`
- MP3: `data/creative_projects/qiang-jin-jiu-normal-song-20260701/selected/qiang-jin-jiu-adapted-normal-draft-candidate1.mp3`
- Review: `data/creative_projects/qiang-jin-jiu-normal-song-20260701/reviews/20260701-004055/SONG_REVIEW.md`
- Analysis: `data/runs/qiang-jin-jiu-normal-song-20260701-20260701-004055-analysis/`
- Quality note: large-v3 review passed, RMS healthy, but lyric overlap is only about `0.49`. Needs listening before website publication.

Candidate 3 is the best modern-lyric intent candidate:

- WAV: `data/creative_projects/qiang-jin-jiu-normal-song-20260701/ace_outputs/zh_corrected_20260701-004438/58468c65-6d46-546d-a897-7d7e793d1b46.wav`
- MP3: `data/creative_projects/qiang-jin-jiu-normal-song-20260701/selected/qiang-jin-jiu-adapted-normal-draft-candidate3.mp3`
- Review: `data/creative_projects/qiang-jin-jiu-normal-song-20260701/reviews/20260701-004527/SONG_REVIEW.md`
- Analysis: `data/runs/qiang-jin-jiu-normal-song-20260701-20260701-004527-analysis/`
- Quality note: first minute is structurally clearer, but automated lyric recovery is lower. Needs listening before selection.

Rejected or experimental:

- Candidate 2: hook garbled as `请营救`; rejected.
- Candidate 4: skipped opening and much of the lyric; rejected.
- Candidate 5: compact native-script hook still garbled; rejected.
- Candidate 6: pinyin-guided route produced odd Mandarin-like words; experimental only.

## Website Decision

Do not publish the normal adapted song to `fun.lazying.art` until one candidate
is accepted by listening. When accepted:

- media id should be `qiang-jin-jiu-normal` or `qiang-jin-jiu-song`;
- visible title should be plain `将进酒`;
- existing `qiang-jin-jiu` remains `将进酒 · ACE Poetry Demo`;
- lyrics must be corrected from the selected candidate's own large-v3 ASR and
  listening evidence;
- record the normal version later, not the poetry-demo version.
