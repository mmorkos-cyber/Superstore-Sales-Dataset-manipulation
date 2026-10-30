from db import get_connection
from utils.logger import get_logger
import pandas as pd
import streamlit as st
import plotly.express as px

lg = get_logger("analyse", "analyse_error.log")


#=============================================
#Analyse Temporelle
#=============================================

@st.cache_data
def get_evolution_temporelle(annees, regions):
    try:
        with get_connection() as con:
            return con.execute("""
                SELECT d.annee, d.mois, d.nom_mois, sum(s.sales) as ca_temps, sum(s.quantity) as qte_temps, sum(s.profit) as total_renta_temps, (sum(s.profit) / NULLIF(sum(s.sales),0)) as marge
                FROM Fact_Sales s
                JOIN Dim_Date d ON s.id_date_commande = d.date_id
                JOIN Dim_Location l ON s.id_dim_location = l.id_dim_location
                WHERE list_contains(?, d.annee) AND list_contains(?, l.region)
                GROUP BY d.annee, d.mois, d.nom_mois
                ORDER BY d.annee, d.mois
            """, [annees, regions]).df()
    except Exception as e:
        lg.error(f"Erreur extraction évolution temporelle : {e}")
        return pd.DataFrame()


def render(annees, regions):
    evolution = get_evolution_temporelle(annees, regions)
    if evolution.empty:
        st.error("Données temporelles indisponibles : voir les logs")
        return

    ca_annuel = evolution.groupby("annee")["ca_temps"].sum().reset_index()
    ca_annuel["evolution"] = ca_annuel["ca_temps"].pct_change()

    colonnes = st.columns(len(ca_annuel))
    for colonne, (_, ligne) in zip(colonnes, ca_annuel.iterrows()):
        if pd.isna(ligne["evolution"]):
            colonne.metric(f"CA {int(ligne['annee'])}", f"{ligne['ca_temps']:,.0f} $")
        else:
            colonne.metric(f"CA {int(ligne['annee'])}", f"{ligne['ca_temps']:,.0f} $", delta=f"{ligne['evolution']:.1%}")

    evolution["periode"] = pd.to_datetime(dict(year=evolution["annee"], month=evolution["mois"], day=1))
    fig_tendance = px.line(evolution, x="periode", y="ca_temps", markers=True, title="Évolution mensuelle du chiffre d'affaires", labels={"periode": "", "ca_temps": "Chiffre d'affaires ($)"})
    st.plotly_chart(fig_tendance, use_container_width=True)

    evolution["annee_texte"] = evolution["annee"].astype(str)
    fig_saison = px.line(evolution, x="nom_mois", y="ca_temps", color="annee_texte", markers=True, title="Saisonnalité : chiffre d'affaires par mois et par année", labels={"nom_mois": "", "ca_temps": "Chiffre d'affaires ($)", "annee_texte": "Année"})
    st.plotly_chart(fig_saison, use_container_width=True)