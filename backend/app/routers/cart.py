from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload, selectinload

from ..database import get_db
from ..deps import get_or_create_cart
from ..models import Cart, CartItem, Product, ProductSize, PromoCode
from ..schemas import CartItemIn, CartItemPatch, CartOut, PromoIn
from ..services import cart_totals

router = APIRouter(prefix="/api/cart", tags=["cart"])


def _load_cart(db: Session, cart: Cart) -> Cart:
    return (
        db.query(Cart)
        .options(
            selectinload(Cart.items).joinedload(CartItem.product).selectinload(Product.images),
            selectinload(Cart.items).joinedload(CartItem.size),
            joinedload(Cart.promo_code),
        )
        .filter(Cart.id == cart.id)
        .one()
    )


@router.get("", response_model=CartOut)
def get_cart(db: Session = Depends(get_db), cart: Cart = Depends(get_or_create_cart)):
    return cart_totals(_load_cart(db, cart))


@router.post("/items", response_model=CartOut)
def add_item(
    payload: CartItemIn,
    db: Session = Depends(get_db),
    cart: Cart = Depends(get_or_create_cart),
):
    size = db.get(ProductSize, payload.size_id)
    if not size or size.product_id != payload.product_id:
        raise HTTPException(status_code=400, detail="That size isn't available for this bouquet.")
    existing = (
        db.query(CartItem)
        .filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == payload.product_id,
            CartItem.size_id == payload.size_id,
        )
        .first()
    )
    if existing:
        existing.quantity = min(20, existing.quantity + payload.quantity)
    else:
        db.add(
            CartItem(
                cart_id=cart.id,
                product_id=payload.product_id,
                size_id=payload.size_id,
                quantity=payload.quantity,
            )
        )
    db.commit()
    return cart_totals(_load_cart(db, cart))


@router.patch("/items/{item_id}", response_model=CartOut)
def update_item(
    item_id: int,
    payload: CartItemPatch,
    db: Session = Depends(get_db),
    cart: Cart = Depends(get_or_create_cart),
):
    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not in cart.")
    item.quantity = payload.quantity
    db.commit()
    return cart_totals(_load_cart(db, cart))


@router.delete("/items/{item_id}", response_model=CartOut)
def remove_item(
    item_id: int,
    db: Session = Depends(get_db),
    cart: Cart = Depends(get_or_create_cart),
):
    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not in cart.")
    db.delete(item)
    db.commit()
    return cart_totals(_load_cart(db, cart))


@router.post("/promo", response_model=CartOut)
def apply_promo(
    payload: PromoIn,
    db: Session = Depends(get_db),
    cart: Cart = Depends(get_or_create_cart),
):
    code = payload.code.strip().upper()
    promo = db.query(PromoCode).filter(PromoCode.code == code, PromoCode.is_active.is_(True)).first()
    if not promo:
        raise HTTPException(status_code=400, detail="That code doesn't look right. Double-check and try again.")
    cart.promo_code_id = promo.id
    db.commit()
    return cart_totals(_load_cart(db, cart))
