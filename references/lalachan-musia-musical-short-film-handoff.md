# LALACHAN Musical Short Film Handoff

Musia can now create a short original music package for LALACHAN-style animation:

```bash
musia soulx-verse --title "Rain Day" --idea "A rainy bilingual musical short film"
```

Use these artifacts:

```text
mix.wav          final first-pass soundtrack
vocal.wav        dry SoulX singing voice
melody.wav       melody guide / lightweight backing
lyrics.md        subtitles and shot timing reference
manifest.json    reproducibility record
LALACHAN_HANDOFF.md  per-run handoff note
```

Recommended video workflow:

1. Generate the Musia verse package.
2. Use `lyrics.md` to plan shots, subtitles, and mouth/gesture timing.
3. Use `mix.wav` as the soundtrack for the first video render.
4. If the short film needs richer music, keep `vocal.wav` and replace or expand `melody.wav` with rain ambience, piano, pads, drums, or orchestration.
5. Save the Musia run path in the LALACHAN video manifest.

Input checks:

- User intent should be original music, or the user must confirm rights for any reference song.
- Celebrity names are style references only, not voice-cloning instructions.
- Voice cloning requires explicit voice consent.
- Lyrics should be original, not copied from existing songs.
- If the audio sounds weak, regenerate metadata/lyrics before making the final animation.

