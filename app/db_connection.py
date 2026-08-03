#!/usr/bin/env python3
import psycopg2 
import logging
import sys

# Configure logging
logging.basicConfig(filename='app.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s: %(message)s')

DB_PARAMS = {
    "host": "localhost",
    "database": "pisaz",
    "user": "YOUR_POSTGRES_USER",
    "password": "YOUR_POSTGRES_PASSWORD"
}

def connect_db():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        logging.info("Connected to database successfully.")
        print("Connected to database successfully.")
        return conn
    except Exception as e:
        logging.error(f"Database connection error: {e}")
        print("Database connection error:", e)
        sys.exit(1)
