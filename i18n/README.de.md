[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)

[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# Musai

*KI-Songlokalisierung: menschliche Stimme, Stems, Lyrics, Beats und Akkorde aus einem Song extrahieren und den Weg zu singbarem mehrsprachigem Re-Singing vorbereiten.*

[![Website](https://img.shields.io/badge/Website-lazying.art-0EA5E9?style=for-the-badge)](https://lazying.art)
[![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python&logoColor=white)](../environment.yml)
[![CUDA](https://img.shields.io/badge/CUDA-tested-76B900?style=for-the-badge&logo=nvidia&logoColor=white)](../references/local-setup-and-test-report.md)
[![Sponsor](https://img.shields.io/badge/Sponsor-lachlanchen-EA4AAA?style=for-the-badge&logo=githubsponsors&logoColor=white)](https://github.com/sponsors/lachlanchen)

Musai ist ein lokales Forschungsprototyp für KI-Musiklokalisierung. Das aktuelle MVP nimmt einen Song, trennt ihn in die vier Demucs-Stems `bass`, `drums`, `vocals` und `other`, erstellt einen `instrumental`-Mix, benennt die Stimme zusätzlich als `human_sound`, transkribiert Lyrics, schätzt Beats und erzeugt Chordify-artige Akkordsegmente.

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://img.shields.io/badge/Donate-LazyingArt-0EA5E9?style=for-the-badge&logo=kofi&logoColor=white)](https://chat.lazying.art/donate) | [![PayPal](https://img.shields.io/badge/PayPal-RongzhouChen-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/RongzhouChen) | [![Stripe](https://img.shields.io/badge/Stripe-Donate-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

## Ausgabe

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

`instrumental.wav` wird aus `bass + drums + other` gemischt. `human_sound.wav` ist der isolierte Vocal-Stem `vocals.wav`.

## Aktueller Inhalt

| Path | Purpose |
| --- | --- |
| [`musai/`](../musai/) | Lokales Python-Analysepaket. |
| [`scripts/bootstrap_musai.sh`](../scripts/bootstrap_musai.sh) | Erstellt die conda-Umgebung und installiert den lokalen Stack. |
| [`scripts/download_open_songs.py`](../scripts/download_open_songs.py) | Lädt freie/offene Testsongs herunter. |
| [`scripts/run_pipeline.py`](../scripts/run_pipeline.py) | Führt Separation, Transkription, Beats, Akkorde und Bericht aus. |
| [`scripts/install_research_repos.sh`](../scripts/install_research_repos.sh) | Klont optionale Forschungsrepos flach nach `third_party/`. |
| [`scripts/musai_lyricfit_openai.py`](../scripts/musai_lyricfit_openai.py) | Optionaler OpenAI-Helfer für Lyrics-Anpassung. |
| [`references/`](../references/) | Architektur, Tiefenrecherche und lokale Setup-Notizen. |
| [`TODO.md`](../TODO.md) | Build-Checkliste und nächste technische Schritte. |

## Schnellstart

```bash
bash scripts/bootstrap_musai.sh
PYTHONNOUSERSITE=1 conda run -n musai python scripts/download_open_songs.py --id danny-boy-1917
PYTHONNOUSERSITE=1 conda run -n musai python scripts/run_pipeline.py data/open_songs/danny-boy-1917/original.ogg --run-name smoke-danny --max-duration 45 --asr-model tiny
```

Ergebnisse werden hier geschrieben:

```text
data/runs/<run-name>/
```

Generiertes Audio, heruntergeladene Songs, Modellgewichte und Drittanbieter-Klone werden von git ignoriert.

## Lokale Validierung

Der lokale Smoke-Test mit einer offenen Aufnahme von Wikimedia Commons lief auf einer NVIDIA RTX 4090 D erfolgreich:

```bash
PYTHONNOUSERSITE=1 conda run -n musai python scripts/run_pipeline.py data/open_songs/danny-boy-1917/original.ogg --run-name smoke-danny-120-fixed --max-duration 120 --asr-model base.en --language en --demucs-device cuda
```

Ergebnis:

- Vier Stems: `bass`, `drums`, `vocals`, `other`
- Zusätzliches Audio: `instrumental`, `human_sound`
- Tempo-Schätzung: `129.20 BPM`
- Beats: `257`
- Akkordsegmente: `132`
- Lyrics-Status: `ok`

Siehe [`references/local-setup-and-test-report.md`](../references/local-setup-and-test-report.md).

## Architektur

Musai ist nicht nur Übersetzung plus TTS. Die geplante vollständige Pipeline ist:

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

Dieses Repository implementiert die erste lokale Analyseschicht. Singing-Synthesis mit YingMusic-Singer-Plus, SoulX-Singer und verwandten Modellen bleibt eine Forschungsintegration, weil große Gewichte, Lizenzprüfungen und separate GPU-Worker nötig sind.

## Zitieren

Wenn du Musai in Forschung nutzt, zitiere dieses Repository. GitHub liest [`CITATION.cff`](../CITATION.cff) und zeigt **Cite this repository** auf der Repository-Seite an.

```bibtex
@software{chen_musai_2026,
  author = {Chen, Lachlan},
  title = {Musai: Local-first AI song localization and music analysis},
  year = {2026},
  url = {https://github.com/lachlanchen/Musai}
}
```

## Status

Musai ist frühe Forschungssoftware. Die lokale Pipeline funktioniert für Tests und Artefakte, aber der Akkorddetektor ist eine leichte Basislinie und die singbare Re-Singing-Schicht ist noch nicht produktionsreif. Nutze eigene Songs, Public-Domain-Material, lizenzierte Songs oder von Creators hochgeladene Inhalte.

