# -*- coding: utf-8 -*-
"""
Şarkıların Anlamı (@songtraibot) — 10 Dilde Popüler Şarkı & Edebi Türkçe Çeviri Kütüphanesi
===========================================================================================
Desteklenen 10 Global Dil:
1) İngilizce (ingilizce / en) 🇬🇧
2) Rusça (rusca / ru) 🇷🇺
3) Japonca (japonca / ja) 🇯🇵
4) Almanca (almanca / de) 🇩🇪
5) İspanyolca (ispanyolca / es) 🇪🇸
6) Korece (korece / ko) 🇰🇷
7) Çince (cince / zh) 🇨🇳
8) İtalyanca (italyanca / it) 🇮🇹
9) Fransızca (fransizca / fr) 🇫🇷
10) Hintçe (hintce / hi) 🇮🇳

Her şarkı paketi:
- Gerçek resmi albüm kapağı arama terimi (`itunes_query`)
- Sosyal medyada paylaşırken eklenecek tam nakarat saniyesi (`chorus_timestamp`) ve ses arama adı (`social_audio_search`)
- 4 ikonik nakarat dizesi (`stanzas`):
  * `orig`: Orijinal dildeki/alfabedeki söz
  * `pron`: Türkçe okunuş rehberi
  * `tr`: Robotik çeviriden uzak, şiirsel ve tertemiz Türkçe çeviri
  * `highlight`: Altın vurgu çizgisiyle öne çıkarılacak anahtar Türkçe ifade
  * `note`: Dizenin taşıdığı derin duygusal/kültürel alt anlam
içerir.
"""

import base64
import datetime
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

BASE_DIR = Path(__file__).resolve().parent.parent
LEDGER_PATH = BASE_DIR / "output" / "zero_repeat_ledger.json"
GITHUB_REPO_SLUG = os.environ.get("SONGTRAI_GITHUB_REPO", "thezencirs/songtrai-bot")

LANGUAGE_ALIASES: Dict[str, str] = {
    "ingilizce": "ingilizce",
    "english": "ingilizce",
    "en": "ingilizce",
    "rusca": "rusca",
    "rusça": "rusca",
    "russian": "rusca",
    "ru": "rusca",
    "japonca": "japonca",
    "japanese": "japonca",
    "ja": "japonca",
    "jp": "japonca",
    "almanca": "almanca",
    "german": "almanca",
    "de": "almanca",
    "ispanyolca": "ispanyolca",
    "spanish": "ispanyolca",
    "es": "ispanyolca",
    "korece": "korece",
    "korean": "korece",
    "kpop": "korece",
    "ko": "korece",
    "kr": "korece",
    "cince": "cince",
    "çince": "cince",
    "chinese": "cince",
    "zh": "cince",
    "cn": "cince",
    "italyanca": "italyanca",
    "italian": "italyanca",
    "it": "italyanca",
    "fransizca": "fransizca",
    "fransızca": "fransizca",
    "french": "fransizca",
    "fr": "fransizca",
    "hintce": "hintce",
    "hintçe": "hintce",
    "hindi": "hintce",
    "hi": "hintce",
    "in": "hintce",
    "arapca": "arapca",
    "arapça": "arapca",
    "arabic": "arapca",
    "ar": "arapca",
}

LANGUAGE_META: Dict[str, Dict[str, str]] = {
    "ingilizce": {"code": "EN", "name_tr": "İngilizce", "flag": "🇬🇧", "tag": "#ingilizceşarkılar #şarkıçevirileri"},
    "arapca": {"code": "AR", "name_tr": "Arapça", "flag": "🇸🇦", "tag": "#arapçaşarkılar #arapçaceviri"},
    "rusca": {"code": "RU", "name_tr": "Rusça", "flag": "🇷🇺", "tag": "#rusçaşarkılar #rusçaceviri"},
    "japonca": {"code": "JA", "name_tr": "Japonca", "flag": "🇯🇵", "tag": "#japoncaşarkılar #jpop #animeost"},
    "almanca": {"code": "DE", "name_tr": "Almanca", "flag": "🇩🇪", "tag": "#almancaşarkılar #deutschpop"},
    "ispanyolca": {"code": "ES", "name_tr": "İspanyolca", "flag": "🇪🇸", "tag": "#ispanyolcaşarkılar #latinpop"},
    "korece": {"code": "KO", "name_tr": "Korece", "flag": "🇰🇷", "tag": "#koreceşarkılar #kpopceviri #kdrama"},
    "cince": {"code": "ZH", "name_tr": "Çince", "flag": "🇨🇳", "tag": "#çinceşarkılar #cpophits"},
    "italyanca": {"code": "IT", "name_tr": "İtalyanca", "flag": "🇮🇹", "tag": "#italyancaşarkılar #italiana"},
    "fransizca": {"code": "FR", "name_tr": "Fransızca", "flag": "🇫🇷", "tag": "#fransızcaşarkılar #chanson"},
    "hintce": {"code": "HI", "name_tr": "Hintçe", "flag": "🇮🇳", "tag": "#hintçeşarkılar #bollywoodsongs"},
}

# İngilizce popüler şarkılara yüksek ağırlık (%50 İngilizce + %50 diğer 10 global dil rotasyonu)
LANGUAGE_ROTATION_ORDER: List[str] = [
    "ingilizce",
    "arapca",
    "ingilizce",
    "fransizca",
    "ingilizce",
    "rusca",
    "ingilizce",
    "ispanyolca",
    "ingilizce",
    "korece",
    "ingilizce",
    "japonca",
    "ingilizce",
    "italyanca",
    "ingilizce",
    "almanca",
    "cince",
    "hintce",
]


SONG_MASTER_CATALOG: List[Dict[str, Any]] = [
    # =========================================================================
    # 1. FRANSIZCA (FR) 🇫🇷
    # =========================================================================
    {
        "id": "fr_indila_derniere_danse",
        "language": "fransizca",
        "language_code": "FR",
        "language_tr": "Fransızca",
        "flag": "🇫🇷",
        "artist": "Indila",
        "title": "Dernière Danse",
        "release_year": "2013",
        "itunes_query": "Indila Derniere Danse",
        "chorus_timestamp": "0:41 - 0:56 (Nakarat Başlangıcı)",
        "social_audio_search": "Indila - Dernière Danse",
        "cover_kicker": "🇫🇷 FRANSIZCA EFSANE • GERÇEK ANLAMI",
        "cover_headline": "YILLARDIR DİNLEDİĞİMİZ BU ŞARKI ASLINDA NE ANLATIYOR?",
        "viral_hook": "Melodisiyle herkesi büyüleyen 'Dernière Danse', aslında toplum tarafından dışlanan yalnız bir ruhun acısını unutup fırtınaya karışarak yaptığı son dansı anlatır.",
        "stanzas": [
            {
                "orig": "Oh ma douce souffrance, pourquoi s'acharner tu recommences ?",
                "pron": "O ma dus sufrans, purkua saşarne tü rökomans",
                "tr": "Ah benim tatlı sızım, neden bu kadar acımasızca yeniden başlıyorsun?",
                "highlight": "Ah benim tatlı sızım",
                "note": "Acısına o kadar alışmıştır ki onu artık 'tatlı bir sızı' ve eski bir dost gibi karşılar.",
            },
            {
                "orig": "Je ne suis qu'un être sans importance, sans lui je suis un peu paro",
                "pron": "Jö nö süi kön etr sanz emportans, san lüi jö süi ön pö paro",
                "tr": "Ben yalnızca önemsiz bir varlığım; o yanımda yokken biraz savunmasız ve ürkeğim.",
                "highlight": "o yanımda yokken biraz savunmasız",
                "note": "Kalabalık Paris sokaklarında sevdiği olmadan kendini görünmez hisseder.",
            },
            {
                "orig": "Je déambule seule dans le métro, une dernière danse",
                "pron": "Jö deambül söl dan lö metro, ün derniyer dans",
                "tr": "Metroda yapayalnız amaçsızca yürüyorum; kalbimdeki kederi unutmak için son bir dans...",
                "highlight": "kederi unutmak için son bir dans",
                "note": "Metro tüneli, iç dünyasındaki karanlık ve sıkışmışlık hissinin metaforudur.",
            },
            {
                "orig": "Je veux m'enfuir que tout recommence, oh ma douce souffrance",
                "pron": "Jö vö manfüir kö tu rökomans, o ma dus sufrans",
                "tr": "Çok uzaklara kaçıp her şeyin sıfırdan başlamasını istiyorum; ah benim tatlı sızım.",
                "highlight": "her şeyin sıfırdan başlamasını istiyorum",
                "note": "Son dans bir pes ediş değil, küllerinden yeniden doğma arzusudur.",
            },
        ],
    },
    {
        "id": "fr_stromae_papaoutai",
        "language": "fransizca",
        "language_code": "FR",
        "language_tr": "Fransızca",
        "flag": "🇫🇷",
        "artist": "Stromae",
        "title": "Papaoutai",
        "release_year": "2013",
        "itunes_query": "Stromae Papaoutai",
        "chorus_timestamp": "0:51 - 1:06 (Ana Nakarat)",
        "social_audio_search": "Stromae - Papaoutai",
        "cover_kicker": "🇫🇷 DANS EDİLİRKEN AĞLATAN FRANSIZCA ŞARKI",
        "cover_headline": "EĞLENCELİ SANILAN BU ŞARKININ HİKAYESİ KALBİNİZİ KIRACAK",
        "viral_hook": "Stromae bu hareketli şarkıyı, Ruanda soykırımında kaybettiği ve çocukluğu boyunca yolunu gözlediği babasına duyduğu tarifsiz özlem için yazmıştır. 'Papaoutai', çocuk ağzıyla 'Baba neredesin?' demektir.",
        "stanzas": [
            {
                "orig": "Dites-moi d'où il vient, enfin je saurai où je vais",
                "pron": "Dit-mua du il viyen, anfen jö sore u jö ve",
                "tr": "Bana onun nereden geldiğini söyleyin; ancak o zaman hayatta nereye gideceğimi bileceğim.",
                "highlight": "nereye gideceğimi bileceğim",
                "note": "Köklerini ve babasını tanımadan kendi kimliğini tamamlayamayan bir çocuğun çığlığı.",
            },
            {
                "orig": "Maman dit que lorsqu'on cherche bien, on finit toujours par trouver",
                "pron": "Maman di kö lorskon şerş biyen, on fini tujur par truve",
                "tr": "Annem der ki: 'İnsan gerçekten dikkatlice ararsa, sonunda mutlaka bulur.'",
                "highlight": "sonunda mutlaka bulur",
                "note": "Annesinin, babasının yokluğunu küçük bir çocuğa açıklayamayışı ve verdiği teselli.",
            },
            {
                "orig": "Elle dit qu'il n'est jamais très loin, qu'il part très souvent travailler",
                "pron": "El di kil ne jame tre luen, kil par tre suvan travaye",
                "tr": "Asla çok uzakta olmadığını, sadece çalışmak için çok sık gittiğini söylüyor.",
                "highlight": "Asla çok uzakta olmadığını",
                "note": "Gerçeği bilmeyen çocuğun, babasını sadece işe gitmiş sanarak pencere önünde beklemesi.",
            },
            {
                "orig": "Où es-tu Papa ? Dis-moi, où es-tu caché ?",
                "pron": "U e tü Papa? Di-mua, u e tü kaşe?",
                "tr": "Neredesin baba? Söyle bana, nereye saklandın?",
                "highlight": "Neredesin baba? Söyle bana",
                "note": "Babasının yokluğunu hâlâ bir saklambaç oyunu sanan çocuk kalbinin en saf sorusu.",
            },
        ],
    },
    # =========================================================================
    # 2. İNGİLİZCE (EN) 🇬🇧
    # =========================================================================
    {
        "id": "en_arctic_monkeys_i_wanna_be_yours",
        "language": "ingilizce",
        "language_code": "EN",
        "language_tr": "İngilizce",
        "flag": "🇬🇧",
        "artist": "Arctic Monkeys",
        "title": "I Wanna Be Yours",
        "release_year": "2013",
        "itunes_query": "Arctic Monkeys I Wanna Be Yours",
        "chorus_timestamp": "1:02 - 1:17 (Nakarat / Secrets I Have Held)",
        "social_audio_search": "Arctic Monkeys - I Wanna Be Yours",
        "cover_kicker": "🇬🇧 İNGİLİZCE KÜLT AŞK ŞARKISI • EDEBİ ÇEVİRİ",
        "cover_headline": "BİR İNSANA 'SENİN OLMAK İSTİYORUM' DEMENİN EN ŞİİRSEL HALİ",
        "viral_hook": "Şair John Cooper Clarke'ın şiirinden bestelenen bu şarkı, büyük ve süslü vaatler yerine sevdiği insanın hayatındaki en sıradan ama en vazgeçilmez parçalar olmak isteyen saf bir bağlılığı anlatır.",
        "stanzas": [
            {
                "orig": "Secrets I have held in my heart are harder to hide than I thought",
                "pron": "Sikrıts ay hev held in may hart ar hardır tu hayd den ay tot",
                "tr": "Kalbimde sakladığım bu sırları gizlemek, sandığımdan çok daha zormuş.",
                "highlight": "sandığımdan çok daha zormuş",
                "note": "İçinde büyüttüğü sevginin artık bakışlarından ve sesinden taşmaya başladığı an.",
            },
            {
                "orig": "Maybe I just wanna be yours, I wanna be yours",
                "pron": "Meybi ay cast vana bi yors, ay vana bi yors",
                "tr": "Belki de tek istediğim yalnızca senin olmaktır; tamamen senin olmak istiyorum.",
                "highlight": "yalnızca senin olmaktır",
                "note": "Karmaşık beklentilerden arınmış, en yalın ve en dürüst aşk itirafı.",
            },
            {
                "orig": "Let me be your 'leccy meter and I'll never run out",
                "pron": "Let mi bi yor leki mitır end ayl nevır ran aut",
                "tr": "Bırak evindeki ışığın olayım; söz veriyorum enerjim ve sıcaklığım hiç tükenmeyecek.",
                "highlight": "sıcaklığım hiç tükenmeyecek",
                "note": "Gösterişli bir kahraman değil, karanlıkta hiç sönmeyen güvenilir bir sığınak olma sözü.",
            },
            {
                "orig": "If you like your coffee hot, let me be your coffee pot",
                "pron": "İf yu layk yor kofi hat, let mi bi yor kofi pat",
                "tr": "Eğer kahveni sıcak seviyorsan, her sabah ilk dokunduğun o cezven ben olayım.",
                "highlight": "her sabah ilk dokunduğun",
                "note": "Sevdiği insanın sabah rutininin ve huzurunun ayrılmaz bir parçası olma arzusu.",
            },
        ],
    },
    {
        "id": "en_billie_eilish_birds_of_a_feather",
        "language": "ingilizce",
        "language_code": "EN",
        "language_tr": "İngilizce",
        "flag": "🇬🇧",
        "artist": "Billie Eilish",
        "title": "BIRDS OF A FEATHER",
        "release_year": "2024",
        "itunes_query": "Billie Eilish Birds of a Feather",
        "chorus_timestamp": "0:43 - 0:58 (Ana Nakarat)",
        "social_audio_search": "Billie Eilish - BIRDS OF A FEATHER",
        "cover_kicker": "🇬🇧 GLOBAL #1 HİT • TÜRKÇE EDEBİ ANLAMI",
        "cover_headline": "RUH EŞİNİZE GÖNDEREBİLECEĞİNİZ EN DERİN İNGİLİZCE ŞARKI",
        "viral_hook": "'Birds of a feather' İngilizce'de 'Aynı tüyün kuşları / Ruh ikizleri bir arada uçar' anlamına gelen asırlık bir deyimdir. Billie Eilish burada ölümden sonra bile sürecek bir bağlılığı anlatır.",
        "stanzas": [
            {
                "orig": "Birds of a feather, we should stick together, I know",
                "pron": "Börds of a fedır, vi şud stik tugedır, ay nov",
                "tr": "Biz aynı gökyüzünün kuşlarıyız; biliyorum ki hep yan yana kalmalıyız.",
                "highlight": "aynı gökyüzünün kuşlarıyız",
                "note": "İki insanın aynı frekansta olması ve birbirine ait hissetmesi.",
            },
            {
                "orig": "I said I'd never think I wasn't better alone",
                "pron": "Ay sed ayd nevır tink ay vazınt bedır alon",
                "tr": "Eskiden yalnızken daha mutlu olduğumu sanırdım; ta ki seni tanıyana dek.",
                "highlight": "ta ki seni tanıyana dek",
                "note": "Yalnızlığı zırh edinmiş bir kalbin, doğru insanla karşılaşınca yelkenleri indirmesi.",
            },
            {
                "orig": "I'll love you 'til the day that I die, 'til the light leaves my eyes",
                "pron": "Ayl lav yu til dı dey det ay day, til dı layt livs may ayz",
                "tr": "Nefes aldığım son güne, gözlerimdeki ışık tamamen sönene kadar seni seveceğim.",
                "highlight": "gözlerimdeki ışık tamamen sönene kadar",
                "note": "Zamanla eksilmeyen, aksine hayatın son anına dek büyüyen sadakat.",
            },
            {
                "orig": "I don't know what I'm crying for, I don't think I could love you more",
                "pron": "Ay dont nov vat aym kraying for, ay dont tink ay kud lav yu mor",
                "tr": "Neden ağladığımı bile bilmiyorum; sanırım seni bundan daha fazla sevmem imkânsız.",
                "highlight": "bundan daha fazla sevmem imkânsız",
                "note": "Sevginin kalbe sığmayıp gözyaşına dönüştüğü o taşma noktası.",
            },
        ],
    },
    # =========================================================================
    # 3. RUSÇA (RU) 🇷🇺
    # =========================================================================
    {
        "id": "ru_rauf_faik_detstvo",
        "language": "rusca",
        "language_code": "RU",
        "language_tr": "Rusça",
        "flag": "🇷🇺",
        "artist": "Rauf & Faik",
        "title": "Детство (Detstvo)",
        "release_year": "2018",
        "itunes_query": "Rauf Faik Detstvo",
        "chorus_timestamp": "0:38 - 0:53 (İkonik Nakarat)",
        "social_audio_search": "Rauf & Faik - Детство",
        "cover_kicker": "🇷🇺 RUSÇA EFSANE • OKUNUŞU & TÜRKÇE ÇEVİRİSİ",
        "cover_headline": "TÜRKİYE'DE MİLYONLARIN DİNLEDİĞİ 'DETSTVO' NE ANLATIYOR?",
        "viral_hook": "'Детство' (Detstvo) Rusça'da 'Çocukluk' demektir. Şarkı, çocukluk yıllarındaki masum ilk aşkı, verilen sözleri ve büyüdükçe kaybedilen o saf güveni özlemle anlatır.",
        "stanzas": [
            {
                "orig": "И я скажу тебе при встрече: «Как же тесен мир»",
                "pron": "İ ya skaju tebe pri vstreçe: Kak je tesen mir",
                "tr": "Ve bir gün yeniden karşılaştığımızda sana diyeceğim ki: 'Dünya ne kadar da küçükmüş.'",
                "highlight": "Dünya ne kadar da küçükmüş",
                "note": "Yıllar sonra tesadüfen göz göze gelinen o ilk karşılaşma anının boğaz düğümleyen sükûneti.",
            },
            {
                "orig": "Ты за стеной жила все эти десять лет, увы",
                "pron": "Tı za stenoy jila vse eti desyat let, uvı",
                "tr": "Meğer bunca yıl, tam on sene boyunca sadece bir duvar ötemde yaşamışsın, ne yazık...",
                "highlight": "sadece bir duvar ötemde yaşamışsın",
                "note": "Fiziksel olarak çok yakın olup duygusal olarak iki yabancıya dönüşmenin hüznü.",
            },
            {
                "orig": "А помнишь, обещали друг другу мы",
                "pron": "A pomniş, obeşali drug drugu mı",
                "tr": "Peki hatırlıyor musun, çocukken birbirimize nasıl da sözler vermiştik?",
                "highlight": "birbirimize nasıl da sözler vermiştik",
                "note": "Çocuklukta dünyanın hiç değişmeyeceğine inanarak verilen masum sözler.",
            },
            {
                "orig": "Что вырастем и будем всегда вместе мы",
                "pron": "Şto vırastem i budem vsegda vmeste mı",
                "tr": "'Büyüyeceğiz ve hayat boyu hep yan yana olacağız' demiştik...",
                "highlight": "hayat boyu hep yan yana olacağız",
                "note": "Büyümenin getirdiği en büyük kaybın, o çocuksu sadakati yitirmek olduğunu hatırlatır.",
            },
        ],
    },
    {
        "id": "ru_jony_kometa",
        "language": "rusca",
        "language_code": "RU",
        "language_tr": "Rusça",
        "flag": "🇷🇺",
        "artist": "JONY",
        "title": "Комета (Kometa)",
        "release_year": "2019",
        "itunes_query": "JONY Kometa",
        "chorus_timestamp": "0:48 - 1:03 (Nakarat)",
        "social_audio_search": "JONY - Комета",
        "cover_kicker": "🇷🇺 RUSÇA MELANKOLİ • TÜRKÇE ÇEVİRİ",
        "cover_headline": "GECE YARISI DİNLENEN O RUSÇA ŞARKININ DERİN ANLAMI",
        "viral_hook": "JONY'nin sesinden dinlediğimiz 'Kometa' (Kuyruklu Yıldız), hayatımıza bir anlığına girip her şeyi aydınlatan ama sonra iz bırakarak kaybolan imkânsız bir aşkı anlatır.",
        "stanzas": [
            {
                "orig": "И пусть с ума сойдёт весь мир, мне наплевать",
                "pron": "İ pust s uma saydyot ves mir, mne naplevat",
                "tr": "Bırak bütün dünya çıldırsın, artık hiçbir şey umurumda bile değil.",
                "highlight": "artık hiçbir şey umurumda bile değil",
                "note": "Gerçek aşkın karşısında dış dünyanın kurallarının anlamını yitirmesi.",
            },
            {
                "orig": "Я к тебе лечу, словно комета",
                "pron": "Ya k tebe leçu, slovna kometa",
                "tr": "Karanlığı yararak tıpkı bir kuyruklu yıldız gibi sana doğru uçuyorum.",
                "highlight": "kuyruklu yıldız gibi sana doğru",
                "note": "Yanıp kül olacağını bilse bile sevdiğine doğru hızla gitmekten vazgeçmemek.",
            },
            {
                "orig": "И даже под дулом пистолета",
                "pron": "İ daje pod dulom pistoleta",
                "tr": "Ve en zor, en çaresiz anımda bile vazgeçmem;",
                "highlight": "en çaresiz anımda bile vazgeçmem",
                "note": "Hiçbir tehdidin veya engelin bu kavuşma arzusunu durduramayacağı vurgusu.",
            },
            {
                "orig": "Я найду тебя, я найду тебя",
                "pron": "Ya naydu tebya, ya naydu tebya",
                "tr": "Nereye gidersen git seni bulacağım, mutlaka seni bulacağım.",
                "highlight": "mutlaka seni bulacağım",
                "note": "Mesafelerin ve zamanın silemediği sarsılmaz bir kararlılık.",
            },
        ],
    },
    # =========================================================================
    # 4. JAPONCA (JA) 🇯🇵
    # =========================================================================
    {
        "id": "ja_fujii_kaze_shinunoga_ewa",
        "language": "japonca",
        "language_code": "JA",
        "language_tr": "Japonca",
        "flag": "🇯🇵",
        "artist": "Fujii Kaze",
        "title": "死ぬのがいいわ (Shinunoga E-Wa)",
        "release_year": "2020",
        "itunes_query": "Fujii Kaze Shinunoga E-Wa",
        "chorus_timestamp": "0:46 - 1:01 (Viral Piyano & Nakarat)",
        "social_audio_search": "Fujii Kaze - Shinunoga E-Wa",
        "cover_kicker": "🇯🇵 JAPONCA VİRAL HİT • TÜRKÇE ÇEVİRİ",
        "cover_headline": "PİYANO GİRİŞİYLE TÜM DÜNYAYI SALLAYAN BU JAPONCA ŞARKI NE DİYOR?",
        "viral_hook": "Fujii Kaze'nin klasik Japon edebiyatı ve modern cazı birleştirdiği bu eseri, sevdiği insanı kaybetmektense yok olmayı tercih eden tutkulu bir bağlılığı anlatır.",
        "stanzas": [
            {
                "orig": "わたしの最後はあなたがいい",
                "pron": "Vataşi no saygo va anata ga ii",
                "tr": "Hayatımın son durağı, son nefesim yalnızca sen olmalısın.",
                "highlight": "son nefesim yalnızca sen olmalısın",
                "note": "Bir ömrü tek bir insanın kalbinde tamamlama dileği.",
            },
            {
                "orig": "あなたとこのままおサラバするより",
                "pron": "Anata to kono mama osaraba suru yori",
                "tr": "Seninle bu şekilde vedalaşıp ayrı düşmektense,",
                "highlight": "vedalaşıp ayrı düşmektense",
                "note": "Eski Japonca 'osaraba' (elveda) kelimesiyle ayrılığın ağırlığını vurgular.",
            },
            {
                "orig": "死ぬのがいいわ、死ぬのがいいわ",
                "pron": "Şinunoga ii va, şinunoga ii va",
                "tr": "Sensiz yaşamaktansa ölmeyi yeğlerim, yok olmayı yeğlerim.",
                "highlight": "Sensiz yaşamaktansa",
                "note": "Japon şiir geleneğindeki mutlak sadakat ve tutkunun zirvesi.",
            },
            {
                "orig": "三度の飯よりあんたがいいのよ",
                "pron": "Sando no meşi yori anta ga ii no yo",
                "tr": "Aldığım nefesten, yediğim ekmekten bile önce sen gelirsin benim için.",
                "highlight": "Aldığım nefesten bile önce sen",
                "note": "Japon deyimi 'üç öğün yemekten bile değerli olmak', vazgeçilmezliği anlatır.",
            },
        ],
    },
    {
        "id": "ja_miki_matsubara_stay_with_me",
        "language": "japonca",
        "language_code": "JA",
        "language_tr": "Japonca",
        "flag": "🇯🇵",
        "artist": "Miki Matsubara",
        "title": "真夜中のドア / Stay With Me",
        "release_year": "1979",
        "itunes_query": "Miki Matsubara Mayonaka no Door Stay With Me",
        "chorus_timestamp": "0:55 - 1:10 (Stay With Me Nakaratı)",
        "social_audio_search": "Miki Matsubara - Mayonaka no Door / Stay With Me",
        "cover_kicker": "🇯🇵 1979 TOKYO CITY POP EFSANESİ • TÜRKÇE ANLAMI",
        "cover_headline": "45 YIL SONRA YENİDEN DÜNYA LİSTELERİNE GİREN O JAPONCA ŞARKI",
        "viral_hook": "1979'da henüz 19 yaşındayken bu başyapıtı söyleyen Miki Matsubara, bir gece yarısı kapıyı çekip giden sevgilisinin ardından duyduğu o zarif ama derin özlemi anlatır.",
        "stanzas": [
            {
                "orig": "Stay with me… 真夜中のドアをたたき",
                "pron": "Stey vit mi... Mayonaka no doa vo tataki",
                "tr": "Yanımda kal... Gece yarısı kapımı çalıp içeri girdiğin o ana dönelim.",
                "highlight": "Gece yarısı kapımı çalıp",
                "note": "Gece yarısı kapısı, anılarla gerçek hayat arasındaki eşiği temsil eder.",
            },
            {
                "orig": "帰らないでと泣いた あの季節が 今 目の前",
                "pron": "Kaeranayde to nayta, ano kisetsu ga ima me no mae",
                "tr": "'Ne olur gitme' diye ağladığım o mevsim, şimdi yeniden gözlerimin önünde canlanıyor.",
                "highlight": "şimdi yeniden gözlerimin önünde",
                "note": "Yıllar geçse de bazı ayrılıkların mevsimi insanın kalbinde hiç değişmez.",
            },
            {
                "orig": "Stay with me… 口ぐせを言いながら",
                "pron": "Stey vit mi... Kuçiguse vo iinagara",
                "tr": "Yanımda kal... Senin o hep tekrarladığın alışıldık sözlerini mırıldanırken,",
                "highlight": "alışıldık sözlerini mırıldanırken",
                "note": "Giden bir insandan geriye kalan en dokunaklı miras, dilimize pelesenk olan cümleleridir.",
            },
            {
                "orig": "二人の瞬間を抱いて まだ忘れず 大事にしていた",
                "pron": "Futari no toki vo dayte, mada vasurezu dayji ni şite ita",
                "tr": "İkimizin paylaştığı o anlara sıkıca sarıldım; unutmadım, kalbimde hep baş tacı ettim.",
                "highlight": "kalbimde hep baş tacı ettim",
                "note": "Öfke duymadan, yaşanmış güzelliğe saygı duyarak sevmeye devam etmek.",
            },
        ],
    },
    # =========================================================================
    # 5. ALMANCA (DE) 🇩🇪
    # =========================================================================
    {
        "id": "de_udo_apache_komet",
        "language": "almanca",
        "language_code": "DE",
        "language_tr": "Almanca",
        "flag": "🇩🇪",
        "artist": "Udo Lindenberg & Apache 207",
        "title": "Komet",
        "release_year": "2023",
        "itunes_query": "Udo Lindenberg Apache 207 Komet",
        "chorus_timestamp": "0:49 - 1:04 (Ana Nakarat)",
        "social_audio_search": "Udo Lindenberg & Apache 207 - Komet",
        "cover_kicker": "🇩🇪 ALMANYA TARİHİNİN EN ÇOK DİNLENEN ŞARKISI",
        "cover_headline": "ALMANCA BİLMEYENLERİN BİLE HAYRAN KALDIĞI 'KOMET' NE ANLATIYOR?",
        "viral_hook": "Almanya müzik tarihinde en uzun süre 1 numarada kalan 'Komet', insanın bu dünyadan geçerken sıradan bir iz değil, gökyüzünü ikiye bölen unutulmaz bir iz bırakma arzusunu anlatır.",
        "stanzas": [
            {
                "orig": "Und wenn ich geh', dann so, wie ich gekommen bin",
                "pron": "Unt ven ih ge, dan zo, vi ih gekomen bin",
                "tr": "Ve bir gün çekip gittiğimde, tıpkı geldiğim günkü gibi dimdik gideceğim;",
                "highlight": "geldiğim günkü gibi dimdik",
                "note": "Hayat yolculuğunda kendi karakterinden ve duruşundan ödün vermemek.",
            },
            {
                "orig": "Wie ein Komet, der zweimal einschlägt",
                "pron": "Vi ayn komet, der tsvaymal aynşlegt",
                "tr": "Tıpkı aynı yere iki kez çarpan bir kuyruklu yıldız gibi unutulmaz olacağım.",
                "highlight": "iki kez çarpan bir kuyruklu yıldız",
                "note": "İmkânsız denileni başaran, hafızalardan silinmeyen bir etki bırakmak.",
            },
            {
                "orig": "Vielleicht tut es weh, doch will auf Nummer sicher geh'n",
                "pron": "Filayht tut es ve, doh vil auf numır ziher gen",
                "tr": "Belki can yakacak ama ardımda bıraktığım izden emin olmak istiyorum;",
                "highlight": "bıraktığım izden emin olmak",
                "note": "Tutkulu yaşamanın bedeli acı olsa da silik yaşamaktan iyidir.",
            },
            {
                "orig": "Dass ich für immer leb', lass uns nochmal aufdreh'n",
                "pron": "Das ih für imır leb, las uns nohmal aufdren",
                "tr": "Anılarda sonsuza dek yaşayacağım; hadi müziğin ve hayatın sesini son kez açalım.",
                "highlight": "Anılarda sonsuza dek yaşayacağım",
                "note": "Sevdiklerimizin kalbinde bıraktığımız anılar bizi ölümsüz kılar.",
            },
        ],
    },
    {
        "id": "de_annenmaykantereit_oft_gefragt",
        "language": "almanca",
        "language_code": "DE",
        "language_tr": "Almanca",
        "flag": "🇩🇪",
        "artist": "AnnenMayKantereit",
        "title": "Oft gefragt",
        "release_year": "2016",
        "itunes_query": "AnnenMayKantereit Oft gefragt",
        "chorus_timestamp": "0:58 - 1:13 (Henning May Vokal Nakarat)",
        "social_audio_search": "AnnenMayKantereit - Oft gefragt",
        "cover_kicker": "🇩🇪 ALMANCA DUYGUSAL BAŞYAPIT • TÜRKÇE ÇEVİRİ",
        "cover_headline": "HENNING MAY'İN O EŞSİZ SESİYLE SÖYLEDİĞİ SÖZLERİN GERÇEK ANLAMI",
        "viral_hook": "Henning May'in derin ve buğulu sesiyle devleşen 'Oft gefragt', insanın ailesine, babasına ve geçmişindeki güvenli limana duyduğu minnet ve özlemi anlatır.",
        "stanzas": [
            {
                "orig": "Du hast mich tausendmal gefragt, was ich denn so mach'",
                "pron": "Du hast mih tauzıntmal gefrakt, vas ih den zo mah",
                "tr": "Bana binlerce kez ne yaptığımı, hayatımın nasıl gittiğini sordun;",
                "highlight": "Bana binlerce kez",
                "note": "Bizi karşılıksız seven insanların bıkmadan usanmadan halimizi sorması.",
            },
            {
                "orig": "Und ich hab' tausendmal gesagt: Alles halb so schlimm",
                "pron": "Unt ih hab tauzıntmal gezakt: Ales halb zo şlim",
                "tr": "Ben ise seni üzmemek için binlerce kez 'Her şey yolunda, o kadar da kötü değil' dedim.",
                "highlight": "seni üzmemek için binlerce kez",
                "note": "İçimiz fırtınalar koparken sevdiklerimiz endişelenmesin diye taktığımız güçlü maske.",
            },
            {
                "orig": "Ich kann immer zu dir kommen, hast du immer zu mir gesagt",
                "pron": "İh kan imır tsu dir komen, hast du imır tsu mir gezakt",
                "tr": "Bana hep 'Ne olursa olsun, kapım sana her zaman açık, bana gelebilirsin' derdin.",
                "highlight": "kapım sana her zaman açık",
                "note": "Hayatta düşsek bile dönebileceğimiz bir evin olduğunu bilmenin verdiği güven.",
            },
            {
                "orig": "Und ich hab' mich oft gefragt, ob du weißt, wie viel mir das bedeutet",
                "pron": "Unt ih hab mih oft gefrakt, op du vayst, vi fil mir das bedoytıt",
                "tr": "Ve kendime hep sordum: Bu sözünün benim için ne kadar değerli olduğunu biliyor musun?",
                "highlight": "benim için ne kadar değerli olduğunu",
                "note": "Sevdiklerimize zamanında söyleyemediğimiz teşekkürün içten itirafı.",
            },
        ],
    },
    # =========================================================================
    # 6. İSPANYOLCA (ES) 🇪🇸
    # =========================================================================
    {
        "id": "es_manu_chao_me_gustas_tu",
        "language": "ispanyolca",
        "language_code": "ES",
        "language_tr": "İspanyolca",
        "flag": "🇪🇸",
        "artist": "Manu Chao",
        "title": "Me Gustas Tú",
        "release_year": "2001",
        "itunes_query": "Manu Chao Me Gustas Tu",
        "chorus_timestamp": "0:32 - 0:47 (Me Gustas Tú Nakarat)",
        "social_audio_search": "Manu Chao - Me Gustas Tu",
        "cover_kicker": "🇪🇸 İSPANYOLCA ZAMANSIZ KLASİK • TÜRKÇE ÇEVİRİ",
        "cover_headline": "DÜNYADAKİ GÜZEL ŞEYLERİ SAYIP SONUNDA 'AMA EN ÇOK SEN' DİYEN ŞARKI",
        "viral_hook": "Manu Chao bu ikonik şarkıda yağmuru, denizi, yolculukları, sabah kahvesini ve rüzgarı tek tek sayar; fakat her dizenin sonunda tüm güzelliklerin merkezine sevdiği insanı koyar.",
        "stanzas": [
            {
                "orig": "Me gustan los aviones, me gustas tú; me gusta viajar, me gustas tú",
                "pron": "Me gustan los avyones, me gustas tu; me gusta vyahar, me gustas tu",
                "tr": "Uçakları severim, ama seni daha çok; uzaklara yolculuk etmeyi severim, ama en çok seni.",
                "highlight": "ama en çok seni",
                "note": "Özgürlüğü ve keşfetmeyi seven bir ruhun, en güzel yolculuğu sevdiğinde bulması.",
            },
            {
                "orig": "Me gusta la mañana, me gustas tú; me gusta el viento, me gustas tú",
                "pron": "Me gusta la manyana, me gustas tu; me gusta el vyento, me gustas tu",
                "tr": "Sabahın ilk ışığını severim, seni severim; yüzüme çarpan rüzgârı severim, seni severim.",
                "highlight": "Sabahın ilk ışığını severim",
                "note": "Doğadaki her taze başlangıcın sevdiği insanı hatırlatması.",
            },
            {
                "orig": "Me gusta soñar, me gustas tú; me gusta la mar, me gustas tú",
                "pron": "Me gusta sonyar, me gustas tu; me gusta la mar, me gustas tu",
                "tr": "Hayal kurmayı severim, seni severim; sonsuz denizi severim, seni severim.",
                "highlight": "sonsuz denizi severim, seni severim",
                "note": "Hayallerin ve denizin derinliğini sevdiği insanın gözlerinde görmek.",
            },
            {
                "orig": "¿Qué voy a hacer? Je ne sais pas… ¿Qué horas son, mi corazón?",
                "pron": "Ke voy a aser? Jö nö se pa... Ke oras son, mi korason?",
                "tr": "Şimdi ne yapacağım? İnan bilmiyorum... Saat kaç oldu benim güzel kalbim?",
                "highlight": "Saat kaç oldu benim güzel kalbim",
                "note": "Aşkın içinde zaman kavramının tamamen kaybolması.",
            },
        ],
    },
    {
        "id": "es_alvaro_soler_sofia",
        "language": "ispanyolca",
        "language_code": "ES",
        "language_tr": "İspanyolca",
        "flag": "🇪🇸",
        "artist": "Álvaro Soler",
        "title": "Sofía",
        "release_year": "2016",
        "itunes_query": "Alvaro Soler Sofia",
        "chorus_timestamp": "0:43 - 0:58 (Mira Sofía Nakarat)",
        "social_audio_search": "Álvaro Soler - Sofía",
        "cover_kicker": "🇪🇸 İSPANYOLCA ENERJİ & AŞK • TÜRKÇE ANLAMI",
        "cover_headline": "YAZ AKŞAMLARININ VAZGEÇİLMEZ İSPANYOLCA ŞARKISI NE ANLATIYOR?",
        "viral_hook": "Kıpır kıpır Akdeniz ritmiyle herkesi gülümseten 'Sofía', aslında kalbi kırıldıktan sonra yeniden umutla ayağa kalkmayı ve sevgiye küsmemeyi anlatır.",
        "stanzas": [
            {
                "orig": "Sueño cuando era pequeño, sin preocupación en el corazón",
                "pron": "Suenyo kuando era pekenyo, sin preokupasyon en el korason",
                "tr": "Kalbimde hiçbir tasa ve kaygı taşımadığım o çocukluk günlerimi düşlüyorum.",
                "highlight": "hiçbir tasa ve kaygı taşımadığım",
                "note": "Kalbin henüz kırılmadığı o saf ve korkusuz yıllara duyulan özlem.",
            },
            {
                "orig": "Sigo viendo aquel momento, se desvaneció, desapareció",
                "pron": "Sigo vyendo akel momento, se desvanesyo, desaparesyo",
                "tr": "O anı hâlâ gözlerimin önünde görüyorum; bir anda solup gitti ve kayboldu.",
                "highlight": "bir anda solup gitti",
                "note": "Güzel başlayan bir hikayenin beklenmedik şekilde sona erişi.",
            },
            {
                "orig": "Mira, Sofía, sin tu mirada, sigo, sin tu mirada, sigo",
                "pron": "Mira, Sofiya, sin tu mirada, sigo, sin tu mirada, sigo",
                "tr": "Bak Sofía; senin bakışların üzerimde olmasa bile yürümeye ve yaşamaya devam ediyorum.",
                "highlight": "yaşamaya devam ediyorum",
                "note": "Ayrılığın ardından kendi gücünü yeniden keşfetme ve iyileşme ilanı.",
            },
            {
                "orig": "Dime cómo hacen los demás, para olvidar tan fácil",
                "pron": "Dime komo asen los demas, para olvidar tan fasil",
                "tr": "Söyle bana, diğer insanlar nasıl oluyor da yaşanmışlıkları bu kadar kolay unutabiliyor?",
                "highlight": "bu kadar kolay unutabiliyor",
                "note": "Derin seven insanların, yüzeysel unutuşlara duyduğu şaşkınlık.",
            },
        ],
    },
    # =========================================================================
    # 7. KORECE (KO) 🇰🇷
    # =========================================================================
    {
        "id": "ko_rose_bruno_mars_apt",
        "language": "korece",
        "language_code": "KO",
        "language_tr": "Korece",
        "flag": "🇰🇷",
        "artist": "ROSÉ & Bruno Mars",
        "title": "APT. (아파트)",
        "release_year": "2024",
        "itunes_query": "ROSE Bruno Mars APT",
        "chorus_timestamp": "0:36 - 0:51 (Apateu Nakarat)",
        "social_audio_search": "ROSÉ & Bruno Mars - APT.",
        "cover_kicker": "🇰🇷 KORECE & İNGİLİZCE DÜNYA REKORU • TÜRKÇE ANLAMI",
        "cover_headline": "HERKESİN DİLİNDEKİ 'APATEU APATEU' ASLINDA NE DEMEK?",
        "viral_hook": "'Apateu' (아파트), Korece'de 'Apartman' demektir ve Güney Kore'de arkadaş buluşmalarında elleri üst üste koyarak oynanan çok popüler bir ritim oyunundan gelir. Şarkı, mesajlaşmayı bırakıp gerçek hayatta buluşma çağrısıdır.",
        "stanzas": [
            {
                "orig": "채영이가 좋아하는 랜덤 게임, 아파트 아파트!",
                "pron": "Çeyong-iga coahanın rendım geim, Apatı Apatı!",
                "tr": "Chaeyoung'un (Rosé'nin) en sevdiği sürpriz oyun başlıyor: Apartman, Apartman!",
                "highlight": "en sevdiği sürpriz oyun",
                "note": "Kore'de samimi dost meclislerini başlatan geleneksel tezahürat.",
            },
            {
                "orig": "Kissy face, kissy face, sent to your phone, but",
                "pron": "Kisi feys, kisi feys, sent tu yor fon, bat",
                "tr": "Telefonuna sürekli öpücük emojileri gönderiyorum ama bu artık yetmiyor;",
                "highlight": "bu artık yetmiyor",
                "note": "Ekran arkasındaki sanal iletişimin gerçek duyguların yerini tutamayacağı gerçeği.",
            },
            {
                "orig": "I'm tryna kiss your lips for real, red hearts, red hearts",
                "pron": "Aym trayna kis yor lips for riyıl, red harts, red harts",
                "tr": "Ben sana gerçekten dokunmak, gözlerinin içine bakmak istiyorum; sadece kırmızı kalpler değil.",
                "highlight": "gözlerinin içine bakmak istiyorum",
                "note": "Dijital çağda gerçek ve samimi yakınlığa duyulan özlem.",
            },
            {
                "orig": "Don't you want me like I want you, baby? Meet me at the APT.",
                "pron": "Dont yu vant mi layk ay vant yu, beybi? Mit mi et dı Apatı",
                "tr": "Sen de beni benim seni istediğim kadar özlemedin mi? Hadi bu akşam buluşalım.",
                "highlight": "benim seni istediğim kadar",
                "note": "Ertelemeyi bırakıp anı yaşama ve kavuşma daveti.",
            },
        ],
    },
    {
        "id": "ko_newjeans_ditto",
        "language": "korece",
        "language_code": "KO",
        "language_tr": "Korece",
        "flag": "🇰🇷",
        "artist": "NewJeans",
        "title": "Ditto (디토)",
        "release_year": "2022",
        "itunes_query": "NewJeans Ditto",
        "chorus_timestamp": "0:45 - 1:00 (Stay in the Middle Nakarat)",
        "social_audio_search": "NewJeans - Ditto",
        "cover_kicker": "🇰🇷 KORECE NOSTALJİK BAŞYAPIT • TÜRKÇE ÇEVİRİ",
        "cover_headline": "KORE LİSTELERİNİ ALTÜST EDEN 'DITTO' ŞARKISININ NAİF ANLAMI",
        "viral_hook": "'Ditto', 'Ben de aynı fikirdeyim / Ben de seni seviyorum' demektir. Şarkı, birini uzaktan severken onun da aynı duyguları paylaşıp paylaşmadığını duymak isteyen kalbin heyecanını anlatır.",
        "stanzas": [
            {
                "orig": "훌쩍 커버렸어 함께한 기억처럼",
                "pron": "Hulcok koboryosso hamkehan giyokçorom",
                "tr": "Birlikte biriktirdiğimiz anılarımız gibi, farkında olmadan bir anda büyüyüverdik.",
                "highlight": "bir anda büyüyüverdik",
                "note": "Zamanın hızla akışı içinde masum duyguların olgunlaşması.",
            },
            {
                "orig": "내 마음을 보는 거울 속엔 너만 있어",
                "pron": "Ne maımıl bonın goul sogen noman isso",
                "tr": "Kalbimin içine tuttuğum o aynaya her baktığımda yalnızca seni görüyorum.",
                "highlight": "yalnızca seni görüyorum",
                "note": "İnsanın kendi iç dünyasında bile sevdiğinin yansımasıyla karşılaşması.",
            },
            {
                "orig": "Stay in the middle, like you a little, don't want no riddle",
                "pron": "Stey in dı midıl, layk yu a lidıl, dont vant no ridıl",
                "tr": "Aramızdaki bu mesafede dur, artık bilmeceler ve belirsizlikler istemiyorum;",
                "highlight": "artık bilmeceler ve belirsizlikler istemiyorum",
                "note": "Sevgide oyunlar yerine netlik ve dürüstlük arayışı.",
            },
            {
                "orig": "말해줘 say it back, oh say it ditto",
                "pron": "Malhecvo sey it bek, o sey it dito",
                "tr": "Ne olur sen de bana söyle, 'Ben de seninle aynı hissediyorum' de.",
                "highlight": "Ben de seninle aynı hissediyorum",
                "note": "Tek taraflı kalma korkusunun yerini karşılıklı sevgi umuduna bırakması.",
            },
        ],
    },
    # =========================================================================
    # 8. ÇİNCE (ZH) 🇨🇳
    # =========================================================================
    {
        "id": "zh_joker_xue_yan_yuan",
        "language": "cince",
        "language_code": "ZH",
        "language_tr": "Çince",
        "flag": "🇨🇳",
        "artist": "Joker Xue (薛之谦)",
        "title": "演员 (Yǎn Yuán — Oyuncu)",
        "release_year": "2015",
        "itunes_query": "Xue Zhiqian Yan Yuan Actor",
        "chorus_timestamp": "1:04 - 1:19 (Ana Nakarat / 該配合你演出的我)",
        "social_audio_search": "薛之谦 - 演员 (Joker Xue - Actor)",
        "cover_kicker": "🇨🇳 MİLYARLARCA KEZ DİNLENEN ÇİNCE ŞARKI • TÜRKÇE ÇEVİRİ",
        "cover_headline": "SEVDİĞİ İNSAN ÜZÜLMESİN DİYE 'OYUNCU' OLAN BİR KALBİN HİKAYESİ",
        "viral_hook": "Çince müzik tarihinin en çok dinlenen baladlarından 'Yǎn Yuán' (Oyuncu), karşısındaki insanın sevgisinin bittiğini bildiği halde, o suçluluk duymasın diye hiçbir şey anlamamış gibi rol yapan bir aşığı anlatır.",
        "stanzas": [
            {
                "orig": "简单点 说话的方式简单点",
                "pron": "Ciyen dan diyen, şuo hua dı fang şı ciyen dan diyen",
                "tr": "Daha sade olalım; konuşurken bahanelerin arkasına saklanmadan dürüstçe konuşalım.",
                "highlight": "bahanelerin arkasına saklanmadan",
                "note": "Ayrılık anında söylenen süslü yalanların kalbi daha çok yorduğu gerçeği.",
            },
            {
                "orig": "递进的情绪请省略 你又不是个演员",
                "pron": "Di cin dı çing şü çing şeng lüe, ni yo bu şı gı yen yüen",
                "tr": "Abartılı duyguları artık bir kenara bırak; sonuçta sen bir tiyatro oyuncusu değilsin.",
                "highlight": "sen bir tiyatro oyuncusu değilsin",
                "note": "Sevgisi biten birinin zoraki üzüntü gösterisine duyulan sessiz sitem.",
            },
            {
                "orig": "该配合你演出的我演视而不见",
                "pron": "Gay pey hı ni yen çu dı vo yen şı er bu ciyen",
                "tr": "Senin bu oyununa eşlik etmem gerektiği için, her şeyi bildiğim halde görmezden geliyorum.",
                "highlight": "bildiğim halde görmezden geliyorum",
                "note": "Sevdiği insanı utandırmamak için gerçeği yutkunarak gizleme fedakârlığı.",
            },
            {
                "orig": "在逼一个最爱你的人即兴表演",
                "pron": "Zay bi yi gı zuy ay ni dı rın ci şing biyao yen",
                "tr": "Seni dünyada en çok seven insanı, hazırlıksız bir ayrılık sahnesinde rol yapmaya zorluyorsun.",
                "highlight": "Seni dünyada en çok seven insanı",
                "note": "Şarkının kalplere kazınan en vurucu ve en hüzünlü dizesi.",
            },
        ],
    },
    {
        "id": "zh_jay_chou_gao_bai_qi_qiu",
        "language": "cince",
        "language_code": "ZH",
        "language_tr": "Çince",
        "flag": "🇨🇳",
        "artist": "Jay Chou (周杰伦)",
        "title": "告白气球 (Gào Bái Qì Qiú — İtiraf Balonu)",
        "release_year": "2016",
        "itunes_query": "Jay Chou Love Confession",
        "chorus_timestamp": "0:52 - 1:07 (Nakarat)",
        "social_audio_search": "周杰伦 - 告白气球 (Jay Chou)",
        "cover_kicker": "🇨🇳 ÇİNCE ROMANTİK KLASİK • OKUNUŞU & TÜRKÇE ANLAMI",
        "cover_headline": "ASYA'DA DÜĞÜNLERİN VE İLAN-I AŞKLARIN BİR NUMARALI ŞARKISI",
        "viral_hook": "Asya popunun kralı Jay Chou'nun bu eseri, pahalı hediyelerin veya gösterişin değil, insanın sevdiğinin gözlerinin içine bakarak ettiği samimi bir tebessümün en büyük mutluluk olduğunu anlatır.",
        "stanzas": [
            {
                "orig": "塞纳河畔 左岸的咖啡",
                "pron": "Say na hı pan, zuo an dı ka fey",
                "tr": "Sen Nehri kıyısında, sol yakadaki o küçük kafede elimde bir fincan kahve;",
                "highlight": "elimde bir fincan kahve",
                "note": "Huzurlu bir sonbahar öğleden sonrasında başlayan romantik bir hatıra.",
            },
            {
                "orig": "我手一杯 品尝你的美",
                "pron": "Vo şo yi bey, pin çang ni dı mey",
                "tr": "Elimdeki kahveyi yudumlarken, aslında senin varlığının güzelliğini izliyorum.",
                "highlight": "senin varlığının güzelliğini izliyorum",
                "note": "Sevilen insanın bulunduğu her ortamı güzelleştirmesi.",
            },
            {
                "orig": "亲爱的 爱上你 从那天起",
                "pron": "Çin ay dı, ay şang ni, cong na tiyen çi",
                "tr": "Sevgilim, sana âşık olduğum o ilk günden beri,",
                "highlight": "sana âşık olduğum o ilk günden beri",
                "note": "Hayatın öncesi ve sonrası olarak ikiye ayrıldığı o kırılma anı.",
            },
            {
                "orig": "甜蜜得很轻易 亲爱的别任性 你的眼睛在说我愿意",
                "pron": "Tiyen mi dı hın çing yi, ni dı yen cing zay şuo vo yüen yi",
                "tr": "Mutluluk o kadar zahmetsiz ki; inat etme, gözlerin çoktan 'Evet, kabul ediyorum' diyor.",
                "highlight": "gözlerin çoktan 'Evet' diyor",
                "note": "Dudaklar sussa bile gözlerin kalpteki sevgiyi ele vermesi.",
            },
        ],
    },
    # =========================================================================
    # 9. İTALYANCA (IT) 🇮🇹
    # =========================================================================
    {
        "id": "it_maneskin_torna_a_casa",
        "language": "italyanca",
        "language_code": "IT",
        "language_tr": "İtalyanca",
        "flag": "🇮🇹",
        "artist": "Måneskin",
        "title": "Torna a casa",
        "release_year": "2018",
        "itunes_query": "Maneskin Torna a casa",
        "chorus_timestamp": "1:12 - 1:27 (Quindi Marlena Torna a Casa Nakarat)",
        "social_audio_search": "Måneskin - Torna a casa",
        "cover_kicker": "🇮🇹 İTALYANCA ŞİİRSEL ROCK BALADI • TÜRKÇE ÇEVİRİ",
        "cover_headline": "İTALYA'YI AĞLATAN 'MARLENA EVE DÖN' ÇAĞRISININ GERÇEK ANLAMI",
        "viral_hook": "Måneskin'in en duygusal başyapıtı 'Torna a casa' (Eve Dön), ilham perisi ve özgürlüğün simgesi olan Marlena'ya yazılmış yakarış dolu bir mektuptur.",
        "stanzas": [
            {
                "orig": "Cammino per la mia città ed il vento soffia forte",
                "pron": "Kammino per la miya çitta ed il vento soffya forte",
                "tr": "Şehrimin sokaklarında tek başıma yürüyorum ve rüzgâr yüzüme sertçe esiyor.",
                "highlight": "tek başıma yürüyorum",
                "note": "Sevdiği gittikten sonra tanıdık bir şehrin bile insana yabancılaşması.",
            },
            {
                "orig": "Mi son lasciato tutto indietro e il sole all'orizzonte",
                "pron": "Mi son laşato tutto indyetro e il sole allorizzonte",
                "tr": "Her şeyi geride bıraktım; şimdi ufukta batan güneşle baş başayım.",
                "highlight": "Her şeyi geride bıraktım",
                "note": "Geçmişin yüklerinden sıyrılıp yalnızca öze, yani sevgiye odaklanma.",
            },
            {
                "orig": "Quindi Marlena torna a casa, che il freddo qua si fa sentire",
                "pron": "Kuindi Marlena torna a kaza, ke il freddo kua si fa sentire",
                "tr": "Öyleyse Marlena, ne olur artık eve dön; çünkü sensizliğin soğuğu iyice hissediliyor.",
                "highlight": "sensizliğin soğuğu iyice hissediliyor",
                "note": "Buradaki soğuk mevsimsel değil, ruhun yalnızlıktan üşümesidir.",
            },
            {
                "orig": "Quindi Marlena torna a casa, che non voglio più aspettare",
                "pron": "Kuindi Marlena torna a kaza, ke non volyo pyu aspettare",
                "tr": "Ne olur eve dön Marlena; çünkü artık bir gün daha beklemeye gücüm kalmadı.",
                "highlight": "beklemeye gücüm kalmadı",
                "note": "Özlemin sabrı tükettiği ve kalbin tüm gururu bıraktığı zirve anı.",
            },
        ],
    },
    {
        "id": "it_andrea_bocelli_con_te_partiro",
        "language": "italyanca",
        "language_code": "IT",
        "language_tr": "İtalyanca",
        "flag": "🇮🇹",
        "artist": "Andrea Bocelli",
        "title": "Con te partirò",
        "release_year": "1995",
        "itunes_query": "Andrea Bocelli Con te partiro",
        "chorus_timestamp": "1:08 - 1:23 (Con te partirò Nakarat)",
        "social_audio_search": "Andrea Bocelli - Con te partirò",
        "cover_kicker": "🇮🇹 İTALYANCA ÖLÜMSÜZ ESER • TÜRKÇE EDEBİ ÇEVİRİ",
        "cover_headline": "DÜNYA TARİHİNİN EN ASİL İTALYANCA ŞARKISI ASLINDA NE SÖYLÜYOR?",
        "viral_hook": "'Con te partirò' (Seninle Yola Çıkacağım), insanın sevdiğiyle birlikte hiç görmediği ufuklara ve denizlere doğru korkusuzca yelken açma arzusunu anlatan ölümsüz bir İtalyan klasiğidir.",
        "stanzas": [
            {
                "orig": "Quando sono solo, sogno all'orizzonte e mancan le parole",
                "pron": "Kuando sono solo, sonyo allorizzonte e mankan le parole",
                "tr": "Yalnız kaldığımda ufka doğru hayaller kurarım ve kelimeler boğazımda düğümlenir.",
                "highlight": "kelimeler boğazımda düğümlenir",
                "note": "Büyük duyguların kelimelere sığmadığı o derin sessizlik anı.",
            },
            {
                "orig": "Sì, lo so che non c'è luce in una stanza quando manca il sole",
                "pron": "Si, lo so ke non çe luçe in una stanza kuando manka il sole",
                "tr": "Evet biliyorum; eğer sen güneş gibi orada değilsen, hiçbir odada ışık yoktur.",
                "highlight": "sen güneş gibi orada değilsen",
                "note": "Sevilen insanın, hayatın tek gerçek ışık kaynağı olarak görülmesi.",
            },
            {
                "orig": "Con te partirò, paesi che non ho mai veduto e vissuto con te",
                "pron": "Kon te partiro, paezi ke non o may veduto e vissuto kon te",
                "tr": "Seninle yola çıkacağım; daha önce hiç görmediğim diyarları seninle yaşayacağım.",
                "highlight": "Seninle yola çıkacağım",
                "note": "Nereye gidildiğinin değil, kiminle gidildiğinin önemli olduğu mesajı.",
            },
            {
                "orig": "Adesso sì, li vivrò, con te partirò su navi per mari",
                "pron": "Adesso si, li vivro, kon te partiro su navi per mari",
                "tr": "Şimdi evet, hepsini gerçeğe dönüştüreceğim; seninle okyanusları aşan gemilere bineceğim.",
                "highlight": "okyanusları aşan gemilere",
                "note": "Sevginin insana sınırları aşma cesareti vermesi.",
            },
        ],
    },
    # =========================================================================
    # 10. HİNTÇE (HI) 🇮🇳
    # =========================================================================
    {
        "id": "hi_arijit_singh_tum_hi_ho",
        "language": "hintce",
        "language_code": "HI",
        "language_tr": "Hintçe",
        "flag": "🇮🇳",
        "artist": "Arijit Singh",
        "title": "Tum Hi Ho (तुम ही हो)",
        "release_year": "2013",
        "itunes_query": "Arijit Singh Tum Hi Ho",
        "chorus_timestamp": "0:50 - 1:05 (Hum Tere Bin Nakarat)",
        "social_audio_search": "Arijit Singh - Tum Hi Ho",
        "cover_kicker": "🇮🇳 HİNT MÜZİĞİNİN EN BÜYÜK AŞK ŞARKISI • TÜRKÇE ÇEVİRİ",
        "cover_headline": "HİNTÇE BİLMEYENLERİ BİLE GÖZYAŞINA BOĞAN 'TUM HI HO' NE DEMEK?",
        "viral_hook": "Aashiqui 2 filminin efsanevi müziği 'Tum Hi Ho', Türkçe'de 'Yalnızca Sensin' anlamına gelir. Bir insanı kendi varoluşunun tek nedeni olarak gören saf Doğu romantizminin zirvesidir.",
        "stanzas": [
            {
                "orig": "हम तेरे बिन अब रह नहीं सकते, तेरे बिना क्या वजूद मेरा",
                "pron": "Ham tere bin ab rah nahin sakte, tere bina kya vacud mera",
                "tr": "Artık sensiz tek bir an bile yaşayamam; sen yokken benim varlığımın ne anlamı var ki?",
                "highlight": "varlığımın ne anlamı var ki",
                "note": "'Vacud' (Vücut/Varlık) kelimesi Türkçe ile ortak köklüdür; varoluş anlamı taşır.",
            },
            {
                "orig": "तुझसे जुदा गर हो जाएँगे, तो ख़ुद से ही हो जाएँगे जुदा",
                "pron": "Tucse cuda gar ho cayenge, to hud se hi ho cayenge cuda",
                "tr": "Eğer bir gün senden ayrı düşersem, bil ki kendi ruhumdan da kopmuş olurum.",
                "highlight": "kendi ruhumdan da kopmuş olurum",
                "note": "Sevdiğinden ayrılmayı, insanın kendi benliğinden sürgün edilmesiyle bir tutar.",
            },
            {
                "orig": "क्योंकि तुम ही हो, अब तुम ही हो, ज़िंदगी अब तुम ही हो",
                "pron": "Kyonki tum hi ho, ab tum hi ho, zindagi ab tum hi ho",
                "tr": "Çünkü yalnızca sensin, artık her şeyim sensin; hayat dediğim şey artık sensin.",
                "highlight": "hayat dediğim şey artık sensin",
                "note": "'Zindagi' (Hayat/Can) kelimesiyle tüm yaşamını sevdiğine adar.",
            },
            {
                "orig": "चैन भी, मेरा दर्द भी, मेरी आशिक़ी अब तुम ही हो",
                "pron": "Çeyn bhi, mera dard bhi, meri aşiki ab tum hi ho",
                "tr": "Huzurum da sensin, kalbimdeki sızım da sensin; benim tek aşkım yalnızca sensin.",
                "highlight": "Huzurum da sensin, kalbimdeki sızım da",
                "note": "'Dard' (Dert) ve 'Aşiki' (Aşk) kelimeleri Türkçe ile aynı duygusal mirası paylaşır.",
            },
        ],
    },
    {
        "id": "hi_arijit_singh_kesariya",
        "language": "hintce",
        "language_code": "HI",
        "language_tr": "Hintçe",
        "flag": "🇮🇳",
        "artist": "Arijit Singh & Pritam",
        "title": "Kesariya (केसरिया)",
        "release_year": "2022",
        "itunes_query": "Pritam Arijit Singh Kesariya",
        "chorus_timestamp": "0:48 - 1:03 (Kesariya Tera Ishq Nakarat)",
        "social_audio_search": "Arijit Singh - Kesariya",
        "cover_kicker": "🇮🇳 MODERN HİNT SİNEMASININ EN POPÜLER ŞARKISI",
        "cover_headline": "SAFRAN SARISI BİR AŞKI ANLATAN 'KESARIYA' ŞARKISININ TÜRKÇE ÇEVİRİSİ",
        "viral_hook": "'Kesariya', Hint kültüründe kutsal bağlılığı ve sıcaklığı simgeleyen 'Safran Rengi' demektir. Şarkı, sevdiğinin aşkıyla hayatının tüm solgun renklerinin safran sarısına boyandığını anlatır.",
        "stanzas": [
            {
                "orig": "मुझको इतना बताये कोई, कैसे तुझसे दिल ना लगाये कोई",
                "pron": "Mucko itna bataye koi, keyse tucse dil na lagaye koi",
                "tr": "Biri bana açıklasın; insan seni görüp de sana kalbini kaptırmadan nasıl durabilir?",
                "highlight": "kalbini kaptırmadan nasıl durabilir",
                "note": "Güzelliğin ve zarafetin karşısında kalbin savunmasız kalışı.",
            },
            {
                "orig": "रब्बा ने तुझको बनाने में कर दी है हुस्न की खाली तिजोरियाँ",
                "pron": "Rabba ne tucko banane mein kar di hey hüsn ki hali ticoriyan",
                "tr": "Yaradan seni yaratırken, gökyüzündeki tüm güzellik hazinelerini senin için boşaltmış.",
                "highlight": "tüm güzellik hazinelerini",
                "note": "'Hüsn' (Güzellik) kelimesiyle klasik Doğu divan şiiri geleneğine selam gönderir.",
            },
            {
                "orig": "केसरिया तेरा इश्क़ है पिया, रंग जाऊँ जो मैं हाथ लगाऊँ",
                "pron": "Kesariya tera işk hey piya, rang caun co mein hat lagaun",
                "tr": "Sevgilim, senin aşkın safran rengi gibi; elimi değdirdiğim anda tüm ruhum senin rengine boyanıyor.",
                "highlight": "tüm ruhum senin rengine boyanıyor",
                "note": "Gerçek sevginin dokunduğu her yeri aydınlatması ve dönüştürmesi.",
            },
            {
                "orig": "दिन बीते सारा तेरी फ़िक्र में, रैना सारी तेरी ख़ैर मनाऊँ",
                "pron": "Din bite sara teri fikr mein, reyna sari teri hayr manaun",
                "tr": "Bütün günüm seni düşünmekle, bütün gecem ise senin iyiliğin için dua etmekle geçiyor.",
                "highlight": "iyiliğin için dua etmekle geçiyor",
                "note": "Sevmenin en saf hali: sevdiğin insanın iyiliği için gizlice dua etmek.",
            },
        ],
    },
    # =========================================================================
    # 11. YENİ TREND & VURUCU GLOBAL HİT PAKETİ (10 DİL GENİŞLETİLMİŞ STOK)
    # =========================================================================
    {
        "id": "en_lady_gaga_bruno_die_with_a_smile",
        "language": "ingilizce",
        "language_code": "EN",
        "language_tr": "İngilizce",
        "flag": "🇬🇧",
        "artist": "Lady Gaga & Bruno Mars",
        "title": "Die With A Smile",
        "release_year": "2024",
        "deck_type": "vinyl_turntable",
        "itunes_query": "Lady Gaga Bruno Mars Die With A Smile",
        "chorus_timestamp": "1:18 - 1:45 (Nakarat Zirvesi)",
        "social_audio_search": "Lady Gaga & Bruno Mars - Die With A Smile",
        "cover_kicker": "🇬🇧 YILIN EN BÜYÜK GLOBAL DÜETİ • VURUCU NAKARAT",
        "cover_headline": "'DÜNYA SONA ERSE BİLE YANINDA GÜLÜMSEYEREK ÖLÜRÜM'",
        "viral_hook": "Lady Gaga ve Bruno Mars'ın tüm dünya listelerini altüst eden bu zamansız baladı, yarın dünyanın sonu gelse bile sevdiğin insanın yanındaysan hiçbir pişmanlığın olmayacağını anlatır.",
        "stanzas": [
            {
                "orig": "If the world was ending, I'd wanna be next to you",
                "pron": "İf dı vörld vaz ending, ayd vana bi nekst tu yu",
                "tr": "Eğer bugün dünyanın sonu gelseydi, yalnızca senin yanında olmak isterdim.",
                "highlight": "yalnızca senin yanında olmak isterdim",
                "note": "Kıyamet kopsa bile tek sığınağın sevdiğin insanın yanı olması.",
            },
            {
                "orig": "If the party was over and our time on Earth was through",
                "pron": "İf dı parti vaz ovır end aur taym on ört vaz tru",
                "tr": "Eğer bu hayat şöleni bitseydi ve yeryüzündeki vaktimiz dolsaydı...",
                "highlight": "yeryüzündeki vaktimiz dolsaydı",
                "note": "Hayatı geçici bir davet, aşkı ise geriye kalan tek gerçek olarak görür.",
            },
            {
                "orig": "I'd wanna hold you just for a while and die with a smile",
                "pron": "Ayd vana hold yu cast for a vayl end day vit a smayl",
                "tr": "Sana son bir kez sarılmak ve yüzümde bir tebessümle gözlerimi yummak isterdim.",
                "highlight": "yüzümde bir tebessümle",
                "note": "Gerçek aşkı tatmış bir kalbin ölümden bile korkmaması.",
            },
            {
                "orig": "Right next to you, next to you",
                "pron": "Rayt nekst tu yu, nekst tu yu",
                "tr": "Tam yanı başında, son nefese kadar senin yanında...",
                "highlight": "son nefese kadar senin yanında",
                "note": "Nakaratın en duygusal vurgu noktası.",
            },
            {
                "orig": "Wherever you go, that's where I'll follow",
                "pron": "Verevır yu go, dets ver ayl folov",
                "tr": "Sen nereye gidersen git, adımlarım hep senin izini takip edecek.",
                "highlight": "hep senin izini takip edecek",
                "note": "Koşulsuz sadakat yemini.",
            },
            {
                "orig": "Nobody's promised tomorrow, so I'ma love you every night like it's the last night",
                "pron": "Nobadis promist tumorov, so ayma lav yu evri nayt layk its dı last nayt",
                "tr": "Kimseye yarının garantisi verilmedi; bu yüzden seni her gece son gecemizmiş gibi seveceğim.",
                "highlight": "son gecemizmiş gibi seveceğim",
                "note": "Sevgiyi ertelemeden, her anı son anmış gibi yaşama çağrısı.",
            },
        ],
    },
    {
        "id": "fr_slimane_mon_amour",
        "language": "fransizca",
        "language_code": "FR",
        "language_tr": "Fransızca",
        "flag": "🇫🇷",
        "artist": "Slimane",
        "title": "Mon amour",
        "release_year": "2024",
        "deck_type": "vinyl_turntable",
        "itunes_query": "Slimane Mon amour",
        "chorus_timestamp": "0:48 - 1:15 (Vurucu Nakarat)",
        "social_audio_search": "Slimane - Mon amour",
        "cover_kicker": "🇫🇷 FRANSIZCA DUYGU PATLAMASI • NAKARAT ÇEVİRİSİ",
        "cover_headline": "AVRUPA'YI TİTRETEN 'MON AMOUR' YAKARIŞININ TÜRKÇE ANLAMI",
        "viral_hook": "Slimane'ın mikrofondan metrelerce uzaklaşıp çıplak sesle söylediği o meşhur nakarat, bitmek üzere olan bir aşkın ardından Paris'e dön çağrısı yapan çaresiz ama gururlu bir mektuptur.",
        "stanzas": [
            {
                "orig": "Je t'aime, j'sais pas pourquoi, je reproduis la même scène",
                "pron": "Jö tem, jöse pa purkua, jö röprodüi la mem sen",
                "tr": "Seni seviyorum; nedenini bilmeden hep aynı ayrılık sahnesini yeniden yaşıyorum.",
                "highlight": "Seni seviyorum; nedenini bilmeden",
                "note": "Kalbin mantığa söz geçiremediği o kırılma anı.",
            },
            {
                "orig": "Mais c'est la même fin, tu n'entends pas ma peine",
                "pron": "Me se la mem fen, tü nantan pa ma pen",
                "tr": "Ama sonu hep aynı bitiyor; içimdeki bu derin sızıyı hiç duymuyorsun.",
                "highlight": "içimdeki bu derin sızıyı",
                "note": "Karşılıksız kalan çabanın yorgunluğu.",
            },
            {
                "orig": "Est-ce que tu m'aimes ? J'sais pas si je t'aime",
                "pron": "Es kö tü mem? Jöse pa si jö tem",
                "tr": "Söyle, sen beni gerçekten seviyor musun? Yoksa ben mi hâlâ vazgeçemiyorum?",
                "highlight": "sen beni gerçekten seviyor musun",
                "note": "Şarkının en vurucu sorgulama dizesi.",
            },
            {
                "orig": "Avec toi c'est toujours oui ou bien toujours non",
                "pron": "Avek tua se tujur vi u biyen tujur non",
                "tr": "Seninle her şey ya tamamen siyah ya da tamamen beyaz; ortası hiç olmadı.",
                "highlight": "ortası hiç olmadı",
                "note": "Fırtınalı bir ilişkinin uçlarda yaşanan duyguları.",
            },
            {
                "orig": "Dis-moi l'endroit, je t'attends, viens vivre à Paris",
                "pron": "Di-mua landrua, jö tatan, viyen vivr a Pari",
                "tr": "Sadece buluşacağımız yeri söyle, seni bekliyorum; gel Paris'te yeniden başlayalım.",
                "highlight": "gel Paris'te yeniden başlayalım",
                "note": "Her şeye rağmen kapıyı açık bırakan son çağrı.",
            },
        ],
    },
    {
        "id": "ru_miyagi_i_got_love",
        "language": "rusca",
        "language_code": "RU",
        "language_tr": "Rusça",
        "flag": "🇷🇺",
        "artist": "Miyagi & Эндшпиль feat. Рем Дигга",
        "title": "I Got Love",
        "release_year": "2016",
        "deck_type": "dj_mix_deck",
        "itunes_query": "Miyagi I Got Love",
        "chorus_timestamp": "0:42 - 1:09 (Vurucu Nakarat)",
        "social_audio_search": "Miyagi & Эндшпиль - I Got Love",
        "cover_kicker": "🇷🇺 1 MİLYAR DİNLENEN RUSÇA EFSANE • TÜRKÇE ÇEVİRİ",
        "cover_headline": "TÜM DÜNYANIN EZBERE BİLDİĞİ 'I GOT LOVE' ASLINDA NE DİYOR?",
        "viral_hook": "YouTube'da 1 milyardan fazla dinlenerek tarihe geçen bu parça, karanlık düşünceleri müziğin ve sevginin ritmiyle iyileştirmeyi anlatan hipnotik bir özgürlük marşıdır.",
        "stanzas": [
            {
                "orig": "Окутала меня, окутала, ты будто мой сорт — мариуанна",
                "pron": "Okutala menya, okutala, tı budta moy sort mariuanna",
                "tr": "Beni baştan ayağa sardın, kuşattın; ruhumu baş döndüren bir iksir gibi ele geçirdin.",
                "highlight": "Beni baştan ayağa sardın",
                "note": "Sevginin insanı çepeçevre saran baş döndürücü etkisi.",
            },
            {
                "orig": "Небо в алмазах, лето летало, ты моя бэйби — дочь карнавала",
                "pron": "Neba v almazah, leta letala, tı maya beybi doç karnavala",
                "tr": "Gökyüzü elmaslarla parlıyor, yaz rüzgâr gibi geçti; sen hayatımın en renkli şölenisin.",
                "highlight": "Gökyüzü elmaslarla parlıyor",
                "note": "Karanlık günlerin ardından gelen aydınlık ve coşku.",
            },
            {
                "orig": "Поступай не спеша, делай дела, со мною милая с ума сошла",
                "pron": "Postupay ne speşa, delay dela, sa mnoyu milaya s uma saşla",
                "tr": "Acele etmeden kalbinin sesini dinle; yanımda olduğunda tüm kuralları unutuyoruz.",
                "highlight": "kalbinin sesini dinle",
                "note": "Anın tadını çıkarma ve akışa güvenme çağrısı.",
            },
            {
                "orig": "Мысли мои улетай-тай-тай, давай делай улетай",
                "pron": "Mısli mai uletay-tay-tay, davay delay uletay",
                "tr": "Kafamdaki tüm ağır düşünceler uçup gitsin; bırak ruhumuz gökyüzüne karışsın.",
                "highlight": "tüm ağır düşünceler uçup gitsin",
                "note": "Müziğin ruhu hafifleten sağaltıcı gücü.",
            },
        ],
    },
    {
        "id": "ja_creepy_nuts_bling_bang",
        "language": "japonca",
        "language_code": "JA",
        "language_tr": "Japonca",
        "flag": "🇯🇵",
        "artist": "Creepy Nuts",
        "title": "Bling-Bang-Bang-Born",
        "release_year": "2024",
        "deck_type": "dj_mix_deck",
        "itunes_query": "Creepy Nuts Bling-Bang-Bang-Born",
        "chorus_timestamp": "0:55 - 1:22 (Viral Nakarat)",
        "social_audio_search": "Creepy Nuts - Bling-Bang-Bang-Born",
        "cover_kicker": "🇯🇵 JAPONCA GLOBAL TREND REKORU • TÜRKÇE ÇEVİRİ",
        "cover_headline": "HERKESİN RİTMİYLE SALLANDIĞI BU JAPONCA ŞARKI NE ANLATIYOR?",
        "viral_hook": "Mashle animesiyle tüm dünyada milyarlarca kez dinlenen bu parça, doğuştan gelen yeteneklerin veya ayrıcalıkların olmadan sadece kendi bileğinin gücüyle zirveye çıkmanın zafer marşıdır.",
        "stanzas": [
            {
                "orig": "鏡よ鏡 答えちゃって Who's the best? I'm the best! Oh yeah",
                "pron": "Kagami yo kagami kotaeçatte, huz dı best? Aym dı best!",
                "tr": "Ayna ayna, söyle şimdi hiç çekinmeden: En iyisi kim? Elbette benim!",
                "highlight": "Ayna ayna, söyle şimdi",
                "note": "Başkalarının onayını beklemeden kendi değerini bilme özgüveni.",
            },
            {
                "orig": "生身のまま行けるところまで To the next, to the 一番上",
                "pron": "Namami no mama ikeru tokoro made, tu dı nekst, tu dı içiban ue",
                "tr": "Hiçbir maske ve hile olmadan, kendi gücümle gidebildiğim en zirveye kadar gideceğim.",
                "highlight": "en zirveye kadar gideceğim",
                "note": "Kendi öz kimliğiyle başarıya ulaşma kararlılığı.",
            },
            {
                "orig": "毎日が俺らの誕生日 存在自体がもう反則級",
                "pron": "Mayniçi ga orera no tancobi, sonzay citay ga mo hansoku kyu",
                "tr": "Yaşadığımız her gün bizim yeniden doğuşumuz; kendi halimizle bile kuralları yıkıyoruz.",
                "highlight": "her gün bizim yeniden doğuşumuz",
                "note": "Sıradanlığı reddeden yüksek enerji.",
            },
            {
                "orig": "誰の七光もいらない お前のiceよりbright",
                "pron": "Dare no nanahikari mo iranay, omae no ays yori brayt",
                "tr": "Kimsenin gölgesine veya torpiline ihtiyacım yok; kendi alın terim elmastan daha parlak!",
                "highlight": "elmastan daha parlak",
                "note": "Şarkının en vurucu özgüven dizesi.",
            },
        ],
    },
    {
        "id": "es_floyymenor_gata_only",
        "language": "ispanyolca",
        "language_code": "ES",
        "language_tr": "İspanyolca",
        "flag": "🇪🇸",
        "artist": "FloyyMenor & Cris MJ",
        "title": "Gata Only",
        "release_year": "2024",
        "deck_type": "dj_mix_deck",
        "itunes_query": "FloyyMenor Cris MJ Gata Only",
        "chorus_timestamp": "0:32 - 0:58 (Ana Nakarat)",
        "social_audio_search": "FloyyMenor & Cris MJ - Gata Only",
        "cover_kicker": "🇪🇸 YILIN EN ÇOK DİNLENEN İSPANYOLCA ŞARKISI",
        "cover_headline": "REELS VE TIKTOK'U SALLAYAN 'GATA ONLY' TÜRKÇE ANLAMI",
        "viral_hook": "Şili'den çıkıp tüm dünyada yılın en çok paylaşılan İspanyolca parçası olan 'Gata Only', gece yarısı kalabalıktan uzaklaşıp sadece sevdiği kişiyle baş başa kalmak isteyen bir tutkuyu anlatır.",
        "stanzas": [
            {
                "orig": "Mami, te siento lejana, hora de que seas mía",
                "pron": "Mami, te siyento lehana, ora de ke seas mia",
                "tr": "Seni bu gece çok uzakta hissediyorum; artık aradaki bu mesafeyi kapatma vakti geldi.",
                "highlight": "mesafeyi kapatma vakti geldi",
                "note": "Özlemin sabırsızlığa dönüştüğü ilk dize.",
            },
            {
                "orig": "Hacerte cosas que nunca te harían, conmigo te ves mejor que en su compañía",
                "pron": "Aserte kosas ke nunka te ariyan, konmigo te ves mehor ke en su kompaniya",
                "tr": "Kimsenin sana hissettiremediği o tutkuyu yaşatacağım; benim yanımda her zamankinden daha güzelsin.",
                "highlight": "benim yanımda her zamankinden daha güzelsin",
                "note": "Gerçek uyumun insanın yüzüne yansıyan ışıltısı.",
            },
            {
                "orig": "Pégate, baílame, que contigo quiero estar",
                "pron": "Pegate, baylame, ke kontigo kiyero estar",
                "tr": "Yaklaş yanıma ve benimle dans et; bu gece yalnızca seninle olmak istiyorum.",
                "highlight": "yalnızca seninle olmak istiyorum",
                "note": "En ikonik ritim ve nakarat dizesi.",
            },
            {
                "orig": "Tranquila, que nadie nos va a encontrar",
                "pron": "Trankila, ke nadiye nos va a enkontrar",
                "tr": "İçin rahat olsun; bu gece bizim dünyamızda kimse bizi bulamayacak.",
                "highlight": "kimse bizi bulamayacak",
                "note": "Kalabalık dünyadan kaçıp iki kişilik bir sığınak kurma arzusu.",
            },
        ],
    },
    # =========================================================================
    # 12. ARAPÇA (AR) POPÜLER EFSANELER & VİRAL HİTLER 🇸🇦
    # =========================================================================
    {
        "id": "ar_sherine_kalam_eineh",
        "language": "arapca",
        "language_code": "AR",
        "language_tr": "Arapça",
        "flag": "🇸🇦",
        "artist": "Sherine (شيرين)",
        "title": "Kalam Eineh (كلام عينيه)",
        "release_year": "2018",
        "deck_type": "vinyl_turntable",
        "itunes_query": "Sherine Kalam Eineh",
        "chorus_timestamp": "0:45 - 1:12 (Nakarat Zirvesi)",
        "social_audio_search": "Sherine - Kalam Eineh",
        "cover_kicker": "🇸🇦 TÜRKİYE'DE EN ÇOK SEVİLEN ARAPÇA ŞARKI",
        "cover_headline": "'GÖZLERİNİN SÖYLEDİĞİ SÖZLER TÜM ŞARKILARDAN DAHA GÜZEL'",
        "viral_hook": "Milyarlarca kez dinlenen ve sosyal medyada en çok paylaşılan Arapça şarkı olan 'Kalam Eineh', kelimelere ihtiyaç duymadan sadece gözlerin bakışıyla anlatılan büyüleyici bir aşkı anlatır.",
        "stanzas": [
            {
                "orig": "كلام عينيه في الغرام أحلى من الأغاني",
                "pron": "Kalam eyneyh fil garam ahla min el agani",
                "tr": "Gözlerinin aşkla söylediği o sessiz sözler, dünyadaki bütün şarkılardan daha güzel.",
                "highlight": "bütün şarkılardan daha güzel",
                "note": "Seven bir insanın bakışının en güzel melodiden bile etkileyici olması.",
            },
            {
                "orig": "من كلمتين من سلام ببقى حد تاني",
                "pron": "Min kelmeteyn min selam bebga had tani",
                "tr": "Senden gelen iki küçük kelime ve bir selamla bile bambaşka bir insana dönüşüyorum.",
                "highlight": "bambaşka bir insana dönüşüyorum",
                "note": "Gerçek aşkın insanın ruhunu bir anda yenilemesi.",
            },
            {
                "orig": "لما يميل قلبي أنا وياخدني الحنين",
                "pron": "Lemma yemil kalbi ana ve yahudni el hanin",
                "tr": "Kalbim sana doğru eğildiğinde ve içimi derin bir özlem sardığında...",
                "highlight": "içimi derin bir özlem sardığında",
                "note": "Özlemin kalbi sevdiğine doğru çekmesi.",
            },
            {
                "orig": "تغمض عينيا واطير معاه في غمضة عين",
                "pron": "Tegmad eyneya ve atir maah fi gamdat eyn",
                "tr": "Gözlerimi kapatıyorum ve göz açıp kapayıncaya dek senin yanına kanatlanıyorum.",
                "highlight": "senin yanına kanatlanıyorum",
                "note": "Mesafeleri tek bir hayalle aşan romantik zirve.",
            },
        ],
    },
    {
        "id": "ar_amr_diab_tamally_maak",
        "language": "arapca",
        "language_code": "AR",
        "language_tr": "Arapça",
        "flag": "🇸🇦",
        "artist": "Amr Diab (عمرو دياب)",
        "title": "Tamally Maak (تملي معاك)",
        "release_year": "2000",
        "deck_type": "retro_cassette",
        "itunes_query": "Amr Diab Tamally Maak",
        "chorus_timestamp": "0:38 - 1:05 (Efsane Nakarat)",
        "social_audio_search": "Amr Diab - Tamally Maak",
        "cover_kicker": "🇸🇦 YILLARA MEYDAN OKUYAN ARAPÇA KLASİK",
        "cover_headline": "HERKESİN DUYDUĞU 'TAMALLY MAAK' ŞARKISININ TÜRKÇE ANLAMI",
        "viral_hook": "Akdeniz ve Orta Doğu müziğinin en unutulmaz gitar melodisine sahip olan 'Tamally Maak', sevdiğinden kilometrelerce uzakta olsa bile ruhunun daima onunla kaldığını anlatır.",
        "stanzas": [
            {
                "orig": "تملي معاك ولو حتى بعيد عني في قلبي هواك",
                "pron": "Tamalli maak ve lev hatta baid anni fi kalbi hevak",
                "tr": "Daima seninleyim; benden çok uzaklarda olsan bile aşkın hep kalbimin en içinde.",
                "highlight": "Daima seninleyim",
                "note": "Mesafelerin gerçek bağlılığı eksiltemeyeceğini anlatan kült dize.",
            },
            {
                "orig": "تملي معاك تملي في بالي وفي قلبي ولا بنساك",
                "pron": "Tamalli maak, tamalli fi bali ve fi kalbi vela bensak",
                "tr": "Her an seninleyim; daima aklımdasın, kalbimdesin ve seni bir an bile unutmuyorum.",
                "highlight": "seni bir an bile unutmuyorum",
                "note": "Zihni ve kalbi aynı anda dolduran sadakat.",
            },
            {
                "orig": "تملي واحشني لو حتى بكون وياك",
                "pron": "Tamalli vahişni lev hatta bekun veyyak",
                "tr": "Seni o kadar çok seviyorum ki, tam yanımda olduğun anda bile seni özlüyorum.",
                "highlight": "yanımda olduğun anda bile seni özlüyorum",
                "note": "Şarkının en ünlü ve en derin aşk dizesi.",
            },
            {
                "orig": "تملي حبيبي بشتاقلك تملي عينيا تندهلك",
                "pron": "Tamalli habibi beştaglak, tamalli eyneya tendehlak",
                "tr": "Sevgilim, her nefeste seni arzuluyorum; gözlerim sessizce hep senin adını çağırıyor.",
                "highlight": "gözlerim sessizce hep senin adını çağırıyor",
                "note": "Bakışların özlemle sevdiğini araması.",
            },
        ],
    },
    {
        "id": "ar_nancy_ajram_ya_tabtab",
        "language": "arapca",
        "language_code": "AR",
        "language_tr": "Arapça",
        "flag": "🇸🇦",
        "artist": "Nancy Ajram (نانسي عجرم)",
        "title": "Ya Tabtab Wa Dalla (يا طبطب ودلع)",
        "release_year": "2006",
        "deck_type": "optical_cd_deck",
        "itunes_query": "Nancy Ajram Ya Tabtab",
        "chorus_timestamp": "0:35 - 1:02 (Nakarat)",
        "social_audio_search": "Nancy Ajram - Ya Tabtab Wa Dalla",
        "cover_kicker": "🇸🇦 2000'LERİN EN POPÜLER ARAPÇA HİTİ • TÜRKÇE ÇEVİRİ",
        "cover_headline": "ÇOCUKLUĞUMUZDAN BERİ DUYDUĞUMUZ 'YA TABTAB' NE ANLATIYOR?",
        "viral_hook": "Türkiye'de de yıllarca her yerde çalan bu enerjik şarkı, sevdiği insanın kaprislerinden ve sitemlerinden yorulsa da ondan asla vazgeçemeyen tatlı bir sitemi anlatır.",
        "stanzas": [
            {
                "orig": "يا طبطب ودلع يا يقولي أنا اتغيرت عليه",
                "pron": "Ya tabtab ve dalla, ya yegulli ana itgayyart aleyh",
                "tr": "Ya onun gönlünü hoş tutup şımartacağım ya da hemen kendisine karşı değiştiğimi söyleyip küsecek.",
                "highlight": "gönlünü hoş tutup şımartacağım",
                "note": "Sevdiği insanın bitmeyen ilgi beklentisine tatlı bir sitem.",
            },
            {
                "orig": "أنا أزعل أولع ما هو كل همه إزاي أرضيه",
                "pron": "Ana ez'al evalla, ma hu küllü hemmu izzay erdih",
                "tr": "Ben üzülsem de kahrolsam da fark etmiyor; tek düşündüğü şey onun gönlünü nasıl alacağım.",
                "highlight": "onun gönlünü nasıl alacağım",
                "note": "Aşkta hep alttan alan taraf olmanın yorgunluğu.",
            },
            {
                "orig": "قولوله ده أنا برضه ساعات بحالات",
                "pron": "Gululu de ana bardo saat bi halat",
                "tr": "Söyleyin ona; benim de bazen kırıldığım, ilgi beklediğim zamanlar oluyor.",
                "highlight": "benim de bazen kırıldığım",
                "note": "Karşılıklı anlayış bekleyen samimi çağrı.",
            },
            {
                "orig": "ومهما زعلت أنا قلبي معاه",
                "pron": "Ve mehma zealt ana kalbi maah",
                "tr": "Ama ne kadar kızarsam kızayım, kalbim yine de hep onun yanında kalıyor.",
                "highlight": "kalbim yine de hep onun yanında",
                "note": "Tüm sitemlere rağmen vazgeçemeyen sevgi.",
            },
        ],
    },
    # =========================================================================
    # 13. İNGİLİZCE (EN) YÜKSEK AĞIRLIKLI POPÜLER & KÜLT HİTLER 🇬🇧
    # =========================================================================
    {
        "id": "en_tom_odell_another_love",
        "language": "ingilizce",
        "language_code": "EN",
        "language_tr": "İngilizce",
        "flag": "🇬🇧",
        "artist": "Tom Odell",
        "title": "Another Love",
        "release_year": "2013",
        "deck_type": "vinyl_turntable",
        "itunes_query": "Tom Odell Another Love",
        "chorus_timestamp": "2:05 - 2:32 (Piyano & Vokal Zirvesi)",
        "social_audio_search": "Tom Odell - Another Love",
        "cover_kicker": "🇬🇧 TÜM ZAMANLARIN EN DUYGUSAL İNGİLİZCE ŞARKISI",
        "cover_headline": "'TÜM GÖZYAŞLARIMI BAŞKA BİR AŞKTA TÜKETTİM'",
        "viral_hook": "Piyano melodisi başladığı anda herkesin boğazını düğümleyen 'Another Love', geçmişteki bir kalp kırıklığında tüm gözyaşlarını tükettiği için yeni sevdiği insana ağlayacak gücü kalmayan bir kalbin itirafıdır.",
        "stanzas": [
            {
                "orig": "I wanna take you somewhere so you know I care",
                "pron": "Ay vana teyk yu samver so yu nov ay ker",
                "tr": "Sana ne kadar değer verdiğimi bilmen için seni çok güzel bir yere götürmek istiyorum.",
                "highlight": "Sana ne kadar değer verdiğimi bilmen için",
                "note": "Sevmek isteyen ama geçmişin yükünü taşıyan yorgun bir başlangıç.",
            },
            {
                "orig": "But it's so cold and I don't know where",
                "pron": "Bat its so kold end ay dont nov ver",
                "tr": "Ama dışarısı o kadar soğuk ki ve seni nereye götüreceğimi bile bilmiyorum.",
                "highlight": "nereye götüreceğimi bile bilmiyorum",
                "note": "İç dünyasındaki çaresizlik ve yönsüzlük.",
            },
            {
                "orig": "And I'doni sing a song that'd be just ours",
                "pron": "End ayd sing a song det bi cast aurs",
                "tr": "Sadece ikimize ait olacak o özel şarkıyı sana söylemek isterdim...",
                "highlight": "Sadece ikimize ait olacak",
                "note": "Yeni bir hikaye yazma arzusu.",
            },
            {
                "orig": "But I sang 'em all to another heart",
                "pron": "Bat ay seng em ol tu enadır hart",
                "tr": "Ama o şarkıların hepsini daha önce başka bir kalbe söyleyip tükettim.",
                "highlight": "başka bir kalbe söyleyip tükettim",
                "note": "Şarkının en can yakan kırılma dizesi.",
            },
            {
                "orig": "And if somebody hurts you, I wanna fight",
                "pron": "End if sambadi hörts yu, ay vana fayt",
                "tr": "Eğer biri seni incitecek olursa, senin için sonuna kadar savaşmak istiyorum.",
                "highlight": "senin için sonuna kadar savaşmak",
                "note": "Koruma ve sahip çıkma içgüdüsü.",
            },
            {
                "orig": "But my hands been broken one too many times",
                "pron": "Bat may hends bin brokın van tu meni tayms",
                "tr": "Fakat ellerim geçmişte o kadar çok kez kırıldı ki artık gücüm kalmadı.",
                "highlight": "ellerim geçmişte o kadar çok kez kırıldı ki",
                "note": "Geçmiş yaraların bugünkü gücü tüketmesi.",
            },
            {
                "orig": "On another love, all my tears have been used up",
                "pron": "On enadır lav, ol may tiırs hev bin yuzd ap",
                "tr": "Başka bir aşk uğruna, içimdeki bütün gözyaşlarım çoktan tükendi.",
                "highlight": "bütün gözyaşlarım çoktan tükendi",
                "note": "Nakaratın unutulmaz zirvesi.",
            },
        ],
    },
    {
        "id": "en_the_weeknd_blinding_lights",
        "language": "ingilizce",
        "language_code": "EN",
        "language_tr": "İngilizce",
        "flag": "🇬🇧",
        "artist": "The Weeknd",
        "title": "Blinding Lights",
        "release_year": "2020",
        "deck_type": "dj_mix_deck",
        "itunes_query": "The Weeknd Blinding Lights",
        "chorus_timestamp": "0:48 - 1:15 (Ana Nakarat)",
        "social_audio_search": "The Weeknd - Blinding Lights",
        "cover_kicker": "🇬🇧 TARİHİN EN ÇOK DİNLENEN İNGİLİZCE ŞARKISI",
        "cover_headline": "SPOTIFY REKORU KIRAN 'BLINDING LIGHTS' TÜRKÇE ANLAMI",
        "viral_hook": "Müzik tarihinde tüm zamanların en çok dinlenen şarkısı olan 'Blinding Lights', gece yarısı şehir ışıklarının altında sevdiği insanın dokunuşu olmadan uyuyamayan bir yalnızlığı anlatır.",
        "stanzas": [
            {
                "orig": "I've been tryna call, I've been on my own for long enough",
                "pron": "Ayv bin trayna kol, ayv bin on may ovn for long inaf",
                "tr": "Seni aramaya çalışıyorum; artık yeterince uzun zamandır yapayalnızım.",
                "highlight": "artık yeterince uzun zamandır yapayalnızım",
                "note": "Gece yarısı başlayan o tanıdık yalnızlık hissi.",
            },
            {
                "orig": "Maybe you can show me how to love, maybe",
                "pron": "Meybi yu ken şov mi hav tu lav, meybi",
                "tr": "Belki de bana yeniden nasıl sevileceğini yalnızca sen öğretebilirsin.",
                "highlight": "yeniden nasıl sevileceğini",
                "note": "Soğumuş bir kalbin yeniden ısınma umudu.",
            },
            {
                "orig": "Sin City's cold and empty, no one's around to judge me",
                "pron": "Sin Sitis kold end empti, no vans eraund tu cac mi",
                "tr": "Bu koca şehir sensiz buz gibi ve bomboş; etrafta beni yargılayacak kimse bile yok.",
                "highlight": "sensiz buz gibi ve bomboş",
                "note": "Kalabalık metropolün sevdiğin yokken ıssızlaşması.",
            },
            {
                "orig": "I look around and Sin City's cold and empty",
                "pron": "Ay luk eraund end Sin Sitis kold end empti",
                "tr": "Etrafıma bakıyorum; sensiz her yer soğuk ve anlamsız.",
                "highlight": "sensiz her yer soğuk",
                "note": "Şehir ışıkları ne kadar parlasa da iç dünyasının karanlık oluşu.",
            },
            {
                "orig": "I said, ooh, I'm blinded by the lights",
                "pron": "Ay sed, uuu, aym blayndıd bay dı layts",
                "tr": "Gözlerim bu sahte ışıklarla kamaşıyor ama aradığım tek ışık sensin.",
                "highlight": "aradığım tek ışık sensin",
                "note": "İkonik nakarat dizesi.",
            },
            {
                "orig": "No, I can't sleep until I feel your touch",
                "pron": "No, ay kent slip antil ay fil yor taç",
                "tr": "Hayır; senin sıcaklığını ve dokunuşunu hissedene dek gözüme uyku girmeyecek.",
                "highlight": "dokunuşunu hissedene dek",
                "note": "Huzuru yalnızca sevdiğinin yanında bulabilme hali.",
            },
        ],
    },
    {
        "id": "en_adele_someone_like_you",
        "language": "ingilizce",
        "language_code": "EN",
        "language_tr": "İngilizce",
        "flag": "🇬🇧",
        "artist": "Adele",
        "title": "Someone Like You",
        "release_year": "2011",
        "deck_type": "vinyl_turntable",
        "itunes_query": "Adele Someone Like You",
        "chorus_timestamp": "1:14 - 1:41 (Nakarat Zirvesi)",
        "social_audio_search": "Adele - Someone Like You",
        "cover_kicker": "🇬🇧 İNGİLİZCE AYRILIK ŞARKILARININ ZİRVESİ • TÜRKÇE ÇEVİRİ",
        "cover_headline": "'ÖNEMİ YOK, SENİN GİBİ BİRİNİ ELBET BULACAĞIM'",
        "viral_hook": "Adele'in seslendirirken gözyaşlarını tutamadığı bu başyapıt, eski sevdiğinin evlendiğini duyduğunda hem onun adına mutlu olmaya çalışan hem de içten içe yıkılan asil bir vedayı anlatır.",
        "stanzas": [
            {
                "orig": "I heard that you're settled down, that you found a girl and you're married now",
                "pron": "Ay hörd det yor setıld daun, det yu faund a görl end yor merid nav",
                "tr": "Duydum ki artık durulmuşsun; kalbine göre birini bulmuş ve evlenmişsin.",
                "highlight": "kalbine göre birini bulmuş",
                "note": "Şarkının kalbi durduran ilk cümlesi.",
            },
            {
                "orig": "I heard that your dreams came true, guess she gave you things I didn't give to you",
                "pron": "Ay hörd det yor drims keym tru, ges şi geyv yu tings ay didnt giv tu yu",
                "tr": "Hayallerinin gerçekleştiğini duydum; sanırım benim sana veremediğim huzuru o verdi.",
                "highlight": "benim sana veremediğim huzuru",
                "note": "Acı bir kabulleniş ve öz eleştiri.",
            },
            {
                "orig": "Never mind, I'll find someone like you",
                "pron": "Nevır maynd, ayl faynd samvan layk yu",
                "tr": "Zararı yok, üzülme; elbet bir gün ben de tıpkı senin gibi birini bulacağım.",
                "highlight": "tıpkı senin gibi birini bulacağım",
                "note": "Unutmaya çalışırken bile yine ona benzeyen birini arama çelişkisi.",
            },
            {
                "orig": "I wish nothing but the best for you, too",
                "pron": "Ay viş nating bat dı best for yu tu",
                "tr": "Senin için de hayatta her zaman en güzelini diliyorum.",
                "highlight": "her zaman en güzelini diliyorum",
                "note": "Kırgınlığa rağmen sevdiğinin iyiliğini dileyen olgunluk.",
            },
            {
                "orig": "Don't forget me, I beg, I remember you said",
                "pron": "Dont forget mi, ay beg, ay rimembır yu sed",
                "tr": "Yalvarırım beni tamamen unutma; bir zamanlar bana söylediğin o sözü hâlâ hatırlıyorum:",
                "highlight": "Yalvarırım beni tamamen unutma",
                "note": "Gururun kırılıp geriye sadece hatıralarda kalma isteğinin kaldığı an.",
            },
            {
                "orig": "Sometimes it lasts in love, but sometimes it hurts instead",
                "pron": "Samtayms it lasts in lav, bat samtayms it hörts insted",
                "tr": "Aşk bazen sonsuza dek sürer; ama bazen de geriye sadece derin bir sızı bırakır.",
                "highlight": "geriye sadece derin bir sızı bırakır",
                "note": "Tüm zamanların en unutulmaz nakarat kapanışı.",
            },
        ],
    },
    {
        "id": "en_sia_unstoppable",
        "language": "ingilizce",
        "language_code": "EN",
        "language_tr": "İngilizce",
        "flag": "🇬🇧",
        "artist": "Sia",
        "title": "Unstoppable",
        "release_year": "2016",
        "deck_type": "dj_mix_deck",
        "itunes_query": "Sia Unstoppable",
        "chorus_timestamp": "0:46 - 1:13 (Güçlü Nakarat)",
        "social_audio_search": "Sia - Unstoppable",
        "cover_kicker": "🇬🇧 ÖZGÜVEN VE GÜÇ VEREN İNGİLİZCE EFSANE",
        "cover_headline": "GÖZYAŞLARINI GİZLEYİP DÜNYAYA MEYDAN OKUYANLARIN ŞARKISI",
        "viral_hook": "Milyonlarca insanın motivasyon marşı olan 'Unstoppable', aslında içinde fırtınalar kopsa ve yalnızken ağlasa bile dış dünyaya karşı kırılmaz bir zırh kuşanan güçlü ruhları anlatır.",
        "stanzas": [
            {
                "orig": "I'll smile, I know what it takes to fool this town",
                "pron": "Ayl smayl, ay nov vat it teyks tu ful dis taun",
                "tr": "Yüzüme bir gülümseme takınacağım; bu şehri güçlü olduğuma inandırmanın yolunu biliyorum.",
                "highlight": "güçlü olduğuma inandırmanın yolunu",
                "note": "İçindeki kırgınlığı dünyadan saklama sanatı.",
            },
            {
                "orig": "I'll do it 'til the sun goes down and all through the night time",
                "pron": "Ayl du it til dı san goz daun end ol tru dı nayt taym",
                "tr": "Güneş batana dek ve bütün gece boyunca dimdik durmaya devam edeceğim.",
                "highlight": "dimdik durmaya devam edeceğim",
                "note": "Pes etmeyen irade.",
            },
            {
                "orig": "I put my armor on, show you how strong how I am",
                "pron": "Ay put may armır on, şov yu hav strong hav ay em",
                "tr": "Görünmez zırhımı kuşanıyorum ve sana ne kadar sarsılmaz olduğumu gösteriyorum.",
                "highlight": "Görünmez zırhımı kuşanıyorum",
                "note": "Acıyı güce dönüştüren metafor.",
            },
            {
                "orig": "I'm unstoppable, I'm a Porsche with no brakes",
                "pron": "Aym anstopıbıl, aym a Porş vit no breyks",
                "tr": "Ben durdurulamazım; frenleri olmayan, hedefine kilitlenmiş bir fırtına gibiyim.",
                "highlight": "Ben durdurulamazım",
                "note": "Nakaratın en enerjik zirvesi.",
            },
            {
                "orig": "I'm invincible, yeah, I win every single game",
                "pron": "Aym invinsıbıl, ye, ay vin evri singıl geym",
                "tr": "Ben yenilmezim; hayatın karşıma çıkardığı her mücadeleden zaferle çıkacağım.",
                "highlight": "her mücadeleden zaferle çıkacağım",
                "note": "Kendi kendine verilen söz ve motivasyon.",
            },
        ],
    },
    # =========================================================================
    # YENİ DALGA 11 DİL GLOBAL VİRAL HİT KATALOĞU (30+ YENİ ŞARKI)
    # =========================================================================
    {
        "id": "en_hozier_take_me_to_church",
        "language": "ingilizce",
        "language_code": "EN",
        "language_tr": "İngilizce",
        "flag": "🇬🇧",
        "artist": "Hozier",
        "title": "Take Me To Church",
        "release_year": "2013",
        "itunes_query": "Hozier Take Me To Church",
        "artwork_url": "",
        "chorus_timestamp": "0:58 - 1:25 (Efsanevi Nakarat Zirvesi)",
        "social_audio_search": "Hozier - Take Me To Church",
        "cover_kicker": "🇬🇧 İNGİLİZCE EFSANE HİT • TÜRKÇE ÇEVİRİ",
        "cover_headline": "SEVGİYİ KUTSAL BİR İBADET GİBİ ANLATAN EFSANE ŞARKI",
        "viral_hook": "Hozier'in dünyayı sarsan başyapıtı 'Take Me To Church', insanın sevdiği kişiye duyduğu tutkuyu ve koşulsuz teslimiyeti şiirsel bir dille anlatır.",
        "stanzas": [
            {
                "orig": "Take me to church, I'll worship like a dog at the shrine of your lies",
                "pron": "Teyk mi tu çörç, ayl vörşip layk e dog et dı şrayn of yor layz",
                "tr": "Beni mabedine götür; göz göre göre söylediğin sözlerin önünde bile sadakatle eğilirim.",
                "highlight": "sadakatle eğilirim",
                "note": "Aşkta mantığın sustuğu ve teslimiyetin başladığı an.",
            },
            {
                "orig": "I'll tell you my sins and you can sharpen your knife",
                "pron": "Ayl tel yu may sinz end yu ken şarpın yor nayf",
                "tr": "Sana tüm günahlarımı ve zaaflarımı anlatacağım; istersen yaralarımı daha da derinleştirebilirsin.",
                "highlight": "tüm günahlarımı ve zaaflarımı",
                "note": "Sevdiği insana karşı tamamen savunmasız kalmak.",
            },
            {
                "orig": "Offer me that deathless death, good God, let me give you my life",
                "pron": "Ofır mi det detles det, gud gad, let mi giv yu may layf",
                "tr": "Bana o ölümsüz aşkı bahşet; bırak tüm ömrümü senin kollarında feda edeyim.",
                "highlight": "tüm ömrümü senin kollarında",
                "note": "Nakaratın en sarsıcı zirve cümlesi.",
            },
        ],
    },
    {
        "id": "en_lana_del_rey_summertime_sadness",
        "language": "ingilizce",
        "language_code": "EN",
        "language_tr": "İngilizce",
        "flag": "🇬🇧",
        "artist": "Lana Del Rey",
        "title": "Summertime Sadness",
        "release_year": "2012",
        "itunes_query": "Lana Del Rey Summertime Sadness",
        "artwork_url": "",
        "chorus_timestamp": "0:52 - 1:19 (Melankolik Nakarat Zirvesi)",
        "social_audio_search": "Lana Del Rey - Summertime Sadness",
        "cover_kicker": "🇬🇧 İNGİLİZCE MELANKOLİ KLASİĞİ • TÜRKÇE ÇEVİRİ",
        "cover_headline": "'GİTMEDEN ÖNCE BENİ SON KEZ ÖP': YAZ HÜZNÜNÜN ŞARKISI",
        "viral_hook": "Lana Del Rey'in zamansız klasiği 'Summertime Sadness', en parlak yaz günlerinde bile insanın içini kaplayan ayrılık korkusunu ve vedayı anlatır.",
        "stanzas": [
            {
                "orig": "Kiss me hard before you go, summertime sadness",
                "pron": "Kis mi hard bifor yu go, samırtaym sednıs",
                "tr": "Beni bırakıp gitmeden önce son kez sımsıkı öp; içimde derin bir yaz hüznü var.",
                "highlight": "gitmeden önce son kez sımsıkı öp",
                "note": "Vedalaşma anındaki çaresiz tutku.",
            },
            {
                "orig": "I just wanted you to know, that baby, you the best",
                "pron": "Ay cast vontıd yu tu nov, det beybi yu dı best",
                "tr": "Sadece şunu bilmeni istedim sevgilim; hayatıma giren en güzel şey sendin.",
                "highlight": "hayatıma giren en güzel şey sendin",
                "note": "Ayrılıkta bile değişmeyen minnet ve sevgi.",
            },
            {
                "orig": "I got my red dress on tonight, dancing in the dark in the pale moonlight",
                "pron": "Ay gat may red dres on tunayt, densing in dı dark in dı peyl munlayt",
                "tr": "Bu gece senin için kırmızı elbisemi giydim; solgun ay ışığında karanlıkla dans ediyorum.",
                "highlight": "solgun ay ışığında karanlıkla",
                "note": "Sinematik yalnızlık sahnesi.",
            },
        ],
    },
    {
        "id": "en_coldplay_yellow",
        "language": "ingilizce",
        "language_code": "EN",
        "language_tr": "İngilizce",
        "flag": "🇬🇧",
        "artist": "Coldplay",
        "title": "Yellow",
        "release_year": "2000",
        "itunes_query": "Coldplay Yellow",
        "artwork_url": "",
        "chorus_timestamp": "0:50 - 1:17 (Yıldızların Parladığı Nakarat)",
        "social_audio_search": "Coldplay - Yellow",
        "cover_kicker": "🇬🇧 İNGİLİZCE ROMANTİK BAŞYAPIT • TÜRKÇE ÇEVİRİ",
        "cover_headline": "'YILDIZLARA BAK, SENİN İÇİN NASIL DA PARLIYORLAR'",
        "viral_hook": "Coldplay'in milyarlarca kalbe dokunan 'Yellow' şarkısı, gece gökyüzündeki tüm yıldızların sevilen insan için parladığını anlatan en saf aşk ilanıdır.",
        "stanzas": [
            {
                "orig": "Look at the stars, look how they shine for you",
                "pron": "Luk et dı starz, luk hav dey şayn for yu",
                "tr": "Başını kaldırıp gökyüzündeki yıldızlara bak; senin için nasıl da ışıldadıklarını gör.",
                "highlight": "senin için nasıl da ışıldadıklarını gör",
                "note": "Müzik tarihinin en unutulmaz açılış dizelerinden biri.",
            },
            {
                "orig": "And everything you do, yeah, they were all yellow",
                "pron": "End evriting yu du, ye, dey vör ol yelov",
                "tr": "Ve senin dokunduğun, yaptığın her şey karanlığı aydınlatan sıcak bir altın sarısıydı.",
                "highlight": "karanlığı aydınlatan sıcak bir altın sarısıydı",
                "note": "Sevginin hayatı aydınlatma metaforu.",
            },
            {
                "orig": "Your skin, oh yeah, your skin and bones, turn into something beautiful",
                "pron": "Yor skin, o ye, yor skin end bonz, törn intu samting biyutiful",
                "tr": "Senin varlığın ve her bir zerren, gözlerimin önünde eşsiz bir mucizeye dönüşüyor.",
                "highlight": "eşsiz bir mucizeye dönüşüyor",
                "note": "Saf hayranlık ve bağlılık.",
            },
        ],
    },
    {
        "id": "en_ed_sheeran_perfect",
        "language": "ingilizce",
        "language_code": "EN",
        "language_tr": "İngilizce",
        "flag": "🇬🇧",
        "artist": "Ed Sheeran",
        "title": "Perfect",
        "release_year": "2017",
        "itunes_query": "Ed Sheeran Perfect",
        "artwork_url": "",
        "chorus_timestamp": "0:55 - 1:22 (Karanlıkta Dans Nakaratı)",
        "social_audio_search": "Ed Sheeran - Perfect",
        "cover_kicker": "🇬🇧 İNGİLİZCE AŞK KLASİĞİ • TÜRKÇE ÇEVİRİ",
        "cover_headline": "GERÇEK AŞKI BULANLARIN İLK DANS ŞARKISI: PERFECT",
        "viral_hook": "Ed Sheeran'ın çocukluk aşkı olan eşine yazdığı 'Perfect', kusurlu bir dünyada iki insanın birbirinde kusursuz huzuru bulmasını anlatır.",
        "stanzas": [
            {
                "orig": "Baby, I'm dancing in the dark, with you between my arms",
                "pron": "Beybi, aym densing in dı dark, vit yu bitvin may armz",
                "tr": "Sevgilim, seni kollarımın arasına almış gecenin karanlığında huzurla dans ediyorum.",
                "highlight": "kollarımın arasına almış",
                "note": "Romantik nakaratın kalbi.",
            },
            {
                "orig": "Barefoot on the grass, listening to our favourite song",
                "pron": "Berfut on dı gres, lısıning tu aur feyvrit song",
                "tr": "Çimlerin üzerinde yalınayak, ikimizin en sevdiği o şarkıyı dinleyerek...",
                "highlight": "ikimizin en sevdiği o şarkıyı",
                "note": "Sadelik içindeki mutluluk.",
            },
            {
                "orig": "I have faith in what I see, now I know I have met an angel in person",
                "pron": "Ay hev feyt in vot ay si, nav ay nov ay hev met en eyncıl in pörsın",
                "tr": "Gözlerimin gördüğü bu güzelliğe inanıyorum; artık yeryüzünde gerçek bir melekle tanıştığımı biliyorum.",
                "highlight": "gerçek bir melekle tanıştığımı biliyorum",
                "note": "Şarkının duygusal zirvesi.",
            },
        ],
    },
    {
        "id": "en_lewis_capaldi_someone_you_loved",
        "language": "ingilizce",
        "language_code": "EN",
        "language_tr": "İngilizce",
        "flag": "🇬🇧",
        "artist": "Lewis Capaldi",
        "title": "Someone You Loved",
        "release_year": "2018",
        "itunes_query": "Lewis Capaldi Someone You Loved",
        "artwork_url": "",
        "chorus_timestamp": "0:50 - 1:17 (Yürek Burkan Nakarat)",
        "social_audio_search": "Lewis Capaldi - Someone You Loved",
        "cover_kicker": "🇬🇧 İNGİLİZCE DUYGUSAL ZİRVE • TÜRKÇE ÇEVİRİ",
        "cover_headline": "YOKLUĞUNA ALIŞAMADIĞIMIZ İNSANLARA YAZILAN EN AĞIR ŞARKI",
        "viral_hook": "Lewis Capaldi'nin milyonları ağlatan 'Someone You Loved' şarkısı, hayatımızdaki en büyük dayanağı kaybettikten sonra kalan boşluğu anlatır.",
        "stanzas": [
            {
                "orig": "Now the day bleeds into nightfall, and you're not here to get me through it all",
                "pron": "Nav dı dey blidz intu naytfol, end yor nat hir tu get mi tru it ol",
                "tr": "Şimdi gün kanayarak geceye karışıyor ve bu karanlığı aşmam için artık yanımda sen yoksun.",
                "highlight": "artık yanımda sen yoksun",
                "note": "Yalnızlığın en ağır çöktüğü akşam saati.",
            },
            {
                "orig": "I let my guard down and then you pulled the rug",
                "pron": "Ay let may gard davn end den yu puld dı rag",
                "tr": "Sana güvenip tüm savunmamı indirdim; sense ayağımın altındaki zemini bir anda çektin.",
                "highlight": "tüm savunmamı indirdim",
                "note": "Güven kırıklığı ve beklenmedik veda.",
            },
            {
                "orig": "I was getting kinda used to being someone you loved",
                "pron": "Ay voz geting kaynda yuzd tu biing samvan yu lavd",
                "tr": "Senin tarafından sevilen biri olma hissine daha yeni alışmaya başlamıştım.",
                "highlight": "senin tarafından sevilen biri",
                "note": "Unutulmaz nakarat cümlesi.",
            },
        ],
    },
    {
        "id": "en_imagine_dragons_believer",
        "language": "ingilizce",
        "language_code": "EN",
        "language_tr": "İngilizce",
        "flag": "🇬🇧",
        "artist": "Imagine Dragons",
        "title": "Believer",
        "release_year": "2017",
        "itunes_query": "Imagine Dragons Believer",
        "artwork_url": "",
        "chorus_timestamp": "0:42 - 1:09 (Patlayıcı Nakarat)",
        "social_audio_search": "Imagine Dragons - Believer",
        "cover_kicker": "🇬🇧 İNGİLİZCE GÜÇ & MOTİVASYON • TÜRKÇE ÇEVİRİ",
        "cover_headline": "'ACI BENİ YIKMADI, İNANAN BİRİNE DÖNÜŞTÜRDÜ'",
        "viral_hook": "Imagine Dragons'ın milyarlarca kez dinlenen 'Believer' marşı, insanın çektiği acıların ve kırgınlıkların onu nasıl yenilmez bir karaktere dönüştürdüğünü anlatır.",
        "stanzas": [
            {
                "orig": "Pain! You made me a, you made me a believer, believer",
                "pron": "Peyn! Yu meyd mi e, yu meyd mi e bilivır, bilivır",
                "tr": "Çektiğim acılar! Beni yıkmak yerine küllerimden doğan inançlı bir savaşçıya dönüştürdünüz.",
                "highlight": "küllerimden doğan inançlı bir savaşçıya",
                "note": "Acıyı güce dönüştüren nakarat.",
            },
            {
                "orig": "Pain! You break me down and build me up, believer, believer",
                "pron": "Peyn! Yu breyk mi davn end bild mi ap, bilivır, bilivır",
                "tr": "Hayatın darbeleri beni önce parçaladı ama her seferinde çok daha güçlü inşa etti.",
                "highlight": "çok daha güçlü inşa etti",
                "note": "Pes etmeyenlerin mottosu.",
            },
            {
                "orig": "My life, my love, my drive, it came from pain",
                "pron": "May layf, may lav, may drayv, it keym from peyn",
                "tr": "Bugünkü hayatım, sevdam ve içimdeki bu durdurulamaz azim; hepsi çektiğim acılardan doğdu.",
                "highlight": "hepsi çektiğim acılardan doğdu",
                "note": "Şarkının felsefesini özetleyen kapanış.",
            },
        ],
    },
    {
        "id": "en_harry_styles_as_it_was",
        "language": "ingilizce",
        "language_code": "EN",
        "language_tr": "İngilizce",
        "flag": "🇬🇧",
        "artist": "Harry Styles",
        "title": "As It Was",
        "release_year": "2022",
        "itunes_query": "Harry Styles As It Was",
        "artwork_url": "",
        "chorus_timestamp": "0:38 - 1:05 (Nostaljik Ritim & Nakarat)",
        "social_audio_search": "Harry Styles - As It Was",
        "cover_kicker": "🇬🇧 İNGİLİZCE GLOBAL REKOR • TÜRKÇE ÇEVİRİ",
        "cover_headline": "NEŞELİ MELODİNİN ARKASINDAKİ HÜZÜN: 'ARTIK HİÇBİR ŞEY ESKİSİ GİBİ DEĞİL'",
        "viral_hook": "Harry Styles'ın tüm dünya listelerini altüst eden 'As It Was' şarkısı, hareketli ritminin altında geçmişe duyulan özlemi ve değişen hayatın yalnızlığını gizler.",
        "stanzas": [
            {
                "orig": "In this world, it's just us, you know it's not the same as it was",
                "pron": "İn dis vörld, its cast as, yu nov its nat dı seym ez it voz",
                "tr": "Bu koca dünyada sadece ikimiz kaldık; ama biliyorsun ki artık hiçbir şey eskisi gibi değil.",
                "highlight": "artık hiçbir şey eskisi gibi değil",
                "note": "Zamanın değiştirdiği duygular.",
            },
            {
                "orig": "Answer the phone, Harry, you're no good alone, why are you sitting at home on the floor?",
                "pron": "Ensır dı fon, Heri, yor no gud elon, vay ar yu siting et hom on dı flor?",
                "tr": "Telefonu aç artık; yalnızlık sana hiç iyi gelmiyor, neden evde tek başına yerde oturuyorsun?",
                "highlight": "yalnızlık sana hiç iyi gelmiyor",
                "note": "Kalabalıklar içindeki yalnızlık.",
            },
        ],
    },
    {
        "id": "en_miley_cyrus_flowers",
        "language": "ingilizce",
        "language_code": "EN",
        "language_tr": "İngilizce",
        "flag": "🇬🇧",
        "artist": "Miley Cyrus",
        "title": "Flowers",
        "release_year": "2023",
        "itunes_query": "Miley Cyrus Flowers",
        "artwork_url": "",
        "chorus_timestamp": "0:40 - 1:07 (Özgürlük Nakaratı)",
        "social_audio_search": "Miley Cyrus - Flowers",
        "cover_kicker": "🇬🇧 İNGİLİZCE ÖZGÜVEN MARŞI • TÜRKÇE ÇEVİRİ",
        "cover_headline": "'BENİ SENİN SEVDİĞİNDEN ÇOK DAHA GÜZEL SEVEBİLİRİM'",
        "viral_hook": "Miley Cyrus'a Grammy kazandıran 'Flowers', bir ayrılıktan sonra insanın kendi değerini fark edip kendi ayakları üzerinde çiçek açmasını anlatır.",
        "stanzas": [
            {
                "orig": "I can buy myself flowers, write my name in the sand",
                "pron": "Ay ken bay mayself flavırz, rayt may neym in dı send",
                "tr": "Kendi çiçeklerimi kendim alabilirim; kumsala kendi adımı gururla yazabilirim.",
                "highlight": "Kendi çiçeklerimi kendim alabilirim",
                "note": "Mutluluğu başkasında aramaktan vazgeçiş.",
            },
            {
                "orig": "I can take myself dancing, and I can hold my own hand",
                "pron": "Ay ken teyk mayself densing, end ay ken hold may ovn hend",
                "tr": "Kendimi dansa çıkarabilir ve en zor anımda kendi elimi kendim tutabilirim.",
                "highlight": "kendi elimi kendim tutabilirim",
                "note": "İçsel güç ve öz yeterlilik.",
            },
            {
                "orig": "Yeah, I can love me better than you can",
                "pron": "Ye, ay ken lav mi betır den yu ken",
                "tr": "Evet, ben kendimi senin beni sevebileceğinden çok daha güzel sevebilirim.",
                "highlight": "çok daha güzel sevebilirim",
                "note": "Şarkının ikonik vurucu dizesi.",
            },
        ],
    },
    {
        "id": "en_benson_boone_beautiful_things",
        "language": "ingilizce",
        "language_code": "EN",
        "language_tr": "İngilizce",
        "flag": "🇬🇧",
        "artist": "Benson Boone",
        "title": "Beautiful Things",
        "release_year": "2024",
        "itunes_query": "Benson Boone Beautiful Things",
        "artwork_url": "",
        "chorus_timestamp": "0:50 - 1:17 (Çığlık Zirvesi Nakarat)",
        "social_audio_search": "Benson Boone - Beautiful Things",
        "cover_kicker": "🇬🇧 İNGİLİZCE VİRAL ZİRVE • TÜRKÇE ÇEVİRİ",
        "cover_headline": "MUTLUYKEN BİLE KAYBETME KORKUSU YAŞAYANLARIN ŞARKISI",
        "viral_hook": "Benson Boone'un sosyal medyayı kasıp kavuran 'Beautiful Things' şarkısı, insanın hayatında her şey yolundayken bile sevdiklerini kaybetme korkusunu haykırır.",
        "stanzas": [
            {
                "orig": "Please stay, I want you, I need you, oh God",
                "pron": "Pliz stey, ay vont yu, ay nid yu, o gad",
                "tr": "Lütfen yanımda kal; sana ihtiyacım var, seni her şeyden çok istiyorum Tanrım.",
                "highlight": "Lütfen yanımda kal",
                "note": "Vokalin zirveye çıktığı yakarış anı.",
            },
            {
                "orig": "Don't take these beautiful things that I've got",
                "pron": "Dont teyk diz biyutiful tingz det ayv gat",
                "tr": "Ne olur elimdeki bu güzel duyguları ve sevdiğim insanı benden geri alma.",
                "highlight": "bu güzel duyguları ve sevdiğim insanı",
                "note": "Kaybetme korkusunun en saf hali.",
            },
        ],
    },
    # --- YENİ ARAPÇA HİTLER ---
    {
        "id": "ar_elissa_aa_bali_habibi",
        "language": "arapca",
        "language_code": "AR",
        "language_tr": "Arapça",
        "flag": "🇸🇦",
        "artist": "Elissa (إليسا)",
        "title": "Aa Bali Habibi (ع بالي حبيبي)",
        "release_year": "2009",
        "itunes_query": "Elissa Aa Bali Habibi",
        "artwork_url": "",
        "chorus_timestamp": "1:02 - 1:29 (Duygusal Nakarat)",
        "social_audio_search": "Elissa - Aa Bali Habibi",
        "cover_kicker": "🇸🇦 ARAPÇA ROMANTİK EFSANE • TÜRKÇE ÇEVİRİ",
        "cover_headline": "ARAP DÜNYASININ EN UNUTULMAZ AŞK İTİRAFI: 'AA BALI HABIBI'",
        "viral_hook": "Elissa'nın başyapıtı 'Aa Bali Habibi', bir insanın sevdiğiyle tüm ömrünü birleştirme hayalini ve kalbindeki en mahrem dilekleri anlatır.",
        "stanzas": [
            {
                "orig": "ع بالي حبيبي، ع بالي حبيبي",
                "pron": "A bali habibi, a bali habibi",
                "tr": "Aklımdasın sevgilim; tüm hayallerimin ve dualarımın tam merkezindesin.",
                "highlight": "hayallerimin ve dualarımın tam merkezindesin",
                "note": "Şarkının kalplere kazınan açılışı.",
            },
            {
                "orig": "أغمرك ما أتركك، أسرقك ما أرجعك",
                "pron": "Ağmurak ma etrukak, esrıkak ma erciak",
                "tr": "Sana öyle bir sarılayım ki hiç bırakmayayım; seni bu dünyadan çalıp bir daha kimseye geri vermeyeyim.",
                "highlight": "seni bu dünyadan çalıp",
                "note": "Tutkulu Arap şiirselliğinin zirvesi.",
            },
            {
                "orig": "أحبسك ما أطلعك من قلبي ولا يوم",
                "pron": "Ahbisak ma atlaak min kalbi vela yevm",
                "tr": "Seni kalbimin en derin köşesine saklayayım ve oradan tek bir gün bile çıkarmayayım.",
                "highlight": "kalbimin en derin köşesine saklayayım",
                "note": "Sonsuz bağlılık yemini.",
            },
        ],
    },
    {
        "id": "ar_saad_lamjarred_lm3allem",
        "language": "arapca",
        "language_code": "AR",
        "language_tr": "Arapça",
        "flag": "🇸🇦",
        "artist": "Saad Lamjarred (سعد لمجرد)",
        "title": "Lm3allem (المعلم)",
        "release_year": "2015",
        "itunes_query": "Saad Lamjarred Lm3allem",
        "artwork_url": "",
        "chorus_timestamp": "0:35 - 1:02 (Enerjik Nakarat)",
        "social_audio_search": "Saad Lamjarred - Lm3allem",
        "cover_kicker": "🇸🇦 ARAPÇA MİLYARLIK REKOR • TÜRKÇE ÇEVİRİ",
        "cover_headline": "1 MİLYAR İZLENMEYİ AŞAN İLK ARAPÇA ŞARKININ GERÇEK ANLAMI",
        "viral_hook": "Saad Lamjarred'in Guinness rekoru kıran 'Lm3allem' şarkısı, gülüşüyle ve duruşuyla herkesi kendine hayran bırakan karizmatik bir aşkı anlatır.",
        "stanzas": [
            {
                "orig": "انت معلم واحنا منك نتعلم",
                "pron": "Enta muallem ve ihna minnak netallem",
                "tr": "Sen aşkın ve zarafetin gerçek ustasısın; biz sevmeyi senden öğreniyoruz.",
                "highlight": "biz sevmeyi senden öğreniyoruz",
                "note": "Milyonların ezbere bildiği ikonik nakarat.",
            },
            {
                "orig": "نسكت وانت موجود ما نرضى نتكلم",
                "pron": "Neskut ve enta mevcud ma nerda netkellem",
                "tr": "Sen bir ortama girdiğinde hepimiz susarız; senin varlığının yanında tek kelime etmeye kıyamayız.",
                "highlight": "senin varlığının yanında",
                "note": "Hayranlık ve büyülenme ifadesi.",
            },
        ],
    },
    {
        "id": "ar_hussain_al_jassmi_bel_bont_el_areed",
        "language": "arapca",
        "language_code": "AR",
        "language_tr": "Arapça",
        "flag": "🇸🇦",
        "artist": "Hussain Al Jassmi (حسين الجسمي)",
        "title": "Bel Bont El Areed (بالبنط العريض)",
        "release_year": "2020",
        "itunes_query": "Hussain Al Jassmi Bel Bont El Areed",
        "artwork_url": "",
        "chorus_timestamp": "0:32 - 0:59 (Ritim & Manşet Nakarat)",
        "social_audio_search": "Hussain Al Jassmi - Bel Bont El Areed",
        "cover_kicker": "🇸🇦 ARAPÇA VİRAL HİT • TÜRKÇE ÇEVİRİ",
        "cover_headline": "'KALBİMİN MANŞETİNE BÜYÜK HARFLERLE ADINI YAZDIM'",
        "viral_hook": "Hussain Al Jassmi'nin sosyal medyada fırtınalar estiren 'Bel Bont El Areed' şarkısı, gizlenemeyen büyük bir aşkı manşetlere taşıyan neşeli bir itiraftır.",
        "stanzas": [
            {
                "orig": "حبيبي بالبنط العريض، غالي وأقرب م الوريد",
                "pron": "Habibi bil bont el arid, ğali ve akrab mil verid",
                "tr": "Sevgilim, büyük puntolarla ilan ediyorum: Sen benim için çok değerlisin ve bana şah damarımdan daha yakınsın.",
                "highlight": "bana şah damarımdan daha yakınsın",
                "note": "Arap edebiyatının en güçlü yakınlık metaforu.",
            },
            {
                "orig": "لقيت في قربك كل ما يسر النظر",
                "pron": "Lakayt fi kurbak kul ma yesurr en-nazar",
                "tr": "Senin yanı başında, gözlerimi ve ruhumu mutlu eden her şeyi eksiksiz buldum.",
                "highlight": "ruhumu mutlu eden her şeyi",
                "note": "Huzur ve tamamlanmışlık hissi.",
            },
        ],
    },
    # --- YENİ FRANSIZCA HİTLER ---
    {
        "id": "fr_stromae_pomme_ma_meilleure_ennemie",
        "language": "fransizca",
        "language_code": "FR",
        "language_tr": "Fransızca",
        "flag": "🇫🇷",
        "artist": "Stromae & Pomme",
        "title": "Ma Meilleure Ennemie",
        "release_year": "2024",
        "itunes_query": "Stromae Pomme Ma Meilleure Ennemie",
        "artwork_url": "",
        "chorus_timestamp": "0:45 - 1:12 (Arcane Viral Nakarat)",
        "social_audio_search": "Stromae & Pomme - Ma Meilleure Ennemie",
        "cover_kicker": "🇫🇷 FRANSIZCA GLOBAL REKOR • TÜRKÇE ÇEVİRİ",
        "cover_headline": "'SEN BAŞIMA GELEN EN GÜZEL ŞEY VE EN BÜYÜK ACISIN'",
        "viral_hook": "Stromae ve Pomme'un rekorlar kıran 'Ma Meilleure Ennemie' düeti, hem vazgeçemediğimiz en yakın dostumuz hem de kalbimizi en çok yaralayan aşkları anlatır.",
        "stanzas": [
            {
                "orig": "T'es la meilleure chose qui m'est arrivée, mais aussi la pire chose qui m'est arrivée",
                "pron": "Te la meyör şoz ki me tarive, me osi la pir şoz ki me tarive",
                "tr": "Sen hayatımda başıma gelen en güzel mucizesin; ama aynı zamanda başıma gelen en büyük felaketsin.",
                "highlight": "başıma gelen en güzel mucizesin",
                "note": "İmkansız ve zıt kutuplu aşkların özeti.",
            },
            {
                "orig": "Mais ma meilleure ennemie c'est toi, fuis-moi, le pire c'est toi et moi",
                "pron": "Me ma meyör enmi se tua, füi mua, lö pir se tua e mua",
                "tr": "Benim en tatlı düşmanım sensin; benden uzaklaş, çünkü en tehlikelisi ikimizin yan yana gelmesi.",
                "highlight": "Benim en tatlı düşmanım sensin",
                "note": "Sosyal medyada milyonlarca kez paylaşılan nakarat.",
            },
        ],
    },
    {
        "id": "fr_edith_piaf_non_je_ne_regrette_rien",
        "language": "fransizca",
        "language_code": "FR",
        "language_tr": "Fransızca",
        "flag": "🇫🇷",
        "artist": "Édith Piaf",
        "title": "Non, je ne regrette rien",
        "release_year": "1960",
        "itunes_query": "Edith Piaf Non je ne regrette rien",
        "artwork_url": "",
        "chorus_timestamp": "0:30 - 0:57 (Ölümsüz Chanson Zirvesi)",
        "social_audio_search": "Édith Piaf - Non, je ne regrette rien",
        "cover_kicker": "🇫🇷 FRANSIZCA ÖLÜMSÜZ EFSANE • TÜRKÇE ÇEVİRİ",
        "cover_headline": "'HAYIR, HİÇBİR ŞEYDEN PİŞMAN DEĞİLİM, GEÇMİŞİ SÜPÜRDÜM!'",
        "viral_hook": "Édith Piaf'ın sinema ve müzik tarihine geçen 'Non, je ne regrette rien' başyapıtı, geçmişin tüm acılarını silip hayata sıfırdan başlama cesaretini anlatır.",
        "stanzas": [
            {
                "orig": "Non, rien de rien, non, je ne regrette rien",
                "pron": "Non, riyen dö riyen, non, jö nö rögret riyen",
                "tr": "Hayır, kesinlikle hiçbir şeyden; yaşadığım hiçbir acıdan ve mutluluktan pişman değilim.",
                "highlight": "hiçbir acıdan ve mutluluktan pişman değilim",
                "note": "Tarihin en güçlü meydan okuma dizelerinden biri.",
            },
            {
                "orig": "Balayés les amours, avec leurs trémolos, balayés pour toujours, je repars à zéro",
                "pron": "Baleye le zamur, avek lör tremolo, baleye pur tujur, jö röpar a zero",
                "tr": "Eski aşkları ve tüm o titrek hüzünleri sonsuza dek süpürüp attım; şimdi hayata sıfırdan başlıyorum.",
                "highlight": "şimdi hayata sıfırdan başlıyorum",
                "note": "Yeniden doğuş manifestosu.",
            },
        ],
    },
    {
        "id": "fr_gims_est_ce_que_tu_maimes",
        "language": "fransizca",
        "language_code": "FR",
        "language_tr": "Fransızca",
        "flag": "🇫🇷",
        "artist": "Gims",
        "title": "Est-ce que tu m'aimes ?",
        "release_year": "2015",
        "itunes_query": "Gims Est ce que tu m aimes",
        "artwork_url": "",
        "chorus_timestamp": "0:48 - 1:15 (Dev Nakarat)",
        "social_audio_search": "Gims - Est-ce que tu m'aimes",
        "cover_kicker": "🇫🇷 FRANSIZCA MODERN KLASİK • TÜRKÇE ÇEVİRİ",
        "cover_headline": "'SENİ SEVMEKTEN KENDİMİ KAYBETTİM: BENİ GERÇEKTEN SEVİYOR MUSUN?'",
        "viral_hook": "Gims'in güçlü vokaliyle devleşen 'Est-ce que tu m'aimes ?', bir ilişkide her şeyini veren insanın karşısındakinin sevgisinden duyduğu derin şüpheyi sorgular.",
        "stanzas": [
            {
                "orig": "J'avais trouvé le sens de la raison qui m'entraînait à chaque pas sur le devant",
                "pron": "Jave truve lö sans dö la rezon ki mantrene a şak pa sür lö dövan",
                "tr": "Attığım her adımda beni ileriye taşıyan yaşam sevincimi senin gözlerinde bulmuştum.",
                "highlight": "yaşam sevincimi senin gözlerinde bulmuştum",
                "note": "Aşkın insana verdiği yön duygusu.",
            },
            {
                "orig": "Je ne sais pas si je t'aime ou si je t'aime plus, j'suis perdu",
                "pron": "Jö nö se pa si jö tem u si jö tem plü, jüi perdü",
                "tr": "Seni hâlâ deli gibi seviyor muyum yoksa artık tükendim mi bilmiyorum; tamamen kayboldum.",
                "highlight": "yoksa artık tükendim mi bilmiyorum",
                "note": "Nakaratın duygusal kırılma noktası.",
            },
        ],
    },
    # --- YENİ RUSÇA HİTLER ---
    {
        "id": "ru_polina_gagarina_kukushka",
        "language": "rusca",
        "language_code": "RU",
        "language_tr": "Rusça",
        "flag": "🇷🇺",
        "artist": "Polina Gagarina",
        "title": "Кукушка (Kukushka)",
        "release_year": "2015",
        "itunes_query": "Polina Gagarina Kukushka",
        "artwork_url": "",
        "chorus_timestamp": "0:55 - 1:22 (Sarsıcı Vokal Zirvesi)",
        "social_audio_search": "Polina Gagarina - Kukushka",
        "cover_kicker": "🇷🇺 RUSÇA EFSANE BAŞYAPIT • TÜRKÇE ÇEVİRİ",
        "cover_headline": "TÜYLERİ DİKEN DİKEN EDEN RUSÇA ŞARKI: 'KADERİMİ SÖYLE GUGUK KUŞU'",
        "viral_hook": "Viktor Tsoi'un efsanevi şiirini Polina Gagarina'nın dev vokaliyle buluşturan 'Kukushka', insanın kaderle, yalnızlıkla ve iradeyle mücadelesini anlatır.",
        "stanzas": [
            {
                "orig": "Солнце моё — взгляни на меня, моя ладонь превратилась в кулак",
                "pron": "Solntse moyo — vzglyani na menya, moya ladon prevratilas v kulak",
                "tr": "Benim güneşim, dön de bir bak bana; açık avucum artık savaşmaya hazır sıkılı bir yumruğa dönüştü.",
                "highlight": "sıkılı bir yumruğa dönüştü",
                "note": "Zorluklara karşı direnişin simgesi.",
            },
            {
                "orig": "И если есть порох — дай огня, вот так",
                "pron": "İ yesli yest poroh — day ognya, vot tak",
                "tr": "Eğer içimizde hâlâ bir kıvılcım ve barut kaldıysa, ateşle gitsin; işte tam böyle!",
                "highlight": "ateşle gitsin; işte tam böyle",
                "note": "Patlayıcı vokal zirvesi.",
            },
        ],
    },
    {
        "id": "ru_hammali_navai_ptichka",
        "language": "rusca",
        "language_code": "RU",
        "language_tr": "Rusça",
        "flag": "🇷🇺",
        "artist": "HammAli & Navai",
        "title": "Птичка (Ptichka)",
        "release_year": "2021",
        "itunes_query": "HammAli Navai Ptichka",
        "artwork_url": "",
        "chorus_timestamp": "0:40 - 1:07 (Melankolik Nakarat)",
        "social_audio_search": "HammAli & Navai - Ptichka",
        "cover_kicker": "🇷🇺 RUSÇA VİRAL HİT • TÜRKÇE ÇEVİRİ",
        "cover_headline": "'UÇUP GİTTİN KÜÇÜK KUŞUM AMA KALBİN HÂLÂ BENDE KALDI'",
        "viral_hook": "HammAli & Navai'nin duygusal başyapıtı 'Ptichka', gurur yüzünden biten ama iki tarafın da geceleri gizlice ağladığı yarım kalmış bir aşkı anlatır.",
        "stanzas": [
            {
                "orig": "Ты же не спишь опять, сидишь тут до утра",
                "pron": "Tı je ne spiş opyat, sidiş tut do utra",
                "tr": "Yine gözüne uyku girmiyor değil mi; sabaha kadar pencerenin önünde oturup düşünüyorsun.",
                "highlight": "sabaha kadar pencerenin önünde",
                "note": "Ayrılık sonrası uykusuz geceler.",
            },
            {
                "orig": "Улетела птичка, оставив пустое гнездо",
                "pron": "Uletela ptiçka, ostaviv pustoye gnezdo",
                "tr": "Küçük kuşum uçup gitti ve ardında sadece buz gibi, bomboş bir yuva bıraktı.",
                "highlight": "bomboş bir yuva bıraktı",
                "note": "Şarkıya adını veren hüzünlü metafor.",
            },
        ],
    },
    # --- YENİ İSPANYOLCA HİTLER ---
    {
        "id": "es_rosalia_despecha",
        "language": "ispanyolca",
        "language_code": "ES",
        "language_tr": "İspanyolca",
        "flag": "🇪🇸",
        "artist": "Rosalía",
        "title": "DESPECHÁ",
        "release_year": "2022",
        "itunes_query": "Rosalia Despecha",
        "artwork_url": "",
        "chorus_timestamp": "0:35 - 1:02 (Dans & Ritmik Nakarat)",
        "social_audio_search": "Rosalía - DESPECHÁ",
        "cover_kicker": "🇪🇸 İSPANYOLCA VİRAL HİT • TÜRKÇE ÇEVİRİ",
        "cover_headline": "'ARTIK BENİ ARAMA, BANA YAŞATTIĞIN KIRGINLIKLARI UNUTTUM!'",
        "viral_hook": "Rosalía'nın yaz hiti 'DESPECHÁ', kalp kırıklığını hüzünle değil dans ederek, eğlenerek ve geçmişi tamamen silerek atlatmanın enerjisini taşır.",
        "stanzas": [
            {
                "orig": "Baby, no me llames, que yo estoy ocupá' olvidando tus males",
                "pron": "Beybi, no me yames, ke yo estoy okupa olvidando tus males",
                "tr": "Artık beni sakın arama; çünkü bana yaşattığın tüm kırgınlıkları unutmakla meşgulüm.",
                "highlight": "kırgınlıkları unutmakla meşgulüm",
                "note": "Eski sevgiliye en net kapı kapatma cümlesi.",
            },
            {
                "orig": "Ya decidí que esta noche se sale, con todas mis motomamis",
                "pron": "Ya desidi ke esta noçe se sale, kon todas mis motomamis",
                "tr": "Kararımı çoktan verdim; bu gece tüm kederi geride bırakıp dostlarımla hayata karışıyorum.",
                "highlight": "tüm kederi geride bırakıp",
                "note": "Özgürlük ve neşe vurgusu.",
            },
        ],
    },
    {
        "id": "es_karol_g_shakira_tqg",
        "language": "ispanyolca",
        "language_code": "ES",
        "language_tr": "İspanyolca",
        "flag": "🇪🇸",
        "artist": "Karol G & Shakira",
        "title": "TQG (Te Quedó Grande)",
        "release_year": "2023",
        "itunes_query": "Karol G Shakira TQG",
        "artwork_url": "",
        "chorus_timestamp": "0:48 - 1:15 (İkonik Düet Nakarat)",
        "social_audio_search": "Karol G & Shakira - TQG",
        "cover_kicker": "🇪🇸 İSPANYOLCA DEV DÜET • TÜRKÇE ÇEVİRİ",
        "cover_headline": "TQG NE DEMEK? 'BENİM SEVGİM SANA FAZLA BÜYÜK GELDİ!'",
        "viral_hook": "Karol G ve Shakira'nın tarihi düeti 'TQG (Te Quedó Grande)', kıymet bilmeyen birinin ardından çok daha güçlü ve parlak bir hayata geçişi anlatır.",
        "stanzas": [
            {
                "orig": "Verte con la nueva me dolió, pero ya estoy puesta pa' lo mío",
                "pron": "Verte kon la nueva me dolyo, pero ya estoy puesta pa lo mio",
                "tr": "Seni yeni biriyle görmek ilk başta canımı yaktı; ama artık tamamen kendi hayatıma ve zaferime odaklandım.",
                "highlight": "kendi hayatıma ve zaferime odaklandım",
                "note": "Samimi itiraf ve güçlü dönüş.",
            },
            {
                "orig": "Lo que vivimos se me olvidó, y eso es lo que te tiene ofendido",
                "pron": "Lo ke vivimos se me olvido, i eso es lo ke te tiyene ofendido",
                "tr": "Yaşadığımız her şeyi çoktan unuttum gitti; senin asıl zoruna giden şey de tam olarak bu.",
                "highlight": "senin asıl zoruna giden şey de tam olarak bu",
                "note": "Nakaratın en keskin cümlesi.",
            },
        ],
    },
    # --- YENİ KORECE HİTLER ---
    {
        "id": "ko_jung_kook_seven",
        "language": "korece",
        "language_code": "KO",
        "language_tr": "Korece",
        "flag": "🇰🇷",
        "artist": "Jung Kook (정국)",
        "title": "Seven",
        "release_year": "2023",
        "itunes_query": "Jung Kook Seven",
        "artwork_url": "",
        "chorus_timestamp": "0:42 - 1:09 (Haftanın 7 Günü Nakaratı)",
        "social_audio_search": "Jung Kook - Seven",
        "cover_kicker": "🇰🇷 KORECE / GLOBAL REKOR HİT • TÜRKÇE ÇEVİRİ",
        "cover_headline": "'HAFTANIN YEDİ GÜNÜ, GÜNÜN HER SAATİ SENİ SEVECEĞİM'",
        "viral_hook": "BTS üyesi Jung Kook'un Spotify tarihinde en hızlı 1 milyar dinlenmeye ulaşan 'Seven' şarkısı, zamanın her anını sevdiği insana adama sözüdür.",
        "stanzas": [
            {
                "orig": "Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday",
                "pron": "Mandey, Tuzdey, Venzdey, Törzdey, Fraydey, Satırdey, Sandey",
                "tr": "Pazartesi, Salı, Çarşamba, Perşembe, Cuma, Cumartesi ve Pazar; haftanın her bir günü...",
                "highlight": "haftanın her bir günü",
                "note": "Akıldan çıkmayan ritmik nakarat.",
            },
            {
                "orig": "Seven days a week, every hour, every minute, every second",
                "pron": "Sevın deyz e vik, evri auır, evri minit, evri sekınd",
                "tr": "Haftanın yedi günü; her saat, her dakika ve her saniye kalbim yalnızca seninle atıyor.",
                "highlight": "kalbim yalnızca seninle atıyor",
                "note": "Kesintisiz bağlılık vurgusu.",
            },
        ],
    },
    {
        "id": "ko_fifty_fifty_cupid",
        "language": "korece",
        "language_code": "KO",
        "language_tr": "Korece",
        "flag": "🇰🇷",
        "artist": "FIFTY FIFTY",
        "title": "Cupid",
        "release_year": "2023",
        "itunes_query": "FIFTY FIFTY Cupid",
        "artwork_url": "",
        "chorus_timestamp": "0:38 - 1:05 (Viral Nakarat)",
        "social_audio_search": "FIFTY FIFTY - Cupid",
        "cover_kicker": "🇰🇷 KORECE VİRAL FENOMEN • TÜRKÇE ÇEVİRİ",
        "cover_headline": "'AŞK TANRISI CUPID'E İKİNCİ BİR ŞANS VERDİM AMA YİNE YALNIZIM'",
        "viral_hook": "Reels ve TikTok'ta milyarlarca videoya fon olan 'Cupid', aşka tekrar inanmak isteyen ama hayal kırıklığından korkan tatlı bir serzeniştir.",
        "stanzas": [
            {
                "orig": "I gave a second chance to Cupid, but now I'm left here feeling stupid",
                "pron": "Ay geyv e sekınd çens tu Kyupid, bat nav aym left hir filing stupid",
                "tr": "Aşka ve kaderime ikinci bir şans verdim; ama şimdi yine tek başıma hayal kırıklığıyla kaldım.",
                "highlight": "ikinci bir şans verdim",
                "note": "Dünyanın ezbere söylediği viral dize.",
            },
            {
                "orig": "Oh, the way he makes me feel that love isn't real, Cupid is so dumb",
                "pron": "O, dı vey hi meyks mi fil det lav izınt riyıl, Kyupid iz so dam",
                "tr": "Bana gerçek aşkın bir masal olduğunu hissettiriyor; aşk meleği bazen gerçekten çok acımasız.",
                "highlight": "gerçek aşkın bir masal olduğunu",
                "note": "Tatlı-hüzünlü nakarat kapanışı.",
            },
        ],
    },
    # --- YENİ JAPONCA HİTLER ---
    {
        "id": "ja_yoasobi_idol",
        "language": "japonca",
        "language_code": "JA",
        "language_tr": "Japonca",
        "flag": "🇯🇵",
        "artist": "YOASOBI",
        "title": "アイドル (Idol)",
        "release_year": "2023",
        "itunes_query": "YOASOBI Idol",
        "artwork_url": "",
        "chorus_timestamp": "0:45 - 1:12 (Rekor Kıran Nakarat)",
        "social_audio_search": "YOASOBI - Idol",
        "cover_kicker": "🇯🇵 JAPONCA GLOBAL ZİRVE • TÜRKÇE ÇEVİRİ",
        "cover_headline": "KUSURSUZ GÖRÜNÜMÜN ARKASINDAKİ YALNIZLIK: YOASOBI - IDOL",
        "viral_hook": "Billboard Global listesinde 1 numaraya yerleşen ilk Japonca şarkı olan 'Idol', sahnede herkesin hayran olduğu kusursuz bir yıldızın gerçek sevgiyi arayışını anlatır.",
        "stanzas": [
            {
                "orig": "誰もが目を奪われていく、君は完璧で究極のアイドル",
                "pron": "Daremo ga me o ubavarete iku, kimi va kanpeki de kyukyoku no aydoru",
                "tr": "Seni gören herkesin nefesi kesiliyor; sen göz kamaştıran, kusursuz ve eşsiz bir yıldızsın.",
                "highlight": "kusursuz ve eşsiz bir yıldızsın",
                "note": "Işıltılı sahne imajı.",
            },
            {
                "orig": "いつかきっと全部手に入れる、私はそう欲張りなアイドル",
                "pron": "İtsuka kitto zenbu te ni ireru, vataşi va so yokubari na aydoru",
                "tr": "Bir gün mutlaka gerçek sevgiyi de kalbimde hissedeceğim; tüm sırlarımla parlamaya devam ediyorum.",
                "highlight": "gerçek sevgiyi de kalbimde hissedeceğim",
                "note": "Maskenin ardındaki insani dilek.",
            },
        ],
    },
    {
        "id": "ja_lisa_gurenge",
        "language": "japonca",
        "language_code": "JA",
        "language_tr": "Japonca",
        "flag": "🇯🇵",
        "artist": "LiSA",
        "title": "紅蓮華 (Gurenge)",
        "release_year": "2019",
        "itunes_query": "LiSA Gurenge",
        "artwork_url": "",
        "chorus_timestamp": "0:50 - 1:17 (Güçlü Rock Nakarat)",
        "social_audio_search": "LiSA - Gurenge",
        "cover_kicker": "🇯🇵 JAPONCA EFSANE MARŞ • TÜRKÇE ÇEVİRİ",
        "cover_headline": "'GÜÇLÜ OLMAK İSTİYORUM ÇÜNKÜ KORUMAM GEREKEN BİRİ VAR!'",
        "viral_hook": "Japon müziğinin modern efsanesi 'Gurenge (Kızıl Nilüfer)', çamurun ve acının içinden filizlenip sevdiklerini korumak için ayağa kalkanların marşıdır.",
        "stanzas": [
            {
                "orig": "強くなれる理由を知った、僕を連れて進め",
                "pron": "Tsuyoku nareru riyu o şitta, boku o tsurete susume",
                "tr": "Artık neden daha güçlü olmam gerektiğini çok iyi biliyorum; elimden tut ve karanlığın içinden ilerleyelim.",
                "highlight": "neden daha güçlü olmam gerektiğini",
                "note": "Milyonlara ilham veren açılış dizesi.",
            },
            {
                "orig": "守りたいものがあるから、紅蓮の華よ咲き誇れ",
                "pron": "Mamoritai mono ga aru kara, guren no hana yo sakihokore",
                "tr": "Hayatta korumam gereken değerli kalpler var; şimdi fırtınalara inat gururla çiçek aç kızıl nilüfer!",
                "highlight": "fırtınalara inat gururla çiçek aç",
                "note": "Sarsıcı nakarat zirvesi.",
            },
        ],
    },
    # --- YENİ İTALYANCA HİTLER ---
    {
        "id": "it_maneskin_zitti_e_buoni",
        "language": "italyanca",
        "language_code": "IT",
        "language_tr": "İtalyanca",
        "flag": "🇮🇹",
        "artist": "Måneskin",
        "title": "Zitti e buoni",
        "release_year": "2021",
        "itunes_query": "Maneskin Zitti e buoni",
        "artwork_url": "",
        "chorus_timestamp": "0:48 - 1:15 (Eurovision Şampiyonu Nakarat)",
        "social_audio_search": "Måneskin - Zitti e buoni",
        "cover_kicker": "🇮🇹 İTALYANCA ROCK ZAFERİ • TÜRKÇE ÇEVİRİ",
        "cover_headline": "'İNSANLAR HİÇ BİLMEDİKLERİ HAYATLAR HAKKINDA KONUŞUP DURUYOR'",
        "viral_hook": "Måneskin'i dünya zirvesine taşıyan 'Zitti e buoni', toplumun kalıplarına sığmayan özgür ruhların ön yargılara karşı başkaldırısıdır.",
        "stanzas": [
            {
                "orig": "Siamo fuori di testa, ma diversi da loro",
                "pron": "Siyamo fuori di testa, ma diversi da loro",
                "tr": "Belki biraz çılgınız ve kurallara uymuyoruz; ama sahte maskeler takan onlardan tamamen farklıyız.",
                "highlight": "onlardan tamamen farklıyız",
                "note": "Özgünlük ve cesaret manifestosu.",
            },
            {
                "orig": "Parla, la gente purtroppo parla, non sa di che cosa parla",
                "pron": "Parla, la cente purtroppo parla, non sa di ke koza parla",
                "tr": "İnsanlar ne yazık ki durmadan konuşuyor; üstelik hakkında hiçbir şey bilmedikleri hayatları yargılıyorlar.",
                "highlight": "hiçbir şey bilmedikleri hayatları yargılıyorlar",
                "note": "Nakaratın en vurucu toplumsal eleştirisi.",
            },
        ],
    },
    {
        "id": "it_mahmood_soldi",
        "language": "italyanca",
        "language_code": "IT",
        "language_tr": "İtalyanca",
        "flag": "🇮🇹",
        "artist": "Mahmood",
        "title": "Soldi",
        "release_year": "2019",
        "itunes_query": "Mahmood Soldi",
        "artwork_url": "",
        "chorus_timestamp": "0:42 - 1:09 (Alkışlı İkonik Nakarat)",
        "social_audio_search": "Mahmood - Soldi",
        "cover_kicker": "🇮🇹 İTALYANCA MODERN KLASİK • TÜRKÇE ÇEVİRİ",
        "cover_headline": "'SANIRSIN Kİ SADECE PARAYI DÜŞÜNÜYOR AMA KALBİ BOMBOŞ'",
        "viral_hook": "Sanremo şampiyonu Mahmood'un 'Soldi' şarkısı, maddiyatı sevginin önüne koyan bir babanın çocukta bıraktığı duygusal izleri anlatır.",
        "stanzas": [
            {
                "orig": "volevi solo soldi, soldi, come se avessi avuto soldi, soldi",
                "pron": "Volevi solo soldi, soldi, kome se avessi avuto soldi, soldi",
                "tr": "Benden sevgi değil, sadece para ve güç istedin; sanki para kırılan bir kalbi onarabilirmiş gibi.",
                "highlight": "sanki para kırılan bir kalbi onarabilirmiş gibi",
                "note": "Şarkının kalbine inen nakarat.",
            },
            {
                "orig": "Dimmi se ti manco o te ne fotti, mi chiedevi come va, come va, come va",
                "pron": "Dimmi se ti manko o te ne fotti, mi kiyedevi kome va, kome va, kome va",
                "tr": "Doğruyu söyle, beni gerçekten özlüyor musun yoksa umurunda bile değil miyim? Sadece adetten 'nasılsın' diye soruyorsun.",
                "highlight": "beni gerçekten özlüyor musun",
                "note": "Yüzeysel ilişkilere sitem.",
            },
        ],
    },
    # --- YENİ ALMANCA HİTLER ---
    {
        "id": "de_cro_traum",
        "language": "almanca",
        "language_code": "DE",
        "language_tr": "Almanca",
        "flag": "🇩🇪",
        "artist": "Cro",
        "title": "Traum",
        "release_year": "2014",
        "itunes_query": "Cro Traum",
        "artwork_url": "",
        "chorus_timestamp": "0:40 - 1:07 (Ritim & Melodik Nakarat)",
        "social_audio_search": "Cro - Traum",
        "cover_kicker": "🇩🇪 ALMANCA POP KLASİĞİ • TÜRKÇE ÇEVİRİ",
        "cover_headline": "HENÜZ TANIŞMADIĞI RUH EŞİNİ ARAYANLARIN ŞARKISI: 'TRAUM'",
        "viral_hook": "Alman müziğinin en sevilen hitlerinden 'Traum', hayallerindeki o doğru insanla bir gün bir yerde mutlaka karşılaşacağına inananların şarkısıdır.",
        "stanzas": [
            {
                "orig": "Denn du bist, was ich суche, schon seit Jahren",
                "pron": "Den du bist, vas ih zuhe, şon zayt yaren",
                "tr": "Çünkü sen, yıllardır her yerde aradığım ama henüz adını bile bilmediğim o mucizesin.",
                "highlight": "yıllardır her yerde aradığım",
                "note": "Ruh eşine duyulan özlem.",
            },
            {
                "orig": "Hey, falls du dich erkennst, ruf mich an, sag mir, wo du bist",
                "pron": "Hey, fals du dih erkenst, ruf mih an, zag mir vo du bist",
                "tr": "Eğer bu sözlerde kendini buluyorsan lütfen bana ses ver ve dünyanın neresinde olduğunu söyle.",
                "highlight": "bu sözlerde kendini buluyorsan",
                "note": "Samimi ve sıcak çağrı.",
            },
        ],
    },
    {
        "id": "de_ayliva_haesslich",
        "language": "almanca",
        "language_code": "DE",
        "language_tr": "Almanca",
        "flag": "🇩🇪",
        "artist": "AYLIVA",
        "title": "Hässlich",
        "release_year": "2023",
        "itunes_query": "AYLIVA Haesslich",
        "artwork_url": "",
        "chorus_timestamp": "0:45 - 1:12 (Duygusal Zirve Nakarat)",
        "social_audio_search": "AYLIVA - Hässlich",
        "cover_kicker": "🇩🇪 ALMANCA VİRAL HİT • TÜRKÇE ÇEVİRİ",
        "cover_headline": "'DIŞIN NE KADAR GÜZELSE KALBİN VE YALANLARIN O KADAR ÇİRKİN'",
        "viral_hook": "Almanya listelerini domine eden AYLIVA'nın 'Hässlich' şarkısı, güzel sözlerin arkasına saklanan ihaneti fark eden bir kadının güçlü yüzleşmesini anlatır.",
        "stanzas": [
            {
                "orig": "Du bist so hässlich, so hässlich von innen, ich kann es kaum fassen",
                "pron": "Du bist zo heslıh, zo heslıh fon innen, ih kan es kaum fassen",
                "tr": "Ruhun ve kalbinin içi o kadar karanlık ki; sana nasıl bu kadar safça inandığıma hâlâ inanamıyorum.",
                "highlight": "sana nasıl bu kadar safça inandığıma",
                "note": "Hayal kırıklığının uyanışa dönüştüğü an.",
            },
            {
                "orig": "Wie konnte ich dich nur so sehr lieben?",
                "pron": "Vi konte ih dih nur zo zer liben?",
                "tr": "Bana bunca acıyı yaşatırken seni nasıl kendimden bile çok sevebildim?",
                "highlight": "seni nasıl kendimden bile çok sevebildim",
                "note": "Nakaratın en sarsıcı sorusu.",
            },
        ],
    },
    # --- YENİ ÇİNCE HİTLER ---
    {
        "id": "zh_eric_chou_ni_hao_bu_hao",
        "language": "cince",
        "language_code": "ZH",
        "language_tr": "Çince",
        "flag": "🇨🇳",
        "artist": "Eric Chou (周兴哲)",
        "title": "你，好不好？ (Nǐ, Hǎo Bù Hǎo?)",
        "release_year": "2016",
        "itunes_query": "Eric Chou How Have You Been",
        "artwork_url": "",
        "chorus_timestamp": "1:00 - 1:27 (Piyano & Vokal Zirvesi)",
        "social_audio_search": "Eric Chou - How Have You Been",
        "cover_kicker": "🇨🇳 ÇİNCE DUYGUSAL BAŞYAPIT • TÜRKÇE ÇEVİRİ",
        "cover_headline": "'BENDEN SONRA GERÇEKTEN İYİ MİSİN?': MİLYONLARI AĞLATAN ÇİNCE ŞARKI",
        "viral_hook": "Eric Chou'nun Asya'da yüz milyonlarca kez dinlenen 'Nǐ, Hǎo Bù Hǎo?' baladı, ayrıldıktan sonra bile eski sevgilinin mutluluğunu uzaktan merak etmenin hüznünü anlatır.",
        "stanzas": [
            {
                "orig": "能不能继续，对我哭，对我笑，对我好",
                "pron": "Nıng bu nıng cışü, duey vo ku, duey vo şyao, duey vo hao",
                "tr": "Eskisi gibi yine benim omzumda ağlamaya, bana gülümsemeye ve yanımda kalmaya devam edemez misin?",
                "highlight": "benim omzumda ağlamaya",
                "note": "Geçmişin sıcaklığına duyulan özlem.",
            },
            {
                "orig": "别融化了眼泪，你，好不好？",
                "pron": "Biye rong hua lı yen ley, ni, hao bu hao?",
                "tr": "Gözyaşların sessizliğe karışıp kaybolmasın; söyle bana, benden uzakta gerçekten iyi misin?",
                "highlight": "benden uzakta gerçekten iyi misin",
                "note": "Şarkının kalbe dokunan ana sorusu.",
            },
        ],
    },
    {
        "id": "zh_gem_guang_nian_zhi_wai",
        "language": "cince",
        "language_code": "ZH",
        "language_tr": "Çince",
        "flag": "🇨🇳",
        "artist": "G.E.M. (邓紫棋)",
        "title": "光年之外 (Light Years Away)",
        "release_year": "2016",
        "itunes_query": "G.E.M. Light Years Away",
        "artwork_url": "",
        "chorus_timestamp": "0:52 - 1:19 (Sinematik Nakarat)",
        "social_audio_search": "G.E.M. - Light Years Away",
        "cover_kicker": "🇨🇳 ÇİNCE REKOR HİT • TÜRKÇE ÇEVİRİ",
        "cover_headline": "'IŞIK YILLARI ÖTEDE BİLE OLSAK KALBİM SENİN YÖRÜNGENDE'",
        "viral_hook": "Passengers filminin resmi müziği olan ve YouTube'da en çok izlenen Çince şarkı rekorunu kıran 'Light Years Away', mesafeleri ve zamanı aşan kader aşkını anlatır.",
        "stanzas": [
            {
                "orig": "缘分让我们相遇乱世以外，命运却要我们危难中相爱",
                "pron": "Yüen fın rang vo mın şyang yü luan şı yi vay, ming yün çüe yao vo mın vey nan cong şyang ay",
                "tr": "Kader bizi bu kaotik dünyanın ötesinde karşılaştırdı ve en imkansız fırtınaların ortasında birbirimize aşık etti.",
                "highlight": "en imkansız fırtınaların ortasında",
                "note": "Sinematik kader teması.",
            },
            {
                "orig": "也许未来遥远在光年之外，我愿守候未知里为你等待",
                "pron": "Ye şü vey lay yao yüen zay guang niyen cı vay, vo yüen şou hou vey cı li vey ni dıng day",
                "tr": "Gelecek bizden ışık yılları kadar uzakta olsa bile; bilinmezliğin içinde sonsuza dek seni beklemeye razıyım.",
                "highlight": "sonsuza dek seni beklemeye razıyım",
                "note": "Dev nakaratın duygusal zirvesi.",
            },
        ],
    },
    # --- YENİ HİNTÇE HİTLER ---
    {
        "id": "hi_jubin_nautiyal_raataan_lambiyan",
        "language": "hintce",
        "language_code": "HI",
        "language_tr": "Hintçe",
        "flag": "🇮🇳",
        "artist": "Jubin Nautiyal & Asees Kaur",
        "title": "Raataan Lambiyan (रातां लम्बियां)",
        "release_year": "2021",
        "itunes_query": "Jubin Nautiyal Raataan Lambiyan",
        "artwork_url": "",
        "chorus_timestamp": "0:38 - 1:05 (Romantik Bollywood Nakaratı)",
        "social_audio_search": "Jubin Nautiyal - Raataan Lambiyan",
        "cover_kicker": "🇮🇳 HİNTÇE ROMANTİK REKOR • TÜRKÇE ÇEVİRİ",
        "cover_headline": "'BU UZUN GECELERİ YALNIZCA SENİNLE KONUŞARAK GEÇİRMEK İSTİYORUM'",
        "viral_hook": "Milyarlarca kez dinlenen 'Raataan Lambiyan', aşık olduğu insanın gözlerine bakarak sabaha kadar sohbet etmenin verdiği saf mutluluğu anlatır.",
        "stanzas": [
            {
                "orig": "काटूँ कैसे रातां ओ साँवरे, जिया नहीं जाता सुन बावरे",
                "pron": "Katu keyse raatan o savre, ciya nahi cata sun bavre",
                "tr": "Sen yanımda olmadan bu upuzun geceleri nasıl geçireyim sevgilim; sensiz nefes bile alınmıyor.",
                "highlight": "sensiz nefes bile alınmıyor",
                "note": "Özlemin en içten ifadesi.",
            },
            {
                "orig": "के रातां लम्बियां लम्बियां रे, कटे तेरे संगियां संगियां रे",
                "pron": "Ke raatan lambiyan lambiyan re, kate tere sangiyan sangiyan re",
                "tr": "Geceler ne kadar uzun olursa olsun; yeter ki her bir dakikası senin yanı başında, seninle geçsin.",
                "highlight": "senin yanı başında, seninle geçsin",
                "note": "Milyonların ezbere bildiği ikonik nakarat.",
            },
        ],
    },
    {
        "id": "hi_arijit_singh_chaleya",
        "language": "hintce",
        "language_code": "HI",
        "language_tr": "Hintçe",
        "flag": "🇮🇳",
        "artist": "Arijit Singh & Shilpa Rao",
        "title": "Chaleya (चलेया)",
        "release_year": "2023",
        "itunes_query": "Arijit Singh Chaleya",
        "artwork_url": "",
        "chorus_timestamp": "0:42 - 1:09 (Modern Bollywood Hit Nakarat)",
        "social_audio_search": "Arijit Singh - Chaleya",
        "cover_kicker": "🇮🇳 HİNTÇE GLOBAL LİSTE HİTİ • TÜRKÇE ÇEVİRİ",
        "cover_headline": "'KALBİM KENDİ İRADESİNİ BIRAKTI, SADECE SENİN İZİNDEN YÜRÜYOR'",
        "viral_hook": "Jawan filminin dünya çapında viral olan şarkısı 'Chaleya', Arijit Singh'in büyüleyici sesiyle aşkın insanı nasıl pusulasız bırakıp peşinden sürüklediğini anlatır.",
        "stanzas": [
            {
                "orig": "इश्क़ में दिल बना है, इश्क़ में दिल फ़ना है",
                "pron": "İşk me dil bana he, işk me dil fana he",
                "tr": "Bu kalp senin aşkınla yeniden var oldu ve yine yalnızca senin aşkında eriyip kaybolmaya hazır.",
                "highlight": "senin aşkınla yeniden var oldu",
                "note": "Tasavvufi derinlik taşıyan romantik dize.",
            },
            {
                "orig": "तेरी ओर चलेया, हुआ मैं तेरा",
                "pron": "Teri or çaleya, hua me tera",
                "tr": "Ruhum sadece senin olduğun yöne doğru yürüyor; ben artık bütünüyle sana aidim.",
                "highlight": "bütünüyle sana aidim",
                "note": "Akıcı ve büyüleyici nakarat.",
            },
        ],
    },
]


def load_used_song_ids() -> List[str]:
    """Yerel + GitHub API Sıfır-Tekrar Çift Kilit defterini okur."""
    os.makedirs(LEDGER_PATH.parent, exist_ok=True)
    used: List[str] = []
    if LEDGER_PATH.exists():
        try:
            data = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
            for sid in (data.get("used_ids") or []):
                if sid not in used:
                    used.append(sid)
        except Exception:
            pass

    gh_token = os.environ.get("GH_TOKEN", "").strip()
    if gh_token:
        try:
            r = requests.get(
                f"https://api.github.com/repos/{GITHUB_REPO_SLUG}/contents/output/zero_repeat_ledger.json",
                headers={"Authorization": f"Bearer {gh_token}", "Accept": "application/vnd.github+json"},
                timeout=10,
            )
            if r.status_code == 200:
                content_b64 = r.json().get("content", "")
                remote_data = json.loads(base64.b64decode(content_b64).decode("utf-8"))
                for sid in (remote_data.get("used_ids") or []):
                    if sid not in used:
                        used.append(sid)
        except Exception:
            pass
    return used


def mark_song_used(song: Dict[str, Any], sync_github: bool = True) -> None:
    """Paylaşılan şarkıyı yerel ve GitHub Sıfır-Tekrar defterine atomik olarak yazar."""
    os.makedirs(LEDGER_PATH.parent, exist_ok=True)
    used = load_used_song_ids()
    sid = str(song.get("id", "")).strip()
    if sid and sid not in used:
        used.append(sid)

    payload_obj = {
        "updated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "total_used": len(used),
        "last_song_id": sid,
        "last_language": song.get("language", "ingilizce"),
        "used_ids": used,
    }
    raw_json = json.dumps(payload_obj, ensure_ascii=False, indent=2)
    LEDGER_PATH.write_text(raw_json, encoding="utf-8")

    gh_token = os.environ.get("GH_TOKEN", "").strip()
    if sync_github and gh_token:
        try:
            api_url = f"https://api.github.com/repos/{GITHUB_REPO_SLUG}/contents/output/zero_repeat_ledger.json"
            headers = {"Authorization": f"Bearer {gh_token}", "Accept": "application/vnd.github+json"}
            get_r = requests.get(api_url, headers=headers, timeout=10)
            put_body: Dict[str, Any] = {
                "message": f"chore(songtraibot): lock song {sid} in zero-repeat ledger [skip ci]",
                "content": base64.b64encode(raw_json.encode("utf-8")).decode("ascii"),
            }
            if get_r.status_code == 200 and get_r.json().get("sha"):
                put_body["sha"] = get_r.json()["sha"]
            requests.put(api_url, headers=headers, json=put_body, timeout=12)
        except Exception:
            pass


def normalize_language_key(raw_lang: str) -> str:
    cleaned = (raw_lang or "").strip().lower().lstrip("/")
    return LANGUAGE_ALIASES.get(cleaned, "otomatik")


def _translate_to_clean_turkish(text: str, src_lang_code: str = "auto") -> str:
    """
    Canlı kullanıcı şarkı isteklerinde satırları Türkçe'ye çevirir ve robotik ifadeleri
    doğal/şiirsel Türkçe akışına göre temizler.
    """
    clean_in = (text or "").strip()
    if not clean_in:
        return ""
    try:
        r = requests.get(
            "https://translate.googleapis.com/translate_a/single",
            params={
                "client": "gtx",
                "sl": src_lang_code.lower() if src_lang_code != "auto" else "auto",
                "tl": "tr",
                "dt": "t",
                "q": clean_in,
            },
            timeout=8,
        )
        if r.status_code == 200:
            arr = r.json()
            if isinstance(arr, list) and arr and isinstance(arr[0], list):
                out = "".join(seg[0] for seg in arr[0] if seg and seg[0]).strip()
                # Doğal Türkçe rötuşları
                out = out.replace("Bebeğim", "Sevgilim").replace("bebeğim", "sevgilim")
                out = re.sub(r"\s+", " ", out).strip()
                return out
    except Exception:
        pass
    return clean_in


EXTENDED_GLOBAL_HIT_QUERIES_BY_LANG: Dict[str, List[str]] = {
    "ingilizce": [
        "Taylor Swift Cruel Summer",
        "The Neighbourhood Sweater Weather",
        "Lord Huron The Night We Met",
        "Sabrina Carpenter Espresso",
        "Teddy Swims Lose Control",
        "Djo End of Beginning",
        "Rihanna Diamonds",
        "Adele Rolling in the Deep",
        "Bruno Mars Locked Out of Heaven",
        "OneRepublic Counting Stars",
        "Passenger Let Her Go",
        "John Legend All of Me",
        "Sam Smith Stay With Me",
        "Shawn Mendes Senorita",
        "Dua Lipa Levitating",
        "Post Malone Circles",
        "Linkin Park In the End",
        "Eminem Lose Yourself",
        "Vance Joy Riptide",
        "Glass Animals Heat Waves",
        "JVKE Golden Hour",
        "Stephen Sanchez Until I Found You",
        "Tate McRae Greedy",
        "Chappell Roan Good Luck Babe",
        "SZA Kill Bill",
    ],
    "arapca": [
        "Amr Diab Nour El Ain",
        "Fairuz Li Beirut",
        "Wael Kfoury El Bint El Awiye",
        "Assala Ghaban",
        "Tamer Hosny Come Back To Me",
        "Sherine Sabry Aalil",
        "Nassif Zeytoun Mich Aam Tezbat Maii",
        "Zuhair Bahaoui Decapotable",
        "kadim Al Sahir Zidini Ishqan",
        "Mohamed Hamaki Ya Sattar",
    ],
    "fransizca": [
        "Indila Love Story",
        "Stromae Alors on danse",
        "Zaz Je veux",
        "Aya Nakamura Djadja",
        "Indila Tourner dans le vide",
        "Lomepal Trop beau",
        "Videoclub Amour plastique",
        "Pomme Ceux qui revent",
        "Dadju Reine",
        "Lara Fabian Je t'aime",
    ],
    "rusca": [
        "Miyagi Andy Panda Kosandra",
        "JONY Alleia",
        "Rauf Faik Ya lyublyu tebya",
        "Xcho Ты и Я",
        "Basta Sansara",
        "Zivert Life",
        "Jah Khalib Medina",
        "Mot Kapkan",
        "MACAN Asphalt 8",
        "ANIVAR Lyubimiy chelovek",
    ],
    "ispanyolca": [
        "Bad Bunny Ojitos Lindos",
        "Luis Fonsi Despacito",
        "Enrique Iglesias Bailando",
        "Maluma Hawái",
        "Peso Pluma Ella Baila Sola",
        "Feid Classy 101",
        "Quevedo Bzrp Music Sessions 52",
        "Rauw Alejandro Todo De Ti",
        "J Balvin Mi Gente",
        "Camilo Vida de Rico",
    ],
    "korece": [
        "BTS Dynamite",
        "BLACKPINK How You Like That",
        "IVE I AM",
        "NewJeans Hype Boy",
        "Jimin Like Crazy",
        "LE SSERAFIM Smart",
        "Stray Kids God's Menu",
        "TWICE Feel Special",
        "aespa Supernova",
        "IU Love wins all",
    ],
    "japonca": [
        "YOASOBI Yoru ni Kakeru",
        "Kenshi Yonezu Kick Back",
        "Ado Usseewa",
        "Vaundy Odoriko",
        "Official HIGE DANdism Pretender",
        "King Gnu Specialz",
        "imase NIGHT DANCER",
        "Radwimps Sparkle",
        "Mrs. GREEN APPLE Que Sera Sera",
        "Eve Kaikai Kitan",
    ],
    "italyanca": [
        "Måneskin I Wanna Be Your Slave",
        "Annalisa Mon Amour",
        "Blanco Mi fai impazzire",
        "Ultimo Piccola stella",
        "Eros Ramazzotti Più bella cosa",
        "Tananai Tango",
        "Lazza Cenere",
        "Angelina Mango La noia",
        "Fedez Chiaroscuro",
        "Laura Pausini La solitudine",
    ],
    "almanca": [
        "Rammstein Sonne",
        "Peter Fox Zukunft Pink",
        "Apache 207 Roller",
        "RAF Camora 500 PS",
        "Nina Chuba Wildberry Lillet",
        "Pashanim Sommergewitter",
        "Bausa Was du Liebe nennst",
        "Mark Forster Chöre",
        "Lea Treppenhaus",
        "Sido Bilder im Kopf",
    ],
    "cince": [
        "Jay Chou Mojito",
        "JJ Lin Twilight",
        "Mayday Suddenly Missing You",
        "Mao Buyi People Like Me",
        "Ronghao Li Sparrow",
        "Faye Wong Red Bean",
        "LBI LBI跳楼机",
        "Cheng Xiang Maybe",
        "Eason Chan Ten Years",
        "Lay Zhang Lit",
    ],
    "hintce": [
        "Arijit Singh Apna Bana Le",
        "Atif Aslam Tera Hone Laga Hoon",
        "Shreya Ghoshal Teri Ore",
        "Pritam Kesariya",
        "Diljit Dosanjh Lover",
        "AR Rahman Kun Faya Kun",
        "Vishal Mishra Pehle Bhi Main",
        "Anuv Jain Husn",
        "Badshah Jugnu",
        "King Maan Meri Jaan",
    ],
}


def build_live_song_concept_from_query(
    query_text: str,
    forced_lang: str = "otomatik",
    requester_chat_id: str = "",
    skip_catalog_match: bool = False,
) -> Dict[str, Any]:
    """
    Kullanıcı Telegram'dan (@songtraibot) özel bir şarkı adı / sanatçı gönderdiğinde
    veya genişletilmiş global hit havuzundan yeni şarkı keşfedildiğinde:
    1) Önce küratörlü katalogda eşleşme var mı kontrol eder (`skip_catalog_match=False` ise).
    2) Yoksa iTunes Search API + LRCLIB API üzerinden gerçek şarkıyı, albüm kapağını ve nakarat sözlerini
       çekip tertemiz Türkçe çevirisiyle canlı olarak oluşturur.
    """
    q_low = (query_text or "").strip().lower()
    if not skip_catalog_match:
        for item in SONG_MASTER_CATALOG:
            if (
                item["title"].lower() in q_low
                or item["artist"].lower() in q_low
                or q_low in f"{item['artist']} {item['title']}".lower()
            ):
                cloned = json.loads(json.dumps(item))
                if requester_chat_id:
                    cloned["requester_chat_id"] = requester_chat_id
                return cloned

    # Canlı iTunes + LRCLIB araması
    artist_name = "Global Artist"
    track_title = query_text.strip() or "Popular Song"
    release_year = "2024"
    artwork_url = ""

    try:
        it_r = requests.get(
            "https://itunes.apple.com/search",
            params={"term": query_text, "entity": "song", "limit": 1},
            timeout=10,
        )
        if it_r.status_code == 200:
            results = it_r.json().get("results") or []
            if results:
                top = results[0]
                artist_name = top.get("artistName", artist_name)
                track_title = top.get("trackName", track_title)
                rel_date = top.get("releaseDate", "2024")
                release_year = rel_date[:4] if len(rel_date) >= 4 else "2024"
                art100 = top.get("artworkUrl100", "")
                if art100:
                    artwork_url = art100.replace("100x100bb", "1000x1000bb")
    except Exception:
        pass

    lang_key = normalize_language_key(forced_lang)
    if lang_key == "otomatik":
        lang_key = "ingilizce"
    lmeta = LANGUAGE_META.get(lang_key, LANGUAGE_META["ingilizce"])

    # LRCLIB üzerinden şarkı sözlerini çek
    raw_lines: List[str] = []
    try:
        lrc_r = requests.get(
            "https://lrclib.net/api/search",
            params={"q": f"{artist_name} {track_title}"},
            timeout=10,
        )
        if lrc_r.status_code == 200:
            items = lrc_r.json()
            if isinstance(items, list) and items:
                plain = items[0].get("plainLyrics") or ""
                for ln in plain.splitlines():
                    s_ln = ln.strip()
                    if len(s_ln) >= 14 and not s_ln.startswith("["):
                        if s_ln not in raw_lines:
                            raw_lines.append(s_ln)
    except Exception:
        pass

    selected_lines = raw_lines[2:6] if len(raw_lines) >= 6 else raw_lines[:4]
    while len(selected_lines) < 4:
        fallback_defaults = [
            f"Every time I hear '{track_title}', the memories come alive",
            "Even across the distance, your voice stays in my heart",
            "Words cannot describe the feeling hidden in this melody",
            "Stay with me tonight before the music fades away",
        ]
        selected_lines.append(fallback_defaults[len(selected_lines)])

    stanzas: List[Dict[str, str]] = []
    for idx, orig_ln in enumerate(selected_lines[:4], start=1):
        tr_ln = _translate_to_clean_turkish(orig_ln, src_lang_code=lmeta["code"])
        words = tr_ln.split()
        hl = " ".join(words[:3]) if len(words) >= 3 else tr_ln
        stanzas.append({
            "orig": orig_ln,
            "pron": orig_ln,
            "tr": tr_ln,
            "highlight": hl,
            "note": f"{artist_name} bu dizede şarkının duygusal kırılma noktasını vurguluyor.",
        })

    q_hash = hashlib.md5(q_low.encode("utf-8")).hexdigest()[:6]
    return {
        "id": f"custom_{lmeta['code'].lower()}_{q_hash}",
        "language": lang_key,
        "language_code": lmeta["code"],
        "language_tr": lmeta["name_tr"],
        "flag": lmeta["flag"],
        "artist": artist_name,
        "title": track_title,
        "release_year": release_year,
        "itunes_query": f"{artist_name} {track_title}",
        "artwork_url": artwork_url,
        "chorus_timestamp": "0:42 - 1:08 (Nakarat / En Vurucu Kısım)",
        "social_audio_search": f"{artist_name} - {track_title}",
        "cover_kicker": f"{lmeta['flag']} {lmeta['name_tr'].upper()} POPÜLER ŞARKI • TÜRKÇE ÇEVİRİ",
        "cover_headline": f"{artist_name.upper()} — {track_title.upper()} TÜRKÇE ANLAMI",
        "viral_hook": f"{artist_name} tarafından seslendirilen '{track_title}', melodisinin arkasında derin ve etkileyici bir hikaye taşıyor.",
        "stanzas": stanzas,
        "requester_chat_id": requester_chat_id,
    }


def _discover_unused_extended_hit(lang_key: str, used_ids: List[str]) -> Optional[Dict[str, Any]]:
    lmeta = LANGUAGE_META.get(lang_key, LANGUAGE_META["ingilizce"])
    for q in EXTENDED_GLOBAL_HIT_QUERIES_BY_LANG.get(lang_key, []):
        q_hash = hashlib.md5(q.strip().lower().encode("utf-8")).hexdigest()[:6]
        cand_id = f"custom_{lmeta['code'].lower()}_{q_hash}"
        if cand_id not in used_ids:
            return build_live_song_concept_from_query(q, forced_lang=lang_key, skip_catalog_match=True)
    return None


def select_next_song_concept(
    force_language: str = "otomatik",
    custom_song: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Sıfır-Tekrar Çift Kilit defterini kontrol ederek 11 dil arasında (%50 popüler İngilizce ağırlıklı)
    dengeli rotasyonla sıradaki YENİ popüler şarkıyı seçer.
    """
    if custom_song is not None:
        return custom_song

    used_ids = load_used_song_ids()
    norm_lang = normalize_language_key(force_language)

    if norm_lang != "otomatik":
        lang_unused = [s for s in SONG_MASTER_CATALOG if s["language"] == norm_lang and s["id"] not in used_ids]
        if lang_unused:
            return json.loads(json.dumps(lang_unused[0]))
        ext_hit = _discover_unused_extended_hit(norm_lang, used_ids)
        if ext_hit is not None:
            return ext_hit
        lang_all = [s for s in SONG_MASTER_CATALOG if s["language"] == norm_lang]
        if lang_all:
            return json.loads(json.dumps(lang_all[len(used_ids) % len(lang_all)]))

    # Otomatik modda İngilizce ağırlıklı (%50 popüler İngilizce + Arapça dahil 11 dil) rotasyon sırasını uygula
    start_idx = len(used_ids) % len(LANGUAGE_ROTATION_ORDER)
    for offset in range(len(LANGUAGE_ROTATION_ORDER)):
        target_l = LANGUAGE_ROTATION_ORDER[(start_idx + offset) % len(LANGUAGE_ROTATION_ORDER)]
        match_l = [s for s in SONG_MASTER_CATALOG if s["language"] == target_l and s["id"] not in used_ids]
        if match_l:
            return json.loads(json.dumps(match_l[0]))
        ext_hit = _discover_unused_extended_hit(target_l, used_ids)
        if ext_hit is not None:
            return ext_hit

    return json.loads(json.dumps(SONG_MASTER_CATALOG[len(used_ids) % len(SONG_MASTER_CATALOG)]))


def build_explanatory_music_guide(song: Dict[str, Any]) -> str:
    """
    Mesaj 1 (Video Altı / Reji & Karaoke Senkron Bilgisi):
    Gerçek şarkı sesinin ve kelime-kelime karaoke çevirisinin videoya milisaniye hassasiyetinde
    gömüldüğünü, dikey 9:16 kapak resmini ve kullanılan dönemsel ses icadını özetler.
    """
    flag = song.get("flag", "🎵")
    lang_tr = song.get("language_tr", "İngilizce")
    artist = song.get("artist", "")
    title = song.get("title", "")

    lines = [
        f"🎬 <b>ŞARKILARIN ANLAMI (@songtraibot) — GERÇEK SES & KARAOKE REELS HAZIR</b>",
        f"━━━━━━━━━━━━━━━━━━━━━━",
        f"🌍 <b>Dil:</b> {flag} {lang_tr} ({song.get('language_code', 'EN')})",
        f"🎵 <b>Şarkı:</b> {artist} — <i>{title}</i> ({song.get('release_year', '')})",
        f"🖼️ <b>Dikey Kapak Resmi (9:16):</b> Paylaşımda kapak olarak seçebileceğiniz şarkıya özel 2K dikey kapak görseli üstte ayrıca gönderildi.",
        f"🔊 <b>Ses & Senkron:</b> %100 Gerçek Şarkı Sesi (Sıfır Efekt) + Whisper/LRCLIB Kelime Vurgulu Karaoke (26.5 sn Vurucu Nakarat)",
        f"🎨 <b>Stüdyo & İcat:</b> Saf Beyaz Fon (#FFFFFF) • +20% Büyük Siyah Tipografi • Dönemsel Ses İcadı (Plak / DJ Mix / Kaset / CD)",
        f"",
        f"📲 <b>Doğrudan Paylaşıma Hazır:</b> Alttaki <b>Kısa & SEO Uyumlu Saf Kopyala-Yapıştır Açıklama</b> mesajını tek dokunuşla kopyalayıp paylaşabilirsiniz!",
    ]
    return "\n".join(lines)


def _slugify_hashtag(text: str) -> str:
    base = (text or "").split("(")[0].strip()
    tr_map = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
    cleaned = base.translate(tr_map).lower()
    return "".join(ch for ch in cleaned if ("a" <= ch <= "z") or ("0" <= ch <= "9"))


def build_pure_copy_paste_caption(song: Dict[str, Any]) -> str:
    """
    Mesaj 2 (%100 Saf, Kısa ve SEO Uyumlu Kopyala-Yapıştır Sosyal Medya Açıklaması):
    Sıfır sarmalayıcı başlık! Doğrudan kopyalanıp Instagram Reels / TikTok / YouTube Shorts'a yapıştırılır.
    """
    flag = song.get("flag", "🎵")
    lang_tr = song.get("language_tr", "İngilizce")
    artist = song.get("artist", "")
    title = song.get("title", "")
    hook = (song.get("viral_hook", "") or "").strip()
    lmeta = LANGUAGE_META.get(song.get("language", "ingilizce"), LANGUAGE_META["ingilizce"])

    # En vurucu tek cümlelik Türkçe alıntıyı seç (mırıldanma satırları yerine en anlamlı edebi dize)
    stanzas = song.get("curated_stanzas") or song.get("stanzas") or []
    best_tr_quote = ""
    for st_cand in stanzas:
        cand_tr = (st_cand.get("tr") or "").strip()
        if len(cand_tr) >= 24:
            best_tr_quote = cand_tr
            break
    if not best_tr_quote and stanzas:
        best_tr_quote = max((s.get("tr") or "").strip() for s in stanzas)

    # Hook metnini tek cümlelik kısa SEO özetine indirge
    short_hook = hook.split(".")[0].strip() + "." if "." in hook else hook

    artist_tag = _slugify_hashtag(artist)
    title_tag = _slugify_hashtag(title)
    extra_tags = " ".join(f"#{t}" for t in [artist_tag, title_tag] if t)

    lines = [
        f"{flag} {artist} — “{title}” Türkçe Çeviri ve Anlamı 🎶✨",
        f"",
    ]
    if best_tr_quote:
        lines.append(f"💬 “{best_tr_quote}”")
    if short_hook:
        lines.append(f"{short_hook}")
    lines.extend([
        f"",
        f"📌 En sevdiğiniz dize hangisi? Çevirisini istediğiniz şarkıyı yorumlara yazın, kaydetmeyi unutmayın! 👇",
        f"",
        f"#şarkıçevirileri #türkçeçeviri #şarkıanlamı {lmeta['tag']} {extra_tags} #keşfet #reels #lyrics #çevirişarkılar".replace("  ", " "),
    ])
    return "\n".join(lines)
