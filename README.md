# Sariwa

A Metro Manila flower shop website. Concepts in `concepts/` are a visual reference only. This build keeps their **Fraunces + Work Sans** pairing and the cream / forest / rose palette, then uses calmer motion, real product photos, and Icons8 iOS 27 Filled icons instead of emojis.

## Stack

| Layer | Choice |
| --- | --- |
| Frontend | Angular 20 + TypeScript + SCSS |
| Backend | Python FastAPI |
| Database | MySQL |

Each screen lives in its own folder (`frontend/src/app/product-details/`, `shop/`, `cart/`, …) with matching `.ts`, `.html`, and `.scss` files.

## Run it

MySQL should already be running locally (root, no password by default).

```bash
# 1. Database + catalog
cd backend
source .venv/bin/activate
python scripts/seed.py

# 2. API  — http://127.0.0.1:8000
uvicorn app.main:app --reload --port 8000

# 3. Website  — http://localhost:4200
cd ../frontend
npm start
```

The Angular dev server proxies `/api` to port 8000.

## Demo data

- Promo: `SARIWA10` (10% off bouquets)
- Customer: `regina@example.com` / `sariwa123`
- Admin user in DB: `ivan.p@example.net` / `sariwa-admin`
- Same-day cutoff: 3:00pm Asia/Manila

## Documentation

Separate PDFs in `docs/`:

- [Use case diagram](docs/sariwa-use-case-diagram.pdf)
- [Database schema](docs/sariwa-database-schema.pdf)

Regenerate them with:

```bash
cd backend
source .venv/bin/activate
python scripts/generate_docs.py
```

Icons are Icons8 iOS 27 Filled, stored in `frontend/public/icons/`, with attribution in the footer.
