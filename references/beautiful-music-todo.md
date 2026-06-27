# Musai Beautiful Music TODO

Goal: produce a convincing Chinese version of a song, with the same musical feeling and a real sung vocal, not speech TTS.

## Completed Setup

- [x] Finish SoulX-Singer model and preprocessing downloads.
- [x] Install the isolated SoulX env in `.conda/soulxsinger`.
- [x] Download ACE-Step 1.5 XL checkpoints for polished full-song experiments.
- [x] Download and install DiffRhythm v1.2 full.
- [x] Download YuE minimal Chinese full-song generation checkpoints.
- [x] Download and install SongGen with FlashAttention.
- [x] Download and install HeartMuLa.
- [x] Download and install MOSS-Music with a TorchCodec runtime wrapper.

## Priority 1: Best Same-Music Chinese Vocal

- [ ] Convert the existing full-song run into SoulX target metadata:
  - source vocal audio
  - phrase timings
  - corrected melody MIDI/F0
  - adapted Chinese lyric lines
- [ ] Run a short 20-40 second chorus/verse first.
- [ ] Mix SoulX Chinese vocal with original `bass`, `drums`, and `other`.
- [ ] Compare against the previous fallback vocal render and keep only the better result.

## Priority 2: Professional Vocal Trial Route

- [ ] Use official Synthesizer V Studio 2 Pro trial on Windows/macOS if available.
- [ ] Use official ACE Studio trial/free plan for MIDI + Chinese lyrics if available.
- [ ] Export Mandarin vocal stems.
- [ ] Mix exported vocal stems with Musai Demucs stems.

## Priority 3: Beautiful Full-Song Alternatives

- [ ] Test ACE-Step 1.5 XL for a polished Chinese reinterpretation.
- [ ] Test DiffRhythm v1.2 full.
- [ ] Test YuE minimal Chinese full-song generation.
- [ ] Test SongGen, HeartMuLa, and MOSS-Music-assisted QA.
- [ ] Keep these outputs labeled as "inspired/new song" unless they preserve the original arrangement.

## Quality Gate

A render is not accepted as "final" unless:

- The vocal is clearly audible.
- The vocal is sung, not spoken.
- The Chinese lyrics are natural and singable.
- The rhythm follows the original phrase timing.
- The mix has `bass`, `drums`, `other`, and the new vocal stem.
- The output paths include stems, lyrics, and final mix.
