#!/usr/bin/env python3
import logging
from decimal import Decimal
from cart_management import get_cart_items  

def populate_sample_products(conn):
    try:
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM "Product"')
        count = cur.fetchone()[0]
        if count > 0:
            cur.close()
            return

        sample_data = {
            "CPU": [
                ("Intel Core i5-11400", "i5-11400", 180, 40),
                ("Intel Core i7-11700K", "i7-11700K", 300, 50),
                ("AMD Ryzen 5 5600X", "Ryzen5-5600X", 220, 60),
                ("AMD Ryzen 7 5800X", "Ryzen7-5800X", 320, 50),
                ("Intel Core i9-11900K", "i9-11900K", 500, 30)
            ],
            "Cooler": [
                ("Cooler Master Hyper 212 EVO", "Hyper 212 EVO", 50, 100),
                ("Noctua NH-U12S", "NH-U12S", 90, 80),
                ("be quiet! Dark Rock Pro 4", "Dark Rock Pro 4", 85, 70),
                ("Corsair Hydro Series H100i", "H100i", 120, 60),
                ("NZXT Kraken X63", "Kraken X63", 130, 50)
            ],
            "Motherboard": [
                ("ASUS ROG Strix Z490-E", "ROG Strix Z490-E", 200, 70),
                ("MSI MPG B550 Gaming Plus", "MPG B550 Gaming Plus", 150, 65),
                ("Gigabyte Aorus X570", "Aorus X570", 220, 80),
                ("ASRock B450M Steel Legend", "B450M Steel Legend", 120, 90),
                ("ASUS Prime B460M-A", "Prime B460M-A", 130, 75)
            ],
            "RAM": [
                ("Corsair Vengeance LPX 16GB", "Vengeance LPX 16GB", 80, 200),
                ("G.Skill Ripjaws V 16GB", "Ripjaws V 16GB", 90, 180),
                ("Kingston HyperX Fury 16GB", "HyperX Fury 16GB", 75, 190),
                ("Crucial Ballistix 16GB", "Ballistix 16GB", 70, 210),
                ("Team T-Force Delta RGB 16GB", "Delta RGB 16GB", 85, 220)
            ],
            "GPU": [
                ("NVIDIA GeForce RTX 3060", "RTX 3060", 400, 40),
                ("NVIDIA GeForce RTX 3070", "RTX 3070", 500, 30),
                ("AMD Radeon RX 6600 XT", "RX 6600 XT", 480, 35),
                ("AMD Radeon RX 6700 XT", "RX 6700 XT", 550, 25),
                ("NVIDIA GeForce RTX 3080", "RTX 3080", 700, 20)
            ],
            "SSD": [
                ("Samsung 970 EVO Plus 500GB", "970 EVO Plus 500GB", 80, 100),
                ("Samsung 980 PRO 1TB", "980 PRO 1TB", 120, 80),
                ("WD Black SN750 500GB", "SN750 500GB", 75, 90),
                ("Crucial MX500 1TB", "MX500 1TB", 110, 85),
                ("Kingston A2000 1TB", "A2000 1TB", 100, 95)
            ],
            "PSU": [
                ("Corsair RM650x", "RM650x", 80, 100),
                ("EVGA SuperNOVA 650 G5", "650 G5", 90, 90),
                ("Seasonic Focus GX-650", "Focus GX-650", 85, 85),
                ("Cooler Master MWE Gold 650", "MWE Gold 650", 95, 75),
                ("Thermaltake Toughpower Grand 650W", "Toughpower 650W", 75, 110)
            ],
            "HDD": [
                ("Seagate Barracuda 2TB", "Barracuda 2TB", 80, 50),
                ("WD Blue 1TB", "WD Blue 1TB", 50, 60),
                ("Seagate IronWolf 4TB", "IronWolf 4TB", 150, 40),
                ("Toshiba X300 4TB", "X300 4TB", 140, 30),
                ("WD Black 6TB", "WD Black 6TB", 200, 20)
            ],
            "Case": [
                ("NZXT H510", "H510", 70, 100),
                ("Corsair Carbide Series 275R", "275R", 80, 90),
                ("Cooler Master MasterBox NR600", "NR600", 60, 110),
                ("Fractal Design Meshify C", "Meshify C", 75, 95),
                ("Phanteks Eclipse P400A", "P400A", 85, 80)
            ]
        }
        prod_ids = {cat: [] for cat in sample_data}
        for category, products in sample_data.items():
            for prod in products:
                brand, model, price, stock = prod
                cur.execute(
                    'INSERT INTO "Product" ("Brand", "Model", "Category", "CurrentPrice", "StockCount") VALUES (%s, %s, %s, %s, %s) RETURNING "Id"',
                    (brand, model, category, price, stock)
                )
                prod_id = cur.fetchone()[0]
                prod_ids[category].append(prod_id)
        # Insert compatibility records
        compatibility_info = {
            ("CPU", "Cooler"): ("CpuId", "CoolerId"),
            ("CPU", "Motherboard"): ("CpuId", "MotherboardId"),
            ("Motherboard", "RAM"): ("MotherboardId", "RamId"),
            ("Motherboard", "GPU"): ("MotherboardId", "GpuId"),
            ("Motherboard", "SSD"): ("MotherboardId", "SsdId"),
            ("GPU", "PSU"): ("GpuId", "PowerSupplyId")
        }
        compatibility_tables = {
            ("CPU", "Cooler"): "CpuCoolerCompatibility",
            ("CPU", "Motherboard"): "CpuMotherboardCompatibility",
            ("Motherboard", "RAM"): "RamMotherboardCompatibility",
            ("Motherboard", "GPU"): "GpuMotherboardCompatibility",
            ("Motherboard", "SSD"): "SsdMotherboardCompatibility",
            ("GPU", "PSU"): "GpuPsuCompatibility"
        }
        for key, (col1, col2) in compatibility_info.items():
            table = compatibility_tables[key]
            cat1, cat2 = key
            for id1 in prod_ids[cat1]:
                for id2 in prod_ids[cat2]:
                    cur.execute(
                        f'INSERT INTO "{table}" ("{col1}", "{col2}") VALUES (%s, %s)',
                        (id1, id2)
                    )
        conn.commit()
        cur.close()
        logging.info("Sample products and compatibility records inserted successfully.")
    except Exception as e:
        conn.rollback()
        logging.error(f"Error populating sample products: {e}")
        print("Error populating sample products:", e)

def view_all_products(conn):
    """Display all products (guest view) sorted by Category, Brand, then Model."""
    try:
        cur = conn.cursor()
        cur.execute('SELECT "Id", "Brand", "Model", "Category", "CurrentPrice", "StockCount" FROM "Product"')
        products = cur.fetchall()
        cur.close()
        products_sorted = sorted(products, key=lambda prod: (prod[3], prod[1], prod[2]))
        print("All Products:")
        for prod in products_sorted:
            print(f"Category: {prod[3]} | Brand: {prod[1]} | Model: {prod[2]} | ID: {prod[0]} | Price: {prod[4]} | Stock: {prod[5]}")
    except Exception as e:
        logging.error(f"Error in viewing all products: {e}")
        print("Error in viewing all products:", e)

def view_products(conn, customer_id, cart_number, locked_number):
    """Display products compatible with the current cart."""
    try:
        from compatibility import get_compatible_products  # import here to avoid circular dependencies
        products = get_compatible_products(conn, customer_id, cart_number, locked_number)
        if products:
            print("Available Products (compatible with your cart):")
            for prod in products:
                print(f"Category: {prod[3]} | Brand: {prod[1]} | Model: {prod[2]} | ID: {prod[0]} | Price: {prod[4]} | Stock: {prod[5]}")
        else:
            print("No compatible products found.")
    except Exception as e:
        logging.error(f"Error in viewing products: {e}")
        print("Error in viewing products:", e)

def add_product_to_cart(conn, customer_id, cart_number, locked_number):
    """Add a product to the cart after checking stock and compatibility."""
    try:
        cur = conn.cursor()
        cur.execute('SELECT "CartStatus" FROM "Cart" WHERE "CartNumber" = %s', (cart_number,))
        state = cur.fetchone()[0]
        if state != "normal":
            print("Cannot add items to a cart that is not in 'normal' state.")
            cur.close()
            return
        prod_id_input = input("Enter Product ID to add: ")
        product_id = int(prod_id_input)
        quantity = int(input("Enter quantity: "))
        cur.execute('SELECT "CurrentPrice", "Category", "StockCount" FROM "Product" WHERE "Id" = %s', (product_id,))
        result = cur.fetchone()
        if not result:
            print("Product not found.")
            cur.close()
            return
        current_price, prod_cat, stock = result
        if quantity > stock:
            print("Insufficient stock. Available:", stock)
            cur.close()
            return
        from compatibility import is_product_compatible
        from cart_management import get_cart_items

        cart_items = get_cart_items(conn, customer_id, cart_number, locked_number)
        available_product = (product_id, "", "", prod_cat, current_price, stock)
        if cart_items and not is_product_compatible(conn, available_product, cart_items):
            print("This product is not compatible with items in your cart.")
            cur.close()
            return
        cart_price = current_price * quantity
        cur.execute(
            'INSERT INTO "CartItem" ("Quantity", "LockedNumber", "CartPrice", "CustomerId", "ProductId", "CartNumber") VALUES (%s, %s, %s, %s, %s, %s)',
            (quantity, locked_number, cart_price, customer_id, product_id, cart_number)
        )
        conn.commit()
        cur.close()
        logging.info(f"Product {product_id} added to cart for CustomerId {customer_id}")
        print("Product added to cart successfully.")
    except Exception as e:
        conn.rollback()
        logging.error(f"Error in adding product to cart: {e}")
        print("Error in adding product to cart:", e)
