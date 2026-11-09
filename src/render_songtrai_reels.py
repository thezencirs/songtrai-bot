# -*- coding: utf-8 -*-
"""
Şarkıların Anlamı (@songtraibot) — 2K QHD+ (1440x2560 @ 30 FPS) Saf Beyaz Fon (#FFFFFF),
Siyah Tipografi, Kelime Vurgulu Karaoke & Dönemsel Ses İcadı (Plak / DJ Mix / Kaset / CD) Motoru
================================================================================================
- %100 Saf Beyaz Fon (#FFFFFF), Sıfır Yapay Kutucuk / Sıfır AI İzi.
- Sıfır yapay ses efekti: Videoda %100 gerçek şarkı sesi çalar ve sözler gerçek vokalle
  milisaniye hassasiyetinde kelime-kelime (Karaoke Word-by-Word) senkronize akar.
- Üst bölümde şarkının dönemine ve baskınlığına göre Dönen Vinil Plak, DJ Mix Jog-Wheel Deck,
  Çift Çarklı Retro Kaset veya İridyum Optik CD gerçek ses frekanslarıyla hareket eder.
- Alt bölümde Saf Beyaz (#FFFFFF) zemin üzerinde Siyah (#0A0A0E) yazılar ve şarkıdan şarkıya
  değişen dinamik vurgu rengiyle (Bordo, Kraliyet Mavisi, Zümrüt, Mor, Kehribar) kelime kelime
  karaoke geçişi uygulanır.
"""

import math
import os
import re
import shutil
import subprocess
from typing import Any, Dict, List, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from audio_karaoke_sync_engine import (
    get_ffmpeg_exe,
    pick_song_accent_color,
    prepare_trimmed_song_wav_and_telemetry,
    synchronize_song_karaoke_timeline,
)
from era_audio_decks import (
    _make_clean_album_card,
    _paste_with_soft_shadow,
    _render_iridescent_cd_disc,
    render_era_audio_deck_on_stage,
    select_audio_deck_type,
)
from white_studio_optics import (
    apply_editorial_paper_film_grain,
    fetch_official_album_artwork,
    render_vinyl_record_disc,
)

try:
    import arabic_reshaper
    from bidi.algorithm import get_display as _bidi_get_display
except Exception:
    arabic_reshaper = None
    _bidi_get_display = None

W, H = 1440, 2560
SCALE = W / 1080.0
FPS = 30

_FONT_CACHE: Dict[Tuple[str, int, bool, bool], ImageFont.FreeTypeFont] = {}


def S(val: float) -> int:
    return int(round(val * SCALE))


def _remotion_spring(
    t: float,
    damping: float = 16.0,
    stiffness: float = 135.0,
    mass: float = 0.8,
) -> float:
    if t <= 0.0:
        return 0.0
    omega0 = math.sqrt(stiffness / max(0.001, mass))
    zeta = damping / (2.0 * math.sqrt(stiffness * max(0.001, mass)))
    if zeta < 1.0:
        omega_d = omega0 * math.sqrt(1.0 - zeta * zeta)
        env = math.exp(-zeta * omega0 * t)
        val = 1.0 - env * (
            math.cos(omega_d * t) + (zeta / math.sqrt(1.0 - zeta * zeta)) * math.sin(omega_d * t)
        )
    else:
        val = 1.0 - (1.0 + omega0 * t) * math.exp(-omega0 * t)
    return float(max(0.0, min(1.06, val)))


def _has_arabic_chars(s: str) -> bool:
    for ch in (s or ""):
        cp = ord(ch)
        if (0x0600 <= cp <= 0x06FF) or (0x0750 <= cp <= 0x077F) or (0xFB50 <= cp <= 0xFDFF) or (0xFE70 <= cp <= 0xFEFF):
            return True
    return False


def _shape_arabic_text(s: str) -> str:
    if not s or not _has_arabic_chars(s):
        return s
    # Eğer metin zaten sunum formlarına (FE70-FEFF) dönüştürülmüşse tekrar dönüştürme
    if any(0xFE70 <= ord(ch) <= 0xFEFF for ch in s):
        return s
    if arabic_reshaper is not None and _bidi_get_display is not None:
        try:
            reshaped = arabic_reshaper.reshape(s)
            return str(_bidi_get_display(reshaped))
        except Exception:
            return s
    return s


def _strip_canvas_emojis(s: str) -> str:
    out_chars = []
    for ch in (s or ""):
        cp = ord(ch)
        if cp >= 0x1F000 or (0x2600 <= cp <= 0x27BF) or cp == 0xFE0F:
            continue
        out_chars.append(ch)
    cleaned = re.sub(r"\s+", " ", "".join(out_chars)).strip()
    return _shape_arabic_text(cleaned)


def _tr_upper(s: str) -> str:
    return _strip_canvas_emojis(s or "").replace("i", "İ").replace("ı", "I").upper()


def _detect_script_family(text: str) -> str:
    for ch in (text or ""):
        cp = ord(ch)
        if (0x0600 <= cp <= 0x06FF) or (0xFB50 <= cp <= 0xFDFF) or (0xFE70 <= cp <= 0xFEFF):
            return "ar"
        if 0xAC00 <= cp <= 0xD7AF or 0x1100 <= cp <= 0x11FF or 0x3130 <= cp <= 0x318F:
            return "ko"
        if 0x3040 <= cp <= 0x30FF:
            return "ja"
        if 0x0900 <= cp <= 0x097F:
            return "hi"
    for ch in (text or ""):
        cp = ord(ch)
        if 0x4E00 <= cp <= 0x9FFF:
            return "zh"
    return "latin_cyrillic"


def get_script_font(
    text: str,
    size_1080: int,
    bold: bool = True,
    serif: bool = False,
) -> ImageFont.FreeTypeFont:
    script = _detect_script_family(text)
    size = S(size_1080)
    cache_key = (script, size, bold, serif)
    if cache_key in _FONT_CACHE:
        return _FONT_CACHE[cache_key]

    if script == "ar":
        candidates = [
            "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
            "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansArabic-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
    elif script == "ko":
        candidates = [
            "C:/Windows/Fonts/malgunbd.ttf" if bold else "C:/Windows/Fonts/malgun.ttf",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        ]
    elif script == "ja":
        candidates = [
            "C:/Windows/Fonts/YuGothB.ttc" if bold else "C:/Windows/Fonts/YuGothM.ttc",
            "C:/Windows/Fonts/msgothic.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        ]
    elif script == "zh":
        candidates = [
            "C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/YuGothB.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        ]
    elif script == "hi":
        candidates = [
            "C:/Windows/Fonts/Nirmala.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
    else:
        if serif:
            candidates = [
                "C:/Windows/Fonts/georgiab.ttf" if bold else "C:/Windows/Fonts/georgia.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
            ]
        else:
            candidates = [
                "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
                "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            ]

    for path in candidates:
        if os.path.exists(path):
            try:
                f = ImageFont.truetype(path, size)
                _FONT_CACHE[cache_key] = f
                return f
            except Exception:
                continue

    fallback = ImageFont.load_default()
    _FONT_CACHE[cache_key] = fallback
    return fallback


def _text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0]
    except Exception:
        return len(text) * S(16)


def _create_pure_white_canvas() -> Image.Image:
    """
    %100 Saf Beyaz Fon (#FFFFFF) — Sıfır kutucuk, sıfır çerçeve karmaşası, sıfır yapay zeka izi!
    """
    return Image.new("RGBA", (W, H), (255, 255, 255, 255))


def _layout_word_lines(
    draw: ImageDraw.ImageDraw,
    words_list: List[Dict[str, Any]],
    font: ImageFont.FreeTypeFont,
    max_width_px: int,
    space_px: int,
) -> List[List[Dict[str, Any]]]:
    """
    Kelime zaman damgalı listeyi (`[{word, start, end}]`), satır genişliğini aşmayacak
    şekilde çoklu satırlara böler ve her kelimenin piksel genişliğini (`w_px`) hesaplar.
    """
    rows: List[List[Dict[str, Any]]] = []
    cur_row: List[Dict[str, Any]] = []
    cur_w = 0

    for w_obj in words_list:
        w_str = _strip_canvas_emojis(str(w_obj.get("word", "")))
        if not w_str:
            continue
        w_px = _text_width(draw, w_str, font)
        item = {**w_obj, "word": w_str, "w_px": w_px}

        added_w = w_px if not cur_row else (space_px + w_px)
        if cur_row and (cur_w + added_w > max_width_px):
            rows.append(cur_row)
            cur_row = [item]
            cur_w = w_px
        else:
            cur_row.append(item)
            cur_w += added_w

    if cur_row:
        rows.append(cur_row)
    return rows[:4]


def _draw_karaoke_word_block(
    draw: ImageDraw.ImageDraw,
    words_list: List[Dict[str, Any]],
    t: float,
    center_x: int,
    start_y: int,
    font: ImageFont.FreeTypeFont,
    max_width_px: int,
    line_step_px: int,
    accent_rgb: Tuple[int, int, int],
    accent_soft_rgb: Tuple[int, int, int],
    is_hero_turkish: bool = False,
    global_alpha: float = 1.0,
) -> int:
    """
    Kelime-kelime (Word-by-Word) Karaoke Çizim Motoru:
    - Henüz söylenmemiş kelimeler: Yumuşak Gri (`#B4B4BE`)
    - Söylenmiş kelimeler: Net Siyah (`#0B0B0F`)
    - Tam şu an söylenen aktif kelime (`w.start <= t <= w.end`):
      * Türkçe çeviri satırında (`is_hero_turkish=True`): Şarkının vurgu renginde (`accent_rgb`)
        yuvarlatılmış Karaoke Vurgu Kapsülü + Beyaz/Siyah yüksek kontrastlı metin ve `-6px` yaylanmalı yükseliş!
      * Orijinal satırda (`is_hero_turkish=False`): Şarkının vurgu renginde (`accent_rgb`) metin +
        kelimenin altında sol-sağ ilerleyen dinamik karaoke çizgisi!
    """
    if not words_list:
        return start_y

    space_px = S(24 if is_hero_turkish else 18)
    rows = _layout_word_lines(draw, words_list, font, max_width_px, space_px)
    ar, ag, ab = accent_rgb
    sr, sg, sb = accent_soft_rgb
    alpha_int = int(255 * max(0.0, min(1.0, global_alpha)))

    cur_y = start_y
    for row in rows:
        is_rtl_row = any(_has_arabic_chars(it["word"]) for it in row)
        row_ordered = list(reversed(row)) if is_rtl_row else row
        total_row_w = sum(it["w_px"] for it in row_ordered) + space_px * max(0, len(row_ordered) - 1)
        cur_x = center_x - (total_row_w // 2)

        for it in row_ordered:
            w_str = it["word"]
            w_px = it["w_px"]
            w_start = float(it.get("start", 0.0))
            w_end = float(it.get("end", w_start + 0.35))
            w_dur = max(0.08, w_end - w_start)

            if global_alpha < 0.55:
                # Önceki veya sonraki soluk satır
                col = (176, 176, 186, alpha_int) if not is_hero_turkish else (142, 142, 154, alpha_int)
                draw.text((cur_x + w_px // 2, cur_y), w_str, fill=col, font=font, anchor="mm")
            else:
                if t >= w_end:
                    # Söylenmiş kelime -> Net Siyah (#0B0B0F)
                    col = (10, 10, 14, 255) if is_hero_turkish else (24, 24, 30, 255)
                    draw.text((cur_x + w_px // 2, cur_y), w_str, fill=col, font=font, anchor="mm")
                elif t < w_start:
                    # Henüz sıra gelmemiş kelime -> Yumuşak Gri (#B4B4BE)
                    col = (170, 170, 180, 255) if is_hero_turkish else (184, 184, 194, 255)
                    draw.text((cur_x + w_px // 2, cur_y), w_str, fill=col, font=font, anchor="mm")
                else:
                    # TAM ŞU AN SÖYLENEN AKTİF KELİME (Karaoke Vurgusu — Sıfır Kutu Çerçevesi!)
                    w_prog = max(0.0, min(1.0, (t - w_start) / w_dur))
                    lift_y = int(round(S(7) * math.sin(w_prog * math.pi)))

                    if is_hero_turkish:
                        pad_x = S(9)
                        # Soldan sağa akan yumuşak pastel karaoke fosfor vurgusu (çerçevesiz, %20 büyütülmüş punto uyumlu!)
                        hl_w = max(S(16), int((w_px + pad_x * 2) * (0.35 + 0.65 * w_prog)))
                        draw.rounded_rectangle(
                            (
                                cur_x - pad_x,
                                cur_y - S(32) - lift_y,
                                cur_x - pad_x + hl_w,
                                cur_y + S(32) - lift_y,
                            ),
                            radius=S(14),
                            fill=(sr, sg, sb, 255),
                        )
                        # Kelimenin altında soldan sağa dolan canlı karaoke ilerleme çizgisi
                        fill_w = max(S(12), int(w_px * w_prog))
                        draw.rounded_rectangle(
                            (
                                cur_x,
                                cur_y + S(33) - lift_y,
                                cur_x + fill_w,
                                cur_y + S(40) - lift_y,
                            ),
                            radius=S(4),
                            fill=(ar, ag, ab, 255),
                        )
                        draw.text(
                            (cur_x + w_px // 2, cur_y - lift_y),
                            w_str,
                            fill=(ar, ag, ab, 255),
                            font=font,
                            anchor="mm",
                        )
                    else:
                        # Orijinal sözde aktif kelime: Vurgu rengi + altta karaoke çizgisi
                        draw.text(
                            (cur_x + w_px // 2, cur_y - lift_y),
                            w_str,
                            fill=(ar, ag, ab, 255),
                            font=font,
                            anchor="mm",
                        )
                        ul_w = max(S(10), int(w_px * w_prog))
                        ul_x1 = (cur_x + w_px - ul_w) if is_rtl_row else cur_x
                        ul_x2 = (cur_x + w_px) if is_rtl_row else (cur_x + ul_w)
                        draw.rounded_rectangle(
                            (ul_x1, cur_y + S(27) - lift_y, ul_x2, cur_y + S(34) - lift_y),
                            radius=S(3),
                            fill=(ar, ag, ab, 255),
                        )

            cur_x += w_px + space_px

        cur_y += line_step_px

    return cur_y


def _fmt_mmss(sec: float) -> str:
    s = max(0, int(round(sec)))
    return f"{s // 60}:{s % 60:02d}"


def _wrap_plain_text_lines(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width_px: int,
) -> List[str]:
    cleaned = _strip_canvas_emojis(text)
    if not cleaned:
        return []
    words = cleaned.split(" ")
    lines: List[str] = []
    cur = ""
    for w in words:
        cand = w if not cur else f"{cur} {w}"
        if _text_width(draw, cand, font) <= max_width_px or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines[:4]


def render_songtrai_vertical_cover_9x16(
    song: Dict[str, Any],
    album_cover: Image.Image,
    accent_info: Dict[str, Any],
    deck_type: str,
    output_jpg_path: str,
) -> str:
    """
    Paylaşımlarda (Instagram Reels / TikTok / YouTube Shorts) kullanılmak üzere
    o şarkıya özel, video karesinden FARKLI, dikey (9:16, 1440x2560) editoryal poster kapak resmi üretir.
    - Tüm ana öğeler 4:5 profil ızgarası güvenli alanı (`y: 280 .. 2280`) içinde hizalanır.
    - Albüm kılıfından yarı çıkan vinil plak/optik disk kompozisyonu, dev şarkı & sanatçı başlığı,
      Türkçe kapak manşeti (`cover_headline`) ve şarkının en vurucu Türkçe sözü yer alır.
    """
    canvas = _create_pure_white_canvas()
    draw = ImageDraw.Draw(canvas)

    accent_rgb: Tuple[int, int, int] = accent_info["rgb"]
    accent_soft_rgb: Tuple[int, int, int] = accent_info["soft_rgb"]
    ar, ag, ab = accent_rgb
    sr, sg, sb = accent_soft_rgb

    artist = _strip_canvas_emojis(song.get("artist", "Artist"))
    title = _strip_canvas_emojis(song.get("title", "Song"))
    lang_tr = _tr_upper(song.get("language_tr", "İNGİLİZCE"))
    lang_code = song.get("language_code", "EN")
    year = str(song.get("release_year", ""))
    headline = _tr_upper(song.get("cover_headline", "BU ŞARKININ TÜRKÇE ANLAMINI BİLİYOR MUYDUNUZ?"))

    # 1) Üst ve Alt Yumuşak Editoryal Dekoratif Şeritler (Saf Beyaz Stüdyo Estetiği)
    draw.rounded_rectangle(
        (S(90), S(290), W - S(90), S(356)),
        radius=S(33),
        fill=(sr, sg, sb, 255),
    )
    f_badge = get_script_font(lang_tr, 21, bold=True)
    badge_text = f"{lang_code} • {lang_tr} ŞARKI ÇEVİRİSİ" + (f"   |   {year}" if year else "")
    draw.text(
        (W // 2, S(323)),
        badge_text,
        fill=(ar, ag, ab, 255),
        font=f_badge,
        anchor="mm",
    )

    # 2) MERKEZ GÖRSEL SAHNE (`y: 410 .. 1060`): Albüm Kılıfı + Yarı Çıkan Vinil Plak / Optik CD
    sleeve_sz = S(490)
    disc_sz = S(460)
    # Plak sağda yarı dışarı çıkmış, albüm kapağı solda önde
    sleeve_x = (W // 2) - S(320)
    sleeve_y = S(425)
    disc_x = sleeve_x + S(215)
    disc_y = sleeve_y + S(15)

    is_optical = deck_type == "optical_cd_deck"
    if is_optical:
        disc_img = _render_iridescent_cd_disc(album_cover, diameter=disc_sz, angle_deg=24.0)
    else:
        disc_img = render_vinyl_record_disc(album_cover, diameter=disc_sz, angle_deg=24.0)

    _paste_with_soft_shadow(
        canvas=canvas,
        card_rgba=disc_img,
        x=disc_x,
        y=disc_y,
        elevation_px=S(12),
    )

    # Albüm Kılıfı (Ön Planda, Yuvarlatılmış Köşe + İnce Çerçeve)
    sleeve_card = _make_clean_album_card(album_cover, sleeve_sz, accent_rgb)
    _paste_with_soft_shadow(
        canvas=canvas,
        card_rgba=sleeve_card,
        x=sleeve_x,
        y=sleeve_y,
        elevation_px=S(14),
    )

    draw = ImageDraw.Draw(canvas)

    # 3) DEV ŞARKI ADI & SANATÇI KİMLİĞİ (`y: 1005 .. 1165`)
    f_cov_title = get_script_font(title, 48, bold=True)
    if _text_width(draw, title, f_cov_title) > W - S(120):
        f_cov_title = get_script_font(title, 38, bold=True)
    if _text_width(draw, title, f_cov_title) > W - S(120):
        f_cov_title = get_script_font(title, 30, bold=True)
    draw.text((W // 2, S(1025)), title, fill=(10, 10, 14, 255), font=f_cov_title, anchor="mm")

    f_cov_artist = get_script_font(artist, 28, bold=True)
    draw.text((W // 2, S(1098)), artist, fill=(ar, ag, ab, 255), font=f_cov_artist, anchor="mm")

    # 4) VURUCU KAPAK MANŞETİ (`y: 1170 .. 1350`)
    f_head = get_script_font(headline, 24, bold=True)
    head_lines = _wrap_plain_text_lines(draw, headline, f_head, W - S(180))[:2]
    box_h = S(58) + len(head_lines) * S(42)
    box_top = S(1168)
    draw.rounded_rectangle(
        (S(80), box_top, W - S(80), box_top + box_h),
        radius=S(22),
        fill=(ar, ag, ab, 255),
    )
    hy = box_top + S(38)
    for hl in head_lines:
        draw.text((W // 2, hy), hl, fill=(255, 255, 255, 255), font=f_head, anchor="mm")
        hy += S(42)

    # 5) ŞARKININ EN VURUCU SÖZÜ & TÜRKÇE ÇEVİRİSİ POSTER BLOĞU (`y: 1365 .. 2110`)
    stanzas = song.get("curated_stanzas") or song.get("stanzas") or []
    best_st = stanzas[0] if stanzas else {"orig": "", "tr": ""}
    for st_cand in stanzas:
        cand_tr = (st_cand.get("tr") or "").strip()
        if len(cand_tr) >= 28 and len(cand_tr) > len(best_st.get("tr", "")):
            best_st = st_cand
            break
    hero_orig = best_st.get("orig", "")
    hero_tr = best_st.get("tr", "")

    quote_top = box_top + box_h + S(48)
    # Dekoratif tırnak işareti
    f_qmark = get_script_font("“", 82, bold=True, serif=True)
    draw.text((W // 2, quote_top + S(12)), "“", fill=(sr, sg, sb, 255), font=f_qmark, anchor="mm")

    # Orijinal dize
    f_q_orig = get_script_font(hero_orig, 30, bold=True)
    orig_lines = _wrap_plain_text_lines(draw, hero_orig, f_q_orig, W - S(150))[:2]
    qy = quote_top + S(62)
    for ol in orig_lines:
        draw.text((W // 2, qy), ol, fill=(92, 92, 104, 255), font=f_q_orig, anchor="mm")
        qy += S(54)

    # İnce vurgu ayırıcı çizgi
    qy += S(12)
    draw.rounded_rectangle(
        (W // 2 - S(55), qy, W // 2 + S(55), qy + S(7)),
        radius=S(4),
        fill=(ar, ag, ab, 255),
    )
    qy += S(58)

    # Dev Türkçe Çeviri Alıntısı (Net Siyah + Vurgu Rengi Şerit)
    f_q_tr = get_script_font(hero_tr, 44, bold=True)
    tr_lines = _wrap_plain_text_lines(draw, f"“{hero_tr}”", f_q_tr, W - S(130))[:3]
    for idx_tl, tl in enumerate(tr_lines):
        tw = _text_width(draw, tl, f_q_tr)
        if idx_tl == len(tr_lines) - 1:
            # Son satırın altında pastel fosfor şeridi
            draw.rounded_rectangle(
                (W // 2 - tw // 2 - S(14), qy - S(26), W // 2 + tw // 2 + S(14), qy + S(28)),
                radius=S(14),
                fill=(sr, sg, sb, 255),
            )
            draw.text((W // 2, qy), tl, fill=(ar, ag, ab, 255), font=f_q_tr, anchor="mm")
        else:
            draw.text((W // 2, qy), tl, fill=(10, 10, 14, 255), font=f_q_tr, anchor="mm")
        qy += S(78)

    # 6) ALT İMZA ŞERİDİ (`S(1685)` = 2246px, 4:5 güvenli alan sınırında)
    footer_y = max(qy + S(32), S(1685))
    f_footer = get_script_font("TÜRKÇE ÇEVİRİ & KARAOKE", 19, bold=True)
    draw.rounded_rectangle(
        (W // 2 - S(275), footer_y - S(26), W // 2 + S(275), footer_y + S(26)),
        radius=S(26),
        fill=(244, 244, 248, 255),
    )
    draw.text(
        (W // 2, footer_y),
        "ŞARKILARIN ANLAMI  •  TÜRKÇE ÇEVİRİ",
        fill=(70, 70, 82, 255),
        font=f_footer,
        anchor="mm",
    )

    cover_rgb = apply_editorial_paper_film_grain(canvas.convert("RGB"), frame_idx=7)
    cover_rgb.save(output_jpg_path, "JPEG", quality=96)
    return output_jpg_path


def render_songtrai_graphmotion_reel(
    song: Dict[str, Any],
    output_mp4: str,
) -> Dict[str, Any]:
    """
    2K QHD+ (1440x2560 @ 30 FPS) Saf Beyaz Fon (#FFFFFF), Siyah Tipografi,
    Gerçek Şarkı Sesi ve Kelime Vurgulu Karaoke Reels Videosu üretir.
    """
    out_dir = os.path.dirname(output_mp4) or "output"
    os.makedirs(out_dir, exist_ok=True)
    frames_dir = os.path.join(out_dir, "_songtrai_frames")
    shutil.rmtree(frames_dir, ignore_errors=True)
    os.makedirs(frames_dir, exist_ok=True)

    target_duration = 26.5

    # 1) Gerçek şarkı sesini indir ve Whisper + LRCLIB ile en vurucu 25-27sn nakarat/zirve zamanlarını hizala
    sync_data = synchronize_song_karaoke_timeline(song, target_duration=target_duration)
    total_duration = float(sync_data.get("duration", target_duration))
    total_frames = int(round(total_duration * FPS))
    events = sync_data["events"]
    if events:
        if not song.get("curated_stanzas") and song.get("stanzas"):
            song["curated_stanzas"] = list(song["stanzas"])
        song["stanzas"] = [
            {"orig": ev["orig"], "pron": ev.get("pron", ""), "tr": ev["tr"]}
            for ev in events
        ]

    wav_path = os.path.join(out_dir, "songtrai_real_song.wav")
    telemetry = prepare_trimmed_song_wav_and_telemetry(
        raw_audio_path=sync_data["raw_audio_path"],
        out_wav_path=wav_path,
        trim_start=sync_data["audio_trim_start"],
        duration=total_duration,
        fps=FPS,
    )
    bass_per_frame = telemetry["bass_per_frame"]
    spec_per_frame = telemetry["spec_per_frame"]

    # 2) Şarkının dönemine ve baskınlığına göre Ses İcadını (Plak / DJ Mix / Kaset / CD) ve Vurgu Rengini seç
    deck_type = select_audio_deck_type(song, avg_bpm_or_energy=telemetry["avg_energy"])
    accent_info = pick_song_accent_color(song)
    accent_rgb: Tuple[int, int, int] = accent_info["rgb"]
    accent_soft_rgb: Tuple[int, int, int] = accent_info["soft_rgb"]

    album_cover = fetch_official_album_artwork(song, size=900)
    artist = _strip_canvas_emojis(song.get("artist", "Artist"))
    title = _strip_canvas_emojis(song.get("title", "Song"))
    lang_tr = _tr_upper(song.get("language_tr", "İNGİLİZCE"))
    lang_code = song.get("language_code", "EN")
    year = str(song.get("release_year", ""))

    deck_labels = {
        "vinyl_turntable": "33⅓ RPM VİNİL PLAK • GERÇEK SES SENKRON",
        "dj_mix_deck": "DJ MIX DECK • CANLI BAS & KARAOKE SENKRON",
        "retro_cassette": "ANALOG KASETÇALAR • GERÇEK SES SENKRON",
        "optical_cd_deck": "OPTİK CD DECK • GERÇEK SES SENKRON",
    }
    deck_badge_txt = f"{lang_code} ({lang_tr})  •  {deck_labels.get(deck_type, 'STÜDYO SENKRON')}"

    f_top_tag = get_script_font(deck_badge_txt, 19, bold=True)
    f_title = get_script_font(title, 36, bold=True)
    f_artist = get_script_font(artist, 25, bold=False)
    f_time = get_script_font("0:00", 19, bold=True)

    cover_saved = False
    first_ev_start = float(events[0]["start"]) if events else 1.2

    for f_idx in range(total_frames):
        t = f_idx / float(FPS)
        bass_val = bass_per_frame[min(f_idx, len(bass_per_frame) - 1)]
        spec_bars = spec_per_frame[min(f_idx, len(spec_per_frame) - 1)]

        canvas = _create_pure_white_canvas()
        draw = ImageDraw.Draw(canvas)

        # Üst Minimal Dil & Ses İcadı Başlığı (Kutucuksuz, saf siyah & vurgu rengi)
        draw.text(
            (W // 2, S(86)),
            deck_badge_txt,
            fill=accent_rgb + (255,),
            font=f_top_tag,
            anchor="mm",
        )

        # 1) ÜST BÖLÜM (`y: 145 .. 680`): Şarkının Dönemine Göre Dönen Plak / DJ Mix / Kaset / CD
        render_era_audio_deck_on_stage(
            canvas=canvas,
            deck_type=deck_type,
            album_cover=album_cover,
            song=song,
            t=t,
            bass_energy=bass_val,
            spectrum_bars=spec_bars,
            accent_rgb=accent_rgb,
            scale_fn=S,
            font_getter=get_script_font,
        )

        # 2) ORTA KİMLİK & CANLI ZAMAN ÇUBUĞU (`y: 710 .. 855`)
        title_line = f"{title}"
        f_t_fit = f_title if _text_width(draw, title_line, f_title) <= W - S(120) else get_script_font(title, 28, bold=True)
        draw.text((W // 2, S(714)), title_line, fill=(12, 12, 16, 255), font=f_t_fit, anchor="mm")
        draw.text(
            (W // 2, S(770)),
            f"{artist}  •  {year}" if year else artist,
            fill=(112, 112, 122, 255),
            font=f_artist,
            anchor="mm",
        )

        # Minimalist Apple Music tarzı oynatma çubuğu (Scrub Bar)
        bar_left, bar_right = S(135), W - S(135)
        bar_y = S(826)
        draw.rounded_rectangle(
            (bar_left, bar_y - S(3), bar_right, bar_y + S(3)),
            radius=S(3),
            fill=(232, 232, 238, 255),
        )
        prog_x = bar_left + int((bar_right - bar_left) * (t / total_duration))
        draw.rounded_rectangle(
            (bar_left, bar_y - S(3), prog_x, bar_y + S(3)),
            radius=S(3),
            fill=accent_rgb + (255,),
        )
        draw.ellipse(
            (prog_x - S(9), bar_y - S(9), prog_x + S(9), bar_y + S(9)),
            fill=accent_rgb + (255,),
        )
        draw.text((bar_left, bar_y + S(28)), _fmt_mmss(t), fill=(130, 130, 140, 255), font=f_time, anchor="lm")
        draw.text((bar_right, bar_y + S(28)), _fmt_mmss(total_duration), fill=(130, 130, 140, 255), font=f_time, anchor="rm")

        # 3) ALT BÖLÜM (`y: 910 .. 2420`): SAF BEYAZ FON ÜZERİNDE %20 BÜYÜTÜLMÜŞ KELİME VURGULU KARAOKE AKIŞI
        active_idx = 0
        for idx_e, ev in enumerate(events):
            if t >= ev["start"]:
                active_idx = idx_e
            else:
                break

        cur_ev = events[active_idx]
        dt_line = max(0.0, t - cur_ev["start"])
        sp_scroll = _remotion_spring(dt_line, damping=16.0, stiffness=135.0, mass=0.8)
        slide_offset_y = int(round((1.0 - min(1.0, sp_scroll)) * S(68)))

        # A) ÖNCEKİ DİZE (Üstte soluk gri, %20 büyütülmüş punto: 24 -> 29)
        if active_idx > 0:
            prev_ev = events[active_idx - 1]
            f_prev_tr = get_script_font(prev_ev["tr"], 29, bold=True)
            _draw_karaoke_word_block(
                draw=draw,
                words_list=prev_ev["tr_words"],
                t=t,
                center_x=W // 2,
                start_y=S(940) + slide_offset_y // 2,
                font=f_prev_tr,
                max_width_px=W - S(130),
                line_step_px=S(52),
                accent_rgb=accent_rgb,
                accent_soft_rgb=accent_soft_rgb,
                is_hero_turkish=True,
                global_alpha=0.28,
            )

        # B) ŞU AN SÖYLENEN AKTİF DİZE (Merkez Sahne — Orijinal Söz + Türkçe Çeviri Kelime Kelime Karaoke!)
        active_top_y = S(1110) + slide_offset_y

        # B.1: Orijinal Şarkı Sözü (%20 büyütülmüş punto: 28 -> 34)
        f_orig_active = get_script_font(cur_ev["orig"], 34, bold=True)
        after_orig_y = _draw_karaoke_word_block(
            draw=draw,
            words_list=cur_ev["orig_words"],
            t=t,
            center_x=W // 2,
            start_y=active_top_y,
            font=f_orig_active,
            max_width_px=W - S(110),
            line_step_px=S(66),
            accent_rgb=accent_rgb,
            accent_soft_rgb=accent_soft_rgb,
            is_hero_turkish=False,
            global_alpha=1.0,
        )

        # B.2: Okunuş (Varsa ve orijinalden farklıysa, %20 büyütülmüş punto: 18 -> 22)
        pron_str = _strip_canvas_emojis(cur_ev.get("pron", ""))
        if pron_str:
            f_pron = get_script_font(pron_str, 22, bold=False)
            draw.text(
                (W // 2, after_orig_y + S(14)),
                f"({pron_str})",
                fill=(136, 136, 146, 255),
                font=f_pron,
                anchor="mm",
            )
            after_orig_y += S(58)
        else:
            after_orig_y += S(26)

        # İnce zarif vurgu noktası / çizgi
        draw.rounded_rectangle(
            (W // 2 - S(42), after_orig_y, W // 2 + S(42), after_orig_y + S(6)),
            radius=S(3),
            fill=accent_rgb + (220,),
        )

        # B.3: ANA ODAK — TERTEMİZ TÜRKÇE ÇEVİRİ (%20 büyütülmüş punto: 38 -> 46!)
        f_tr_active = get_script_font(cur_ev["tr"], 46, bold=True)
        after_tr_y = _draw_karaoke_word_block(
            draw=draw,
            words_list=cur_ev["tr_words"],
            t=t,
            center_x=W // 2,
            start_y=after_orig_y + S(72),
            font=f_tr_active,
            max_width_px=W - S(100),
            line_step_px=S(90),
            accent_rgb=accent_rgb,
            accent_soft_rgb=accent_soft_rgb,
            is_hero_turkish=True,
            global_alpha=1.0,
        )

        # C) SIRADAKİ DİZE (%20 büyütülmüş punto: 21 -> 25 ve 25 -> 30)
        if active_idx + 1 < len(events):
            next_ev = events[active_idx + 1]
            next_y = max(after_tr_y + S(75), S(1680))
            f_next_orig = get_script_font(next_ev["orig"], 25, bold=False)
            f_next_tr = get_script_font(next_ev["tr"], 30, bold=True)

            y_n1 = _draw_karaoke_word_block(
                draw=draw,
                words_list=next_ev["orig_words"],
                t=t,
                center_x=W // 2,
                start_y=next_y,
                font=f_next_orig,
                max_width_px=W - S(130),
                line_step_px=S(46),
                accent_rgb=accent_rgb,
                accent_soft_rgb=accent_soft_rgb,
                is_hero_turkish=False,
                global_alpha=0.25,
            )
            _draw_karaoke_word_block(
                draw=draw,
                words_list=next_ev["tr_words"],
                t=t,
                center_x=W // 2,
                start_y=y_n1 + S(14),
                font=f_next_tr,
                max_width_px=W - S(120),
                line_step_px=S(52),
                accent_rgb=accent_rgb,
                accent_soft_rgb=accent_soft_rgb,
                is_hero_turkish=True,
                global_alpha=0.30,
            )

        frame_rgb = apply_editorial_paper_film_grain(canvas.convert("RGB"), frame_idx=f_idx)

        frame_path = os.path.join(frames_dir, f"frame_{f_idx:04d}.jpg")
        frame_rgb.save(frame_path, "JPEG", quality=95)

    # Paylaşımlarda kullanılacak şarkıya özel FARKLI DİKEY KAPAK RESMİ (9:16, 1440x2560) üret
    vertical_cover_path = os.path.join(out_dir, "vertical_cover_9x16.jpg")
    render_songtrai_vertical_cover_9x16(
        song=song,
        album_cover=album_cover,
        accent_info=accent_info,
        deck_type=deck_type,
        output_jpg_path=vertical_cover_path,
    )
    hook_cover_path = os.path.join(out_dir, "hook_cover.jpg")
    shutil.copyfile(vertical_cover_path, hook_cover_path)

    ffmpeg_exe = get_ffmpeg_exe()
    cmd = [
        ffmpeg_exe,
        "-y",
        "-framerate", str(FPS),
        "-i", os.path.join(frames_dir, "frame_%04d.jpg"),
        "-i", wav_path,
        "-vf", "unsharp=5:5:0.65:3:3:0.0,format=yuv420p",
        "-c:v", "libx264",
        "-preset", "slow",
        "-profile:v", "high",
        "-level:v", "5.1",
        "-crf", "12",
        "-b:v", "22M",
        "-maxrate", "30M",
        "-bufsize", "45M",
        "-pix_fmt", "yuv420p",
        "-color_primaries", "bt709",
        "-color_trc", "bt709",
        "-colorspace", "bt709",
        "-c:a", "aac",
        "-b:a", "320k",
        "-ar", "44100",
        "-ac", "2",
        "-shortest",
        "-movflags", "+faststart",
        output_mp4,
    ]
    subprocess.run(cmd, check=True)
    shutil.rmtree(frames_dir, ignore_errors=True)

    return {
        "video_path": output_mp4,
        "hook_cover_path": hook_cover_path,
        "vertical_cover_path": vertical_cover_path,
        "duration_sec": total_duration,
        "resolution": f"{W}x{H}",
        "fps": FPS,
        "deck_type": deck_type,
        "accent_color": accent_info["name"],
        "synced_lines_count": len(events),
        "real_audio_used": bool(sync_data.get("raw_audio_path")),
    }
