from db import get_connection
from utils.logger import get_logger
import pandas as pd

lg = get_logger("analyse", "analyse_error.log")

#=============================================
#Analyse Geographique
#=============================================

def get_performance_regionale():
    try:
        with get_connection() as con:
            return con.execute("""
                SELECT sum(s.sales) as ca_region, sum(s.profit) as profit_region, l.region, (sum(s.profit) / NULLIF(sum(s.sales),0)) as marge
                FROM Fact_sales s 
                JOIN Dim_Location l ON s.id_dim_location = l.id_dim_location
                GROUP BY l.region
                ORDER BY ca_region DESC
            """).df()
    except Exception as e:
        lg.error(f"Erreur extraction performance régionale : {e}")
        return pd.DataFrame()    


def get_performance_locale():
    try:
        with get_connection() as con:
            return con.execute("""
                SELECT sum(s.sales) as ca_etat, sum(s.profit) as total_profit_etat, l.state, l.region, (sum(s.profit) / NULLIF(sum(s.sales),0)) as marge
                FROM Fact_sales s 
                JOIN Dim_Location l ON s.id_dim_location = l.id_dim_location
                GROUP BY l.state, l.region
                ORDER BY ca_etat DESC
            """).df()
    except Exception as e:
        lg.error(f"Erreur extraction performance locale : {e}")
        return pd.DataFrame()

def get_top_villes():
    try:
        with get_connection() as con:
            return con.execute("""
                SELECT sum(s.sales) as ca_ville, sum(s.profit) as total_profit_ville, l.city
                FROM Fact_sales s 
                JOIN Dim_Location l ON s.id_dim_location = l.id_dim_location
                GROUP BY l.city
                ORDER BY ca_ville DESC
                LIMIT 10
            """).df()
    except Exception as e:
        lg.error(f"Erreur extraction top villes : {e}")
        return pd.DataFrame()
