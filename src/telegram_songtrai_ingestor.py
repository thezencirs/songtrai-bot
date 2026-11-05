# -*- coding: utf-8 -*-
"""
Şarkıların Anlamı (@songtraibot) — Telegram İstek, 10 Dil Komutu & Özel Şarkı Yakalayıcı Motoru
================================================================================================
- Bot: @songtraibot
- Token: 8824304361:AAFeGn-3yjGbd_YA-80GHo3wS6p2v-b-pRA
- Kullanıcı bota:
  * `/uret` veya `/ingilizce`, `/rusca`, `/japonca`, `/almanca`, `/ispanyolca`, `/korece`,
    `/cince`, `/italyanca`, `/fransizca`, `/hintce` komutu gönderdiğinde,
  * Videonun altındaki 10 dilden birinin butonuna tıkladığında,
  * Veya herhangi bir şarkı adı / sanatçı / söz yazdığında (Örn: "Indila Derniere Danse" veya "Adele Someone Like You")
  anında kuyruğa alır ve 2K Saf Beyaz Stüdyo Türkçe Çeviri videosunu hazırlar.
"""

import base64
import datetime
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from song_catalog_10langs import (
    BASE_DIR,
    GITHUB_REPO_SLUG,
    LANGUAGE_ALIASES,
    build_live_song_concept_from_query,
    normalize_language_key,
    select_next_song_concept,
)

DEFAULT_BOT_TOKEN = "8824304361:AAFeGn-3yjGbd_YA-80GHo3wS6p2v-b-pRA"
DEFAULT_ADMIN_CHAT_ID = "995164733"

TG_QUEUE_PATH = BASE_DIR / "output" / "telegram_pending_queue.json"
TG_OFFSET_PATH = BASE_DIR / "output" / "telegram_update_offset.json"
SUBSCRIBERS_FILE = BASE_DIR / "assets" / "telegram_subscribers.json"


def get_bot_token() -> str:
    return os.environ.get("TELEGRAM_BOT_TOKEN", DEFAULT_BOT_TOKEN).strip()


def tg_call(method: str, payload: Optional[Dict[str, Any]] = None, timeout: int = 20) -> Dict[str, Any]:
    tok = get_bot_token()
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{tok}/{method}",
            json=payload or {},
            timeout=timeout,
        )
        return r.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}


def register_subscriber(chat_id: str, user_info: Dict[str, Any]) -> None:
    os.makedirs(SUBSCRIBERS_FILE.parent, exist_ok=True)
    data: Dict[str, Any] = {"chats": {}}
    if SUBSCRIBERS_FILE.exists():
        try:
            data = json.loads(SUBSCRIBERS_FILE.read_text(encoding="utf-8"))
        except Exception:
            data = {"chats": {}}
    if "chats" not in data or not isinstance(data["chats"], dict):
        data["chats"] = {}
    data["chats"][str(chat_id)] = {
        "username": user_info.get("username", ""),
        "first_name": user_info.get("first_name", ""),
        "updated_at": datetime.datetime.utcnow().isoformat() + "Z",
    }
    SUBSCRIBERS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_tg_queue() -> List[Dict[str, Any]]:
    os.makedirs(TG_QUEUE_PATH.parent, exist_ok=True)
    queue: List[Dict[str, Any]] = []
    seen = set()
    if TG_QUEUE_PATH.exists():
        try:
            items = json.loads(TG_QUEUE_PATH.read_text(encoding="utf-8"))
            if isinstance(items, list):
                for it in items:
                    rid = it.get("request_id")
                    if rid and rid not in seen:
                        queue.append(it)
                        seen.add(rid)
        except Exception:
            pass

    gh_token = os.environ.get("GH_TOKEN", "").strip()
    if gh_token:
        try:
            r = requests.get(
                f"https://api.github.com/repos/{GITHUB_REPO_SLUG}/contents/output/telegram_pending_queue.json",
                headers={"Authorization": f"Bearer {gh_token}", "Accept": "application/vnd.github+json"},
                timeout=10,
            )
            if r.status_code == 200:
                b64 = r.json().get("content", "")
                remote_items = json.loads(base64.b64decode(b64).decode("utf-8"))
                if isinstance(remote_items, list):
                    for it in remote_items:
                        rid = it.get("request_id")
                        if rid and rid not in seen:
                            queue.append(it)
                            seen.add(rid)
        except Exception:
            pass
    return queue


def save_tg_queue(queue: List[Dict[str, Any]], sync_github: bool = True) -> None:
    os.makedirs(TG_QUEUE_PATH.parent, exist_ok=True)
    raw = json.dumps(queue, ensure_ascii=False, indent=2)
    TG_QUEUE_PATH.write_text(raw, encoding="utf-8")

    gh_token = os.environ.get("GH_TOKEN", "").strip()
    if sync_github and gh_token:
        try:
            api_url = f"https://api.github.com/repos/{GITHUB_REPO_SLUG}/contents/output/telegram_pending_queue.json"
            headers = {"Authorization": f"Bearer {gh_token}", "Accept": "application/vnd.github+json"}
            get_r = requests.get(api_url, headers=headers, timeout=10)
            payload: Dict[str, Any] = {
                "message": "chore(songtraibot): sync telegram pending song queue [skip ci]",
                "content": base64.b64encode(raw.encode("utf-8")).decode("ascii"),
            }
            if get_r.status_code == 200 and get_r.json().get("sha"):
                payload["sha"] = get_r.json()["sha"]
            requests.put(api_url, headers=headers, json=payload, timeout=12)
        except Exception:
            pass


def _load_last_offset() -> int:
    if TG_OFFSET_PATH.exists():
        try:
            return int(json.loads(TG_OFFSET_PATH.read_text(encoding="utf-8")).get("offset", 0))
        except Exception:
            pass
    return 0


def _save_last_offset(offset: int) -> None:
    os.makedirs(TG_OFFSET_PATH.parent, exist_ok=True)
    TG_OFFSET_PATH.write_text(json.dumps({"offset": offset}), encoding="utf-8")


def poll_and_enqueue_telegram_requests(acknowledge: bool = True) -> List[Dict[str, Any]]:
    """@songtraibot üzerindeki yeni mesaj ve buton tıklamalarını kontrol edip kuyruğa ekler."""
    last_offset = _load_last_offset()
    resp = tg_call("getUpdates", {"offset": last_offset + 1, "timeout": 2})
    if not resp.get("ok"):
        return load_tg_queue()

    updates = resp.get("result") or []
    if not updates:
        return load_tg_queue()

    queue = load_tg_queue()
    seen_ids = {q.get("request_id") for q in queue}
    max_uid = last_offset

    for upd in updates:
        uid = int(upd.get("update_id", 0))
        if uid > max_uid:
            max_uid = uid

        # 1) Inline Buton Tıklaması (Örn: gen_lang:rusca)
        cb = upd.get("callback_query")
        if cb:
            cb_id = cb.get("id")
            data_str = str(cb.get("data", ""))
            msg = cb.get("message") or {}
            chat = msg.get("chat") or {}
            cid = str(chat.get("id") or DEFAULT_ADMIN_CHAT_ID)
            register_subscriber(cid, cb.get("from") or {})

            if cb_id:
                tg_call("answerCallbackQuery", {"callback_query_id": cb_id, "text": "🎬 2K Saf Beyaz Stüdyo Şarkı Çevirisi Hazırlanıyor..."})

            if data_str.startswith("gen_lang:"):
                lang_req = data_str.split(":", 1)[1].strip()
                req_id = f"cb_{uid}_{cid}"
                if req_id not in seen_ids:
                    queue.append({
                        "request_id": req_id,
                        "requester_chat_id": cid,
                        "type": "language_command",
                        "language": lang_req,
                        "query": "",
                        "created_at": time.time(),
                    })
                    seen_ids.add(req_id)
            continue

        # 2) Normal Mesaj / Komut
        msg = upd.get("message") or upd.get("edited_message")
        if not msg:
            continue
        chat = msg.get("chat") or {}
        cid = str(chat.get("id") or DEFAULT_ADMIN_CHAT_ID)
        register_subscriber(cid, msg.get("from") or {})

        text = str(msg.get("text") or msg.get("caption") or "").strip()
        if not text:
            continue

        clean_cmd = text.lower().split()[0].lstrip("/").split("@")[0]
        if clean_cmd == "start":
            if acknowledge:
                tg_call(
                    "sendMessage",
                    {
                        "chat_id": cid,
                        "parse_mode": "HTML",
                        "text": (
                            "🎵 <b>Şarkıların Anlamı (@songtraibot) — 2K Saf Beyaz Stüdyo Şarkı Çeviri Otomasyonu</b>\n\n"
                            "🌍 <b>10 Global Dil Desteği:</b> İngilizce, Rusça, Japonca, Almanca, İspanyolca, Korece, Çince, İtalyanca, Fransızca ve Hintçe.\n"
                            "✨ <b>Görsel Standart:</b> Saf Beyaz Stüdyo (#FFFFFF) • Sıfır Uzay/AI İzi • Gerçek Plak & 2K GraphMotion.\n\n"
                            "👇 <b>Hemen Üretmek İçin:</b>\n"
                            "• /uret — Sıradaki popüler şarkıyı üret\n"
                            "• /ingilizce • /rusca • /japonca • /almanca • /ispanyolca\n"
                            "• /korece • /cince • /italyanca • /fransizca • /hintce\n"
                            "• Veya istediğiniz <b>Sanatçı - Şarkı Adını</b> doğrudan mesaj olarak yazın!"
                        ),
                    },
                )
            continue

        req_id = f"msg_{uid}_{cid}"
        if req_id in seen_ids:
            continue

        if clean_cmd in ("uret", "üret", "otomatik") or clean_cmd in LANGUAGE_ALIASES:
            lang_key = "otomatik" if clean_cmd in ("uret", "üret", "otomatik") else normalize_language_key(clean_cmd)
            extra_arg = text[len(text.split()[0]):].strip()
            queue.append({
                "request_id": req_id,
                "requester_chat_id": cid,
                "type": "custom_song" if extra_arg else "language_command",
                "language": lang_key,
                "query": extra_arg,
                "created_at": time.time(),
            })
            seen_ids.add(req_id)
            if acknowledge:
                tg_call(
                    "sendMessage",
                    {
                        "chat_id": cid,
                        "parse_mode": "HTML",
                        "text": f"🎬 <b>Talebiniz Alındı!</b> Saf Beyaz Stüdyo 2K Türkçe Şarkı Çevirisi hazırlanıyor ({lang_key.upper()})...",
                    },
                )
        else:
            # Kullanıcı doğrudan bir şarkı adı / sanatçı yazdı
            queue.append({
                "request_id": req_id,
                "requester_chat_id": cid,
                "type": "custom_song",
                "language": "otomatik",
                "query": text,
                "created_at": time.time(),
            })
            seen_ids.add(req_id)
            if acknowledge:
                tg_call(
                    "sendMessage",
                    {
                        "chat_id": cid,
                        "parse_mode": "HTML",
                        "text": f"🎵 <b>“{text[:60]}”</b> için Saf Beyaz Stüdyo 2K Türkçe Çeviri Reels videosu hazırlanıyor...",
                    },
                )

    _save_last_offset(max_uid)
    save_tg_queue(queue, sync_github=True)
    return queue


def pop_next_telegram_song_request() -> Optional[Dict[str, Any]]:
    """Kuyrukta bekleyen kullanıcı talebi varsa çekip şarkı konseptine dönüştürür."""
    queue = poll_and_enqueue_telegram_requests(acknowledge=True)
    if not queue:
        return None

    req = queue.pop(0)
    save_tg_queue(queue, sync_github=True)

    cid = str(req.get("requester_chat_id") or DEFAULT_ADMIN_CHAT_ID)
    req_type = req.get("type", "language_command")
    lang_key = req.get("language", "otomatik")
    query_txt = str(req.get("query") or "").strip()

    if req_type == "custom_song" and query_txt:
        return build_live_song_concept_from_query(query_txt, forced_lang=lang_key, requester_chat_id=cid)

    song = select_next_song_concept(force_language=lang_key)
    song["requester_chat_id"] = cid
    return song
