# -*- coding: utf-8 -*-
"""
Şarkıların Anlamı (@songtraibot) — Şarkının Dönemine ve Baskınlığına Göre 4 Farklı Ses İcadı Motoru
====================================================================================================
Kullanıcı vizyonu doğrultusunda, saf beyaz stüdyo (#FFFFFF) üzerinde şarkının:
- Çıkış dönemine (1970'ler, 80'ler, 90'lar, 2000'ler, 2010'lar, 2020'ler) ve
- Müzikal baskınlığına / enerjisine (yüksek baslı club/pop hit, nostaljik balad, akustik/chanson, rock)
göre 4 farklı fiziksel ses icadından (Audio Deck) en uygun olanını seçer ve gerçek zamanlı ses
enerjisiyle (`bass_energy`, `spectrum_bars`) senkronize döndürür / hareketlendirir:

1) `vinyl_turntable`: Klasik Dönen 12" Vinil Plak + Albüm Kapağı Zarfı + Metalik Pikap İğne Kolu (Tonearm)
2) `dj_mix_deck`    : Modern Pioneer/Club Tarzı Dönen DJ Mix Jog-Wheel + Bas Duyarlı LED Halka + Pitch Fader & EQ
3) `retro_cassette` : 80'ler/90'lar Nostaljik Çift Çarklı Dönen Şeffaf Kaset (Compact Cassette Deck)
4) `optical_cd_deck`: 2000'ler İridyum/Prizma Yansımalı Dönen Optik Kompakt Disk (CD) + Albüm Kitapçığı
"""

import math
from typing import Any, Dict, List, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from white_studio_optics import apply_studio_contact_shadow_card, render_vinyl_record_disc

_CD_DISC_CACHE: Dict[int, Image.Image] = {}


def select_audio_deck_type(song: Dict[str, Any], avg_bpm_or_energy: float = 0.5) -> str:
    """
    Şarkının dönemine (`release_year`), diline/türüne ve ses baskınlığına göre:
    - `vinyl_turntable`
    - `dj_mix_deck`
    - `retro_cassette`
    - `optical_cd_deck`
    arasından en uygun ses icadını seçer.
    """
    explicit = str(song.get("deck_type", "")).strip()
    if explicit in ("vinyl_turntable", "dj_mix_deck", "retro_cassette", "optical_cd_deck"):
        return explicit

    sid = str(song.get("id", "")).lower()
    title_low = f"{song.get('artist', '')} {song.get('title', '')}".lower()
    try:
        year = int(str(song.get("release_year", "2020"))[:4])
    except Exception:
        year = 2020

    # Yüksek enerjili / baskın ritimli modern hitler -> DJ Mix Deck
    dj_keywords = ("apt", "bruno", "komet", "apache", "kometa", "jony", "billie", "sofia", "despecha", "tqg", "hass", "idol")
    if any(k in title_low or k in sid for k in dj_keywords) or (year >= 2021 and avg_bpm_or_energy > 0.58):
        return "dj_mix_deck"

    # Nostaljik / samimi / çocukluk & içsel mektup şarkıları -> Çift Çarklı Retro Kaset
    cassette_keywords = ("detstvo", "rauf", "oft gefragt", "annenmay", "ditto", "newjeans", "yan yuan", "joker")
    if any(k in title_low or k in sid for k in cassette_keywords) or (1985 <= year <= 2002):
        return "retro_cassette"

    # 2003 - 2016 arası modern klasik / rock / film müziği -> Optik CD Deck
    cd_keywords = ("arctic", "wanna be yours", "tum hi ho", "arijit", "stromae", "papaoutai", "gao bai")
    if any(k in title_low or k in sid for k in cd_keywords):
        return "optical_cd_deck"

    # Klasik dönem veya zamansız chanson/plak ruhu -> Dönen Vinil Plak & Pikap Kolu
    return "vinyl_turntable"


def _paste_with_soft_shadow(
    canvas: Image.Image,
    card_rgba: Image.Image,
    x: int,
    y: int,
    elevation_px: int = 12,
) -> None:
    """Kartın yuvarlatılmış köşelerini kesmeden doğal stüdyo gölgesiyle tuvale yapıştırır."""
    w, h = card_rgba.size
    pad = max(24, elevation_px * 3)
    out = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    alpha = card_rgba.split()[3]
    shadow_alpha = alpha.point(lambda a: int(a * 0.11))
    shadow_layer = Image.new("RGBA", (w, h), (22, 22, 28, 0))
    shadow_layer.putalpha(shadow_alpha)
    out.paste(shadow_layer, (pad, pad + int(elevation_px * 0.75)))
    out = out.filter(ImageFilter.GaussianBlur(radius=max(6.0, elevation_px * 0.85)))
    out.paste(card_rgba, (pad, pad), card_rgba)
    canvas.paste(out, (x - pad, y - pad), out)


def _make_clean_album_card(album_cover: Image.Image, size: int, accent_rgb: Tuple[int, int, int]) -> Image.Image:
    card = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)
    r_rad = max(14, size // 16)
    draw.rounded_rectangle(
        (0, 0, size - 1, size - 1),
        radius=r_rad,
        fill=(255, 255, 255, 255),
        outline=(225, 225, 232, 255),
        width=3,
    )
    pad = max(8, size // 36)
    inner = album_cover.resize((size - pad * 2, size - pad * 2), Image.Resampling.LANCZOS)
    mask = Image.new("L", inner.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, inner.width - 1, inner.height - 1),
        radius=max(10, r_rad - 4),
        fill=255,
    )
    card.paste(inner, (pad, pad), mask)
    return card


def _render_iridescent_cd_disc(album_cover: Image.Image, diameter: int, angle_deg: float) -> Image.Image:
    base_cd = _CD_DISC_CACHE.get(diameter)
    if base_cd is None:
        yy, xx = np.mgrid[0:diameter, 0:diameter].astype(np.float32)
        cx = (diameter - 1) * 0.5
        cy = (diameter - 1) * 0.5
        dx = xx - cx
        dy = yy - cy
        r = np.sqrt(dx * dx + dy * dy)
        max_r = diameter * 0.5 - 2.0
        norm_r = np.clip(r / max_r, 0.0, 1.0)
        theta = np.arctan2(dy, dx)

        mask = np.clip((max_r - r) * 1.5, 0.0, 1.0)
        inner_hole = r < (diameter * 0.085)
        mask[inner_hole] = 0.0

        # Polikarbonat gümüş gövde + prizmatik CD gökkuşağı yansıma kuşağı
        sheen1 = np.exp(-((np.sin(theta * 2.0 + 0.4)) ** 2) / 0.09) * (norm_r ** 0.5)
        sheen2 = np.exp(-((np.sin(theta * 2.0 - 0.35)) ** 2) / 0.11) * (norm_r ** 0.5)

        base_lum = 218.0 + np.sin(norm_r * 160.0) * 3.5
        r_ch = np.clip(base_lum + sheen1 * 32.0 - sheen2 * 14.0, 165, 252).astype(np.uint8)
        g_ch = np.clip(base_lum + sheen1 * 18.0 + sheen2 * 26.0, 168, 252).astype(np.uint8)
        b_ch = np.clip(base_lum - sheen1 * 12.0 + sheen2 * 38.0, 175, 255).astype(np.uint8)

        # İç şeffaf polikarbonat halka
        hub_ring = (norm_r > 0.17) & (norm_r < 0.34)
        r_ch[hub_ring] = 240
        g_ch[hub_ring] = 242
        b_ch[hub_ring] = 246

        rgba = np.dstack([r_ch, g_ch, b_ch, (mask * 255.0).astype(np.uint8)])
        base_cd = Image.fromarray(rgba, mode="RGBA")
        _CD_DISC_CACHE[diameter] = base_cd

    cd = base_cd.copy()
    # CD üzerine yarım/halka albüm baskısı
    lbl_d = int(diameter * 0.44)
    lbl = album_cover.resize((lbl_d, lbl_d), Image.Resampling.LANCZOS).rotate(
        -angle_deg, resample=Image.Resampling.BILINEAR
    )
    lbl_mask = Image.new("L", (lbl_d, lbl_d), 0)
    mdraw = ImageDraw.Draw(lbl_mask)
    mdraw.ellipse((0, 0, lbl_d - 1, lbl_d - 1), fill=235)
    inner_r = int(lbl_d * 0.38)
    c_l = lbl_d // 2
    mdraw.ellipse((c_l - inner_r, c_l - inner_r, c_l + inner_r, c_l + inner_r), fill=0)

    pos = (diameter - lbl_d) // 2
    cd.paste(lbl, (pos, pos), lbl_mask)
    ddraw = ImageDraw.Draw(cd)
    ddraw.ellipse((2, 2, diameter - 3, diameter - 3), outline=(180, 184, 194, 240), width=3)
    return cd


def render_era_audio_deck_on_stage(
    canvas: Image.Image,
    deck_type: str,
    album_cover: Image.Image,
    song: Dict[str, Any],
    t: float,
    bass_energy: float,
    spectrum_bars: List[float],
    accent_rgb: Tuple[int, int, int],
    scale_fn,
    font_getter,
) -> None:
    """
    Saf beyaz stüdyo tuvalinin üst bölümüne (`y: 120 .. 790`) seçilen ses icadını
    (`vinyl_turntable`, `dj_mix_deck`, `retro_cassette`, `optical_cd_deck`) çizer.
    """
    S = scale_fn
    W, _ = canvas.size
    draw = ImageDraw.Draw(canvas)
    ar, ag, ab = accent_rgb

    # =========================================================================
    # 1. MODERN DJ MIX DECK (Dönen Jog-Wheel + Bas Duyarlı LED Halka + Pitch/EQ)
    # =========================================================================
    if deck_type == "dj_mix_deck":
        deck_w, deck_h = S(940), S(490)
        dx = (W - deck_w) // 2
        dy = S(155)

        # Beyaz/Mat Gümüş Endüstriyel DJ Konsol Gövdesi (Teenage Engineering / Pioneer Beyaz Stüdyo Serisi)
        deck_card = Image.new("RGBA", (deck_w, deck_h), (0, 0, 0, 0))
        ddraw = ImageDraw.Draw(deck_card)
        ddraw.rounded_rectangle(
            (0, 0, deck_w - 1, deck_h - 1),
            radius=S(34),
            fill=(248, 249, 252, 255),
            outline=(218, 220, 228, 255),
            width=S(3),
        )
        ddraw.rounded_rectangle(
            (S(14), S(14), deck_w - S(15), deck_h - S(15)),
            radius=S(26),
            outline=(234, 236, 242, 255),
            width=S(2),
        )

        # Sol Bölüm: Dönen Motorize DJ Jog-Wheel Platter
        jog_cx, jog_cy = S(285), deck_h // 2
        jog_r = S(195)
        # Bas enerjisine duyarlı dış LED halka (şarkının vurgu renginde parlar!)
        halo_r = jog_r + S(12) + int(S(8) * bass_energy)
        ddraw.ellipse(
            (jog_cx - halo_r, jog_cy - halo_r, jog_cx + halo_r, jog_cy + halo_r),
            fill=(ar, ag, ab, int(45 + 95 * bass_energy)),
            outline=(ar, ag, ab, 235),
            width=S(4),
        )

        # Jog-Wheel mat siyah/grafit dış tekerlek
        ddraw.ellipse(
            (jog_cx - jog_r, jog_cy - jog_r, jog_cx + jog_r, jog_cy + jog_r),
            fill=(20, 21, 26, 255),
            outline=(62, 64, 74, 255),
            width=S(4),
        )

        # Jog-Wheel çevresindeki dönen metalik çentikler (stroboscopic dots)
        rot_rad = math.radians(t * 72.0)
        for i_dot in range(24):
            ang = rot_rad + (i_dot * 2.0 * math.pi / 24.0)
            dot_dist = jog_r - S(18)
            px = jog_cx + int(math.cos(ang) * dot_dist)
            py = jog_cy + int(math.sin(ang) * dot_dist)
            dot_col = (ar, ag, ab, 255) if i_dot % 6 == 0 else (140, 144, 156, 210)
            r_d = S(5) if i_dot % 6 == 0 else S(3)
            ddraw.ellipse((px - r_d, py - r_d, px + r_d, py + r_d), fill=dot_col)

        # Jog-Wheel merkezinde dönen yüksek çözünürlüklü albüm kapağı ekranı
        center_d = S(236)
        rot_cov = album_cover.resize((center_d, center_d), Image.Resampling.LANCZOS).rotate(
            -(t * 72.0) % 360.0, resample=Image.Resampling.BILINEAR
        )
        c_mask = Image.new("L", (center_d, center_d), 0)
        ImageDraw.Draw(c_mask).ellipse((0, 0, center_d - 1, center_d - 1), fill=255)
        deck_card.paste(rot_cov, (jog_cx - center_d // 2, jog_cy - center_d // 2), c_mask)
        ddraw.ellipse(
            (jog_cx - center_d // 2, jog_cy - center_d // 2, jog_cx + center_d // 2, jog_cy + center_d // 2),
            outline=(ar, ag, ab, 245),
            width=S(4),
        )

        # Sağ Bölüm: DJ Pitch Fader, 3'lü EQ Potansiyometreleri & Canlı Frekans Spektrumu
        rx_left = S(535)
        f_lbl = font_getter("DJ MIX", 14, bold=True)
        ddraw.text((rx_left, S(48)), "STUDIO DJ MIX DECK • LIVE SYNC", fill=(110, 114, 126, 255), font=f_lbl)

        # 4 Adet Performans CUE Pad'i (Aktif vuruşta yanar)
        for p_i in range(4):
            px0 = rx_left + p_i * S(82)
            py0 = S(82)
            is_lit = (int(t * 4.0) % 4) == p_i
            p_fill = (ar, ag, ab, 255) if is_lit else (232, 234, 240, 255)
            p_txt = (255, 255, 255, 255) if is_lit else (90, 94, 106, 255)
            ddraw.rounded_rectangle(
                (px0, py0, px0 + S(70), py0 + S(52)),
                radius=S(10),
                fill=p_fill,
                outline=(ar, ag, ab, 220) if is_lit else (204, 208, 218, 255),
                width=S(2),
            )
            ddraw.text((px0 + S(35), py0 + S(26)), f"CUE {p_i + 1}", fill=p_txt, font=f_lbl, anchor="mm")

        # Canlı Ses Spektrum Analizörü (16 Frekans Çubuğu — Gerçek Şarkı Sesine Duyarlı!)
        spec_top = S(168)
        spec_bot = S(338)
        ddraw.rounded_rectangle(
            (rx_left, spec_top, rx_left + S(336), spec_bot),
            radius=S(16),
            fill=(18, 19, 24, 255),
        )
        n_bars = min(16, len(spectrum_bars))
        bw = S(13)
        bgap = S(19)
        b_start_x = rx_left + S(22)
        for b_i in range(n_bars):
            val = max(0.08, min(1.0, spectrum_bars[b_i]))
            bh = int((spec_bot - spec_top - S(36)) * val)
            bx = b_start_x + b_i * bgap
            by1 = spec_bot - S(16)
            by0 = by1 - bh
            col = (ar, ag, ab, 255) if b_i % 2 == 0 else (255, 255, 255, 230)
            ddraw.rounded_rectangle((bx, by0, bx + bw, by1), radius=S(4), fill=col)

        # Alt Crossfader & Pitch Slider
        fader_y = S(398)
        ddraw.line([(rx_left + S(10), fader_y), (rx_left + S(326), fader_y)], fill=(190, 194, 206, 255), width=S(6))
        knob_x = rx_left + S(168) + int(math.sin(t * 1.8) * S(75))
        ddraw.rounded_rectangle(
            (knob_x - S(22), fader_y - S(20), knob_x + S(22), fader_y + S(20)),
            radius=S(8),
            fill=(ar, ag, ab, 255),
            outline=(255, 255, 255, 255),
            width=S(2),
        )

        _paste_with_soft_shadow(canvas, deck_card, dx, dy, elevation_px=S(14))
        return

    # =========================================================================
    # 2. RETRO ÇİFT ÇARKLI ŞEFFAF KASETÇALAR (Compact Cassette Deck)
    # =========================================================================
    if deck_type == "retro_cassette":
        cas_w, cas_h = S(880), S(480)
        cx0 = (W - cas_w) // 2
        cy0 = S(160)

        cas = Image.new("RGBA", (cas_w, cas_h), (0, 0, 0, 0))
        cdraw = ImageDraw.Draw(cas)

        # Kaset Dış Gövdesi (Fildişi / Kırık Beyaz Endüstriyel Kaset Kabuğu)
        cdraw.rounded_rectangle(
            (0, 0, cas_w - 1, cas_h - 1),
            radius=S(32),
            fill=(246, 245, 242, 255),
            outline=(205, 204, 200, 255),
            width=S(4),
        )
        # Köşe vidaları
        for vx, vy in [(S(28), S(28)), (cas_w - S(28), S(28)), (S(28), cas_h - S(28)), (cas_w - S(28), cas_h - S(28))]:
            cdraw.ellipse((vx - S(8), vy - S(8), vx + S(8), vy + S(8)), fill=(190, 190, 195, 255))

        # Üst Kaset Etiketi (Vurgu rengi şerit + Sol tarafta albüm kapağı)
        cdraw.rounded_rectangle(
            (S(46), S(38), cas_w - S(46), S(345)),
            radius=S(20),
            fill=(255, 255, 255, 255),
            outline=(ar, ag, ab, 235),
            width=S(3),
        )
        cdraw.rounded_rectangle(
            (S(46), S(38), cas_w - S(46), S(96)),
            radius=S(18),
            fill=(ar, ag, ab, 255),
        )
        f_cas = font_getter("CHROME", 16, bold=True)
        cdraw.text(
            (cas_w // 2, S(67)),
            f"TYPE II CHROME • HI-FI ANALOG CASSETTE • {song.get('release_year', '')}",
            fill=(255, 255, 255, 255),
            font=f_cas,
            anchor="mm",
        )

        # Sol tarafta mini albüm kapağı
        cov_mini = album_cover.resize((S(175), S(175)), Image.Resampling.LANCZOS)
        cas.paste(cov_mini, (S(74), S(128)))
        cdraw.rectangle((S(74), S(128), S(74) + S(175), S(128) + S(175)), outline=(ar, ag, ab, 240), width=S(2))

        # Orta-Sağ Kaset Penceresi ve DÖNEN ÇİFT MAKARA ÇARKLARI (Spools)
        win_left, win_top, win_right, win_bot = S(278), S(128), cas_w - S(74), S(305)
        cdraw.rounded_rectangle(
            (win_left, win_top, win_right, win_bot),
            radius=S(22),
            fill=(26, 27, 32, 255),
            outline=(160, 162, 170, 255),
            width=S(3),
        )

        reel_y = (win_top + win_bot) // 2
        reel_lx = win_left + S(125)
        reel_rx = win_right - S(125)
        reel_r = S(58)

        # Manyetik bant rulosu
        cdraw.ellipse((reel_lx - S(74), reel_y - S(74), reel_lx + S(74), reel_y + S(74)), fill=(46, 38, 36, 255))
        cdraw.ellipse((reel_rx - S(68), reel_y - S(68), reel_rx + S(68), reel_y + S(68)), fill=(46, 38, 36, 255))

        # Dönen beyaz dişli kaset çarkları
        rot_a = math.radians(t * 95.0)
        for rx_c in (reel_lx, reel_rx):
            cdraw.ellipse(
                (rx_c - reel_r, reel_y - reel_r, rx_c + reel_r, reel_y + reel_r),
                fill=(248, 248, 250, 255),
                outline=(ar, ag, ab, 255),
                width=S(4),
            )
            for k_tooth in range(6):
                a_t = rot_a + k_tooth * (math.pi / 3.0)
                tx1 = rx_c + int(math.cos(a_t) * S(20))
                ty1 = reel_y + int(math.sin(a_t) * S(20))
                tx2 = rx_c + int(math.cos(a_t) * (reel_r - S(6)))
                ty2 = reel_y + int(math.sin(a_t) * (reel_r - S(6)))
                cdraw.line([(tx1, ty1), (tx2, ty2)], fill=(26, 27, 32, 255), width=S(7))
            cdraw.ellipse((rx_c - S(18), reel_y - S(18), rx_c + S(18), reel_y + S(18)), fill=(26, 27, 32, 255))

        # Alt Kaset Manyetik Kafa Yamuğu (Trapezoid Head Shield)
        cdraw.polygon(
            [(S(190), cas_h - S(4)), (S(235), S(372)), (cas_w - S(235), S(372)), (cas_w - S(190), cas_h - S(4))],
            fill=(232, 231, 226, 255),
            outline=(195, 194, 188, 255),
        )
        # Canlı ses seviye (VU) barları alt yamukta
        for b_i in range(12):
            v_b = spectrum_bars[b_i % len(spectrum_bars)] if spectrum_bars else 0.5
            bx = S(295) + b_i * S(25)
            bh = max(S(6), int(S(46) * v_b))
            cdraw.rounded_rectangle(
                (bx, cas_h - S(24) - bh, bx + S(14), cas_h - S(24)),
                radius=S(4),
                fill=(ar, ag, ab, 255) if b_i % 2 == 0 else (30, 30, 36, 220),
            )

        _paste_with_soft_shadow(canvas, cas, cx0, cy0, elevation_px=S(14))
        return

    # =========================================================================
    # 3. OPTİK CD DECK (Dönen İridyum Yansımalı Kompakt Disk + Albüm Kitapçığı)
    # =========================================================================
    if deck_type == "optical_cd_deck":
        sleeve_sz = S(450)
        cd_d = S(430)
        rot_deg = (t * 68.0) % 360.0
        cd_im = _render_iridescent_cd_disc(album_cover, diameter=cd_d, angle_deg=rot_deg)
        sleeve_im = _make_clean_album_card(album_cover, size=sleeve_sz, accent_rgb=accent_rgb)

        canvas.paste(cd_im, (S(485), S(168)), cd_im)
        _paste_with_soft_shadow(canvas, sleeve_im, S(145), S(155), elevation_px=S(12))
        return

    # =========================================================================
    # 4. KLASİK DÖNEN VİNİL PLAK & PİKAP İĞNE KOLU (Vinyl Turntable)
    # =========================================================================
    sleeve_sz = S(460)
    vinyl_d = S(445)
    rot_deg = (t * 52.0) % 360.0
    vinyl_im = render_vinyl_record_disc(album_cover, diameter=vinyl_d, angle_deg=rot_deg)
    sleeve_im = _make_clean_album_card(album_cover, size=sleeve_sz, accent_rgb=accent_rgb)

    vx, vy = S(470), S(162)
    canvas.paste(vinyl_im, (vx, vy), vinyl_im)
    _paste_with_soft_shadow(canvas, sleeve_im, S(130), S(152), elevation_px=S(12))

    # Pikap Metalik İğne Kolu (Turntable Tonearm) — Sağ üstten plağın oluğuna uzanır
    pivot_x, pivot_y = vx + vinyl_d + S(26), vy + S(48)
    stylus_x, stylus_y = vx + int(vinyl_d * 0.78), vy + int(vinyl_d * 0.66)
    draw.ellipse(
        (pivot_x - S(26), pivot_y - S(26), pivot_x + S(26), pivot_y + S(26)),
        fill=(228, 230, 236),
        outline=(160, 164, 174),
        width=S(3),
    )
    draw.ellipse(
        (pivot_x - S(11), pivot_y - S(11), pivot_x + S(11), pivot_y + S(11)),
        fill=accent_rgb,
    )
    draw.line([(pivot_x, pivot_y), (stylus_x, stylus_y)], fill=(180, 184, 192), width=S(8))
    draw.line([(pivot_x - S(2), pivot_y), (stylus_x - S(2), stylus_y)], fill=(242, 244, 248), width=S(3))
    # İğne başlığı (Headshell)
    draw.rounded_rectangle(
        (stylus_x - S(14), stylus_y - S(10), stylus_x + S(10), stylus_y + S(18)),
        radius=S(5),
        fill=accent_rgb,
    )
