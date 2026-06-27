[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)

[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# Musai

*توطين الأغاني بالذكاء الاصطناعي: استخراج الصوت البشري، والمسارات، والكلمات، والإيقاعات، والأوتار من أغنية، ثم تمهيد الطريق لإعادة غناء متعددة اللغات قابلة للغناء.*

[![Website](https://img.shields.io/badge/Website-lazying.art-0EA5E9?style=for-the-badge)](https://lazying.art)
[![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python&logoColor=white)](../environment.yml)
[![CUDA](https://img.shields.io/badge/CUDA-tested-76B900?style=for-the-badge&logo=nvidia&logoColor=white)](../references/local-setup-and-test-report.md)
[![Sponsor](https://img.shields.io/badge/Sponsor-lachlanchen-EA4AAA?style=for-the-badge&logo=githubsponsors&logoColor=white)](https://github.com/sponsors/lachlanchen)

Musai هو نموذج بحثي محلي أولا لتوطين الموسيقى بالذكاء الاصطناعي. يأخذ MVP الحالي أغنية إدخال، ويفصلها إلى مسارات Demucs الأربعة `bass` و`drums` و`vocals` و`other`، وينشئ مزيج `instrumental`، ويحفظ الصوت البشري باسم `human_sound`، ثم يستخرج الكلمات والإيقاعات ومقاطع الأوتار بأسلوب Chordify.

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://img.shields.io/badge/Donate-LazyingArt-0EA5E9?style=for-the-badge&logo=kofi&logoColor=white)](https://chat.lazying.art/donate) | [![PayPal](https://img.shields.io/badge/PayPal-RongzhouChen-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/RongzhouChen) | [![Stripe](https://img.shields.io/badge/Stripe-Donate-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

## المخرجات

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

يتم مزج `instrumental.wav` من `bass + drums + other`. أما `human_sound.wav` فهو مسار الصوت البشري المعزول `vocals.wav`.

## المحتوى الحالي

| Path | Purpose |
| --- | --- |
| [`musai/`](../musai/) | أدوات تحليل Python محلية. |
| [`scripts/bootstrap_musai.sh`](../scripts/bootstrap_musai.sh) | ينشئ بيئة conda ويثبت الحزمة المحلية. |
| [`scripts/download_open_songs.py`](../scripts/download_open_songs.py) | ينزل أغاني اختبار مجانية/مفتوحة. |
| [`scripts/run_pipeline.py`](../scripts/run_pipeline.py) | يشغل الفصل، والنسخ، والإيقاعات، والأوتار، والتقرير. |
| [`scripts/install_research_repos.sh`](../scripts/install_research_repos.sh) | يستنسخ مستودعات البحث الاختيارية إلى `third_party/`. |
| [`scripts/musai_lyricfit_openai.py`](../scripts/musai_lyricfit_openai.py) | مساعد اختياري لتكييف الكلمات باستخدام OpenAI. |
| [`references/`](../references/) | المعمارية، والبحث العميق، وملاحظات الإعداد المحلي. |
| [`TODO.md`](../TODO.md) | قائمة البناء والخطوات الهندسية التالية. |

## البداية السريعة

```bash
bash scripts/bootstrap_musai.sh
PYTHONNOUSERSITE=1 conda run -n musai python scripts/download_open_songs.py --id danny-boy-1917
PYTHONNOUSERSITE=1 conda run -n musai python scripts/run_pipeline.py data/open_songs/danny-boy-1917/original.ogg --run-name smoke-danny --max-duration 45 --asr-model tiny
```

تكتب النتائج إلى:

```text
data/runs/<run-name>/
```

يتجاهل git الصوت المولد، والأغاني المنزلة، وأوزان النماذج، ومستودعات الطرف الثالث.

## التحقق المحلي

نجح اختبار محلي على تسجيل مفتوح من Wikimedia Commons على جهاز NVIDIA RTX 4090 D:

```bash
PYTHONNOUSERSITE=1 conda run -n musai python scripts/run_pipeline.py data/open_songs/danny-boy-1917/original.ogg --run-name smoke-danny-120-fixed --max-duration 120 --asr-model base.en --language en --demucs-device cuda
```

النتيجة المسجلة:

- أربعة مسارات: `bass`، `drums`، `vocals`، `other`
- صوت إضافي: `instrumental`، `human_sound`
- تقدير السرعة: `129.20 BPM`
- عدد الإيقاعات: `257`
- مقاطع الأوتار: `132`
- حالة الكلمات: `ok`

راجع [`references/local-setup-and-test-report.md`](../references/local-setup-and-test-report.md).

## اتجاه المعمارية

Musai ليس مجرد ترجمة مع TTS. المسار الكامل المقصود هو:

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

ينفذ هذا المستودع طبقة التحليل المحلية الأولى. أما تركيب الغناء باستخدام YingMusic-Singer-Plus وSoulX-Singer والنماذج المشابهة فيبقى تكاملا بحثيا لأنه يحتاج إلى أوزان كبيرة، وفحص تراخيص، وتغليف GPU workers منفصل.

## الاقتباس

إذا استخدمت Musai في بحث، فاستشهد بهذا المستودع. يقرأ GitHub ملف [`CITATION.cff`](../CITATION.cff) ويعرض **Cite this repository** في صفحة المستودع.

```bibtex
@software{chen_musai_2026,
  author = {Chen, Lachlan},
  title = {Musai: Local-first AI song localization and music analysis},
  year = {2026},
  url = {https://github.com/lachlanchen/Musai}
}
```

## الحالة

Musai برنامج بحثي مبكر. تعمل القناة المحلية للاختبار وإنتاج الملفات، لكن كاشف الأوتار ما زال خط أساس خفيفا، وطبقة إعادة الغناء القابلة للغناء ليست جاهزة للإنتاج بعد. استخدم الأغاني التي تملكها، أو أغاني النطاق العام، أو الأغاني المرخصة، أو المواد التي يرفعها أصحابها.

