# 🛍️ Jules Online Shop Backend

Backend for a client e-commerce project using Django and Django REST Framework (DRF).

---

## 📚 Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Project](#running-the-project)
- [Project Structure](#project-structure)
- [Environment Variables](#environment-variables)
- [Contributing](#contributing)
- [License](#license)

---

## Project Overview

This project is the backend for **Jules Online Shop**, an e-commerce platform that supports:

- User authentication and management
- Product catalog with categories and images
- Shopping cart management
- Order management and order history
- Payment processing with transaction tracking

Built with Django and Django REST Framework, designed to integrate seamlessly with a React frontend.

---

## Features

- **Users**: Custom user model with email, phone number, and addresses
- **Catalog**: Products, categories, and multiple product images
- **Cart**: Session-based shopping cart with multiple items
- **Orders**: Checkout process and complete order history
- **Payments**: Tracks transactions, status, and timestamps
- **JWT Authentication**: Secure token-based authentication

---

## Tech Stack

- Python 3.11
- Django 4.2
- Django REST Framework 3.15
- Pillow (image handling)
- `django-cors-headers` (frontend integration)
- DRF Simple JWT (authentication)
- Dev Tools: `black`, `isort`, `flake8`

---

## Getting Started

### Prerequisites

- Python 3.11+ installed
- Poetry installed ([Basic usage guide](https://python-poetry.org/docs/basic-usage/))

### 📦 Installation

Clone the repository:

```bash
git clone git@github.com:Jules-Online-Ecommerce-Shop/jules-online-shop-backend.git
cd jules-online-shop-backend
```

Install dependencies:

```bash
poetry install --no-root
```

Activate virtual environment (optional):

```bash
poetry env activate
```

---

### 🏃 Running the Project

Apply migrations:

```bash
python manage.py migrate
```

Create a superuser:

```bash
python manage.py createsuperuser
```

Run the development server:

```bash
python manage.py runserver
```

API available at:  
**http://127.0.0.1:8000/**

---

## Project Structure

```text
jules-online-shop-backend/
├─ backend/           # Django project settings
├─ users/             # User management
├─ catalog/           # Product catalog
├─ cart/              # Shopping cart
├─ orders/            # Order management
├─ payments/          # Payment transactions
├─ pyproject.toml     # Poetry dependency file
├─ poetry.lock        # Locked dependencies
├─ manage.py          # Django management commands
└─ README.md
```

---

## Environment Variables

Create a `.env` file in the root directory:

```env
cp .env.example .env
```

Use `python-decouple` to load these variables in Django.
