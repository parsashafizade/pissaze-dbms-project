# Pissaze E-Commerce CLI

A simple command-line e-commerce application built with **Python** and
**PostgreSQL** as an academic database project.

## Features

- User registration and login
- Product browsing
- Shopping cart management
- Checkout and payment
- Wallet balance
- Promo codes
- VIP membership
- Hardware compatibility checks
- Purchase history
- Referral system

## Requirements

- Python 3.9 or newer
- PostgreSQL

## Installation

### 1. Create the database

Create a PostgreSQL database named:

```text
pisaz
```

### 2. Configure the connection

Open `db_connection.py` and update:

```python
DB_PARAMS = {
    "host": "localhost",
    "database": "pisaz",
    "user": "YOUR_POSTGRES_USER",
    "password": "YOUR_POSTGRES_PASSWORD"
}
```

Do not publish a real password in a public repository.

### 3. Create a virtual environment

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the application

```bash
python main.py
```

The application creates the required tables and inserts sample products when
it starts.

## Project Files

- `main.py` — application entry point
- `db_connection.py` — PostgreSQL connection
- `tables.py` — database table creation
- `products.py` — product operations
- `cart_management.py` — shopping cart and checkout
- `payment.py` — wallet and payment operations
- `promo_codes.py` — discount codes
- `vip.py` — VIP membership
- `compatibility.py` — hardware compatibility checks
- `purchase_history.py` — order history
- `user_management.py` — registration, login, and profiles

## Academic Context

Developed as a Database Systems project in the Computer Engineering program at
Bu-Ali Sina University.

## Author

Parsa Shafizade
