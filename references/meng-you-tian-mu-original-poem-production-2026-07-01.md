# Meng You Tian Mu Original Poem Production

Date: 2026-07-01

Goal: generate a `梦游天姥吟留别` yuanshiban item that treats Li Bai's original poem as the lyrics, then audit the generated vocal with ASR before publishing website data.

## Source

- Project: `data/creative_projects/meng-you-tian-mu-original-poem-20260701/`
- Original poem: `data/creative_projects/meng-you-tian-mu-original-poem-20260701/source/source-poem.md`
- Pronunciation guide: `data/creative_projects/meng-you-tian-mu-original-poem-20260701/source/pronunciation-guide.md`
- Website item: `website/data/songs/meng-you-tian-mu-original-poem/`

Pronunciation notes were supplied to the generation prompt for classical readings such as `天姥`, `剡溪`, `脚著`, `殷岩泉`, `澹澹`, `列缺`, `訇然`, `惟觉时`, `须行即骑`, and `安能摧眉折腰`.

## Generation Route

ACE-Step was used in normal full-song mode, with the poem split into short phrase lines and no English section labels in the final selected route. This avoided the earlier recitation/demo behavior and made the model treat the poem as song lyrics.

Candidate summary:

| Candidate | Route | Result |
| --- | --- | --- |
| seeds `733101`, `733102` | XL turbo, sectioned labels, 260s | Rejected. ASR overlap was effectively zero and one candidate hallucinated end-credit style text. |
| seeds `733103`, `733104` | Turbo, no labels, 260s | Rejected as final. Seed `733103` was usable but incomplete; seed `733104` had weak lyric recovery. |
| seed `733105` | Turbo, no labels, 330s | Selected. Best balance of song quality, continuity, and poem recovery. |
| seed `733106` | Turbo, no labels, 330s | Rejected. Less complete lyric recovery than `733105`. |
| seed `733107` | Base guided, 330s | Rejected. Collapsed into non-lyric output. |

Selected generated WAV:

`data/creative_projects/meng-you-tian-mu-original-poem-20260701/ace_outputs/zh_turbo_long/cf268363-30b5-16ec-32be-0c01f29da578.wav`

The selected render contained unwanted generated end-credit text after the song ending, so the public version was trimmed to 296 seconds:

`data/creative_projects/meng-you-tian-mu-original-poem-20260701/selected/meng-you-tian-mu-original-poem-zh-Hans-ace-20260701-trimmed.wav`

## Audit And Correction

Analysis run:

`data/runs/meng-you-tian-mu-original-poem-20260701-selected-trimmed-analysis/`

Correction packet:

`data/creative_projects/meng-you-tian-mu-original-poem-20260701/correction_packets/selected-trimmed-large-v3/CORRECTION_PACKET.md`

The lyric JSON was corrected by cross-checking:

- the original poem text;
- full-mix Whisper large-v3 ASR;
- vocal-stem Whisper large-v3 ASR;
- the actual repeated or omitted sections in the generated audio.

Where the audio was close to the poem, the original poem wording was preserved. Where the model skipped lines or repeated later dream-palace/freedom sections, the website timing follows the audio instead of pretending the full source poem was sung exactly.

Quality caveat: this is the best selected original-poem candidate and is song-like, beautiful, and usable, but it is not a perfect classical diction master. The dense opening and some rare-word phrases are blurred. The adapted normal-song route remains cleaner when exact word intelligibility is more important than preserving the original poem verbatim.

## Website Data

Packager:

`scripts/prepare_meng_you_tian_mu_original_poem_fun_item.py`

Generated files:

- `website/data/songs/meng-you-tian-mu-original-poem/manifest.json`
- `website/data/songs/meng-you-tian-mu-original-poem/lyrics/zh-vocal/zh-Hans.json`
- `website/data/songs/meng-you-tian-mu-original-poem/lyrics/zh-vocal/en.json`
- `website/data/songs/meng-you-tian-mu-original-poem/lyrics/zh-vocal/ja.json`
- `website/data/catalog.json`

Public audio repo artifact:

`../MusiaSongs/audio/meng-you-tian-mu-original-poem-zh-Hans-ace-20260701.mp3`

Expected public URLs:

- `https://fun.lazying.art/#meng-you-tian-mu-original-poem`
- `https://lazyingart.github.io/MusiaSongs/audio/meng-you-tian-mu-original-poem-zh-Hans-ace-20260701.mp3`

Validation commands:

```bash
npm run website:validate
node --check website/app.js
node bin/musia.js fun-audit --media-id meng-you-tian-mu-original-poem
```

All passed after adding a manual Japanese furigana override for `剡`.
