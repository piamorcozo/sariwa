from __future__ import annotations

from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .database import get_db
from .models import Cart, User
from .security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    if not token:
        return None
    user_id = decode_access_token(token)
    if not user_id:
        return None
    return db.get(User, int(user_id))


def get_current_user(user: Optional[User] = Depends(get_current_user_optional)) -> User:
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please sign in.")
    return user


def get_or_create_cart(
    x_session_id: Optional[str] = Header(default=None, alias="X-Session-Id"),
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional),
) -> Cart:
    cart = None
    if user:
        cart = db.query(Cart).filter(Cart.user_id == user.id).first()
    if not cart and x_session_id:
        cart = db.query(Cart).filter(Cart.session_id == x_session_id).first()
        if cart and user and cart.user_id is None:
            existing = db.query(Cart).filter(Cart.user_id == user.id).first()
            if existing and existing.id != cart.id:
                _merge_carts(db, existing, cart)
                cart = existing
            else:
                cart.user_id = user.id
                db.commit()
                db.refresh(cart)
    if not cart:
        cart = Cart(user_id=user.id if user else None, session_id=x_session_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


def _merge_carts(db: Session, target: Cart, source: Cart) -> None:
    from .models import CartItem

    for item in list(source.items):
        match = next(
            (
                existing
                for existing in target.items
                if existing.product_id == item.product_id and existing.size_id == item.size_id
            ),
            None,
        )
        if match:
            match.quantity = min(20, match.quantity + item.quantity)
            db.delete(item)
        else:
            item.cart_id = target.id
    if source.promo_code_id and not target.promo_code_id:
        target.promo_code_id = source.promo_code_id
    db.delete(source)
    db.commit()
    db.refresh(target)
