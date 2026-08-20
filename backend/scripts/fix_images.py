"""Repoint product photos that now 404 on Unsplash, without re-seeding the database."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal  # noqa: E402
from app.models import Product, ProductImage  # noqa: E402

REPLACEMENTS = {
    ("sunny-kalog", 1): "photo-1490750967868-88aa4486c946",
    ("simpleng-mahal", 1): "photo-1582794543139-8ac9cb0f7b11",
    ("simpleng-mahal", 2): "photo-1519378058457-4c29a0a2efac",
    ("masayang-kaarawan", 0): "photo-1526047932273-341f2a7631f9",
    ("liwanag", 0): "photo-1597848212624-a19eb35e2651",
    ("liwanag", 1): "photo-1490750967868-88aa4486c946",
    ("unang-tingin", 0): "photo-1582794543139-8ac9cb0f7b11",
    ("tuwang-tuwa", 1): "photo-1508610048659-a06b669e3321",
}
TEMPLATE = "https://images.unsplash.com/{photo}?auto=format&fit=crop&w=1200&q=80"


def main() -> None:
    db = SessionLocal()
    try:
        changed = 0
        for (slug, position), photo in REPLACEMENTS.items():
            product = db.query(Product).filter(Product.slug == slug).one_or_none()
            if product is None:
                print("skip: no product " + slug)
                continue
            images = (
                db.query(ProductImage)
                .filter(ProductImage.product_id == product.id)
                .order_by(ProductImage.sort_order, ProductImage.id)
                .all()
            )
            if position >= len(images):
                print("skip: {} has no image {}".format(slug, position))
                continue
            images[position].url = TEMPLATE.format(photo=photo)
            changed += 1
        db.commit()
        print("updated {} product images".format(changed))
    finally:
        db.close()


if __name__ == "__main__":
    main()
