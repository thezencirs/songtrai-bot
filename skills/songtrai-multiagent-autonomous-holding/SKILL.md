---
name: songtrai-multiagent-autonomous-holding
description: 9-Agent Autonomous Music Translation, Real Song Audio + Whisper/LRCLIB Word-by-Word Karaoke, 9:16 Vertical Cover Poster, 4 Era Audio Decks & Pre-Render Turkish Translation Circuit-Breaker Holding for @songtraibot. Coordinates 11-language popular song discovery (~50% Popular English weight + AR, RU, JA, DE, ES, KO, ZH, IT, FR, HI), poetic Turkish literary translation, Pure White Studio (#FFFFFF) + Black Text (#0A0A0E) + Song-Specific Accent Color, 4 Era/Dominance Audio Decks, QA Translation Circuit Breaker (zero wasted CPU/carbon), and 24/7 Telegram delivery.
---

# Şarkıların Anlamı (@songtraibot) — 9 Ajanlı Otonom Gerçek Ses Senkronizasyonlu Karaoke, 9:16 Dikey Kapak, 4 Ses İcadı & Türkçe Çeviri Denetim Holding Mimarisi (`songtrai-multiagent-autonomous-holding`)

## 1. Organizasyonel Amaç
`@songtraibot`, 11 global dilde (**~%50 Popüler İngilizce ağırlıklı** + Arapça, Rusça, Japonca, Almanca, İspanyolca, Korece, Çince, İtalyanca, Fransızca, Hintçe) en popüler ve duygusal derinliği yüksek şarkıları bulan, **sıfır yapay ses efekti ve sıfır yapay zeka şablonu iziyle Saf Beyaz Stüdyo (`#FFFFFF`)** üzerinde **gerçek resmi şarkı sesiyle kelime-kelime senkronize 26.5 saniyelik 2K QHD+ (`1440x2560 @ 30fps`) Karaoke Reels** videolarına ve **şarkıya özel farklı 9:16 dikey kapak resmine (`vertical_cover_9x16.jpg`)** dönüştüren, **kısa ve SEO uyumlu saf kopyala-yapıştır açıklama** ile GitHub Actions üzerinden Telegram'a stok akıtan 9 ajanlı otonom bir medya sistemidir.

---

## 2. 9 Uzman Ajan Kadrosu (`src/agent_team_registry.py`)

1. **`global-chart-trend-hunter` — 11 Dilde (%50 Popüler İngilizce + Arapça Dahil) Global Hit & Viral Şarkı Keşif Ajanı**
   - Başta popüler İngilizce hitler olmak üzere Arapça, Rusça, Japonca, Almanca, İspanyolca, Korece, Çince, İtalyanca, Fransızca ve Hintçe listelerinde Türkiye'de en çok merak edilen viral şarkıları sıfır tekrarla seçer.
2. **`poetic-turkish-literary-translator` — Edebi & Kusursuz Türkçe Şarkı Sözü Çevirmen Ajanı**
   - Şarkı sözlerini robotik çeviri izi bırakmadan, Türkçe'nin şiirsel ve doğal akışına uygun şekilde çevirir; Arapça (`arabic-reshaper` + `python-bidi` RTL), Kiril, Kanji, Hangul, Hanzi ve Devanagari alfabeleri için Türkçe okunuş (fonetik) satırı ekler.
3. **`white-studio-editorial-art-director` — Saf Beyaz Stüdyo (#FFFFFF), +20% Büyük Siyah Tipografi & 9:16 Dikey Kapak Sanat Yönetmeni**
   - İtici kutucuk/çerçeve kalabalığını ve yapay zeka şablonlarını tamamen engeller; `#FFFFFF` saf beyaz fon üzerinde `#0A0A0E` siyah tipografi, şarkıdan şarkıya değişen 7 editoryal vurgu rengi ve paylaşımlarda kullanılmak üzere video karesinden farklı **9:16 Dikey Editoryal Kapak Resmi (`output/vertical_cover_9x16.jpg`)** üretir.
4. **`era-audio-deck-choreographer` — Dönem & Müzikal Baskınlık Bazlı 4 Ses İcadı Tasarım Ajanı (`src/era_audio_decks.py`)**
   - Şarkının çıkış yılına ve bas/ritim baskınlığına göre üst sahnede dönecek ses icadını seçer ve gerçek zamanlı ses enerjisiyle döndürür: `vinyl_turntable` (Dönen 12" Plak & Pikap Kolu), `dj_mix_deck` (Dönen DJ Jog-Wheel + Bas LED Halka + CUE Pad + 16-Bant Spektrum), `retro_cassette` (80'ler/90'lar Çift Çarklı Dönen Kaset), `optical_cd_deck` (2000'ler İridyum Dönen CD).
5. **`whisper-lrclib-karaoke-sync-director` — Gerçek Şarkı Sesi & Kelime-Kelime Karaoke Senkronizasyon Rejisörü (`src/audio_karaoke_sync_engine.py`)**
   - Şarkının gerçek 256kbps sesini iTunes/Deezer üzerinden indirir, en vurucu 26.5 saniyelik nakarat/zirve kesitini seçer, `faster-whisper` (`word_timestamps=True`) ve `LRCLIB syncedLyrics` ile milisaniyelik vokal ofsetini kilitler.
6. **`pure-real-audio-mastering-maestro` — Sıfır Yapay Efekt & Saf Gerçek Şarkı Sesi Mastering Mühendisi**
   - Yapay bip/efekt seslerini tamamen yasaklar; yalnızca gerçek şarkı sesini yumuşak fade-in/fade-out ve `320 kbps AAC` stüdyo kalitesiyle videoya gömer.
7. **`zero-repeat-stock-scheduler` — 4'lü Günlük Vardiya (09:00, 10:00, 19:00, 20:00) & Sıfır-Tekrar Çift Kilit Planlayıcı Ajanı**
   - `output/zero_repeat_ledger.json` ve `output/youtube_uploaded_ledger.json` dosyalarını kilitleyerek aynı şarkının tekrar üretilmesini veya YouTube'a mükerrer yüklenmesini engeller; Antigravity Automations (`gufteai-youtube-4slots-daily`), Windows Task Scheduler ve GitHub Actions üzerinde her gün **Sabah 09:00, 10:00 ve Akşam 19:00, 20:00 (`Europe/Istanbul`)** vardiyalarında çalışır.
8. **`telegram-songtrai-publisher` — 7/24 @songtraibot & YouTube (@gufteai) Harf Sayılı Yayın ve 🟢/🔴 Büyüme Analiz Ajanı**
   - `@songtraibot` üzerinden **1) 9:16 Dikey Kapak (`sendPhoto`), 2) 26.5sn 2K Karaoke Video (`sendVideo`), 3) Kısa SEO Açıklama, 4) YouTube (`@gufteai`) Harf Sayılı Başlık (`45..96/100`) & `1️⃣..N️⃣` Sıralı Açıklama (`<=5000`), 5) 🟢 YEŞİL / 🔴 KIRMIZI Kanal Günlük İzlenme & Para Kazanma (YPP) Raporu** teslim eder.
   - Chrome CDP (Port 9233) üzerinden `mmehmetofficial@gmail.com` hesabındaki **Güfte | Şarkı Çevirileri & Lyrics (`@gufteai` — `UCYN1vkTazFZ-SZSH9Gn4giA`)** kanalına doğrudan yükleme yapar (`PUBLIC` seçimi sonrası Polymer'in `"Yayınla"` butonunu aktif etmesi için `2.0 sn` bekler).
9. **`qa-turkish-translation-circuit-breaker` — Türkçe Çeviri Doğrulama & Hatalı Üretim Durdurucu Denetim Ajanı (`src/qa_translation_guardian.py`)**
   - 2K video kareleri henüz çizilmeden ÖNCE (`Pre-Render Gate`) ve yayından ÖNCE (`Pre-Publish Gate`) her dizeyi 5 kuraldan geçirir (`orig != tr`, sıfır yabancı alfabe sızıntısı, sıfır yabancı stopword sızıntısı, pozitif Türkçe dil sinyali).
   - Çevrilmemiş satır varsa önce 4 katmanlı çoklu çeviri motoru (`clients5.google.com`, `dict-chrome-ex`, `gtx`, `MyMemory`) ve `song["curated_stanzas"]` ile onarır; onarılamazsa boşa CPU, zaman ve karbon harcamamak için **üretimi anında durdurur (`TranslationQAGateError`)**.
