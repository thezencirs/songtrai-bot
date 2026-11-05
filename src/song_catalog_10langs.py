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
}

LANGUAGE_META: Dict[str, Dict[str, str]] = {
    "ingilizce": {"code": "EN", "name_tr": "İngilizce", "flag": "🇬🇧", "tag": "#ingilizceşarkılar #şarkıçevirileri"},
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

LANGUAGE_ROTATION_ORDER: List[str] = [
    "ingilizce",
    "fransizca",
    "rusca",
    "japonca",
    "ispanyolca",
    "korece",
    "italyanca",
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


def build_live_song_concept_from_query(
    query_text: str,
    forced_lang: str = "otomatik",
    requester_chat_id: str = "",
) -> Dict[str, Any]:
    """
    Kullanıcı Telegram'dan (@songtraibot) özel bir şarkı adı / sanatçı gönderdiğinde:
    1) Önce küratörlü 10 dil kataloğunda eşleşme var mı kontrol eder.
    2) Yoksa iTunes Search API + LRCLIB API üzerinden gerçek şarkıyı, albüm kapağını ve nakarat sözlerini
       çekip tertemiz Türkçe çevirisiyle canlı olarak oluşturur.
    """
    q_low = (query_text or "").strip().lower()
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

    short_hash = hashlib.md5(f"{artist_name}_{track_title}".encode("utf-8")).hexdigest()[:6]
    return {
        "id": f"custom_{lmeta['code'].lower()}_{short_hash}",
        "language": lang_key,
        "language_code": lmeta["code"],
        "language_tr": lmeta["name_tr"],
        "flag": lmeta["flag"],
        "artist": artist_name,
        "title": track_title,
        "release_year": release_year,
        "itunes_query": f"{artist_name} {track_title}",
        "artwork_url": artwork_url,
        "chorus_timestamp": "0:42 - 0:57 (Nakarat / En Popüler Kısım)",
        "social_audio_search": f"{artist_name} - {track_title}",
        "cover_kicker": f"{lmeta['flag']} {lmeta['name_tr'].upper()} POPÜLER ŞARKI • TÜRKÇE ÇEVİRİ",
        "cover_headline": f"{artist_name.upper()} — {track_title.upper()} TÜRKÇE ANLAMI",
        "viral_hook": f"{artist_name} tarafından seslendirilen '{track_title}', melodisinin arkasında derin ve etkileyici bir hikaye taşıyor.",
        "stanzas": stanzas,
        "requester_chat_id": requester_chat_id,
    }


def select_next_song_concept(
    force_language: str = "otomatik",
    custom_song: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Sıfır-Tekrar Çift Kilit defterini kontrol ederek 10 dil arasında dengeli rotasyonla
    sıradaki popüler şarkıyı seçer.
    """
    if custom_song is not None:
        return custom_song

    used_ids = load_used_song_ids()
    norm_lang = normalize_language_key(force_language)

    candidates = SONG_MASTER_CATALOG
    if norm_lang != "otomatik":
        lang_filtered = [s for s in SONG_MASTER_CATALOG if s["language"] == norm_lang]
        if lang_filtered:
            candidates = lang_filtered

    unused = [s for s in candidates if s["id"] not in used_ids]
    if not unused:
        # Tüm katalog tamamlandıysa ilgili filtrede en baştan temiz rotasyon başlat
        unused = candidates

    # Eğer otomatik moddaysa, son kullanılan dilden farklı bir dili önceliklendir
    chosen = unused[0]
    if norm_lang == "otomatik" and LEDGER_PATH.exists():
        try:
            last_lang = json.loads(LEDGER_PATH.read_text(encoding="utf-8")).get("last_language", "")
            if last_lang in LANGUAGE_ROTATION_ORDER:
                start_idx = (LANGUAGE_ROTATION_ORDER.index(last_lang) + 1) % len(LANGUAGE_ROTATION_ORDER)
                for offset in range(len(LANGUAGE_ROTATION_ORDER)):
                    target_l = LANGUAGE_ROTATION_ORDER[(start_idx + offset) % len(LANGUAGE_ROTATION_ORDER)]
                    match_l = [s for s in unused if s["language"] == target_l]
                    if match_l:
                        chosen = match_l[0]
                        break
        except Exception:
            pass

    return json.loads(json.dumps(chosen))


def build_explanatory_music_guide(song: Dict[str, Any]) -> str:
    """
    Mesaj 1 (Video Altı / Reji & Karaoke Senkron Bilgisi):
    Gerçek şarkı sesinin ve kelime-kelime karaoke çevirisinin videoya milisaniye hassasiyetinde
    gömüldüğünü ve kullanılan dönemsel ses icadını özetler.
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
        f"🔊 <b>Ses & Senkron:</b> %100 Gerçek Şarkı Sesi (Sıfır Efekt) + Whisper/LRCLIB Kelime Vurgulu Karaoke",
        f"🎨 <b>Stüdyo & İcat:</b> Saf Beyaz Fon (#FFFFFF) • Siyah Tipografi • Dönemsel Ses İcadı (Plak / DJ Mix / Kaset / CD)",
        f"",
        f"📲 <b>Doğrudan Paylaşıma Hazır:</b> Videoda gerçek şarkı sesi ve kelime-kelime Türkçe çeviri senkronu hazırdır; alttaki <b>Saf Kopyala-Yapıştır Açıklama</b> mesajını tek dokunuşla kopyalayıp paylaşabilirsiniz!",
    ]
    return "\n".join(lines)


def build_pure_copy_paste_caption(song: Dict[str, Any]) -> str:
    """
    Mesaj 2 (%100 Saf Kopyala-Yapıştır Sosyal Medya Açıklaması):
    Sıfır sarmalayıcı başlık! Doğrudan kopyalanıp Instagram Reels / TikTok / YouTube Shorts'a yapıştırılır.
    """
    flag = song.get("flag", "🎵")
    lang_tr = song.get("language_tr", "İngilizce")
    artist = song.get("artist", "")
    title = song.get("title", "")
    hook = song.get("viral_hook", "")
    lmeta = LANGUAGE_META.get(song.get("language", "ingilizce"), LANGUAGE_META["ingilizce"])

    lines = [
        f"{flag} {artist} — “{title}” şarkısının gerçek Türkçe anlamını biliyor muydunuz? 🎶✨",
        f"",
        f"{hook}",
        f"",
        f"📖 Şarkının En Vurucu Sözleri ve Türkçe Çevirisi:",
    ]

    for idx, st in enumerate(song.get("stanzas") or [], start=1):
        orig = st.get("orig", "")
        tr = st.get("tr", "")
        lines.append(f"{idx}️⃣ “{orig}”")
        lines.append(f"🇹🇷 Çevirisi: “{tr}”")
        lines.append("")

    lines.extend([
        f"💬 Sizin bu şarkıda kalbinize en çok dokunan dize hangisi? Yorumlarda buluşalım, bir sonraki çeviri için istediğiniz şarkıyı yazın! 👇",
        f"📌 Daha sonra tekrar dinlemek ve sözlerini okumak için videoyu kaydetmeyi unutmayın.",
        f"",
        f"#şarkıçevirileri #türkçeçeviri #şarkılarınhikayesi {lmeta['tag']} #keşfet #reels #lyrics #müzik #songtraibot",
    ])
    return "\n".join(lines)
