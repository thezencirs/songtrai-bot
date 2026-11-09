# Şarkıların Anlamı (@songtraibot) — Zorunlu Proje Kuralları (Workspace Rules)

Bu dizinde (`songtrai-bot`) çalışırken aşağıdaki kurallar istisnasız uygulanır:

1. **Sıfır Yapay Ses Efekti & %100 Gerçek Şarkı Sesi (Uzun Vurucu Kesit: 25s – 28.5s):**
   - Videolara asla yapay bip, chime, deklanşör veya sentetik ses efekti eklenmez.
   - Her videoda şarkının resmi yüksek kaliteli sesi (iTunes / Deezer 256kbps preview) kullanılır; en vurucu nakarat/zirve bölümü (`25.0s – 28.5s` uzunluğunda, 6–10 senkronize dize) seçilir ve `faster-whisper` (`word_timestamps=True`) + `LRCLIB syncedLyrics` ile milisaniyelik vokal senkronizasyonu otomatik yapılır.

2. **Kutusuz Saf Beyaz Fon (`#FFFFFF`), Siyah Yazı (`#0A0A0E`) ve Kelime-Kelime Karaoke:**
   - Arka plan daima `%100 Saf Beyaz (#FFFFFF)` olmalıdır; yapay zeka şablonu hissi veren iç içe kutular, çerçeveler veya karanlık/uzay arka planlar kesinlikle yasaktır.
   - Şarkı sözlerinde söylenmiş kelimeler **Net Siyah (`#0A0A0E`)**, henüz söylenmemiş kelimeler **Yumuşak Gri (`#B4B4BE`)**, tam o salisede söylenen aktif kelime ise **çerçevesiz pastel fosfor (`accent_soft_rgb`) + alt karaoke ilerleme çizgisi (`accent_rgb`)** ile vurgulanır. Aktif kelimenin etrafına bitişik kelimelere çarpan kalın kutu çerçevesi (`outline`) çizilmez.

3. **Şarkının Dönemine ve Baskınlığına Göre Dönen 4 Ses İcadı (`src/era_audio_decks.py`):**
   - Üst sahnede şarkının çıkış dönemine (`release_year`) ve bas/ritim baskınlığına (`bass_energy`, `spectrum_bars`) göre 4 ses icadından en uygunu döner:
     - `dj_mix_deck`: Yüksek enerjili / bas baskın modern hitler (Dönen DJ Jog-Wheel + Bas LED Halka + 4 CUE Pad + 16-Bant Canlı Spektrum + Crossfader).
     - `retro_cassette`: 80'ler/90'lar / nostaljik / samimi parçalar (Çift makarası dönen Type II Chrome Kaset + Canlı VU barları).
     - `optical_cd_deck`: 2000'ler/2010'lar rock/pop klasikleri (İridyum prizma yansımalı dönen Optik CD + Albüm kitapçığı).
     - `vinyl_turntable`: Zamansız klasikler / chanson eserler (Dönen 12" mikro oluklu Vinil Plak + Albüm zarfı + Metalik pikap iğne kolu).

4. **Teknik Görsel ve Operasyonel Koruma Kuralları:**
   - **Gölge Kırpılması Yasağı:** Yuvarlatılmış köşeli kartların gölgeleri asla kartın `(w, h)` boyutuna kırpılmaz; `_paste_with_soft_shadow` ile `pad = max(24, elevation_px * 3)` boşluk bırakılarak tuvale yapıştırılır.
   - **Tuval Emoji Temizliği:** Pillow TrueType fontlarında `□□` (tofu) kutusu oluşmaması için tuval üstüne yazılan tüm metinler `_strip_canvas_emojis` fonksiyonundan geçirilir (Telegram açıklamalarında emojiler korunur).
   - **Tekil Render Kilidi:** Aynı `output/_songtrai_frames` dizinini kullanan iki FFmpeg/render işlemi asla paralel başlatılmaz; ardışık (sequential) çalıştırılır.

5. **11 Global Dil (%50 Popüler İngilizce Ağırlıklı + Arapça RTL Desteği):**
   - Otomatik rotasyonda (`LANGUAGE_ROTATION_ORDER`) üretilen videoların ~%50'si popüler İngilizce hitlerden, diğer yarısı ise **Arapça (`arapca` / 🇸🇦)**, Fransızca, Rusça, Japonca, İspanyolca, Korece, İtalyanca, Almanca, Çince ve Hintçe popüler şarkılardan oluşur.
   - Arapça şarkılarda harflerin birleşik ve sağdan sola (RTL) doğru akması için `arabic-reshaper` + `python-bidi` (`_shape_arabic_text`) ve sağdan sola kelime dizilimi (`is_rtl_row`) zorunludur.

6. **Şarkıya Özel Farklı 9:16 Dikey Kapak Resmi (`output/vertical_cover_9x16.jpg`):**
   - Her şarkı için video karesinden farklı, `1440x2560` (9:16 dikey, 4:5 profil ızgarası güvenli alanına tam uyumlu) özel bir editoryal poster kapak resmi (`render_songtrai_vertical_cover_9x16`) üretilir ve Telegram'da videoyla birlikte ayrıca `sendPhoto` olarak gönderilir.

7. **Kısa ve SEO Uyumlu Saf Kopyala-Yapıştır Açıklama (`build_pure_copy_paste_caption`):**
   - Sosyal medya açıklama metni uzun kıta listeleri yerine 5–6 satırlık vurucu, kısa ve SEO uyumlu formatta (Şarkı başlığı + en vurucu Türkçe dize alıntısı + tek cümlelik anlam özeti + yorum/kaydetme çağrısı + hedef odaklı SEO etiketleri) ve sıfır sarmalayıcı başlıkla gönderilir.
