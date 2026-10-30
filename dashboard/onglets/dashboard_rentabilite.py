from db import get_connection
from utils.logger import get_logger
import pandas as pd
import streamlit as st
import plotly.express as px

lg = get_logger("analyse", "analyse_error.log")

COULEURS_RESULTAT = {"Gain": "#2E86AB", "Perte": "#D64545"}

#=============================================
#Analyse Rentabilite
#=============================================

@st.cache_data
def get_rentabilite_cat(annees, regions):
    try:
        with get_connection() as con:
            return con.execute("""
                SELECT p.product_category, sum(s.profit) as profit_cat, (sum(s.profit) / NULLIF(sum(s.sales),0)) as marge
                FROM Fact_Sales s
                JOIN Dim_Product p ON s.product_id = p.product_id
                JOIN Dim_Date d ON s.id_date_commande = d.date_id
                JOIN Dim_Location l ON s.id_dim_location = l.id_dim_location
                WHERE list_contains(?, d.annee) AND list_contains(?, l.region)
                GROUP BY p.product_category
                ORDER BY profit_cat DESC
            """, [annees, regions]).df()
    except Exception as e:
        lg.error(f"Erreur extraction rentabilité par catégorie : {e}")
        return pd.DataFrame()

@st.cache_data
def get_rentabilite_sous_cat(annees, regions):
    try:
        with get_connection() as con:
            return con.execute("""
                SELECT p.product_sub_category, sum(s.profit) as sous_cat_profit
                FROM Fact_Sales s
                JOIN Dim_Product p ON s.product_id = p.product_id
                JOIN Dim_Date d ON s.id_date_commande = d.date_id
                JOIN Dim_Location l ON s.id_dim_location = l.id_dim_location
                WHERE list_contains(?, d.annee) AND list_contains(?, l.region)
                GROUP BY p.product_sub_category
                ORDER BY sous_cat_profit DESC
            """, [annees, regions]).df()
    except Exception as e:
        lg.error(f"Erreur extraction rentabilité par sous-catégorie : {e}")
        return pd.DataFrame()

@st.cache_data
def get_rentabilite_remise(annees, regions):
    try:
        with get_connection() as con:
            return con.execute("""
                SELECT s.discount, sum(s.profit) as profit_remise
                FROM Fact_Sales s
                JOIN Dim_Date d ON s.id_date_commande = d.date_id
                JOIN Dim_Location l ON s.id_dim_location = l.id_dim_location
                WHERE list_contains(?, d.annee) AND list_contains(?, l.region)
                GROUP BY s.discount
                ORDER BY s.discount
            """, [annees, regions]).df()
    except Exception as e:
        lg.error(f"Erreur extraction rentabilité par remise : {e}")
        return pd.DataFrame()

@st.cache_data
def get_produits_moins_rentables(annees, regions):
    try:
        with get_connection() as con:
            return con.execute("""
                SELECT p.product_name, sum(s.profit) as rentabilite_prod, sum(s.sales) as total_vente
                FROM Fact_Sales s
                JOIN Dim_Product p ON s.product_id = p.product_id
                JOIN Dim_Date d ON s.id_date_commande = d.date_id
                JOIN Dim_Location l ON s.id_dim_location = l.id_dim_location
                WHERE list_contains(?, d.annee) AND list_contains(?, l.region)
                GROUP BY p.product_name
                ORDER BY rentabilite_prod ASC
                LIMIT 10
            """, [annees, regions]).df()
    except Exception as e:
        lg.error(f"Erreur extraction produits les moins rentables : {e}")
        return pd.DataFrame()


def render(annees, regions):
    renta_cat = get_rentabilite_cat(annees, regions)
    renta_sous_cat = get_rentabilite_sous_cat(annees, regions)
    renta_remise = get_rentabilite_remise(annees, regions)
    produits_pertes = get_produits_moins_rentables(annees, regions)

    if renta_cat.empty or renta_sous_cat.empty:
        st.error("Données de rentabilité indisponibles : voir les logs")
        return

    colonnes = st.columns(len(renta_cat))
    for colonne, (_, ligne) in zip(colonnes, renta_cat.iterrows()):
        colonne.metric(f"{ligne['product_category']} (marge {ligne['marge']:.1%})", f"{ligne['profit_cat']:,.0f} $")

    renta_sous_cat["resultat"] = renta_sous_cat["sous_cat_profit"].apply(lambda p: "Perte" if p < 0 else "Gain")
    fig_sous_cat = px.bar(renta_sous_cat, x="sous_cat_profit", y="product_sub_category", color="resultat", color_discrete_map=COULEURS_RESULTAT, orientation="h", title="Profit par sous-catégorie", labels={"sous_cat_profit": "Profit ($)", "product_sub_category": "", "resultat": ""})
    fig_sous_cat.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_sous_cat, use_container_width=True)

    if not renta_remise.empty:
        renta_remise["remise"] = renta_remise["discount"].apply(lambda d: f"{d:.0%}")
        renta_remise["resultat"] = renta_remise["profit_remise"].apply(lambda p: "Perte" if p < 0 else "Gain")
        fig_remise = px.bar(renta_remise, x="remise", y="profit_remise", color="resultat", color_discrete_map=COULEURS_RESULTAT, title="Profit par niveau de remise", labels={"remise": "Remise", "profit_remise": "Profit ($)", "resultat": ""})
        st.plotly_chart(fig_remise, use_container_width=True)

    if not produits_pertes.empty:
        st.subheader("Les 10 produits les moins rentables")
        st.dataframe(produits_pertes, hide_index=True)