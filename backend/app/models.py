from datetime import datetime, time

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(30))
    role = Column(String(20), nullable=False, default="customer")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    carts = relationship("Cart", back_populates="user")
    orders = relationship("Order", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")


class Occasion(Base):
    __tablename__ = "occasions"

    id = Column(Integer, primary_key=True)
    slug = Column(String(50), unique=True, nullable=False)
    name = Column(String(80), nullable=False)
    icon = Column(String(80), nullable=False)
    sort_order = Column(Integer, nullable=False, default=0)

    products = relationship("ProductOccasion", back_populates="occasion")


class FlowerType(Base):
    __tablename__ = "flower_types"

    id = Column(Integer, primary_key=True)
    slug = Column(String(50), unique=True, nullable=False)
    name = Column(String(80), nullable=False)

    products = relationship("Product", back_populates="flower_type")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    slug = Column(String(120), unique=True, nullable=False)
    name = Column(String(160), nullable=False)
    short_description = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    flower_type_id = Column(Integer, ForeignKey("flower_types.id"), nullable=False)
    featured = Column(Boolean, nullable=False, default=False)
    same_day_eligible = Column(Boolean, nullable=False, default=True)
    color_palette = Column(String(120), nullable=False)
    included_text = Column(Text, nullable=False)
    delivery_text = Column(Text, nullable=False)
    care_text = Column(Text, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    sort_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    flower_type = relationship("FlowerType", back_populates="products")
    sizes = relationship("ProductSize", back_populates="product", cascade="all, delete-orphan")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    occasions = relationship("ProductOccasion", back_populates="product", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")


class ProductSize(Base):
    __tablename__ = "product_sizes"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    name = Column(String(80), nullable=False)
    stem_count = Column(Integer)
    price = Column(Numeric(10, 2), nullable=False)
    compare_at_price = Column(Numeric(10, 2))
    is_default = Column(Boolean, nullable=False, default=False)

    product = relationship("Product", back_populates="sizes")


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    url = Column(String(500), nullable=False)
    alt = Column(String(160), nullable=False)
    sort_order = Column(Integer, nullable=False, default=0)

    product = relationship("Product", back_populates="images")


class ProductOccasion(Base):
    __tablename__ = "product_occasions"
    __table_args__ = (UniqueConstraint("product_id", "occasion_id"),)

    product_id = Column(Integer, ForeignKey("products.id"), primary_key=True)
    occasion_id = Column(Integer, ForeignKey("occasions.id"), primary_key=True)

    product = relationship("Product", back_populates="occasions")
    occasion = relationship("Occasion", back_populates="products")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    product = relationship("Product", back_populates="reviews")
    user = relationship("User", back_populates="reviews")


class Favorite(Base):
    __tablename__ = "favorites"
    __table_args__ = (UniqueConstraint("user_id", "product_id"),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    user = relationship("User", back_populates="favorites")
    product = relationship("Product")


class DeliveryArea(Base):
    __tablename__ = "delivery_areas"

    id = Column(Integer, primary_key=True)
    slug = Column(String(50), unique=True, nullable=False)
    name = Column(String(80), nullable=False)
    fee = Column(Numeric(10, 2), nullable=False)
    is_core = Column(Boolean, nullable=False, default=True)


class DeliverySlot(Base):
    __tablename__ = "delivery_slots"

    id = Column(Integer, primary_key=True)
    slug = Column(String(50), unique=True, nullable=False)
    name = Column(String(80), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    sort_order = Column(Integer, nullable=False, default=0)


class PromoCode(Base):
    __tablename__ = "promo_codes"

    id = Column(Integer, primary_key=True)
    code = Column(String(40), unique=True, nullable=False)
    discount_percent = Column(Integer, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    description = Column(String(160))


class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(String(64), unique=True)
    promo_code_id = Column(Integer, ForeignKey("promo_codes.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="carts")
    promo_code = relationship("PromoCode")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")


class CartItem(Base):
    __tablename__ = "cart_items"
    __table_args__ = (UniqueConstraint("cart_id", "product_id", "size_id"),)

    id = Column(Integer, primary_key=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    size_id = Column(Integer, ForeignKey("product_sizes.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)

    cart = relationship("Cart", back_populates="items")
    product = relationship("Product")
    size = relationship("ProductSize")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    order_number = Column(String(20), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    guest_email = Column(String(255))
    status = Column(String(30), nullable=False, default="confirmed")
    recipient_name = Column(String(160), nullable=False)
    recipient_phone = Column(String(30), nullable=False)
    address = Column(String(255), nullable=False)
    area_id = Column(Integer, ForeignKey("delivery_areas.id"), nullable=False)
    delivery_date = Column(Date, nullable=False)
    slot_id = Column(Integer, ForeignKey("delivery_slots.id"), nullable=False)
    gift_message = Column(String(140))
    anonymous = Column(Boolean, nullable=False, default=False)
    sender_name = Column(String(160))
    payment_method = Column(String(20), nullable=False)
    payment_status = Column(String(20), nullable=False, default="pending")
    subtotal = Column(Numeric(10, 2), nullable=False)
    delivery_fee = Column(Numeric(10, 2), nullable=False)
    discount = Column(Numeric(10, 2), nullable=False, default=0)
    total = Column(Numeric(10, 2), nullable=False)
    promo_code_id = Column(Integer, ForeignKey("promo_codes.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    user = relationship("User", back_populates="orders")
    area = relationship("DeliveryArea")
    slot = relationship("DeliverySlot")
    promo_code = relationship("PromoCode")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    size_id = Column(Integer, ForeignKey("product_sizes.id"))
    product_name = Column(String(160), nullable=False)
    size_name = Column(String(80), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")


class ContactMessage(Base):
    __tablename__ = "contact_messages"

    id = Column(Integer, primary_key=True)
    name = Column(String(160), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(30))
    topic = Column(String(80), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class FaqEntry(Base):
    __tablename__ = "faq_entries"

    id = Column(Integer, primary_key=True)
    slug = Column(String(50), unique=True, nullable=False)
    icon = Column(String(80), nullable=False, default="help")
    is_quick_action = Column(Boolean, nullable=False, default=False)
    sort_order = Column(Integer, nullable=False, default=0)
    question_en = Column(String(255), nullable=False)
    question_tl = Column(String(255), nullable=False)
    answer_en = Column(Text, nullable=False)
    answer_tl = Column(Text, nullable=False)
    link_url = Column(String(160))
    link_label_en = Column(String(80))
    link_label_tl = Column(String(80))
    show_options = Column(Boolean, nullable=False, default=False)

    keywords = relationship("FaqKeyword", back_populates="faq", cascade="all, delete-orphan")


class FaqKeyword(Base):
    __tablename__ = "faq_keywords"

    id = Column(Integer, primary_key=True)
    faq_id = Column(Integer, ForeignKey("faq_entries.id"), nullable=False)
    keyword = Column(String(80), nullable=False, index=True)
    language = Column(String(8), nullable=False, default="en")

    faq = relationship("FaqEntry", back_populates="keywords")
