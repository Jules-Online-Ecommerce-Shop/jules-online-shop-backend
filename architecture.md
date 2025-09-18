# jules-online-shop-backend
Backend for Jules online shop

### E-commerce Site Architecture: A Detailed Blueprint

This document provides a comprehensive, field-by-field architectural plan for a Django-based e-commerce site. It follows the modular monolith pattern, ensuring each application is responsible for a single domain, which simplifies development, maintenance, and future scaling.

#### App Breakdown

The site is composed of five core applications, each with a specific set of responsibilities:

1.  **`users`**: Manages all user accounts, authentication, and personal information.

2.  **`catalog`**: The product database, including categories, products, and images.

3.  **`cart`**: Handles the temporary state of a user's shopping cart.

4.  **`orders`**: Manages the complete history of placed orders.

5.  **`payments`**: Records all payment transactions and their status.

#### Detailed App and Model Design

**1. `users` App**

This app is the foundation for all user-centric data.

* **`CustomUser` Model (Extends `AbstractUser`)**

    * **Purpose:** The central model for all user accounts, providing core authentication fields and a flexible base for additional information.

    * **Fields:**

        * `username`: `CharField` (Unique)

        * `email`: `EmailField` (Unique)

        * `phone_number`: `CharField` (Optional)

        * `date_of_birth`: `DateField` (Optional)

        * `is_active`, `is_staff`, `is_superuser`: `BooleanField`

        * `date_joined`: `DateTimeField`

    * **Relationships:** None (This is the primary user model for other apps to reference)

* **`Address` Model**

    * **Purpose:** Stores a user's physical addresses for shipping and billing, adapted for the Ghanaian addressing scheme.

    * **Fields:**

        * `user`: `ForeignKey` to `CustomUser` (One-to-Many: a user can have many addresses)

        * `full_name`: `CharField`

        * `street_address`: `TextField`

        * `city`: `CharField`

        * `zip_code`: `CharField`

        * `country`: `CharField`

        * `is_default_shipping`: `BooleanField`

        * `is_default_billing`: `BooleanField`

    * **Relationships:** `ForeignKey` to `CustomUser`

**2. `catalog` App**

This app is the single source of truth for all product information.

* **`Category` Model**

    * **Purpose:** Organizes products into a hierarchical structure.

    * **Fields:**

        * `name`: `CharField`

        * `slug`: `SlugField` (Unique for URLs)

        * `description`: `TextField`

        * `parent`: `ForeignKey` to `self` (Optional, for nested categories)

    * **Relationships:** `ForeignKey` to itself.

* **`Product` Model**

    * **Purpose:** The core product data, including pricing, inventory, and description.

    * **Fields:**

        * `name`: `CharField`

        * `slug`: `SlugField` (Unique for URLs)

        * `description`: `TextField`

        * `price`: `DecimalField`

        * `stock`: `PositiveIntegerField`

        * `category`: `ForeignKey` to `Category` (One-to-Many: a category can have many products)

        * `is_available`: `BooleanField`

        * `created_at`: `DateTimeField`

        * `updated_at`: `DateTimeField`

    * **Relationships:** `ForeignKey` to `Category`

* **`ProductImage` Model**

    * **Purpose:** Stores multiple images associated with a single product.

    * **Fields:**

        * `product`: `ForeignKey` to `Product` (One-to-Many: a product can have many images)

        * `image`: `ImageField`

        * `is_main`: `BooleanField` (Indicates the primary image for the product page)

    * **Relationships:** `ForeignKey` to `Product`

**3. `cart` App**

This app manages a user's session-based shopping cart.

* **`Cart` Model**

    * **Purpose:** The container for all items in a user's active shopping cart.

    * **Fields:**

        * `user`: `OneToOneField` to `CustomUser` (One-to-One: a user has only one cart)

        * `created_at`: `DateTimeField`

    * **Relationships:** `OneToOneField` to `CustomUser`

* **`CartItem` Model**

    * **Purpose:** Represents a single product and its quantity within a cart.

    * **Fields:**

        * `cart`: `ForeignKey` to `Cart` (One-to-Many: a cart can have many items)

        * `product`: `ForeignKey` to `Product` (One-to-Many: a product can be in many carts)

        * `quantity`: `PositiveIntegerField`

    * **Relationships:** `ForeignKey` to `Cart` and `ForeignKey` to `Product`

**4. `orders` App**

This app handles the checkout process and preserves a permanent record of all transactions.

* **`Order` Model**

    * **Purpose:** A record of a completed purchase.

    * **Fields:**

        * `user`: `ForeignKey` to `CustomUser` (One-to-Many: a user can have many orders)

        * `shipping_address`: `ForeignKey` to `Address`

        * `total_amount`: `DecimalField` (The final price at the time of purchase)

        * `status`: `CharField` (e.g., 'Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled')

        * `created_at`: `DateTimeField`

    * **Relationships:** `ForeignKey` to `CustomUser` and `ForeignKey` to `Address`

* **`OrderItem` Model**

    * **Purpose:** Stores a snapshot of the product details at the time of purchase. This is vital for historical accuracy.

    * **Fields:**

        * `order`: `ForeignKey` to `Order` (One-to-Many: an order can have many items)

        * `product`: `ForeignKey` to `Product` (One-to-Many: a product can be in many orders)

        * `product_name`: `CharField` (Snapshot of the name)

        * `product_price`: `DecimalField` (Snapshot of the price)

    * `quantity`: `PositiveIntegerField`

    * **Relationships:** `ForeignKey` to `Order` and `ForeignKey` to `Product`

**5. `payments` App**

This app is the record keeper for all payment attempts and their outcomes.

* **`Transaction` Model**

    * **Purpose:** Tracks each payment transaction and its status.

    * **Fields:**

        * `order`: `OneToOneField` to `Order` (One-to-One: an order has one payment transaction)

        * `transaction_id`: `CharField` (From the payment gateway)

        * `amount`: `DecimalField`

        * `status`: `CharField` (e.g., 'Pending', 'Success', 'Failed')

        * `timestamp`: `DateTimeField`

    * **Relationships:** `OneToOneField` to `Order`


```text
backend/
├─ users/
│  ├─ models.py           # CustomUser, Address
│  ├─ serializers.py      # CustomUserSerializer, AddressSerializer
│  ├─ views.py            # User registration, profile, address management
│  ├─ urls.py
│  └─ admin.py
│
├─ catalog/
│  ├─ models.py           # Category, Product, ProductImage
│  ├─ serializers.py
│  ├─ views.py            # ProductList, ProductDetail, CategoryList
│  ├─ urls.py
│  └─ admin.py
│
├─ cart/
│  ├─ models.py           # Cart, CartItem
│  ├─ serializers.py
│  ├─ views.py            # CartView, CartItemView
│  ├─ urls.py
│  └─ admin.py
│
├─ orders/
│  ├─ models.py           # Order, OrderItem
│  ├─ serializers.py
│  ├─ views.py            # OrderList, OrderDetail, CheckoutView
│  ├─ urls.py
│  └─ admin.py
│
├─ payments/
│  ├─ models.py           # Transaction
│  ├─ serializers.py
│  ├─ views.py            # PaymentCreate, PaymentStatus
│  ├─ urls.py
│  └─ admin.py
│
├─ utils/                 # Shared helpers across apps
│  ├─ validators.py
│  └─ helpers.py
│
├─ settings.py
├─ urls.py                # Root URL config
└─ wsgi.py
```
