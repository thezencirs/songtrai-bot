---
name: songtrai-white-studio-lyric-graphmotion
description: 2K QHD+ (1440x2560 @ 30fps) Pure White Studio (#FFFFFF), Real Song Audio + Whisper/LRCLIB Word-by-Word Karaoke & 4 Era/Dominance Audio Decks (Vinyl Turntable, DJ Mix Deck, Retro Cassette, Optical CD) Engine for @songtraibot. Strictly prohibits artificial sound effects, space/neon/AI templates, or cluttered boxes. Uses pure white background, black text (#0A0A0E), song-specific dynamic accent colors, real 256kbps song audio, and poetic Turkish lyric translations across 10 global languages.
---

# Şarkıların Anlamı (@songtraibot) — Saf Beyaz Stüdyo, Gerçek Şarkı Sesi, Kelime Vurgulu Karaoke & 4 Ses İcadı Motoru (`songtrai-white-studio-lyric-graphmotion`)

## 1. Temel Görsel & İşitsel Anayasa: Saf Beyaz Fon (`#FFFFFF`), Siyah Yazı (`#0A0A0E`), Gerçek Şarkı Sesi & Sıfır Yapay Zeka İzi
`@songtraibot` için üretilen her 2K Reels videosu **Apple Music Sing / Musixmatch Pro / Teenage Engineering** editoryal sadeliğinde işlenir:
- **Kesin Yasaklar:** Yapay ses efektleri (bip, deklanşör, chime), uzay boşluğu, mor/mavi neon siber çizgiler, iç içe geçmiş kutucuk/çerçeve kalabalığı veya yapay zeka kokan plastik şablonlar **kesinlikle yasaktır**.
- **Gerçek Resmi Şarkı Sesi & Otomatik Senkronizasyon (`src/audio_karaoke_sync_engine.py`):** Şarkının gerçek resmi yüksek kaliteli sesi (iTunes / Deezer 256kbps AAC/MP3) doğrudan videoya gömülür. `faster-whisper` (`word_timestamps=True`) ve `LRCLIB syncedLyrics` (`[mm:ss.xx]`) hibrit hizalama motoru ile gerçek sesin şarkının hangi saniyesinden başladığı milisaniyesi milisaniyesine kilitlenir.
- **Kelime-Kelime (Word-by-Word) Karaoke Geçişleri:**
  - Arka plan **%100 Saf Beyaz (`#FFFFFF`)** ve kutusuzdur.
  - Söylenmiş kelimeler **Net Siyah (`#0A0A0E`)**, henüz sırası gelmemiş kelimeler **Yumuşak Gri (`#B4B4BE`)** olarak görünür.
  - Şarkıcının tam o salisede söylediği aktif kelime, **şarkıdan şarkıya değişen 7 editoryal vurgu renginden biriyle** (`Crimson Bordeaux`, `Royal Cobalt`, `Emerald Studio`, `Deep Violet`, `Burnt Amber`, `Ocean Teal`, `Magenta Rose`) çerçevesiz pastel fosfor ve alt ilerleme çizgisiyle aydınlanır.

---

## 2. Şarkının Dönemine ve Baskınlığına Göre Dönen 4 Farklı Ses İcadı (`src/era_audio_decks.py`)
Üst sahnede şarkının çıkış yılına (`release_year`) ve ses enerjisine/baskınlığına (`bass_energy`, `spectrum_bars`) göre 4 farklı fiziksel ses icadından en uygunu otomatik seçilir ve gerçek zamanlı döner:
1. **`vinyl_turntable` (Klasik Dönen 12" Vinil Plak & Pikap Kolu):** Zamansız klasikler, chanson ve akustik başyapıtlar için mikro oluklu dönen plak + albüm zarfı + metalik pikap iğne kolu (`tonearm`).
2. **`dj_mix_deck` (Modern Dönen DJ Mix Jog-Wheel + Canlı Spektrum & CUE Pad):** Yüksek enerjili ve bas baskın modern hitler için dönen motorize DJ Jog-Wheel, bas vuruşuyla parlayan LED halka, 4 CUE performans pad'i, 16-bant canlı frekans spektrumu ve hareketli crossfader.
3. **`retro_cassette` (80'ler/90'lar Çift Çarklı Dönen Kasetçalar):** Nostaljik, samimi ve indie şarkılar için çift makarası (`spools`) eşzamanlı dönen `Type II Chrome` kaset ve canlı VU ses seviye barları.
4. **`optical_cd_deck` (2000'ler İridyum Yansımalı Dönen Optik CD):** 2000'ler/2010'lar rock ve pop hitleri için gökkuşağı prizma yansımalı dönen polikarbonat Kompakt Disk (CD) ve albüm kitapçığı.

---

## 3. 10 Global Dil Havuzu & Çoklu Alfabe Desteği
1. **İngilizce (`en`)** 🇬🇧 | 2. **Rusça (`ru`)** 🇷🇺 | 3. **Japonca (`ja`)** 🇯🇵 | 4. **Almanca (`de`)** 🇩🇪 | 5. **İspanyolca (`es`)** 🇪🇸 | 6. **Korece (`ko`)** 🇰🇷 | 7. **Çince (`zh`)** 🇨🇳 | 8. **İtalyanca (`it`)** 🇮🇹 | 9. **Fransızca (`fr`)** 🇫🇷 | 10. **Hintçe (`hi`)** 🇮🇳

---

## 4. Zorunlu Teknik Koruma Kuralları & Uzun Vurucu Kesit Standardı (26.5s)
- **Uzun Vurucu Nakarat Zirvesi (`target_duration = 26.5s`):** Şarkının resmi 30 saniyelik önizleme kesitindeki en vurucu nakarat/zirve penceresi (`25.0s – 28.0s`, 6–10 senkronize dize) işlenir; kısa (`15-17s`) kesilmez.
- **Çerçevesiz Aktif Kelime Vurgusu (`_draw_karaoke_word_block`):** Aktif Türkçe kelimede bitişik kelimelere çarpan dış çerçeve (`outline`) çizilmez; yalnızca `accent_soft_rgb` dolgulu pastel vurgu (`pad_x = S(7)`), `accent_rgb` metin rengi ve kelime altında soldan sağa dolan ilerleme barı kullanılır.
- **Kırpılmasız Temas Gölgesi (`_paste_with_soft_shadow`):** Ses icadı kartları (`dj_mix_deck`, `retro_cassette`, albüm zarfı) tuvale yapıştırılırken GaussianBlur gölgesinin köşelerde dikdörtgen iz bırakmaması için `pad = max(24, elevation_px * 3)` taşma payı bırakılır.
- **Tofu (`□□`) Koruması (`_strip_canvas_emojis`):** Pillow TrueType fontlarıyla tuvale yazılan hiçbir metinde Unicode bayrak/sembol emojisi bırakılmaz.
