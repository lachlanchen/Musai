# SoulX Verse Tool

`musia soulx-verse` creates a short original bilingual singing package:

```bash
musia soulx-verse \
  --title "Rain Day" \
  --idea "A gentle rainy-day musical short film verse in Chinese and English" \
  --provider deepseek
```

Outputs:

```text
lyrics.md
target_metadata.json
melody.wav
vocal.wav
mix.wav
manifest.json
LALACHAN_HANDOFF.md
```

The tool can optionally ask DeepSeek or OpenAI to refine the lyric into a safer, more singable four-line verse. If no API key is available, it falls back to a local original rain-day lyric.

## What SoulX Needs

SoulX does not accept only a natural-language prompt. It needs aligned singing metadata:

- text tokens;
- phonemes;
- note durations;
- note pitches;
- note types;
- F0 curve.

The Musia verse tool creates this metadata automatically for short Mandarin/English lines, then calls the local SoulX wrapper with `CONTROL=score`.

## CLI Examples

Generate the default rain-day verse:

```bash
musia soulx-verse --title "Rain Day"
```

Use your own lyrics:

```bash
musia soulx-verse \
  --title "My Bilingual Hook" \
  --lyrics "雨落窗前 rain on my mind
街灯微亮 I walk through time
风把旧梦 wash into blue
等云散开 I sing with you"
```

Write metadata and melody only:

```bash
musia soulx-verse --skip-soulx --provider offline
```

## Quality Rule

Accept a render only if:

- the vocal is clearly sung;
- the mixed file keeps the vocal audible;
- the lyric is original and legal to use;
- real-person voice imitation is not requested unless there is explicit consent;
- the run folder contains `manifest.json` and `LALACHAN_HANDOFF.md`.

