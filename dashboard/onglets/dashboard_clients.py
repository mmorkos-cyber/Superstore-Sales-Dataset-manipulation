from db import get_connection
from utils.logger import get_logger
import pandas as pd
import plotly.express as px
import streamlit as st

lg = get_logger("analyse", "analyse_error.log")

#=============================================
#Analyse Clients
#=============================================

@st.cache_data
def get_performance_segments():
    try:
        with get_connection() as con:
            return con.execute("""
                SELECT count(c.customer_id) as client_count, sum(s.sales) as ca_segment, sum(s.profit) as renta_par_segment, c.segment
                FROM Fact_sales s
                JOIN Dim_Customer c ON s.id_dim_customer = c.id_dim_customer
                GROUP BY c.segment
                ORDER BY client_count DESC
            """).df()
    except Exception as e:
        lg.error(f"Erreur extraction performance segments clients : {e}")
        return pd.DataFrame()

@st.cache_data
def get_performance_clients():
    try:
        with get_connection() as con:
            return con.execute("""
                SELECT sum(s.sales) as ventes_totale, sum(s.profit) as renta_client, count(s.order_id) as nbr_commande, c.customer_name, c.segment, c.customer_id
                FROM Fact_sales s
                JOIN Dim_Customer c ON s.id_dim_customer = c.id_dim_customer
                GROUP BY c.customer_name, c.segment, c.customer_id
                ORDER BY ventes_totale DESC
            """).df()
    except Exception as e:
        lg.error(f"Erreur extraction performance clients : {e}")
        return pd.DataFrame()

def render():
    seg = get_performance_segments()
    if seg.empty:
        st.error("Données clients indisponibles : voir les logs")
        return
 
    gauche, droite = st.columns(2)
    fig_nb = px.pie(seg, names="segment", values="client_count",
                    hole=0.5, title="Répartition des clients")
    gauche.plotly_chart(fig_nb)
 
    fig_ca = px.bar(seg, x="segment",
                    y=["ca_segment", "renta_par_segment"],
                    barmode="group", title="CA et profit par segment",
                    labels={"value": "Montant ($)", "variable": ""})
    droite.plotly_chart(fig_ca)
 
    clients = get_performance_clients()
    if not clients.empty:
        fig_cli = px.scatter(clients, x="ventes_totale",
                             y="renta_client", color="segment",
                             hover_name="customer_name",
                             title="Chaque point est un client")
        st.plotly_chart(fig_cli)
        st.subheader("Top 10 clients par chiffre d'affaires")
        st.dataframe(clients.head(10), hide_index=True)
