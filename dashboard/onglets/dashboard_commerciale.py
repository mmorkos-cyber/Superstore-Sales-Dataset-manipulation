from db import get_connection
from utils.logger import get_logger
import pandas as pd
import streamlit as st
import plotly.express as px

lg = get_logger("analyse", "analyse_error.log")

#=============================================
#Analyse Commerciale
#=============================================

@st.cache_data
def get_vente_categorie(annees, regions):
    try:
        with get_connection() as con:
            return con.execute("""
                    SELECT sum(s.sales) as total_sales_cat, p.product_category
                    FROM Fact_Sales s
                    JOIN Dim_Product p ON s.product_id = p.product_id
                    JOIN Dim_Date d ON s.id_date_commande = d.date_id
                    JOIN Dim_Location l ON s.id_dim_location = l.id_dim_location
                    WHERE list_contains(?, d.annee) AND list_contains(?, l.region)
                    GROUP BY p.product_category
                    ORDER BY total_sales_cat DESC
                """, [annees, regions]).df()
    except Exception as e:
        lg.error(f"Erreur extraction vente de categorie : {e}")
        return pd.DataFrame()

@st.cache_data
def get_vente_sous_categorie(annees, regions):
    try:
        with get_connection() as con:
            return con.execute("""
                    SELECT sum(s.sales) as sous_cat_ca, p.product_sub_category, p.product_category
                    FROM Fact_Sales s
                    JOIN Dim_Product p ON s.product_id = p.product_id
                    JOIN Dim_Date d ON s.id_date_commande = d.date_id
                    JOIN Dim_Location l ON s.id_dim_location = l.id_dim_location
                    WHERE list_contains(?, d.annee) AND list_contains(?, l.region)
                    GROUP BY p.product_sub_category, p.product_category
                    ORDER BY sous_cat_ca DESC
                """, [annees, regions]).df()
    except Exception as e:
        lg.error(f"Erreur extraction vente de sous-categorie : {e}")
        return pd.DataFrame()

@st.cache_data
def get_performance_produits(annees, regions):
    try:
        with get_connection() as con:
            return con.execute("""
                    SELECT p.product_name, sum(s.sales) as prod_ca, sum(s.quantity) as qte_vendue
                    FROM Fact_Sales s
                    JOIN Dim_Product p ON s.product_id = p.product_id
                    JOIN Dim_Date d ON s.id_date_commande = d.date_id
                    JOIN Dim_Location l ON s.id_dim_location = l.id_dim_location
                    WHERE list_contains(?, d.annee) AND list_contains(?, l.region)
                    GROUP BY p.product_name
                    ORDER BY prod_ca DESC
                    LIMIT 10
                """, [annees, regions]).df()
    except Exception as e:
        lg.error(f"Erreur extraction performance produits : {e}")
        return pd.DataFrame()


def render(annees, regions):
    ventes_cat = get_vente_categorie(annees, regions)
    ventes_sous_cat = get_vente_sous_categorie(annees, regions)
    perf_produits = get_performance_produits(annees, regions)

    if ventes_cat.empty or ventes_sous_cat.empty:
        st.error("Données commerciales indisponibles : voir les logs")
        return

    colonnes = st.columns(len(ventes_cat))
    for colonne, (_, ligne) in zip(colonnes, ventes_cat.iterrows()):
        colonne.metric(ligne["product_category"], f"{ligne['total_sales_cat']:,.0f} $")

    fig_sous_cat = px.bar(ventes_sous_cat, x="sous_cat_ca", y="product_sub_category", color="product_category", orientation="h", title="Chiffre d'affaires par sous-catégorie", labels={"sous_cat_ca": "Chiffre d'affaires ($)", "product_sub_category": "", "product_category": "Catégorie"})
    fig_sous_cat.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_sous_cat, use_container_width=True)

    if not perf_produits.empty:
        st.subheader("Top 10 produits par chiffre d'affaires")
        st.dataframe(perf_produits, hide_index=True)