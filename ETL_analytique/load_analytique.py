import duckdb
from ETL_analytique.transform_analytique import df_date, df_customer, df_product, df_shipping, df_location, df_sales
from pathlib import Path
from utils.logger import get_logger

BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "data" / "db"
FICHIER_DB = DB_DIR / "Superstore_analytique.db"

lg = get_logger("etl", "ETL_error.log")

DB_DIR.mkdir(parents=True, exist_ok=True)
conn = duckdb.connect(str(FICHIER_DB))


def init_dim_date():
    conn.execute("""
    CREATE TABLE IF NOT EXISTS Dim_Date (
    date_id INTEGER PRIMARY KEY,
    date_complete DATE NOT NULL,
    annee INTEGER NOT NULL,
    trimestre INTEGER NOT NULL,
    mois INTEGER NOT NULL,
    nom_mois TEXT NOT NULL,
    semaine INTEGER NOT NULL,
    jour_semaine TEXT NOT NULL,
    est_weekend BOOLEAN NOT NULL
    )
    """)
    conn.commit()

def insert_dim_date():
    conn.register("df_date", df_date)
    conn.execute(""" Insert into Dim_Date (date_id, date_complete, annee, trimestre, mois, nom_mois, semaine, jour_semaine, est_weekend) SELECT date_id, "date", annee, trimestre, mois, nom_mois, semaine, jour_semaine, est_weekend FROM df_date ON CONFLICT (date_id) DO NOTHING""")
    conn.commit()
    conn.unregister("df_date")

def init_dim_customer():
    conn.execute("""
    CREATE TABLE IF NOT EXISTS Dim_Customer(
    customer_id     TEXT PRIMARY KEY,
    customer_name   TEXT NOT NULL,
    segment         TEXT NOT NULL
    )
    """)
    conn.commit()

def insert_dim_customer():
    conn.register("df_customer", df_customer)
    conn.execute(""" Insert into Dim_Customer (customer_id, customer_name, segment) SELECT client_id, nom_client, segment FROM df_customer ON CONFLICT (customer_id) DO NOTHING""")
    conn.commit()
    conn.unregister("df_customer")

def init_dim_product():
    conn.execute("""
    CREATE TABLE IF NOT EXISTS Dim_Product(
    product_id  TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    product_category TEXT NOT NULL,
    product_sub_category TEXT NOT NULL
    )
    """)
    conn.commit()

def insert_dim_product():
    conn.register("df_product", df_product)
    conn.execute(""" Insert into Dim_Product (product_id, product_name, product_category, product_sub_category) SELECT produit_id, nom_produit, categorie, sous_categorie FROM df_product ON CONFLICT (product_id) DO NOTHING """)
    conn.commit()
    conn.unregister("df_product")

def init_dim_location():
    conn.execute("""
        CREATE TABLE IF NOT EXISTS Dim_Location(
            id_dim_location     INTEGER PRIMARY KEY,
            country     TEXT NOT NULL,
            state       TEXT NOT NULL,
            city        TEXT NOT NULL,
            region      TEXT NOT NULL,
            postal_code TEXT NOT NULL
        )
    """)
    conn.commit()

def insert_dim_location():
    conn.register("df_location", df_location)
    conn.execute(""" Insert into Dim_Location (id_dim_location, country, state, city, region, postal_code) SELECT geographie_id, pays, etat, ville, region, code_postal FROM df_location ON CONFLICT (id_dim_location) DO NOTHING """)
    conn.commit()
    conn.unregister("df_location")

def init_dim_shipping():
    conn.execute("""
        CREATE TABLE IF NOT EXISTS Dim_Shipping(
            id_dim_shipping     INTEGER PRIMARY KEY,
            shipping_mode   TEXT NOT NULL,
            UNIQUE (shipping_mode)
        )
    """)
    conn.commit()

def insert_dim_shipping():
    conn.register("df_shipping", df_shipping)
    conn.execute(""" Insert into Dim_Shipping (id_dim_shipping, shipping_mode) SELECT mode_expedition_id, mode_expedition FROM df_shipping ON CONFLICT (id_dim_shipping) DO NOTHING """)
    conn.commit()
    conn.unregister("df_shipping")

def init_fact_sales():
    conn.execute("""
        CREATE TABLE IF NOT EXISTS Fact_Sales(
            id_fact_sales       INTEGER PRIMARY KEY,
            order_id            TEXT NOT NULL,
            id_date_commande    INTEGER NOT NULL REFERENCES Dim_Date(date_id),
            id_date_expedition  INTEGER NOT NULL REFERENCES Dim_Date(date_id),
            customer_id         TEXT NOT NULL REFERENCES Dim_Customer(customer_id),
            product_id          TEXT NOT NULL REFERENCES Dim_Product(product_id),
            id_dim_location     INTEGER NOT NULL REFERENCES Dim_Location(id_dim_location),
            id_dim_shipping     INTEGER NOT NULL REFERENCES Dim_Shipping(id_dim_shipping),
            sales               DOUBLE NOT NULL,
            quantity            INTEGER NOT NULL,
            discount            DOUBLE NOT NULL,
            profit              DOUBLE NOT NULL,
            shipping_delay      INTEGER NOT NULL
        )
    """)
    conn.commit()

def  insert_fact_sales():
    conn.register("df_sales", df_sales)
    conn.execute("""
        Insert into Fact_Sales(id_fact_sales, order_id, id_date_commande, id_date_expedition, customer_id, product_id, id_dim_location, id_dim_shipping, sales, quantity, discount, profit, shipping_delay)
        SELECT ligne_id, commande_id, date_commande_id, date_expedition_id, client_id, produit_id, geographie_id, mode_expedition_id, ventes, quantite, remise, profit, delai_expedition
        FROM df_sales
        ON CONFLICT (id_fact_sales) DO NOTHING
    """)
    conn.commit()
    conn.unregister("df_sales")

def run_analytique():
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
        run_analytique()
    except Exception as e:
        lg.error(f"Erreur Pendant le chargement : {e}")
        raise
    finally:
        conn.close()