import streamlit as st
from dashboard.onglets import (vue_kpi, dashboard_clients, dashboard_commerciale, dashboard_geographique, dashboard_logistique, dashboard_rentabilite, dashboard_temporelle, dashboard_prevision)
from db import get_connection

st.set_page_config(page_title="Superstore Sales", layout="wide")
st.title("Tableau de bord Superstore Sales")
 
ONGLETS = {
    "Vue KPI": vue_kpi,
    "Clients": dashboard_clients,
    "Commerciale": dashboard_commerciale,
    "Géographique": dashboard_geographique,
    "Logistique": dashboard_logistique,
    "Rentabilité": dashboard_rentabilite,
    "Temporelle": dashboard_temporelle,
    "Prévision": dashboard_prevision,
}


@st.cache_data
def get_options_filtres():
    with get_connection() as con:
        annees = con.execute("""
            SELECT DISTINCT d.annee
            FROM Fact_Sales s
            JOIN Dim_Date d ON s.id_date_commande = d.date_id
            ORDER BY d.annee
        """).df()["annee"].tolist()
        regions = con.execute("""
            SELECT DISTINCT region FROM Dim_Location ORDER BY region
        """).df()["region"].tolist()
    return annees, regions


def dashboard():
    annees_dispo, regions_dispo = get_options_filtres()

    st.sidebar.header("Filtres")
    annees = st.sidebar.multiselect("Années", annees_dispo, default=annees_dispo)
    regions = st.sidebar.multiselect("Régions", regions_dispo, default=regions_dispo)

    if not annees or not regions:
        st.warning("Sélectionnez au moins une année et une région.")
        return

    for onglet, module in zip(st.tabs(list(ONGLETS)), ONGLETS.values()):
        with onglet:
            module.render(annees, regions)

if __name__ == "__main__":
    dashboard()