#!/usr/bin/env python3
"""Create the Sariwa database, tables, and starter catalog."""

from __future__ import annotations

import sys
from datetime import time
from pathlib import Path
from random import Random

import pymysql

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config import settings  # noqa: E402
from app.database import Base, SessionLocal, engine  # noqa: E402
from app.models import (  # noqa: E402
    DeliveryArea,
    DeliverySlot,
    FaqEntry,
    FaqKeyword,
    FlowerType,
    Occasion,
    Product,
    ProductImage,
    ProductOccasion,
    ProductSize,
    PromoCode,
    Review,
    User,
)
from app.security import hash_password  # noqa: E402

CARE = (
    "Trim stems at an angle, change the water every two days, and keep away from "
    "direct sun and ripening fruit. Lasts 5–7 days with care."
)
DELIVERY = (
    "Same-day delivery in Makati, Taguig, QC, Pasig, Pasay, Mandaluyong, and Marikina "
    "when ordered before 3pm. If a bloom is out of season, our florist substitutes "
    "with something of equal or greater value."
)

FAQS = [
    {
        "slug": "track",
        "icon": "shopping-bag",
        "quick": True,
        "sort": 1,
        "question_en": "Track my order",
        "question_tl": "Sundan ang order ko",
        "answer_en": "You can track any order with the number from your confirmation email — no account needed. It looks like SW-48213. Open Track an order, paste the number, and you'll see status, delivery window, and what's in the box.",
        "answer_tl": "Pwede ninyong sundan ang order gamit ang number sa confirmation email — hindi kailangan ng account. Parang SW-48213 ang itsura. Buksan ang Track an order, i-paste ang number, at makikita ninyo ang status, oras ng delivery, at laman ng box.",
        "link_url": "/track",
        "link_label_en": "Track an order",
        "link_label_tl": "Sundan ang order",
        "show_options": False,
        "keywords": [
            ("en", "track"),
            ("en", "tracking"),
            ("en", "order status"),
            ("en", "order number"),
            ("en", "where is my"),
            ("en", "shipment"),
            ("tl", "sundan"),
            ("tl", "nasaan"),
            ("tl", "status ng order"),
        ],
    },
    {
        "slug": "find",
        "icon": "flower",
        "quick": True,
        "sort": 2,
        "question_en": "Find the perfect flowers",
        "question_tl": "Hanapin ang tamang bulaklak",
        "answer_en": "Tell us the moment and we'll keep the list short. Shop by Birthday, Romance, I'm Sorry, Sympathy, or Just Because — or browse everything. Bouquets start around ₱890. For a mom's birthday, Masayang Kaarawan or Sunny Kalog are easy yeses.",
        "answer_tl": "Sabihin ninyo ang okasyon, iikli namin ang listahan. Pumili sa Birthday, Romance, I'm Sorry, Sympathy, o Just Because — o tingnan lahat. Nagsisimula ang bouquets sa ₱890. Para sa birthday ng nanay, ang Masayang Kaarawan o Sunny Kalog ay madaling piliin.",
        "link_url": "/shop",
        "link_label_en": "Browse the shop",
        "link_label_tl": "Tingnan ang shop",
        "show_options": False,
        "keywords": [
            ("en", "flower"),
            ("en", "flowers"),
            ("en", "bouquet"),
            ("en", "shop"),
            ("en", "perfect"),
            ("en", "birthday"),
            ("en", "romance"),
            ("en", "sympathy"),
            ("en", "sorry"),
            ("en", "gift"),
            ("en", "occasion"),
            ("en", "mom"),
            ("en", "mother"),
            ("tl", "bulaklak"),
            ("tl", "hanap"),
            ("tl", "hanapin"),
            ("tl", "kaarawan"),
            ("tl", "nanay"),
            ("tl", "mama"),
            ("tl", "regalo"),
            ("tl", "pasensya"),
        ],
    },
    {
        "slug": "delivery",
        "icon": "delivery",
        "quick": True,
        "sort": 3,
        "question_en": "Same-day delivery",
        "question_tl": "Same-day na padala",
        "answer_en": "We deliver daily across Metro Manila. Same-day is available in Makati, Taguig, Quezon City, Pasig, Pasay, Mandaluyong, and Marikina when you order before 3:00pm. Other Metro Manila areas are next-day (₱149; core areas are ₱99). Windows: Anytime 9AM–8PM, 9AM–12NN, 12NN–4PM, and 4PM–8PM.",
        "answer_tl": "Araw-araw po kaming nagde-deliver sa Metro Manila. Same-day sa Makati, Taguig, Quezon City, Pasig, Pasay, Mandaluyong, at Marikina kung mag-order kayo bago mag-3:00pm. Ibang areas sa Metro Manila ay next-day (₱149; ₱99 sa core areas). Mga oras: Anytime 9AM–8PM, 9AM–12NN, 12NN–4PM, at 4PM–8PM.",
        "link_url": "/contact",
        "link_label_en": "See delivery areas",
        "link_label_tl": "Tingnan ang delivery areas",
        "show_options": False,
        "keywords": [
            ("en", "delivery"),
            ("en", "deliver"),
            ("en", "same-day"),
            ("en", "sameday"),
            ("en", "same day"),
            ("en", "cutoff"),
            ("en", "3pm"),
            ("en", "area"),
            ("en", "areas"),
            ("en", "schedule"),
            ("en", "slot"),
            ("en", "arrive"),
            ("en", "frequency"),
            ("tl", "padala"),
            ("tl", "magpadala"),
            ("tl", "darating"),
            ("tl", "kailan"),
        ],
    },
    {
        "slug": "care",
        "icon": "leaf",
        "quick": True,
        "sort": 4,
        "question_en": "Care tips",
        "question_tl": "Payo sa pag-alaga",
        "answer_en": "Trim stems at an angle, change the water every two days, and keep the vase away from direct sun and ripening fruit. With that, a Sariwa bouquet usually lasts 5–7 days.",
        "answer_tl": "Putulin ang tangkay nang pahilis, palitan ang tubig tuwing dalawang araw, at ilayo sa araw at hinog na prutas. Sa ganitong alaga, tumatagal ang bouquet ng Sariwa ng 5–7 araw.",
        "link_url": None,
        "link_label_en": None,
        "link_label_tl": None,
        "show_options": False,
        "keywords": [
            ("en", "care"),
            ("en", "tips"),
            ("en", "water"),
            ("en", "vase"),
            ("en", "last"),
            ("en", "lasts"),
            ("en", "wilt"),
            ("en", "trim"),
            ("tl", "alaga"),
            ("tl", "alagaan"),
            ("tl", "tubig"),
            ("tl", "tumatagal"),
            ("tl", "lanta"),
        ],
    },
    {
        "slug": "payment",
        "icon": "bank-cards",
        "quick": False,
        "sort": 10,
        "question_en": "Payment options",
        "question_tl": "Mga paraan ng bayad",
        "answer_en": "We accept cash on delivery, GCash, and card at checkout. COD is collected when the bouquet arrives. Promo code SARIWA10 takes 10% off the bouquet (not delivery).",
        "answer_tl": "Tumatanggap kami ng cash on delivery, GCash, at card sa checkout. Ang COD ay binabayaran pagdating ng bouquet. Ang promo code SARIWA10 ay 10% off sa bouquet (hindi kasama ang delivery).",
        "link_url": "/cart",
        "link_label_en": "Go to cart",
        "link_label_tl": "Pumunta sa cart",
        "show_options": False,
        "keywords": [
            ("en", "payment"),
            ("en", "pay"),
            ("en", "cod"),
            ("en", "cash"),
            ("en", "gcash"),
            ("en", "card"),
            ("tl", "bayad"),
            ("tl", "bayaran"),
            ("tl", "pambayad"),
        ],
    },
    {
        "slug": "promo",
        "icon": "confetti",
        "quick": False,
        "sort": 11,
        "question_en": "Promo codes",
        "question_tl": "Mga promo code",
        "answer_en": "Use SARIWA10 at checkout for 10% off your bouquet. It applies to the flowers, not the delivery fee. One code per order.",
        "answer_tl": "Gamitin ang SARIWA10 sa checkout para sa 10% off sa bouquet. Sa bulaklak ito nalalapat, hindi sa delivery fee. Isang code bawat order.",
        "link_url": "/cart",
        "link_label_en": "Apply a code",
        "link_label_tl": "Gamitin ang code",
        "show_options": False,
        "keywords": [
            ("en", "promo"),
            ("en", "discount"),
            ("en", "coupon"),
            ("en", "sariwa10"),
            ("en", "percent"),
            ("tl", "diskwento"),
            ("tl", "promo"),
        ],
    },
    {
        "slug": "hours",
        "icon": "clock",
        "quick": False,
        "sort": 12,
        "question_en": "Hours and contact",
        "question_tl": "Oras at contact",
        "answer_en": "We're around daily, 8am–8pm. Call 0917 000 0000 or email hello@sariwa.ph. Same-day questions before 3pm usually get a same-day answer.",
        "answer_tl": "Bukas kami araw-araw, 8am–8pm. Tumawag sa 0917 000 0000 o mag-email sa hello@sariwa.ph. Ang same-day na tanong bago mag-3pm ay karanihang nasasagot din within the day.",
        "link_url": "/contact",
        "link_label_en": "Contact us",
        "link_label_tl": "Makipag-ugnayan",
        "show_options": False,
        "keywords": [
            ("en", "hours"),
            ("en", "open"),
            ("en", "contact"),
            ("en", "phone"),
            ("en", "email"),
            ("en", "hello@sariwa"),
            ("tl", "oras"),
            ("tl", "bukas"),
            ("tl", "telepono"),
            ("tl", "tawag"),
        ],
    },
    {
        "slug": "price",
        "icon": "money",
        "quick": False,
        "sort": 13,
        "question_en": "Prices",
        "question_tl": "Mga presyo",
        "answer_en": "Bouquets start at ₱890 and go up to around ₱2,350 for a grand size. Delivery is ₱99 in core Metro Manila and ₱149 elsewhere in the metro.",
        "answer_tl": "Nagsisimula ang bouquets sa ₱890 hanggang mga ₱2,350 para sa grand size. Ang delivery ay ₱99 sa core Metro Manila at ₱149 sa iba pang parte ng metro.",
        "link_url": "/shop",
        "link_label_en": "See prices",
        "link_label_tl": "Tingnan ang presyo",
        "show_options": False,
        "keywords": [
            ("en", "price"),
            ("en", "prices"),
            ("en", "cost"),
            ("en", "expensive"),
            ("en", "how much"),
            ("tl", "presyo"),
            ("tl", "magkano"),
            ("tl", "mahal"),
        ],
    },
    {
        "slug": "greeting",
        "icon": "sparkling",
        "quick": False,
        "sort": 20,
        "question_en": "Hello",
        "question_tl": "Kamusta",
        "answer_en": "Hi — I'm here. Pick one of the options below, or type a word like delivery, track, or care.",
        "answer_tl": "Hi — nandito lang ako. Pumili sa mga option sa ibaba, o mag-type ng salita tulad ng delivery, sundan, o alaga.",
        "link_url": None,
        "link_label_en": None,
        "link_label_tl": None,
        "show_options": True,
        "keywords": [
            ("en", "hello"),
            ("en", "hey"),
            ("en", "thanks"),
            ("en", "thank you"),
            ("tl", "kamusta"),
            ("tl", "kumusta"),
            ("tl", "salamat"),
        ],
    },
]


FLOWERS = [f"products/flower_{n}.png" for n in range(1, 7)]

# Homepage "This week's picks" shows featured first, then the next products by name.
# Give those six distinct covers so flower_1–flower_6 each appear once.
WEEKLY_PICK_COVERS = {
    "simpleng-mahal": "products/flower_1.png",
    "sunny-kalog": "products/flower_2.png",
    "tahimik-na-alay": "products/flower_3.png",
    "bahaghari": "products/flower_4.png",
    "ginhawa": "products/flower_5.png",
    "liwanag": "products/flower_6.png",
}


def gallery_for(slug: str) -> list[str]:
    pool = FLOWERS[:]
    cover = WEEKLY_PICK_COVERS.get(slug)
    if cover:
        rest = [path for path in pool if path != cover]
        Random(slug).shuffle(rest)
        return [cover, *rest[:2]]
    Random(slug).shuffle(pool)
    return pool[:3]

PRODUCTS = [
    {
        "slug": "sunny-kalog",
        "name": "Sunny Kalog",
        "short": "Sunflowers, marigold, and mustard mums.",
        "description": "A bright, unfussy mix for birthdays and ordinary Tuesdays. Sunflowers lead, marigold and mustard mums fill in, tied loosely so it still looks like a garden.",
        "type": "sunflowers",
        "occasions": ["birthday", "justbecause"],
        "featured": True,
        "palette": "#D79A2C,#EADCDF,#B5697A",
        "included": "Sunflowers, marigold, mustard mums, seasonal foliage, kraft wrap, and a handwritten note card.",
        "sizes": [{"name": "Classic", "stems": 10, "price": 1190, "compare": None, "default": True}],
    },
    {
        "slug": "simpleng-mahal",
        "name": "Simpleng Mahal",
        "short": "A dozen garden roses, no filler, no fuss.",
        "description": "A dozen garden roses, no filler, no fuss. Hand-tied the morning it's delivered, with a short note card included at no extra cost.",
        "type": "roses",
        "occasions": ["romance"],
        "featured": True,
        "palette": "#B5697A,#C77E8B,#8F4655",
        "included": "Fresh-cut garden roses, seasonal foliage, kraft wrap, and a handwritten note card. Vase not included.",
        "sizes": [
            {"name": "Petite (6)", "stems": 6, "price": 990, "compare": 1290, "default": False},
            {"name": "Classic (12)", "stems": 12, "price": 1450, "compare": 1890, "default": True},
            {"name": "Grand (24)", "stems": 24, "price": 2350, "compare": 2990, "default": False},
        ],
    },
    {
        "slug": "tahimik-na-alay",
        "name": "Tahimik na Alay",
        "short": "White lilies and eucalyptus, quietly arranged.",
        "description": "White lilies and silver-dollar eucalyptus, arranged so the room stays quiet. Meant for condolences, hospital rooms, and any moment that doesn't need extra words.",
        "type": "lilies",
        "occasions": ["sympathy", "sorry"],
        "featured": True,
        "palette": "#FFFDF9,#8A9A7E,#EADCDF",
        "included": "White lilies, eucalyptus, muted foliage, kraft wrap, and a blank note card.",
        "sizes": [{"name": "Classic", "stems": 8, "price": 1690, "compare": None, "default": True}],
    },
    {
        "slug": "paumanhin",
        "name": "Paumanhin",
        "short": "Soft blush tulips — says it before you do.",
        "description": "Blush tulips in a loose gather. Soft enough to arrive without making a scene, clear enough that the other person will know what you meant.",
        "type": "mixed",
        "occasions": ["sorry"],
        "featured": False,
        "palette": "#EADCDF,#C9D0C4,#B5697A",
        "included": "Blush tulips, light foliage, kraft wrap, and a handwritten note card.",
        "sizes": [{"name": "Classic", "stems": 10, "price": 1290, "compare": None, "default": True}],
    },
    {
        "slug": "bahaghari",
        "name": "Bahaghari",
        "short": "Mixed garden blooms, a little of everything.",
        "description": "A little of everything from the morning market. Color without a theme — for desks, kitchen tables, and 'I saw these and thought of you.'",
        "type": "mixed",
        "occasions": ["justbecause"],
        "featured": False,
        "palette": "#D79A2C,#8A9A7E,#B5697A",
        "included": "Seasonal mixed garden blooms, foliage, kraft wrap, and a note card.",
        "sizes": [{"name": "Classic", "stems": 12, "price": 990, "compare": 1350, "default": True}],
    },
    {
        "slug": "masayang-kaarawan",
        "name": "Masayang Kaarawan",
        "short": "Playful pinks, peach ranunculus, one big bow.",
        "description": "Playful pinks, peach ranunculus, and one honest bow. Birthday energy without the balloon-and-glitter version of it.",
        "type": "mixed",
        "occasions": ["birthday", "romance"],
        "featured": True,
        "palette": "#B5697A,#D79A2C,#EADCDF",
        "included": "Peach ranunculus, garden roses, seasonal pinks, a grosgrain bow, kraft wrap, and a note card.",
        "sizes": [{"name": "Classic", "stems": 14, "price": 1590, "compare": None, "default": True}],
    },
    {
        "slug": "puting-rosas-24",
        "name": "Puting Rosas (24)",
        "short": "Two dozen white roses, classic and quiet.",
        "description": "Two dozen white roses. Classic, quiet, and still the arrangement people remember. Suitable for romance and for sympathy, depending on the note.",
        "type": "roses",
        "occasions": ["romance", "sympathy"],
        "featured": True,
        "palette": "#FFFDF9,#8A9A7E,#EADCDF",
        "included": "24 white roses, eucalyptus, kraft wrap, and a handwritten note card.",
        "sizes": [
            {"name": "Classic (12)", "stems": 12, "price": 1290, "compare": 1590, "default": False},
            {"name": "Grand (24)", "stems": 24, "price": 1990, "compare": 2450, "default": True},
        ],
    },
    {
        "slug": "ginhawa",
        "name": "Ginhawa",
        "short": "Get-well mix — citrus tones, no heavy scent.",
        "description": "Citrus tones and a light scent, made for recovery rooms and 'take it easy' texts. Nothing heavy, nothing that asks for a vase speech.",
        "type": "mixed",
        "occasions": ["justbecause", "sorry"],
        "featured": False,
        "palette": "#D79A2C,#8A9A7E,#FFFDF9",
        "included": "Citrus-toned seasonal blooms, eucalyptus, kraft wrap, and a note card.",
        "sizes": [{"name": "Classic", "stems": 10, "price": 1150, "compare": None, "default": True}],
    },
    {
        "slug": "liwanag",
        "name": "Liwanag",
        "short": "Golden sunflowers, single-stem statement.",
        "description": "A handful of golden sunflowers, faced forward. One idea, done clearly — for birthdays, desks, and anyone who doesn't want a complicated bouquet.",
        "type": "sunflowers",
        "occasions": ["birthday", "justbecause"],
        "featured": False,
        "palette": "#D79A2C,#B5697A,#8A9A7E",
        "included": "Sunflowers, minimal foliage, kraft wrap, and a note card.",
        "sizes": [{"name": "Classic", "stems": 5, "price": 890, "compare": None, "default": True}],
    },
    {
        "slug": "unang-tingin",
        "name": "Unang Tingin",
        "short": "Lavender roses with silver dollar eucalyptus.",
        "description": "Lavender garden roses with silver-dollar eucalyptus. Soft, a little unexpected, and better than a first-date overthink.",
        "type": "roses",
        "occasions": ["romance"],
        "featured": False,
        "palette": "#B5697A,#8A9A7E,#EADCDF",
        "included": "Lavender garden roses, silver-dollar eucalyptus, kraft wrap, and a note card.",
        "sizes": [{"name": "Classic", "stems": 12, "price": 1750, "compare": None, "default": True}],
    },
    {
        "slug": "payapa",
        "name": "Payapa",
        "short": "Calla lilies, structured and minimal.",
        "description": "Calla lilies in a structured gather. Minimal on purpose — for sympathy, for altars, for anyone who prefers a clean line to a mixed bunch.",
        "type": "lilies",
        "occasions": ["sympathy"],
        "featured": False,
        "palette": "#FFFDF9,#C9D0C4,#8A9A7E",
        "included": "White calla lilies, structured foliage, kraft wrap, and a blank note card.",
        "sizes": [{"name": "Classic", "stems": 7, "price": 1890, "compare": None, "default": True}],
    },
    {
        "slug": "tuwang-tuwa",
        "name": "Tuwang-tuwa",
        "short": "Bright mixed blooms for no reason at all.",
        "description": "Bright mixed blooms for no reason at all. The arrangement you send when the occasion is simply that someone exists.",
        "type": "mixed",
        "occasions": ["justbecause", "birthday"],
        "featured": False,
        "palette": "#D79A2C,#B5697A,#EADCDF",
        "included": "Seasonal mixed blooms, foliage, kraft wrap, and a note card.",
        "sizes": [{"name": "Classic", "stems": 12, "price": 1050, "compare": 1290, "default": True}],
    },
]

REVIEWS = {
    "sunny-kalog": [(5, "Ordered five minutes before a meeting. It still arrived same day.", "Regina"), (5, "Looked exactly like the photo, which almost never happens.", "Marco"), (4, "A little smaller than I imagined, still made her day.", "Anna")],
    "simpleng-mahal": [(5, "Felt like asking a friend who knows flowers, not a website.", "Anna"), (5, "The note card handwriting was a nice touch.", "Paolo"), (5, "Classic roses, no filler. That's what I wanted.", "Lina"), (4, "Arrived a bit later than the window, flowers were perfect.", "Gio")],
    "tahimik-na-alay": [(5, "Quiet and appropriate. That's rare.", "Bea"), (5, "The family kept it by the photo. Thank you.", "Carlo")],
    "paumanhin": [(5, "She texted before I even got home.", "Miguel"), (4, "Tulips were slightly closed. Opened overnight.", "Kat")],
    "bahaghari": [(4, "Colorful without being loud. Good desk flowers.", "Ira")],
    "masayang-kaarawan": [(5, "The bow made my sister laugh. That's the brief.", "Nina"), (5, "Peach ranunculus were the whole point. They showed up.", "Sam")],
    "puting-rosas-24": [(5, "Two dozen, counted. White, actually white.", "Elena")],
    "ginhawa": [(5, "No heavy scent in a hospital room. Thank you for that.", "Mika")],
    "liwanag": [(4, "Simple and bright. Did what it needed to.", "Dex")],
    "unang-tingin": [(5, "Lavender roses look more expensive than they are. In a good way.", "Pat")],
    "payapa": [(5, "Structured, not sad-looking. That's hard.", "Ria")],
    "tuwang-tuwa": [(5, "Sent it for no reason. She sent a voice note back.", "Alex")],
}


def ensure_database() -> None:
    if settings.uses_sqlite:
        settings.sqlite_file.parent.mkdir(parents=True, exist_ok=True)
        return
    conn = pymysql.connect(
        host=settings.mysql_host,
        port=settings.mysql_port,
        user=settings.mysql_user,
        password=settings.mysql_password or None,
        charset="utf8mb4",
        autocommit=True,
    )
    with conn.cursor() as cursor:
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{settings.mysql_database}` "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
    conn.close()


def seed(reset: bool = True) -> None:
    ensure_database()
    if reset:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        occasions = [
            Occasion(slug="birthday", name="Birthday", icon="birthday-cake", sort_order=1),
            Occasion(slug="sorry", name="I'm Sorry", icon="handshake", sort_order=2),
            Occasion(slug="romance", name="Romance", icon="heart", sort_order=3),
            Occasion(slug="sympathy", name="Sympathy", icon="camellia", sort_order=4),
            Occasion(slug="justbecause", name="Just Because", icon="sun", sort_order=5),
        ]
        types = [
            FlowerType(slug="roses", name="Roses"),
            FlowerType(slug="sunflowers", name="Sunflowers"),
            FlowerType(slug="lilies", name="Lilies"),
            FlowerType(slug="mixed", name="Mixed Blooms"),
        ]
        areas = [
            DeliveryArea(slug="makati", name="Makati", fee=99, is_core=True),
            DeliveryArea(slug="taguig", name="Taguig", fee=99, is_core=True),
            DeliveryArea(slug="qc", name="Quezon City", fee=99, is_core=True),
            DeliveryArea(slug="pasig", name="Pasig", fee=99, is_core=True),
            DeliveryArea(slug="pasay", name="Pasay", fee=99, is_core=True),
            DeliveryArea(slug="mandaluyong", name="Mandaluyong", fee=99, is_core=True),
            DeliveryArea(slug="marikina", name="Marikina", fee=99, is_core=True),
            DeliveryArea(slug="other", name="Other Metro Manila", fee=149, is_core=False),
        ]
        slots = [
            DeliverySlot(slug="anytime", name="Anytime (9AM – 8PM)", start_time=time(9, 0), end_time=time(20, 0), sort_order=0),
            DeliverySlot(slug="morning", name="9AM – 12NN", start_time=time(9, 0), end_time=time(12, 0), sort_order=1),
            DeliverySlot(slug="afternoon", name="12NN – 4PM", start_time=time(12, 0), end_time=time(16, 0), sort_order=2),
            DeliverySlot(slug="evening", name="4PM – 8PM", start_time=time(16, 0), end_time=time(20, 0), sort_order=3),
        ]
        db.add_all(occasions + types + areas + slots)
        db.add(PromoCode(code="SARIWA10", discount_percent=10, is_active=True, description="10% off your bouquet"))
        admin = User(
            email="ivan.p@example.net",
            password_hash=hash_password("sariwa-admin"),
            first_name="Sariwa",
            last_name="Florist",
            phone="09170000000",
            role="admin",
        )
        demo = User(
            email="regina@example.com",
            password_hash=hash_password("sariwa123"),
            first_name="Regina",
            last_name="Santos",
            phone="09171234567",
            role="customer",
        )
        reviewers = {
            "Regina": demo,
            "Marco": User(email="marco@example.com", password_hash=hash_password("sariwa123"), first_name="Marco", last_name="Reyes", role="customer"),
            "Anna": User(email="anna@example.com", password_hash=hash_password("sariwa123"), first_name="Anna", last_name="Lim", role="customer"),
            "Paolo": User(email="paolo@example.com", password_hash=hash_password("sariwa123"), first_name="Paolo", last_name="Cruz", role="customer"),
            "Lina": User(email="lina@example.com", password_hash=hash_password("sariwa123"), first_name="Lina", last_name="Tan", role="customer"),
            "Gio": User(email="gio@example.com", password_hash=hash_password("sariwa123"), first_name="Gio", last_name="Uys", role="customer"),
            "Bea": User(email="bea@example.com", password_hash=hash_password("sariwa123"), first_name="Bea", last_name="Ong", role="customer"),
            "Carlo": User(email="carlo@example.com", password_hash=hash_password("sariwa123"), first_name="Carlo", last_name="Sison", role="customer"),
            "Miguel": User(email="miguel@example.com", password_hash=hash_password("sariwa123"), first_name="Miguel", last_name="Yap", role="customer"),
            "Kat": User(email="kat@example.com", password_hash=hash_password("sariwa123"), first_name="Kat", last_name="Go", role="customer"),
            "Ira": User(email="ira@example.com", password_hash=hash_password("sariwa123"), first_name="Ira", last_name="Bautista", role="customer"),
            "Nina": User(email="nina@example.com", password_hash=hash_password("sariwa123"), first_name="Nina", last_name="Fernandez", role="customer"),
            "Sam": User(email="sam@example.com", password_hash=hash_password("sariwa123"), first_name="Sam", last_name="Villanueva", role="customer"),
            "Elena": User(email="elena@example.com", password_hash=hash_password("sariwa123"), first_name="Elena", last_name="Chua", role="customer"),
            "Mika": User(email="mika@example.com", password_hash=hash_password("sariwa123"), first_name="Mika", last_name="Ramos", role="customer"),
            "Dex": User(email="dex@example.com", password_hash=hash_password("sariwa123"), first_name="Dex", last_name="Navarro", role="customer"),
            "Pat": User(email="pat@example.com", password_hash=hash_password("sariwa123"), first_name="Pat", last_name="Sy", role="customer"),
            "Ria": User(email="ria@example.com", password_hash=hash_password("sariwa123"), first_name="Ria", last_name="Mendoza", role="customer"),
            "Alex": User(email="alex@example.com", password_hash=hash_password("sariwa123"), first_name="Alex", last_name="Diaz", role="customer"),
        }
        db.add_all([admin, *reviewers.values()])
        db.flush()

        occ_map = {item.slug: item for item in occasions}
        type_map = {item.slug: item for item in types}

        for index, item in enumerate(PRODUCTS):
            product = Product(
                slug=item["slug"],
                name=item["name"],
                short_description=item["short"],
                description=item["description"],
                flower_type_id=type_map[item["type"]].id,
                featured=item["featured"],
                same_day_eligible=True,
                color_palette=item["palette"],
                included_text=item["included"],
                delivery_text=DELIVERY,
                care_text=CARE,
                sort_order=index,
            )
            db.add(product)
            db.flush()
            for size in item["sizes"]:
                db.add(
                    ProductSize(
                        product_id=product.id,
                        name=size["name"],
                        stem_count=size["stems"],
                        price=size["price"],
                        compare_at_price=size["compare"],
                        is_default=size["default"],
                    )
                )
            for order, url in enumerate(gallery_for(item["slug"])):
                db.add(ProductImage(product_id=product.id, url=url, alt=item["name"], sort_order=order))
            for slug in item["occasions"]:
                db.add(ProductOccasion(product_id=product.id, occasion_id=occ_map[slug].id))
            for rating, comment, author in REVIEWS.get(item["slug"], []):
                db.add(
                    Review(
                        product_id=product.id,
                        user_id=reviewers[author].id,
                        rating=rating,
                        comment=comment,
                    )
                )

        for item in FAQS:
            faq = FaqEntry(
                slug=item["slug"],
                icon=item["icon"],
                is_quick_action=item["quick"],
                sort_order=item["sort"],
                question_en=item["question_en"],
                question_tl=item["question_tl"],
                answer_en=item["answer_en"],
                answer_tl=item["answer_tl"],
                link_url=item["link_url"],
                link_label_en=item["link_label_en"],
                link_label_tl=item["link_label_tl"],
                show_options=item["show_options"],
            )
            db.add(faq)
            db.flush()
            for language, keyword in item["keywords"]:
                db.add(FaqKeyword(faq_id=faq.id, keyword=keyword.lower(), language=language))

        db.commit()
        print(f"Using {'SQLite' if settings.uses_sqlite else 'MySQL'} ({settings.database_url.split('://')[0]}).")
        print("Sariwa database seeded.")
        print("Demo login:  regina@example.com / sariwa123")
        print("Admin login: ivan.p@example.net / sariwa-admin")
        print("Promo code:  SARIWA10")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
