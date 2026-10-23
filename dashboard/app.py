import streamlit as st
from onglets import (vue_kpi, dashboard_clients, dashboard_commerciale, dashboard_geographique, dashboard_logistique, dashboard_rentabilite, dashboard_temporelle)
 
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
}
 
for onglet, module in zip(st.tabs(list(ONGLETS)), ONGLETS.values()):
    with onglet:
        module.render()