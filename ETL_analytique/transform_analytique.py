from ETL_analytique.extraction_analytique import df_dim_client, df_dim_geographie, df_dim_produit, df_modes, df_faits
import pandas as pd
from utils.logger import get_logger
import os

lg = get_logger("etl", "ETL_error.log")
dossier_root =  os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


debut = df_faits["date_commande"].min()
fin = df_faits["date_expedition"].max()

NOMS_MOIS = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
NOMS_JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

#preparation Dim_Date
def dim_date_prep():
    df_dim_date = pd.DataFrame({"date": pd.date_range(debut, fin, freq="D")})
    df_dim_date["date_id"] = df_dim_date["date"].dt.strftime("%Y%m%d").astype(int)
    df_dim_date["annee"] = df_dim_date["date"].dt.year
    df_dim_date["trimestre"] = df_dim_date["date"].dt.quarter
    df_dim_date["mois"] = df_dim_date["date"].dt.month
    df_dim_date["nom_mois"] = df_dim_date["mois"].map(lambda m: NOMS_MOIS[m - 1])
    df_dim_date["semaine"] = df_dim_date["date"].dt.isocalendar().week.astype(int)
    df_dim_date["jour_semaine"] = df_dim_date["date"].dt.dayofweek.map(lambda j: NOMS_JOURS[j])
    df_dim_date["est_weekend"] = df_dim_date["date"].dt.dayofweek >= 5
    return df_dim_date

#preparation Dim_Customer
def dim_customer_prep():
    df_customer = df_dim_client.copy()
    return df_customer

#preparation Dim_Product
def dim_product_prep():
    df_product = df_dim_produit.copy()
    return df_product

#preparation Dim_Shipping
def dim_mode_prep():
    df_dim_mode = df_modes.copy()
    df_dim_mode["mode_expedition_id"] = range(1, len(df_dim_mode) + 1)
    return df_dim_mode

#preparation Dim_Location
def dim_location_prep():
    df_location = df_dim_geographie.copy()
    return df_location

#preparation Fact_Sales
def faits_ventes_prep():
    df_dim_mode = dim_mode_prep()
    df_fait_ventes = df_faits.merge(df_dim_mode, on="mode_expedition")
    df_fait_ventes["date_commande_id"] = df_fait_ventes["date_commande"].dt.strftime("%Y%m%d").astype(int)
    df_fait_ventes["date_expedition_id"] = df_fait_ventes["date_expedition"].dt.strftime("%Y%m%d").astype(int)
    df_fait_ventes["delai_expedition"] = (df_fait_ventes["date_expedition"] - df_fait_ventes["date_commande"]).dt.days
    df_fait_ventes = df_fait_ventes[["ligne_id", "commande_id", "date_commande_id", "date_expedition_id", "produit_id", "client_id", "geographie_id", "mode_expedition_id", "ventes", "quantite", "remise", "profit", "delai_expedition"]]
    return df_fait_ventes

try:
    df_date = dim_date_prep()
    df_customer = dim_customer_prep()
    df_product = dim_product_prep()
    df_shipping = dim_mode_prep()
    df_location = dim_location_prep()
    df_sales = faits_ventes_prep()
    print(df_sales.dtypes)
except Exception as e:
    lg.error(f"Erreur pendant la Transformation : {e}")
    raise