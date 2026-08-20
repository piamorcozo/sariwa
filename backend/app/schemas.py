from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class OccasionOut(BaseModel):
    id: int
    slug: str
    name: str
    icon: str

    model_config = {"from_attributes": True}


class FlowerTypeOut(BaseModel):
    id: int
    slug: str
    name: str

    model_config = {"from_attributes": True}


class ProductSizeOut(BaseModel):
    id: int
    name: str
    stem_count: Optional[int]
    price: Decimal
    compare_at_price: Optional[Decimal]
    is_default: bool

    model_config = {"from_attributes": True}


class ProductImageOut(BaseModel):
    id: int
    url: str
    alt: str

    model_config = {"from_attributes": True}


class ProductCardOut(BaseModel):
    id: int
    slug: str
    name: str
    short_description: str
    featured: bool
    same_day_eligible: bool
    color_palette: str
    default_size_id: int
    price: Decimal
    compare_at_price: Optional[Decimal] = None
    occasion: Optional[str] = None
    occasion_slugs: list[str] = []
    flower_type: str
    image: Optional[str] = None
    rating: float = 0
    review_count: int = 0
    favorited: bool = False

    model_config = {"from_attributes": True}


class ReviewOut(BaseModel):
    id: int
    rating: int
    comment: str
    author: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ProductDetailOut(ProductCardOut):
    description: str
    included_text: str
    delivery_text: str
    care_text: str
    sizes: list[ProductSizeOut]
    images: list[ProductImageOut]
    occasions: list[OccasionOut]
    reviews: list[ReviewOut] = []


class DeliveryAreaOut(BaseModel):
    id: int
    slug: str
    name: str
    fee: Decimal
    is_core: bool

    model_config = {"from_attributes": True}


class DeliverySlotOut(BaseModel):
    id: int
    slug: str
    name: str
    sort_order: int

    model_config = {"from_attributes": True}


class CartItemIn(BaseModel):
    product_id: int
    size_id: int
    quantity: int = Field(ge=1, le=20)


class CartItemPatch(BaseModel):
    quantity: int = Field(ge=1, le=20)


class PromoIn(BaseModel):
    code: str


class CartItemOut(BaseModel):
    id: int
    product_id: int
    size_id: int
    slug: str
    name: str
    size_name: str
    short_description: str
    image: Optional[str]
    color_palette: str
    unit_price: Decimal
    quantity: int
    line_total: Decimal


class CartOut(BaseModel):
    id: int
    items: list[CartItemOut]
    subtotal: Decimal
    delivery_fee: Decimal = Decimal("0")
    discount: Decimal
    total: Decimal
    promo_code: Optional[str] = None
    promo_message: Optional[str] = None


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str
    last_name: str
    phone: Optional[str] = None


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str]
    role: str

    model_config = {"from_attributes": True}


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class OrderIn(BaseModel):
    recipient_name: str
    recipient_phone: str
    address: str
    area_id: int
    delivery_date: date
    slot_id: int
    gift_message: Optional[str] = Field(default=None, max_length=140)
    anonymous: bool = False
    sender_name: Optional[str] = None
    guest_email: Optional[EmailStr] = None
    payment_method: str


class OrderItemOut(BaseModel):
    product_name: str
    size_name: str
    unit_price: Decimal
    quantity: int
    image: Optional[str] = None


class OrderOut(BaseModel):
    order_number: str
    status: str
    recipient_name: str
    recipient_phone: str
    address: str
    area_name: str
    delivery_date: date
    slot_name: str
    gift_message: Optional[str]
    anonymous: bool
    payment_method: str
    payment_status: str
    subtotal: Decimal
    delivery_fee: Decimal
    discount: Decimal
    total: Decimal
    created_at: datetime
    items: list[OrderItemOut]


class ContactIn(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    topic: str
    message: str = Field(min_length=8)


class ContactOut(BaseModel):
    ok: bool
    message: str


class SameDayOut(BaseModel):
    eligible: bool
    cutoff: str
    remaining_seconds: int
    label: str


class ChatAskIn(BaseModel):
    message: str = Field(min_length=1, max_length=500)
    intent: Optional[str] = None
    language: Optional[str] = None


class ChatLinkOut(BaseModel):
    url: str
    label: str


class ChatAskOut(BaseModel):
    reply: str
    matched: bool
    language: str
    handover: bool = False
    show_options: bool = False
    slug: Optional[str] = None
    link: Optional[ChatLinkOut] = None


class ChatOptionOut(BaseModel):
    slug: str
    icon: str
    label: str
