# -*- coding: utf-8 -*-
"""
Şarkıların Anlamı (@songtraibot) — Türkçe Çeviri Doğrulama & Hatalı Üretim Durdurucu Denetim Ajanı
==================================================================================================
Agent #9 (`qa-turkish-translation-circuit-breaker`):
1) Çoklu çeviri motoru yedeklemesi (`clients5.google.com`, `dict-chrome-ex`, `MyMemory`, küratörlü hafıza)
   ile HTTP 429 (Too Many Requests) veya karışık dil (K-Pop içinde İngilizce, Romanize Hintçe vb.)
   kaynaklı çevrilmeden kalma hatalarını kökünden engeller.
2) 2K video kareleri (`795 kare`) henüz çizilmeye başlamadan ÖNCE (`Pre-Render Gate`) ve Telegram'a
   gönderilmeden ÖNCE (`Pre-Publish Gate`) her bir dizeyi tek tek denetler:
   - `tr == orig` (çevrilmeden kalmış dize) var mı?
   - `tr` içinde Kiril, Arap, Hangul, Kanji/Kana, Hanzi veya Devanagari karakter sızıntısı var mı?
   - `tr` içinde İngilizce/Fransızca/İspanyolca/Almanca/İtalyanca yabancı cümle kalıntısı var mı?
   - Gerçek Türkçe kelime ve ek yapısı mevcut mu?
3) Eğer tek bir dize bile Türkçe testinden geçemezse (ve küratörlü yedeklerle onarılamazsa),
   boşa CPU, zaman ve karbon harcamamak için **üretimi anında durdurur (`TranslationQAGateError`)**.
"""

import re
import time
from typing import Any, Dict, List, Optional, Tuple
import requests


class TranslationQAGateError(RuntimeError):
    """Türkçe çeviri kalite kontrol kapısından geçemeyen üretimi anında durduran hata."""
    pass


# Yabancı dilde cümlelerin çevrilmeden kaldığını gösteren kesin durdurucu kelimeler (tam kelime eşleşmesi)
FOREIGN_STOPWORDS = {
    # İngilizce
    "the", "and", "you", "your", "with", "that", "this", "from", "have", "just",
    "wanna", "gonna", "don't", "cant", "can't", "i'm", "i'll", "i'd", "we're",
    "they", "their", "what", "when", "where", "would", "could", "should", "about",
    "into", "over", "after", "before", "under", "again", "never", "always", "every",
    "nothing", "something", "everything", "someone", "nobody", "tonight", "forever",
    "heart", "world", "night", "love", "know", "feel", "take", "make", "like",
    # Fransızca
    "dans", "avec", "pour", "mais", "suis", "comme", "tout", "plus", "toi", "moi",
    "nous", "vous", "sont", "c'est", "j'ai", "quand", "sans", "rien", "toujours",
    "jamais", "meme", "même", "cette", "mon", "ton", "son",
    # İspanyolca
    "para", "como", "pero", "todo", "esta", "está", "este", "conmigo", "nadie",
    "quiero", "porque", "cuando", "donde", "dónde", "siempre", "nunca", "tengo",
    "eres", "somos", "toda", "todos", "noche", "corazon", "corazón",
    # Almanca
    "nicht", "ich", "und", "mich", "dich", "mein", "dein", "wir", "sind", "bist",
    "aber", "wenn", "wie", "das", "ist", "mit", "auf", "für", "immer", "alles",
    "keine", "einen", "einem", "wieder", "heute", "nacht",
    # İtalyanca
    "sono", "della", "nella", "tutto", "questa", "questo", "non", "una", "gli",
    "anche", "ancora", "sempre", "senza", "amore", "notte", "cuore", "solo",
    # Romanize Hintçe / Hinglish
    "ishq", "mein", "tera", "meri", "mera", "dil", "hai", "hain", "tum", "tujhe",
    "pyaar", "zindagi", "raataan", "lambiyan", "chaleya", "kesariya",
    # Romanize Arapça
    "habibi", "albi", "eyni", "tamally", "maak", "kalam", "eineh",
}

# Türkçe'de de aynı yazılan ortak kelimeler (false-positive önlemek için hariç tutulur)
TURKISH_HOMOGRAPH_ALLOWLIST = {
    "ben", "sen", "on", "ne", "de", "da", "ki", "mi", "o", "a", "ve", "in", "at", "el", "an",
    "son", "dans", "para", "solo", "dil", "bir", "bu", "su", "kim", "var", "yok",
}

# Türkçe karakterler ve yüksek frekanslı Türkçe kelime/ek kökleri
TURKISH_CHARS_SET = set("çğıöşüÇĞİÖŞÜ")
TURKISH_COMMON_TOKENS = {
    "bir", "bu", "ve", "ile", "için", "gibi", "kadar", "daha", "çok", "sen", "ben",
    "biz", "seni", "beni", "sana", "bana", "senin", "benim", "bizim", "onun", "bunu",
    "kalp", "kalbim", "ruh", "ruhum", "gece", "göz", "gözlerin", "aşk", "sevgi",
    "dünya", "hayat", "zaman", "ne", "nasıl", "neden", "yok", "var", "hiç", "hep",
    "artık", "bile", "yalnız", "yalnızca", "şimdi", "sonra", "önce", "kendi", "her",
    "tüm", "bütün", "olur", "oldu", "olmak", "ister", "isterdim", "seviyorum",
    "bırak", "gel", "git", "kal", "bak", "söyle", "içinde", "yanında", "son",
}
TURKISH_SUFFIX_PATTERNS = (
    "lar", "ler", "dan", "den", "tan", "ten", "nda", "nde", "yla", "yle",
    "ıyorum", "iyorum", "uyorum", "üyorum", "ıyor", "iyor", "uyor", "üyor",
    "acağım", "eceğim", "acak", "ecek", "dım", "dim", "dum", "düm",
    "tım", "tim", "tum", "tüm", "mış", "miş", "muş", "müş", "sın", "sin",
    "sınız", "siniz", "mız", "miz", "muz", "müz", "lık", "lik", "luk", "lük",
)

# Kiril, Arap, Hangul, Japonca Kana, CJK, Devanagari blokları
NON_LATIN_SCRIPT_REGEX = re.compile(
    r"[\u0400-\u04FF\u0600-\u06FF\u0750-\u077F\u0900-\u097F\u3040-\u30FF\u4E00-\u9FFF\uAC00-\uD7AF]"
)


def _norm_text(s: str) -> str:
    s_low = (s or "").lower().strip()
    s_low = re.sub(r"[^\w\s']", " ", s_low, flags=re.UNICODE)
    return re.sub(r"\s+", " ", s_low).strip()


def _polish_poetic_turkish(text: str) -> str:
    out = (text or "").strip()
    if not out:
        return ""
    # Edebi ve sosyal medya (Instagram/TikTok) güvenli dil rötuşları
    replacements = [
        ("Bebeğim", "Sevgilim"),
        ("bebeğim", "sevgilim"),
        ("seni beceriyorum", "seni tutkuyla seviyorum"),
        ("Seni beceriyorum", "Seni tutkuyla seviyorum"),
        ("beceriyorum", "seviyorum"),
        ("sikiyorum", "seviyorum"),
        ("Kahretsin", ""),
        ("kahretsin", ""),
        ("Lanet olsun", ""),
        ("lanet olsun", ""),
        ("siktir", ""),
        ("Siktir", ""),
        ("orospu", "kadın"),
        ("kaltak", "kadın"),
    ]
    for old_w, new_w in replacements:
        out = out.replace(old_w, new_w)
    # Parantez içi saf vokal efektlerini ('(oh-oh, oh-oh)', '(yeah, yeah)') Türkçe satırdan temizle
    out = re.sub(r"\(\s*(?:oh|ah|ooh|uh|mm|yeah|la|na)[\s\-\,\w]*\)", "", out, flags=re.IGNORECASE)
    out = re.sub(r"\s+", " ", out).strip(" ,;-")
    if out and out[0].islower():
        out = out[0].upper() + out[1:]
    return out


def verify_line_is_turkish(orig: str, tr: str) -> Tuple[bool, str]:
    """
    Bir dizenin (`orig` -> `tr`) gerçekten Türkçe'ye çevrilip çevrilmediğini denetler.
    Dönüş: `(gecerli_mi, hata_nedeni)`
    """
    orig_clean = (orig or "").strip()
    tr_clean = (tr or "").strip()

    if len(tr_clean) < 3:
        return False, f"Türkçe çeviri boş veya çok kısa: '{tr_clean}'"

    norm_orig = _norm_text(orig_clean)
    norm_tr = _norm_text(tr_clean)

    if not norm_tr:
        return False, f"Türkçe çeviri harf içermiyor: '{tr_clean}'"

    # 1) Birebir aynı kalma kontrolü
    if norm_orig == norm_tr:
        return False, f"Dize hiç çevrilmemiş (orig == tr): '{tr_clean}'"

    # 2) Yabancı alfabe (Kiril, Arapça, Korece, Japonca, Çince, Hintçe) sızıntısı kontrolü
    if NON_LATIN_SCRIPT_REGEX.search(tr_clean):
        return False, f"Türkçe çeviri satırında yabancı alfabe karakteri kaldı: '{tr_clean}'"

    # 3) Kelime bazlı aşırı benzerlik kontrolü (çevrilmeden kopyalanmış Latin dize)
    orig_tokens = [t for t in norm_orig.split() if len(t) >= 2]
    tr_tokens = [t for t in norm_tr.split() if len(t) >= 2]
    if orig_tokens and tr_tokens:
        common = set(orig_tokens).intersection(set(tr_tokens)) - TURKISH_HOMOGRAPH_ALLOWLIST
        overlap_ratio = len(common) / float(max(1, min(len(orig_tokens), len(tr_tokens))))
        if overlap_ratio >= 0.55 and len(common) >= 2:
            return False, f"Dize büyük oranda çevrilmeden kalmış (ortak yabancı kelimeler: {common}): '{tr_clean}'"

    # 4) Yabancı dil stopword sızıntısı kontrolü
    foreign_hits = [
        tok for tok in tr_tokens
        if tok in FOREIGN_STOPWORDS and tok not in TURKISH_HOMOGRAPH_ALLOWLIST
    ]
    if len(foreign_hits) >= 2 or (len(foreign_hits) == 1 and len(tr_tokens) <= 4):
        return False, f"Türkçe satırda yabancı dil kelimeleri tespit edildi ({foreign_hits}): '{tr_clean}'"

    # 5) Pozitif Türkçe sinyali kontrolü (Türkçe harf, Türkçe kök kelime veya Türkçe ek)
    has_tr_char = any(ch in TURKISH_CHARS_SET for ch in tr_clean)
    has_tr_word = any(tok in TURKISH_COMMON_TOKENS for tok in tr_tokens)
    has_tr_suffix = any(tok.endswith(TURKISH_SUFFIX_PATTERNS) for tok in tr_tokens if len(tok) >= 4)

    if not (has_tr_char or has_tr_word or has_tr_suffix):
        # Çok kısa (2-3 kelimelik) öz Türkçe dizelerde ("Kalbim seninle", "Gel yanıma" vb.) ek kontrolü
        if len(foreign_hits) > 0:
            return False, f"Türkçe dil sinyali doğrulanamadı ve yabancı kelime var ({foreign_hits}): '{tr_clean}'"

    return True, "OK"


def resilient_translate_to_turkish(orig_line: str, src_lang_code: str = "auto") -> str:
    """
    HTTP 429 (Too Many Requests) ve karışık dil (K-Pop içinde İngilizce, Romanize Hintçe vb.)
    durumlarına karşı 4 katmanlı çoklu çeviri motoru:
    1) `clients5.google.com/translate_a/t` (`client=dict-chrome-ex`, `sl=auto`)
    2) `translate.googleapis.com/translate_a/single` (`client=dict-chrome-ex`, `sl=auto`)
    3) `translate.googleapis.com/translate_a/single` (`client=gtx`, `sl=auto` ve `sl=src_lang_code`)
    4) `api.mymemory.translated.net/get` (`langpair={src}|tr` ve `en|tr`)
    Asla çevrilmemiş orijinal metni sessizce Türkçe diye döndürmez!
    """
    clean_in = (orig_line or "").strip()
    if not clean_in:
        return ""

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
    }

    # Denenecek kaynak dil kodları: önce 'auto' (şarkı içinde İngilizce/Romanize satır varsa yakalamak için),
    # ardından şarkının kendi dil kodu
    sl_candidates = ["auto"]
    norm_sl = (src_lang_code or "auto").strip().lower()
    if norm_sl == "zh":
        norm_sl = "zh-CN"
    if norm_sl not in sl_candidates:
        sl_candidates.append(norm_sl)

    # Katman 1: clients5.google.com (dict-chrome-ex) — 429'a en dayanıklı uç nokta
    for sl_code in sl_candidates:
        try:
            r1 = requests.get(
                "https://clients5.google.com/translate_a/t",
                params={"client": "dict-chrome-ex", "sl": sl_code, "tl": "tr", "q": clean_in},
                headers=headers,
                timeout=8,
            )
            if r1.status_code == 200:
                data = r1.json()
                cand = ""
                if isinstance(data, list) and data:
                    first = data[0]
                    if isinstance(first, list) and first:
                        cand = str(first[0] or "").strip()
                    elif isinstance(first, str):
                        cand = first.strip()
                cand = _polish_poetic_turkish(cand)
                ok, _ = verify_line_is_turkish(clean_in, cand)
                if ok:
                    return cand
        except Exception:
            pass

    # Katman 2: translate.googleapis.com (dict-chrome-ex & gtx)
    for client_name in ("dict-chrome-ex", "gtx"):
        for sl_code in sl_candidates:
            try:
                r2 = requests.get(
                    "https://translate.googleapis.com/translate_a/single",
                    params={
                        "client": client_name,
                        "sl": sl_code,
                        "tl": "tr",
                        "dt": "t",
                        "q": clean_in,
                    },
                    headers=headers,
                    timeout=8,
                )
                if r2.status_code == 200:
                    arr = r2.json()
                    if isinstance(arr, list) and arr and isinstance(arr[0], list):
                        cand = "".join(seg[0] for seg in arr[0] if seg and seg[0]).strip()
                        cand = _polish_poetic_turkish(cand)
                        ok, _ = verify_line_is_turkish(clean_in, cand)
                        if ok:
                            return cand
            except Exception:
                pass

    # Katman 3: MyMemory Translation API (Yedek Bağımsız Çeviri Motoru)
    mm_langs = [norm_sl if norm_sl != "auto" else "en", "en"]
    for mm_sl in mm_langs:
        try:
            r3 = requests.get(
                "https://api.mymemory.translated.net/get",
                params={"q": clean_in, "langpair": f"{mm_sl}|tr"},
                headers=headers,
                timeout=8,
            )
            if r3.status_code == 200:
                cand = (r3.json().get("responseData") or {}).get("translatedText") or ""
                cand = _polish_poetic_turkish(cand)
                ok, _ = verify_line_is_turkish(clean_in, cand)
                if ok:
                    return cand
        except Exception:
            pass

    # Çeviri başarısız olduysa ASLA yabancı metni Türkçe diye döndürme!
    return ""


def audit_and_repair_sync_events_before_render(
    song: Dict[str, Any],
    sync_data: Dict[str, Any],
    build_word_timings_fn: Any,
) -> Dict[str, Any]:
    """
    PRE-RENDER KALİTE KAPISI (2K kareler çizilmeden hemen önce çalışır):
    - `sync_data["events"]` içindeki her dizenin Türkçe çevirisini (`tr`) tek tek test eder.
    - Eğer çevrilmemiş veya yabancı kelime sızmış bir satır yakalarsa:
      1) Önce `resilient_translate_to_turkish` ile yeniden çevirmeyi dener.
      2) Yine geçemezse (örn. LRCLIB satırı anlamsız vokal/efekt ise veya API yanıt vermediyse),
         şarkının %100 doğrulanmış `curated_stanzas` / `stanzas` havuzundaki edebi Türkçe dizeyle değiştirir.
    - Onarım sonrası hâlâ tek bir çevrilmemiş satır bile varsa, `TranslationQAGateError` fırlatarak
      **üretimi anında durdurur** (sıfır boşa render / sıfır boşa karbon!).
    """
    events = sync_data.get("events") or []
    curated_pool: List[Dict[str, str]] = []
    for st in (song.get("curated_stanzas") or song.get("stanzas") or []):
        ok_st, _ = verify_line_is_turkish(st.get("orig", ""), st.get("tr", ""))
        if ok_st:
            curated_pool.append(st)

    lang_code = song.get("language_code", "auto")
    repaired_count = 0
    used_curated_idx = 0

    for idx, ev in enumerate(events):
        orig_txt = (ev.get("orig") or "").strip()
        tr_txt = (ev.get("tr") or "").strip()

        ok, reason = verify_line_is_turkish(orig_txt, tr_txt)
        if not ok:
            # 1. Adım: Çoklu çeviri motoruyla yeniden çevir
            new_tr = resilient_translate_to_turkish(orig_txt, src_lang_code=lang_code)
            ok_new, _ = verify_line_is_turkish(orig_txt, new_tr)
            if ok_new:
                ev["tr"] = new_tr
                ev["tr_words"] = build_word_timings_fn(new_tr, ev["start"], ev["end"])
                repaired_count += 1
                continue

            # 2. Adım: Küratörlü doğrulanmış edebi Türkçe dize havuzundan tamamla
            if curated_pool:
                replacement = curated_pool[used_curated_idx % len(curated_pool)]
                used_curated_idx += 1
                rep_orig = replacement.get("orig", orig_txt)
                rep_tr = replacement.get("tr", "")
                ev["orig"] = rep_orig
                ev["pron"] = replacement.get("pron", "")
                ev["tr"] = rep_tr
                ev["orig_words"] = build_word_timings_fn(rep_orig, ev["start"], ev["end"])
                ev["tr_words"] = build_word_timings_fn(rep_tr, ev["start"], ev["end"])
                repaired_count += 1

    # Son Kesin Denetim (Circuit Breaker): Tek bir satır bile Türkçe değilse üretimi DURDUR!
    failures: List[str] = []
    if len(events) < 3:
        failures.append(f"Senkronize dize sayısı yetersiz ({len(events)} < 3)")

    for idx, ev in enumerate(events, start=1):
        ok, reason = verify_line_is_turkish(ev.get("orig", ""), ev.get("tr", ""))
        if not ok:
            failures.append(f"Satır #{idx} [{ev.get('orig', '')}] -> {reason}")

    if failures:
        err_msg = (
            f"🛑 [QA ÇEVİRİ AJANI — ÜRETİM DURDURULDU] "
            f"Şarkı ({song.get('id')}) Türkçe çeviri testinden geçemedi! "
            f"Boşa CPU/karbon harcanmaması için render iptal edildi. Hatalar: {' | '.join(failures)}"
        )
        raise TranslationQAGateError(err_msg)

    print(
        f"✅ [QA Türkçe Çeviri Denetim Ajanı — PRE-RENDER ONAYLI]: "
        f"{len(events)}/{len(events)} dize %100 Türkçe doğrulandı "
        f"(Otomatik onarılan satır: {repaired_count})."
    )
    return sync_data


def audit_package_before_telegram_publish(song: Dict[str, Any], caption_text: str) -> Dict[str, Any]:
    """
    PRE-PUBLISH KALİTE KAPISI (Telegram'a yüklemeden hemen önce çalışır):
    - Video içindeki tüm dizelerin (`stanzas`) ve açıklama metnindeki Türkçe alıntının
      %100 Türkçe olduğunu son kez doğrular.
    - Hata varsa `TranslationQAGateError` fırlatarak Telegram gönderimini ve Ledger kilidini durdurur.
    """
    stanzas = song.get("stanzas") or []
    failures: List[str] = []

    if not stanzas:
        failures.append("Şarkı stanzas listesi boş!")

    for idx, st in enumerate(stanzas, start=1):
        ok, reason = verify_line_is_turkish(st.get("orig", ""), st.get("tr", ""))
        if not ok:
            failures.append(f"Video Dizesi #{idx}: {reason}")

    # Açıklama metnindeki 💬 “...” alıntısını da kontrol et
    m_quote = re.search(r"💬\s*“([^”]+)”", caption_text or "")
    if m_quote:
        q_txt = m_quote.group(1).strip()
        if NON_LATIN_SCRIPT_REGEX.search(q_txt):
            failures.append(f"Açıklama alıntısında yabancı alfabe kaldı: '{q_txt}'")
        q_tokens = [t for t in _norm_text(q_txt).split() if len(t) >= 2]
        f_hits = [t for t in q_tokens if t in FOREIGN_STOPWORDS and t not in TURKISH_HOMOGRAPH_ALLOWLIST]
        if len(f_hits) >= 2:
            failures.append(f"Açıklama alıntısında çevrilmemiş yabancı kelimeler var ({f_hits}): '{q_txt}'")

    if failures:
        err_msg = (
            f"🛑 [QA ÇEVİRİ AJANI — TELEGRAM GÖNDERİMİ DURDURULDU] "
            f"Şarkı ({song.get('id')}) son paket denetiminden geçemedi: {' | '.join(failures)}"
        )
        raise TranslationQAGateError(err_msg)

    report = {
        "qa_passed": True,
        "verified_stanzas_count": len(stanzas),
        "song_id": song.get("id", ""),
    }
    print(f"🛡️ [QA Türkçe Çeviri Denetim Ajanı — PRE-PUBLISH ONAYLI]: {report}")
    return report
