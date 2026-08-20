from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload, selectinload

from ..database import get_db
from ..deps import get_current_user, get_current_user_optional
from ..models import Favorite, Product, ProductOccasion, Review, User
from ..schemas import ProductCardOut, ProductDetailOut, ReviewOut
from ..services import default_size, to_card

router = APIRouter(prefix="/api/products", tags=["products"])


def _product_query(db: Session):
    return (
        db.query(Product)
        .options(
            selectinload(Product.sizes),
            selectinload(Product.images),
            joinedload(Product.flower_type),
            selectinload(Product.occasions).joinedload(ProductOccasion.occasion),
            selectinload(Product.reviews).joinedload(Review.user),
        )
        .filter(Product.is_active.is_(True))
    )


def _favorite_ids(db: Session, user: Optional[User]) -> set:
    if not user:
        return set()
    rows = db.query(Favorite.product_id).filter(Favorite.user_id == user.id).all()
    return {row[0] for row in rows}


@router.get("", response_model=list[ProductCardOut])
def list_products(
    occasion: Optional[str] = None,
    flower_type: Optional[str] = Query(default=None, alias="type"),
    q: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    sort: str = "featured",
    featured: Optional[bool] = None,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional),
):
    products = _product_query(db).all()
    favs = _favorite_ids(db, user)
    results = []
    for product in products:
        size = default_size(product)
        if not size:
            continue
        price = float(size.price)
        slugs = [link.occasion.slug for link in product.occasions]
        if occasion and occasion != "all" and occasion not in slugs:
            continue
        if flower_type and flower_type != "all" and product.flower_type.slug != flower_type:
            continue
        if featured is True and not product.featured:
            continue
        if price_min is not None and price < price_min:
            continue
        if price_max is not None and price > price_max:
            continue
        haystack = f"{product.name} {product.short_description} {product.description}".lower()
        if q and q.lower() not in haystack:
            continue
        results.append(to_card(product, product.id in favs))

    if sort == "price-asc":
        results.sort(key=lambda item: item["price"])
    elif sort == "price-desc":
        results.sort(key=lambda item: item["price"], reverse=True)
    elif sort == "rating":
        results.sort(key=lambda item: item["rating"], reverse=True)
    else:
        results.sort(key=lambda item: (not item["featured"], item["name"]))
    return results


@router.get("/{slug}", response_model=ProductDetailOut)
def get_product(
    slug: str,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional),
):
    product = (
        _product_query(db)
        .filter(Product.slug == slug)
        .one_or_none()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Arrangement not found.")
    card = to_card(product, product.id in _favorite_ids(db, user))
    reviews = [
        ReviewOut(
            id=review.id,
            rating=review.rating,
            comment=review.comment,
            author=review.user.first_name,
            created_at=review.created_at,
        )
        for review in sorted(product.reviews, key=lambda r: r.created_at, reverse=True)
    ]
    return {
        **card,
        "description": product.description,
        "included_text": product.included_text,
        "delivery_text": product.delivery_text,
        "care_text": product.care_text,
        "sizes": product.sizes,
        "images": sorted(product.images, key=lambda img: img.sort_order),
        "occasions": [link.occasion for link in product.occasions],
        "reviews": reviews,
    }


@router.get("/{slug}/similar", response_model=list[ProductCardOut])
def similar_products(
    slug: str,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional),
):
    product = _product_query(db).filter(Product.slug == slug).one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Arrangement not found.")
    target = {link.occasion_id for link in product.occasions}
    favs = _favorite_ids(db, user)
    others = [p for p in _product_query(db).all() if p.id != product.id]
    scored = []
    for other in others:
        overlap = len(target & {link.occasion_id for link in other.occasions})
        same_type = 1 if other.flower_type_id == product.flower_type_id else 0
        scored.append((overlap * 2 + same_type, other))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [to_card(item, item.id in favs) for _, item in scored[:8]]


@router.post("/{product_id}/favorite")
def toggle_favorite(
    product_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Arrangement not found.")
    existing = (
        db.query(Favorite)
        .filter(Favorite.user_id == user.id, Favorite.product_id == product_id)
        .first()
    )
    if existing:
        db.delete(existing)
        db.commit()
        return {"favorited": False}
    db.add(Favorite(user_id=user.id, product_id=product_id))
    db.commit()
    return {"favorited": True}
