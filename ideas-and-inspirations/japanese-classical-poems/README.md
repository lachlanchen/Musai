# Japanese Classical Poem Song Inspirations

This note collects highly musical Japanese classical poems for future Musia
song generation. Treat these as inspiration briefs, not finished production
packages. Before generation, verify pronunciation again, create a Japanese
reading guide, and run post-generation ASR/listening correction before website
publication.

## Best Man'yoshu Candidate

Recommended poem:

```text
東の野に
かぎろひの立つ見えて
かへり見すれば
月傾きぬ
```

Source:

```text
万葉集 巻1-48
柿本人麻呂
https://manyo-hyakka.pref.nara.jp/db/detailLink?cls=db_manyo&pkey=48
```

Reading:

```text
ひむがしの のに
かぎろひの たつみえて
かへりみすれば
つき かたぶきぬ
```

Romaji:

```text
Himugashi no no ni
kagirohi no tatsu miete
kaerimisureba
tsuki katabukinu
```

Working English sense:

```text
Across the eastern fields,
the first fire of dawn begins to rise.
I turn and look back:
the moon is sinking low.
```

Why it is strong for Musia:

- sunrise and moonset happen in one cinematic breath;
- the image is vast but quiet;
- it has a natural visual arc for a song or MV;
- `かぎろひ` is a beautiful but risky pronunciation word, so prepare a
  phonetic guide before generation.

Producer direction:

```text
Ancient Japanese dawn art song, vast eastern field, moon fading behind the
singer, first red glow of sunrise, quiet awe, female or androgynous clear vocal,
shakuhachi, koto, low strings, soft taiko pulse, spacious reverb, 68-76 BPM,
cinematic but restrained.
```

## Best Kokin Wakashu Candidate

Recommended poem:

```text
ひさかたの
光のどけき
春の日に
しづ心なく
花の散るらむ
```

Source:

```text
古今和歌集 春下 84
紀友則
Also Hyakunin Isshu 33
https://ogurasansou.jp.net/columns/hyakunin/2017/10/17/1177/
https://www.karuta.or.jp/karuta-everyday/2807/
```

Reading:

```text
ひさかたの
ひかりのどけき
はるのひに
しづごころなく
はなのちるらむ
```

Romaji:

```text
Hisakata no
hikari nodokeki
haru no hi ni
shizugokoro naku
hana no chiruramu
```

Working English sense:

```text
On this spring day,
so gentle with quiet light,
why do the blossoms
scatter with no still heart?
```

Why it is strong for Musia:

- it has a perfect emotional contrast: calm spring light versus restless falling
  blossoms;
- the sound is soft and singable, with repeated `hi/ha/no` vowel colors;
- it can become a short, beautiful 70-90 second song without needing heavy
  modern rewriting;
- it expresses mono no aware clearly enough for listeners who do not know the
  source.

Producer direction:

```text
Elegant Heian spring art-pop song, gentle sunlight, falling sakura, quiet
sadness under a bright sky, clear Japanese female vocal, koto, piano, soft
strings, brushed percussion, airy reverb, 72-82 BPM, beautiful and fragile,
not dramatic, leave space between phrases.
```

## Other Kokin Wakashu Candidates

Use these when the song needs a different emotional color:

```text
人はいさ
心も知らず
ふるさとは
花ぞ昔の
香ににほひける
```

Source:

```text
古今集 春 42
紀貫之
https://ogurasansou.jp.net/columns/hyakunin/2017/10/17/1182/
```

Best for: memory, old places, unchanged flower scent, bittersweet return.

```text
ちはやぶる
神代もきかず
竜田川
からくれなゐに
水くくるとは
```

Source:

```text
古今集 秋 294
在原業平朝臣
https://ogurasansou.jp.net/columns/hyakunin/2017/10/17/1039/
```

Best for: vivid autumn, red water, dramatic color, stronger visual MV.

## Musia Generation Rule

For Japanese classical poems:

```text
1. Verify source text and poem number.
2. Prepare kana reading and romaji guide.
3. Mark risky old words before generation.
4. If the poem is short, repeat the strongest line or couplet as a hook.
5. Preserve source text when sound and phrase length are close.
6. Use ASR only as evidence; do not let ASR replace beautiful original wording
   with a weaker nearby guess.
7. After generation, correct website JSON from listening + ASR + source text.
```

For the Kokinshū poem above, a first generation layout can be:

```text
[Verse]
ひさかたの
光のどけき
春の日に

[Hook]
しづ心なく
花の散るらむ

[Verse]
ひさかたの
光のどけき
春の日に

[Final Hook]
しづ心なく
花の散るらむ
花の散るらむ
```

This keeps the original poem text while giving the model enough musical form.
