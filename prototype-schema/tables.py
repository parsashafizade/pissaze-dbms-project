#!/usr/bin/env python3
import sys
import logging

def create_tables(conn):
    """Create all necessary tables (including HDDProduct, CaseProduct, VIPCustomer, etc.)."""
    commands = [
        # Customer table
        '''
        CREATE TABLE IF NOT EXISTS "Customer" (
            "CustomerId" SERIAL PRIMARY KEY,
            "FirstName" VARCHAR(40) NOT NULL,
            "LastName" VARCHAR(40) NOT NULL,
            "PhoneNumber" VARCHAR(13) NOT NULL UNIQUE,
            "ReferralCode" VARCHAR(18) NOT NULL UNIQUE,
            "WalletBalance" DECIMAL(10,2) NOT NULL DEFAULT 0.00,
            "TimeStamp" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ''',
        # Product table
        '''
        CREATE TABLE IF NOT EXISTS "Product" (
            "Id" SERIAL PRIMARY KEY,
            "Brand" VARCHAR(40) NOT NULL,
            "Model" VARCHAR(40) NOT NULL,
            "Category" VARCHAR(45),
            "CurrentPrice" INT,
            "StockCount" SMALLINT
        );
        ''',
        # HDDProduct table
        '''
        CREATE TABLE IF NOT EXISTS "HDDProduct" (
            "ProductId" INT PRIMARY KEY,
            "Wattage" INT,
            "Capacity" DECIMAL(8,3),
            "RotationalSpeed" INT,
            "Depth" DECIMAL(8,3),
            FOREIGN KEY ("ProductId") REFERENCES "Product" ("Id") ON UPDATE CASCADE ON DELETE CASCADE
        );
        ''',
        # CaseProduct table
        '''
        CREATE TABLE IF NOT EXISTS "CaseProduct" (
            "ProductId" INT PRIMARY KEY,
            "NumFans" SMALLINT,
            "Material" VARCHAR(40),
            "FanSize" INT,
            "Wattage" INT,
            "ProductType" VARCHAR(40),
            "Width" DECIMAL(8,3),
            "Depth" DECIMAL(8,3),
            "Height" DECIMAL(8,3),
            "Color" VARCHAR(40),
            FOREIGN KEY ("ProductId") REFERENCES "Product" ("Id") ON UPDATE CASCADE ON DELETE CASCADE
        );
        ''',
        # VIPCustomer table
        '''
        CREATE TABLE IF NOT EXISTS "VIPCustomer" (
            "CustomerId" INT PRIMARY KEY,
            "ExpirationTime" TIMESTAMP NOT NULL,
            FOREIGN KEY ("CustomerId") REFERENCES "Customer" ("CustomerId") ON UPDATE CASCADE ON DELETE CASCADE
        );
        ''',
        # Cart table
        '''
        CREATE TABLE IF NOT EXISTS "Cart" (
            "CartNumber" SERIAL PRIMARY KEY,
            "CartStatus" VARCHAR(20) NOT NULL DEFAULT 'normal',
            "CustomerId" INT NOT NULL,
            FOREIGN KEY ("CustomerId") REFERENCES "Customer" ("CustomerId") ON UPDATE CASCADE ON DELETE CASCADE
        );
        ''',
        # LockedCart table
        '''
        CREATE TABLE IF NOT EXISTS "LockedCart" (
            "LockedNumber" SERIAL,
            "CustomerId" INT NOT NULL,
            "CartNumber" INT NOT NULL,
            "TimeStamp" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY ("CustomerId", "CartNumber", "LockedNumber"),
            FOREIGN KEY ("CustomerId") REFERENCES "Customer" ("CustomerId") ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY ("CartNumber") REFERENCES "Cart" ("CartNumber") ON UPDATE CASCADE ON DELETE CASCADE
        );
        ''',
        # CartItem table
        '''
        CREATE TABLE IF NOT EXISTS "CartItem" (
            "Quantity" INT DEFAULT 1 CHECK ("Quantity" > 0),
            "LockedNumber" INT NOT NULL,
            "CartPrice" DECIMAL(10,2) CHECK ("CartPrice" >= 0),
            "CustomerId" INT NOT NULL,
            "ProductId" INT NOT NULL,
            "CartNumber" INT NOT NULL,
            PRIMARY KEY ("CustomerId", "CartNumber", "LockedNumber", "ProductId"),
            FOREIGN KEY ("CustomerId", "CartNumber", "LockedNumber") REFERENCES "LockedCart" ("CustomerId", "CartNumber", "LockedNumber") ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY ("ProductId") REFERENCES "Product" ("Id") ON UPDATE CASCADE ON DELETE CASCADE
        );
        ''',
        # PromoCode table
        '''
        CREATE TABLE IF NOT EXISTS "PromoCode" (
            "Code" INT PRIMARY KEY,
            "DiscountLimit" DECIMAL(10,2) CHECK ("DiscountLimit" > 0),
            "Amount" DECIMAL(10,2) CHECK ("Amount" > 0),
            "ExpirationTime" TIMESTAMP,
            "CodeType" VARCHAR(40) NOT NULL
        );
        ''',
        # PromoAssignment table
        '''
        CREATE TABLE IF NOT EXISTS "PromoAssignment" (
            "Code" INT PRIMARY KEY,
            "CustomerId" INT NOT NULL,
            FOREIGN KEY ("Code") REFERENCES "PromoCode" ("Code") ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY ("CustomerId") REFERENCES "Customer" ("CustomerId") ON UPDATE CASCADE ON DELETE CASCADE
        );
        ''',
        # AppliedPromo table
        '''
        CREATE TABLE IF NOT EXISTS "AppliedPromo" (
            "PromoCode" INT NOT NULL,
            "CustomerId" INT NOT NULL,
            "LockedNumber" INT NOT NULL,
            "CartNumber" INT NOT NULL,
            PRIMARY KEY ("CustomerId", "CartNumber", "LockedNumber", "PromoCode"),
            FOREIGN KEY ("PromoCode") REFERENCES "PromoCode" ("Code") ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY ("CustomerId", "CartNumber", "LockedNumber") REFERENCES "LockedCart" ("CustomerId", "CartNumber", "LockedNumber") ON UPDATE CASCADE ON DELETE CASCADE
        );
        ''',
        # IssuedOrder table
        '''
        CREATE TABLE IF NOT EXISTS "IssuedOrder" (
            "TrackingCode" SERIAL PRIMARY KEY,
            "CartNumber" INT NOT NULL,
            "LockedNumber" INT NOT NULL,
            "CustomerId" INT NOT NULL,
            "OrderTime" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY ("CustomerId", "CartNumber", "LockedNumber") REFERENCES "LockedCart" ("CustomerId", "CartNumber", "LockedNumber") ON UPDATE CASCADE ON DELETE CASCADE
        );
        ''',
        '''ALTER TABLE "IssuedOrder" ADD COLUMN IF NOT EXISTS "OrderTime" TIMESTAMP DEFAULT CURRENT_TIMESTAMP;''',
        # Referral table
        '''
        CREATE TABLE IF NOT EXISTS "Referral" (
            "ReferrerId" VARCHAR(18) NOT NULL,
            "RefereeId" VARCHAR(18) PRIMARY KEY,
            FOREIGN KEY ("RefereeId") REFERENCES "Customer" ("ReferralCode") ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY ("ReferrerId") REFERENCES "Customer" ("ReferralCode") ON UPDATE CASCADE ON DELETE CASCADE
        );
        ''',
        # Compatibility tables
        '''
        CREATE TABLE IF NOT EXISTS "CpuCoolerCompatibility" (
            "CpuId" INT NOT NULL,
            "CoolerId" INT NOT NULL,
            PRIMARY KEY ("CpuId", "CoolerId"),
            FOREIGN KEY ("CpuId") REFERENCES "Product" ("Id") ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY ("CoolerId") REFERENCES "Product" ("Id") ON UPDATE CASCADE ON DELETE CASCADE
        );
        ''',
        '''
        CREATE TABLE IF NOT EXISTS "CpuMotherboardCompatibility" (
            "CpuId" INT NOT NULL,
            "MotherboardId" INT NOT NULL,
            PRIMARY KEY ("CpuId", "MotherboardId"),
            FOREIGN KEY ("CpuId") REFERENCES "Product" ("Id") ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY ("MotherboardId") REFERENCES "Product" ("Id") ON UPDATE CASCADE ON DELETE CASCADE
        );
        ''',
        '''
        CREATE TABLE IF NOT EXISTS "RamMotherboardCompatibility" (
            "MotherboardId" INT NOT NULL,
            "RamId" INT NOT NULL,
            PRIMARY KEY ("RamId", "MotherboardId"),
            FOREIGN KEY ("MotherboardId") REFERENCES "Product" ("Id") ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY ("RamId") REFERENCES "Product" ("Id") ON UPDATE CASCADE ON DELETE CASCADE
        );
        ''',
        '''
        CREATE TABLE IF NOT EXISTS "GpuMotherboardCompatibility" (
            "MotherboardId" INT NOT NULL,
            "GpuId" INT NOT NULL,
            PRIMARY KEY ("GpuId", "MotherboardId"),
            FOREIGN KEY ("MotherboardId") REFERENCES "Product" ("Id") ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY ("GpuId") REFERENCES "Product" ("Id") ON UPDATE CASCADE ON DELETE CASCADE
        );
        ''',
        '''
        CREATE TABLE IF NOT EXISTS "SsdMotherboardCompatibility" (
            "MotherboardId" INT NOT NULL,
            "SsdId" INT NOT NULL,
            PRIMARY KEY ("SsdId", "MotherboardId"),
            FOREIGN KEY ("MotherboardId") REFERENCES "Product" ("Id") ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY ("SsdId") REFERENCES "Product" ("Id") ON UPDATE CASCADE ON DELETE CASCADE
        );
        ''',

        '''
        CREATE TABLE IF NOT EXISTS "IssuedOrderDetail" (
            "TrackingCode" INT,
            "ProductId" INT,
            "Quantity" INT,
            "CartPrice" DECIMAL(10,2),
            PRIMARY KEY ("TrackingCode", "ProductId"),
            FOREIGN KEY ("TrackingCode") REFERENCES "IssuedOrder" ("TrackingCode") ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY ("ProductId") REFERENCES "Product" ("Id") ON UPDATE CASCADE ON DELETE CASCADE
        );
        ''',
        '''
        CREATE TABLE IF NOT EXISTS "GpuPsuCompatibility" (
            "GpuId" INT NOT NULL,
            "PowerSupplyId" INT NOT NULL,
            PRIMARY KEY ("GpuId", "PowerSupplyId"),
            FOREIGN KEY ("GpuId") REFERENCES "Product" ("Id") ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY ("PowerSupplyId") REFERENCES "Product" ("Id") ON UPDATE CASCADE ON DELETE CASCADE
        );
        '''
    ]
    try:
        cur = conn.cursor()
        for command in commands:
            cur.execute(command)
        conn.commit()
        cur.close()
        logging.info("All necessary tables are created or already exist.")
    except Exception as e:
        conn.rollback()
        logging.error(f"Error creating tables: {e}")
        print("Error creating tables:", e)
        sys.exit(1)
