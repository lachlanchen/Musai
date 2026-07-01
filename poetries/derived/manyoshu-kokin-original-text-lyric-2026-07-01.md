# 万葉集 x 古今和歌集 Original-Text Lyric Draft - 2026-07-01

This is a Musia song-lyric arrangement built only from original Japanese
classical poem text. The creative change is selection, ordering, phrase
splitting, and repetition. Do not add modern Japanese lyrics inside the sung
text unless making a separate adapted version.

Orthography note: the local Wikisource raw text often omits dakuten and uses
fully kana historical spelling, such as `しつ` / `しらす` / `花そ`. This draft
uses a readable singing orthography with kanji and expected voicing, while
preserving original poem wording. Use the raw Wikisource form if a strict
diplomatic text is required.

## Working Title

```text
かぎろひと花
```

## Source Lines Used

### 万葉集

```text
東の野にかぎろひの立つ見えてかへり見すれば月かたぶきぬ
```

```text
あかねさす紫野行き標野行き野守は見ずや君が袖振る
```

```text
君待つと我が恋ひをれば我が宿の簾動かし秋の風吹く
```

```text
春過ぎて夏来るらし白栲の衣干したり天の香具山
```

### 古今和歌集

```text
久方のひかりのどけき春の日にしつ心なく花のちるらむ
```

```text
花の色はうつりにけりないたつらにわか身世にふるなかめせしまに
```

```text
人はいさ心も知らずふるさとは花ぞ昔の香ににほひける
```

## Sung Lyric Arrangement

```text
[Intro]
東の野に
かぎろひの立つ見えて
かへり見すれば
月かたぶきぬ

[Verse 1]
あかねさす
紫野行き
標野行き
野守は見ずや
君が袖振る

[Pre-Chorus]
君待つと
我が恋ひをれば
我が宿の
簾動かし
秋の風吹く

[Chorus]
久方の
ひかりのどけき
春の日に
しつ心なく
花のちるらむ

[Verse 2]
春過ぎて
夏来るらし
白栲の
衣干したり
天の香具山

[Bridge]
花の色は
うつりにけりな
いたつらに
わか身世にふる
なかめせしまに

[Final Chorus]
久方の
ひかりのどけき
春の日に
しつ心なく
花のちるらむ

[Outro]
人はいさ
心も知らず
ふるさとは
花ぞ昔の
香ににほひける

花のちるらむ
花のちるらむ
```

## Chinese Meaning

```text
[前奏]
东方的原野上，
晨曦的光焰已经升起；
回首望去，
月亮正渐渐西沉。

[第一段]
在茜色光辉中，
走过紫草之野，
走过禁苑的原野；
守野的人没有看见吗？
你正挥动衣袖。

[预副歌]
我等待着你，
独自恋慕着你时；
我家门前的帘子微微动了，
原来是秋风吹来。

[副歌]
在这悠远明净的
春日光中，
为何花却不能安静，
纷纷散落呢？

[第二段]
春天已经过去，
夏天似乎已经到来；
洁白的衣裳晾晒着，
在天香具山上。

[桥段]
花的颜色已经凋谢褪去；
我也在徒然的时光里，
因长久凝望、因人世流转，
渐渐老去。

[最终副歌]
在这悠远明净的
春日光中，
为何花却不能安静，
纷纷散落呢？

[尾声]
人心如何，我不知道；
可是旧乡的花，
仍像从前一样，
散发着熟悉的香气。

花仍在飘落。
花仍在飘落。
```

## Production Notes

- Keep `久方の / ひかりのどけき / 春の日に / しつ心なく / 花のちるらむ`
  as the main hook. It is the most immediately singable phrase.
- For generation, provide the model a kana/romaji guide before audio synthesis.
  Risky readings include `かぎろひ`, `標野`, `我が恋ひをれば`, `白栲`,
  `天の香具山`, and historical no-dakuten spellings such as `しつ`, `わか`,
  `なかめ`.
- If the model garbles `しつ心なく`, accept a public subtitle spelling of
  `しづ心なく` only when the audio clearly sings `shizu`; otherwise preserve
  the local source text above.
- If this becomes a public Fun Lazying Art item, run independent ASR/listening
  correction before website JSON and subtitles.
