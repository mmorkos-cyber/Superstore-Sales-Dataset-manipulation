from db import get_connection
from utils.logger import get_logger
import pandas as pd

lg = get_logger("analyse", "analyse_error.log")

#=============================================
#Analyse Commerciale
#=============================================


def get_vente_categorie():
    try: 
        with get_connection() as con:
            return con.execute("""
                    SELECT sum(s.sales) as total_sales_cat, p.product_category 
                    FROM Fact_sales s 
                    JOIN Dim_Product p ON s.id_dim_product = p.id_dim_product
                    GROUP BY p.product_category
                    ORDER BY total_sales_cat DESC
                """).df()
    except Exception as e:
        lg.error(f"Erreur extraction vente de categorie : {e}")
        return pd.DataFrame()


def get_vente_sous_categorie():
    try:
        with get_connection() as con:
            return con.execute("""
                    SELECT sum(s.sales) as sous_cat_ca, p.product_sub_category 
                    FROM Fact_sales s 
                    JOIN Dim_Product p ON s.id_dim_product = p.id_dim_product
                    GROUP BY p.product_sub_category
                    ORDER BY sous_cat_ca DESC
                """).df()
    except Exception as e:
        lg.error(f"Erreur extraction vente de sous-categorie : {e}")
        return pd.DataFrame()

def get_performance_produits():
    try:
        with get_connection() as con:
            return con.execute("""
                    SELECT sum(s.sales) as prod_ca, sum(s.quantity) as qte_vendue, p.product_name
                    FROM Fact_sales s 
                    JOIN Dim_Product p ON s.id_dim_product = p.id_dim_product
                    GROUP BY p.product_name
                    ORDER BY prod_ca DESC
                """).df()
    except Exception as e:
        lg.error(f"Erreur extraction performance produits : {e}")
        return pd.DataFrame()

def get_vente_segment():
    try:
        with get_connection() as con:
            return con.execute("""
                SELECT sum(s.sales) as ca_segment, c.segment
                FROM Fact_sales s 
                JOIN Dim_Customer c ON s.id_dim_customer = c.id_dim_customer
                GROUP BY c.segment
                ORDER BY ca_segment DESC
            """).df()
    except Exception as e:
        lg.error(f"Erreur extraction ventes par segment : {e}")
        return pd.DataFrame()

def get_top_clients():
    try:
        with get_connection() as con:
            return con.execute("""
                SELECT count(DISTINCT s.order_id) as nbr_commande, c.customer_name, c.segment, c.customer_id
                FROM Fact_sales s
                JOIN Dim_Customer c ON s.id_dim_customer = c.id_dim_customer
                GROUP BY c.customer_id, c.customer_name, c.segment
                ORDER BY nbr_commande DESC
                LIMIT 10
            """).df()
    except Exception as e:
            lg.error(f"Erreur extraction top clients : {e}")
            return pd.DataFrame()


def get_performance_geographique():
    try:
        with get_connection() as con:
            return con.execute("""
                SELECT sum(s.sales) as chiffre_affaire, l.state, l.region
                FROM Fact_sales s 
                JOIN Dim_Location l ON s.id_dim_location = l.id_dim_location
                GROUP BY  l.state, l.region
                ORDER BY chiffre_affaire DESC
            """).df()
    except Exception as e:
        lg.error(f"Erreur extraction performance géographique : {e}")
        return pd.DataFrame()
    