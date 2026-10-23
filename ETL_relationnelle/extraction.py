import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
FICHIER_CSV = RAW_DIR / "Superstore.csv"
from utils.logger import get_logger

lg = get_logger("etl_relationnelle", "ETL_error_relationnelle.log")



dataframe = []
df = None
try: 
    df_superstore = pd.read_csv(FICHIER_CSV, sep=',', encoding="cp1252")
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