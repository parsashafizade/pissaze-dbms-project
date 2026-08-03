#!/usr/bin/env python3
import sys
import logging
from db_connection import connect_db
from tables import create_tables
from products import populate_sample_products, view_all_products
from user_management import register_user, login_user, view_profile, view_my_referrals
from cart_management import (
    get_active_cart, get_locked_cart, view_cart, apply_promo, checkout,
    pay_cart, simulate_cart_expiration, select_vip_cart, get_cart_state
)
from payment import increase_wallet
from vip import is_vip, become_vip, ensure_vip_carts, assign_vip_discount_code
from purchase_history import view_purchase_history

# python /Users/parsash/Desktop/P4/main.py

def help_menu():
    print("Help Menu:")
    print("1. Register: Create a new account. Optionally, enter a referral code if invited.")
    print("2. Login: Log into your account using your phone number.")
    print("3. Help: Display this help menu.")
    print("4. View Products (Guest): View all available products without logging in.")
    print("5. Exit: Close the application.")

def main_menu():
    print("\nMain Menu:")
    print("1. Register")
    print("2. Login")
    print("3. Help")
    print("4. View Products (Guest)")
    print("5. Exit")
    return input("Enter your choice: ")

def user_menu(conn, customer):
    customer_id = customer["CustomerId"]
    vip_status = is_vip(conn, customer_id)
    if vip_status:
        print("You are a VIP member.")
        # برای VIP، ابتدا اطمینان از وجود 5 سبد خرید و تخصیص کد تخفیف انجام می‌شود.
        ensure_vip_carts(conn, customer_id)
        assign_vip_discount_code(conn, customer_id)
        # نمایش لیست سبدهای خرید برای انتخاب توسط کاربر VIP.
        cart_number, locked_number = select_vip_cart(conn, customer_id)
        if cart_number is None:
            return
    else:
        print("You are a regular member.")
        cart_number = get_active_cart(conn, customer_id, vip=False)
        if cart_number is None:
            return
        locked_number = get_locked_cart(conn, customer_id, cart_number)

    while True:
        state = get_cart_state(conn, cart_number)
        if not vip_status:
            print("\nUser Menu:")
            print("1. View Products")
            print("2. Add Product to Cart")
            print("3. View Cart")
            print("4. Apply Promo Code")
            if state == "normal":
                print("5. Submit Cart")
            elif state == "registered":
                print("5. Pay Cart")
            elif state == "locked":
                print("5. Cart Locked (View Only)")
            print("6. Increase Wallet Balance")
            print("7. View Purchase History")
            print("8. View Profile")
            print("9. View Discount Codes")
            print("10. View My Referrals")
            print("11. Check Compatibility (manual)")
            print("12. Become VIP")
            print("13. Simulate Cart Expiration")
            print("14. Logout")
            choice = input("Enter your choice: ")
            if choice == "1":
                from products import view_products
                view_products(conn, customer_id, cart_number, locked_number)
            elif choice == "2":
                from products import add_product_to_cart
                if state != "normal":
                    print("Cannot add items to a cart that is not in 'normal' state.")
                else:
                    add_product_to_cart(conn, customer_id, cart_number, locked_number)
            elif choice == "3":
                view_cart(conn, customer_id, cart_number, locked_number)
            elif choice == "4":
                apply_promo(conn, customer_id, cart_number, locked_number)
            elif choice == "5":
                if state == "normal":
                    checkout(conn, customer_id, cart_number, locked_number)
                elif state == "registered":
                    pay_cart(conn, customer_id, cart_number, locked_number)
                    cart_number = get_active_cart(conn, customer_id, vip=False)
                    locked_number = get_locked_cart(conn, customer_id, cart_number)
                    print("Your cart has been cleared. A new cart has been created for further shopping.")
                elif state == "locked":
                    print("This cart is locked and cannot be modified.")
            elif choice == "6":
                increase_wallet(conn, customer)
            elif choice == "7":
                view_purchase_history(conn, customer)
            elif choice == "8":
                view_profile(conn, customer)
            elif choice == "9":
                from promo_codes import view_discount_codes
                view_discount_codes(conn, customer_id)
            elif choice == "10":
                view_my_referrals(conn, customer)
            elif choice == "11":
                from compatibility import check_compatibility
                check_compatibility(conn)
            elif choice == "12":
                become_vip(conn, customer)
                print("You have been logged out automatically as a VIP member.")
                break
            elif choice == "13":
                simulate_cart_expiration(conn, customer_id)
            elif choice == "14":
                print("Logged out.")
                break
            else:
                print("Invalid choice. Please try again.")
        else:
            print("\nVIP User Menu:")
            print("1. View Products")
            print("2. Add Product to Cart")
            print("3. View Cart")
            print("4. Apply Promo Code")
            if state == "normal":
                print("5. Submit Cart")
            elif state == "registered":
                print("5. Pay Cart")
            elif state == "locked":
                print("5. Cart Locked (View Only)")
            print("6. Increase Wallet Balance")
            print("7. View Purchase History")
            print("8. View Profile")
            print("9. View Discount Codes")
            print("10. View My Referrals")
            print("11. Check Compatibility (manual)")
            print("12. Change Cart (Select a Different Cart)")
            print("13. Renew VIP")
            print("14. Simulate Cart Expiration")
            print("15. Logout")
            choice = input("Enter your choice: ")
            if choice == "1":
                from products import view_products
                view_products(conn, customer_id, cart_number, locked_number)
            elif choice == "2":
                from products import add_product_to_cart
                if state != "normal":
                    print("Cannot add items to a cart that is not in 'normal' state.")
                else:
                    add_product_to_cart(conn, customer_id, cart_number, locked_number)
            elif choice == "3":
                view_cart(conn, customer_id, cart_number, locked_number)
            elif choice == "4":
                apply_promo(conn, customer_id, cart_number, locked_number)
            elif choice == "5":
                if state == "normal":
                    checkout(conn, customer_id, cart_number, locked_number)
                elif state == "registered":
                    pay_cart(conn, customer_id, cart_number, locked_number)
                    # پس از پرداخت، امکان انتخاب سبد جدید به کاربر داده می‌شود.
                    cart_number, locked_number = select_vip_cart(conn, customer_id)
                    print("Your cart has been cleared. You may select a different cart for further shopping.")
                elif state == "locked":
                    print("This cart is locked and cannot be modified.")
            elif choice == "6":
                increase_wallet(conn, customer)
            elif choice == "7":
                view_purchase_history(conn, customer)
            elif choice == "8":
                view_profile(conn, customer)
            elif choice == "9":
                from promo_codes import view_discount_codes
                view_discount_codes(conn, customer_id)
            elif choice == "10":
                view_my_referrals(conn, customer)
            elif choice == "11":
                from compatibility import check_compatibility
                check_compatibility(conn)
            elif choice == "12":
                new_cart, new_locked = select_vip_cart(conn, customer_id)
                if new_cart:
                    cart_number = new_cart
                    locked_number = new_locked
                    print(f"Switched to cart {cart_number}.")
            elif choice == "13":
                # تمدید عضویت VIP
                become_vip(conn, customer)
                print("Your VIP membership has been renewed. You have been logged out.")
                break
            elif choice == "14":
                simulate_cart_expiration(conn, customer_id)
            elif choice == "15":
                print("Logged out.")
                break
            else:
                print("Invalid choice. Please try again.")

def main():
    conn = connect_db()
    create_tables(conn)
    populate_sample_products(conn)
    while True:
        choice = main_menu()
        if choice == "1":
            register_user(conn)
        elif choice == "2":
            customer = login_user(conn)
            if customer:
                user_menu(conn, customer)
        elif choice == "3":
            help_menu()
        elif choice == "4":
            view_all_products(conn)
        elif choice == "5":
            print("Exiting application.")
            break
        else:
            print("Invalid choice. Please try again.")
    conn.close()

if __name__ == "__main__":
    main()
