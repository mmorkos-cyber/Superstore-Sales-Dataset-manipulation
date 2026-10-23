import pandas as pd
from ETL_relationnelle.extraction import df
from utils.logger import get_logger

lg = get_logger("etl_relationnelle", "ETL_error_relationnelle.log")

df = df.copy()

df["Order Date"] = pd.to_datetime(df["Order Date"], format="%d-%m-%Y")
df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="%d-%m-%Y")
df["Postal Code"] = df["Postal Code"].astype(str).str.zfill(5)

COLONNES_LOC = ["Country", "State", "City", "Region", "Postal Code"]
df["localisation_id"] = df.groupby(COLONNES_LOC).ngroup() + 1


def prepa_df_client():
    df_client = (df[["Customer ID", "Customer Name", "Segment"]].drop_duplicates(subset=["Customer ID"]).rename(columns={"Customer ID": "client_id", "Customer Name": "nom", "Segment": "segment"}))
    return df_client


def prepa_df_localisation():
    df_localisation = (df[COLONNES_LOC + ["localisation_id"]].drop_duplicates().rename(columns={"Country": "pays", "State": "etat", "City": "ville", "Region": "region", "Postal Code": "code_postal"}))
    return df_localisation


def prepa_df_category():
    df_category = (df[["Category"]].drop_duplicates().rename(columns={"Category": "categorie"}))
    return df_category


def prepa_df_sous_category():
    df_sous_category = (df[["Sub-Category", "Category"]].drop_duplicates().rename(columns={"Sub-Category": "sous_categorie", "Category": "categorie"}))
    return df_sous_category


def prepa_df_produit():
    df_produit = (df[["Product ID", "Product Name", "Sub-Category"]].drop_duplicates(subset=["Product ID"]).rename(columns={"Product ID": "produit_id", "Product Name": "nom", "Sub-Category": "sous_categorie"}))
    return df_produit


def prepa_df_commande():
    df_commande = (df[["Order ID", "Order Date", "Ship Date", "Ship Mode", "Customer ID", "localisation_id"]].drop_duplicates(subset=["Order ID"]).rename(columns={"Order ID": "commande_id", "Order Date": "date_commande", "Ship Date": "date_expedition", "Ship Mode": "mode_expedition", "Customer ID": "client_id"}))
    return df_commande


def prepa_df_ligne_commande():
    df_l_commande = (df[["Row ID", "Order ID", "Product ID", "Sales", "Quantity", "Discount", "Profit"]].rename(columns={"Row ID": "ligne_id", "Order ID": "commande_id", "Product ID": "produit_id", "Sales": "ventes", "Quantity": "quantite", "Discount": "remise", "Profit": "profit"}))
    return df_l_commande