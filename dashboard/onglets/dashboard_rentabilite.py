from db import get_connection
from utils.logger import get_logger
import pandas as pd

lg = get_logger("analyse", "analyse_error.log")

#=============================================
#Analyse Rentabilite
#=============================================


def get_rentabilite_cat():
    try: 
        with get_connection() as con:
            return con.execute("""
                SELECT sum(s.profit) as profit_cat, p.product_category 
                FROM Fact_sales s 
                JOIN Dim_Product p ON s.id_dim_product = p.id_dim_product
                GROUP BY p.product_category
                ORDER BY profit_cat DESC
            """).df()
    except Exception as e:
        lg.error(f"Erreur extraction rentabilité par catégorie : {e}")
        return pd.DataFrame()


def get_rentabilite_sous_cat():
    try: 
        with get_connection() as con:
            return con.execute("""
                SELECT sum(s.profit) as sous_cat_profit, p.product_sub_category 
                FROM Fact_sales s 
                JOIN Dim_Product p ON s.id_dim_product = p.id_dim_product
                GROUP BY p.product_sub_category
                ORDER BY sous_cat_profit DESC
            """).df()
    except Exception as e:
        lg.error(f"Erreur extraction rentabilité par sous-catégorie : {e}")
        return pd.DataFrame()

def get_rentabilite_produit():
    try:
        with get_connection() as con:
            return con.execute("""
                SELECT sum(s.profit) as rentabilite_prod, sum(s.sales) as total_vente, p.product_name
                FROM Fact_sales s 
                JOIN Dim_Product p ON s.id_dim_product = p.id_dim_product
                GROUP BY p.product_name
                ORDER BY rentabilite_prod DESC
            """).df()
    except Exception as e:
        lg.error(f"Erreur extraction rentabilité produits : {e}")
        return pd.DataFrame()

def get_rentabilite_segment():
    try:
        with get_connection() as con:
            return con.execute("""
                SELECT sum(s.profit) as renta_par_segment, c.segment
                FROM Fact_sales s
                JOIN Dim_Customer c ON s.id_dim_customer = c.id_dim_customer
                GROUP BY c.segment
                ORDER BY renta_par_segment DESC
            """).df()
    except Exception as e:
        lg.error(f"Erreur extraction rentabilité par segment client : {e}")
        return pd.DataFrame()

def get_top_clients_rentable():
    try:
        with get_connection() as con:
            return con.execute("""
                SELECT sum(s.profit) as renta_client, c.customer_name, c.segment, c.customer_id
                FROM Fact_sales s
                JOIN Dim_Customer c ON s.id_dim_customer = c.id_dim_customer
                GROUP BY c.customer_id, c.customer_name, c.segment
                ORDER BY renta_client DESC
                LIMIT 10
            """).df()
    except Exception as e:
        lg.error(f"Erreur extraction top clients rentables : {e}")
        return pd.DataFrame()

def get_rentabilite_geographique():
    try:
        with get_connection() as con:
            return con.execute("""
                SELECT sum(s.profit) as rentabilite, l.state, l.region
                FROM Fact_sales s 
                JOIN Dim_Location l ON s.id_dim_location = l.id_dim_location
                GROUP BY l.state, l.region
                ORDER BY rentabilite DESC
            """).df()
    except Exception as e:
        lg.error(f"Erreur extraction rentabilité géographique : {e}")
        return pd.DataFrame()

def get_marge_categorie():
    try:
        with get_connection() as con:
            return con.execute("""
                SELECT (sum(s.profit) / NULLIF(sum(s.sales),0)) as marge, p.product_category 
                FROM Fact_sales s 
                JOIN Dim_Product p ON s.id_dim_product = p.id_dim_product
                GROUP BY p.product_category
                ORDER BY marge DESC
            """).df()
    except Exception as e:
            lg.error(f"Erreur extraction marge par catégorie : {e}")
            return pd.DataFrame()
