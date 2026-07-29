import duckdb
from transform_superstore import df_customer, df_date, df_product, df_shipping, df_location, df_sales
import os

dossier_root =  os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fichier_bdd = os.path.join(dossier_root, "Superstore.db")

conn = duckdb.connect(fichier_bdd)


def init_dim_date():
    conn.execute(""" CREATE SEQUENCE IF NOT EXISTS id_dim_date_seq START 1; """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS Dim_Date (
    id_dim_date     INTEGER PRIMARY KEY DEFAULT nextval('id_dim_date_seq'),
    date_complete   DATE NOT NULL,
    year            INTEGER NOT NULL,
    month           INTEGER NOT NULL,
    day             INTEGER NOT NULL,
    trimestre       INTEGER NOT NULL,
    UNIQUE (date_complete)
    )
    """)
    conn.commit()
 
def insert_dim_date():
    conn.register("df_date", df_date)
    conn.execute(""" Insert into Dim_Date (date_complete, year, month, day, trimestre) SELECT ("Order Date", YEAR, Month, Day, Trimestre) FROM df_date""")
    conn.commit()

def init_dim_customer():
    conn.execute("""
    CREATE TABLE IF NOT EXISTS Dim_Customer(
    customer_id     TEXT PRIMARY KEY DEFAULT,
    customer_name   TEXT NOT NULL,
    segment         TEXT NOT NULL
    UNIQUE (customer_id)
    )
    """)
    conn.commit()

def insert_dim_customer():
    conn.register("df_customer", df_customer)
    conn.execute(""" Insert into Dim_Customer SELECT * FROM df_customer""")
    conn.commit()

def init_dim_product():
    conn.execute("""
    CREATE TABLE IF NOT EXISTS Dim_Product(
    product_id  TEXT PRIMARY KEY DEFAULT,
    product_name TEXT NOT NULL,
    product_category TEXT NOT NULL,
    product_sub_category TEXT NOT NULL,
    UNIQUE  (product_id)
    )
    """)
    conn.commit()

def insert_dim_product():
    conn.register("df_product", df_product)
    conn.execute(""" Insert into Dim_Product SELECT * FROM df_product """)
    conn.commit()

def init_dim_location():
    conn.execute(""" CREATE SEQUENCE IF NOT EXISTS id_dim_location_seq START 1; """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS Dim_Location(
            id_location     INTEGER PRIMARY KEY DEFAULT nextval('id_dim_location_seq'),
            country     TEXT NOT NULL,
            state       TEXT NOT NULL,
            city        TEXT NOT NULL,
            region      TEXT NOT NULL,
            postal_code INTEGER NOT NULL,
            Unique(id_location)
        )
    """)
    conn.commit()

def insert_dim_location():
    conn.register("df_location", df_location)
    conn.execute(""" Insert into Dim_Location (country, state, city, region, postal_code) SELECT (Country, State, City, Region, 'Postal Code') FROM df_location""")
    conn.commit()

def init_dim_shipping():
    conn.execute(""" CREATE SEQUENCE IF NOT EXISTS id_dim_shipping_seq START 1; """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS Dim_Shipping(
            id_shipping     INTEGER PRIMARY KEY DEFAULT nextval('id_dim_shipping_seq'),
            shipping_mode   TEXT NOT NULL,
            UNIQUE  (id_shipping)
        )
    """)
    conn.commit()

def insert_dim_shipping():
    conn.register("df_shipping", df_shipping)
    conn.execute(""" Insert into Dim_Shipping (shipping_mode) SELECT ('Ship Mode') FROM df_shipping""")
    conn.commit()

def init_fait_sales():
    