from __future__ import annotations

import random
from datetime import datetime

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload, selectinload

from ..database import get_db
from ..deps import get_current_user, get_current_user_optional, get_or_create_cart
from ..models import Cart, CartItem, DeliveryArea, DeliverySlot, Order, OrderItem, Product, User
from ..schemas import OrderIn, OrderOut
from ..services import cart_totals, default_image, money
from ..timeutil import MANILA, same_day_status

router = APIRouter(prefix="/api/orders", tags=["orders"])


def _serialize(order: Order) -> dict:
    image_by_product = {}
    for item in order.items:
        if item.product:
            image_by_product[item.product_id] = default_image(item.product)
    return {
        "order_number": order.order_number,
        "status": order.status,
        "recipient_name": order.recipient_name,
        "recipient_phone": order.recipient_phone,
        "address": order.address,
        "area_name": order.area.name,
        "delivery_date": order.delivery_date,
        "slot_name": order.slot.name,
        "gift_message": order.gift_message,
        "anonymous": order.anonymous,
        "payment_method": order.payment_method,
        "payment_status": order.payment_status,
        "subtotal": order.subtotal,
        "delivery_fee": order.delivery_fee,
        "discount": order.discount,
        "total": order.total,
        "created_at": order.created_at,
        "items": [
            {
                "product_name": item.product_name,
                "size_name": item.size_name,
                "unit_price": item.unit_price,
                "quantity": item.quantity,
                "image": image_by_product.get(item.product_id),
            }
            for item in order.items
        ],
    }


def _next_order_number(db: Session) -> str:
    for _ in range(8):
        candidate = f"SW-{random.randint(10000, 99999)}"
        if not db.query(Order).filter(Order.order_number == candidate).first():
            return candidate
    raise HTTPException(status_code=500, detail="Could not assign an order number.")


@router.post("", response_model=OrderOut)
def place_order(
    payload: OrderIn,
    db: Session = Depends(get_db),
    cart: Cart = Depends(get_or_create_cart),
    user: Optional[User] = Depends(get_current_user_optional),
):
    cart = (
        db.query(Cart)
        .options(
            selectinload(Cart.items).joinedload(CartItem.product).selectinload(Product.images),
            selectinload(Cart.items).joinedload(CartItem.size),
            joinedload(Cart.promo_code),
        )
        .filter(Cart.id == cart.id)
        .one()
    )
    if not cart.items:
        raise HTTPException(status_code=400, detail="Your cart is quiet. Add a bouquet first.")
    if payload.payment_method not in {"cod", "gcash", "card"}:
        raise HTTPException(status_code=400, detail="Choose a payment method.")
    if not user and not payload.guest_email:
        raise HTTPException(status_code=400, detail="Please leave an email so we can send your confirmation.")

    area = db.get(DeliveryArea, payload.area_id)
    slot = db.get(DeliverySlot, payload.slot_id)
    if not area or not slot:
        raise HTTPException(status_code=400, detail="Please pick a delivery area and time.")

    today = datetime.now(MANILA).date()
    if payload.delivery_date < today:
        raise HTTPException(status_code=400, detail="Delivery date can't be in the past.")
    if payload.delivery_date == today and not same_day_status()["eligible"]:
        raise HTTPException(status_code=400, detail="Same-day cutoff has passed. Please pick tomorrow.")

    totals = cart_totals(cart, money(area.fee))
    payment_status = "pending" if payload.payment_method == "cod" else "paid"
    order = Order(
        order_number=_next_order_number(db),
        user_id=user.id if user else None,
        guest_email=None if user else str(payload.guest_email),
        status="confirmed",
        recipient_name=payload.recipient_name.strip(),
        recipient_phone=payload.recipient_phone.strip(),
        address=payload.address.strip(),
        area_id=area.id,
        delivery_date=payload.delivery_date,
        slot_id=slot.id,
        gift_message=(payload.gift_message or "").strip() or None,
        anonymous=payload.anonymous,
        sender_name=None if payload.anonymous else (payload.sender_name or (user.first_name if user else None)),
        payment_method=payload.payment_method,
        payment_status=payment_status,
        subtotal=totals["subtotal"],
        delivery_fee=totals["delivery_fee"],
        discount=totals["discount"],
        total=totals["total"],
        promo_code_id=cart.promo_code_id,
    )
    db.add(order)
    db.flush()
    for item in cart.items:
        db.add(
            OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                size_id=item.size_id,
                product_name=item.product.name,
                size_name=item.size.name,
                unit_price=money(item.size.price),
                quantity=item.quantity,
            )
        )
        db.delete(item)
    cart.promo_code_id = None
    db.commit()
    order = (
        db.query(Order)
        .options(
            selectinload(Order.items).joinedload(OrderItem.product).selectinload(Product.images),
            joinedload(Order.area),
            joinedload(Order.slot),
        )
        .filter(Order.id == order.id)
        .one()
    )
    return _serialize(order)


@router.get("", response_model=list[OrderOut])
def my_orders(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    orders = (
        db.query(Order)
        .options(
            selectinload(Order.items).joinedload(OrderItem.product).selectinload(Product.images),
            joinedload(Order.area),
            joinedload(Order.slot),
        )
        .filter(Order.user_id == user.id)
        .order_by(Order.created_at.desc())
        .all()
    )
    return [_serialize(order) for order in orders]


@router.get("/{order_number}", response_model=OrderOut)
def track_order(order_number: str, db: Session = Depends(get_db)):
    order = (
        db.query(Order)
        .options(
            selectinload(Order.items).joinedload(OrderItem.product).selectinload(Product.images),
            joinedload(Order.area),
            joinedload(Order.slot),
        )
        .filter(Order.order_number == order_number.upper())
        .one_or_none()
    )
    if not order:
        raise HTTPException(status_code=404, detail="We couldn't find that order number.")
    return _serialize(order)
