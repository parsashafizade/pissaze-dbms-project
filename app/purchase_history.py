#!/usr/bin/env python3
import logging


def view_purchase_history(conn, customer):
    try:
        customer_id = customer["CustomerId"]
        cur = conn.cursor()
        cur.execute(
            'SELECT "TrackingCode", "OrderTime", "CartNumber", "LockedNumber" FROM "IssuedOrder" '
            'WHERE "CustomerId" = %s ORDER BY "OrderTime" DESC',
            (customer_id,)
        )
        orders = cur.fetchall()
        if orders:
            print("Purchase History:")
            for order in orders:
                tracking, order_time, cart_number, locked_number = order
                print(f"\nOrder Tracking Code: {tracking}, Order Time: {order_time}")
                cur.execute(
                    'SELECT p."Brand", p."Model", od."Quantity", od."CartPrice" '
                    'FROM "IssuedOrderDetail" od JOIN "Product" p ON od."ProductId" = p."Id" '
                    'WHERE od."TrackingCode" = %s',
                    (tracking,)
                )
                items = cur.fetchall()
                if items:
                    for item in items:
                        brand, model, qty, price = item
                        print(f"   {brand} {model} | Quantity: {qty} | Price per unit: {price}")
                else:
                    print("   (No items found for this order)")
        else:
            print("No purchase history found.")
        cur.close()
    except Exception as e:
        logging.error(f"Error in viewing purchase history: {e}")
        print("Error in viewing purchase history:", e)

    try:
        customer_id = customer["CustomerId"]
        cur = conn.cursor()
        cur.execute(
            'SELECT "TrackingCode", "OrderTime", "CartNumber", "LockedNumber" FROM "IssuedOrder" '
            'WHERE "CustomerId" = %s ORDER BY "OrderTime" DESC',
            (customer_id,)
        )
        orders = cur.fetchall()
        if orders:
            print("Purchase History:")
            for order in orders:
                tracking, order_time, cart_number, locked_number = order
                print(f"\nOrder Tracking Code: {tracking}, Order Time: {order_time}")
                cur.execute(
                    'SELECT p."Brand", p."Model", ci."Quantity", ci."CartPrice" '
                    'FROM "CartItem" ci JOIN "Product" p ON ci."ProductId" = p."Id" '
                    'WHERE ci."CustomerId" = %s AND ci."CartNumber" = %s AND ci."LockedNumber" = %s',
                    (customer_id, cart_number, locked_number)
                )
                items = cur.fetchall()
                if items:
                    for item in items:
                        brand, model, qty, price = item
                        print(f"   {brand} {model} | Quantity: {qty} | Total Price: {price}")
                else:
                    print("   (No items found for this order)")
        else:
            print("No purchase history found.")
        cur.close()
    except Exception as e:
        logging.error(f"Error in viewing purchase history: {e}")
        print("Error in viewing purchase history:", e)
