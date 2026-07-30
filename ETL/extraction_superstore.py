import pandas as pd
import os
import sys

dossier_root =  os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(dossier_root)

from utils.logger import get_logger


dossier_raw = os.path.join(dossier_root, "raw_data")

fichier_superstore = os.path.join(dossier_raw, "Superstore.csv")
lg = get_logger("etl", "ETL_error.log")



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
    raise