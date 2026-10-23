from db import get_connection
from utils.logger import get_logger
import pandas as pd

lg = get_logger("analyse", "analyse_error.log")


#=============================================
#Analyse Temporelle
#=============================================

def get_evolution_temporelle():
    try:
        with get_connection() as con:
            return con.execute("""
                SELECT sum(s.sales) as ca_temps, sum(s.quantity) as qte_temps, sum(s.profit) as total_renta_temps, (sum(s.profit) / NULLIF(sum(s.sales),0)) as marge, d.year, d.month
                FROM Fact_sales s 
                JOIN Dim_Date d ON s.id_dim_date = d.id_dim_date
                GROUP BY d.year, d.month
                ORDER BY d.year, d.month
            """).df()
    except Exception as e:
        lg.error(f"Erreur extraction évolution temporelle : {e}")
        return pd.DataFrame()

