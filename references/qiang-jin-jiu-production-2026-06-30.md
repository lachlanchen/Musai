# 将进酒 ACE Production Note

Date: 2026-06-30

## Goal

Create a female Mandarin ACE-Step poetry-song from Li Bai's original 《将进酒》:

- lyrics must use the original poem text as the lyric source;
- vocal feeling: 豪气干云, 优美动人, 侠骨柔肠, 百转千回;
- pronunciation must protect `将进酒` as `qiāng jìn jiǔ`;
- output must be prepared for Fun Lazying Art with pinyin, furigana, translations, timing, chords, and public audio.

## Source And Pronunciation

Local source checked:

- `/home/lachlan/ProjectsLFS/ZhJpBook/sources/tangshi-sanbai/zh-wikisource-tangshi-sanbai/raw/0080-將進酒 (李白).wiki`

Reference pages checked:

- `https://zh.wikisource.org/zh-hant/將進酒_(李白)`
- `https://m.cngwzj.com/pygushi/TangDai/12843/`
- `https://www.shicile.com/detail/9110299361174`

The user-requested simplified version with `杯莫停` and `但愿长醉不愿醒` was used. The local ZhJpBook pinyin build reads the title `将` as `jiāng`, so Musia overrides the title phrase to `qiāng jìn jiǔ`.

Pronunciation guide:

- `data/creative_projects/qiang-jin-jiu-20260630/source/pronunciation-guide.md`

## Generation

Project:

- `data/creative_projects/qiang-jin-jiu-20260630/`

ACE route:

- model: `ACE-Step 1.5 XL Turbo`
- selected seed: `732002`
- selected WAV: `data/creative_projects/qiang-jin-jiu-20260630/ace_outputs/zh_corrected_20260701-000444/d9fba6aa-69e6-040c-765d-cb781f2d901b.wav`
- selected MP3: `data/creative_projects/qiang-jin-jiu-20260630/selected/qiang-jin-jiu-zh-Hans-ace-20260701.mp3`

Three candidates were generated and reviewed. The selected candidate passed the local quality gate and had the best ASR overlap among the candidates.

Review report:

- `data/creative_projects/qiang-jin-jiu-20260630/reviews/20260701-000551/SONG_REVIEW.md`

Analysis run:

- `data/runs/qiang-jin-jiu-20260630-20260701-000551-analysis/`

Key artifacts:

- stems: `data/runs/qiang-jin-jiu-20260630-20260701-000551-analysis/stems/`
- chords: `data/runs/qiang-jin-jiu-20260630-20260701-000551-analysis/analysis/chords.csv`
- beats: `data/runs/qiang-jin-jiu-20260630-20260701-000551-analysis/analysis/beats.csv`
- ASR: `data/runs/qiang-jin-jiu-20260630-20260701-000551-analysis/analysis/lyrics.json`

## Post-Correction

ACE did not perform a perfect literal recital of every classical line. The website item therefore uses the standard Musia post-correction policy:

- keep the original poem wording where the sound is close enough;
- use ASR/listening to identify real timing and repeated sections;
- reflect repeated sung sections in the lyric timeline;
- keep pronunciation metadata visible for high-risk Mandarin characters.

The selected render repeats:

- `钟鼓馔玉不足贵 / 但愿长醉不愿醒`
- `古来圣贤皆寂寞 / 惟有饮者留其名 / 陈王昔时宴平乐 / 斗酒十千恣欢谑`

Reproducible website-prep script:

- `scripts/prepare_qiang_jin_jiu_fun_item.py`

## Deep Lyric Correction 2026-07-01

The public lyric data was corrected again after publication because the first
website pass was too optimistic about line timing. The correction used:

- large-v3 ASR on the selected mix and separated vocal stem;
- medium/small ASR as cross-checks;
- the original poem as the intended lyric reference;
- the Musia evidence rule: real sung structure first, then sound-close intended
  classical text, then ASR guesses.

Evidence packets:

- `data/creative_projects/qiang-jin-jiu-20260630/corrections/deep-large-20260701/CORRECTION_PACKET.md`
- `data/creative_projects/qiang-jin-jiu-20260630/corrections/deep-20260701/CORRECTION_PACKET.md`

Main correction decisions:

- split `君不见高堂 / 明镜悲白发` instead of showing one long merged line;
- split `烹羊宰牛且为乐 / 会须一饮三百杯`;
- split `与君歌一曲 / 请君为我倾耳听`;
- retimed the repeated `钟鼓馔玉不足贵 / 但愿长醉不愿醒` section from
  the large-v3 vocal-stem pass;
- retimed the repeated `古来圣贤皆寂寞 / 惟有饮者留其名 / 陈王昔时宴平乐 /
  斗酒十千恣欢谑` section;
- fixed Mandarin pinyin for polyphonic or context-sensitive words:
  `将进酒 = qiang1 jin4 jiu3`, `朝 = zhao1`, `白发 = bai2 fa4`,
  `且为乐 = qie3 wei2 le4`, `请君为我 = qing3 jun1 wei4 wo3`,
  `斗酒 = dou3 jiu3`, and `平乐 = ping2 le4`.

The active Chinese track now has 32 timed lyric lines.

## Website Item

Fun media id:

- `qiang-jin-jiu`

Website data:

- `website/data/songs/qiang-jin-jiu/manifest.json`
- `website/data/songs/qiang-jin-jiu/lyrics/zh-vocal/zh-Hans.json`
- `website/data/songs/qiang-jin-jiu/lyrics/zh-vocal/en.json`
- `website/data/songs/qiang-jin-jiu/lyrics/zh-vocal/ja.json`

Cover:

- `website/assets/covers/qiang-jin-jiu-16x9.png`

Public audio mirror:

- `/home/lachlan/ProjectsLFS/MusiaSongs/audio/qiang-jin-jiu-zh-Hans-ace-20260701.mp3`
- `https://lazyingart.github.io/MusiaSongs/audio/qiang-jin-jiu-zh-Hans-ace-20260701.mp3`

Website URL after publish:

- `https://fun.lazying.art/#qiang-jin-jiu`

## Validation

Commands:

```bash
npm run website:validate
node bin/musia.js fun-audit --media-id qiang-jin-jiu
node --check website/app.js
git diff --check -- scripts/prepare_qiang_jin_jiu_fun_item.py website/data/catalog.json website/data/songs/qiang-jin-jiu
```

Current result:

- website schema validation passed;
- media item audit passed;
- JavaScript syntax check passed;
- whitespace check passed.
