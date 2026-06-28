# Fun Player Redesign - 2026-06-28

This pass simplified `fun.lazying.art` into a bright default media page for songs, localized songs, MVs, short films, and future Musai/LALACHAN media.

Default visual media should use a 16:9 poster. Square album-cover assets may still be used for thumbnails or music-library compatibility, but the player hero and share image should prefer the 16:9 poster.

## Layout

- One media player on the left.
- The player stage uses a 16:9 poster/video frame by default.
- One lyric carousel on the right, showing all selected languages by default.
- Language buttons are multi-select toggles, so Chinese, Japanese, and English can be shown together or filtered.
- The bottom section shows the full lyrics line by line in all available languages.
- Chords are a single horizontal carousel at the top of the lyric card.
- Media selection lives in a collapsible left drawer opened by the header library button.
- Search is an icon-only header action and opens the drawer when active.

## Lyric Tracks

The `rain-day-bilingual-verse` demo now has three same-timing localized lyric tracks:

- English: `website/data/songs/rain-day-bilingual-verse/lyrics/en.json`
- Japanese with furigana: `website/data/songs/rain-day-bilingual-verse/lyrics/ja.json`
- Chinese with pinyin: `website/data/songs/rain-day-bilingual-verse/lyrics/zh-Hans.json`

These are singable adaptations written for the same four phrase windows, not literal line-by-line translations. The manifest timeline carries the canonical phrase ids; language-specific text, timing, ruby, and pinyin data live in each language JSON.

## Generated Media Assets

- 16:9 generated poster: `website/assets/covers/rain-day-trilingual-poster-16x9.png`
- Source generated image kept by Codex image generation: `/home/lachlan/.codex/generated_images/019f0842-25ba-7bd2-9d4b-0b1c60d8a951/ig_0a38f1ca1573c42e016a40bc8d5570819ba83a857fb2c01c07.png`
- SoulX run folder: `data/soulx_verses/rain-day-trilingual-zh-localized-20260628/`
- Website mix MP3: `website/assets/audio/rain-day-bilingual-verse.mp3`
- Website vocal MP3: `website/assets/audio/rain-day-bilingual-verse-vocal.mp3`
- Website melody guide MP3: `website/assets/audio/rain-day-trilingual-melody-guide.mp3`
- Generated lyric sheet: `data/soulx_verses/rain-day-trilingual-zh-localized-20260628/lyrics.md`

The current generated short-verse audio is a real Chinese SoulX vocal render plus melody guide using the Chinese localized lyric. English and Japanese are synced localized lyric tracks in the website data, but they are not yet separate re-sung vocal renders because the current local SoulX metadata builder supports Mandarin/English tokens and still needs a Japanese phoneme path.

The full-song catalog item, `rain-day-full-song-trilingual`, does have separate English, Chinese, and Japanese playable MP3s. Those are ACE-Step creative generation outputs, not strict same-music/stem localization renders.

## Validation

Local checks run after the redesign:

```bash
npm run website:validate
node --check website/app.js
google-chrome --headless=new --no-sandbox --disable-gpu --window-size=1440,1200 \
  --virtual-time-budget=2500 --screenshot=/tmp/fun-tidy-bright.png \
  --dump-dom http://127.0.0.1:8778/
```

The browser smoke check confirmed that the old bilingual text and duplicated pinyin strings were removed.
