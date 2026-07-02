# Star Bucks Production Note

Date: 2026-07-02

## Concept

`Star Bucks` is an original English-first song seed about a man traveling at
sea. He speaks with wind, tide, moon, stars, and the living sea. He sees
star-lit bucks/deer swimming through the ocean and learns from them to keep
going.

The emotional influence is Mary Oliver's `Wild Geese` / Chinese title often
rendered as `野雁`: nature calling a lonely person back into belonging. This is
not a translation or quotation of that poem.

## Lyric Packages

- Main long lyric: `ideas-and-inspirations/star-bucks/lyrics.en.txt`
- Short performance lyric: `ideas-and-inspirations/star-bucks/lyrics.en.performance-short.txt`
- Selected vocal-hook lyric: `ideas-and-inspirations/star-bucks/lyrics.en.vocal-hook.txt`
- Optional mixed-language hook: `ideas-and-inspirations/star-bucks/lyrics.mixed-hook.txt`
- Producer brief: `ideas-and-inspirations/star-bucks/producer-brief.md`

## Generation Attempts

### Attempt 1

- Project: `data/creative_projects/star-bucks-20260702`
- Model: `acestep-v15-xl-sft`
- Steps: `50`
- Seed: `731001`
- Duration: `120s`
- Output: `data/creative_projects/star-bucks-20260702/ace_outputs/en/b1337b74-789e-2879-ae24-3444efb84f91.wav`
- Review: `data/creative_projects/star-bucks-20260702/reviews/20260702-233954/SONG_REVIEW.md`
- Caveat: ASR recovered unrelated generic outro text, so this was not selected.

### Attempt 2

- Project: `data/creative_projects/star-bucks-20260702`
- Correction: `data/creative_projects/star-bucks-20260702/corrections/20260702-234148/`
- Model: `acestep-v15-xl-sft`
- Steps: `50`
- Seed: `731117`
- Duration: `90s`
- Output: `data/creative_projects/star-bucks-20260702/ace_outputs/en_corrected_20260702-234148/38f100f4-ea5c-30c4-4575-b1d465c954d4.wav`
- Review: `data/creative_projects/star-bucks-20260702/reviews/20260702-234256/SONG_REVIEW.md`
- Caveat: ASR again recovered unrelated generic outro text; this was not selected.

### Selected Rough Candidate

- Project: `data/creative_projects/star-bucks-vocal-hook-20260702`
- Model: `acestep-v15-xl-sft`
- Steps: `50`
- Seed: `731231`
- Duration: `75s`
- WAV: `data/creative_projects/star-bucks-vocal-hook-20260702/selected/star-bucks-en-vocal-hook.wav`
- MP3: `data/creative_projects/star-bucks-vocal-hook-20260702/selected/star-bucks-en-vocal-hook.mp3`
- Review: `data/creative_projects/star-bucks-vocal-hook-20260702/reviews/20260702-234538/SONG_REVIEW.md`
- Analysis: `data/runs/star-bucks-vocal-hook-20260702-20260702-234538-analysis/`
- Stems: `data/runs/star-bucks-vocal-hook-20260702-20260702-234538-analysis/stems/`
- Chords: `data/runs/star-bucks-vocal-hook-20260702-20260702-234538-analysis/analysis/chords.csv`
- Beats: `data/runs/star-bucks-vocal-hook-20260702-20260702-234538-analysis/analysis/beats.csv`

## Quality Note

The selected candidate is a generated rough song candidate, not a website-ready
final. ASR did not reliably recover the planned lyric, but ASR can be weak on
AI singing. Use listening judgment before publishing. If this becomes a Fun
website item later, run the normal Musia website workflow: listen, correct
lyrics to the actual vocal, create timed JSON, cover, manifest, and validate.

