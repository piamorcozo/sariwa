from __future__ import annotations

from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from .models import Cart, Product


def money(value) -> Decimal:
    return Decimal(value).quantize(Decimal("0.01"))


def product_rating(product: Product) -> tuple[float, int]:
    reviews = product.reviews or []
    if not reviews:
        return 0.0, 0
    total = sum(r.rating for r in reviews)
    return round(total / len(reviews), 1), len(reviews)


def default_size(product: Product):
    return next((s for s in product.sizes if s.is_default), product.sizes[0] if product.sizes else None)


def default_image(product: Product) -> Optional[str]:
    if not product.images:
        return None
    ordered = sorted(product.images, key=lambda img: img.sort_order)
    return ordered[0].url


def cart_totals(cart: Cart, delivery_fee: Decimal = Decimal("0")) -> dict:
    items = []
    subtotal = Decimal("0")
    for item in cart.items:
        price = money(item.size.price)
        line = price * item.quantity
        subtotal += line
        items.append(
            {
                "id": item.id,
                "product_id": item.product_id,
                "size_id": item.size_id,
                "slug": item.product.slug,
                "name": item.product.name,
                "size_name": item.size.name,
                "short_description": item.product.short_description,
                "image": default_image(item.product),
                "color_palette": item.product.color_palette,
                "unit_price": price,
                "quantity": item.quantity,
                "line_total": money(line),
            }
        )
    discount = money(0)
    promo_code = None
    if cart.promo_code and cart.promo_code.is_active and subtotal > 0:
        discount = money(subtotal * Decimal(cart.promo_code.discount_percent) / Decimal("100"))
        promo_code = cart.promo_code.code
    total = money(max(Decimal("0"), subtotal + delivery_fee - discount))
    return {
        "id": cart.id,
        "items": items,
        "subtotal": money(subtotal),
        "delivery_fee": money(delivery_fee),
        "discount": discount,
        "total": total,
        "promo_code": promo_code,
        "promo_message": (
            f'"{promo_code}" applied — {cart.promo_code.discount_percent}% off your bouquet.'
            if promo_code
            else None
        ),
    }


def to_card(product: Product, favorited: bool = False) -> dict:
    size = default_size(product)
    rating, count = product_rating(product)
    occasions = [link.occasion for link in product.occasions]
    return {
        "id": product.id,
        "slug": product.slug,
        "name": product.name,
        "short_description": product.short_description,
        "featured": product.featured,
        "same_day_eligible": product.same_day_eligible,
        "color_palette": product.color_palette,
        "default_size_id": size.id if size else 0,
        "price": money(size.price) if size else Decimal("0"),
        "compare_at_price": money(size.compare_at_price) if size and size.compare_at_price else None,
        "occasion": occasions[0].name if occasions else None,
        "occasion_slugs": [o.slug for o in occasions],
        "flower_type": product.flower_type.slug,
        "image": default_image(product),
        "rating": rating,
        "review_count": count,
        "favorited": favorited,
    }
