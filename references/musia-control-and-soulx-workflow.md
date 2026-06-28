# Musia Control Levels And SoulX Vocal Workflow

Musia should support several levels of creative control. The goal is not one model for everything; the goal is a router that chooses the right backend for the user’s material.

## Generation Modes

| Mode | User Input | Best First Route | Output |
| --- | --- | --- | --- |
| `free_vocal` | prompt, optional lyrics | DeepSeek/OpenAI/Codex prompt refinement -> SoulX | dry sung vocal / `human_sound` |
| `melody_generation` | idea, mood, rhythm/melody requirements | AI music brief -> notation/MIDI/metadata planning | melody/rhythm plan, then vocal or full song |
| `full_production` | idea, style, lyrics | AI prompt refinement -> ACE-Step/YuE-style model | full mixed song candidate |
| `controlled_song` | lyrics, chords, sheet, friend demo, reference recording | analyze/reference extraction -> controlled prompt/metadata | controlled song or vocal render |
| `localization` | rights-confirmed source song + target language | stems/lyrics/beats/chords -> singable adaptation -> SoulX/YingMusic -> mix | localized version |

## Control Levels

| Level | Meaning |
| --- | --- |
| `free` | Musia may invent lyrics, melody, harmony, arrangement, and vocal direction. |
| `lyrics` | Preserve or lightly polish supplied lyrics; create the music around them. |
| `lyrics_chords` | Preserve lyric intent and chord/harmony notes. |
| `melody_sheet` | Preserve supplied melody, 旋律, sheet music, jianpu, MIDI notes, phrase rhythm, or hook contour. |
| `reference_audio` | Analyze and follow a supplied recording, rough demo, friend vocal, or track reference. |
| `strict_localization` | Preserve source-song melody/rhythm/arrangement as much as possible while adapting lyrics into the target language. |

## Why SoulX Matters

The local runs:

```text
data/runs/soulx-wrapper-demo-en/generated.wav
data/runs/soulx-wrapper-demo-zh/generated.wav
data/runs/soulx-demo-zh/generated.wav
```

are short dry vocal outputs. They are useful because they are mainly human-sounding singing voice, not a full instrumental mix. This makes SoulX the current best local path for:

- vocal-only generation;
- target-language vocal rendering;
- later mixing with an instrumental;
- high-control experiments where lyrics, note durations, pitch, and phrase timing matter.

## SoulX Requirements

SoulX quality depends on metadata:

```text
prompt_wav
prompt_metadata.json
target_metadata.json
control = score or melody
```

Good metadata contains:

- text tokens;
- phonemes;
- note durations;
- note pitches;
- note types;
- F0 contour.

For Chinese lyric editing, character count must match sung tokens unless the preprocessing/alignment step is rerun. This is why Musia should save a `SOULX_REQUEST.md` for every controlled project instead of only saving `generated.wav`.

## Routing Policy

Use:

- SoulX for clean vocal / `human_sound`;
- ACE-Step or similar full-song models for complete arrangements;
- Demucs/WhisperX/RMVPE/Basic Pitch for source-song analysis;
- DeepSeek/OpenAI/Codex 5.5 xhigh/AgInTi workers for prompt refinement, lyric adaptation, metadata planning, and QA.

## Safety And Rights

Artist names should be treated as style references, not voice impersonation requests. Voice/timbre cloning requires explicit consent. Song localization requires rights confirmation before public release or commercial use.

