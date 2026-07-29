import pandas as pd
import numpy as np
import os
import logging as lg
import streamlit as st
import matplotlib.pyplot as plt


dossier_root =  os.path.dirname(os.path.abspath(__file__))
dossier_raw = os.path.join(dossier_root, "raw_data")

fichier_sales= os.path.join(dossier_raw, "sales_data.csv")
fichier_log = os.path.join(dossier_root, "pipeline_error.log")

lg.basicConfig(filename=fichier_log, level=lg.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")
#extraction
try :
    df_vente_cat = pd.read_csv(fichier_sales, sep=",")
except Exception as e:
    lg.error(f"Erreur de chargement csv vente {e}")

#transform
df_vente_cat= df_vente_cat.groupby(by=df_vente_cat["Product_Category"])["Quantity_Sold"].sum().reset_index()

#load
st.title('Dashboard ventes par category')

data_load_state = st.text('Loading graph')

categories_x = df_vente_cat["Product_Category"]
vente_y = df_vente_cat["Quantity_Sold"]
fig, ax = plt.subplots(figsize=(10, 6))
bar_container = ax.bar(df_vente_cat["Product_Category"], df_vente_cat["Quantity_Sold"])
ax.set_xlabel("Categories")
ax.bar_label(bar_container, fmt='{:,.0f}')

st.pyplot(fig)
data_load_state.text("Done!")
