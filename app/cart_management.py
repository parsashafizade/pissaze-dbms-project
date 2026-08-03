#!/usr/bin/env python3
import logging
from decimal import Decimal
from datetime import datetime, timedelta

def get_active_cart(conn, customer_id, vip=False):
    try:
        cur = conn.cursor()
        cur.execute('SELECT "CartNumber" FROM "Cart" WHERE "CustomerId" = %s AND "CartStatus" = %s ORDER BY "CartNumber" ASC LIMIT 1',
                    (customer_id, "normal"))
        result = cur.fetchone()
        if result:
            cart_number = result[0]
        else:
            cur.execute(
                'INSERT INTO "Cart" ("CartStatus", "CustomerId") VALUES (%s, %s) RETURNING "CartNumber"',
                ("normal", customer_id)
            )
            cart_number = cur.fetchone()[0]
            conn.commit()
        cur.close()
        return cart_number
    except Exception as e:
        conn.rollback()
        logging.error(f"Error in getting/creating active cart: {e}")
        print("Error in cart operation:", e)
        return None

def get_locked_cart(conn, customer_id, cart_number):
    try:
        cur = conn.cursor()
        cur.execute(
            'SELECT "LockedNumber", "TimeStamp" FROM "LockedCart" WHERE "CustomerId" = %s AND "CartNumber" = %s',
            (customer_id, cart_number)
        )
        result = cur.fetchone()
        if result:
            locked_number = result[0]
        else:
            cur.execute(
                'INSERT INTO "LockedCart" ("CustomerId", "CartNumber") VALUES (%s, %s) RETURNING "LockedNumber"',
                (customer_id, cart_number)
            )
            locked_number = cur.fetchone()[0]
            conn.commit()
        cur.close()
        return locked_number
    except Exception as e:
        conn.rollback()
        logging.error(f"Error in getting/creating locked cart: {e}")
        print("Error in cart operation:", e)
        return None

def get_cart_items(conn, customer_id, cart_number, locked_number):
    try:
        cur = conn.cursor()
        cur.execute(
            'SELECT p."Id", p."Category", ci."Quantity", ci."CartPrice" FROM "CartItem" ci JOIN "Product" p ON ci."ProductId" = p."Id" '
            'WHERE ci."CustomerId" = %s AND ci."CartNumber" = %s AND ci."LockedNumber" = %s',
            (customer_id, cart_number, locked_number)
        )
        items = cur.fetchall()
        cur.close()
        return items
    except Exception as e:
        logging.error(f"Error in retrieving cart items: {e}")
        return []

def view_cart(conn, customer_id, cart_number, locked_number):
    try:
        cur = conn.cursor()
        cur.execute(
            'SELECT ci."ProductId", p."Brand", p."Model", ci."Quantity", ci."CartPrice" '
            'FROM "CartItem" ci JOIN "Product" p ON ci."ProductId" = p."Id" '
            'WHERE ci."CustomerId" = %s AND ci."CartNumber" = %s AND ci."LockedNumber" = %s',
            (customer_id, cart_number, locked_number)
        )
        items = cur.fetchall()
        cur.close()
        if items:
            print("Your Cart Items:")
            subtotal = Decimal("0.00")
            for item in items:
                print(f"Product ID: {item[0]}, Brand: {item[1]}, Model: {item[2]}, Quantity: {item[3]}, Price: {item[4]}")
                subtotal += item[4]
            print("Subtotal:", subtotal)
            cur = conn.cursor()
            cur.execute(
                'SELECT pc."Code", pc."Amount", pc."CodeType" FROM "AppliedPromo" ap JOIN "PromoCode" pc ON ap."PromoCode" = pc."Code" '
                'WHERE ap."CustomerId" = %s AND ap."CartNumber" = %s AND ap."LockedNumber" = %s',
                (customer_id, cart_number, locked_number)
            )
            promos = cur.fetchall()
            cur.close()
            discount_total = Decimal("0.00")
            for promo in promos:
                code, amount, code_type = promo
                if code_type in ["Standard", "ReferralPercentage", "VIP"]:
                    discount = subtotal * Decimal(str(amount))
                else:
                    discount = Decimal(str(amount))
                discount_total += discount
                print(f"Applied Promo Code: {code} | Discount: {discount:.2f}")
            final_total = max(subtotal - discount_total, Decimal("0.00"))
            print("Total Discount:", discount_total)
            print("Final Total:", final_total)
        else:
            print("Your cart is empty.")
    except Exception as e:
        logging.error(f"Error in viewing cart: {e}")
        print("Error in viewing cart:", e)

def apply_promo(conn, customer_id, cart_number, locked_number):
    try:
        state = get_cart_state(conn, cart_number)
        if state != "registered":
            print("Promo code can only be applied on a registered cart.")
            return
        promo_code = int(input("Enter Promo Code (three-digit number): "))
        cur = conn.cursor()
        cur.execute(
            'SELECT * FROM "AppliedPromo" WHERE "CustomerId" = %s AND "CartNumber" = %s AND "LockedNumber" = %s AND "PromoCode" = %s',
            (customer_id, cart_number, locked_number, promo_code)
        )
        if cur.fetchone():
            print("This promo code has already been applied to your cart.")
            cur.close()
            return
        cur.execute(
            'INSERT INTO "AppliedPromo" ("PromoCode", "CustomerId", "LockedNumber", "CartNumber") VALUES (%s, %s, %s, %s)',
            (promo_code, customer_id, locked_number, cart_number)
        )
        conn.commit()
        cur.close()
        logging.info(f"Promo code {promo_code} applied for CustomerId {customer_id}")
        print("Promo code applied successfully.")
    except Exception as e:
        conn.rollback()
        logging.error(f"Error in applying promo code: {e}")
        print("Error in applying promo code:", e)

def get_cart_state(conn, cart_number):
    try:
        cur = conn.cursor()
        cur.execute('SELECT "CartStatus" FROM "Cart" WHERE "CartNumber" = %s', (cart_number,))
        state = cur.fetchone()[0]
        cur.close()
        return state
    except Exception as e:
        logging.error(f"Error retrieving cart state: {e}")
        return None

def checkout(conn, customer_id, cart_number, locked_number):
    try:
        cur = conn.cursor()
        cur.execute(
            'SELECT "ProductId", "Quantity" FROM "CartItem" WHERE "CustomerId" = %s AND "CartNumber" = %s AND "LockedNumber" = %s',
            (customer_id, cart_number, locked_number)
        )
        items = cur.fetchall()
        if not items:
            print("Your cart is empty.")
            cur.close()
            return
        subtotal = Decimal("0.00")
        for item in items:
            prod_id, qty = item
            cur.execute('SELECT "CurrentPrice" FROM "Product" WHERE "Id" = %s', (prod_id,))
            price = cur.fetchone()[0]
            subtotal += price * qty
        cur.execute(
            'SELECT pc."Amount", pc."CodeType" FROM "AppliedPromo" ap JOIN "PromoCode" pc ON ap."PromoCode" = pc."Code" '
            'WHERE ap."CustomerId" = %s AND ap."CartNumber" = %s AND ap."LockedNumber" = %s',
            (customer_id, cart_number, locked_number)
        )
        promos = cur.fetchall()
        discount_total = Decimal("0.00")
        for promo in promos:
            amount, code_type = promo
            if code_type in ["Standard", "ReferralPercentage", "VIP"]:
                discount_total += subtotal * Decimal(str(amount))
            else:
                discount_total += Decimal(str(amount))
        final_total = max(subtotal - discount_total, Decimal("0.00"))
        print(f"Subtotal: {subtotal}")
        print(f"Total Discount: {discount_total}")
        print(f"Amount Due on Payment: {final_total}")
        cur.execute('UPDATE "Cart" SET "CartStatus" = %s WHERE "CartNumber" = %s', ("registered", cart_number))
        conn.commit()
        cur.close()
        logging.info(f"Cart {cart_number} submitted by CustomerId {customer_id}")
        print("Cart submitted successfully. Please proceed to payment when ready.")
    except Exception as e:
        conn.rollback()
        logging.error(f"Error in checkout: {e}")
        print("Error in checkout:", e)

def pay_cart(conn, customer_id, cart_number, locked_number):


    try:
        cur = conn.cursor()

        cur.execute(
            'SELECT "ProductId", "Quantity" FROM "CartItem" WHERE "CustomerId" = %s AND "CartNumber" = %s AND "LockedNumber" = %s',
            (customer_id, cart_number, locked_number)
        )
        items = cur.fetchall()
        if not items:
            print("Your cart is empty.")
            cur.close()
            return
        from decimal import Decimal
        subtotal = Decimal("0.00")

        for item in items:
            prod_id, qty = item
            cur.execute('SELECT "StockCount", "CurrentPrice" FROM "Product" WHERE "Id" = %s', (prod_id,))
            stock, price = cur.fetchone()
            if qty > stock:
                print(f"Insufficient stock for product ID {prod_id}. Available: {stock}")
                cur.close()
                return
            subtotal += price * qty

        cur.execute(
            'SELECT pc."Amount", pc."CodeType" FROM "AppliedPromo" ap JOIN "PromoCode" pc ON ap."PromoCode" = pc."Code" '
            'WHERE ap."CustomerId" = %s AND ap."CartNumber" = %s AND ap."LockedNumber" = %s',
            (customer_id, cart_number, locked_number)
        )
        promos = cur.fetchall()
        discount_total = Decimal("0.00")
        for promo in promos:
            amount, code_type = promo
            if code_type in ["Standard", "ReferralPercentage", "VIP"]:
                discount_total += subtotal * Decimal(str(amount))
            else:
                discount_total += Decimal(str(amount))
        final_total = max(subtotal - discount_total, Decimal("0.00"))
        
        print("Payment Details:")
        print(f"Subtotal: {subtotal}")
        print(f"Total Discount: {discount_total}")
        print(f"Final Total: {final_total}")
        
        
        cur.execute('SELECT "WalletBalance" FROM "Customer" WHERE "CustomerId" = %s', (customer_id,))
        wallet = cur.fetchone()[0]
        if wallet < final_total:
            print("Insufficient wallet balance for payment. Please increase your wallet balance.")
            cur.close()
            return
        cur.execute('UPDATE "Customer" SET "WalletBalance" = "WalletBalance" - %s WHERE "CustomerId" = %s', (final_total, customer_id))
        for item in items:
            prod_id, qty = item
            cur.execute('UPDATE "Product" SET "StockCount" = "StockCount" - %s WHERE "Id" = %s', (qty, prod_id))
        cur.execute('INSERT INTO "IssuedOrder" ("CartNumber", "LockedNumber", "CustomerId") VALUES (%s, %s, %s) RETURNING "TrackingCode"',
                    (cart_number, locked_number, customer_id))
        tracking_code = cur.fetchone()[0]
        conn.commit()
        

        for item in items:
            prod_id, qty = item
            cur.execute('SELECT "CurrentPrice" FROM "Product" WHERE "Id" = %s', (prod_id,))
            price = cur.fetchone()[0]
            cur.execute('INSERT INTO "IssuedOrderDetail" ("TrackingCode", "ProductId", "Quantity", "CartPrice") VALUES (%s, %s, %s, %s)',
                        (tracking_code, prod_id, qty, price))
        conn.commit()
        

        cur.execute('DELETE FROM "CartItem" WHERE "CustomerId" = %s AND "CartNumber" = %s AND "LockedNumber" = %s',
                    (customer_id, cart_number, locked_number))

        cur.execute('DELETE FROM "AppliedPromo" WHERE "CustomerId" = %s AND "CartNumber" = %s AND "LockedNumber" = %s',
                    (customer_id, cart_number, locked_number))

        cur.execute('UPDATE "Cart" SET "CartStatus" = %s WHERE "CartNumber" = %s', ("normal", cart_number))
        conn.commit()
        cur.close()
        print("Payment successful. Your order has been finalized and order details have been saved. The cart is now in 'normal' state.")
    except Exception as e:
        conn.rollback()
        print("Error in payment:", e)

    try:
        cur = conn.cursor()
        cur.execute(
            'SELECT "ProductId", "Quantity" FROM "CartItem" WHERE "CustomerId" = %s AND "CartNumber" = %s AND "LockedNumber" = %s',
            (customer_id, cart_number, locked_number)
        )
        items = cur.fetchall()
        if not items:
            print("Your cart is empty.")
            cur.close()
            return
        subtotal = 0
        from decimal import Decimal
        subtotal = Decimal("0.00")
        for item in items:
            prod_id, qty = item
            cur.execute('SELECT "StockCount", "CurrentPrice" FROM "Product" WHERE "Id" = %s', (prod_id,))
            stock, price = cur.fetchone()
            if qty > stock:
                print(f"Insufficient stock for product ID {prod_id}. Available: {stock}")
                cur.close()
                return
            subtotal += price * qty
        cur.execute(
            'SELECT pc."Amount", pc."CodeType" FROM "AppliedPromo" ap JOIN "PromoCode" pc ON ap."PromoCode" = pc."Code" '
            'WHERE ap."CustomerId" = %s AND ap."CartNumber" = %s AND ap."LockedNumber" = %s',
            (customer_id, cart_number, locked_number)
        )
        promos = cur.fetchall()
        discount_total = Decimal("0.00")
        for promo in promos:
            amount, code_type = promo
            if code_type in ["Standard", "ReferralPercentage", "VIP"]:
                discount_total += subtotal * Decimal(str(amount))
            else:
                discount_total += Decimal(str(amount))
        final_total = max(subtotal - discount_total, Decimal("0.00"))
        
        print("Payment Details:")
        print(f"Subtotal: {subtotal}")
        print(f"Total Discount: {discount_total}")
        print(f"Final Total: {final_total}")
        
        cur.execute('SELECT "WalletBalance" FROM "Customer" WHERE "CustomerId" = %s', (customer_id,))
        wallet = cur.fetchone()[0]
        if wallet < final_total:
            print("Insufficient wallet balance for payment. Please increase your wallet balance.")
            cur.close()
            return
        cur.execute('UPDATE "Customer" SET "WalletBalance" = "WalletBalance" - %s WHERE "CustomerId" = %s', (final_total, customer_id))
        for item in items:
            prod_id, qty = item
            cur.execute('UPDATE "Product" SET "StockCount" = "StockCount" - %s WHERE "Id" = %s', (qty, prod_id))

        cur.execute('INSERT INTO "IssuedOrder" ("CartNumber", "LockedNumber", "CustomerId") VALUES (%s, %s, %s)',
                    (cart_number, locked_number, customer_id))
        conn.commit()
        cur.execute('DELETE FROM "CartItem" WHERE "CustomerId" = %s AND "CartNumber" = %s AND "LockedNumber" = %s',
                    (customer_id, cart_number, locked_number))
        cur.execute('DELETE FROM "AppliedPromo" WHERE "CustomerId" = %s AND "CartNumber" = %s AND "LockedNumber" = %s',
                    (customer_id, cart_number, locked_number))

        cur.execute('UPDATE "Cart" SET "CartStatus" = %s WHERE "CartNumber" = %s', ("normal", cart_number))
        conn.commit()
        cur.close()
        print("Payment successful. Your order has been finalized. The cart has been cleared and is now in 'normal' state for new orders.")
    except Exception as e:
        conn.rollback()
        print("Error in payment:", e)


def simulate_cart_expiration(conn, customer_id):
    try:
        cur = conn.cursor()
        cur.execute('SELECT "CartNumber" FROM "Cart" WHERE "CustomerId" = %s AND "CartStatus" = %s', (customer_id, "registered"))
        carts = cur.fetchall()
        for cart in carts:
            cart_number = cart[0]
            cur.execute('SELECT "TimeStamp" FROM "LockedCart" WHERE "CustomerId" = %s AND "CartNumber" = %s', (customer_id, cart_number))
            timestamp = cur.fetchone()[0]
            if datetime.now() - timestamp > timedelta(days=3):
                cur.execute('SELECT "ProductId", "Quantity" FROM "CartItem" WHERE "CustomerId" = %s AND "CartNumber" = %s', (customer_id, cart_number))
                items = cur.fetchall()
                for item in items:
                    prod_id, qty = item
                    cur.execute('UPDATE "Product" SET "StockCount" = "StockCount" + %s WHERE "Id" = %s', (qty, prod_id))
                cur.execute('UPDATE "Cart" SET "CartStatus" = %s WHERE "CartNumber" = %s', ("locked", cart_number))
                print(f"Cart {cart_number} has expired and is now locked. Its items have been returned to inventory.")
        conn.commit()
        cur.close()
    except Exception as e:
        conn.rollback()
        logging.error(f"Error in simulating cart expiration: {e}")
        print("Error in simulating cart expiration:", e)

def select_vip_cart(conn, customer_id):

    try:
        cur = conn.cursor()
        cur.execute('SELECT "CartNumber", "CartStatus" FROM "Cart" WHERE "CustomerId" = %s ORDER BY "CartNumber" ASC', (customer_id,))
        carts = cur.fetchall()
        cur.close()
        if not carts or len(carts) < 5:
            print("Error: Less than 5 carts found for VIP user.")
            return None, None
        print("VIP Carts:")
        for cart in carts:
            print(f"Cart Number: {cart[0]} | Status: {cart[1]}")
        cart_number = int(input("Enter the cart number you want to select: "))
        locked_number = get_locked_cart(conn, customer_id, cart_number)
        return cart_number, locked_number
    except Exception as e:
        logging.error(f"Error in selecting VIP cart: {e}")
        print("Error in selecting cart:", e)
        return None, None
