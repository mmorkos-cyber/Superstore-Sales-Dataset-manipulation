from db import get_connection
from utils.logger import get_logger
from pathlib import Path
import joblib
import pandas as pd
import plotly.express as px
import streamlit as st

lg = get_logger("analyse", "analyse_error.log")

FICHIER_MODELE = Path(__file__).resolve().parents[2] / "data" / "modeles" / "prediction_ventes.joblib"

CATEGORIES = ["Furniture", "Office Supplies", "Technology"]
REGIONS = ["Central", "East", "South", "West"]
NOMS_MOIS = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]


#=============================================
#Prévision des ventes
#=============================================

@st.cache_resource
def charger_modele():
    try:
        return joblib.load(FICHIER_MODELE)
    except Exception as e:
        lg.error(f"Erreur chargement du modèle : {e}")
        return None

@st.cache_data
def get_ventes_mensuelles(categorie, region):
    try:
        with get_connection() as con:
            return con.execute("""
                SELECT d.annee, d.mois, sum(s.sales) as ventes
                FROM Fact_Sales s
                JOIN Dim_Date d ON s.id_date_commande = d.date_id
                JOIN Dim_Product p ON s.product_id = p.product_id
                JOIN Dim_Location l ON s.id_dim_location = l.id_dim_location
                WHERE p.product_category = ? AND l.region = ?
                GROUP BY d.annee, d.mois
                ORDER BY d.annee, d.mois
            """, [categorie, region]).df()
    except Exception as e:
        lg.error(f"Erreur extraction ventes mensuelles : {e}")
        return pd.DataFrame()


def render(annees, regions):
    modele = charger_modele()
    if modele is None:
        st.error("Modèle indisponible : lancez d'abord l'entraînement (python main.py)")
        return

    gauche, droite = st.columns(2)
    categorie = gauche.selectbox("Catégorie", CATEGORIES)
    region = droite.selectbox("Région", REGIONS)

    historique = get_ventes_mensuelles(categorie, region)
    if historique.empty:
        st.error("Données de ventes indisponibles : voir les logs")
        return

    annee_prevue = int(historique["annee"].max()) + 1

    X_futur = pd.DataFrame({
        "annee": [annee_prevue] * 12,
        "mois": list(range(1, 13)),
        "product_category": [categorie] * 12,
        "region": [region] * 12
    })

    prevision = X_futur.copy()
    prevision["ventes"] = modele.predict(X_futur).clip(min=0)
    prevision["nom_mois"] = prevision["mois"].map(lambda m: NOMS_MOIS[m - 1])

    st.metric(f"Chiffre d'affaires prévu en {annee_prevue}", f"{prevision['ventes'].sum():,.0f} $")

    historique["periode"] = pd.to_datetime(dict(year=historique["annee"], month=historique["mois"], day=1))
    fig_historique = px.line(historique, x="periode", y="ventes", markers=True, title=f"Historique des ventes : {categorie}, région {region}", labels={"periode": "", "ventes": "Chiffre d'affaires ($)"})
    st.plotly_chart(fig_historique, use_container_width=True)

    fig_prevision = px.bar(prevision, x="nom_mois", y="ventes", text_auto=",.0f", title=f"Prévision {annee_prevue} : {categorie}, région {region}", labels={"nom_mois": "", "ventes": "Chiffre d'affaires prévu ($)"})
    st.plotly_chart(fig_prevision, use_container_width=True)

    st.caption("Prévision issue du modèle entraîné sur l'historique des ventes. Son erreur moyenne est élevée : les valeurs donnent un ordre de grandeur, pas une prévision précise.")