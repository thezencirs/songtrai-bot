# -*- coding: utf-8 -*-
"""
Şarkıların Anlamı (@songtraibot) — Saf Stüdyo Plak Dokusu & Sayfa Geçiş Akustik Motoru
======================================================================================
Kullanıcı gerçek şarkıyı sosyal medyada (Instagram Reels / TikTok) paylaşırken platformun kendi
müzik kütüphanesinden ekleyeceği için, video dosyasında telif sorununa yol açmayan,
yalnızca dize kartlarının geçiş anlarında zarif bir vinil plak / dergi sayfası hissi veren
temiz stüdyo akustiği (44.1 kHz, 16-bit Stereo WAV -> 320 kbps AAC) üretir.
"""

import os
import wave
from typing import List

import numpy as np


def generate_studio_vinyl_soundtrack(
    wav_path: str,
    duration: float = 14.4,
    transition_times: List[float] = None,
) -> str:
    os.makedirs(os.path.dirname(wav_path) or ".", exist_ok=True)
    sr = 44100
    n_samples = int(duration * sr)
    t = np.linspace(0.0, duration, n_samples, endpoint=False, dtype=np.float32)

    rng = np.random.default_rng(seed=20261105)
    # Çok hafif sıcak vinil plak stüdyo ambiyansı (sosyal medyada müzik eklendiğinde asla bastırmaz)
    vinyl_warmth = rng.normal(0.0, 0.0035, size=n_samples).astype(np.float32)
    ambient_chord = (
        0.018 * np.sin(2.0 * np.pi * 220.0 * t)
        + 0.012 * np.sin(2.0 * np.pi * 277.18 * t)
        + 0.010 * np.sin(2.0 * np.pi * 329.63 * t)
    ) * (0.65 + 0.35 * np.sin(2.0 * np.pi * 0.25 * t))

    left = vinyl_warmth + ambient_chord
    right = vinyl_warmth * 0.95 + ambient_chord * 0.98

    # Dize kartı geçiş anlarında yumuşak mekanik stüdyo deklanşör / sayfa geçiş tıkı
    clicks = transition_times or [0.05, 1.45, 4.20, 6.75, 9.30, 11.85]
    for ct in clicks:
        idx0 = int(ct * sr)
        c_len = int(0.065 * sr)
        if 0 <= idx0 and idx0 + c_len < n_samples:
            ct_arr = np.linspace(0.0, 0.065, c_len, dtype=np.float32)
            env = np.exp(-ct_arr * 85.0)
            chime = (
                0.085 * np.sin(2.0 * np.pi * 528.0 * ct_arr)
                + 0.045 * np.sin(2.0 * np.pi * 1056.0 * ct_arr)
            ) * env
            left[idx0:idx0 + c_len] += chime
            right[idx0:idx0 + c_len] += chime * 0.92

    stereo = np.column_stack([left, right])
    stereo = np.clip(stereo * 32767.0, -32767.0, 32767.0).astype(np.int16)

    with wave.open(wav_path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(stereo.tobytes())

    return wav_path
