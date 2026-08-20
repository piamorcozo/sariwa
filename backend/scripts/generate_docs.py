#!/usr/bin/env python3
"""Generate Sariwa documentation PDFs."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
DOCS.mkdir(exist_ok=True)

FOREST = HexColor("#2C3A2B")
FOREST_SOFT = HexColor("#4A5C46")
CREAM = HexColor("#F5F0E6")
CREAM_DEEP = HexColor("#EDE5D4")
ROSE = HexColor("#B5697A")
SAGE = HexColor("#8A9A7E")
WHITE = HexColor("#FFFDF9")
MUSTARD = HexColor("#D79A2C")


def rounded_rect(c: canvas.Canvas, x, y, w, h, r, fill, stroke=None, width=1):
    c.saveState()
    c.setFillColor(fill)
    if stroke:
        c.setStrokeColor(stroke)
        c.setLineWidth(width)
        c.roundRect(x, y, w, h, r, fill=1, stroke=1)
    else:
        c.setStrokeColor(fill)
        c.roundRect(x, y, w, h, r, fill=1, stroke=0)
    c.restoreState()


def header(c: canvas.Canvas, width, height, title, subtitle):
    rounded_rect(c, 0, 0, width, height, 0, CREAM)
    rounded_rect(c, 0, height - 28 * mm, width, 28 * mm, 0, FOREST)
    c.setFillColor(WHITE)
    c.setFont("Times-Bold", 18)
    c.drawString(18 * mm, height - 14 * mm, "sariwa")
    c.setFillColor(ROSE)
    c.setFont("Times-Italic", 18)
    c.drawString(18 * mm + c.stringWidth("sariwa", "Times-Bold", 18) - 12, height - 14 * mm, "")
    c.setFillColor(WHITE)
    c.setFont("Times-Roman", 11)
    c.drawRightString(width - 18 * mm, height - 12 * mm, title)
    c.setFont("Times-Italic", 9)
    c.drawRightString(width - 18 * mm, height - 18 * mm, subtitle)
    c.setFillColor(FOREST_SOFT)
    c.setFont("Times-Roman", 8)
    c.drawString(18 * mm, 10 * mm, "Sariwa Flower Shop  ·  Metro Manila  ·  2026")
    c.drawRightString(width - 18 * mm, 10 * mm, "Internal project documentation")


def oval(c, cx, cy, w, h, label, lines=1):
    c.setFillColor(WHITE)
    c.setStrokeColor(FOREST)
    c.setLineWidth(1.1)
    c.ellipse(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, fill=1, stroke=1)
    c.setFillColor(FOREST)
    c.setFont("Times-Roman", 8)
    if "\n" in label:
        parts = label.split("\n")
        c.drawCentredString(cx, cy + 2, parts[0])
        c.drawCentredString(cx, cy - 8, parts[1])
    else:
        c.drawCentredString(cx, cy - 3, label)


def actor(c, x, y, name):
    c.setStrokeColor(FOREST)
    c.setFillColor(FOREST)
    c.setLineWidth(1.4)
    c.circle(x, y + 22, 7, fill=0, stroke=1)
    c.line(x, y + 15, x, y - 2)
    c.line(x - 10, y + 8, x + 10, y + 8)
    c.line(x, y - 2, x - 8, y - 16)
    c.line(x, y - 2, x + 8, y - 16)
    c.setFont("Times-Bold", 9)
    c.drawCentredString(x, y - 28, name)


def arrow(c, x1, y1, x2, y2):
    c.setStrokeColor(SAGE)
    c.setFillColor(SAGE)
    c.setLineWidth(0.9)
    c.line(x1, y1, x2, y2)


def write_use_case():
    path = DOCS / "sariwa-use-case-diagram.pdf"
    width, height = landscape(A4)
    c = canvas.Canvas(str(path), pagesize=landscape(A4))
    header(c, width, height, "Use Case Diagram", "Actors, system boundary, and customer journeys")

    # System box
    box_x, box_y, box_w, box_h = 62 * mm, 22 * mm, 174 * mm, 148 * mm
    c.setStrokeColor(FOREST)
    c.setFillColor(Color(1, 0.992, 0.976, alpha=0.35))
    c.setLineWidth(1.4)
    c.roundRect(box_x, box_y, box_w, box_h, 8, fill=1, stroke=1)
    c.setFillColor(ROSE)
    c.setFont("Times-Bold", 11)
    c.drawCentredString(box_x + box_w / 2, box_y + box_h - 10 * mm, "Sariwa Flower Shop")

    actor(c, 32 * mm, 110 * mm, "Guest")
    actor(c, 32 * mm, 55 * mm, "Customer")
    actor(c, width - 32 * mm, 90 * mm, "Florist / Admin")

    cases = [
        (90, 145, "Browse catalog"),
        (128, 145, "Filter by occasion"),
        (166, 145, "Search arrangements"),
        (204, 145, "View product details"),
        (90, 122, "Add to cart"),
        (128, 122, "Manage cart"),
        (166, 122, "Apply promo code"),
        (204, 122, "Checkout as guest"),
        (90, 99, "Enter delivery details"),
        (128, 99, "Choose payment"),
        (166, 99, "Place order"),
        (204, 99, "Track order"),
        (90, 76, "Register / sign in"),
        (128, 76, "Save favorites"),
        (166, 76, "View order history"),
        (204, 76, "Send contact message"),
        (109, 53, "Read Our Story"),
        (166, 53, "Same-day cutoff check"),
        (128, 32, "Manage catalog &\norders"),
    ]

    for x, y, label in cases:
        oval(c, x * mm, y * mm, 34 * mm, 12 * mm, label)

    # Guest associations
    guest_cases = [
        (90, 145), (128, 145), (166, 145), (204, 145),
        (90, 122), (128, 122), (166, 122), (204, 122),
        (90, 99), (128, 99), (166, 99), (204, 99),
        (109, 53), (166, 53), (204, 76),
    ]
    for x, y in guest_cases:
        arrow(c, 40 * mm, 110 * mm, (x - 17) * mm, y * mm)

    # Customer extra
    for x, y in [(90, 76), (128, 76), (166, 76), (128, 32)]:
        arrow(c, 40 * mm, 55 * mm, (x - 17) * mm, y * mm)

    # Admin
    arrow(c, width - 42 * mm, 90 * mm, 145 * mm, 32 * mm)
    arrow(c, width - 42 * mm, 90 * mm, 183 * mm, 53 * mm)

    # Page 2 - narrative
    c.showPage()
    header(c, width, height, "Use Case Descriptions", "Primary flows for Sariwa")

    stories = [
        ("UC-01 Browse & filter", "Guest or Customer opens Shop, filters by occasion, flower type, or price, and scans a short curated list instead of an infinite catalog."),
        ("UC-02 View arrangement", "The shopper opens a product page, compares sizes, reads what's included / delivery / care, and sees similar bouquets."),
        ("UC-03 Cart", "The shopper adds a size and quantity. Cart persists by session (and merges after sign-in). Quantity can be changed or removed."),
        ("UC-04 Checkout", "Guest or Customer enters recipient, address, Metro Manila area, date, time window, optional gift note, optional promo SARIWA10, and payment method (COD, GCash, card)."),
        ("UC-05 Place order", "System snapshots line items, fees, and discount, issues an SW-##### number, and clears the cart. Same-day orders are rejected after 3:00pm Asia/Manila."),
        ("UC-06 Track order", "Anyone with the order number can look up status, recipient, schedule, and totals — no account required."),
        ("UC-07 Account", "A registered customer signs in to save favorites and review past orders. Checkout still works without an account."),
        ("UC-08 Contact", "A visitor sends a named message (order, delivery, product, other). Staff can read it from contact_messages."),
        ("UC-09 Catalog maintenance", "Florist / Admin maintains products, sizes, images, occasions, areas, slots, and promo codes in the database."),
    ]

    y = height - 42 * mm
    for title, body in stories:
        rounded_rect(c, 18 * mm, y - 22 * mm, width - 36 * mm, 24 * mm, 6, WHITE, CREAM_DEEP)
        c.setFillColor(ROSE)
        c.setFont("Times-Bold", 10)
        c.drawString(24 * mm, y - 6 * mm, title)
        c.setFillColor(FOREST_SOFT)
        c.setFont("Times-Roman", 9)
        text = c.beginText(24 * mm, y - 12 * mm)
        text.setLeading(12)
        for line in _wrap(body, 118):
            text.textLine(line)
        c.drawText(text)
        y -= 28 * mm

    c.save()
    print(f"Wrote {path}")


def _wrap(text: str, width: int) -> list[str]:
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        if len(trial) > width:
            lines.append(current)
            current = word
        else:
            current = trial
    if current:
        lines.append(current)
    return lines


TABLES = [
    ("users", "Registered shoppers and staff.", [
        ("id", "INT PK"), ("email", "VARCHAR(255) UNIQUE"), ("password_hash", "VARCHAR(255)"),
        ("first_name", "VARCHAR(100)"), ("last_name", "VARCHAR(100)"), ("phone", "VARCHAR(30)"),
        ("role", "customer | admin"), ("created_at", "DATETIME"),
    ]),
    ("occasions", "Birthday, Romance, Sympathy, I'm Sorry, Just Because.", [
        ("id", "INT PK"), ("slug", "VARCHAR(50) UNIQUE"), ("name", "VARCHAR(80)"),
        ("icon", "Icons8 name"), ("sort_order", "INT"),
    ]),
    ("flower_types", "Roses, Sunflowers, Lilies, Mixed Blooms.", [
        ("id", "INT PK"), ("slug", "VARCHAR(50) UNIQUE"), ("name", "VARCHAR(80)"),
    ]),
    ("products", "Arrangements offered in the shop.", [
        ("id", "INT PK"), ("slug", "VARCHAR(120) UNIQUE"), ("name", "VARCHAR(160)"),
        ("short_description", "VARCHAR(255)"), ("description", "TEXT"),
        ("flower_type_id", "FK flower_types"), ("featured", "BOOL"),
        ("same_day_eligible", "BOOL"), ("color_palette", "VARCHAR(120)"),
        ("included_text / delivery_text / care_text", "TEXT"),
        ("is_active", "BOOL"), ("sort_order", "INT"), ("created_at", "DATETIME"),
    ]),
    ("product_sizes", "Petite / Classic / Grand pricing.", [
        ("id", "INT PK"), ("product_id", "FK products"), ("name", "VARCHAR(80)"),
        ("stem_count", "INT"), ("price", "DECIMAL(10,2)"),
        ("compare_at_price", "DECIMAL(10,2)"), ("is_default", "BOOL"),
    ]),
    ("product_images", "Gallery photos per arrangement.", [
        ("id", "INT PK"), ("product_id", "FK products"), ("url", "VARCHAR(500)"),
        ("alt", "VARCHAR(160)"), ("sort_order", "INT"),
    ]),
    ("product_occasions", "Many-to-many products ↔ occasions.", [
        ("product_id", "PK, FK products"), ("occasion_id", "PK, FK occasions"),
    ]),
    ("reviews", "Star ratings shown on cards and PDP.", [
        ("id", "INT PK"), ("product_id", "FK products"), ("user_id", "FK users"),
        ("rating", "INT 1–5"), ("comment", "TEXT"), ("created_at", "DATETIME"),
    ]),
    ("favorites", "Saved arrangements for a signed-in customer.", [
        ("id", "INT PK"), ("user_id", "FK users"), ("product_id", "FK products"),
        ("created_at", "DATETIME"), ("UNIQUE(user_id, product_id)", ""),
    ]),
    ("delivery_areas", "Metro Manila zones and fees.", [
        ("id", "INT PK"), ("slug", "VARCHAR(50)"), ("name", "VARCHAR(80)"),
        ("fee", "DECIMAL(10,2)"), ("is_core", "BOOL"),
    ]),
    ("delivery_slots", "9AM–12NN, 12NN–4PM, 4PM–8PM.", [
        ("id", "INT PK"), ("slug", "VARCHAR(50)"), ("name", "VARCHAR(80)"),
        ("start_time", "TIME"), ("end_time", "TIME"), ("sort_order", "INT"),
    ]),
    ("promo_codes", "e.g. SARIWA10 = 10% off.", [
        ("id", "INT PK"), ("code", "VARCHAR(40) UNIQUE"), ("discount_percent", "INT"),
        ("is_active", "BOOL"), ("description", "VARCHAR(160)"),
    ]),
    ("carts", "Session or user basket.", [
        ("id", "INT PK"), ("user_id", "FK users NULL"), ("session_id", "VARCHAR(64) UNIQUE"),
        ("promo_code_id", "FK promo_codes"), ("created_at", "DATETIME"), ("updated_at", "DATETIME"),
    ]),
    ("cart_items", "Lines in a live cart.", [
        ("id", "INT PK"), ("cart_id", "FK carts"), ("product_id", "FK products"),
        ("size_id", "FK product_sizes"), ("quantity", "INT"),
        ("UNIQUE(cart_id, product_id, size_id)", ""),
    ]),
    ("orders", "Placed checkout snapshot.", [
        ("id", "INT PK"), ("order_number", "VARCHAR(20) UNIQUE"), ("user_id", "FK users NULL"),
        ("guest_email", "VARCHAR(255)"), ("status", "VARCHAR(30)"),
        ("recipient_name / phone / address", "required"),
        ("area_id", "FK delivery_areas"), ("delivery_date", "DATE"),
        ("slot_id", "FK delivery_slots"), ("gift_message", "VARCHAR(140)"),
        ("anonymous", "BOOL"), ("sender_name", "VARCHAR(160)"),
        ("payment_method", "cod | gcash | card"), ("payment_status", "pending | paid"),
        ("subtotal / delivery_fee / discount / total", "DECIMAL(10,2)"),
        ("promo_code_id", "FK promo_codes"), ("created_at", "DATETIME"),
    ]),
    ("order_items", "Frozen product name, size, price, qty.", [
        ("id", "INT PK"), ("order_id", "FK orders"), ("product_id", "FK products"),
        ("size_id", "FK product_sizes"), ("product_name", "VARCHAR(160)"),
        ("size_name", "VARCHAR(80)"), ("unit_price", "DECIMAL(10,2)"), ("quantity", "INT"),
    ]),
    ("contact_messages", "Inbound notes from the contact page.", [
        ("id", "INT PK"), ("name", "VARCHAR(160)"), ("email", "VARCHAR(255)"),
        ("phone", "VARCHAR(30)"), ("topic", "VARCHAR(80)"), ("message", "TEXT"),
        ("created_at", "DATETIME"),
    ]),
]


def table_box(c, x, y, w, h, title, color=FOREST):
    rounded_rect(c, x, y, w, h, 5, WHITE, color, 1.2)
    rounded_rect(c, x, y + h - 8 * mm, w, 8 * mm, 5, color)
    # square off bottom of header
    c.setFillColor(color)
    c.rect(x, y + h - 8 * mm, w, 4 * mm, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Times-Bold", 8)
    c.drawCentredString(x + w / 2, y + h - 5.5 * mm, title)


def write_schema():
    path = DOCS / "sariwa-database-schema.pdf"
    width, height = landscape(A4)
    c = canvas.Canvas(str(path), pagesize=landscape(A4))
    header(c, width, height, "Database Schema", "Tables, columns, and relationships  ·  MySQL / InnoDB / utf8mb4")

    # ER diagram
    c.setFillColor(FOREST)
    c.setFont("Times-Bold", 12)
    c.drawString(18 * mm, height - 38 * mm, "Entity-relationship overview")

    boxes = {
        "users": (20, 92, 38, 28),
        "products": (78, 118, 42, 32),
        "occasions": (138, 132, 36, 22),
        "flower_types": (138, 102, 36, 22),
        "product_sizes": (188, 128, 40, 24),
        "product_images": (188, 98, 40, 24),
        "reviews": (78, 82, 38, 22),
        "favorites": (22, 58, 36, 22),
        "carts": (78, 48, 38, 24),
        "cart_items": (128, 48, 38, 24),
        "orders": (178, 52, 42, 32),
        "order_items": (230, 58, 40, 24),
        "delivery_areas": (178, 22, 40, 20),
        "delivery_slots": (230, 22, 40, 20),
        "promo_codes": (128, 18, 36, 20),
        "contact_messages": (20, 22, 42, 22),
    }

    # relationship lines first
    def center(name):
        x, y, w, h = boxes[name]
        return (x + w / 2) * mm, (y + h / 2) * mm

    links = [
        ("users", "favorites"), ("users", "carts"), ("users", "orders"), ("users", "reviews"),
        ("products", "reviews"), ("products", "favorites"), ("products", "product_sizes"),
        ("products", "product_images"), ("products", "occasions"), ("products", "flower_types"),
        ("products", "cart_items"), ("carts", "cart_items"), ("carts", "promo_codes"),
        ("orders", "order_items"), ("orders", "delivery_areas"), ("orders", "delivery_slots"),
        ("orders", "promo_codes"), ("order_items", "products"),
    ]
    c.setStrokeColor(SAGE)
    c.setLineWidth(0.8)
    for a, b in links:
        x1, y1 = center(a)
        x2, y2 = center(b)
        c.line(x1, y1, x2, y2)

    for name, (x, y, w, h) in boxes.items():
        color = ROSE if name in {"orders", "order_items"} else FOREST
        table_box(c, x * mm, y * mm, w * mm, h * mm, name.replace("_", " "), color)

    c.setFillColor(FOREST_SOFT)
    c.setFont("Times-Italic", 8)
    c.drawString(18 * mm, 14 * mm, "Cardinality: users 1—N carts/orders/reviews/favorites; products 1—N sizes/images/reviews; products N—N occasions; carts 1—N items; orders 1—N items.")

    # Page 2+ table dictionary
    c.showPage()
    header(c, width, height, "Table dictionary", "Columns and keys for each MySQL table")

    col_w = (width - 40 * mm) / 2
    x_positions = [18 * mm, 18 * mm + col_w + 4 * mm]
    y = height - 40 * mm
    col = 0

    for name, blurb, columns in TABLES:
        block_h = 11 * mm + 4.2 * mm * len([c for c in columns if c[1]])
        if y - block_h < 18 * mm:
            if col == 0:
                col = 1
                y = height - 40 * mm
            else:
                c.showPage()
                header(c, width, height, "Table dictionary (continued)", "Columns and keys for each MySQL table")
                col = 0
                y = height - 40 * mm
        x = x_positions[col]
        rounded_rect(c, x, y - block_h, col_w, block_h, 5, WHITE, CREAM_DEEP)
        c.setFillColor(FOREST)
        c.setFont("Times-Bold", 10)
        c.drawString(x + 4 * mm, y - 6 * mm, name)
        c.setFillColor(FOREST_SOFT)
        c.setFont("Times-Italic", 8)
        c.drawString(x + 4 * mm, y - 10 * mm, blurb)
        text_y = y - 15 * mm
        for field, typ in columns:
            if not typ:
                continue
            c.setFillColor(FOREST)
            c.setFont("Courier", 7.5)
            c.drawString(x + 4 * mm, text_y, field)
            c.setFillColor(SAGE)
            c.setFont("Times-Roman", 7.5)
            c.drawRightString(x + col_w - 4 * mm, text_y, typ)
            text_y -= 4.2 * mm
        y -= block_h + 4 * mm

    c.showPage()
    header(c, width, height, "Notes & constraints", "How the schema supports the shop")
    notes = [
        "Engine: MySQL InnoDB, character set utf8mb4. Created by backend/scripts/seed.py via SQLAlchemy.",
        "Money is DECIMAL(10,2) in Philippine pesos. Promo discount is a percent on bouquet subtotal, not delivery.",
        "Guest checkout stores guest_email on orders and leaves user_id NULL. Session carts use X-Session-Id.",
        "On sign-in, a session cart merges into the user's cart (matching product_id + size_id quantities combine).",
        "order_items freeze product_name, size_name, and unit_price so later catalog edits do not rewrite history.",
        "Same-day rule is application logic (Asia/Manila, 15:00 cutoff), not a database constraint.",
        "product_occasions is the associative table for the home/shop moment filters.",
        "Favorites require a registered user. Reviews in the seed data belong to demo customers.",
        "Demo promo: SARIWA10. Demo login:  regina@example.com / sariwa123.",
        "Relationships are enforced with ForeignKey columns; unique constraints prevent duplicate cart lines and duplicate favorites.",
    ]
    y = height - 44 * mm
    for i, note in enumerate(notes, 1):
        rounded_rect(c, 18 * mm, y - 16 * mm, width - 36 * mm, 18 * mm, 5, WHITE, CREAM_DEEP)
        c.setFillColor(ROSE)
        c.setFont("Times-Bold", 10)
        c.drawString(24 * mm, y - 7 * mm, f"{i:02d}")
        c.setFillColor(FOREST)
        c.setFont("Times-Roman", 10)
        text = c.beginText(34 * mm, y - 7 * mm)
        text.setLeading(13)
        for line in _wrap(note, 120):
            text.textLine(line)
        c.drawText(text)
        y -= 20 * mm

    c.save()
    print(f"Wrote {path}")


if __name__ == "__main__":
    write_use_case()
    write_schema()
