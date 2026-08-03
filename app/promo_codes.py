#!/usr/bin/env python3
import random
import string
from datetime import datetime, timedelta
import logging

def generate_three_digit_code(conn):
    """Generate a unique three-digit discount code."""
    while True:
        code = random.randint(100, 999)
        cur = conn.cursor()
        cur.execute('SELECT "Code" FROM "PromoCode" WHERE "Code" = %s', (code,))
        if not cur.fetchone():
            cur.close()
            return code
        cur.close()

def generate_referral_code(length=18):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def get_customer_id_by_referral(conn, referral_code):
    cur = conn.cursor()
    cur.execute('SELECT "CustomerId" FROM "Customer" WHERE "ReferralCode" = %s', (referral_code,))
    result = cur.fetchone()
    cur.close()
    return result[0] if result else None

def process_referral_discount(conn, new_referral, referral_input):

    try:
        current_referral = referral_input
        level = 1
        while current_referral:
            discount_rate = 50 / (2 * level)
            expiration = datetime.now() + timedelta(weeks=1)
            if discount_rate < 0.01:
                discount_amount = 50000
                code_type = "ReferralFixed"
            else:
                discount_amount = discount_rate
                code_type = "ReferralPercentage"
            if code_type == "ReferralFixed" and discount_amount > 1000000:
                discount_amount = 1000000
            code = generate_three_digit_code(conn)
            cur = conn.cursor()
            cur.execute(
                'INSERT INTO "PromoCode" ("Code", "DiscountLimit", "Amount", "ExpirationTime", "CodeType") VALUES (%s, %s, %s, %s, %s)',
                (code, 1000000, discount_amount, expiration, code_type)
            )
            cust_id = get_customer_id_by_referral(conn, current_referral)
            if cust_id:
                cur.execute(
                    'INSERT INTO "PromoAssignment" ("Code", "CustomerId") VALUES (%s, %s)',
                    (code, cust_id)
                )
            conn.commit()
            cur.close()
            cur = conn.cursor()
            cur.execute('SELECT "ReferrerId" FROM "Referral" WHERE "RefereeId" = %s', (current_referral,))
            result = cur.fetchone()
            cur.close()
            current_referral = result[0] if result else None
            level += 1
        # Also assign discount code to the new user itself (level 1)
        discount_rate = 50 / 2
        if discount_rate < 0.01:
            discount_amount = 50000
            code_type = "ReferralFixed"
        else:
            discount_amount = discount_rate
            code_type = "ReferralPercentage"
        if code_type == "ReferralFixed" and discount_amount > 1000000:
            discount_amount = 1000000
        expiration = datetime.now() + timedelta(weeks=1)
        code = generate_three_digit_code(conn)
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO "PromoCode" ("Code", "DiscountLimit", "Amount", "ExpirationTime", "CodeType") VALUES (%s, %s, %s, %s, %s)',
            (code, 1000000, discount_amount, expiration, code_type)
        )
        cust_id = get_customer_id_by_referral(conn, new_referral)
        if cust_id:
            cur.execute(
                'INSERT INTO "PromoAssignment" ("Code", "CustomerId") VALUES (%s, %s)',
                (code, cust_id)
            )
        conn.commit()
        cur.close()
    except Exception as e:
        conn.rollback()
        logging.error(f"Error in processing referral discount: {e}")
        print("Error in processing referral discount:", e)

def assign_discount_codes(conn, customer_id):
    """Assign two standard discount codes (15% and 20%) as three-digit codes."""
    try:
        cur = conn.cursor()
        expiration = datetime.now() + timedelta(weeks=1)
        promo_data = [
            (0.15, 1000000, expiration, 'Standard'),
            (0.20, 1000000, expiration, 'Standard')
        ]
        for amount, discount_limit, exp_time, code_type in promo_data:
            code = generate_three_digit_code(conn)
            cur.execute(
                'INSERT INTO "PromoCode" ("Code", "DiscountLimit", "Amount", "ExpirationTime", "CodeType") VALUES (%s, %s, %s, %s, %s)',
                (code, discount_limit, amount, exp_time, code_type)
            )
            cur.execute(
                'INSERT INTO "PromoAssignment" ("Code", "CustomerId") VALUES (%s, %s)',
                (code, customer_id)
            )
        conn.commit()
        cur.close()
        logging.info(f"Standard discount codes assigned to CustomerId {customer_id}")
    except Exception as e:
        conn.rollback()
        logging.error(f"Error assigning standard discount codes to CustomerId {customer_id}: {e}")

def view_discount_codes(conn, customer_id):
    """Display discount codes assigned to the user."""
    try:
        cur = conn.cursor()
        cur.execute(
            'SELECT pc."Code", pc."Amount", pc."ExpirationTime", pc."CodeType" FROM "PromoAssignment" pa JOIN "PromoCode" pc ON pa."Code" = pc."Code" WHERE pa."CustomerId" = %s',
            (customer_id,)
        )
        codes = cur.fetchall()
        cur.close()
        if codes:
            print("Your Discount Codes:")
            for code in codes:
                if code[3] in ["Standard", "ReferralPercentage"]:
                    discount_str = f"{float(code[1])*100:.0f}%"
                else:
                    discount_str = f"{int(code[1])} Toman"
                print(f"Code: {code[0]}, Discount: {discount_str}, Expires: {code[2]}")
        else:
            print("No discount codes found.")
    except Exception as e:
        logging.error(f"Error in viewing discount codes: {e}")
        print("Error in viewing discount codes:", e)
