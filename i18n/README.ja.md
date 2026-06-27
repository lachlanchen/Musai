[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)

[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# Musai

*AI 楽曲ローカライズ：楽曲から人声、ステム、歌詞、ビート、コードを抽出し、歌える多言語リシングへの道を作る。*

[![Website](https://img.shields.io/badge/Website-lazying.art-0EA5E9?style=for-the-badge)](https://lazying.art)
[![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python&logoColor=white)](../environment.yml)
[![CUDA](https://img.shields.io/badge/CUDA-tested-76B900?style=for-the-badge&logo=nvidia&logoColor=white)](../references/local-setup-and-test-report.md)
[![Sponsor](https://img.shields.io/badge/Sponsor-lachlanchen-EA4AAA?style=for-the-badge&logo=githubsponsors&logoColor=white)](https://github.com/sponsors/lachlanchen)

Musai はローカル優先の AI 音楽ローカライズ研究プロトタイプです。現在の MVP は入力曲を受け取り、Demucs の 4 ステム `bass`、`drums`、`vocals`、`other` に分離し、`instrumental` ミックスを作り、ボーカルを `human_sound` として別名保存し、歌詞転写、ビート推定、Chordify 風のコード区間を生成します。

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://img.shields.io/badge/Donate-LazyingArt-0EA5E9?style=for-the-badge&logo=kofi&logoColor=white)](https://chat.lazying.art/donate) | [![PayPal](https://img.shields.io/badge/PayPal-RongzhouChen-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/RongzhouChen) | [![Stripe](https://img.shields.io/badge/Stripe-Donate-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

## 出力

```text
input song
-> source/input.wav
-> stems/bass.wav
-> stems/drums.wav
-> stems/vocals.wav
-> stems/other.wav
-> stems/instrumental.wav
-> stems/human_sound.wav
-> analysis/lyrics.json + lyrics.txt
-> analysis/beats.json + beats.csv
-> analysis/chords.json + chords.csv
-> manifest.json + REPORT.md
```

`instrumental.wav` は `bass + drums + other` からミックスされます。`human_sound.wav` は分離されたボーカルステム `vocals.wav` です。

## 現在の内容

| Path | Purpose |
| --- | --- |
| [`musai/`](../musai/) | ローカル Python 解析ツールキット。 |
| [`scripts/bootstrap_musai.sh`](../scripts/bootstrap_musai.sh) | conda 環境を作成し、ローカルスタックをインストールします。 |
| [`scripts/download_open_songs.py`](../scripts/download_open_songs.py) | 自由/オープンなテスト曲をダウンロードします。 |
| [`scripts/run_pipeline.py`](../scripts/run_pipeline.py) | 分離、転写、ビート、コード、レポート生成を実行します。 |
| [`scripts/install_research_repos.sh`](../scripts/install_research_repos.sh) | 任意の研究リポジトリを `third_party/` に shallow clone します。 |
| [`scripts/musai_lyricfit_openai.py`](../scripts/musai_lyricfit_openai.py) | OpenAI を使った任意の歌詞適応ヘルパー。 |
| [`references/`](../references/) | アーキテクチャ、深掘り調査、ローカルセットアップ記録。 |
| [`TODO.md`](../TODO.md) | ビルドチェックリストと次の実装ステップ。 |

## クイックスタート

```bash
bash scripts/bootstrap_musai.sh
PYTHONNOUSERSITE=1 conda run -n musai python scripts/download_open_songs.py --id danny-boy-1917
PYTHONNOUSERSITE=1 conda run -n musai python scripts/run_pipeline.py data/open_songs/danny-boy-1917/original.ogg --run-name smoke-danny --max-duration 45 --asr-model tiny
```

結果は次に書き込まれます：

```text
data/runs/<run-name>/
```

生成音声、ダウンロード曲、モデル重み、第三者リポジトリのクローンは git から除外されます。

## ローカル検証

NVIDIA RTX 4090 D 搭載マシンで、Wikimedia Commons のオープン録音を使ったローカル smoke test に成功しました：

```bash
PYTHONNOUSERSITE=1 conda run -n musai python scripts/run_pipeline.py data/open_songs/danny-boy-1917/original.ogg --run-name smoke-danny-120-fixed --max-duration 120 --asr-model base.en --language en --demucs-device cuda
```

記録された結果：

- 4 ステム：`bass`、`drums`、`vocals`、`other`
- 追加音声：`instrumental`、`human_sound`
- テンポ推定：`129.20 BPM`
- ビート数：`257`
- コード区間：`132`
- 歌詞状態：`ok`

詳細は [`references/local-setup-and-test-report.md`](../references/local-setup-and-test-report.md)。

## アーキテクチャ方針

Musai は単なる翻訳 + TTS ではありません。目標となる完全な流れは：

```text
song upload
-> rights / ownership check
-> vocal + instrumental separation
-> lyrics transcription
-> word / phoneme timing
-> melody / pitch extraction
-> singable lyric adaptation
-> AI singing synthesis
-> optional voice/timbre conversion
-> mixing + mastering
-> music-player interface
```

このリポジトリは最初のローカル解析層を実装しています。YingMusic-Singer-Plus、SoulX-Singer などによる歌唱合成は、大きな重み、ライセンス確認、独立した GPU worker が必要なため研究統合として扱います。

## 引用

研究で Musai を使う場合は、このリポジトリを引用してください。GitHub は [`CITATION.cff`](../CITATION.cff) を読み取り、リポジトリページに **Cite this repository** を表示します。

```bibtex
@software{chen_musai_2026,
  author = {Chen, Lachlan},
  title = {Musai: Local-first AI song localization and music analysis},
  year = {2026},
  url = {https://github.com/lachlanchen/Musai}
}
```

## 状態

Musai は初期段階の研究ソフトウェアです。ローカルパイプラインはテストと成果物生成に使えますが、コード検出器は軽量ベースラインであり、歌えるリシング層はまだ本番品質ではありません。自分が権利を持つ曲、パブリックドメイン、ライセンス済み、または制作者がアップロードした素材を使ってください。

