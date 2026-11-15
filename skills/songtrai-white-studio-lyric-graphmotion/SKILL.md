---
name: songtrai-white-studio-lyric-graphmotion
description: 2K QHD+ (1440x2560 @ 30fps) Pure White Studio (#FFFFFF), +20% Large Black Typography (#0A0A0E), Real Song Audio + Whisper/LRCLIB Word-by-Word Karaoke, Dedicated 9:16 Vertical Cover Poster & 4 Era Audio Decks Engine for @songtraibot. Supports 11 global languages (~50% Popular English weight + connected Arabic RTL, RU, JA, DE, ES, KO, ZH, IT, FR, HI) and short SEO copy-paste captions.
---

# Şarkıların Anlamı (@songtraibot) — Saf Beyaz Stüdyo, +20% Büyük Tipografi, 9:16 Dikey Kapak, Gerçek Şarkı Sesi & Kelime Vurgulu Karaoke Motoru (`songtrai-white-studio-lyric-graphmotion`)

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

## 3. 11 Global Dil Havuzu (%50 Popüler İngilizce Ağırlıklı + Birleşik Arapça RTL) & 180+ Şarkılık Genişletilmiş Katalog
- **Ağırlıklı Rotasyon (`LANGUAGE_ROTATION_ORDER`):** Otomatik üretimlerin ~%50'si popüler İngilizce (`en` 🇬🇧) hitlerden, diğer %50'si ise **Arapça (`ar` 🇸🇦)**, **Rusça (`ru` 🇷🇺)**, **Japonca (`ja` 🇯🇵)**, **Almanca (`de` 🇩🇪)**, **İspanyolca (`es` 🇪🇸)**, **Korece (`ko` 🇰🇷)**, **Çince (`zh` 🇨🇳)**, **İtalyanca (`it` 🇮🇹)**, **Fransızca (`fr` 🇫🇷)** ve **Hintçe (`hi` 🇮🇳)** şarkılardan seçilir.
- **Arapça Birleşik Harf & Sağdan Sola (RTL) Karaoke:** Pillow üzerinde Arapça harflerin kopuk görünmemesi için `arabic-reshaper` + `python-bidi` (`_shape_arabic_text`) zorunludur; Arapça satırlarda kelime sırası sağdan sola (`is_rtl_row`) dizilir.

---

## 4. Zorunlu Teknik Koruma Kuralları, +20% Punto, 9:16 Dikey Kapak & Kısa SEO Açıklama
- **Uzun Vurucu Nakarat Zirvesi (`target_duration = 26.5s`) & Mırıldanma Filtresi:** Şarkının en vurucu `26.5s` nakarat/zirve penceresi işlenir. LRCLIB'den gelen `"Hm-mm-mm"`, `"Oh-oh"` gibi anlamsız mırıldanma satırları (`_parse_lrc_lines`) otomatik filtrelenir.
- **+%20 Büyütülmüş Tipografi:** Aktif Türkçe çeviri `46pt` (`S(46)`), aktif orijinal söz `34pt` (`S(34)`), şarkı başlığı `36pt`, sanatçı `25pt`, önceki Türkçe dize `29pt`, sonraki Türkçe dize `30pt` ölçeğinde çizilir.
- **Şarkıya Özel Farklı 9:16 Dikey Kapak Resmi (`output/vertical_cover_9x16.jpg`):** Her şarkı için video karesinden bağımsız, albüm kılıfı + yarı çıkan plak/CD, başlık manşeti ve en anlamlı Türkçe dizeyi (`curated_stanzas`) içeren `1440x2560` dikey kapak (`render_songtrai_vertical_cover_9x16`) üretilir; tüm öğeler `S(200)..S(1710)` (4:5 güvenli alan) içinde tutulur ve Telegram'a `sendPhoto` ile ayrıca iletilir.
- **Kısa ve SEO Uyumlu Saf Kopyala-Yapıştır Açıklama (`build_pure_copy_paste_caption`):** 5–6 satırlık vurucu format (Başlık + en anlamlı Türkçe dize alıntısı + tek cümlelik anlam özeti + etkileşim çağrısı + temiz SEO etiketleri) kullanılır.
- **Çerçevesiz Aktif Kelime Vurgusu (`_draw_karaoke_word_block`):** Aktif Türkçe kelimede bitişik kelimelere çarpan dış çerçeve (`outline`) çizilmez; yalnızca `accent_soft_rgb` dolgulu pastel vurgu (`pad_x = S(9)`), `accent_rgb` metin rengi ve kelime altında soldan sağa dolan ilerleme barı kullanılır.
- **Kırpılmasız Temas Gölgesi (`_paste_with_soft_shadow`):** Ses icadı kartları (`dj_mix_deck`, `retro_cassette`, albüm zarfı) tuvale yapıştırılırken GaussianBlur gölgesinin köşelerde dikdörtgen iz bırakmaması için `pad = max(24, elevation_px * 3)` taşma payı bırakılır.
- **Tofu (`□□`) Koruması (`_strip_canvas_emojis`):** Pillow TrueType fontlarıyla tuvale yazılan hiçbir metinde Unicode bayrak/sembol emojisi bırakılmaz.
