# Fun Website Version Naming And Playback

Date: 2026-06-30

## Version Naming

Use concise public suffixes so listeners can tell which generation route they are hearing:

- Standard selected ACE/ACE-Step version: pure song name, no suffix.
- Older ACE/ACE-Step candidate: `ACE Legacy`.
- DiffRhythm variants: `DR Short`, `DR Full Lyrics`, or another compact `DR ...` suffix.
- Localization/SVC/model-transfer route: include the method, such as `SoulX Localization`.

For `云海之恋`, the public set is:

- `云海之恋`: standard ACE selected version.
- `云海之恋 · DR Short`: DiffRhythm short route.
- `云海之恋 · DR Full Lyrics`: DiffRhythm full-lyrics route.
- `云海之恋 · ACE Legacy`: earlier ACE candidate kept for comparison.

For `Take Care of Yourself`, the good ACE hope version is the plain public title. The earlier localization pipeline is labeled `Take Care of Yourself · SoulX Localization`.

Run the helper when the catalog needs the current naming pass:

```bash
PYTHONNOUSERSITE=1 conda run -n musia python scripts/apply_fun_version_naming.py
```

## Playback Modes

The Fun player supports:

- `Stop`: stop after the current media ends.
- `Cycle`: advance through songs/localized songs in catalog order.
- `Shuffle`: advance to a random different song/localized song.
- `Loop 1`: replay the current song.

The manifest may set:

```json
{
  "playback": {
    "defaultMode": "single",
    "reason": "Standard ACE-selected version should loop by default for listening and recording."
  }
}
```

Only selected standard ACE versions should get this default looping hint. Other variants should omit it unless the user explicitly asks.

The player hides playback mode controls in capture/recording mode so generated videos keep the clean player-and-lyrics layout.
