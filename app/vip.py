#!/usr/bin/env python3
import logging
from datetime import datetime, timedelta

def is_vip(conn, customer_id):
    try:
        cur = conn.cursor()
        cur.execute('SELECT "ExpirationTime" FROM "VIPCustomer" WHERE "CustomerId" = %s', (customer_id,))
        result = cur.fetchone()
        cur.close()
        if result and result[0] > datetime.now():
            return True
        return False
    except Exception as e:
        logging.error(f"Error checking VIP status: {e}")
        return False

def become_vip(conn, customer):

    try:
        customer_id = customer["CustomerId"]
        cur = conn.cursor()
        cur.execute('SELECT "WalletBalance" FROM "Customer" WHERE "CustomerId" = %s', (customer_id,))
        wallet = cur.fetchone()[0]
        if wallet < 45:
            print("Insufficient wallet balance to become VIP.")
            cur.close()
            return
        if is_vip(conn, customer_id):
            prompt = "You are already VIP. Do you want to renew VIP membership by paying 45? (y/n): "
        else:
            prompt = "Do you want to become VIP by paying 45? (y/n): "
        confirm = input(prompt).lower()
        if confirm != 'y':
            cur.close()
            return
        cur.execute('UPDATE "Customer" SET "WalletBalance" = "WalletBalance" - %s WHERE "CustomerId" = %s', (45, customer_id))
        expiration = datetime.now() + timedelta(days=30)
        cur.execute('INSERT INTO "VIPCustomer" ("CustomerId", "ExpirationTime") VALUES (%s, %s) ON CONFLICT ("CustomerId") DO UPDATE SET "ExpirationTime" = EXCLUDED."ExpirationTime"',
                    (customer_id, expiration))
        conn.commit()
        cur.close()
        assign_vip_discount_code(conn, customer_id)
        print("Your VIP membership has been set/renewed. A 25% discount code has been assigned to you.")
    except Exception as e:
        conn.rollback()
        logging.error(f"Error in becoming VIP: {e}")
        print("Error in becoming VIP:", e)

def ensure_vip_carts(conn, customer_id):

    try:
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM "Cart" WHERE "CustomerId" = %s', (customer_id,))
        count = cur.fetchone()[0]
        while count < 5:
            cur.execute('INSERT INTO "Cart" ("CartStatus", "CustomerId") VALUES (%s, %s)', ("normal", customer_id))
            conn.commit()
            count += 1
        cur.close()
    except Exception as e:
        conn.rollback()
        logging.error(f"Error ensuring VIP carts: {e}")

def assign_vip_discount_code(conn, customer_id):

    try:
        cur = conn.cursor()
        cur.execute('SELECT pa."Code" FROM "PromoAssignment" pa JOIN "PromoCode" pc ON pa."Code" = pc."Code" '
                    'WHERE pa."CustomerId" = %s AND pc."CodeType" = %s', (customer_id, "VIP"))
        if not cur.fetchone():
            from promo_codes import generate_three_digit_code
            code = generate_three_digit_code(conn)
            expiration = datetime.now() + timedelta(weeks=1)
            cur.execute('INSERT INTO "PromoCode" ("Code", "DiscountLimit", "Amount", "ExpirationTime", "CodeType") VALUES (%s, %s, %s, %s, %s)',
                        (code, 1000000, 0.25, expiration, "VIP"))
            cur.execute('INSERT INTO "PromoAssignment" ("Code", "CustomerId") VALUES (%s, %s)', (code, customer_id))
            conn.commit()
        cur.close()
    except Exception as e:
        conn.rollback()
        logging.error(f"Error assigning VIP discount code: {e}")
