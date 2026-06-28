# SoulX Good Vocal Runs - 2026-06-28

The following local SoulX outputs were identified as useful because they sound mainly like clean human singing / vocal-only `human_sound`:

```text
data/runs/soulx-wrapper-demo-en/generated.wav
data/runs/soulx-wrapper-demo-zh/generated.wav
data/runs/soulx-demo-zh/generated.wav
```

## Audio Properties

| Run | Duration | Format | Use |
| --- | ---: | --- | --- |
| `soulx-wrapper-demo-en` | 6.90 s | 24 kHz mono WAV | English vocal-only quality reference |
| `soulx-wrapper-demo-zh` | 6.71 s | 24 kHz mono WAV | Mandarin vocal-only quality reference |
| `soulx-demo-zh` | 6.71 s | 24 kHz mono WAV | Mandarin vocal-only quality reference |

These outputs should be treated as dry vocal assets, not full songs. The next production step is to mix them with an instrumental or use them as quality baselines for future SoulX renders.

## Reproducible Direction

Every new Musai creative project now writes:

```text
SOULX_REQUEST.md
commands.sh
```

Useful commands:

```bash
commands.sh soulx-demo-en
commands.sh soulx-demo-zh
PROMPT_WAV=/path/to/prompt.wav PROMPT_METADATA=/path/to/prompt.json TARGET_METADATA=/path/to/target.json commands.sh soulx-custom
commands.sh qa-soulx
```

## Quality Rule

Accept a SoulX render only if:

- the vocal is clearly sung, not spoken;
- the voice is audible and not buried;
- target-language words are intelligible;
- phrase rhythm follows the requested melody / 旋律 / score;
- prompt, metadata, model, command, output path, and QA note are saved.

