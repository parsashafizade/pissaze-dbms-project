#!/usr/bin/env python3
import logging

def increase_wallet(conn, customer):
    """Increase the digital wallet balance."""
    try:
        amount = float(input("Enter amount to add to your wallet: "))
        customer_id = customer["CustomerId"]
        cur = conn.cursor()
        cur.execute('UPDATE "Customer" SET "WalletBalance" = "WalletBalance" + %s WHERE "CustomerId" = %s', (amount, customer_id))
        conn.commit()
        cur.close()
        logging.info(f"Wallet increased by {amount} for CustomerId {customer_id}")
        print("Wallet balance increased successfully.")
    except Exception as e:
        conn.rollback()
        logging.error(f"Error increasing wallet balance: {e}")
        print("Error increasing wallet balance:", e)
