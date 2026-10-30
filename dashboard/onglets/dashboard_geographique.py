from db import get_connection
from utils.logger import get_logger
import pandas as pd
import streamlit as st
import plotly.express as px

lg = get_logger("analyse", "analyse_error.log")

CODES_ETATS = {"Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"}

#=============================================
#Analyse Géographique
#=============================================

@st.cache_data
def get_vente_etat(annees, regions):
    try:
        with get_connection() as con:
            return con.execute("""
                    SELECT l.state, l.region, sum(s.sales) as ca_etat, sum(s.profit) as profit_etat
                    FROM Fact_Sales s
                    JOIN Dim_Location l ON s.id_dim_location = l.id_dim_location
                    JOIN Dim_Date d ON s.id_date_commande = d.date_id
                    WHERE list_contains(?, d.annee) AND list_contains(?, l.region)
                    GROUP BY l.state, l.region
                    ORDER BY ca_etat DESC
                """, [annees, regions]).df()
    except Exception as e:
        lg.error(f"Erreur extraction ventes par état : {e}")
        return pd.DataFrame()


def render(annees, regions):
    ventes_etat = get_vente_etat(annees, regions)
    if ventes_etat.empty:
        st.error("Données géographiques indisponibles : voir les logs")
        return

    ventes_etat["code_etat"] = ventes_etat["state"].map(CODES_ETATS)

    fig_carte = px.choropleth(ventes_etat, locations="code_etat", locationmode="USA-states", scope="usa", color="ca_etat", hover_name="state", hover_data={"code_etat": False, "region": True, "ca_etat": ":,.0f", "profit_etat": ":,.0f"}, color_continuous_scale="Blues", title="Chiffre d'affaires par état", labels={"ca_etat": "CA ($)", "profit_etat": "Profit ($)", "region": "Région"})
    st.plotly_chart(fig_carte, use_container_width=True)