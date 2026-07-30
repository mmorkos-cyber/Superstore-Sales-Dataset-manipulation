import os
import sys
import duckdb
import pandas as pd

dossier_root =  os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(dossier_root)

from utils.logger import get_logger
lg = get_logger("analyse", "analyse_error.log")
fichier_db = os.path.join(dossier_root, "Superstore.db")

con = duckdb.connect(fichier_db)

#=============================================
#Analyse Vente
#=============================================

#categories les plus vendues
df_cat_vent = con.execute("""
        SELECT sum(s.sales) as total_sales_cat, p.product_category 
        FROM Fact_sales s 
        JOIN Dim_Product p ON s.id_dim_product = p.id_dim_product
        GROUP BY p.product_category
        ORDER BY total_sales_cat DESC
    """).df()

#categories les plus rentables
df_cat_rentable = con.execute("""
        SELECT sum(s.profit) as total_profit_cat, p.product_category 
        FROM Fact_sales s 
        JOIN Dim_Product p ON s.id_dim_product = p.id_dim_product
        GROUP BY p.product_category
        ORDER BY total_profit_cat DESC
    """).df()

#produits les plus rentables
df_prod_rentable = con.execute("""
        SELECT sum(s.profit) as total_profit_prod, p.product_name
        FROM Fact_sales s 
        JOIN Dim_Product p ON s.id_dim_product = p.id_dim_product
        GROUP BY p.product_name
        ORDER BY total_profit_prod DESC
        LIMIT 10
    """).df()


#produits les moins rentables
df_prod_moins_rent = con.execute("""
        SELECT sum(s.profit) as total_profit_prod, p.product_name
        FROM Fact_sales s 
        JOIN Dim_Product p ON s.id_dim_product = p.id_dim_product
        GROUP BY p.product_name
        ORDER BY total_profit_prod ASC
        LIMIT 10
    """).df()

#evolution des ventes dans le temps
df_vent_temps = con.execute("""
        SELECT sum(s.sales) as total_sales_temps, d.year, d.month
        FROM Fact_sales s 
        JOIN Dim_Date d ON s.id_dim_date = d.id_dim_date
        GROUP BY d.year, d.month
        ORDER BY d.year, d.month
    """).df()

#=============================================
#Analyse Geographic
#=============================================

#performance par etat
df_perf_etat = con.execute("""
        SELECT sum(s.profit) as total_profit_etat, l.state
        FROM Fact_sales s 
        JOIN Dim_Location l ON s.id_dim_location = l.id_dim_location
        GROUP BY l.state
        ORDER BY total_profit_etat DESC
    """).df()

#=============================================
#Analyse Clients
#=============================================

#vente par segment de client
df_vente_segment = con.execute("""
        SELECT sum(s.quantity) as total_vente_segment, c.segment
        FROM Fact_sales s 
        JOIN Dim_Customer c ON s.id_dim_customer = c.id_dim_customer
        GROUP BY c.segment
        ORDER BY total_vente_segment DESC
    """).df()

#=============================================
#Analyse des Expeditions
#=============================================

#moyen d'expeditions les plus utiliser
df_moyen_expedition = con.execute("""
        SELECT count(s.order_id) as nbr_commande_expedition, sh.shipping_mode
        FROM Fact_sales s 
        JOIN Dim_Shipping sh ON s.id_dim_shipping = sh.id_dim_shipping
        GROUP BY sh.shipping_mode
        ORDER BY nbr_commande_expedition DESC
    """).df()

#oyen d'expeditions avec le plus de ventes
df_vente_expedition = con.execute("""
        SELECT sum(s.sales) as vente_expedition, sh.shipping_mode
        FROM Fact_sales s 
        JOIN Dim_Shipping sh ON s.id_dim_shipping = sh.id_dim_shipping
        GROUP BY sh.shipping_mode
        ORDER BY vente_expedition DESC
    """).df()

#moyen d'expeditions les plus rentables
df_expedition_rentable = con.execute("""
        SELECT sum(s.profit) as total_profit_expedition, sh.shipping_mode
        FROM Fact_sales s 
        JOIN Dim_Shipping sh ON s.id_dim_shipping = sh.id_dim_shipping
        GROUP BY p.sh.shipping_mode
        ORDER BY total_profit_expedition DESC
    """).df()

#delai d'expedition moyen
#fix the type of shipping_date in table Fact_Sales it is VARCHAR now and use DATEDIFF to find the time between order and shipping 
df_delai_expedition = con.execute("""
        SELECT s.shipping_date, d.date_complete
        FROM Fact_sales s 
        JOIN Dim_Date d ON s.id_dim_date = d.id_dim_date
    """).df()



