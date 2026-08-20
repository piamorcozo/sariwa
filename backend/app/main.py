from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import auth, cart, catalog, chat, contact, orders, products

app = FastAPI(title="Sariwa", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
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
