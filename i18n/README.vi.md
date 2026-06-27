[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)

[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# Musai

*Bản địa hóa bài hát bằng AI: trích xuất giọng người, stem, lời, nhịp và hợp âm từ một bài hát, rồi chuẩn bị đường đi tới hát lại đa ngôn ngữ có thể hát được.*

[![Website](https://img.shields.io/badge/Website-lazying.art-0EA5E9?style=for-the-badge)](https://lazying.art)
[![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python&logoColor=white)](../environment.yml)
[![CUDA](https://img.shields.io/badge/CUDA-tested-76B900?style=for-the-badge&logo=nvidia&logoColor=white)](../references/local-setup-and-test-report.md)
[![Sponsor](https://img.shields.io/badge/Sponsor-lachlanchen-EA4AAA?style=for-the-badge&logo=githubsponsors&logoColor=white)](https://github.com/sponsors/lachlanchen)

Musai là một nguyên mẫu nghiên cứu local-first cho bản địa hóa âm nhạc bằng AI. MVP hiện tại nhận một bài hát đầu vào, tách thành bốn stem Demucs `bass`, `drums`, `vocals`, `other`, tạo bản trộn `instrumental`, đặt bí danh giọng hát là `human_sound`, chép lời, ước lượng nhịp và tạo các đoạn hợp âm kiểu Chordify.

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://img.shields.io/badge/Donate-LazyingArt-0EA5E9?style=for-the-badge&logo=kofi&logoColor=white)](https://chat.lazying.art/donate) | [![PayPal](https://img.shields.io/badge/PayPal-RongzhouChen-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/RongzhouChen) | [![Stripe](https://img.shields.io/badge/Stripe-Donate-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

## Đầu Ra

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

`instrumental.wav` được trộn từ `bass + drums + other`. `human_sound.wav` là stem giọng hát đã tách `vocals.wav`.

## Nội Dung Hiện Có

| Path | Purpose |
| --- | --- |
| [`musai/`](../musai/) | Bộ công cụ phân tích Python chạy cục bộ. |
| [`scripts/bootstrap_musai.sh`](../scripts/bootstrap_musai.sh) | Tạo môi trường conda và cài stack cục bộ. |
| [`scripts/download_open_songs.py`](../scripts/download_open_songs.py) | Tải bài hát thử nghiệm miễn phí/mở. |
| [`scripts/run_pipeline.py`](../scripts/run_pipeline.py) | Chạy tách stem, chép lời, nhịp, hợp âm và báo cáo. |
| [`scripts/install_research_repos.sh`](../scripts/install_research_repos.sh) | Shallow-clone repo nghiên cứu tùy chọn vào `third_party/`. |
| [`scripts/musai_lyricfit_openai.py`](../scripts/musai_lyricfit_openai.py) | Trợ lý tùy chọn để thích nghi lời hát bằng OpenAI. |
| [`references/`](../references/) | Kiến trúc, nghiên cứu sâu và ghi chú cài đặt cục bộ. |
| [`TODO.md`](../TODO.md) | Danh sách việc cần làm và bước kỹ thuật tiếp theo. |

## Bắt Đầu Nhanh

```bash
bash scripts/bootstrap_musai.sh
PYTHONNOUSERSITE=1 conda run -n musai python scripts/download_open_songs.py --id danny-boy-1917
PYTHONNOUSERSITE=1 conda run -n musai python scripts/run_pipeline.py data/open_songs/danny-boy-1917/original.ogg --run-name smoke-danny --max-duration 45 --asr-model tiny
```

Kết quả được ghi vào:

```text
data/runs/<run-name>/
```

Âm thanh sinh ra, bài hát tải về, trọng số mô hình và repo bên thứ ba được git bỏ qua.

## Kiểm Chứng Cục Bộ

Smoke test cục bộ trên một bản ghi mở từ Wikimedia Commons đã chạy thành công trên máy NVIDIA RTX 4090 D:

```bash
PYTHONNOUSERSITE=1 conda run -n musai python scripts/run_pipeline.py data/open_songs/danny-boy-1917/original.ogg --run-name smoke-danny-120-fixed --max-duration 120 --asr-model base.en --language en --demucs-device cuda
```

Kết quả ghi nhận:

- Bốn stem: `bass`, `drums`, `vocals`, `other`
- Âm thanh bổ sung: `instrumental`, `human_sound`
- Ước lượng tempo: `129.20 BPM`
- Số beat: `257`
- Đoạn hợp âm: `132`
- Trạng thái lời: `ok`

Xem [`references/local-setup-and-test-report.md`](../references/local-setup-and-test-report.md).

## Hướng Kiến Trúc

Musai không chỉ là dịch cộng TTS. Pipeline đầy đủ dự kiến là:

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

Repo này triển khai lớp phân tích cục bộ đầu tiên. Tổng hợp giọng hát với YingMusic-Singer-Plus, SoulX-Singer và các mô hình liên quan vẫn là tích hợp nghiên cứu vì cần trọng số lớn, kiểm tra giấy phép và đóng gói worker GPU riêng.

## Trích Dẫn

Nếu dùng Musai trong nghiên cứu, hãy trích dẫn repo này. GitHub đọc [`CITATION.cff`](../CITATION.cff) và hiển thị **Cite this repository** trên trang repo.

```bibtex
@software{chen_musai_2026,
  author = {Chen, Lachlan},
  title = {Musai: Local-first AI song localization and music analysis},
  year = {2026},
  url = {https://github.com/lachlanchen/Musai}
}
```

## Trạng Thái

Musai là phần mềm nghiên cứu giai đoạn đầu. Pipeline cục bộ dùng được cho thử nghiệm và tạo artifact, nhưng bộ nhận diện hợp âm vẫn là baseline nhẹ và lớp hát lại có thể hát được chưa sẵn sàng cho sản xuất. Hãy dùng bài hát bạn sở hữu, bài public-domain, bài có giấy phép hoặc nội dung do creator tải lên.

