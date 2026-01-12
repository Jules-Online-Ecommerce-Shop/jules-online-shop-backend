# Jules Shop – Backend API

Production-ready **Django REST Framework (DRF)** backend for an e-commerce platform.

This repository is intended for **frontend developers**, **backend contributors**, and reviewers who want to understand how the system works and how to run it locally.

> 📌 For deeper design and system decisions, see **`architecture.md`**.

---

## Tech Stack

* **Django 5.x** + **Django REST Framework**
* **PostgreSQL (Neon)**
* **Cloudinary** (media storage & image optimization)
* **Railway** (backend hosting)
* **Whitenoise** (static files)
* **DRF Spectacular** (OpenAPI / Swagger docs)

---

## Key Features

* Product catalog with categories & images
* Optimized product listing vs detail endpoints
* Cloudinary-backed image uploads with dynamic transformations
* Django Admin (Unfold UI)
* Production-like deployment early in development

---

## 📂 Project Structure (High-Level)

```
.
├── catalog/
├── cart/
├── orders/
├── users/
├── payments/
├── utils/
├── jules_shop/
├── architecture.md
├── requirements.txt
├── requirements.dev.txt
└── README.md
```

---

## 🧑‍💻 Frontend Developers

### Base URL

```
https://jules-online-shop-backend-development.up.railway.app
```

### API Docs

* Swagger UI: `/api/v1/docs/swagger`
* OpenAPI schema: `/api/v1/schema/`

Docs are **serializer-driven** and reflect the real response structure.

### Product Listings

Listing endpoints return **summaries**, not full objects, for performance:

```json
{
  "id": 1,
  "name": "Product Name",
  "slug": "product-name",
  "price": "99.99",
  "image": {
    "url": "https://res.cloudinary.com/...",
    "alt_text": "Product image"
  }
}
```

Images are already optimized (size, format, compression).

---

## 🧑‍🔧 Backend Developers

### Environment Variables

Create a `.env` file or copy `.env.example` file:

```env
DJANGO_SECRET_KEY=...
DEBUG=True
USE_SQLITE=True

# PostgreSQL (prod)
PGDATABASE=...
PGUSER=...
PGPASSWORD=...
PGHOST=...
PGPORT=5432

# Cloudinary
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
```

---

### Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For development tools (debug toolbar, typing, testing):

```bash
pip install -r requirements-dev.txt
```

---

### Database & Fixtures

```bash
python manage.py migrate
python manage.py loaddata */fixtures/*.json
```

---

### Run Locally

```bash
python manage.py runserver
```

---

## 🖼 Media & Images

* Media files are stored on **Cloudinary**
* Database stores references only
* URLs are transformed dynamically per use-case

This avoids large payloads and keeps frontend performance fast.

---

## 🌍 Deployment

* Backend hosted on **Railway**
* PostgreSQL on **Neon**
* Environment variables managed via Railway dashboard

---

## 📄 Notes

* Debug tooling is **dev-only**
* Listing endpoints are intentionally minimal
* Admin performance tuning is ongoing

For architectural reasoning and tradeoffs, see **architecture.md**.
