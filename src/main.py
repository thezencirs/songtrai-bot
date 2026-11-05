# -*- coding: utf-8 -*-
"""
Şarkıların Anlamı (@songtraibot) — Ana Orkestrasyon & Saatlik Stok Üretim Motoru
================================================================================
1) @songtraibot Telegram kuyruğunu kontrol eder (kullanıcının gönderdiği 10 dil komutu veya şarkı adını yakalar).
2) 10 Global Dil (İngilizce, Rusça, Japonca, Almanca, İspanyolca, Korece, Çince, İtalyanca, Fransızca, Hintçe)
   arasından Sıfır-Tekrar Çift Kilit ile popüler şarkıyı ve tertemiz edebi Türkçe çevirisini hazırlar.
3) Saf Beyaz Stüdyo (#FFFFFF) • Sıfır Uzay/AI İzi • Gerçek Plak & 2K QHD+ (1440x2560 @ 30 FPS) GraphMotion
   Reels videosunu üretir.
4) @songtraibot üzerinden:
   - Mesaj 1: 2K MP4 Video + Sosyal Medya Nakarat Saniyesi Eşleştirme Rehberi + 10 Dil Hızlı Üretim Butonları
   - Mesaj 2: %100 Saf Kopyala-Yapıştır Sosyal Medya Açıklaması (Sıfır ekstra başlık)
   olarak teslim eder.
"""

import argparse
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_team_registry import run_agent_team_pipeline_audit
from render_songtrai_reels import render_songtrai_graphmotion_reel
from song_catalog_10langs import (
    build_live_song_concept_from_query,
    select_next_song_concept,
)
from telegram_songtrai_ingestor import pop_next_telegram_song_request
from telegram_songtrai_publisher import (
    configure_songtrai_bot_profile,
    deliver_songtrai_package_to_telegram,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--language", default=os.environ.get("SONGTRAI_LANGUAGE", "otomatik"))
    parser.add_argument("--query", default=os.environ.get("SONGTRAI_QUERY", ""))
    parser.add_argument("--batch-count", type=int, default=int(os.environ.get("SONGTRAI_BATCH_COUNT", "1")))
    parser.add_argument("--output", default="output/songtrai_reel_final.mp4")
    parser.add_argument("--only-if-telegram-pending", action="store_true")
    parser.add_argument("--setup-bot", action="store_true")
    parser.add_argument("--no-telegram-publish", action="store_true")
    args = parser.parse_args()

    out_dir = os.path.dirname(args.output) or "output"
    os.makedirs(out_dir, exist_ok=True)

    if args.setup_bot:
        cfg = configure_songtrai_bot_profile()
        print(f"🤖 [@songtraibot Profil & 10 Dil Komut Yapılandırması]: {cfg}")

    pending_song = pop_next_telegram_song_request()
    if args.only_if_telegram_pending and pending_song is None:
        print("ℹ️ [Hızlı Telegram Kuyruk Kontrolü] @songtraibot üzerinde bekleyen yeni talep yok, adım tamamlandı.")
        return

    batch_n = max(1, min(10, args.batch_count))
    for b_idx in range(batch_n):
        if b_idx == 0 and pending_song is not None:
            song = pending_song
        elif b_idx == 0 and args.query.strip():
            song = build_live_song_concept_from_query(args.query.strip(), forced_lang=args.language)
        else:
            song = select_next_song_concept(force_language=args.language if b_idx == 0 else "otomatik")

        print(
            f"🎵 [{b_idx + 1}/{batch_n} Seçilen Şarkı]: {song['flag']} {song['language_tr']} — "
            f"{song['artist']} - {song['title']} ({song['id']})"
        )

        audit = run_agent_team_pipeline_audit(song)
        print(
            f"🤝 [8-Ajanlı Otonom Şarkı Çeviri Kadrosu]: {audit['active_agents_count']}/8 Ajan Aktif | "
            f"Stüdyo: {audit['studio_backdrop']} | Durum: {audit['overall_status']}"
        )

        mp4_path = args.output if batch_n == 1 else os.path.join(out_dir, f"songtrai_reel_{song['id']}.mp4")
        render_info = render_songtrai_graphmotion_reel(song, output_mp4=mp4_path)
        print(f"🎬 [2K Saf Beyaz Stüdyo GraphMotion Reels Hazır]: {render_info}")

        if not args.no_telegram_publish:
            deliver_songtrai_package_to_telegram(song, video_mp4_path=mp4_path, out_dir=out_dir)


if __name__ == "__main__":
    main()
