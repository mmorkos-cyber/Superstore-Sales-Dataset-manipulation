from db import get_connection
from utils.logger import get_logger
import pandas as pd
import plotly.express as px
import streamlit as st
 
lg = get_logger("analyse", "analyse_error.log")


#=============================================
#vue KPI
#=============================================
@st.cache_data
def get_general_kpi_evolution():
    try: 
        with get_connection() as con:
            return con.execute("""
                SELECT sum(s.sales) as ca_total, sum(s.profit) as profit_total, count(DISTINCT s.order_id) as nb_commandes_total, sum(s.quantity) as quantite_vendue, (sum(s.profit) / / NULLIF(sum(s.sales),0) as marge_globale, (sum(s.profit) / NULLIF(sum(s.quantity),0) as profit_moyen_article, d.year, d.month
                FROM Fact_sales s 
                JOIN Dim_Date d ON s.id_dim_date = d.id_dim_date
                GROUP BY d.year, d.month
                ORDER BY d.year DESC, d.month DESC
            """).df()
    except Exception as e:
        lg.error(f"Erreur durant la saisie des KPIs general : {e}")
        return pd.DataFrame()

@st.cache_data
def get_top_produits():
    try:
        with get_connection() as con:
            return con.execute("""
                SELECT p.product_name, sum(s.quantity) as qte_vendue
                From  Fact_sales s
                JOIN Dim_Product p ON s.id_dim_product = p.id_dim_product
                GROUP BY p.product_name
                ORDER BY qte_vendue DESC
            """).df()
    except Exception as e:
        lg.error(f"Erreur durant la saisie des Tops produits : {e}")
        return pd.DataFrame()

@st.cache_data
def get_rentabilite_categories():
    try:
        with get_connection() as con:
            return con.execute("""
                SELECT sum(s.profit) as total_profit_cat, p.product_category 
                FROM Fact_sales s 
                JOIN Dim_Product p ON s.id_dim_product = p.id_dim_product
                GROUP BY p.product_category
                ORDER BY total_profit_cat DESC
            """).df()
    except Exception as e:
        lg.error(f"Erreur durant la saisie des Categories les plus rentables : {e}")
        return pd.DataFrame()

def fmt(n):
    return f"{n:,.0f}".replace(",", " ")
 
def render():
    evo = get_general_kpi_evolution()
    if evo.empty:
        st.error("KPIs indisponibles : voir logs/analyse_error.log")
        return
 
    ca = evo["ca_total"].sum()
    profit = evo["profit_total"].sum()
    commandes = evo["nb_commandes_total"].sum()
 
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Chiffre d'affaires", f"{fmt(ca)} $")
    c2.metric("Profit", f"{fmt(profit)} $")
    c3.metric("Marge globale", f"{profit / ca:.1%}")
    c4.metric("Commandes", fmt(commandes))
    evo = evo.sort_values(["year", "month"])
    dates = evo[["year", "month"]].assign(day=1)
    evo["periode"] = pd.to_datetime(dates)

    g = evo.rename(columns={"ca_total": "CA", "profit_total": "Profit"})
    fig = px.line(g, x="periode", y=["CA", "Profit"],
                  title="Évolution mensuelle du CA et du profit",
                  labels={"periode": "Mois", "value": "Montant ($)",
                          "variable": ""},
                  markers=True)
    st.plotly_chart(fig)
    gauche, droite = st.columns(2)

    top = get_top_produits().head(10)
    if not top.empty:
        fig_top = px.bar(top, x="qte_vendue", y="product_name",
                         orientation="h", title="Top 10 produits",
                         labels={"qte_vendue": "Quantité vendue",
                                 "product_name": ""})
        fig_top.update_layout(yaxis={"categoryorder": "total ascending"})
        gauche.plotly_chart(fig_top)
    cat = get_rentabilite_categories()
    if not cat.empty:
        fig_cat = px.bar(cat, x="product_category", y="total_profit_cat",
                         text_auto=".3s", title="Profit par catégorie",
                         labels={"product_category": "",
                                 "total_profit_cat": "Profit ($)"})
        droite.plotly_chart(fig_cat)