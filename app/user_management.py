#!/usr/bin/env python3
import sys
import logging
import re
from promo_codes import generate_referral_code, process_referral_discount, assign_discount_codes
from tables import create_tables  # In case you need table functions here

def validate_phone(phone):
    pattern = r'^09\d{9}$'
    return re.match(pattern, phone)

def register_user(conn):
    """Register new user with phone validation and optional referral."""
    try:
        first_name = input("Enter your first name: ")
        last_name = input("Enter your last name: ")
        phone = input("Enter your phone number (11 digits, starting with 09): ")
        if not validate_phone(phone):
            print("Invalid phone number format. Registration aborted.")
            return
        referral_input = input("Enter referral code (optional): ").strip()
        new_referral = generate_referral_code()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO "Customer" ("FirstName", "LastName", "PhoneNumber", "ReferralCode") VALUES (%s, %s, %s, %s) RETURNING "CustomerId"',
            (first_name, last_name, phone, new_referral)
        )
        customer_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        logging.info(f"User registered successfully: CustomerId {customer_id}")
        print("Registration successful. Your Customer ID is:", customer_id)
        if referral_input:
            try:
                cur = conn.cursor()
                cur.execute('SELECT "ReferralCode" FROM "Customer" WHERE "ReferralCode" = %s', (referral_input,))
                if cur.fetchone():
                    cur.execute(
                        'INSERT INTO "Referral" ("ReferrerId", "RefereeId") VALUES (%s, %s)',
                        (referral_input, new_referral)
                    )
                    conn.commit()
                    print("Referral recorded successfully.")
                else:
                    print("Invalid referral code. Skipping referral.")
                cur.close()
            except Exception as e:
                conn.rollback()
                logging.error(f"Error recording referral for CustomerId {customer_id}: {e}")
                print("Error recording referral:", e)
            process_referral_discount(conn, new_referral, referral_input)
        assign_discount_codes(conn, customer_id)
    except Exception as e:
        conn.rollback()
        logging.error(f"Error in registration: {e}")
        print("Error in registration:", e)

def login_user(conn):
    """Log in user by phone number."""
    try:
        phone = input("Enter your phone number: ")
        cur = conn.cursor()
        cur.execute(
            'SELECT "CustomerId", "FirstName", "LastName", "WalletBalance", "ReferralCode" FROM "Customer" WHERE "PhoneNumber" = %s',
            (phone,)
        )
        result = cur.fetchone()
        cur.close()
        if result:
            customer = {
                "CustomerId": result[0],
                "FirstName": result[1],
                "LastName": result[2],
                "WalletBalance": result[3],
                "ReferralCode": result[4]
            }
            logging.info(f"User logged in successfully: CustomerId {customer['CustomerId']}")
            print("Login successful. Welcome,", customer["FirstName"])
            return customer
        else:
            print("No user found with that phone number.")
            return None
    except Exception as e:
        logging.error(f"Error in login: {e}")
        print("Error in login:", e)
        return None

def view_profile(conn, customer):
    """Display user profile with referral info."""
    try:
        customer_id = customer["CustomerId"]
        referral_code = customer["ReferralCode"]
        cur = conn.cursor()
        cur.execute(
            'SELECT "CustomerId", "FirstName", "LastName", "PhoneNumber", "WalletBalance", "ReferralCode", "TimeStamp" FROM "Customer" WHERE "CustomerId" = %s',
            (customer_id,)
        )
        profile = cur.fetchone()
        if profile:
            print("Profile Information:")
            print(f"Customer ID: {profile[0]}")
            print(f"Name: {profile[1]} {profile[2]}")
            print(f"Phone: {profile[3]}")
            print(f"Wallet Balance: {profile[4]}")
            print(f"Your Referral Code: {profile[5]}")
            print(f"Registered On: {profile[6]}")
            cur.execute('SELECT "ReferrerId" FROM "Referral" WHERE "RefereeId" = %s', (referral_code,))
            inviter = cur.fetchone()
            invited_by = inviter[0] if inviter else ""
            print(f"Invited By: {invited_by}")
        else:
            print("Profile not found.")
        cur.close()
    except Exception as e:
        logging.error(f"Error in viewing profile: {e}")
        print("Error in viewing profile:", e)

def view_my_referrals(conn, customer):
    """Display list of users invited by the current user."""
    try:
        referral_code = customer["ReferralCode"]
        cur = conn.cursor()
        cur.execute(
            'SELECT c."FirstName", c."LastName", c."PhoneNumber", c."TimeStamp" FROM "Referral" r JOIN "Customer" c ON r."RefereeId" = c."ReferralCode" WHERE r."ReferrerId" = %s',
            (referral_code,)
        )
        referrals = cur.fetchall()
        cur.close()
        if referrals:
            print("Users You Invited:")
            for ref in referrals:
                print(f"{ref[0]} {ref[1]} | Phone: {ref[2]} | Registered On: {ref[3]}")
        else:
            print("You haven't invited anyone yet.")
    except Exception as e:
        logging.error(f"Error in viewing referrals: {e}")
        print("Error in viewing referrals:", e)
