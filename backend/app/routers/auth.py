from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload, selectinload

from ..database import get_db
from ..deps import get_current_user, get_current_user_optional
from ..models import Favorite, Product, User
from ..schemas import LoginIn, RegisterIn, TokenOut, UserOut
from ..security import create_access_token, hash_password, verify_password
from ..services import to_card

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenOut)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    email = payload.email.lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="An account with that email already exists.")
    user = User(
        email=email,
        password_hash=hash_password(payload.password),
        first_name=payload.first_name.strip(),
        last_name=payload.last_name.strip(),
        phone=payload.phone,
        role="customer",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenOut(access_token=create_access_token(str(user.id)), user=user)


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Email or password doesn't match.")
    return TokenOut(access_token=create_access_token(str(user.id)), user=user)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@router.get("/favorites")
def favorites(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = (
        db.query(Favorite)
        .options(joinedload(Favorite.product).joinedload(Product.sizes))
        .filter(Favorite.user_id == user.id)
        .all()
    )
    products = []
    for row in rows:
        product = (
            db.query(Product)
            .options(
                selectinload(Product.sizes),
                selectinload(Product.images),
                joinedload(Product.flower_type),
                selectinload(Product.occasions),
                selectinload(Product.reviews),
            )
            .filter(Product.id == row.product_id)
            .first()
        )
        if product:
            products.append(to_card(product, True))
    return products
