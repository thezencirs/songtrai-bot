# -*- coding: utf-8 -*-
"""
Şarkıların Anlamı (@songtraibot) — Saf Beyaz Stüdyo (#FFFFFF) & Fiziksel Plak/Kağıt Optik Motoru
=================================================================================================
- Kesinlikle uzay, neon veya yapay zeka (AI) yüz/arka plan izi içermez.
- Şarkıların gerçek resmi 1000x1000 HD albüm kapaklarını iTunes / Deezer resmi kataloglarından çeker.
- Fiziksel vinil plak olukları, gerçek stüdyo temas gölgesi (contact shadow), organik el kamerası
  nefes alış salınımı ve Kodak Portra 400 / Kinfolk pamuklu dergi kağıdı mikro-dokusunu işler.
"""

import io
import math
import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np
import requests
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

BASE_DIR = Path(__file__).resolve().parent.parent
COVERS_DIR = BASE_DIR / "assets" / "covers"

_PAPER_GRAIN_CACHE: Dict[Tuple[int, int], Image.Image] = {}
_VINYL_BASE_CACHE: Dict[int, Image.Image] = {}


def fetch_official_album_artwork(song: Dict[str, Any], size: int = 900) -> Image.Image:
    """
    Şarkının gerçek resmi yüksek çözünürlüklü (1000x1000) albüm kapağını iTunes veya Deezer API'den
    indirir ve `assets/covers/{id}.jpg` olarak önbelleğe alır.
    """
    COVERS_DIR.mkdir(parents=True, exist_ok=True)
    sid = str(song.get("id", "default_song")).strip()
    cache_path = COVERS_DIR / f"{sid}.jpg"

    if cache_path.exists() and cache_path.stat().st_size > 4000:
        try:
            im = Image.open(cache_path).convert("RGB")
            return im.resize((size, size), Image.Resampling.LANCZOS)
        except Exception:
            pass

    query = song.get("itunes_query") or f"{song.get('artist', '')} {song.get('title', '')}"
    direct_url = str(song.get("artwork_url", "")).strip()

    candidate_urls = []
    if direct_url.startswith("http"):
        candidate_urls.append(direct_url)

    # 1) iTunes Official Search API (1000x1000bb HD Cover)
    try:
        r = requests.get(
            "https://itunes.apple.com/search",
            params={"term": query, "entity": "song", "limit": 3},
            timeout=10,
        )
        if r.status_code == 200:
            results = r.json().get("results") or []
            for res in results:
                u100 = res.get("artworkUrl100", "")
                if u100:
                    candidate_urls.append(u100.replace("100x100bb", "1000x1000bb"))
    except Exception:
        pass

    # 2) Deezer Official API Fallback (1000x1000 Cover XL)
    if not candidate_urls:
        try:
            dr = requests.get(
                "https://api.deezer.com/search",
                params={"q": query, "limit": 2},
                timeout=10,
            )
            if dr.status_code == 200:
                d_items = dr.json().get("data") or []
                for ditem in d_items:
                    cov_xl = (ditem.get("album") or {}).get("cover_xl", "")
                    if cov_xl:
                        candidate_urls.append(cov_xl)
        except Exception:
            pass

    for url in candidate_urls:
        try:
            img_r = requests.get(url, timeout=12)
            if img_r.status_code == 200 and len(img_r.content) > 4000:
                im = Image.open(io.BytesIO(img_r.content)).convert("RGB")
                im = ImageEnhance.Contrast(im).enhance(1.06)
                im = ImageEnhance.Color(im).enhance(1.05)
                im = im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=115, threshold=2))
                im.save(cache_path, "JPEG", quality=96)
                return im.resize((size, size), Image.Resampling.LANCZOS)
        except Exception:
            continue

    # Çevrimdışı / yedek durumda: Saf Beyaz & Altın Minimalist Editoryal Plak Kapağı
    return _render_minimal_editorial_cover(song, size=size)


def _render_minimal_editorial_cover(song: Dict[str, Any], size: int = 900) -> Image.Image:
    im = Image.new("RGB", (size, size), (250, 247, 240))
    draw = ImageDraw.Draw(im)
    gold = (197, 160, 89)
    dark = (20, 18, 22)
    draw.rectangle((28, 28, size - 28, size - 28), outline=gold, width=5)
    draw.rectangle((44, 44, size - 44, size - 44), outline=(218, 196, 148), width=2)
    cx, cy = size // 2, size // 2
    draw.ellipse((cx - 180, cy - 180, cx + 180, cy + 180), fill=dark, outline=gold, width=4)
    draw.ellipse((cx - 55, cy - 55, cx + 55, cy + 55), fill=gold)
    try:
        f_b = ImageFont.truetype("C:/Windows/Fonts/georgiab.ttf", 44)
        f_s = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 28)
    except Exception:
        f_b = ImageFont.load_default()
        f_s = ImageFont.load_default()
    artist = str(song.get("artist", "ARTIST")).upper()[:22]
    title = str(song.get("title", "SONG")).upper()[:24]
    draw.text((cx, 125), artist, fill=dark, font=f_b, anchor="mm")
    draw.text((cx, size - 125), title, fill=(138, 102, 36), font=f_s, anchor="mm")
    return im


def render_vinyl_record_disc(album_cover: Image.Image, diameter: int, angle_deg: float = 0.0) -> Image.Image:
    """
    Gerçekçi 12-inç vinil plak diski (mikro-oluklar, anizotropik stüdyo ışık yansıması ve
    merkezde dönen albüm etiketi) oluşturur.
    """
    base_disc = _VINYL_BASE_CACHE.get(diameter)
    if base_disc is None:
        yy, xx = np.mgrid[0:diameter, 0:diameter].astype(np.float32)
        cx = (diameter - 1) * 0.5
        cy = (diameter - 1) * 0.5
        dx = xx - cx
        dy = yy - cy
        r = np.sqrt(dx * dx + dy * dy)
        max_r = diameter * 0.5 - 2.0

        mask = np.clip((max_r - r) * 1.5, 0.0, 1.0)
        norm_r = np.clip(r / max_r, 0.0, 1.0)

        # Vinil mikro-olukları (concentric grooves)
        grooves = (
            np.sin(norm_r * 210.0) * 4.5
            + np.cos(norm_r * 520.0) * 2.5
            + np.sin(norm_r * 95.0) * 3.0
        )
        # Anizotropik stüdyo ışık yansıması (diagonal sheen)
        theta = np.arctan2(dy, dx)
        sheen = np.exp(-((np.sin(theta * 2.0 + 0.65)) ** 2) / 0.14) * 36.0 * (norm_r ** 0.6)

        lum = np.clip(22.0 + grooves + sheen, 10.0, 74.0)
        # Dış altın/grafit çerçeve halkası
        rim = (norm_r > 0.965) & (norm_r <= 1.0)
        rgba = np.zeros((diameter, diameter, 4), dtype=np.uint8)
        rgba[:, :, 0] = lum.astype(np.uint8)
        rgba[:, :, 1] = lum.astype(np.uint8)
        rgba[:, :, 2] = np.clip(lum + 3.0, 12.0, 78.0).astype(np.uint8)
        rgba[rim, 0] = 197
        rgba[rim, 1] = 160
        rgba[rim, 2] = 89
        rgba[:, :, 3] = (mask * 255.0).astype(np.uint8)

        base_disc = Image.fromarray(rgba, mode="RGBA")
        _VINYL_BASE_CACHE[diameter] = base_disc

    disc = base_disc.copy()
    # Merkez albüm etiketi (dönen)
    lbl_d = int(diameter * 0.38)
    lbl_im = album_cover.resize((lbl_d, lbl_d), Image.Resampling.LANCZOS).rotate(
        -angle_deg, resample=Image.Resampling.BILINEAR
    )
    lbl_mask = Image.new("L", (lbl_d, lbl_d), 0)
    mdraw = ImageDraw.Draw(lbl_mask)
    mdraw.ellipse((0, 0, lbl_d - 1, lbl_d - 1), fill=255)

    lx = (diameter - lbl_d) // 2
    ly = (diameter - lbl_d) // 2
    disc.paste(lbl_im, (lx, ly), lbl_mask)

    ddraw = ImageDraw.Draw(disc)
    ddraw.ellipse((lx, ly, lx + lbl_d - 1, ly + lbl_d - 1), outline=(197, 160, 89, 235), width=3)
    hole_r = max(6, diameter // 34)
    cx_i, cy_i = diameter // 2, diameter // 2
    ddraw.ellipse(
        (cx_i - hole_r, cy_i - hole_r, cx_i + hole_r, cy_i + hole_r),
        fill=(252, 250, 246, 255),
        outline=(197, 160, 89, 255),
        width=2,
    )
    return disc


def apply_studio_contact_shadow_card(
    card_rgba: Image.Image,
    elevation_px: int = 12,
) -> Image.Image:
    """
    Saf beyaz stüdyo zemini üzerinde kartların ve albüm kapaklarının havada yapay durmaması için
    altlarına gerçekçi fiziksel stüdyo temas gölgesi (contact shadow) ekler.
    """
    w, h = card_rgba.size
    pad = max(14, elevation_px * 2)
    out = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))

    alpha = card_rgba.split()[3]
    shadow_alpha = alpha.point(lambda a: int(a * 0.16))
    shadow_layer = Image.new("RGBA", (w, h), (32, 26, 20, 0))
    shadow_layer.putalpha(shadow_alpha)

    out.paste(shadow_layer, (pad, pad + int(elevation_px * 0.85)))
    out = out.filter(ImageFilter.GaussianBlur(radius=max(4.0, elevation_px * 0.75)))
    out.paste(card_rgba, (pad, pad), card_rgba)
    return out.crop((pad, pad, pad + w, pad + h))


def apply_organic_camera_breathing(
    img: Image.Image,
    t: float,
    stage_idx: int = 0,
) -> Image.Image:
    """
    Sabit ve cansız ekran görüntüsü hissini ortadan kaldırmak için çok frekanslı
    mikro el kamerası nefes alış salınımı uygular.
    """
    w, h = img.size
    scale_factor = w / 1440.0
    phase = float(stage_idx) * 1.37

    sway_x = (
        math.sin(t * 1.45 + phase) * 3.8
        + math.cos(t * 2.65 + phase * 0.7) * 1.5
    ) * scale_factor
    sway_y = (
        math.cos(t * 1.25 + phase * 1.1) * 4.2
        + math.sin(t * 2.35 + phase * 0.6) * 1.6
    ) * scale_factor

    zoom_breath = 1.012 + 0.0035 * math.sin(t * 1.15 + phase)
    vw = w / zoom_breath
    vh = h / zoom_breath

    max_dx = max(0.0, (w - vw) * 0.5 - 0.5)
    max_dy = max(0.0, (h - vh) * 0.5 - 0.5)
    dx = max(-max_dx, min(max_dx, sway_x))
    dy = max(-max_dy, min(max_dy, sway_y))

    x0 = (w - vw) * 0.5 + dx
    y0 = (h - vh) * 0.5 + dy
    return img.resize(
        (w, h),
        resample=Image.Resampling.BILINEAR,
        box=(x0, y0, x0 + vw, y0 + vh),
    )


def apply_editorial_paper_film_grain(frame_rgb: Image.Image, frame_idx: int = 0) -> Image.Image:
    """
    Saf beyaz stüdyo ve dergi kağıdı üzerine çok hafif Kodak Portra 400 / pamuklu kağıt
    mikro-dokusu uygular (dijital plastikliği kırar, 2K netliğini korur).
    """
    w, h = frame_rgb.size
    bank_key = (w // 2, h // 2)
    grain_im = _PAPER_GRAIN_CACHE.get(bank_key)
    if grain_im is None:
        gw, gh = bank_key
        rng = np.random.default_rng(seed=20261105)
        noise = rng.normal(0.0, 3.2, size=(gh, gw)).astype(np.float32)
        rgba = np.zeros((gh, gw, 4), dtype=np.uint8)
        pos = noise > 1.2
        neg = noise < -1.2
        rgba[pos, 0] = 255
        rgba[pos, 1] = 248
        rgba[pos, 2] = 232
        rgba[pos, 3] = np.clip((noise[pos] - 1.0) * 4.2, 2, 14).astype(np.uint8)
        rgba[neg, 0] = 38
        rgba[neg, 1] = 32
        rgba[neg, 2] = 26
        rgba[neg, 3] = np.clip((-noise[neg] - 1.0) * 3.8, 2, 12).astype(np.uint8)
        grain_im = Image.fromarray(rgba, mode="RGBA").resize((w, h), Image.Resampling.BILINEAR)
        _PAPER_GRAIN_CACHE[bank_key] = grain_im

    out_rgba = frame_rgb.convert("RGBA")
    return Image.alpha_composite(out_rgba, grain_im).convert("RGB")
