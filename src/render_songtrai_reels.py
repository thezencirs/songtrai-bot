# -*- coding: utf-8 -*-
"""
Şarkıların Anlamı (@songtraibot) — 2K QHD+ (1440x2560 @ 30 FPS) Saf Beyaz Stüdyo & GraphMotion Reels Motoru
===========================================================================================================
- %100 Saf Beyaz Sonsuz Fon Fotoğraf Stüdyosu (#FFFFFF -> #F6F3EC) • Sıfır Uzay / Sıfır Yapay Zeka İzi!
- Gerçek resmi 1000x1000 HD albüm kapağı + dönen 12-inç vinil plak diski + fiziksel temas gölgesi.
- Remotion Yay Fiziği (`damping=14, stiffness=120, mass=0.8`) + 180° Obtüratör Hareket Bulanıklığı.
- 10 Dil (İngilizce, Rusça, Japonca, Almanca, İspanyolca, Korece, Çince, İtalyanca, Fransızca, Hintçe)
  ve tüm alfabeler (Latin, Kiril, Kanji/Kana, Hangul, Hanzi, Devanagari, Türkçe) için sıfır kutucuklu (zero-tofu)
  akıllı Unicode font motoru ve satır-satır altın vurgulu tertemiz edebi Türkçe çeviri akışı.
"""

import math
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from studio_vinyl_audio_engine import generate_studio_vinyl_soundtrack
from white_studio_optics import (
    apply_editorial_paper_film_grain,
    apply_organic_camera_breathing,
    apply_studio_contact_shadow_card,
    fetch_official_album_artwork,
    render_vinyl_record_disc,
)

W, H = 1440, 2560
SCALE = W / 1080.0
FPS = 30

_FONT_CACHE: Dict[Tuple[str, int, bool, bool], ImageFont.FreeTypeFont] = {}


def S(val: float) -> int:
    return int(round(val * SCALE))


def _remotion_spring(
    t: float,
    damping: float = 14.0,
    stiffness: float = 120.0,
    mass: float = 0.8,
) -> float:
    """
    Remotion `spring({ frame, fps, config: { damping: 14, stiffness: 120, mass: 0.8 } })`
    harmonik salınım çözücüsü.
    """
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
    return float(max(0.0, min(1.08, val)))


def _apply_180deg_shutter_blur(card_im: Image.Image, speed_px: float) -> Image.Image:
    if speed_px < 20.0:
        return card_im
    radius = min(4.2, speed_px / 70.0)
    return card_im.filter(ImageFilter.GaussianBlur(radius=radius))


def _apply_warm_studio_light_sweep(
    frame_rgb: Image.Image,
    intensity: float,
    sweep_pos: float = 0.5,
) -> Image.Image:
    """Sahne geçişlerinde saf beyaz stüdyo üzerinde sıcak şampanya gün ışığı yansıması."""
    if intensity <= 0.01:
        return frame_rgb
    arr = np.array(frame_rgb, dtype=np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    nx = xx / float(W)
    ny = yy / float(H)
    diag = nx * 0.75 + ny * 0.25
    band = np.exp(-((diag - sweep_pos) ** 2) / 0.035) * float(intensity)
    arr[:, :, 0] = np.clip(arr[:, :, 0] + band * 185.0, 0.0, 255.0)
    arr[:, :, 1] = np.clip(arr[:, :, 1] + band * 148.0, 0.0, 255.0)
    arr[:, :, 2] = np.clip(arr[:, :, 2] + band * 88.0, 0.0, 255.0)
    return Image.fromarray(arr.astype(np.uint8), mode="RGB")


def get_ffmpeg_exe() -> str:
    sys_ff = shutil.which("ffmpeg")
    if sys_ff:
        return sys_ff
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def _detect_script_family(text: str) -> str:
    for ch in (text or ""):
        cp = ord(ch)
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
    """
    Metindeki alfabeyi (Latin/Türkçe/Kiril, Japonca Kanji/Kana, Korece Hangul, Çince Hanzi,
    Hintçe Devanagari) otomatik algılar ve hem Windows hem Ubuntu (GitHub Actions) üzerinde
    tam karşılığı olan Unicode fontunu yükler.
    """
    script = _detect_script_family(text)
    size = S(size_1080)
    cache_key = (script, size, bold, serif)
    if cache_key in _FONT_CACHE:
        return _FONT_CACHE[cache_key]

    if script == "ko":
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


def _strip_canvas_emojis(s: str) -> str:
    """Video tuvali üzerinde TrueType fontlarda kutucuk (□) oluşturabilecek renkli emojileri temizler."""
    out_chars = []
    for ch in (s or ""):
        cp = ord(ch)
        if cp >= 0x1F000 or (0x2600 <= cp <= 0x27BF) or cp == 0xFE0F:
            continue
        out_chars.append(ch)
    import re
    return re.sub(r"\s+", " ", "".join(out_chars)).strip()


def _tr_upper(s: str) -> str:
    return _strip_canvas_emojis(s or "").replace("i", "İ").replace("ı", "I").upper()


def _text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0]
    except Exception:
        return len(text) * S(16)


def wrap_text_pixel(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width_px: int,
    max_lines: int = 3,
) -> List[str]:
    """
    Piksel genişliğine göre hem boşluklu dilleri (Türkçe, İngilizce, Rusça, Fransızca, İspanyolca,
    Almanca, İtalyanca, Hintçe) hem de boşluksuz CJK dillerini (Japonca, Çince) taşmadan sarar.
    """
    clean = (text or "").strip()
    if not clean:
        return [""]

    has_spaces = " " in clean
    lines: List[str] = []

    if has_spaces:
        words = clean.split()
        cur = ""
        for w in words:
            cand = f"{cur} {w}".strip() if cur else w
            if _text_width(draw, cand, font) <= max_width_px:
                cur = cand
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
    else:
        cur = ""
        for ch in clean:
            cand = cur + ch
            if _text_width(draw, cand, font) <= max_width_px:
                cur = cand
            else:
                if cur:
                    lines.append(cur)
                cur = ch
        if cur:
            lines.append(cur)

    return lines[:max_lines] if lines else [clean]


def create_pure_white_studio_stage() -> Image.Image:
    """
    2K (1440x2560) çözünürlükte Saf Beyaz Sonsuz Fon Fotoğraf Stüdyosu (#FFFFFF -> #F6F3EC)
    ve çift katmanlı 18K Şampanya Altın editoryal çerçeve oluşturur.
    Kesinlikle uzay, karanlık veya yapay zeka izi içermez.
    """
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    nx = (xx - W * 0.5) / (W * 0.65)
    ny = (yy - H * 0.45) / (H * 0.62)
    dist = np.clip(np.sqrt(nx * nx + ny * ny), 0.0, 1.35) / 1.35
    smooth = dist * dist * (3.0 - 2.0 * dist)

    r_ch = (255.0 - 9.0 * smooth).astype(np.uint8)
    g_ch = (255.0 - 12.0 * smooth).astype(np.uint8)
    b_ch = (255.0 - 18.0 * smooth).astype(np.uint8)
    a_ch = np.full((H, W), 255, dtype=np.uint8)
    bg = Image.fromarray(np.dstack([r_ch, g_ch, b_ch, a_ch]), mode="RGBA")

    draw = ImageDraw.Draw(bg)
    # Dış ve iç 18K Şampanya Altın stüdyo çerçevesi
    draw.rounded_rectangle(
        (S(18), S(18), W - S(18), H - S(18)),
        radius=S(28),
        outline=(197, 160, 89, 235),
        width=S(3),
    )
    draw.rounded_rectangle(
        (S(28), S(28), W - S(28), H - S(28)),
        radius=S(22),
        outline=(197, 160, 89, 120),
        width=S(1),
    )
    return bg


def _draw_pill(
    draw: ImageDraw.ImageDraw,
    cx: int,
    cy: int,
    text: str,
    font: ImageFont.FreeTypeFont,
    fill_rgba: tuple,
    text_rgba: tuple,
    pad_x: int,
    pad_y: int,
    radius: int,
    outline_rgba: tuple = None,
    outline_width: int = 0,
) -> None:
    tw = _text_width(draw, text, font)
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        th = bbox[3] - bbox[1]
    except Exception:
        th = S(26)
    half_w = min((W - S(52)) // 2, (tw // 2) + pad_x)
    half_h = (th // 2) + pad_y
    rect = (cx - half_w, cy - half_h, cx + half_w, cy + half_h)
    draw.rounded_rectangle(rect, radius=radius, fill=fill_rgba, outline=outline_rgba, width=outline_width)
    draw.text((cx, cy), text, fill=text_rgba, font=font, anchor="mm")


def _make_framed_album_sleeve(album_cover: Image.Image, sleeve_size: int) -> Image.Image:
    """Gerçek albüm kapağını beyaz-altın plak zarfı ve fiziksel stüdyo gölgesiyle hazırlar."""
    card = Image.new("RGBA", (sleeve_size, sleeve_size), (0, 0, 0, 0))
    cdraw = ImageDraw.Draw(card)
    cdraw.rounded_rectangle(
        (0, 0, sleeve_size - 1, sleeve_size - 1),
        radius=S(22),
        fill=(255, 255, 255, 255),
        outline=(197, 160, 89, 245),
        width=S(4),
    )
    inner_pad = S(12)
    cov_resized = album_cover.resize(
        (sleeve_size - inner_pad * 2, sleeve_size - inner_pad * 2),
        Image.Resampling.LANCZOS,
    )
    mask = Image.new("L", cov_resized.size, 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.rounded_rectangle((0, 0, cov_resized.width - 1, cov_resized.height - 1), radius=S(14), fill=255)
    card.paste(cov_resized, (inner_pad, inner_pad), mask)
    return apply_studio_contact_shadow_card(card, elevation_px=S(12))


def _build_bento_stanza_card(
    stanza: Dict[str, str],
    idx: int,
    lang_code: str,
    lang_tr: str,
    card_w: int,
    card_h: int,
) -> Image.Image:
    """
    Perde II (1.45s - 4.20s) için Saf Beyaz Stüdyo 4'lü Nakarat Bento Kartı oluşturur.
    """
    card = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)
    draw.rounded_rectangle(
        (0, 0, card_w - 1, card_h - 1),
        radius=S(24),
        fill=(255, 255, 255, 252),
        outline=(197, 160, 89, 235),
        width=S(3),
    )
    draw.rounded_rectangle(
        (S(8), S(8), card_w - S(9), card_h - S(9)),
        radius=S(18),
        outline=(197, 160, 89, 105),
        width=S(1),
    )

    f_badge = get_script_font("DİZE", 16, bold=True)
    orig_txt = stanza.get("orig", "")
    tr_txt = stanza.get("tr", "")
    f_orig = get_script_font(orig_txt, 19, bold=False)
    f_tr = get_script_font(tr_txt, 23, bold=True, serif=True)

    # Sol üst altın numara rozeti
    draw.rounded_rectangle(
        (S(20), S(18), S(168), S(54)),
        radius=S(11),
        fill=(197, 160, 89, 255),
    )
    draw.text((S(94), S(36)), f"DİZE 0{idx} • {lang_code}", fill=(255, 255, 255, 255), font=f_badge, anchor="mm")

    # Sağ üst Türkçe Çeviri etiketi
    draw.rounded_rectangle(
        (card_w - S(235), S(18), card_w - S(20), S(54)),
        radius=S(11),
        fill=(248, 244, 236, 255),
        outline=(197, 160, 89, 180),
        width=S(1),
    )
    draw.text(
        (card_w - S(127), S(36)),
        f"{_tr_upper(lang_tr)} -> TÜRKÇE",
        fill=(142, 104, 36, 255),
        font=f_badge,
        anchor="mm",
    )

    # Orijinal söz (üst satır)
    orig_lines = wrap_text_pixel(draw, f"“{orig_txt}”", f_orig, card_w - S(64), max_lines=2)
    y_orig = S(82)
    for o_ln in orig_lines:
        draw.text((card_w // 2, y_orig), o_ln, fill=(96, 88, 78, 255), font=f_orig, anchor="mm")
        y_orig += S(30)

    # İnce altın ayırıcı çizgi
    div_y = S(146)
    draw.line([(S(48), div_y), (card_w - S(48), div_y)], fill=(218, 196, 148, 190), width=S(2))

    # Alt kısım: Tertemiz Edebi Türkçe Çeviri (Altın vurgu kutusu içinde)
    draw.rounded_rectangle(
        (S(20), S(160), card_w - S(20), card_h - S(18)),
        radius=S(16),
        fill=(251, 248, 241, 255),
        outline=(197, 160, 89, 165),
        width=S(1),
    )
    tr_lines = wrap_text_pixel(draw, f"“{tr_txt}”", f_tr, card_w - S(76), max_lines=2)
    y_tr = S(198) if len(tr_lines) == 2 else S(215)
    for t_ln in tr_lines:
        draw.text((card_w // 2, y_tr), t_ln, fill=(18, 16, 22, 255), font=f_tr, anchor="mm")
        y_tr += S(38)

    return apply_studio_contact_shadow_card(card, elevation_px=S(9))


def _render_spotlight_hero_card(
    stanza: Dict[str, str],
    stanza_idx: int,
    total_stanzas: int,
    song: Dict[str, Any],
    highlight_progress: float,
) -> Image.Image:
    """
    Perde III (4.20s - 14.40s) için tam odak Satır-Satır Kinetik Türkçe Çeviri Spotlight Kartı:
    1) Orijinal Söz (kendi dilinde/alfabesinde)
    2) Okunuş Rehberi (Fonetik)
    3) TERTEMİZ EDEBİ TÜRKÇE ÇEVİRİ (Dinamik Şampanya Altın Fosforlu Vurgu Akışı ile)
    4) Dizenin Derin Duygusal Alt Anlam Notu
    """
    cw, ch = S(984), S(965)
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)

    # Saf Beyaz Dergi Kartı Gövdesi + Çift Katmanlı 18K Altın Çerçeve
    draw.rounded_rectangle(
        (0, 0, cw - 1, ch - 1),
        radius=S(34),
        fill=(255, 255, 255, 254),
        outline=(197, 160, 89, 248),
        width=S(4),
    )
    draw.rounded_rectangle(
        (S(12), S(12), cw - S(13), ch - S(13)),
        radius=S(26),
        outline=(197, 160, 89, 120),
        width=S(1),
    )

    lang_tr = _tr_upper(song.get("language_tr", "İNGİLİZCE"))
    lang_code = song.get("language_code", "EN")
    orig_txt = stanza.get("orig", "")
    pron_txt = stanza.get("pron", "")
    tr_txt = stanza.get("tr", "")
    note_txt = stanza.get("note", "")

    f_kicker = get_script_font("DİZE", 18, bold=True)
    f_orig = get_script_font(orig_txt, 26, bold=True)
    f_pron = get_script_font(pron_txt, 19, bold=False)
    f_tr_hero = get_script_font(tr_txt, 35, bold=True, serif=True)
    f_note_lbl = get_script_font("DERİN ANLAMI", 16, bold=True)
    f_note = get_script_font(note_txt, 19, bold=False)

    # 1. Üst Başlık Rozeti
    _draw_pill(
        draw,
        cw // 2,
        S(52),
        f"DİZE 0{stanza_idx} / 0{total_stanzas}  •  {lang_code} ({lang_tr} ORİJİNAL SÖZ)",
        f_kicker,
        (248, 244, 236, 255),
        (142, 104, 36, 255),
        S(28),
        S(11),
        S(18),
        (197, 160, 89, 210),
        S(2),
    )

    # 2. Orijinal Dize
    orig_lines = wrap_text_pixel(draw, f"“{orig_txt}”", f_orig, cw - S(86), max_lines=3)
    y_orig = S(118) if len(orig_lines) <= 2 else S(104)
    for o_ln in orig_lines:
        draw.text((cw // 2, y_orig), o_ln, fill=(44, 40, 36, 255), font=f_orig, anchor="mm")
        y_orig += S(40)

    # 3. Okunuş Rehberi (Fonetik Kutusu)
    pron_y = S(238)
    draw.rounded_rectangle(
        (S(46), pron_y - S(26), cw - S(46), pron_y + S(26)),
        radius=S(14),
        fill=(250, 246, 238, 255),
        outline=(216, 192, 142, 180),
        width=S(1),
    )
    pron_clean = f"OKUNUŞU:  “{pron_txt}”"
    if _text_width(draw, pron_clean, f_pron) > cw - S(110):
        f_pron_sm = get_script_font(pron_txt, 16, bold=False)
        draw.text((cw // 2, pron_y), pron_clean, fill=(132, 96, 34, 255), font=f_pron_sm, anchor="mm")
    else:
        draw.text((cw // 2, pron_y), pron_clean, fill=(132, 96, 34, 255), font=f_pron, anchor="mm")

    # 4. Şampanya Altın Ayırıcı + "TÜRKÇE EDEBİ ÇEVİRİSİ" Rozeti
    div_y = S(308)
    draw.line([(S(56), div_y), (cw - S(56), div_y)], fill=(197, 160, 89, 220), width=S(2))
    _draw_pill(
        draw,
        cw // 2,
        div_y,
        "» TERTEMİZ TÜRKÇE ÇEVİRİSİ «",
        f_kicker,
        (197, 160, 89, 255),
        (255, 255, 255, 255),
        S(26),
        S(9),
        S(16),
    )

    # 5. ANA ODAK: TERTEMİZ TÜRKÇE ÇEVİRİ + Dinamik Altın Fosforlu Vurgu (Highlighter Sweep)
    tr_box_top, tr_box_bot = S(348), S(718)
    draw.rounded_rectangle(
        (S(32), tr_box_top, cw - S(32), tr_box_bot),
        radius=S(24),
        fill=(253, 251, 247, 255),
        outline=(197, 160, 89, 210),
        width=S(2),
    )

    tr_lines = wrap_text_pixel(draw, f"“{tr_txt}”", f_tr_hero, cw - S(108), max_lines=4)
    line_step = S(62)
    total_tr_h = (len(tr_lines) - 1) * line_step
    start_tr_y = (tr_box_top + tr_box_bot) // 2 - total_tr_h // 2

    prog = max(0.0, min(1.0, highlight_progress))
    for l_idx, t_ln in enumerate(tr_lines):
        ly = start_tr_y + l_idx * line_step
        lw = _text_width(draw, t_ln, f_tr_hero)
        # Satır bazlı kademeli altın vurgu şeridi (izleyicinin gözünü satır boyunca taşır)
        line_start_p = l_idx / max(1.0, float(len(tr_lines)))
        line_end_p = (l_idx + 1) / max(1.0, float(len(tr_lines)))
        local_p = max(0.0, min(1.0, (prog - line_start_p * 0.7) / max(0.25, (line_end_p - line_start_p * 0.7))))
        if local_p > 0.02:
            hl_w = int((lw + S(24)) * local_p)
            hl_left = (cw - (lw + S(24))) // 2
            draw.rounded_rectangle(
                (hl_left, ly - S(24), hl_left + hl_w, ly + S(24)),
                radius=S(10),
                fill=(246, 226, 178, 185),
            )
        draw.text((cw // 2, ly), t_ln, fill=(16, 14, 20, 255), font=f_tr_hero, anchor="mm")

    # 6. Alt Kutu: Duygusal & Kültürel Alt Anlam Notu
    note_top, note_bot = S(742), ch - S(28)
    draw.rounded_rectangle(
        (S(32), note_top, cw - S(32), note_bot),
        radius=S(20),
        fill=(246, 241, 231, 255),
        outline=(197, 160, 89, 195),
        width=S(2),
    )
    _draw_pill(
        draw,
        cw // 2,
        note_top + S(28),
        "BU DİZENİN HİKAYESİ & DERİN ANLAMI",
        f_note_lbl,
        (24, 20, 26, 255),
        (242, 214, 158, 255),
        S(22),
        S(7),
        S(12),
    )
    note_lines = wrap_text_pixel(draw, note_txt, f_note, cw - S(104), max_lines=3)
    ny_start = note_top + S(82) if len(note_lines) <= 2 else note_top + S(70)
    for n_ln in note_lines:
        draw.text((cw // 2, ny_start), n_ln, fill=(54, 48, 42, 255), font=f_note, anchor="mm")
        ny_start += S(32)

    return apply_studio_contact_shadow_card(card, elevation_px=S(12))


def generate_hook_cover_and_story_card(
    song: Dict[str, Any],
    album_cover: Image.Image,
    out_dir: str,
) -> Image.Image:
    """
    1) `output/hook_cover.jpg`: Perde I (0.00s - 1.45s) ve Instagram Reels Kapak Fotoğrafı
    2) `output/song_story_collage.jpg`: 9:16 Saf Beyaz Stüdyo 4'lü Şarkı Sözü Özeti
    """
    stage = create_pure_white_studio_stage()
    draw = ImageDraw.Draw(stage)

    lang_tr = _tr_upper(song.get("language_tr", "İNGİLİZCE"))
    lang_code = song.get("language_code", "EN")
    artist = song.get("artist", "Artist")
    title = song.get("title", "Song")
    year = song.get("release_year", "")
    kicker = _tr_upper(song.get("cover_kicker", f"{lang_tr} POPÜLER ŞARKI • TÜRKÇE ÇEVİRİ"))
    headline = _tr_upper(song.get("cover_headline", f"{artist} - {title} TÜRKÇE ANLAMI"))
    hook_txt = song.get("viral_hook", "")
    ts_txt = song.get("chorus_timestamp", "0:42 - 0:57")

    f_crest = get_script_font("SONGTRAIBOT", 17, bold=True)
    f_kicker = get_script_font(kicker, 21, bold=True)
    f_artist = get_script_font(artist, 28, bold=True)
    f_title = get_script_font(title, 36, bold=True, serif=True)
    f_head = get_script_font(headline, 31, bold=True, serif=True)
    f_hook = get_script_font(hook_txt, 21, bold=False)
    f_sub = get_script_font("NAKARAT", 19, bold=True)

    _draw_pill(
        draw,
        W // 2,
        S(82),
        f"ŞARKILARIN ANLAMI (@SONGTRAIBOT)  •  SAF BEYAZ STÜDYO EDİSYONU",
        f_crest,
        (255, 255, 255, 250),
        (22, 18, 24, 255),
        S(26),
        S(9),
        S(16),
        (197, 160, 89, 235),
        S(2),
    )
    _draw_pill(
        draw,
        W // 2,
        S(142),
        f"» {lang_code} • {kicker[:44]} «",
        f_kicker,
        (197, 160, 89, 255),
        (255, 255, 255, 255),
        S(28),
        S(11),
        S(20),
    )

    # Merkez Plak & Albüm Zarfı Kompozisyonu (Saf Beyaz Stüdyo Üzerinde Gerçek Albüm Kapağı + Vinil Plak)
    sleeve_sz = S(520)
    vinyl_d = S(490)
    vinyl_im = render_vinyl_record_disc(album_cover, diameter=vinyl_d, angle_deg=18.0)
    sleeve_im = _make_framed_album_sleeve(album_cover, sleeve_size=sleeve_sz)

    # Plak sağda, albüm kapağı solda
    stage.paste(vinyl_im, (S(465), S(225)), vinyl_im)
    stage.paste(sleeve_im, (S(115), S(210)), sleeve_im)

    # Şarkı Kimlik & Hikaye Kutusu
    box_top, box_bot = S(785), S(1620)
    draw.rounded_rectangle(
        (S(46), box_top, W - S(46), box_bot),
        radius=S(34),
        fill=(255, 255, 255, 252),
        outline=(197, 160, 89, 248),
        width=S(3),
    )
    draw.rounded_rectangle(
        (S(58), box_top + S(12), W - S(58), box_bot - S(12)),
        radius=S(26),
        outline=(197, 160, 89, 115),
        width=S(1),
    )

    _draw_pill(
        draw,
        W // 2,
        box_top + S(54),
        f"{_tr_upper(artist)}  •  {year}",
        f_artist,
        (248, 244, 236, 255),
        (142, 104, 36, 255),
        S(30),
        S(10),
        S(18),
        (197, 160, 89, 200),
        S(2),
    )

    title_lines = wrap_text_pixel(draw, f"“{title}”", f_title, W - S(160), max_lines=2)
    ty = box_top + S(125)
    for t_ln in title_lines:
        draw.text((W // 2, ty), t_ln, fill=(18, 16, 22, 255), font=f_title, anchor="mm")
        ty += S(46)

    div_y = box_top + S(210)
    draw.line([(S(95), div_y), (W - S(95), div_y)], fill=(197, 160, 89, 210), width=S(2))

    # Vurucu Başlık
    head_lines = wrap_text_pixel(draw, headline, f_head, W - S(150), max_lines=3)
    hy = box_top + S(268)
    for h_ln in head_lines:
        draw.text((W // 2, hy), h_ln, fill=(18, 16, 22, 255), font=f_head, anchor="mm")
        hy += S(48)

    # Şarkının Hikayesi (Alt Kutu)
    story_top = box_top + S(435)
    draw.rounded_rectangle(
        (S(78), story_top, W - S(78), box_bot - S(95)),
        radius=S(22),
        fill=(250, 246, 238, 255),
        outline=(197, 160, 89, 175),
        width=S(1),
    )
    hook_lines = wrap_text_pixel(draw, hook_txt, f_hook, W - S(210), max_lines=5)
    hky = story_top + S(48)
    for hk_ln in hook_lines:
        draw.text((W // 2, hky), hk_ln, fill=(52, 46, 40, 255), font=f_hook, anchor="mm")
        hky += S(36)

    _draw_pill(
        draw,
        W // 2,
        box_bot - S(46),
        f"» EKLENECEK MÜZİK ARALIĞI: {ts_txt} «",
        f_sub,
        (20, 18, 24, 255),
        (242, 214, 158, 255),
        S(28),
        S(11),
        S(18),
    )

    # En Alt Çağrı Bandı
    _draw_pill(
        draw,
        W // 2,
        S(1725),
        "» SATIR SATIR TÜRKÇE ÇEVİRİ AKIŞI BAŞLIYOR «",
        f_kicker,
        (197, 160, 89, 255),
        (255, 255, 255, 255),
        S(32),
        S(13),
        S(22),
    )

    rgb_cover = stage.convert("RGB")
    os.makedirs(out_dir, exist_ok=True)
    rgb_cover.save(os.path.join(out_dir, "hook_cover.jpg"), "JPEG", quality=97, subsampling=0)
    return rgb_cover


def render_songtrai_graphmotion_reel(
    song: Dict[str, Any],
    output_mp4: str,
) -> Dict[str, Any]:
    """
    2K QHD+ (1440x2560 @ 30 FPS) Saf Beyaz Stüdyo & GraphMotion Şarkı Çeviri Videosunu üretir:
    - Perde I (0.00s - 1.45s): Saf Beyaz Stüdyo Plak & Şarkı Kimliği Kancası
    - Perde II (1.45s - 4.20s): 4'lü Nakarat GraphMotion Bento Özeti (Remotion Spring Physics)
    - Perde III (4.20s - 14.40s): Satır Satır Kinetik Türkçe Çeviri Spotlight Akışı (4 Dize x 2.55s)
    """
    out_dir = os.path.dirname(output_mp4) or "output"
    os.makedirs(out_dir, exist_ok=True)
    frames_dir = os.path.join(out_dir, "_songtrai_frames")
    shutil.rmtree(frames_dir, ignore_errors=True)
    os.makedirs(frames_dir, exist_ok=True)

    bg_stage = create_pure_white_studio_stage()
    album_cover = fetch_official_album_artwork(song, size=900)
    hook_cover_rgb = generate_hook_cover_and_story_card(song, album_cover, out_dir=out_dir)

    stanzas = (song.get("stanzas") or [])[:4]
    lang_code = song.get("language_code", "EN")
    lang_tr = song.get("language_tr", "İngilizce")
    artist = song.get("artist", "Artist")
    title = song.get("title", "Song")

    # Perde II için 4 Bento Kartını önceden hazırla
    bento_w, bento_h = S(984), S(285)
    bento_cards: List[Dict[str, Any]] = []
    for idx, st in enumerate(stanzas, start=1):
        c_im = _build_bento_stanza_card(st, idx, lang_code, lang_tr, bento_w, bento_h)
        target_x = (W - bento_w) // 2
        target_y = S(305) + (idx - 1) * S(320)
        start_x = -bento_w - S(60) if idx % 2 == 1 else W + S(60)
        bento_cards.append({
            "card_im": c_im,
            "target_xy": (target_x, target_y),
            "start_xy": (start_x, target_y - S(30)),
            "t_in": 1.45 + (idx - 1) * 0.26,
        })

    # Perde II & III için üst stüdyo albüm kapağı mini zarfı
    mini_sleeve = _make_framed_album_sleeve(album_cover, sleeve_size=S(230))
    spot_sleeve = _make_framed_album_sleeve(album_cover, sleeve_size=S(290))

    f_hdr_kicker = get_script_font("ŞARKILARIN ANLAMI", 16, bold=True)
    f_hdr_title = get_script_font(title, 26, bold=True, serif=True)
    f_hdr_artist = get_script_font(artist, 20, bold=True)
    f_step = get_script_font("DİZE 01", 17, bold=True)
    f_cta = get_script_font("KAYDET", 19, bold=True)

    total_duration = 14.4
    total_frames = int(total_duration * FPS)
    act1_end = 1.45
    act2_end = 4.20
    stanza_dur = (total_duration - act2_end) / max(1, len(stanzas))

    for f_idx in range(total_frames):
        t = f_idx / float(FPS)

        # =====================================================================
        # PERDE I (0.00s - 1.45s): SAF BEYAZ STÜDYO PLAK & ŞARKI KİMLİĞİ KANCASI
        # =====================================================================
        if t < act1_end:
            frame_rgb = apply_organic_camera_breathing(hook_cover_rgb, t=t, stage_idx=0)

        # =====================================================================
        # PERDE II (1.45s - 4.20s): 4'LÜ NAKARAT GRAPHMOTION BENTO ÖZETİ
        # =====================================================================
        elif t < act2_end:
            canvas = bg_stage.copy()
            cdraw = ImageDraw.Draw(canvas)

            # Üst Kompakt Saf Beyaz Stüdyo Şarkı Başlığı Barı
            cdraw.rounded_rectangle(
                (S(48), S(54), W - S(48), S(268)),
                radius=S(24),
                fill=(255, 255, 255, 252),
                outline=(197, 160, 89, 235),
                width=S(3),
            )
            canvas.paste(mini_sleeve, (S(68), S(46)), mini_sleeve)

            tx_center = S(640)
            _draw_pill(
                cdraw,
                tx_center,
                S(98),
                f"{lang_code} • {_tr_upper(lang_tr)} POPÜLER ŞARKI • 4 ANA DİZE",
                f_hdr_kicker,
                (197, 160, 89, 255),
                (255, 255, 255, 255),
                S(22),
                S(7),
                S(13),
            )
            cdraw.text(
                (tx_center, S(158)),
                f"{artist} — “{title[:24]}”",
                fill=(18, 16, 22, 255),
                font=f_hdr_title,
                anchor="mm",
            )
            cdraw.text(
                (tx_center, S(214)),
                f"Sosyal Medya Ses Aralığı: {song.get('chorus_timestamp', '0:42 - 0:57')}",
                fill=(142, 104, 36, 255),
                font=f_hdr_artist,
                anchor="mm",
            )

            # 4 Bento Kartının Remotion Yay Fiziği + 180° Shutter Motion Blur ile Sahneye Girişi
            for b_item in bento_cards:
                t_in = b_item["t_in"]
                if t < t_in:
                    continue
                dt = t - t_in
                dt_prev = max(0.0, dt - (1.0 / float(FPS)))
                sp_now = _remotion_spring(dt, damping=14.0, stiffness=120.0, mass=0.8)
                sp_prev = _remotion_spring(dt_prev, damping=14.0, stiffness=120.0, mass=0.8)

                tx, ty = b_item["target_xy"]
                sx, sy = b_item["start_xy"]
                cur_x = int(round(sx + (tx - sx) * sp_now))
                cur_y = int(round(sy + (ty - sy) * sp_now))
                prev_x = int(round(sx + (tx - sx) * sp_prev))
                prev_y = int(round(sy + (ty - sy) * sp_prev))

                speed_px = math.hypot(cur_x - prev_x, cur_y - prev_y)
                card_vis = _apply_180deg_shutter_blur(b_item["card_im"], speed_px)
                canvas.paste(card_vis, (cur_x, cur_y), card_vis)

            _draw_pill(
                cdraw,
                W // 2,
                S(1655),
                "» ŞİMDİ HER DİZENİN DERİN TÜRKÇE ANLAMINA GEÇİYORUZ «",
                f_cta,
                (20, 18, 24, 255),
                (242, 214, 158, 255),
                S(30),
                S(12),
                S(20),
            )
            frame_rgb = apply_organic_camera_breathing(canvas.convert("RGB"), t=t, stage_idx=1)

        # =====================================================================
        # PERDE III (4.20s - 14.40s): SATIR SATIR KİNETİK TÜRKÇE ÇEVİRİ SPOTLIGHT
        # =====================================================================
        else:
            rel_t = t - act2_end
            s_idx = min(len(stanzas) - 1, int(rel_t // stanza_dur))
            local_t = rel_t - (s_idx * stanza_dur)
            cur_stanza = stanzas[s_idx]

            canvas = bg_stage.copy()
            cdraw = ImageDraw.Draw(canvas)

            # 1) Üst Saf Beyaz Stüdyo Plak Çalar & Akustik Dalga Paneli (y: 54..415)
            cdraw.rounded_rectangle(
                (S(48), S(54), W - S(48), S(415)),
                radius=S(28),
                fill=(255, 255, 255, 252),
                outline=(197, 160, 89, 238),
                width=S(3),
            )
            # Dönen 12-inç Vinil Plak Diski + Resmi Albüm Kapağı Zarfı
            rot_deg = (t * 45.0) % 360.0
            spinning_vinyl = render_vinyl_record_disc(album_cover, diameter=S(268), angle_deg=rot_deg)
            canvas.paste(spinning_vinyl, (S(215), S(96)), spinning_vinyl)
            canvas.paste(spot_sleeve, (S(68), S(85)), spot_sleeve)

            info_cx = S(740)
            _draw_pill(
                cdraw,
                info_cx,
                S(112),
                f"{lang_code} • {_tr_upper(lang_tr)} ŞARKI ÇEVİRİSİ",
                f_hdr_kicker,
                (197, 160, 89, 255),
                (255, 255, 255, 255),
                S(22),
                S(8),
                S(14),
            )
            cdraw.text(
                (info_cx, S(178)),
                _tr_upper(artist)[:24],
                fill=(142, 104, 36, 255),
                font=f_hdr_artist,
                anchor="mm",
            )
            cdraw.text(
                (info_cx, S(226)),
                f"“{title[:22]}”",
                fill=(18, 16, 22, 255),
                font=f_hdr_title,
                anchor="mm",
            )

            # Canlı Şampanya Altın Akustik Ses Dalgası Çubukları (Waveform)
            n_bars = 22
            bar_w = S(8)
            bar_gap = S(15)
            wf_start_x = info_cx - ((n_bars * bar_gap) // 2)
            wf_cy = S(318)
            for b_i in range(n_bars):
                wave_val = (
                    0.35
                    + 0.40 * abs(math.sin(t * 6.5 + b_i * 0.55))
                    + 0.25 * abs(math.cos(t * 3.8 - b_i * 0.35))
                )
                bh_half = max(S(6), int(S(38) * wave_val))
                bx = wf_start_x + b_i * bar_gap
                col_bar = (197, 160, 89, 255) if b_i % 2 == 0 else (34, 30, 38, 220)
                cdraw.rounded_rectangle(
                    (bx, wf_cy - bh_half, bx + bar_w, wf_cy + bh_half),
                    radius=S(4),
                    fill=col_bar,
                )

            # 2) Merkez Hero Türkçe Çeviri Kartı (Remotion Spring Girişi + Altın Fosforlu Vurgu)
            sp_now = _remotion_spring(local_t, damping=14.0, stiffness=120.0, mass=0.8)
            sp_prev = _remotion_spring(max(0.0, local_t - (1.0 / float(FPS))), damping=14.0, stiffness=120.0, mass=0.8)

            hl_prog = max(0.0, min(1.0, (local_t - 0.18) / max(0.5, stanza_dur * 0.62)))
            hero_card = _render_spotlight_hero_card(
                cur_stanza,
                stanza_idx=s_idx + 1,
                total_stanzas=len(stanzas),
                song=song,
                highlight_progress=hl_prog,
            )

            target_hx = (W - hero_card.width) // 2
            target_hy = S(448)
            start_hx = W + S(80) if s_idx % 2 == 0 else -hero_card.width - S(80)
            cur_hx = int(round(start_hx + (target_hx - start_hx) * sp_now))
            prev_hx = int(round(start_hx + (target_hx - start_hx) * sp_prev))
            speed_h = abs(cur_hx - prev_hx)
            hero_vis = _apply_180deg_shutter_blur(hero_card, speed_h)
            canvas.paste(hero_vis, (cur_hx, target_hy), hero_vis)

            # 3) Alt 4 Adımlı Dize İlerleme Bandı (01 • 02 • 03 • 04) + Kaydetme Çağrısı
            step_y = S(1465)
            step_w = S(228)
            step_h = S(74)
            step_gap = S(24)
            total_steps_w = len(stanzas) * step_w + (len(stanzas) - 1) * step_gap
            step_start_x = (W - total_steps_w) // 2

            for st_i in range(len(stanzas)):
                sx_box = step_start_x + st_i * (step_w + step_gap)
                is_active = st_i == s_idx
                is_done = st_i < s_idx
                fill_c = (197, 160, 89, 255) if is_active else ((242, 236, 224, 255) if is_done else (255, 255, 255, 245))
                txt_c = (255, 255, 255, 255) if is_active else ((132, 96, 34, 255) if is_done else (120, 114, 106, 255))
                cdraw.rounded_rectangle(
                    (sx_box, step_y, sx_box + step_w, step_y + step_h),
                    radius=S(18),
                    fill=fill_c,
                    outline=(197, 160, 89, 240),
                    width=S(3 if is_active else 1),
                )
                cdraw.text(
                    (sx_box + step_w // 2, step_y + step_h // 2),
                    f"DİZE 0{st_i + 1}",
                    fill=txt_c,
                    font=f_step,
                    anchor="mm",
                )

            _draw_pill(
                cdraw,
                W // 2,
                S(1605),
                f"» EKLENECEK NAKARAT: {song.get('chorus_timestamp', '0:42 - 0:57')} «",
                f_hdr_artist,
                (248, 244, 236, 255),
                (132, 96, 34, 255),
                S(28),
                S(11),
                S(18),
                (197, 160, 89, 210),
                S(2),
            )
            _draw_pill(
                cdraw,
                W // 2,
                S(1690),
                "» VİDEOYU KAYDET • TÜM ÇEVİRİ METNİ AÇIKLAMADA «",
                f_cta,
                (20, 18, 24, 255),
                (242, 214, 158, 255),
                S(32),
                S(13),
                S(20),
            )

            frame_rgb = apply_organic_camera_breathing(canvas.convert("RGB"), t=local_t, stage_idx=s_idx + 2)

        # Sahne geçişlerinde hafif sıcak stüdyo gün ışığı yansıması
        for tr_t in (1.45, 4.20, 6.75, 9.30, 11.85):
            if abs(t - tr_t) <= 0.16:
                lp = (t - (tr_t - 0.16)) / 0.32
                frame_rgb = _apply_warm_studio_light_sweep(
                    frame_rgb,
                    intensity=0.32 * math.sin(lp * math.pi),
                    sweep_pos=lp,
                )

        # İnce pamuklu dergi kağıdı / Portra 400 stüdyo dokusu
        frame_rgb = apply_editorial_paper_film_grain(frame_rgb, frame_idx=f_idx)

        # Üst 6px Şampanya Altın İzlenme Tutma (Retention) İlerleme Çubuğu
        top_draw = ImageDraw.Draw(frame_rgb)
        prog_w = max(S(12), int(W * (t / total_duration)))
        top_draw.rectangle((0, 0, prog_w, S(6)), fill=(197, 160, 89))

        frame_path = os.path.join(frames_dir, f"frame_{f_idx:04d}.jpg")
        frame_rgb.save(frame_path, "JPEG", quality=95)

    wav_path = os.path.join(out_dir, "songtrai_studio_audio.wav")
    generate_studio_vinyl_soundtrack(wav_path, duration=total_duration)

    ffmpeg_exe = get_ffmpeg_exe()
    cmd = [
        ffmpeg_exe,
        "-y",
        "-framerate", str(FPS),
        "-i", os.path.join(frames_dir, "frame_%04d.jpg"),
        "-i", wav_path,
        "-vf", "unsharp=5:5:0.75:3:3:0.0,format=yuv420p",
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
        "hook_cover_path": os.path.join(out_dir, "hook_cover.jpg"),
        "duration_sec": total_duration,
        "resolution": f"{W}x{H}",
        "fps": FPS,
        "video_codec": "libx264 (CRF 12, 22 Mbps, BT.709)",
        "studio_style": "Pure White Studio (#FFFFFF) • Zero Space/AI Trace • Spinning Vinyl & 4-Stanza GraphMotion",
    }
