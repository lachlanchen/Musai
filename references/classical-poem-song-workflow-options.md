# Classical Poem Song Workflow Options

Use this for Li Bai, Tang poetry, Song lyrics, or any classical text that may be
too dense for ACE/YuE to sing literally.

## Default: Adapted Normal Song

Use this when the user wants a beautiful song.

Goal:

```text
poem spirit -> modern singable lyric -> ACE full-song generation -> deep lyric correction -> website
```

This is the default Musia route because it usually produces better music than a
literal poem recital.

Rules:

- preserve the poem's core emotion, iconic images, and famous lines;
- rewrite into short breath-friendly sections: verse, pre-chorus, chorus,
  bridge/outro;
- keep some original lines only where they are naturally singable;
- use musical space, held vowels, and repeated hooks instead of cramming every
  couplet;
- check rhyme, cadence, and Mandarin tone comfort before generation;
- after generation, correct lyrics with large ASR plus listening before website
  or LazyEdit publication.

Good catalog naming:

- standard adapted ACE version: plain title, such as `将进酒`;
- no visible suffix.

## Optional: Original Poem / Poetry Demo

Use this only when the user explicitly asks for original-text-only lyrics or a
poetry-recitation-style demo.

Goal:

```text
original poem text -> ACE poetry-song attempt -> ASR/listening correction -> website as demo
```

Rules:

- keep the original poem text as the prompt lyric;
- expect ACE may skip, merge, repeat, or garble dense classical lines;
- label the public item clearly, such as `ACE Poetry Demo`;
- do not call it the main version when a normal song exists;
- never use prompt-only lyrics for publication; correct the website JSON from
  the actual audio.

Good catalog naming:

- `将进酒 · ACE Poetry Demo`
- `侠客行 · Original Poem Demo`

## Correction Standard

For public songs and recordings, use:

```bash
PYTHONNOUSERSITE=1 conda run --no-capture-output -n musia python \
  scripts/build_lyric_correction_packet.py \
  --title "Song Title" \
  --audio SELECTED.wav \
  --vocal-stem ANALYSIS/stems/vocals.wav \
  --expected-lyrics lyrics.txt \
  --language zh \
  --models large-v3 \
  --output-dir data/creative_projects/<song>/corrections/deep-large-YYYYMMDD
```

Then use `small` or `medium` only as cross-checks. Publish only after:

- active vocal lyrics match the actual sung structure;
- repeated or skipped lines are reflected truthfully;
- translations use the corrected active lyric, not the draft prompt;
- Mandarin pinyin, Japanese furigana, or Cantonese Jyutping are clean;
- `npm run website:validate` and `node bin/musia.js fun-audit --media-id ID`
  pass.
