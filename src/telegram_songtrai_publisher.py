# -*- coding: utf-8 -*-
"""
Şarkıların Anlamı (@songtraibot) — Telegram Bot Yapılandırıcı & 2K Reels Teslim Motoru
======================================================================================
- Bot: @songtraibot (Token: 8824304361:AAFeGn-3yjGbd_YA-80GHo3wS6p2v-b-pRA)
- Teslimat:
  1) 2K Saf Beyaz Stüdyo GraphMotion Reels Videosu (`songtrai_reel_final.mp4`) +
     Sosyal Medyada Eklenecek Tam Nakarat Saniyesi Rehberi + 10 Dil Hızlı Üretim Butonları
  2) %100 Saf Kopyala-Yapıştır Sosyal Medya Açıklaması (Sıfır ekstra başlık, doğrudan Instagram/TikTok'a yapıştırılır)
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from song_catalog_10langs import (
    build_explanatory_music_guide,
    build_pure_copy_paste_caption,
    mark_song_used,
)
from telegram_songtrai_ingestor import (
    DEFAULT_ADMIN_CHAT_ID,
    SUBSCRIBERS_FILE,
    get_bot_token,
)


def tg_api(
    method: str,
    data: Optional[Dict[str, Any]] = None,
    files: Optional[Dict[str, Any]] = None,
    token: Optional[str] = None,
) -> Dict[str, Any]:
    tok = token or get_bot_token()
    url = f"https://api.telegram.org/bot{tok}/{method}"
    try:
        if files:
            resp = requests.post(url, data=data, files=files, timeout=120)
        else:
            resp = requests.post(url, json=data or {}, timeout=35)
        return resp.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}


def configure_songtrai_bot_profile(token: Optional[str] = None) -> Dict[str, Any]:
    """@songtraibot profilini, açıklamasını ve 11 dil komutunu Telegram'a kaydeder."""
    tok = token or get_bot_token()
    results = {}
    results["setMyName"] = tg_api(
        "setMyName",
        {"name": "Şarkıların Anlamı • 11 Dil 2K Çeviri (@songtraibot)"},
        token=tok,
    )
    results["setMyShortDescription"] = tg_api(
        "setMyShortDescription",
        {
            "short_description": "🎵 11 Dilde Popüler Şarkıların Edebi Türkçe Çevirisi • 2K Saf Beyaz Stüdyo & Dikey Kapak"
        },
        token=tok,
    )
    results["setMyDescription"] = tg_api(
        "setMyDescription",
        {
            "description": (
                "🎵 Şarkıların Anlamı (@songtraibot) — 11 Dilde Popüler Şarkı Çeviri & 2K Reels Otomasyonu\n\n"
                "🌍 Başta popüler İngilizce hitler olmak üzere; Arapça, Rusça, Japonca, Almanca, İspanyolca, Korece, Çince, İtalyanca, Fransızca ve Hintçe "
                "en popüler şarkıların tertemiz, şiirsel Türkçe çevirilerini Saf Beyaz Stüdyo (#FFFFFF) estetiğiyle ve şarkıya özel dikey kapak resmiyle hazırlar.\n"
                "📲 Her saat başı otomatik stok gönderir; ayrıca istediğiniz şarkı adını veya dil komutunu yazarak anında üretebilirsiniz."
            )
        },
        token=tok,
    )
    results["setMyCommands"] = tg_api(
        "setMyCommands",
        {
            "commands": [
                {"command": "start", "description": "Komuta merkezini ve 11 dil rehberini aç"},
                {"command": "uret", "description": "🎵 Sıradaki popüler şarkıyı 2K çeviriyle üret"},
                {"command": "ingilizce", "description": "🇬🇧 İngilizce popüler şarkı çevirisi üret"},
                {"command": "arapca", "description": "🇸🇦 Arapça popüler şarkı çevirisi üret"},
                {"command": "rusca", "description": "🇷🇺 Rusça popüler şarkı çevirisi üret"},
                {"command": "japonca", "description": "🇯🇵 Japonca popüler şarkı çevirisi üret"},
                {"command": "almanca", "description": "🇩🇪 Almanca popüler şarkı çevirisi üret"},
                {"command": "ispanyolca", "description": "🇪🇸 İspanyolca popüler şarkı çevirisi üret"},
                {"command": "korece", "description": "🇰🇷 Korece popüler şarkı çevirisi üret"},
                {"command": "cince", "description": "🇨🇳 Çince popüler şarkı çevirisi üret"},
                {"command": "italyanca", "description": "🇮🇹 İtalyanca popüler şarkı çevirisi üret"},
                {"command": "fransizca", "description": "🇫🇷 Fransızca popüler şarkı çevirisi üret"},
                {"command": "hintce", "description": "🇮🇳 Hintçe popüler şarkı çevirisi üret"},
            ]
        },
        token=tok,
    )
    return results


def build_songtrai_inline_keyboard() -> Dict[str, Any]:
    """Videonun altına 11 dilde tek tıkla yeni şarkı çevirisi üretme butonları ekler."""
    return {
        "inline_keyboard": [
            [
                {"text": "🇬🇧 İngilizce Hit Üret", "callback_data": "gen_lang:ingilizce"},
                {"text": "🇸🇦 Arapça Üret", "callback_data": "gen_lang:arapca"},
            ],
            [
                {"text": "🇫🇷 Fransızca Üret", "callback_data": "gen_lang:fransizca"},
                {"text": "🇷🇺 Rusça Üret", "callback_data": "gen_lang:rusca"},
            ],
            [
                {"text": "🇯🇵 Japonca Üret", "callback_data": "gen_lang:japonca"},
                {"text": "🇪🇸 İspanyolca Üret", "callback_data": "gen_lang:ispanyolca"},
            ],
            [
                {"text": "🇰🇷 Korece Üret", "callback_data": "gen_lang:korece"},
                {"text": "🇮🇹 İtalyanca Üret", "callback_data": "gen_lang:italyanca"},
            ],
            [
                {"text": "🇩🇪 Almanca Üret", "callback_data": "gen_lang:almanca"},
                {"text": "🇨🇳 Çince Üret", "callback_data": "gen_lang:cince"},
            ],
            [
                {"text": "🇮🇳 Hintçe Üret", "callback_data": "gen_lang:hintce"},
                {"text": "✨ Otomatik Hit Üret", "callback_data": "gen_lang:otomatik"},
            ],
        ]
    }


def load_target_chat_ids(song: Dict[str, Any]) -> List[str]:
    chat_ids: List[str] = ["995164733"]
    env_cid = os.environ.get("TELEGRAM_CHAT_ID", DEFAULT_ADMIN_CHAT_ID).strip()
    for part in env_cid.replace(";", ",").split(","):
        p = part.strip()
        if p and p not in chat_ids:
            chat_ids.append(p)

    req_cid = str(song.get("requester_chat_id", "")).strip()
    if req_cid and req_cid not in chat_ids:
        chat_ids.append(req_cid)

    if SUBSCRIBERS_FILE.exists():
        try:
            sub = json.loads(SUBSCRIBERS_FILE.read_text(encoding="utf-8"))
            for cid in (sub.get("chats") or {}).keys():
                if str(cid) not in chat_ids:
                    chat_ids.append(str(cid))
        except Exception:
            pass
    return chat_ids


def deliver_songtrai_package_to_telegram(
    song: Dict[str, Any],
    video_mp4_path: str,
    out_dir: str = "output",
    token: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Hazırlanan 2K Saf Beyaz Stüdyo Şarkı Çeviri paketini @songtraibot üzerinden teslim eder:
    1) 2K MP4 Video + Sosyal Medyada Eklenecek Tam Nakarat Saniyesi Rehberi + 10 Dil Butonları
    2) %100 Saf Kopyala-Yapıştır Sosyal Medya Açıklaması (Sıfır başlık/sarmalayıcı)
    """
    tok = token or get_bot_token()
    out_p = Path(out_dir)
    os.makedirs(out_p, exist_ok=True)

    guide_msg = build_explanatory_music_guide(song)
    pure_caption = build_pure_copy_paste_caption(song)

    (out_p / "1_music_sync_guide.txt").write_text(guide_msg, encoding="utf-8")
    (out_p / "2_social_caption_copypaste.txt").write_text(pure_caption, encoding="utf-8")
    (out_p / "song_concept_metadata.json").write_text(
        json.dumps(song, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    v_path = Path(video_mp4_path)
    cover_path = out_p / "vertical_cover_9x16.jpg"
    if not cover_path.exists():
        cover_path = out_p / "hook_cover.jpg"

    reply_markup_json = json.dumps(build_songtrai_inline_keyboard())
    chat_ids = load_target_chat_ids(song)
    delivery_report: Dict[str, Any] = {}

    flag = song.get("flag", "🎵")
    artist = song.get("artist", "")
    title = song.get("title", "")
    cover_caption = (
        f"🖼️ <b>{flag} {artist} — “{title}”</b>\n"
        f"📐 <b>Paylaşım İçin Özel 9:16 Dikey Kapak Resmi (1440x2560)</b>"
    )

    for cid in chat_ids:
        res_chat: Dict[str, Any] = {}

        # Mesaj 1: Şarkıya Özel 9:16 Dikey Kapak Resmi (Paylaşımlarda Kapak Seçimi İçin)
        if cover_path.exists():
            with open(cover_path, "rb") as cf:
                r_cov = tg_api(
                    "sendPhoto",
                    data={
                        "chat_id": cid,
                        "caption": cover_caption,
                        "parse_mode": "HTML",
                    },
                    files={"photo": cf},
                    token=tok,
                )
                res_chat["vertical_cover_9x16"] = r_cov.get("ok", False)

        # Mesaj 2: 2K Karaoke Video + 11 Dil Butonları
        if v_path.exists():
            with open(v_path, "rb") as vf:
                files_payload: Dict[str, Any] = {"video": vf}
                cov_fp = open(cover_path, "rb") if cover_path.exists() else None
                if cov_fp is not None:
                    files_payload["cover"] = cov_fp
                try:
                    r_vid = tg_api(
                        "sendVideo",
                        data={
                            "chat_id": cid,
                            "caption": guide_msg[:1020],
                            "parse_mode": "HTML",
                            "reply_markup": reply_markup_json,
                            "supports_streaming": "true",
                            "width": "1440",
                            "height": "2560",
                        },
                        files=files_payload,
                        token=tok,
                    )
                finally:
                    if cov_fp is not None:
                        cov_fp.close()
                res_chat["video"] = r_vid.get("ok", False)
                if not r_vid.get("ok"):
                    res_chat["video_error"] = r_vid.get("description", "")

        # Mesaj 3: Kısa ve SEO Uyumlu %100 Saf Kopyala-Yapıştır Sosyal Medya Açıklaması (Sıfır Ekstra Başlık!)
        r_cap = tg_api(
            "sendMessage",
            data={
                "chat_id": cid,
                "text": pure_caption[:4000],
                "disable_web_page_preview": True,
            },
            token=tok,
        )
        res_chat["caption_copypaste"] = r_cap.get("ok", False)
        delivery_report[cid] = res_chat
        print(f"✅ [@songtraibot Teslimat -> {cid}]: {res_chat}")

    # Sıfır-Tekrar Çift Kilidini (Yerel + GitHub API) kilitle
    mark_song_used(song, sync_github=True)
    return delivery_report
