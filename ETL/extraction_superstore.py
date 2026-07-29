import pandas as pd
import os
import logging as lg

dossier_root =  os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dossier_raw = os.path.join(dossier_root, "raw_data")

fichier_superstore = os.path.join(dossier_raw, "Superstore.csv")
fichier_log = os.path.join(dossier_root, "pipeline_error.log")

lg.basicConfig(filename=fichier_log, level=lg.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

dataframe = []
df = None
try: 
    df_superstore = pd.read_csv(fichier_superstore, sep=',', encoding="utf-8-sig")
    dataframe.append(df_superstore)
except Exception as e:
    lg.error(f"Erreur de chargement csv Superstore {e}")

try:
    if (dataframe):
        df = pd.concat(dataframe, ignore_index=True)
    else:
        raise ValueError("Aucun fichier valider")
except Exception as e:
    lg.error(f"Erreur pipeline : {e}")


