# Musia To LALACHAN MV Pipeline Contract

Date: 2026-06-28

This contract is for Codex, AgInTiFlow, Musia, and LALACHAN sessions that need to create music-led short films or MVs.

## Ownership

Musia owns:

- song idea expansion
- lyrics and translations
- melody/vocal/full-song generation
- audio review and correction
- stems, chords, beats, and analysis reports
- final soundtrack choice
- MV pack export

LALACHAN owns:

- Xiaoyunque/noVNC browser session
- reference-image selection and upload
- prompt submission
- generation watching and download
- video QA
- LazyEdit or publishing handoff when requested

## Pack Schema

Each Musia MV pack uses:

```text
data/mv_packs/<slug>/
  README.md
  PROMPT_XYQ.md
  MUSIA_LALACHAN_MV_HANDOFF.json
  replace_video_audio.sh
  audio/<slug>-15s.mp3
  references/*.png|*.jpg
```

`MUSIA_LALACHAN_MV_HANDOFF.json` has schema:

```text
art.lazying.musia.mv-pack.v1
```

Required fields:

- `title`
- `musician`
- `source_audio`
- `audio_reference`
- `mv_duration_seconds`
- `ratio`
- `target_platform`
- `cdp_url`
- `chrome_profile`
- `prompt`
- `references`
- `replace_audio_script`
- `quality_gates`

## Browser Defaults

Use the LALACHAN controlled browser:

```text
CDP URL: http://127.0.0.1:9222
Chrome profile: ~/.cache/xyq-chrome
Launch script: ../LALACHAN/scripts/xyq_chrome/launch_chrome.sh
Page helper: ../LALACHAN/scripts/xyq_cdp_browser.py
Watcher: ../LALACHAN/scripts/xyq_chrome/watch_thread_dom_download.py
```

Start:

```bash
cd ../LALACHAN
PORT=9222 PROFILE_DIR="$HOME/.cache/xyq-chrome" \
  scripts/xyq_chrome/launch_chrome.sh
```

Inspect:

```bash
scripts/xyq_cdp_browser.py list-pages
scripts/xyq_cdp_browser.py visible PAGE_ID
scripts/xyq_cdp_browser.py bring-to-front PAGE_ID
```

## Submission Rules

Use Xiaoyunque browser UI, not API, unless the user explicitly asks for API use.

Before submit, verify:

- mode is `沉浸式短片`
- duration is the requested duration, usually `15s`
- ratio is requested ratio, usually `4:3`
- prompt has no local filesystem paths
- all reference files are attached and visible
- audio reference is attached if the UI supports it
- user has authorized spending credits for the generation

Do not submit silently when credits may be charged.

## Four Buddies Reference Order

Preferred MV upload order:

```text
words-card.jpg
LazyingArtRobot.png
raraxia.jpeg
ayachan.png
sasakun.jpeg
Trio.png
```

Use the prompt labels:

- 图1: words card / learning prop
- 图2: Zhuangzi Robot, preserve the LazyingArt logo
- 图3: Rara Xia / 啦啦侠
- 图4: Aya Chan / 阿芽酱
- 图5: Sasa Kun / 飒飒君
- 图6: group identity reference

If the LALACHAN episode needs glasses, notebook, or other props, add those files after the identity references and update the prompt labels.

## Final Assembly

After Xiaoyunque returns a video:

1. Save the raw downloaded MP4 in LALACHAN outputs.
2. Run `ffprobe` to confirm duration, video stream, and audio stream.
3. If the soundtrack is not exact, run the pack `replace_video_audio.sh`.
4. Review the final video for timing, character consistency, and unwanted text.
5. Only then publish or add it to Fun Lazying Art.

## Feasibility Assessment

This pipeline is feasible today as an MV workflow. The highest-confidence route is:

```text
Musia creates exact audio -> Xiaoyunque creates visuals -> ffmpeg restores exact audio
```

The lower-confidence route is:

```text
Xiaoyunque uses uploaded audio as exact soundtrack
```

That may work in some UI modes, but must be verified per generation. Treat uploaded audio as a reference unless the returned video proves otherwise.

## Next Engineering Improvements

- Add explicit audio-file scoring to `../LALACHAN/scripts/xyq_cdp_browser.py` upload helpers.
- Add a LALACHAN watcher preset for MusiaVideo output folders.
- Add a Musia CLI command wrapper around `scripts/prepare_lalachan_mv_pack.py`.
- Add Fun Lazying Art `kind: mv` examples that link audio, video, lyrics, and prompt provenance.
