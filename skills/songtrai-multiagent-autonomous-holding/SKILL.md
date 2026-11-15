---
name: songtrai-multiagent-autonomous-holding
description: 8-Agent Autonomous Music Translation, Real Song Audio + Whisper/LRCLIB Word-by-Word Karaoke, 9:16 Vertical Cover Poster & 4 Era Audio Decks Holding for @songtraibot. Coordinates 11-language popular song discovery (~50% Popular English weight + AR, RU, JA, DE, ES, KO, ZH, IT, FR, HI), poetic Turkish literary translation, Pure White Studio (#FFFFFF) + Black Text (#0A0A0E) + Song-Specific Accent Color, 4 Era/Dominance Audio Decks (Vinyl Turntable, DJ Mix Deck, Retro Cassette, Optical CD), hourly GitHub Actions stock generation, Zero-Repeat Double-Lock, and 24/7 Telegram delivery.
---

# Şarkıların Anlamı (@songtraibot) — 8 Ajanlı Otonom Gerçek Ses Senkronizasyonlu Karaoke, 9:16 Dikey Kapak & 4 Ses İcadı Holding Mimarisi (`songtrai-multiagent-autonomous-holding`)

## 1. Organizasyonel Amaç
`@songtraibot`, 11 global dilde (**~%50 Popüler İngilizce ağırlıklı** + Arapça, Rusça, Japonca, Almanca, İspanyolca, Korece, Çince, İtalyanca, Fransızca, Hintçe) en popüler ve duygusal derinliği yüksek şarkıları bulan, **sıfır yapay ses efekti ve sıfır yapay zeka şablonu iziyle Saf Beyaz Stüdyo (`#FFFFFF`)** üzerinde **gerçek resmi şarkı sesiyle kelime-kelime senkronize 26.5 saniyelik 2K QHD+ (`1440x2560 @ 30fps`) Karaoke Reels** videolarına ve **şarkıya özel farklı 9:16 dikey kapak resmine (`vertical_cover_9x16.jpg`)** dönüştüren, **kısa ve SEO uyumlu saf kopyala-yapıştır açıklama** ile GitHub Actions üzerinden Telegram'a stok akıtan 8 ajanlı otonom bir medya sistemidir.

---

## 2. 8 Uzman Ajan Kadrosu (`src/agent_team_registry.py`)

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
7. **`zero-repeat-stock-scheduler` — Saatlik Stok & Sıfır-Tekrar Çift Kilit Planlayıcı Ajanı**
   - `output/zero_repeat_ledger.json` dosyasını hem yerel diske hem GitHub API'ye kilitleyerek aynı şarkının tekrar üretilmesini engeller; her zamanlanmış çalışmada 3 adet uzun stok video üretir.
8. **`telegram-songtrai-publisher` — 7/24 @songtraibot 11 Dil Komut, 9:16 Dikey Kapak & Kısa SEO Kopyala-Yapıştır Teslimat Ajanı**
   - `@songtraibot` üzerinden gelen tüm dil komutlarını (`/ingilizce`, `/arapca`, `/rusca`, `/japonca`, `/almanca`, `/ispanyolca`, `/korece`, `/cince`, `/italyanca`, `/fransizca`, `/hintce`, `/uret`) veya şarkı adı/link taleplerini işler; **1) Şarkıya Özel 9:16 Dikey Kapak Resmi (`sendPhoto`), 2) Gerçek Sesli 26.5sn 2K Karaoke Video (`sendVideo`), 3) Kısa ve SEO Uyumlu %100 Saf Kopyala-Yapıştır Açıklama Metni (`sendMessage`)** olarak teslim eder.
