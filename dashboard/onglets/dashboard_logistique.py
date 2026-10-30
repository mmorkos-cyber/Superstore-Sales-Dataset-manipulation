from db import get_connection
from utils.logger import get_logger
import pandas as pd
import streamlit as st
import plotly.express as px

lg = get_logger("analyse", "analyse_error.log")


#=============================================
#Analyse Logistique
#=============================================

#Modes d'expedition
#=============================================
@st.cache_data
def get_performance_modes_expedition(annees, regions):
    try:
        with get_connection() as con:
            return con.execute("""
            SELECT count(DISTINCT s.order_id) as nbr_commande_modes, sum(s.sales) as ca_modes, sum(s.profit) as profit_modes, sh.shipping_mode
            FROM Fact_Sales s
            JOIN Dim_Shipping sh ON s.id_dim_shipping = sh.id_dim_shipping
            JOIN Dim_Date d ON s.id_date_commande = d.date_id
            JOIN Dim_Location l ON s.id_dim_location = l.id_dim_location
            WHERE list_contains(?, d.annee) AND list_contains(?, l.region)
            GROUP BY sh.shipping_mode
            ORDER BY nbr_commande_modes DESC
        """, [annees, regions]).df()
    except Exception as e:
        lg.error(f"Erreur extraction performance modes expédition : {e}")
        return pd.DataFrame()

@st.cache_data
def get_delai_expedition(annees, regions):
    try:
        with get_connection() as con:
            return con.execute("""
                SELECT AVG(s.shipping_delay) as delai_moyen, sh.shipping_mode
                FROM Fact_Sales s
                JOIN Dim_Shipping sh ON s.id_dim_shipping = sh.id_dim_shipping
                JOIN Dim_Date d ON s.id_date_commande = d.date_id
                JOIN Dim_Location l ON s.id_dim_location = l.id_dim_location
                WHERE list_contains(?, d.annee) AND list_contains(?, l.region)
                GROUP BY sh.shipping_mode
                ORDER BY delai_moyen
            """, [annees, regions]).df()
    except Exception as e:
        lg.error(f"Erreur extraction délai expédition : {e}")
        return pd.DataFrame()


def render(annees, regions):
    modes = get_performance_modes_expedition(annees, regions)
    delais = get_delai_expedition(annees, regions)

    if modes.empty or delais.empty:
        st.error("Données logistiques indisponibles : voir les logs")
        return

    gauche, droite = st.columns(2)

    fig_modes = px.bar(modes, x="shipping_mode", y="nbr_commande_modes", text_auto=True, title="Nombre de commandes par mode d'expédition", labels={"shipping_mode": "", "nbr_commande_modes": "Commandes"})
    gauche.plotly_chart(fig_modes)

    fig_delais = px.bar(delais, x="shipping_mode", y="delai_moyen", text_auto=".1f", title="Délai moyen d'expédition (jours)", labels={"shipping_mode": "", "delai_moyen": "Jours"})
    droite.plotly_chart(fig_delais)