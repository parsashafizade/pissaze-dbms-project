#!/usr/bin/env python3
import logging

# Compatibility rules: key tuples and corresponding table/column names.
compatibility_rules = {
    ("CPU", "Cooler"): ("CpuCoolerCompatibility", "CpuId", "CoolerId"),
    ("CPU", "Motherboard"): ("CpuMotherboardCompatibility", "CpuId", "MotherboardId"),
    ("Motherboard", "RAM"): ("RamMotherboardCompatibility", "MotherboardId", "RamId"),
    ("Motherboard", "GPU"): ("GpuMotherboardCompatibility", "MotherboardId", "GpuId"),
    ("Motherboard", "SSD"): ("SsdMotherboardCompatibility", "MotherboardId", "SsdId"),
    ("GPU", "PSU"): ("GpuPsuCompatibility", "GpuId", "PowerSupplyId")
}

def is_product_compatible(conn, available_prod, cart_items):
    available_id = int(available_prod[0])
    available_cat = available_prod[3]
    cur = conn.cursor()
    for cart_item in cart_items:
        cart_prod_id = int(cart_item[0])
        cart_cat = cart_item[1]
        rule = None
        if (cart_cat, available_cat) in compatibility_rules:
            rule = compatibility_rules[(cart_cat, available_cat)]
            val1 = cart_prod_id
            val2 = available_id
        elif (available_cat, cart_cat) in compatibility_rules:
            rule = compatibility_rules[(available_cat, cart_cat)]
            val1 = available_id
            val2 = cart_prod_id
        if rule:
            table, col1, col2 = rule
            query = f'SELECT 1 FROM "{table}" WHERE "{col1}" = %s AND "{col2}" = %s'
            cur.execute(query, (val1, val2))
            if not cur.fetchone():
                cur.close()
                return False
    cur.close()
    return True

def get_compatible_products(conn, customer_id, cart_number, locked_number):
    """Retrieve products compatible with items in the cart."""
    try:
        cur = conn.cursor()
        cur.execute('SELECT "Id", "Brand", "Model", "Category", "CurrentPrice", "StockCount" FROM "Product"')
        all_products = cur.fetchall()
        cur.close()
        from cart_management import get_cart_items  # avoid circular import issues
        cart_items = get_cart_items(conn, customer_id, cart_number, locked_number)
        if cart_items:
            compatible = [prod for prod in all_products if is_product_compatible(conn, prod, cart_items)]
            return sorted(compatible, key=lambda prod: (prod[3], prod[1], prod[2]))
        else:
            return sorted(all_products, key=lambda prod: (prod[3], prod[1], prod[2]))
    except Exception as e:
        logging.error(f"Error in retrieving compatible products: {e}")
        return []

def check_compatibility(conn):
    try:
        prod_id1 = input("Enter first Product ID: ")
        prod_id2 = input("Enter second Product ID: ")
        cur = conn.cursor()
        cur.execute('SELECT "Category", "Brand", "Model" FROM "Product" WHERE "Id" = %s', (prod_id1,))
        prod1 = cur.fetchone()
        cur.execute('SELECT "Category", "Brand", "Model" FROM "Product" WHERE "Id" = %s', (prod_id2,))
        prod2 = cur.fetchone()
        if not prod1 or not prod2:
            print("One or both products not found.")
            cur.close()
            return
        cat1, cat2 = prod1[0], prod2[0]
        rule = None
        if (cat1, cat2) in compatibility_rules:
            rule = compatibility_rules[(cat1, cat2)]
            val1, val2 = prod_id1, prod_id2
        elif (cat2, cat1) in compatibility_rules:
            rule = compatibility_rules[(cat2, cat1)]
            val1, val2 = prod_id2, prod_id1
        if rule:
            table, col1, col2 = rule
            query = f'SELECT 1 FROM "{table}" WHERE "{col1}" = %s AND "{col2}" = %s'
            cur.execute(query, (val1, val2))
            if cur.fetchone():
                print("Products are compatible.")
            else:
                print("Products are NOT compatible.")
        else:
            print("No compatibility rules between these product categories.")
        cur.close()
    except Exception as e:
        logging.error(f"Error in checking compatibility: {e}")
        print("Error in checking compatibility:", e)
