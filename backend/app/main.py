from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import auth, cart, catalog, chat, contact, orders, products


def _bootstrap_sqlite() -> None:
    if not settings.uses_sqlite:
        return
    from sqlalchemy.exc import SQLAlchemyError

    from .database import Base, SessionLocal, engine
    from .models import Product

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        empty = db.query(Product).first() is None
    except SQLAlchemyError:
        empty = True
    finally:
        db.close()
    if empty:
        import sys
        from pathlib import Path

        root = Path(__file__).resolve().parents[1]
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
        from scripts.seed import seed

        seed(reset=False)


@asynccontextmanager
async def lifespan(_: FastAPI):
    _bootstrap_sqlite()
    yield


app = FastAPI(title="Sariwa", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_origin_regex=r"https://.*\.onrender\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(catalog.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(auth.router)
app.include_router(contact.router)
app.include_router(chat.router)


@app.get("/api/health")
def health():
    return {"ok": True, "shop": "sariwa"}
