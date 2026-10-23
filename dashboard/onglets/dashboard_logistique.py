from db import get_connection
from utils.logger import get_logger
import pandas as pd

lg = get_logger("analyse", "analyse_error.log")


#=============================================
#Analyse Logistique
#=============================================

#Modes d'expedition
#=============================================
def get_performance_modes_expedition():
    try:
        with get_connection() as con:
            return con.execute("""
            SELECT count(DISTINCT s.order_id) as nbr_commande_modes, sum(s.sales) as ca_modes, sum(s.profit) as profit_modes, sh.shipping_mode
            FROM Fact_sales s 
            JOIN Dim_Shipping sh ON s.id_dim_shipping = sh.id_dim_shipping
            GROUP BY sh.shipping_mode
            ORDER BY nbr_commande_modes DESC
        """).df()
    except Exception as e:
        lg.error(f"Erreur extraction performance modes expédition : {e}")
        return pd.DataFrame()


def get_delai_expedition():
    try:
        with get_connection() as  con:
            return con.execute("""
                SELECT AVG(DATEDIFF('day', d.date_complete, s.shipping_date)) as delai_moyen, sh.shipping_mode
                FROM Fact_sales s 
                JOIN Dim_Date d ON s.id_dim_date = d.id_dim_date
                JOIN Dim_Shipping sh ON s.id_dim_shipping = sh.id_dim_shipping
                GROUP BY sh.shipping_mode
                ORDER BY delai_moyen
            """).df()
    except Exception as e:
        lg.error(f"Erreur extraction délai expédition : {e}")
        return pd.DataFrame()
