import duckdb
from transform_superstore import df_customer, df_date, df_product, df_shipping, df_location, df_sales
import os
from utils.logger import get_logger

dossier_root =  os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fichier_bdd = os.path.join(dossier_root, "Superstore.db")
lg = get_logger("etl", "ETL_error.log")

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
    conn.execute(""" Insert into Dim_Date (date_complete, year, month, day, trimestre) SELECT "Order Date", YEAR, Month, Day, Trimestre FROM df_date ON CONFLICT (date_complete) DO NOTHING""")
    conn.commit()
    conn.unregister("df_date")

def init_dim_customer():
    conn.execute(""" CREATE SEQUENCE IF NOT EXISTS id_dim_customer_seq START 1; """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS Dim_Customer(
    id_dim_customer    INTEGER PRIMARY KEY DEFAULT nextval('id_dim_customer_seq'),
    customer_id     TEXT NOT NULL,
    customer_name   TEXT NOT NULL,
    segment         TEXT NOT NULL,
    UNIQUE (customer_id)
    )
    """)
    conn.commit()

def insert_dim_customer():
    conn.register("df_customer", df_customer)
    conn.execute(""" Insert into Dim_Customer (customer_id, customer_name, segment) SELECT "Customer ID", "Customer Name", Segment FROM df_customer ON CONFLICT (customer_id) DO NOTHING""")
    conn.commit()
    conn.unregister("df_customer")

def init_dim_product():
    conn.execute(""" CREATE SEQUENCE IF NOT EXISTS id_dim_product_seq START 1; """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS Dim_Product(
    id_dim_product    INTEGER PRIMARY KEY DEFAULT nextval('id_dim_product_seq'),
    product_id  TEXT NOT NULL,
    product_name TEXT NOT NULL,
    product_category TEXT NOT NULL,
    product_sub_category TEXT NOT NULL,
    UNIQUE (product_id)
    )
    """)
    conn.commit()

def insert_dim_product():
    conn.register("df_product", df_product)
    conn.execute(""" Insert into Dim_Product (product_id, product_name, product_category, product_sub_category) SELECT "Product ID", "Product Name", Category, "Sub-Category" FROM df_product ON CONFLICT (product_id) DO NOTHING """)
    conn.commit()
    conn.unregister("df_product")

def init_dim_location():
    conn.execute(""" CREATE SEQUENCE IF NOT EXISTS id_dim_location_seq START 1; """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS Dim_Location(
            id_dim_location     INTEGER PRIMARY KEY DEFAULT nextval('id_dim_location_seq'),
            country     TEXT NOT NULL,
            state       TEXT NOT NULL,
            city        TEXT NOT NULL,
            region      TEXT NOT NULL,
            postal_code INTEGER NOT NULL,
            Unique(country, state, city, region, postal_code)
        )
    """)
    conn.commit()

def insert_dim_location():
    conn.register("df_location", df_location)
    conn.execute(""" Insert into Dim_Location (country, state, city, region, postal_code) SELECT Country, State, City, Region, "Postal Code" FROM df_location ON CONFLICT (country, state, city, region, postal_code) DO NOTHING """)
    conn.commit()
    conn.unregister("df_location")

def init_dim_shipping():
    conn.execute(""" CREATE SEQUENCE IF NOT EXISTS id_dim_shipping_seq START 1; """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS Dim_Shipping(
            id_dim_shipping     INTEGER PRIMARY KEY DEFAULT nextval('id_dim_shipping_seq'),
            shipping_mode   TEXT NOT NULL,
            UNIQUE (shipping_mode)
        )
    """)
    conn.commit()

def insert_dim_shipping():
    conn.register("df_shipping", df_shipping)
    conn.execute(""" Insert into Dim_Shipping (shipping_mode) SELECT "Ship Mode" FROM df_shipping ON CONFLICT (shipping_mode) DO NOTHING """)
    conn.commit()
    conn.unregister("df_shipping")

def init_fact_sales():
    conn.execute(""" CREATE SEQUENCE IF NOT EXISTS id_fact_sales_seq START 1; """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS Fact_Sales(
            id_fact_sales INTEGER PRIMARY KEY DEFAULT nextval('id_fact_sales_seq'),
            order_id            TEXT NOT NULL,
            id_dim_date         INTEGER REFERENCES Dim_Date(id_dim_date),
            id_dim_customer     INTEGER REFERENCES Dim_Customer(id_dim_customer),
            id_dim_product      INTEGER REFERENCES Dim_Product(id_dim_product),
            id_dim_location     INTEGER REFERENCES Dim_Location(id_dim_location),
            id_dim_shipping     INTEGER REFERENCES Dim_Shipping(id_dim_shipping),
            shipping_date       TEXT NOT NULL,
            sales               REAL NOT NULL,
            quantity            INTEGER NOT NULL,
            discount            REAL NOT NULL,
            profit              REAL NOT NULL,
            UNIQUE (order_id, id_dim_product)
        )
    """)
    conn.commit()

def  insert_fact_sales():
    conn.register("df_sales", df_sales)
    conn.execute("""
        Insert into Fact_Sales(order_id, id_dim_date, id_dim_customer, id_dim_product, id_dim_location, id_dim_shipping, shipping_date, sales, quantity, discount, profit) 
        SELECT s."Order ID", d.id_dim_date, c.id_dim_customer, p.id_dim_product, l.id_dim_location, sh.id_dim_shipping, s."Ship Date", s.sales, s.quantity, s.discount, s.profit
        FROM df_sales s
        JOIN Dim_Date d ON s."Order Date" = d.date_complete
        JOIN Dim_Customer c ON s."Customer ID" = c.customer_id
        JOIN Dim_Product p ON s."Product ID" = p.product_id
        JOIN Dim_Location l ON s.Country = l.country AND s.State = l.state AND s.City = l.city AND s.Region = l.region AND s."Postal Code" = l.postal_code
        JOIN Dim_Shipping sh ON s."Ship Mode" = sh.shipping_mode
        ON CONFLICT (order_id, id_dim_product) DO NOTHING
    """)  
    conn.commit()
    conn.unregister("df_sales") 

def main():
    init_dim_date()
    insert_dim_date()

    init_dim_customer()
    insert_dim_customer()

    init_dim_product()
    insert_dim_product()

    init_dim_location()
    insert_dim_location()

    init_dim_shipping()
    insert_dim_shipping()

    init_fact_sales()
    insert_fact_sales()



if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        lg.error(f"Erreur Pendant le chargement : {e}")
        raise
    finally:
        conn.close()